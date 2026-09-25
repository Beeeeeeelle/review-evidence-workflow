#!/usr/bin/env python3
"""Generate synthetic, openly redistributable fixtures. No real study data or human decisions."""
import argparse, copy, csv, importlib.util, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'review-evidence-workflow/scripts'))
import review_workflow as rw

def write_pdf(path,lines):
    lines=['SYNTHETIC EXAMPLE - not research data']+lines
    body='BT /F1 11 Tf 40 750 Td '+' '.join(('0 -20 Td ' if i else '')+'('+x.replace(chr(92),chr(92)*2).replace('(',chr(92)+'(').replace(')',chr(92)+')')+') Tj' for i,x in enumerate(lines))+' ET'
    objects=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',('<< /Length '+str(len(body.encode()))+' >>\nstream\n'+body+'\nendstream').encode()]
    data=b'%PDF-1.4\n';offsets=[0]
    for n,obj in enumerate(objects,1): offsets.append(len(data));data+=str(n).encode()+b' 0 obj\n'+obj+b'\nendobj\n'
    start=len(data);data+=b'xref\n0 6\n0000000000 65535 f \n'+b''.join(f'{o:010} 00000 n \n'.encode() for o in offsets[1:]);data+=f'trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n'.encode();path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)

CASES=[
 {'id':'primary-study','unit':'Primary study','title':'Synthetic classroom study of language feedback','rid':'P001','purpose':'Illustrate a primary-study workflow inspired by TALL; no actual TALL data.',
 'fields':[('assignment','Assignment procedure','Report how groups were formed.','source_extraction','Intact classes','Intact classes received the feedback intervention.'),('randomized','Random allocation','Code Yes only when random assignment is reported.','descriptive_coding','No','Random assignment was not used.')], 'rule':True},
 {'id':'review-level','unit':'Review report','title':'Synthetic review of learner agency measures','rid':'MR001','purpose':'Illustrate a review-level workflow inspired by Agency; no actual Agency data.',
 'fields':[('measurement','Measurement types','Extract measurement categories reported by this review.','source_extraction','Self-report and trace','We classified outcomes as self-report or behavioural trace.'),('evidence_level','Evidence level','Classify what this source provides; do not treat review summaries as newly analysed primary data.','descriptive_coding','Review-level synthesis','This review synthesizes previously published studies.')], 'rule':False},
 {'id':'field-report','unit':'Archaeological field report','title':'Synthetic excavation report of ceramic remains','rid':'F001','purpose':'Transfer test outside the two motivating review domains.',
 'fields':[('material','Reported material','Extract the named material from the source.','source_extraction','Ceramic','The recovered objects were ceramic fragments.'),('context','Context documentation','Code Documented when a stratigraphic context is reported.','descriptive_coding','Documented','All fragments were recorded in stratigraphic layer three.')], 'rule':False}
]

def generate(out,render=False):
    out=Path(out).resolve();rw.require(not out.exists(),'Use a new demo output directory')
    results=[]
    for case in CASES:
        project=out/(case['id']+'-project');c=rw.read(ROOT/'review-evidence-workflow/assets/review-config.template.json')
        c.update(project_id=case['id'],title=case['title'],status='ready',unit_of_analysis=case['unit'])
        c['review_round']={'id':'demo-round-1','purpose':case['purpose']};c['research']['decision_rule']=case['purpose'];c['codebook_governance'].update(provided_by='SYNTHETIC EXAMPLE TEAM',source='Illustrative fixture definitions; not a real human research protocol',development_status='calibrating')
        c['verification']['min_reviewers']=1;c['verification']['reviewer_profiles']={'reviewer-a':{'mode':'assisted_verification','ui':{'instructions':'Demo: verify the synthetic proposals against the one-page fictional source.'}},'reviewer-b':{'mode':'independent_review','ui':{'title':case['title']+' — independent','instructions':'Demo: read the fictional source and enter your own answers.'}}}
        c['fields']=[];items=[]
        for fid,label,definition,layer,value,quote in case['fields']:
            f=dict(id=fid,label=label,definition=definition,stage='extraction',layer=layer,required=True)
            if fid=='randomized':f['options']=['Yes','No']
            if fid=='context':f['options']=['Documented','Not documented']
            c['fields'].append(f);items.append(dict(field_id=fid,status='proposed',value=value,rationale='Synthetic worked example applying the illustrated rule.',evidence=[dict(pdf_page=1,section='Methods or findings',quote=quote)]))
        if case['rule']:c['derived_rules']=[dict(id='allocation-example',operation='all_equal',fields=['randomized'],required_value='Yes',failure_values=['No'],success='RANDOMIZED',failure='NOT_RANDOMIZED',unresolved='UNRESOLVED')]
        source=project/'sources'/(case['rid']+'.pdf');write_pdf(source,[case['title']]+[f[-1] for f in case['fields']])
        b={k:c[k] for k in ('schema_version','project_id','protocol_version','codebook_version')};b.update(assignment_id='demo-round-1',records=[dict(record_id=case['rid'],title=case['title'],source=dict(path='sources/'+source.name,sha256=rw.sha(source),page_count=1,identity_status='matched'),items=items)],outputs=[])
        rw.save(project/'review-config.json',c);rw.save(project/'bundle.json',b)
        with (project/'record_state.csv').open('w',newline='') as stream:
            w=csv.DictWriter(stream,fieldnames=['ID','title','DOI','pdf_filename','identity_status']);w.writeheader();w.writerow(dict(ID=case['rid'],title=case['title'],DOI='',pdf_filename=source.name,identity_status='accepted'))
        for reviewer,label in [('reviewer-a','assisted'),('reviewer-b','independent')]:results.append(rw.build(project,out/(case['id']+'-'+label),reviewer,render))
    rw.save(out/'demo-manifest.json',{'synthetic_only':True,'packages':results});return results

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',required=True);ap.add_argument('--render-pages',action='store_true');a=ap.parse_args();print(json.dumps(generate(a.out,a.render_pages),indent=2))
