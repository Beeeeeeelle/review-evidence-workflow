"""Problem-first opening, kept separate from the approved long-form films.

Uses generated Belle concept art and unchanged public Pilot captures.
Requires Pillow, edge-tts (voice step only), ffmpeg and the companion
render_belle.py. All annotations and camera moves are editorial overlays.
"""
import argparse, asyncio, functools, hashlib, json, math, subprocess, wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
import render_belle as b

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT.parents[1]/'assets/review-opening-belle黑色彗星'
FPS=24

@functools.lru_cache(maxsize=24)
def layer_asset(name):
    # Alpha-bounds are only a compositing viewport; original assets are not edited.
    im=Image.open(ART/'layers'/f'{name}.png').convert('RGBA')
    # Ignore near-transparent generation specks when determining the viewport.
    bounds=im.getchannel('A').point(lambda a:255 if a>96 else 0).getbbox()
    return im.crop(bounds)

def layer(im,name,box,t,delay=0,direction=(0,30),duration=.65):
    k=b.ease((t-delay)/duration)
    if k<=0:return
    obj=ImageOps.contain(layer_asset(name),(box[2]-box[0],box[3]-box[1]),Image.Resampling.LANCZOS)
    alpha=obj.getchannel('A').point(lambda a:round(a*k));obj.putalpha(alpha)
    x=round(box[0]+(box[2]-box[0]-obj.width)/2+direction[0]*(1-k))
    y=round(box[1]+(box[3]-box[1]-obj.height)/2+direction[1]*(1-k))
    im.paste(obj,(x,y),obj)

def path(d,points,progress,color=b.ORANGE,width=3):
    if progress<=0:return
    smooth=[]
    for i in range(len(points)-1):
        a=points[max(0,i-1)];c=points[i];e=points[i+1];f=points[min(len(points)-1,i+2)]
        for j in range(20):
            t=j/20
            smooth.append(tuple(.5*((2*c[k])+(-a[k]+e[k])*t+(2*a[k]-5*c[k]+4*e[k]-f[k])*t*t+(-a[k]+3*c[k]-3*e[k]+f[k])*t*t*t) for k in (0,1)))
    points=smooth+[points[-1]]
    n=(len(points)-1)*min(1,progress);full=int(n)
    visible=points[:full+1]
    if full<len(points)-1:
        a,c=points[full:full+2];f=n-full;visible.append((a[0]+(c[0]-a[0])*f,a[1]+(c[1]-a[1])*f))
    if len(visible)>1:d.line(visible,fill=color,width=width,joint='curve')

def note(im,label,box,color,t,delay,direction):
    # These are simple editorial feedback tokens, not screenshots or Belle artwork.
    k=b.ease((t-delay)/.65)
    if k<=0:return
    w,h=box[2]-box[0],box[3]-box[1];card=Image.new('RGBA',(w+8,h+8),(255,255,255,0));d=ImageDraw.Draw(card)
    points=[(3,5),(w-3,2),(w+2,h-2),(7,h+3),(3,5)]
    d.polygon(points,fill='white');d.line(points,fill=b.INK,width=2)
    d.text((24,18),label,font=b.font(29,True),fill=color)
    for i,length in enumerate([w-75,w-105,w-60]):
        d.line((26,65+i*22,length,64+i*22),fill=color,width=2)
    card.putalpha(card.getchannel('A').point(lambda a:round(a*k)))
    im.paste(card,(round(box[0]+direction*(1-k)),box[1]),card)

def animate_pain(im,p,t):
    i=p['active'];d=ImageDraw.Draw(im)
    if i==0:
        layer(im,'01-papers',(100,252,1500,691),t,0,(-45,0))
        layer(im,'01-gate',(956,380,1105,650),t,.5,(0,35))
        # The path grows toward the hand, then toward the blocked access route.
        points=[(290,420),(368,450),(435,540),(538,570),(656,598),(741,578),(901,577),(978,574),(1102,574),(1170,541),(1262,505),(1370,568)]
        path(d,points,b.ease((t-1.3)/1.35))
        layer(im,'01-belle',(580,255,923,690),t,.95,(0,28))
    elif i==1:
        note(im,'Code?',(1190,282,1450,430),b.INK,t,0,35)
        layer(im,'02-paper',(445,215,1060,708),t,.5,(0,28))
        layer(im,'02-belle',(512,390,790,668),t,1.0,(-28,0))
        path(d,[(1205,409),(1136,438),(1067,488),(1007,555),(916,581),(816,584)],b.ease((t-1.45)/1.0))
        if t>2:
            k=b.ease((t-2)/.6);d.arc((777,558,874,611),-30,-30+340*k,fill=b.BLUE,width=3)
            b.text(d,b.tx('原文在哪里？','Where in the source?'),1120,514,390,27,color=b.BLUE)
    else:
        # Two independent returns enter from opposite directions before comparison.
        note(im,'A',(135,441,455,604),b.BLUE,t,0,-105)
        note(im,'B',(1145,441,1465,604),b.ORANGE,t,.5,105)
        layer(im,'03-belle-notebook',(538,228,1060,714),t,1.0,(0,30))
        path(d,[(458,530),(505,530),(558,560),(634,566)],b.ease((t-1.5)/.85),b.BLUE)
        path(d,[(1141,530),(1092,530),(1041,560),(965,566)],b.ease((t-1.7)/.85))
        if t>2.15:b.text(d,b.tx('分歧，要回到证据里讨论。','Bring disagreements back to evidence.'),147,652,370,25,color=b.GREY,maxheight=75)

