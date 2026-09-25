import importlib.util, json, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('demo',ROOT/'examples/make_examples.py');demo=importlib.util.module_from_spec(spec);spec.loader.exec_module(demo)
rw=demo.rw
class Transfer(unittest.TestCase):
 def test_three_domains_both_modes_and_source_bridge(self):
  import prepare_sources as ps
  with tempfile.TemporaryDirectory(prefix='portable review ') as tmp:
   out=Path(tmp)/'demonstration';results=demo.generate(out);self.assertEqual(len(results),6)
   for case in demo.CASES:
    project=out/(case['id']+'-project');c,b,items=rw.load_project(project,True);self.assertEqual(c['unit_of_analysis'],case['unit']);self.assertEqual(len(items),2)
    payload=rw.package_payload(c,b,items,'reviewer-b',False);self.assertTrue(all(set(it)=={'field_id','status'} for r in payload['bundle']['records'] for it in r['items']))
    r=ps.prepare(project/'record_state.csv',project/'sources',out/(case['id']+'-handoff'));self.assertEqual(r['accepted'],1)
 def test_fresh_project_cannot_invent_reviewer_release(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/'demo';demo.generate(out);c,b,items=rw.load_project(out/'field-report-project',True)
   comparison=rw.comparison_from_returns(c,b,items,[],[]);self.assertEqual(comparison['counts']['pending'],2)
   with self.assertRaises(ValueError):rw.finalize(c,b,items,comparison,{**rw.binding(c,b),'comparison_sha256':rw.digest(comparison),'decisions':[]})
if __name__=='__main__':unittest.main(verbosity=2)
