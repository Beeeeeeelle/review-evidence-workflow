#!/usr/bin/env python3
"""Portable evidence review packages. Python 3.9+, standard library only.
Semantic coding and adjudication remain with the review team, not this script.
"""
import argparse
from pdf_text import extract_pdf_words
import copy
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = '1.2.0'
ACTIONS = {'accept', 'revise', 'unclear'}
LAYERS = {'source_extraction', 'descriptive_coding', 'synthesis'}

def now():
    return datetime.now(timezone.utc).isoformat()

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()

def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2, ensure_ascii=False)
        f.write('\n')

def require(ok, message):
    if not ok:
        raise ValueError(message)

def nonempty(value):
    return isinstance(value, str) and bool(value.strip())

def safe_id(value):
    return isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,99}', value)

def source_path(project, relative):
    require(nonempty(relative) and not Path(relative).is_absolute(), 'Source path must be relative')
    require('..' not in Path(relative).parts, 'Source path traversal is not allowed')
    p = (project / relative).resolve()
    require(p.is_relative_to(project.resolve()), 'Source escapes project')
    require(p.suffix.lower() == '.pdf', 'The built-in viewer supports PDF sources')
    return p

def load_project(project, check_files=False, ready=True):
    project = Path(project).resolve()
    c, b = read(project/'review-config.json'), read(project/'bundle.json')
    require(c.get('schema_version') == b.get('schema_version') == '1.0', 'Unsupported schema')
    for k in ('project_id', 'protocol_version', 'codebook_version'):
        require(nonempty(c.get(k)) and c.get(k) == b.get(k), f'Config/bundle mismatch: {k}')
    require(safe_id(c['project_id']) and safe_id(b.get('assignment_id')), 'Invalid project/assignment ID')
    if ready:
        require(c.get('status') == 'ready', 'Resolve the project protocol before building or reconciling')
        require(nonempty(c.get('unit_of_analysis')), 'Unit of analysis required')
        require(nonempty(c.get('research', {}).get('decision_rule')), 'Decision rule required')
    require(c.get('verification', {}).get('mode') in MODES, 'Unsupported review mode')
    if ready:
        require(c.get('codebook_governance', {}).get('origin') in ('human_developed', 'human_led') and nonempty(c['codebook_governance'].get('provided_by')) and nonempty(c['codebook_governance'].get('source')), 'Use a human-led codebook with its provider and source recorded')
    reviewers = c['verification'].get('reviewers', [])
    require(reviewers and len(set(reviewers)) == len(reviewers) and all(safe_id(x) for x in reviewers), 'Unique reviewer IDs required')
    minimum = c['verification'].get('min_reviewers')
    require(type(minimum) is int and 1 <= minimum <= len(reviewers), 'Invalid min_reviewers')
    stages = c.get('ui', {}).get('stages', [])
    require(stages and all(safe_id(x.get('id')) and nonempty(x.get('label')) for x in stages), 'Define UI stages')
    stage_ids = [s['id'] for s in stages]
    require(len(stage_ids) == len(set(stage_ids)), 'Duplicate stage ID')
    fields = c.get('fields', [])
    field_map = {f.get('id'): f for f in fields}
    require(fields and len(field_map) == len(fields), 'Unique field definitions required')
    for f in fields:
        require(safe_id(f.get('id')) and nonempty(f.get('label')) and nonempty(f.get('definition')), 'Invalid field definition')
        require(f.get('stage') in stage_ids and f.get('layer') in LAYERS, 'Invalid field stage/layer')
        require(f.get('layer') != 'synthesis', 'Cross-review synthesis requires a separate multi-source package')
        if 'options' in f:
            require(isinstance(f['options'], list) and f['options'], 'Options must be a nonempty list')
    require(type(c.get('evidence', {}).get('quote_word_limit')) is int and c['evidence']['quote_word_limit'] > 0, 'Quote limit required')
    ids, keys, item_map = set(), set(), {}
    records = b.get('records', [])
    require(isinstance(records, list), 'records must be a list')
    if ready:
        require(records, 'No records assigned')
    for r in records:
        rid = r.get('record_id')
        require(safe_id(rid) and rid not in ids and nonempty(r.get('title')), 'Invalid/duplicate record')
        ids.add(rid)
        s = r.get('source', {})
        require(s.get('identity_status') == 'matched', f'{rid}: verify source identity first')
        require(re.fullmatch('[0-9a-f]{64}', str(s.get('sha256', ''))), f'{rid}: source hash required')
        require(type(s.get('page_count')) is int and s['page_count'] > 0, f'{rid}: invalid page count')
        p = source_path(project, s.get('path'))
        if check_files:
            require(p.is_file() and p.read_bytes().startswith(b'%PDF-'), f'{rid}: PDF missing/invalid')
            require(sha(p) == s['sha256'], f'{rid}: source hash changed')
        seen = set()
        require(isinstance(r.get('items'), list), f'{rid}: items missing')
        for it in r['items']:
            fid = it.get('field_id')
            require(fid in field_map and fid not in seen, f'{rid}: unknown/duplicate field {fid}')
            seen.add(fid)
            key = rid+'/'+fid
            keys.add(key); item_map[key] = (r, it, field_map[fid])
            require(nonempty(it.get('rationale')), f'{key}: rationale required')
            require(it.get('status') in ('proposed', 'not_assessed'), f'{key}: proposal must not claim finality')
            missing = it.get('missingness')
            require(missing in (None, 'NR', 'NA', 'Unclear'), f'{key}: invalid missingness')
            evidence = it.get('evidence', [])
            require(isinstance(evidence, list), f'{key}: evidence must be a list')
            if it['status'] == 'not_assessed':
                require(it.get('value') is None and not evidence, f'{key}: unassessed item must not have a value/evidence')
                continue
            if missing:
                require(it.get('value') == missing, f'{key}: missing value must use its explicit code')
            else:
                require(it.get('value') is not None, f'{key}: value required')
                if 'options' in field_map[fid]:
                    require(it['value'] in field_map[fid]['options'], f'{key}: value outside options')
            if missing == 'NR':
                locs = it.get('checked_locations', [])
                require(locs and all(type(x.get('pdf_page')) is int and 1 <= x['pdf_page'] <= s['page_count'] and nonempty(x.get('section')) for x in locs), f'{key}: NR needs checked locations')
            elif missing != 'NA':
                require(evidence, f'{key}: source evidence required')
            for e in evidence:
                require(type(e.get('pdf_page')) is int and 1 <= e['pdf_page'] <= s['page_count'], f'{key}: page outside source')
                require(nonempty(e.get('section')) and nonempty(e.get('quote')), f'{key}: section/quote required')
                require(len(e['quote'].split()) <= c['evidence']['quote_word_limit'], f'{key}: quote too long')
        required = {f['id'] for f in fields if f.get('required', False)}
        require(required <= seen, f'{rid}: required fields omitted: {sorted(required-seen)}')
    for key, (_, it, _) in item_map.items():
        require(all(d in keys for d in it.get('depends_on', [])), f'{key}: unknown dependency')
    outputs = b.get('outputs', [])
    output_ids = [x.get('id') for x in outputs]
    require(len(set(output_ids)) == len(output_ids) and all(safe_id(x) for x in output_ids), 'Invalid output IDs')
    visiting, visited = set(), set()
    def visit(key):
        require(key not in visiting, 'Cyclic field dependencies are not supported')
        if key in visited: return
        visiting.add(key)
        for dep in item_map[key][1].get('depends_on', []): visit(dep)
        visiting.remove(key); visited.add(key)
    for key in item_map: visit(key)
    for out in outputs:
        require(out.get('depends_on') and all(d in keys for d in out['depends_on']), 'Output needs known dependencies')
    rule_ids = [r.get('id') for r in c.get('derived_rules', [])]
    require(len(set(rule_ids)) == len(rule_ids), 'Duplicate derived rule ID')
    for rule in c.get('derived_rules', []):
        require(safe_id(rule.get('id')) and rule.get('operation') == 'all_equal', 'Unsupported deterministic rule')
        require(rule.get('fields') and all(f in field_map for f in rule['fields']), 'Rule fields missing')
        for name in ('success', 'failure', 'unresolved'):
            require(nonempty(rule.get(name)), 'Rule states required')
    validate_profiles(c, b, item_map)
    return c, b, item_map

