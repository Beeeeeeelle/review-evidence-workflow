"""Render guided video from authentic captures plus explicitly editorial overlays.

Requires Pillow, edge-tts (voice generation only), ffmpeg, ffprobe.
No UI pixels or source highlights are generated or altered. Camera crops and
orange/teal annotation layers belong to the video, not the application.
"""
import argparse, asyncio, hashlib, json, math, os, subprocess, wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
FRAMES = ROOT.parent / 'frames'
OUT = ROOT / '.build'
OUT.mkdir(exist_ok=True)
W,H,FPS,TOP = 1280,900,24,70
BG='#172026'; INK='#f4f1e9'; MUTED='#bac4c8'; ORANGE='#ffac73'; TEAL='#79d8cc'
FONT_PATH=os.environ.get('GUIDE_FONT','/System/Library/Fonts/Hiragino Sans GB.ttc')
FONTS={n:ImageFont.truetype(FONT_PATH,n) for n in (16,18,20,22,25,27,29)}
SCENES=json.loads((ROOT.parent/'storyboard.json').read_text())
PARTS=[dict(part,chapter=i+1,title=scene['title'],stage=scene['stage']) for i,scene in enumerate(SCENES) for part in scene['parts']]
for i,p in enumerate(PARTS):
    if i and PARTS[i-1]['chapter']==p['chapter']:
        p['start_camera']=PARTS[i-1].get('camera',[0,0,1280,720])

def run(args,**kw):
    return subprocess.run(args,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,**kw)

async def voices():
    import edge_tts
    sem=asyncio.Semaphore(3)
    async def one(i,p):
        target=OUT/f'voice-{i:02}.mp3'
        digest=hashlib.sha256(p['speech'].encode()).hexdigest()
        stamp=target.with_suffix('.sha256')
        if target.exists() and stamp.exists() and stamp.read_text()==digest:
            return
        async with sem:
            for attempt in range(3):
                try:
                    await asyncio.wait_for(edge_tts.Communicate(p['speech'],'zh-CN-XiaoxiaoNeural',rate='-2%').save(str(target)),45)
                    stamp.write_text(digest)
                    print(f'Voice {i+1}/{len(PARTS)} ready',flush=True)
                    return
                except Exception:
                    if attempt==2: raise
                    await asyncio.sleep(1)
    await asyncio.gather(*(one(i,p) for i,p in enumerate(PARTS)))

def timing():
    start=0; raw=bytearray(); segments=[]
    for i,p in enumerate(PARTS):
        voice=run(['ffmpeg','-v','error','-i',str(OUT/f'voice-{i:02}.mp3'),'-f','s16le','-ar','24000','-ac','1','pipe:1']).stdout
        speech_len=len(voice)/48000
        lead=.45; n=math.ceil((speech_len+lead+.55)*FPS); dur=n/FPS
        raw.extend(b'\0'*round(lead*48000))
        raw.extend(voice)
        raw.extend(b'\0'*(round(dur*24000)*2-round(lead*48000)-len(voice)))
        segments.append(dict(p,index=i,start=round(start,5),duration=dur,nframes=n,speech_duration=speech_len))
        start+=dur
    with wave.open(str(OUT/'narration.wav'),'wb') as wav:
        wav.setparams((1,2,24000,0,'NONE','not compressed')); wav.writeframes(raw)
    (OUT/'timeline.json').write_text(json.dumps(segments,ensure_ascii=False,indent=2)+'\n')
    return segments

def ease(t):
    t=max(0,min(1,t)); return t*t*(3-2*t)

def camera(p,t,dur):
    target=p.get('camera',[0,0,1280,720])
    x0,y0,x1,y1=target
    if y1>720: y0-=y1-720;y1=720
    # Short camera push gives a readable close-up, then settles.
    k=ease(t/.85)
    initial=list(p.get('start_camera',[0,0,1280,720]))
    if initial[3]>720:initial[1]-=initial[3]-720;initial[3]=720
    return [a+(b-a)*k for a,b in zip(initial,[x0,y0,x1,y1])]

def lines(text,font,width,draw):
    result=[]; current=''
    for ch in text:
        if draw.textlength(current+ch,font=font)>width and current:
            result.append(current);current=ch
        else:current+=ch
    if current:result.append(current)
    return result

def arrow(d,start,end,color,progress=1,width=4):
    sx,sy=start;ex,ey=end
    ex=sx+(ex-sx)*progress;ey=sy+(ey-sy)*progress
    d.line([(sx,sy),(ex,ey)],fill=color,width=width)
    if progress>.3:
        a=math.atan2(ey-sy,ex-sx);r=13
        d.polygon([(ex,ey),(ex-r*math.cos(a-.48),ey-r*math.sin(a-.48)),(ex-r*math.cos(a+.48),ey-r*math.sin(a+.48))],fill=color)

