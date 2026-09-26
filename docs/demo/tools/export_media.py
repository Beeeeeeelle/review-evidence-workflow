"""Export a finished render, timed captions, chapters and a readable transcript."""
import argparse,json,shutil,subprocess
from pathlib import Path

def timestamp(seconds,sep=','):
    ms=round(seconds*1000)
    return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02}{sep}{ms%1000:03}'

def export(build,destination,stem,lang,source):
    timeline=json.loads((build/'timeline.json').read_text())
    movie=build/source
    duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(movie)],text=True))
    expected=timeline[-1]['start']+timeline[-1]['duration']
    if abs(duration-expected)>.15:raise ValueError(f'Incomplete render: {duration} vs {expected}')
    destination.mkdir(parents=True,exist_ok=True)
    shutil.copy2(movie,destination/f'{stem}.{lang}.mp4')
    chapters=[];srt=[];vtt=['WEBVTT',''];transcript=['# '+('解说全文' if lang=='zh-CN' else 'Narration transcript'),'']
    previous=None
    for i,p in enumerate(timeline):
        if p['chapter']!=previous:
            chapters.append({'number':p['chapter'],'title':p['title'],'start':p['start']})
            transcript.extend(['## '+p['title'],''])
        a=p['start']+.45;b=a+p['speech_duration']
        srt.extend([str(i+1),timestamp(a)+' --> '+timestamp(b),p['speech'],''])
        vtt.extend([timestamp(a,'.')+' --> '+timestamp(b,'.'),p['speech'],''])
        transcript.extend([p['speech'],'']);previous=p['chapter']
    (destination/f'{stem}.{lang}.srt').write_text('\n'.join(srt))
    (destination/f'{stem}.{lang}.vtt').write_text('\n'.join(vtt))
    (destination/f'chapters.{lang}.json').write_text(json.dumps({'duration':duration,'chapters':chapters},ensure_ascii=False,indent=2)+'\n')
    (destination/f'TRANSCRIPT.{lang}.md').write_text('\n'.join(transcript))
    return {'duration':duration,'chapters':chapters}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--build',type=Path,required=True);p.add_argument('--destination',type=Path,required=True);p.add_argument('--stem',required=True);p.add_argument('--lang',required=True);p.add_argument('--source',required=True)
    a=p.parse_args();v=export(a.build,a.destination,a.stem,a.lang,a.source);print(json.dumps({'seconds':v['duration'],'chapters':len(v['chapters'])}))