def binding(c, b):
    return {'schema_version': '1.0', 'project_id': c['project_id'],
            'assignment_id': b['assignment_id'], 'protocol_version': c['protocol_version'],
            'codebook_version': c['codebook_version'], 'config_sha256': digest(c),
            'bundle_sha256': digest(b), 'mode': c['verification']['mode'],
            'source_fingerprints': {r['record_id']: r['source']['sha256'] for r in b['records']}}

def reviewable(items):
    return {k: v for k, v in items.items() if v[1]['status'] == 'proposed'}

MODES = {'assisted_verification', 'independent_review'}

def profile(c, reviewer):
    return c['verification'].get('reviewer_profiles', {}).get(reviewer, {})

def review_mode(c, reviewer):
    return profile(c, reviewer).get('mode', c['verification']['mode'])

def assigned_keys(c, b, items, reviewer):
    p = profile(c, reviewer)
    rids = p.get('record_ids', [r['record_id'] for r in b['records']])
    fids = p.get('field_ids', [f['id'] for f in c['fields']])
    independent = review_mode(c, reviewer) == 'independent_review'
    return [k for k, (r, it, _) in items.items() if r['record_id'] in rids and it['field_id'] in fids and (independent or it['status'] == 'proposed')]

def target_items(c, b, items):
    keys = {k for reviewer in c['verification']['reviewers'] for k in assigned_keys(c,b,items,reviewer)}
    return {k:v for k,v in items.items() if k in keys}

