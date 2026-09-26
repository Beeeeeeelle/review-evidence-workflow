#!/usr/bin/env python3
"""Local Belle edition preview; mount only public demo/intro assets and byte ranges."""
import argparse, importlib.util
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('original_server',ROOT.parent/'demo/serve.py')
original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)
class Handler(original.Handler):
 def translate_path(self,path):
  parts=[p for p in unquote(urlsplit(path).path).split('/') if p not in ('','.','..')]
  root=ROOT
  if parts and parts[0] in ('intro','demo'):
   root=ROOT.parent/parts.pop(0)
  candidate=root.joinpath(*parts).resolve()
  return str(candidate if candidate.is_relative_to(root.resolve()) else root/'.unavailable')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8942);a=p.parse_args()
 print(f'Belle edition: http://127.0.0.1:{a.port}/',flush=True)
 ThreadingHTTPServer(('127.0.0.1',a.port),partial(Handler,directory=str(ROOT))).serve_forever()
