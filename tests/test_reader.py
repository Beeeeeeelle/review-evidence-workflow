import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('reader_demo', ROOT / 'examples/make_examples.py')
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

class Reader(unittest.TestCase):
    def test_quote_locator(self):
        subprocess.run(['node', str(ROOT / 'tests/test_reader.js')], check=True)

    @unittest.skipUnless(importlib.util.find_spec('pdfplumber'), 'optional pdfplumber not installed')
    def test_source_bound_glyphs_and_offline_package(self):
        from pdf_text import extract_pdf_words
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / 'demo'
            demo.generate(dest, True)
            package = dest / 'review-level-assisted'
            raw = (package / 'data.js').read_text()
            data = json.loads(raw.removeprefix('window.REVIEW_DATA = ').strip().removesuffix(';'))
            record = data['bundle']['records'][0]
            coords = record['source']['text_coordinates']
            self.assertEqual(coords['source_sha256'], record['source']['sha256'])
            words = coords['pages']['1']
            self.assertTrue(any(w['text'] == 'self-report' for w in words))
            self.assertTrue(all(0 <= w['x'] < 1 and 0 <= w['y'] < 1 and 0 < w['h'] < .03 for w in words))
            self.assertTrue((package / 'evidence-reader.js').exists())
            self.assertTrue((package / 'evidence-reader.css').exists())
            blank = dest / 'review-level-independent'
            self.assertNotIn('Synthetic worked example applying', (blank / 'data.js').read_text())

if __name__ == '__main__': unittest.main()