def required_reviews(c, definition):
    return definition.get('min_reviewers', c['verification']['min_reviewers'])

def validate_profiles(c, b, items):
    profiles=c['verification'].get('reviewer_profiles', {})
    require(isinstance(profiles,dict) and set(profiles)<=set(c['verification']['reviewers']), 'Unknown reviewer profile')
    for reviewer in c['verification']['reviewers']:
        p=profile(c,reviewer)
        require(review_mode(c,reviewer) in MODES, 'Unsupported reviewer mode')
        for name, allowed in [('record_ids',{r['record_id'] for r in b['records']}),('field_ids',{f['id'] for f in c['fields']})]:
            if name in p:
                require(isinstance(p[name],list) and p[name] and len(set(p[name]))==len(p[name]) and set(p[name])<=allowed, 'Invalid personalized '+name)
        require(isinstance(p.get('ui',{}),dict), 'Invalid personalized UI')
    for key, (_,_,definition) in target_items(c,b,items).items():
        n=required_reviews(c,definition)
        require(type(n) is int and n>0, 'Invalid field review coverage')
        capacity=sum(key in assigned_keys(c,b,items,r) for r in c['verification']['reviewers'])
        require(capacity>=n, key+': assignment cannot satisfy required reviewer coverage')

def package_binding(c,b,items,reviewer):
    keys=assigned_keys(c,b,items,reviewer)
    return {**binding(c,b), 'package_schema_version':'1.1', 'review_mode':review_mode(c,reviewer),
            'assignment_sha256':digest({'reviewer':reviewer,'keys':keys,'profile':profile(c,reviewer),'mode':review_mode(c,reviewer)}),
            'source_fingerprints':{r['record_id']:r['source']['sha256'] for r in b['records'] if any(k.startswith(r['record_id']+'/') for k in keys)}}

def validate_human_value(x, rec, field, c):
    require(nonempty(x.get('rationale')), 'Independent answer needs a rationale')
    missing=x.get('missingness')
    require(missing in (None,'NR','NA','Unclear'), 'Invalid independent missingness')
    value=x.get('value')
    if missing: require(value==missing, 'Missingness code and value differ')
    else:
        require(value is not None and (not isinstance(value,str) or nonempty(value)), 'Independent value missing')
        if 'options' in field: require(value in field['options'], 'Independent value outside codebook options')
    ev=x.get('evidence',[])
    require(isinstance(ev,list), 'Independent evidence must be a list')
    if missing=='NR':
        locs=x.get('checked_locations',[])
        require(isinstance(locs,list) and locs and all(type(z.get('pdf_page')) is int and 1<=z['pdf_page']<=rec['source']['page_count'] and nonempty(z.get('section')) for z in locs), 'NR needs checked locations')
    elif missing!='NA': require(ev, 'Independent answer needs source evidence')
    for e in ev:
        require(type(e.get('pdf_page')) is int and 1<=e['pdf_page']<=rec['source']['page_count'] and nonempty(e.get('section')) and nonempty(e.get('quote')), 'Invalid independent evidence location')
        require(len(e['quote'].split())<=c['evidence']['quote_word_limit'], 'Independent quote exceeds limit')