def render(p,t,source):
    cam=camera(p,t,p.get('duration',5));x0,y0,x1,y1=cam
    sx=W/(x1-x0);sy=720/(y1-y0)
    def pt(x,y):return ((x-x0)*sx,(y-y0)*sy+TOP)
    def box(b,pad=0):
        a,c=pt(b[0]-pad,b[1]-pad),pt(b[2]+pad,b[3]+pad)
        return [max(3,a[0]),max(TOP+3,a[1]),min(W-3,c[0]),min(TOP+717,c[1])]
    shot=source.crop(tuple(cam)).resize((W,720),Image.Resampling.BICUBIC)
    canvas=Image.new('RGB',(W,H),BG);canvas.paste(shot,(0,TOP))
    progress=ease(t/.42)
    mask=Image.new('L',(W,H),0);md=ImageDraw.Draw(mask)
    md.rectangle((0,TOP,W,TOP+720),fill=int(100*progress))
    boxes=[box(p['box'],6)]
    if p.get('second'):boxes.append(box(p['second'],6))
    for b in boxes:
        if b[2]>b[0] and b[3]>b[1]:md.rounded_rectangle(b,12,fill=0)
    canvas=Image.composite(Image.new('RGB',(W,H),'#0b1218'),canvas,mask)
    d=ImageDraw.Draw(canvas)
    d.text((25,16),p['title'],font=FONTS[29],fill=INK)
    meta=f"{p['chapter']:02d} / {len(SCENES):02d}   ·   {p['stage']}"
    mw=d.textlength(meta,font=FONTS[18]);d.text((W-mw-24,23),meta,font=FONTS[18],fill=ORANGE)
    d.line((0,TOP-1,W,TOP-1),fill='#36434b',width=1)
    # Original DEMO badge stays visible in the capture; editorial identification also stays outside it.
    label_bounds=[]
    for idx,b in enumerate(boxes):
        color=ORANGE if idx==0 else TEAL
        if b[2]<=b[0] or b[3]<=b[1]:continue
        if idx==0 and p.get('shape')=='circle':
            d.arc(b,start=-80,end=-80+359*progress,fill=color,width=4)
        else:
            d.rounded_rectangle(b,10,outline=color,width=3)
        label=p['label'] if idx==0 else p.get('second_label','对应原文')
        lw=d.textlength(label,font=FONTS[22])+30
        lx=max(12,min(W-lw-12,b[0]));ly=b[1]-48
        if ly<TOP+10:ly=b[3]+14
        if ly+39>TOP+710:ly=TOP+660
        for other in label_bounds:
            if lx<other[2] and lx+lw>other[0] and ly<other[3] and ly+39>other[1]:
                ly=max(TOP+8,other[1]-48)
        lb=[lx,ly,lx+lw,ly+39];label_bounds.append(lb)
        if t>.16:
            d.rounded_rectangle(lb,10,fill='#172026',outline=color,width=2)
            d.text((lx+15,ly+6),label,font=FONTS[22],fill=INK)
            if ly>b[3]:arrow(d,(lx+min(30,lw/2),ly),(max(b[0]+10,min(b[2]-10,lx+30)),b[3]+2),color)
            else:arrow(d,(lx+min(30,lw/2),ly+39),(max(b[0]+10,min(b[2]-10,lx+30)),b[1]-2),color)
    if p.get('link') and t>.45:
        start=pt(*p['link']);b=boxes[-1]
        end=(b[0]+8,(b[1]+b[3])/2)
        arrow(d,(start[0]+15,start[1]),end,TEAL,ease((t-.45)/.8),4)
    if p.get('click') and .25<t<1.65:
        cx,cy=pt(*p['click']);q=(t-.25)/1.4;r=10+q*29
        d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=ORANGE,width=max(1,int(5*(1-q))))
        d.ellipse((cx-4,cy-4,cx+4,cy+4),fill=ORANGE)
    if p.get('drag'):
        a,b,y=p['drag'];f=ease((t-.6)/1.5)
        start=pt(a,y);end=pt(b,y)
        arrow(d,start,end,ORANGE,ease((t-.25)/.8),5)
        px,py=pt(a+(b-a)*f,y)
        d.ellipse((px-12,py-12,px+12,py+12),fill=ORANGE,outline=INK,width=2)
    if p.get('scroll'):
        # Editorial scroll direction cue; no fabricated intermediate UI states.
        x=1237;y=TOP+425;f=(t*.65)%1
        arrow(d,(x,y-75),(x,y+65),ORANGE,1,5)
        d.ellipse((x-8,y-70+125*f,x+8,y-54+125*f),fill=ORANGE)
    d.rectangle((0,790,W,H),fill=BG)
    subtitles=lines(p['speech'],FONTS[27],1140,d)
    for j,line in enumerate(subtitles):
        tw=d.textlength(line,font=FONTS[27]);d.text(((W-tw)/2,801+j*35),line,font=FONTS[27],fill=INK)
    d.text((24,874),'真实界面 · 后期引导标注 · 演示反馈单独保存',font=FONTS[16],fill=MUTED)
    d.text((1060,874),'人核验 · AI 协助',font=FONTS[16],fill=MUTED)
    return canvas

def preview():
    for i in [0,1,3,6,10,11,12,13,18,23,26,28,30,31,33]:
        if i>=len(PARTS):continue
        p=PARTS[i];img=Image.open(FRAMES/(p['frame']+'.jpg')).convert('RGB')
        render(p,2,img).save(OUT/f'preview-{i:02}.jpg',quality=94)

def film(segments,limit=None):
    selected=segments if limit is None else segments[:limit]
    dest=OUT/('guided-video.mp4' if limit is None else 'proof.mp4')
    process=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-i',str(OUT/'narration.wav'),'-map','0:v','-map','1:a','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','112k','-ar','48000','-af','loudnorm=I=-16:TP=-1.5:LRA=9','-movflags','+faststart','-shortest',str(dest)],stdin=subprocess.PIPE)
    for s in selected:
        source=Image.open(FRAMES/(s['frame']+'.jpg')).convert('RGB')
        for n in range(s['nframes']):
            process.stdin.write(render(s,n/FPS,source).tobytes())
        print(f"Rendered {s['index']+1}/{len(selected)} — {s['title']}",flush=True)
    process.stdin.close()
    if process.wait():raise RuntimeError('ffmpeg render failed')
    print(dest,flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['voice','preview','proof','render'])
    mode=parser.parse_args().mode
    if mode=='voice':asyncio.run(voices())
    elif mode=='preview':preview()
    else:film(timing(),2 if mode=='proof' else None)