def run(args):
    return subprocess.run(args,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

async def voice(parts,build,lang):
    import edge_tts
    speaker='en-US-JennyNeural' if lang=='en' else 'zh-CN-XiaoxiaoNeural'
    rate='+2%';sem=asyncio.Semaphore(3)
    async def one(i,p):
        target=build/f'voice-{i:02}.mp3';stamp=target.with_suffix('.sha256')
        digest=hashlib.sha256((speaker+'|'+rate+'|'+p['speech']).encode()).hexdigest()
        if target.exists() and stamp.exists() and stamp.read_text()==digest:return
        async with sem:
            for attempt in range(3):
                try:
                    await asyncio.wait_for(edge_tts.Communicate(p['speech'],speaker,rate=rate).save(str(target)),45)
                    stamp.write_text(digest);print(f'{lang} voice {i+1}/{len(parts)}',flush=True);return
                except Exception:
                    if attempt==2:raise
                    await asyncio.sleep(1)
    await asyncio.gather(*(one(i,p) for i,p in enumerate(parts)))

def timing(parts,build):
    raw=bytearray();start=0;timeline=[]
    for i,p in enumerate(parts):
        pcm=run(['ffmpeg','-v','error','-i',str(build/f'voice-{i:02}.mp3'),'-f','s16le','-ar','24000','-ac','1','pipe:1']).stdout
        lead=.18;tail=.32 if p['kind']=='pain' else .5
        n=math.ceil((len(pcm)/48000+lead+tail)*FPS);duration=n/FPS
        raw.extend(b'\0'*round(lead*24000)*2);raw.extend(pcm)
        raw.extend(b'\0'*(round(duration*24000)*2-round(lead*24000)*2-len(pcm)))
        timeline.append(dict(p,index=i,start=start,duration=duration,nframes=n))
        start+=duration
    with wave.open(str(build/'narration.wav'),'wb') as f:
        f.setparams((1,2,24000,0,'NONE','not compressed'));f.writeframes(raw)
    (build/'timeline.json').write_text(json.dumps(timeline,ensure_ascii=False,indent=2)+'\n')
    return timeline

def frame(p,t):
    if p['kind']=='ui':return b.ui(p,t)
    im,d=b.base(p)
    if p['kind']=='pain':
        b.text(d,p['headline'],64,98,1472,64,bold=True,maxheight=110)
        animate_pain(im,p,t)
        d=ImageDraw.Draw(im)
        for i,label in enumerate(b.tx(['找全文','查原文','对反馈'],['Find the file','Find the evidence','Reconcile returns'])):
            x=64+i*503;color=b.ORANGE if i==p['active'] else b.LINE
            d.line((x,746,x+450,746),fill=color,width=3 if i==p['active'] else 1)
            b.text(d,label,x,757,450,20,color=b.INK if i==p['active'] else b.QUIET)
        note=b.tx('Belle 概念插画 · 三个常见的来回','Belle concept illustration · three recurring frictions')
    elif p['kind']=='pair':
        b.text(d,b.tx('把这些来回，接成一条路。','Connect the work around the review.'),64,100,1450,56,bold=True,maxheight=120)
        for i,(title,desc) in enumerate(zip(['Literature PDF\nRetrieval','Review Evidence\nWorkflow'],b.tx(['找全文 · 核对来源','按人的规则准备 · 核验 · 回传'],['Retrieve full texts · check identity','Prepare from your rules · verify · return']))):
            x=64+i*790;active=i==p['active']
            d.text((x,280),f'0{i+1}',font=b.font(64,True),fill=b.ORANGE if active else b.QUIET)
            b.text(d,title,x,378,675,52,bold=True,leading=1.08,maxheight=145)
            b.text(d,desc,x,559,675,29,color=b.INK if active else b.GREY,maxheight=100)
            d.line((x,676,x+674,676),fill=b.ORANGE if active else b.LINE,width=3 if active else 1)
        b.arrow(d,(743,311),(835,311),b.ORANGE,b.ease(t/.8))
        note=b.tx('从你当前的阶段开始；已有全文可直接进入核对与审阅','Start at your current stage; existing PDFs can enter checking and review')
    else:
        b.text(d,b.tx('让 AI 做准备。\n让人有依据地判断。','AI prepares the work.\nPeople make the judgments.'),64,126,1430,66,bold=True,leading=1.16,maxheight=200)
        for i,label in enumerate(b.tx(['人发展规则','人核验证据','人讨论分歧'],['Develop the rules','Verify the evidence','Resolve disagreements'])):
            x=64+i*503;d.line((x,434,x+443,434),fill=b.ORANGE if i==min(2,int(t/1.4)) else b.LINE,width=2)
            b.text(d,label,x,464,446,35,bold=True,maxheight=90)
        b.text(d,b.tx('接下来 → 两个 skill 怎么用','NEXT → How to use the two skills'),64,662,1400,30,color=b.BLUE)
        note=b.tx('可追溯帮助人检查；不等于答案自动正确','Traceability supports checking; it does not guarantee correctness')
    return b.footer(im,p,note)

def clock(t,sep='.'):
    ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02}{sep}{ms%1000:03}'