def validate_return(ret, c, b, items):
    reviewer=ret.get('reviewer_id')
    require(reviewer in c['verification']['reviewers'], 'Unassigned reviewer')
    # Preserve v1 returns for an unpersonalized assisted project only.
    legacy=ret.get('package_schema_version') is None
    if legacy:
        require(not c['verification'].get('reviewer_profiles') and c['verification']['mode']=='assisted_verification', 'Legacy return incompatible with configured mode/profile')
    expected=binding(c,b) if legacy else package_binding(c,b,items,reviewer)
    for k,v in expected.items(): require(ret.get(k)==v, 'Return binding mismatch: '+k)
    require(nonempty(ret.get('exported_at')), 'Export timestamp missing')
    allowed=set(assigned_keys(c,b,items,reviewer)); seen=set()
    require(isinstance(ret.get('responses'),list), 'Return responses missing')
    for x in ret['responses']:
        key=x.get('key')
        require(key in allowed and key not in seen, 'Unknown/duplicate/unassigned returned field');seen.add(key)
        require(nonempty(x.get('reviewed_at')) and isinstance(x.get('comment'),str), 'Invalid response metadata')
        if review_mode(c,reviewer)=='independent_review':
            require(x.get('committed') is True, 'Draft answers are not submitted human review')
            require(x.get('action') in ('submit','defer'), 'Independent review cannot accept an unseen suggestion')
            if x['action']=='submit': validate_human_value(x,items[key][0],items[key][2],c)
            else: require(nonempty(x['comment']), 'Deferral requires explanation')
        else:
            require(x.get('action') in ACTIONS, 'Invalid assisted response')
            if x['action']!='accept': require(nonempty(x['comment']), 'Challenge/uncertainty requires explanation')
    return {'reviewer_id':reviewer,'review_mode':review_mode(c,reviewer),'responded':len(seen),'assigned':len(allowed),'pending':sorted(allowed-seen)}

def compare(c, b, items, return_paths):
    returns, reviewer_ids = [], set()
    for p in return_paths:
        r = read(p); validate_return(r, c, b, items)
        require(r['reviewer_id'] not in reviewer_ids, 'Choose one latest return per reviewer')
        reviewer_ids.add(r['reviewer_id']); returns.append(r)
    return comparison_from_returns(c, b, items, returns, [sha(p) for p in return_paths])

def comparison_from_returns(c, b, items, returns, return_hashes):
    reviewer_ids = set()
    for r in returns:
        validate_return(r, c, b, items)
        require(r['reviewer_id'] not in reviewer_ids, 'Duplicate reviewer')
        reviewer_ids.add(r['reviewer_id'])
    rows = []
    states=('pending','needs_adjudication','accepted_by_required_reviewers','concordant_independent_values')
    for key, (_,it,f) in target_items(c,b,items).items():
        responses=[dict(x,reviewer_id=r['reviewer_id'],review_mode=review_mode(c,r['reviewer_id'])) for r in returns for x in r['responses'] if x['key']==key]
        if len(responses)<required_reviews(c,f): state='pending'
        elif all(x['review_mode']=='assisted_verification' and x['action']=='accept' for x in responses): state='accepted_by_required_reviewers'
        elif all(x['review_mode']=='independent_review' and x['action']=='submit' for x in responses) and len({digest({'value':x['value'],'missingness':x.get('missingness')}) for x in responses})==1: state='concordant_independent_values'
        else: state='needs_adjudication'
        rows.append({'key':key,'label':f['label'],'proposed_value':it['value'],'state':state,'responses':responses})
    return {**binding(c,b),'generated_at':now(),'return_hashes':return_hashes,'returns':returns,'items':rows,
            'counts':{state:sum(x['state']==state for x in rows) for state in states},
            'comparison_rule':'Independent concordance compares value and missingness, not evidence quality; mixed modes require human adjudication.'}

