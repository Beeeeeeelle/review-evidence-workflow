import copy, csv, json, subprocess, sys, tempfile, unittest
from pathlib import Path
from test_workflow import rw, fixture
import test_workflow as base
sys.path.insert(0,str(rw.ROOT/'scripts'))
import prepare_sources as ps

def pdf(path,lines):
    lines=['SYNTHETIC EXAMPLE - not research data']+lines
    body='BT /F1 11 Tf 40 750 Td '+' '.join(('0 -20 Td ' if i else '')+'('+x.replace('\\','\\\\').replace('(','\\(').replace(')','\\)')+') Tj' for i,x in enumerate(lines))+' ET'
    objects=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',('<< /Length '+str(len(body.encode()))+' >>\nstream\n'+body+'\nendstream').encode()]
    data=b'%PDF-1.4\n';offsets=[0]
    for n,obj in enumerate(objects,1): offsets.append(len(data));data+=str(n).encode()+b' 0 obj\n'+obj+b'\nendobj\n'
    start=len(data);data+=b'xref\n0 6\n0000000000 65535 f \n'+b''.join(f'{o:010} 00000 n \n'.encode() for o in offsets[1:]);data+=f'trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n'.encode();path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)

class Reuse(unittest.TestCase):
    setUp=base.Workflow.setUp
    tearDown=base.Workflow.tearDown
    write=base.Workflow.write
    invalid=base.Workflow.invalid
    ret=base.Workflow.ret
    decisions=base.Workflow.decisions
    def configure(self,mode='independent_review',blank=False):
        self.c['verification']['mode']=mode
        if blank:
            for it in self.b['records'][0]['items']:it.update(status='not_assessed',value=None,evidence=[])
        self.write();self.c,self.b,self.items=rw.load_project(self.p)
    def actual_source(self):
        path=self.p/'sources/R1.pdf';pdf(path,['Synthetic classroom study of learning feedback','Intact classes received a feedback intervention.']);self.b['records'][0]['source']['sha256']=rw.sha(path);self.write()
    def independent_return(self,reviewer='reviewer-a',value='Yes'):
        return {**rw.package_binding(self.c,self.b,self.items,reviewer),'reviewer_id':reviewer,'exported_at':'TEST','responses':[dict(key=k,action='submit',committed=True,value=value,missingness=None,rationale='Synthetic interpretation',comment='',reviewed_at='TEST',evidence=[dict(pdf_page=1,section='Fixture',quote='Synthetic evidence.')]) for k in rw.assigned_keys(self.c,self.b,self.items,reviewer)]}
    def test_independent_blank_codebook_development(self):
        self.configure(blank=True);self.assertEqual(len(rw.assigned_keys(self.c,self.b,self.items,'reviewer-a')),2)
        r=self.independent_return();self.assertEqual(rw.validate_return(r,self.c,self.b,self.items)['responded'],2)
    def test_independent_payload_does_not_ship_hidden_content(self):
        self.configure();self.b['records'][0]['items'][0]['rationale']='SECRET_AI_RATIONALE';self.b['records'][0]['items'][0]['evidence'][0]['quote']='SECRET_QUOTE';self.b['records'][0]['feedback']='SECRET_OTHER_REVIEWER';self.c['verification']['reviewer_profiles']={'reviewer-a':{'field_ids':['a'],'ui':{'title':'Personal worksheet'}}};self.c['verification']['min_reviewers']=1
        payload=rw.package_payload(self.c,self.b,self.items,'reviewer-a',False);raw=json.dumps(payload)
        self.assertNotIn('SECRET',raw);self.assertNotIn('reviewer-b',raw);self.assertEqual(payload['bundle']['records'][0]['items'],[{'field_id':'a','status':'awaiting_human'}]);self.assertEqual(len(payload['config']['fields']),1)
    def test_independent_rejects_accept_or_draft(self):
        self.configure()
        for update in ({'action':'accept'},{'committed':False},{'rationale':''},{'value':'Invented'},{'evidence':[]}):
            with self.subTest(update=update):
                r=self.independent_return();r['responses'][0].update(update)
                with self.assertRaises(ValueError):rw.validate_return(r,self.c,self.b,self.items)
    def test_independent_concordance_is_not_release(self):
        self.configure(blank=True);rs=[self.independent_return(),self.independent_return('reviewer-b')];x=rw.comparison_from_returns(self.c,self.b,self.items,rs,[])
        self.assertEqual(x['counts']['concordant_independent_values'],2);result=rw.finalize(self.c,self.b,self.items,x,self.decisions(x));self.assertFalse(result['complete'])
        events=[dict(key=k,disposition='select_review',reviewer_id='reviewer-a',rationale='TEST human selection') for k in self.items];result=rw.finalize(self.c,self.b,self.items,x,self.decisions(x,events));self.assertTrue(result['complete'])
    def test_independent_disagreement_requires_adjudication(self):
        self.configure();x=rw.comparison_from_returns(self.c,self.b,self.items,[self.independent_return(),self.independent_return('reviewer-b','No')],[]);self.assertEqual(x['counts']['needs_adjudication'],2)
        with self.assertRaises(ValueError):rw.finalize(self.c,self.b,self.items,x,self.decisions(x,[dict(key='R1/a',disposition='retain',rationale='Cannot retain hidden AI')]))
    def test_selected_evidence_change_invalidates_dependents_even_same_value(self):
        self.configure();a=self.independent_return();b=self.independent_return('reviewer-b')
        for ret in (a,b):ret['responses'][0]['evidence'][0]['quote']='Newly checked source passage.'
        comp=rw.comparison_from_returns(self.c,self.b,self.items,[a,b],[])
        events=[dict(key=k,disposition='select_review',reviewer_id='reviewer-a',rationale='TEST adjudication') for k in self.items]
        result=rw.finalize(self.c,self.b,self.items,comp,self.decisions(comp,events))
        self.assertEqual(result['items'][1]['status'],'stale_requires_reverification')
        self.assertEqual(result['outputs'][0]['status'],'stale_requires_recompute')
    def test_mixed_modes_are_not_independent_agreement(self):
        self.c['verification']['reviewer_profiles']={'reviewer-b':{'mode':'independent_review'}};self.write();self.c,self.b,self.items=rw.load_project(self.p)
        a={**rw.package_binding(self.c,self.b,self.items,'reviewer-a'),**{'reviewer_id':'reviewer-a','exported_at':'TEST','responses':self.ret()['responses']}}
        x=rw.comparison_from_returns(self.c,self.b,self.items,[a,self.independent_return('reviewer-b')],[]);self.assertEqual(x['counts']['needs_adjudication'],2)
    def test_profile_cannot_leave_coverage_impossible(self):
        self.c['verification']['reviewer_profiles']={'reviewer-a':{'field_ids':['a']}};self.invalid()
    def test_scoped_return_rejects_extra_field(self):
        self.configure();self.c['verification']['min_reviewers']=1;self.c['verification']['reviewer_profiles']={'reviewer-a':{'field_ids':['a']}};r=self.independent_return();r['responses'].append(dict(r['responses'][0],key='R1/b'))
        with self.assertRaises(ValueError):rw.validate_return(r,self.c,self.b,self.items)
    def test_new_round_preserves_source_and_rejects_old_returns(self):
        self.configure();self.actual_source();old=self.independent_return();dest=self.p/'round2';rw.new_round(self.p,dest,'round2','AI applies human-led codebook',mode='assisted_verification');c,b,items=rw.load_project(dest,True)
        self.assertEqual(c['verification']['mode'],'assisted_verification');self.assertEqual(b['records'][0]['source']['sha256'],self.b['records'][0]['source']['sha256'])
        with self.assertRaises(ValueError):rw.validate_return(old,c,b,items)
    def test_codebook_revision_invalidates_proposals(self):
        self.actual_source();dest=self.p/'round2';rw.new_round(self.p,dest,'round2','Recalibrate',codebook_version='2');c,b,items=rw.load_project(dest,True);self.assertFalse(rw.reviewable(items))
        with self.assertRaises(ValueError):rw.build(dest,self.p/'package','reviewer-a')
    def test_independent_package_only_copies_assigned_pdfs(self):
        self.configure();self.actual_source();second=copy.deepcopy(self.b['records'][0]);second['record_id']='R2';second['items'][1]['depends_on']=['R2/a'];self.b['records'].append(second);self.c['verification']['min_reviewers']=1;self.c['verification']['reviewer_profiles']={'reviewer-a':{'record_ids':['R1']},'reviewer-b':{'record_ids':['R2']}};self.write();out=self.p/'package';rw.build(self.p,out,'reviewer-a');self.assertEqual([p.name for p in (out/'sources').iterdir()],['R1.pdf'])

