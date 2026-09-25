import copy, importlib.util, json, tempfile, unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'review-evidence-workflow'
spec=importlib.util.spec_from_file_location('rw',P/'scripts/review_workflow.py');rw=importlib.util.module_from_spec(spec);spec.loader.exec_module(rw)

def fixture():
 c=rw.read(P/'assets/review-config.template.json');c.update(status='ready',unit_of_analysis='Synthetic report');c['codebook_governance'].update(provided_by='SYNTHETIC TEST ONLY',source='Synthetic codebook fixture');c['research']['decision_rule']='Illustrative method coding; no live review';c['fields']=[dict(id='a',label='A',definition='Reported A',stage='extraction',layer='source_extraction',required=True,options=['Yes','No']),dict(id='b',label='B',definition='Code B',stage='extraction',layer='descriptive_coding',required=True,options=['Yes','No'])];c['derived_rules']=[dict(id='gate',operation='all_equal',fields=['a'],required_value='Yes',failure_values=['No'],success='PASS',failure='FAIL',unresolved='REVIEW')]
 it=lambda f:dict(field_id=f,status='proposed',value='Yes',rationale='Synthetic fixture only',evidence=[dict(pdf_page=1,section='Fixture',quote='Synthetic evidence.')])
 b={k:c[k] for k in ['schema_version','project_id','protocol_version','codebook_version']};b.update(assignment_id='test-v1',records=[dict(record_id='R1',title='Synthetic fixture',source=dict(path='sources/R1.pdf',sha256='0'*64,page_count=1,identity_status='matched'),items=[it('a'),dict(it('b'),depends_on=['R1/a'])])],outputs=[dict(id='table1',depends_on=['R1/b'])]);return c,b

class Workflow(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.p=Path(self.tmp.name);self.c,self.b=fixture();self.write();self.c,self.b,self.items=rw.load_project(self.p)
 def tearDown(self):self.tmp.cleanup()
 def write(self):
  for n,d in [('review-config.json',self.c),('bundle.json',self.b)]: (self.p/n).write_text(json.dumps(d))
 def invalid(self):
  self.write()
  with self.assertRaises(ValueError):rw.load_project(self.p)
 def ret(self,reviewer='reviewer-a',action='accept',comment=''):
  return {**rw.binding(self.c,self.b),'reviewer_id':reviewer,'exported_at':'2026-09-25','responses':[dict(key=k,action=action,comment=comment,reviewed_at='2026-09-25') for k in self.items]}
 def comparison(self,action='accept'):
  return rw.comparison_from_returns(self.c,self.b,self.items,[self.ret(),self.ret('reviewer-b',action,'Review this' if action!='accept' else '')],[])
 def decisions(self,comp,events=[]):return {**rw.binding(self.c,self.b),'human_authorized':True,'authorized_by':'SYNTHETIC TEST ONLY','authorized_at':'2026-09-25','comparison_sha256':rw.digest(comp),'decisions':events}
 def test_valid(self):self.assertEqual(len(self.items),2)
 def test_draft(self):self.c['status']='draft';self.invalid()
 def test_independent_label_rejected(self):self.c['verification']['mode']='independent';self.invalid()
 def test_source_traversal(self):self.b['records'][0]['source']['path']='../x.pdf';self.invalid()
 def test_page_bounds(self):self.b['records'][0]['items'][0]['evidence'][0]['pdf_page']=2;self.invalid()
 def test_cycle(self):self.b['records'][0]['items'][0]['depends_on']=['R1/b'];self.invalid()
 def test_nr_needs_search_locations(self):self.b['records'][0]['items'][0].update(value='NR',missingness='NR',evidence=[]);self.invalid()
 def test_nr_valid(self):self.b['records'][0]['items'][0].update(value='NR',missingness='NR',evidence=[],checked_locations=[dict(pdf_page=1,section='Methods')]);self.write();rw.load_project(self.p)
 def test_wrong_bundle_return(self):
  r=self.ret();r['bundle_sha256']='1'*64
  with self.assertRaises(ValueError):rw.validate_return(r,self.c,self.b,self.items)
 def test_challenge_requires_comment(self):
  with self.assertRaises(ValueError):rw.validate_return(self.ret(action='revise'),self.c,self.b,self.items)
 def test_duplicate_reviewer(self):
  with self.assertRaises(ValueError):rw.comparison_from_returns(self.c,self.b,self.items,[self.ret(),self.ret()],[])
 def test_pending_coverage(self):
  x=rw.comparison_from_returns(self.c,self.b,self.items,[self.ret()],[]);self.assertEqual(x['counts']['pending'],2)
  with self.assertRaises(ValueError):rw.finalize(self.c,self.b,self.items,x,self.decisions(x,[dict(key='R1/a',disposition='retain',rationale='Test')]))
 def test_challenges_stay_unresolved(self):
  x=self.comparison('revise');result=rw.finalize(self.c,self.b,self.items,x,self.decisions(x));self.assertFalse(result['complete']);self.assertEqual(result['derived'][0]['value'],'REVIEW')
 def test_accepted_release(self):
  x=self.comparison();result=rw.finalize(self.c,self.b,self.items,x,self.decisions(x));self.assertTrue(result['complete']);self.assertEqual(result['derived'][0]['value'],'PASS')
 def test_authorization_required(self):
  x=self.comparison();d=self.decisions(x);d['human_authorized']=False
  with self.assertRaises(ValueError):rw.finalize(self.c,self.b,self.items,x,d)
 def test_comparison_cannot_override_returns(self):
  x=self.comparison('revise');x['items'][0]['state']='accepted_by_required_reviewers'
  with self.assertRaises(ValueError):rw.finalize(self.c,self.b,self.items,x,self.decisions(x))
 def test_correction_invalidates_transitive_outputs(self):
  x=self.comparison();e=dict(key='R1/a',disposition='adopt',rationale='Synthetic correction',value='No',missingness=None,evidence=[dict(pdf_page=1,section='Fixture',quote='Synthetic correction.')]);r=rw.finalize(self.c,self.b,self.items,x,self.decisions(x,[e]));self.assertEqual(r['derived'][0]['value'],'FAIL');self.assertEqual(r['items'][1]['status'],'stale_requires_reverification');self.assertEqual(r['outputs'][0]['status'],'stale_requires_recompute');self.assertFalse(r['complete'])
 def test_unassessed_blocks_completion(self):
  self.b['records'][0]['items'][1].update(status='not_assessed',value=None,evidence=[]);self.write();self.c,self.b,self.items=rw.load_project(self.p);ret=self.ret();ret['responses']=ret['responses'][:1];ret2=copy.deepcopy(ret);ret2['reviewer_id']='reviewer-b';x=rw.comparison_from_returns(self.c,self.b,self.items,[ret,ret2],[]);r=rw.finalize(self.c,self.b,self.items,x,self.decisions(x));self.assertFalse(r['complete']);self.assertEqual(r['outputs'][0]['status'],'stale_requires_recompute')
 def test_no_overwrite(self):
  rw.save(self.p/'once.json',{})
  with self.assertRaises(FileExistsError):rw.save(self.p/'once.json',{})
 def test_source_changed(self):
  (self.p/'sources').mkdir();(self.p/'sources/R1.pdf').write_bytes(b'%PDF-1.4\nmodified')
  with self.assertRaises(ValueError):rw.load_project(self.p,True)

if __name__=='__main__':unittest.main(verbosity=2)