def finalize(c, b, items, comparison, decisions):
    for k, v in binding(c, b).items():
        require(comparison.get(k) == v, f'Comparison binding mismatch: {k}')
    expected = comparison_from_returns(c, b, items, comparison.get('returns', []), comparison.get('return_hashes', []))
    require(comparison.get('items') == expected['items'] and comparison.get('counts') == expected['counts'], 'Comparison differs from its reviewer returns')
    for k, v in binding(c, b).items():
        require(decisions.get(k) == v, f'Adjudication binding mismatch: {k}')
    require(decisions.get('human_authorized') is True and nonempty(decisions.get('authorized_by')) and nonempty(decisions.get('authorized_at')), 'Record actual human authorization; do not fabricate it')
    require(decisions.get('comparison_sha256') == digest(comparison), 'Decisions refer to another comparison')
    events = decisions.get('decisions', [])
    dmap = {x.get('key'): x for x in events}
    require(len(dmap) == len(events) and set(dmap) <= set(target_items(c,b,items)), 'Unknown/duplicate adjudication item')
    result, changed = [], set()
    for row in comparison['items']:
        key = row['key']; rec, it, definition = items[key]
        event = dmap.get(key)
        state, value, evidence, rationale = 'unresolved', None, [], ''
        missingness, checked_locations = it.get('missingness'), it.get('checked_locations', [])
        if row['state'] == 'accepted_by_required_reviewers' and event is None:
            state, value, evidence, rationale = 'authorized', it['value'], it.get('evidence', []), it['rationale']
        elif event:
            require(event.get('disposition') in ('adopt', 'retain', 'select_review', 'unresolved') and nonempty(event.get('rationale')), f'{key}: invalid adjudication')
            require(row['state'] != 'pending', f'{key}: required review coverage incomplete')
            if event['disposition'] == 'retain':
                require(it['status']=='proposed' and any(x.get('review_mode')=='assisted_verification' for x in row['responses']), 'An unseen proposal cannot be retained as independent adjudication')
                state, value, evidence, rationale = 'authorized', it['value'], it.get('evidence', []), event['rationale']
            elif event['disposition'] == 'select_review':
                selected=next((x for x in row['responses'] if x['reviewer_id']==event.get('reviewer_id') and x['action']=='submit'),None)
                require(selected is not None, 'Select an actual submitted independent response')
                validate_human_value(selected,rec,definition,c)
                state,value,evidence,rationale='authorized',selected['value'],selected.get('evidence',[]),event['rationale']
                missingness,checked_locations=selected.get('missingness'),selected.get('checked_locations',[])
                # Jointly submitted dependent fields already belong to the same independent round.
                if it['status']=='proposed' and (selected.get('value')!=it.get('value') or selected.get('missingness')!=it.get('missingness') or (selected.get('evidence') or [])!=(it.get('evidence') or []) or (selected.get('checked_locations') or [])!=(it.get('checked_locations') or [])): changed.add(key)
            elif event['disposition'] == 'adopt':
                replacement = copy.deepcopy(it)
                for k in ('value', 'evidence', 'missingness', 'checked_locations'):
                    replacement[k] = event.get(k)
                replacement['rationale'] = event['rationale']
                replacement['status'] = 'proposed'
                require(replacement['value'] is not None, f'{key}: corrected value required')
                # Reuse full schema validation on the candidate bundle before accepting it.
                candidate = copy.deepcopy(b)
                cr = next(r for r in candidate['records'] if r['record_id'] == rec['record_id'])
                cr['items'] = [replacement if x['field_id'] == it['field_id'] else x for x in cr['items']]
                validate_in_memory(c, candidate)
                state, value, evidence, rationale = 'authorized', replacement['value'], replacement.get('evidence', []), replacement['rationale']
                missingness, checked_locations = replacement.get('missingness'), replacement.get('checked_locations') or []
                changed.add(key)
        result.append({'key': key, 'status': state, 'value': value, 'evidence': evidence, 'rationale': rationale,
                       'missingness': missingness, 'checked_locations': checked_locations,
                       'reviewer_responses': row['responses'], 'adjudication': event,
                       'source_sha256': rec['source']['sha256']})
    # Transitive invalidation: a dependent field is not silently kept authorized.
    affected = set(changed)
    while True:
        extra = {k for k, (_, it, _) in items.items() if set(it.get('depends_on', [])) & affected} - affected
        if not extra: break
        affected |= extra
    dependent = {k for k, (_, it, _) in items.items() if set(it.get('depends_on', [])) & affected}
    for row in result:
        if row['key'] in dependent:
            row['status'] = 'stale_requires_reverification'
            row['value'] = None
    final_map = {x['key']: x for x in result}
    derived = []
    for r in b['records']:
        for rule in c.get('derived_rules', []):
            inputs = [final_map.get(r['record_id']+'/'+f, {}) for f in rule['fields']]
            values = [x.get('value') for x in inputs]
            if any(x.get('status') != 'authorized' for x in inputs): state = rule['unresolved']
            elif all(v == rule.get('required_value') for v in values): state = rule['success']
            elif any(v in rule.get('failure_values', []) for v in values): state = rule['failure']
            else: state = rule['unresolved']
            derived.append({'record_id': r['record_id'], 'rule_id': rule['id'], 'value': state, 'inputs': values})
    blocked = {x['key'] for x in result if x['status'] != 'authorized'} | (set(items)-set(final_map))
    outputs = [{**x, 'status': 'stale_requires_recompute' if set(x['depends_on']) & (affected | blocked) else 'inputs_unchanged_not_semantically_validated'} for x in b.get('outputs', [])]
    return {**binding(c, b), 'generated_at': now(), 'authorized_by': decisions['authorized_by'],
            'authorization_record_sha256': digest(decisions), 'items': result, 'derived': derived, 'outputs': outputs,
            'complete': bool(result) and not blocked,
            'unassessed_fields': sorted(set(items)-set(final_map)),
            'limitations': 'Authorization metadata records an asserted human action, not identity authentication or scientific truth. Unregistered dependencies cannot be invalidated.'}

def validate_in_memory(c, b):
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = Path(d); save(p/'review-config.json', c); save(p/'bundle.json', b)
        load_project(p, check_files=False)