def export(parts,lang):
    media=ROOT/'media';media.mkdir(exist_ok=True)
    captions=['WEBVTT\n'];srt=[];chapters=[];transcript=[]
    for i,p in enumerate(parts):
        start=p['start'];end=start+p['duration']
        # Two short caption chunks are easier to read than a paragraph cue.
        chunks=b.lines(p['speech'],28,1300)
        weights=[max(1,len(s)) for s in chunks];at=start
        for chunk,weight in zip(chunks,weights):
            until=at+p['duration']*weight/sum(weights)
            captions.append(f'{clock(at)} --> {clock(until)}\n{chunk}\n')
            srt.append(f'{len(srt)+1}\n{clock(at,",")} --> {clock(until,",")}\n{chunk}\n');at=until
        if not chapters or chapters[-1]['number']!=p['chapter']:
            chapters.append(dict(number=p['chapter'],start=round(start,5),title=p['title']))
            transcript.append(f'\n## {int(start)//60:02}:{int(start)%60:02} · {p["title"]}\n')
        transcript.append(p['speech']+'\n')
    (media/f'opening.{lang}.vtt').write_text('\n'.join(captions))
    (media/f'opening.{lang}.srt').write_text('\n'.join(srt))
    title=b.tx('从痛点开始，马上看真实例子','The problem, then a real example')
    (ROOT/'opening'/f'TRANSCRIPT.{lang}.md').write_text('# '+title+'\n\n'+b.tx('新开场。后续两段详细视频保持原样。','New opening. The two detailed films remain unchanged.')+'\n'+'\n'.join(transcript))
    metadata=dict(kind='opening',lang=lang,duration=parts[-1]['start']+parts[-1]['duration'],src=f'media/opening.{lang}.mp4',poster=f'media/opening.{lang}.jpg',transcript=f'opening/TRANSCRIPT.{lang}.md',guide=f'README.{lang}.md' if lang!='en' else 'README.md',captions=f'media/opening.{lang}.vtt',chapters=chapters)
    (ROOT/'opening'/f'chapters.{lang}.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')

def render(parts,build,lang):
    out=ROOT/'media'/f'opening.{lang}.mp4'
    proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1600x900','-r',str(FPS),'-i','pipe:0','-i',str(build/'narration.wav'),'-map','0:v','-map','1:a','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','112k','-ar','48000','-af','loudnorm=I=-16:TP=-1.5:LRA=9','-movflags','+faststart','-shortest',str(out)],stdin=subprocess.PIPE)
    for p in parts:
        for n in range(p['nframes']):proc.stdin.write(frame(p,n/FPS).tobytes())
        print(f'{lang} scene {p["index"]+1}/{len(parts)}',flush=True)
    proc.stdin.close()
    if proc.wait():raise RuntimeError('ffmpeg render failed')
    frame(parts[0],2).save(ROOT/'media'/f'opening.{lang}.jpg',quality=94)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['voice','preview','render']);ap.add_argument('--lang',choices=['en','zh-CN'],required=True);ap.add_argument('--build',type=Path,required=True)
    args=ap.parse_args();args.build.mkdir(parents=True,exist_ok=True)
    b.LANG=args.lang;b.KIND='pilot';b.COUNT=6
    parts=json.loads((ROOT/'opening'/f'storyboard.{args.lang}.json').read_text())
    if args.mode=='voice':asyncio.run(voice(parts,args.build,args.lang));timing(parts,args.build)
    else:
        parts=json.loads((args.build/'timeline.json').read_text())
        for p in parts:frame(p,3).save(args.build/f'preview-{p["index"]:02}.jpg',quality=92)
        export(parts,args.lang)
        if args.mode=='render':render(parts,args.build,args.lang)
    if b.OVERFLOWS:raise ValueError('Text overflow: '+str(b.OVERFLOWS))