class Sources(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.p=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def audit(self,rows):
        with (self.p/'audit.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=['ID','title','DOI','identity_status','access_reason']);w.writeheader();w.writerows(rows)
    def row(self,id='P1',**kw):return dict(ID=id,title='Synthetic classroom study of learning feedback',DOI='',identity_status='accepted',access_reason='',**kw)
    def test_valid_handoff_seed_and_independent_build(self):
        pdf(self.p/'P1.pdf',[self.row()['title'],'Intact classes received feedback.']);self.audit([self.row()]);out=self.p/'handoff';r=ps.prepare(self.p/'audit.csv',self.p,out);self.assertEqual(r['accepted'],1)
        c,b=fixture();c['verification']['mode']='independent_review';rw.save(self.p/'config.json',c);rw.seed(self.p/'config.json',out/'sources-manifest.json',self.p/'round','pilot');rw.build(self.p/'round',self.p/'package','reviewer-a');self.assertTrue((self.p/'package/OPEN_ME.html').exists())
    def test_wrong_pdf_and_missing_are_queued(self):
        pdf(self.p/'P1.pdf',['Another unrelated report','doi: 10.1234/wrong']);a=self.row();a['DOI']='10.1234/target';self.audit([a,self.row('P2')]);r=ps.prepare(self.p/'audit.csv',self.p,self.p/'out');self.assertEqual(r['accepted'],0);self.assertEqual(r['unresolved_or_excluded'],2)
    def test_duplicate_hashes_not_promoted(self):
        pdf(self.p/'P1.pdf',[self.row()['title']]);(self.p/'P2.pdf').write_bytes((self.p/'P1.pdf').read_bytes());self.audit([self.row(),self.row('P2')]);r=ps.prepare(self.p/'audit.csv',self.p,self.p/'out');self.assertEqual(r['accepted'],0)
    def test_report_hash_is_rechecked(self):
        pdf(self.p/'P1.pdf',[self.row()['title']]);self.audit([self.row()]);rw.save(self.p/'report.json',{'results':[{'id':'P1','sha256':'0'*64,'pages':1,'structural':'pass','identity':'pass'}]});r=ps.prepare(self.p/'audit.csv',self.p,self.p/'out',validation=self.p/'report.json');self.assertEqual(r['accepted'],0)
    def test_replaced_source_invalidates_old_coding(self):
        pdf(self.p/'P1.pdf',[self.row()['title']]);self.audit([self.row()]);rw.save(self.p/'old.json',{'records':[{'record_id':'P1','source':{'sha256':'0'*64},'items':[{'field_id':'design'}]}]});r=ps.prepare(self.p/'audit.csv',self.p,self.p/'out',previous_bundle=self.p/'old.json');self.assertEqual(r['invalidated_records'],1)
    def test_ambiguous_identity_needs_human_record(self):
        pdf(self.p/'P1.pdf',['A short title']);a=self.row();a['title']='A short title';self.audit([a]);r=ps.prepare(self.p/'audit.csv',self.p,self.p/'out');self.assertEqual(r['accepted'],0)
        rw.save(self.p/'identity.json',[dict(record_id='P1',source_sha256=rw.sha(self.p/'P1.pdf'),human_confirmed=True,confirmed_by='SYNTHETIC TEST',confirmed_at='TEST',reason='Synthetic manual identity check')]);r=ps.prepare(self.p/'audit.csv',self.p,self.p/'out2',identity_decisions=self.p/'identity.json');self.assertEqual(r['accepted'],1)

if __name__=='__main__':unittest.main(verbosity=2)