def package_payload(c,b,items,reviewer,render_pages):
    keys=assigned_keys(c,b,items,reviewer); p=profile(c,reviewer); mode=review_mode(c,reviewer)
    # Whitelist serialization. Never ship hidden proposal fields, source annotations or another reviewer's feedback.
    ui={k:copy.deepcopy(c['ui'][k]) for k in ('stages','title','instructions','stage_labels','action_labels','collapsed_groups','expand_all_groups') if k in c['ui']}
    ui['stages']=[{k:s[k] for k in ('id','label')} for s in ui['stages']]
    for k in ('title','instructions','stage_labels','action_labels','collapsed_groups','expand_all_groups'):
        if k in p.get('ui',{}):ui[k]=p['ui'][k]
    if ui.get('stage_labels'):
        for stage in ui['stages']: stage['label']=ui['stage_labels'].get(stage['id'],stage['label'])
    fc=[]
    field_order=p.get('field_ids',[f['id'] for f in c['fields']])
    for fid in field_order:
        if not any(k.endswith('/'+fid) for k in keys):continue
        f=next(f for f in c['fields'] if f['id']==fid)
        fc.append({k:copy.deepcopy(f[k]) for k in ('id','label','definition','stage','layer','options','group','required') if k in f})
    records=[]
    for rid in p.get('record_ids',[r['record_id'] for r in b['records']]):
        r=next(r for r in b['records'] if r['record_id']==rid)
        assigned=[it for fid in field_order for it in r['items'] if it['field_id']==fid and rid+'/'+fid in keys]
        if not assigned:continue
        nr={k:r[k] for k in ('record_id','title','doi') if k in r}
        nr['source']={k:r['source'][k] for k in ('path','sha256','page_count')}
        nr['items']=[]
        for it in assigned:
            if mode=='independent_review': ni={'field_id':it['field_id'],'status':'awaiting_human'}
            else:ni={k:copy.deepcopy(it[k]) for k in ('field_id','status','value','rationale','missingness','evidence','checked_locations') if k in it}
            nr['items'].append(ni)
        records.append(nr)
    conf={'title':ui.get('title',c.get('title',c['project_id'])),'project_id':c['project_id'],'unit_of_analysis':c['unit_of_analysis'],'fields':fc,'ui':ui,'evidence':c['evidence'],'codebook_governance':{k:c['codebook_governance'][k] for k in ('origin','provided_by','source')},'protocol_version':c['protocol_version'],'codebook_version':c['codebook_version']}
    return {'config':conf,'bundle':{'records':records},'binding':package_binding(c,b,items,reviewer),'reviewer_id':reviewer,'review_mode':mode,'rendered_pages':render_pages,'tool_version':VERSION}

def build(project,out,reviewer,render_pages=False):
    project,out=Path(project).resolve(),Path(out).resolve();c,b,items=load_project(project,True)
    require(reviewer in c['verification']['reviewers'], 'Reviewer not assigned')
    require(assigned_keys(c,b,items,reviewer), 'No reviewable fields assigned to this reviewer')
    require(not out.exists(), 'Output already exists; use a new versioned directory')
    if render_pages:require(shutil.which('pdftoppm'),'Install Poppler or omit --render-pages')
    data=package_payload(c,b,items,reviewer,render_pages)
    out.mkdir(parents=True)
    for r in data['bundle']['records']:
        original=source_path(project,r['source']['path']);target=out/'sources'/f"{r['record_id']}.pdf";target.parent.mkdir(exist_ok=True);shutil.copy2(original,target);r['source']['path']='sources/'+target.name
        if render_pages:
            if shutil.which('pdftotext'):
                try: r['source']['text_coordinates']=extract_pdf_words(target)
                except (ImportError, subprocess.SubprocessError, ValueError, OSError): pass
            pages=out/'pages'/r['record_id'];pages.mkdir(parents=True)
            subprocess.run(['pdftoppm','-jpeg','-scale-to','1500',str(original),str(pages/'p')],check=True,capture_output=True)
            generated=sorted(pages.glob('p-*.jpg'),key=lambda p:int(p.stem.split('-')[-1]))
            require(len(generated)==r['source']['page_count'],'Rendered page count does not match manifest')
            for i,p in enumerate(generated,1):p.rename(pages/f'{i}.jpg')
    payload=json.dumps(data,ensure_ascii=False).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
    (out/'data.js').write_text('window.REVIEW_DATA = '+payload+';\n',encoding='utf-8')
    for name in ('OPEN_ME.html','app.js','styles.css','evidence-reader.js','evidence-reader.css'):shutil.copy2(ROOT/'assets'/name,out/name)
    save(out/'package-manifest.json',{**data['binding'],'reviewer_id':reviewer,'tool_version':VERSION,'built_at':now(),'rendered_pages':render_pages})
    (out/'READ_FIRST.txt').write_text('Open OPEN_ME.html. Use the human-developed codebook and complete source.\nMode: '+data['review_mode']+'\nIndependent packages omit AI proposals and all other reviewer feedback.\nExport JSON to return your work to the coordinator; import your own JSON to resume.\nA sent package or matching answers do not prove independent reviewer conduct.\nActivity estimates are not total work time or measured time savings.\n',encoding='utf-8')
    return {'package':str(out),'records':len(data['bundle']['records']),'fields':len(assigned_keys(c,b,items,reviewer)),'mode':data['review_mode']}

