#!/usr/bin/env python3
"""Local preview with byte ranges so video chapter links can seek."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Mount the sibling introduction without exposing the rest of the project.
        parts = [part for part in unquote(urlsplit(path).path).split('/') if part not in ('', '.', '..')]
        root = Path(self.directory).resolve()
        if parts and parts[0] == 'intro':
            root = root.parent / 'intro'
            parts = parts[1:]
        elif parts and parts[0] == 'demo':
            parts = parts[1:]
        candidate = root.joinpath(*parts).resolve()
        return str(candidate if candidate.is_relative_to(root.resolve()) else root / '.unavailable')

    def send_head(self):
        self.remaining = None
        path = Path(self.translate_path(self.path))
        if path.suffix != '.mp4' or not path.is_file(): return super().send_head()
        size = path.stat().st_size
        start, end = 0, size - 1
        value = self.headers.get('Range')
        if value:
            match = re.fullmatch(r'bytes=(\d*)-(\d*)', value)
            if not match or not any(match.groups()): self.send_error(416); return None
            first,last=match.groups()
            if first: start=int(first);end=min(int(last),size-1) if last else size-1
            else: start=max(0,size-int(last))
            if start>end or start>=size: self.send_error(416);return None
        self.send_response(206 if value else 200)
        self.send_header('Content-Type','video/mp4')
        self.send_header('Accept-Ranges','bytes')
        self.send_header('Content-Length',str(end-start+1))
        if value:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
        self.end_headers()
        stream=path.open('rb');stream.seek(start);self.remaining=end-start+1;return stream
    def copyfile(self,source,out):
        if self.remaining is None:return super().copyfile(source,out)
        try:
            while self.remaining:
                data=source.read(min(65536,self.remaining))
                if not data:break
                out.write(data);self.remaining-=len(data)
        except (BrokenPipeError,ConnectionResetError):pass

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8940);a=p.parse_args()
    print(f'Video walkthrough: http://127.0.0.1:{a.port}/')
    ThreadingHTTPServer(('127.0.0.1',a.port),partial(Handler,directory=str(Path(__file__).resolve().parent))).serve_forever()
