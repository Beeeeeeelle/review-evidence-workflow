#!/usr/bin/env python3
"""Revalidate a PDF retrieval audit and hand accepted full texts to a review round.
Uses Python 3.9+ and Poppler. Does not search, download, or decide scientific eligibility.
"""
import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from review_workflow import require, read, save, sha, safe_id, now

ACCEPTED={'accepted','downloaded','accepted_pdf','user_supplied_pdf','corrected_pdf_validated_existing'}
def first(row,*names):
    return next((str(row.get(k,'')).strip() for k in names if str(row.get(k,'')).strip()),'')
def doi(value):
    return re.sub(r'^(https?://(dx\.)?doi\.org/|doi:\s*)','',value.lower().strip()).rstrip('.,;)')
def tokens(value):
    return set(re.findall('[a-z0-9]+',unicodedata.normalize('NFKD',value).encode('ascii','ignore').decode().lower()))
def inspect(path,title,expected_doi):
    require(path.is_file() and path.read_bytes().startswith(b'%PDF-'),'missing_or_non_pdf')
    info=subprocess.run(['pdfinfo',str(path)],check=True,capture_output=True,text=True).stdout
    count=int(re.search(r'^Pages:\s*(\d+)',info,re.M).group(1));require(count>0,'empty_pdf')
    text=subprocess.run(['pdftotext','-f','1','-l',str(min(2,count)),str(path),'-'],check=True,capture_output=True,text=True).stdout
    found={doi(x) for x in re.findall(r'10\.\d{4,9}/[-._;()/:a-z0-9]+',text,re.I)}
    expected=doi(expected_doi);ts=tokens(title);score=len(ts&tokens(text))/len(ts) if ts else 0
    if expected and expected in found: identity,reason='pass','doi_match'
    elif expected and found: identity,reason='fail','doi_mismatch'
    elif len(ts)>=5 and score>=0.8: identity,reason='pass','strong_early_title_match'
    else: identity,reason='review','insufficient_identity_evidence'
    return {'sha256':sha(path),'page_count':count,'identity':identity,'reason':reason,'title_coverage':score,'found_dois':sorted(found)}

def prepare(audit,pdf_dir,out,validation=None,attempts=None,previous_bundle=None,identity_decisions=None):
    require(shutil.which('pdfinfo') and shutil.which('pdftotext'),'Install Poppler (pdfinfo and pdftotext) for source validation')
    audit,pdf_dir,out=Path(audit).resolve(),Path(pdf_dir).resolve(),Path(out).resolve()
    require(not out.exists(),'Output exists; use a new source handoff version')
    with audit.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
    require(rows,'Empty audit')
    reports={x['id']:x for x in read(validation)['results']} if validation else {}
    manual={x['record_id']:x for x in read(identity_decisions)} if identity_decisions else {}
    ids=[];accepted=[];queue=[];checks=[]
    for row in rows:
        rid=first(row,'ID','id','provisional_include_no','study_id','record_id');require(safe_id(rid) and rid not in ids,'Missing, unsafe or duplicate source ID');ids.append(rid)
        title=first(row,'title','Title','article_title');expected=first(row,'doi','DOI')
        status=first(row,'identity_status','validation_status','validation status','download_status','download status','status')
        raw=first(row,'pdf_path','PDF path','path','corrected_pdf_path') or first(row,'pdf_filename','PDF filename','filename') or rid+'.pdf'
        path=Path(raw).expanduser();path=path if path.is_absolute() else pdf_dir/path
        if status not in ACCEPTED:
            queue.append({'record_id':rid,'reason':first(row,'access_reason','retrieval_status','notes') or status or 'not_attempted'});continue
        try:
            require(bool(title),'missing_title');checked=inspect(path,title,expected);checked['record_id']=rid;checks.append(checked)
            if validation:
                report=reports.get(rid,{});require(report.get('sha256')==checked['sha256'] and report.get('pages')==checked['page_count'],'stale_or_missing_validation_report')
                require(report.get('structural')=='pass' and report.get('identity') in ('pass','review'),'external_validator_rejected')
            if checked['identity']=='review':
                m=manual.get(rid,{})
                require(m.get('source_sha256')==checked['sha256'] and m.get('human_confirmed') is True and all(m.get(k) for k in ('confirmed_by','confirmed_at','reason')),'identity_needs_human_review')
                checked['human_identity_decision']=m
            else: require(checked['identity']=='pass',checked['reason'])
            accepted.append({'record_id':rid,'title':title,'doi':expected,'source':{'path':'sources/'+rid+'.pdf','sha256':checked['sha256'],'page_count':checked['page_count'],'identity_status':'matched','identity_basis':checked},'_path':str(path)})
        except (ValueError,OSError,subprocess.CalledProcessError) as e:
            queue.append({'record_id':rid,'reason':str(e)})
    counts=Counter(r['source']['sha256'] for r in accepted)
    unique=[]
    for r in accepted:
        if counts[r['source']['sha256']]>1:queue.append({'record_id':r['record_id'],'reason':'duplicate_hash_across_ids_resolve_record_identity_before_handoff'})
        else:unique.append(r)
    accepted=unique;invalidations=[]
    if previous_bundle:
        old=read(previous_bundle);newhash={r['record_id']:r['source']['sha256'] for r in accepted}
        for r in old['records']:
            if r['record_id'] in newhash and r['source']['sha256']!=newhash[r['record_id']]:
                invalidations.append({'record_id':r['record_id'],'old_sha256':r['source']['sha256'],'new_sha256':newhash[r['record_id']],'status':'all_record_coding_and_downstream_outputs_require_reverification','affected_keys':[r['record_id']+'/'+x['field_id'] for x in r.get('items',[])]})
    out.mkdir(parents=True)
    for r in accepted:
        p=Path(r.pop('_path'));target=out/r['source']['path'];target.parent.mkdir(exist_ok=True);shutil.copy2(p,target)
    provenance={'audit_sha256':sha(audit),'created_at':now(),'method':'Poppler structural/early identity checks; source completeness and semantic relevance still require review.'}
    for name,path in [('record_state.csv',audit),('validation-input.json',validation),('retrieval_attempts.csv',attempts),('identity-decisions.json',identity_decisions)]:
        if path:shutil.copy2(path,out/name);provenance[name+'_sha256']=sha(path)
    manifest={'schema_version':'1.0','records':accepted,'provenance':provenance,'downstream_invalidations':invalidations}
    save(out/'sources-manifest.json',manifest);save(out/'remaining-queue.json',queue);save(out/'identity-checks.json',checks)
    result={'total_records':len(rows),'accepted':len(accepted),'unresolved_or_excluded':len(queue),'invalidated_records':len(invalidations),'source_manifest':str(out/'sources-manifest.json')}
    require(len(accepted)+len(queue)==len(rows),'Audit denominator mismatch');save(out/'summary.json',result);return result

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ('audit','pdf-dir','out'):ap.add_argument('--'+name,required=True)
    for name in ('validation','attempts','previous-bundle','identity-decisions'):ap.add_argument('--'+name)
    a=ap.parse_args();print(json.dumps(prepare(a.audit,a.pdf_dir,a.out,a.validation,a.attempts,a.previous_bundle,a.identity_decisions),indent=2))
if __name__=='__main__':
    try:main()
    except (ValueError,OSError,KeyError,TypeError,subprocess.CalledProcessError) as e:
        print(json.dumps({'error':str(e)}),file=sys.stderr);sys.exit(2)