def new_round(project, out, round_id, purpose, mode=None, codebook_version=None, record_ids=None):
    project,out=Path(project).resolve(),Path(out).resolve()
    c,b,items=load_project(project,True)
    require(safe_id(round_id) and round_id!=b['assignment_id'], 'Use a new round/assignment ID')
    require(nonempty(purpose), 'Record the purpose of this round')
    require(not out.exists(), 'Round output exists; preserve the previous round')
    keep=set(record_ids or [r['record_id'] for r in b['records']])
    require(keep and keep <= {r['record_id'] for r in b['records']}, 'Unknown round record IDs')
    previous=b['assignment_id'];b['assignment_id']=round_id
    c['review_round']={'id':round_id,'purpose':purpose,'previous_assignment':previous}
    if mode:
        require(mode in MODES,'Unsupported round mode');c['verification']['mode']=mode
        for p in c['verification'].get('reviewer_profiles',{}).values():p.pop('mode',None)
    codebook_changed=bool(codebook_version and codebook_version!=c['codebook_version'])
    if codebook_version:
        c['codebook_version']=b['codebook_version']=codebook_version
    b['records']=[r for r in b['records'] if r['record_id'] in keep]
    if codebook_changed:
        for r in b['records']:
            for it in r['items']:
                for k in ('missingness','checked_locations','details'):it.pop(k,None)
                it.update(status='not_assessed',value=None,evidence=[],rationale='Codebook changed; recode under the new human-led rules.')
    retained={r['record_id']+'/'+it['field_id'] for r in b['records'] for it in r['items']}
    require(all(set(it.get('depends_on',[]))<=retained for r in b['records'] for it in r['items']), 'Round selection omits a dependency; include its record or explicitly revise the dependency model')
    b['outputs']=[x for x in b.get('outputs',[]) if set(x['depends_on'])<=retained]
    for p in c['verification'].get('reviewer_profiles',{}).values():
        if 'record_ids' in p:
            p['record_ids']=[r for r in p['record_ids'] if r in keep]
            require(p['record_ids'],'Round leaves a reviewer unassigned; adjust profiles explicitly before cloning')
    validate_in_memory(c,b)
    for r in b['records']:
        src=source_path(project,r['source']['path']);target=out/'sources'/(r['record_id']+'.pdf');target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,target);r['source']['path']='sources/'+target.name
    save(out/'review-config.json',c);save(out/'bundle.json',b)
    return {'project':str(out),'round':round_id,'records':len(b['records']),'note':'Edit new-round proposals/codebook definitions as needed, then validate and build. Prior returns do not transfer.'}

def seed(config, manifest, out, assignment_id):
    c=read(config);m=read(manifest);out=Path(out).resolve()
    require(not out.exists(),'Project exists');require(safe_id(assignment_id),'Invalid assignment ID')
    require(m.get('records'),'No validated full texts available')
    b={k:c[k] for k in ('schema_version','project_id','protocol_version','codebook_version')}
    b.update(assignment_id=assignment_id,records=[],outputs=[],source_manifest_sha256=sha(manifest))
    for r in m['records']:
        require(safe_id(r['record_id']),'Unsafe source ID')
        src=source_path(Path(manifest).resolve().parent,r['source']['path'])
        require(sha(src)==r['source']['sha256'],'Source changed since handoff')
        nr=copy.deepcopy(r);nr['source']['path']='sources/'+r['record_id']+'.pdf'
        nr['items']=[{'field_id':f['id'],'status':'not_assessed','value':None,'rationale':'Awaiting coding under the human-led codebook.','evidence':[]} for f in c['fields']]
        b['records'].append(nr)
    validate_in_memory(c,b)
    for r in m['records']:
        target=out/'sources'/(r['record_id']+'.pdf');target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source_path(Path(manifest).resolve().parent,r['source']['path']),target)
    save(out/'review-config.json',c);save(out/'bundle.json',b)
    return {'project':str(out),'records':len(b['records']),'note':'Blank items are ready for independent coding; assisted mode first needs evidence-grounded AI proposals.'}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='command', required=True)
    p = sub.add_parser('init');p.add_argument('project');p.add_argument('--project-id', default='new-review')
    p = sub.add_parser('validate');p.add_argument('project');p.add_argument('--check-files', action='store_true');p.add_argument('--return-file')
    p = sub.add_parser('build');p.add_argument('project');p.add_argument('--out', required=True);p.add_argument('--reviewer', required=True);p.add_argument('--render-pages', action='store_true')
    p = sub.add_parser('compare');p.add_argument('project');p.add_argument('--returns', nargs='+', required=True);p.add_argument('--out', required=True)
    p = sub.add_parser('finalize');p.add_argument('project');p.add_argument('--comparison', required=True);p.add_argument('--decisions', required=True);p.add_argument('--out', required=True)
    p = sub.add_parser('dossier');p.add_argument('pdf');p.add_argument('--record-id', required=True);p.add_argument('--out', required=True)
    p = sub.add_parser('new-round');p.add_argument('project');p.add_argument('--out',required=True);p.add_argument('--round-id',required=True);p.add_argument('--purpose',required=True);p.add_argument('--mode',choices=sorted(MODES));p.add_argument('--codebook-version');p.add_argument('--record-ids',nargs='+')
    p = sub.add_parser('seed');p.add_argument('--config',required=True);p.add_argument('--source-manifest',required=True);p.add_argument('--out',required=True);p.add_argument('--assignment-id',required=True)
    args = ap.parse_args()
    if args.command == 'init':
        require(safe_id(args.project_id), 'Invalid project ID')
        p = Path(args.project);require(not p.exists(), 'Project already exists; preserve its files')
        c = read(ROOT/'assets/review-config.template.json');c['project_id'] = args.project_id
        b = {k: c[k] for k in ('schema_version', 'project_id', 'protocol_version', 'codebook_version')}
        b.update(assignment_id='pilot-v1', records=[], outputs=[])
        save(p/'review-config.json', c);save(p/'bundle.json', b)
        result = {'project': str(p.resolve()), 'status': 'draft'}
    elif args.command == 'dossier':
        require(shutil.which('pdftotext') and shutil.which('pdfinfo'), 'Poppler required for page extraction')
        pdf = Path(args.pdf).resolve();require(pdf.is_file(), 'PDF missing')
        info = subprocess.run(['pdfinfo', str(pdf)], check=True, capture_output=True, text=True).stdout
        count = int(re.search(r'^Pages:\s*(\d+)', info, re.M).group(1))
        pages = []
        for i in range(1, count+1):
            txt = subprocess.run(['pdftotext', '-f', str(i), '-l', str(i), '-layout', str(pdf), '-'], check=True, capture_output=True, text=True).stdout
            pages.append({'pdf_page': i, 'text': txt.rstrip('\f\n')})
        result = {'record_id': args.record_id, 'source_sha256': sha(pdf), 'page_count': count, 'raw_pages': pages,
                  'identity_status': 'unverified', 'tool': 'Poppler pdftotext', 'created_at': now(),
                  'warnings': ['Text extraction does not verify identity or reading order; inspect tables and ambiguous pages.']}
        save(args.out, result);result = {'dossier': args.out, 'pages': count}
    elif args.command == 'build':result = build(args.project, args.out, args.reviewer, args.render_pages)
    elif args.command == 'new-round':result = new_round(args.project,args.out,args.round_id,args.purpose,args.mode,args.codebook_version,args.record_ids)
    elif args.command == 'seed':result = seed(args.config,args.source_manifest,args.out,args.assignment_id)
    else:
        c, b, items = load_project(args.project, getattr(args, 'check_files', False) or args.command == 'finalize')
        if args.command == 'validate':
            result = {'valid': True, 'records': len(b['records']), 'total_fields': len(items),
                      'proposed_fields': len(reviewable(items)), 'assigned_fields': len(target_items(c,b,items)),
                      'assignments': [{'reviewer_id':r,'mode':review_mode(c,r),'assigned_fields':len(assigned_keys(c,b,items,r))} for r in c['verification']['reviewers']]}
            if args.return_file:result['return'] = validate_return(read(args.return_file), c, b, items)
        elif args.command == 'compare':
            result = compare(c, b, items, args.returns);save(args.out, result)
        else:
            comparison = read(args.comparison)
            for k, v in binding(c, b).items():require(comparison.get(k) == v, 'Comparison no longer matches project')
            require(set(x['key'] for x in comparison['items']) == set(target_items(c,b,items)), 'Comparison coverage mismatch')
            result = finalize(c, b, items, comparison, read(args.decisions));save(args.out, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    try:main()
    except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as e:
        print(json.dumps({'error': str(e)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(2)
