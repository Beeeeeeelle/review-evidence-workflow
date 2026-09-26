"""Belle editorial edition. Reuses approved narration, timing and authentic captures.

No source pixels, PDF highlights, narration or judgments are synthesized here.
Frames use a separate annotation rail; all movement is editorial camera guidance.
Requires Pillow and ffmpeg. Font paths can be supplied for non-macOS hosts.
"""
from pathlib import Path
import argparse, functools, json, math, os, re, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageOps
ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT.parent
W,H,FPS=1600,900,24
INK='#0a0a0a'; WHITE='#ffffff'; GREY='#525252'; QUIET='#737373'; LINE='#dedede'; ORANGE='#d97745'; BLUE='#5f7fa3'
LANG='en'; KIND='intro'; COUNT=12; IMAGES={}; OVERFLOWS=[]

def tx(zh,en):return en if LANG=='en' else zh
@functools.lru_cache(maxsize=160)
def font(size,bold=False,mono=False):
    if mono:return ImageFont.truetype(os.environ.get('BELLE_MONO','/System/Library/Fonts/Menlo.ttc'),size)
    en=LANG=='en'; path=os.environ.get('BELLE_FONT_EN' if en else 'BELLE_FONT_ZH','/System/Library/Fonts/HelveticaNeue.ttc' if en else '/System/Library/Fonts/Hiragino Sans GB.ttc')
    return ImageFont.truetype(path,size,index=(1 if en else 2) if bold else 0)

def lines(value,size,width,bold=False):
    d=ImageDraw.Draw(Image.new('RGB',(1,1)));result=[]; f=font(size,bold)
    for paragraph in str(value).split('\n'):
        tokens=paragraph.split() if LANG=='en' else list(paragraph); current='';sep=' ' if LANG=='en' else ''
        for token in tokens:
            candidate=(current+sep+token).strip() if LANG=='en' else current+token
            if current and d.textlength(candidate,font=f)>width:result.append(current);current=token
            else:current=candidate
        result.append(current)
    return result

def text(d,value,x,y,width,size=32,color=INK,bold=False,leading=1.3,maxheight=None):
    ls=lines(value,size,width,bold)
    if maxheight:
        while len(ls)*size*leading>maxheight and size>18:
            size-=2;ls=lines(value,size,width,bold)
        if len(ls)*size*leading>maxheight:OVERFLOWS.append(value)
    for s in ls:d.text((x,y),s,font=font(size,bold),fill=color);y+=size*leading
    return y

def ease(t):return 1-(1-max(0,min(1,t)))**4

def img(path):
    key=str(path)
    if key not in IMAGES:IMAGES[key]=Image.open(path).convert('RGB')
    return IMAGES[key]

def fit(canvas,path,box):
    shot=ImageOps.contain(img(path),(int(box[2]-box[0]),int(box[3]-box[1])),Image.Resampling.LANCZOS)
    canvas.paste(shot,(int(box[0]+(box[2]-box[0]-shot.width)/2),int(box[1]+(box[3]-box[1]-shot.height)/2)))

def arrow(d,a,b,color=ORANGE,progress=1,width=2):
    sx,sy=a;ex,ey=b;ex=sx+(ex-sx)*progress;ey=sy+(ey-sy)*progress
    d.line((sx,sy,ex,ey),fill=color,width=width)
    if progress>.2:
        ang=math.atan2(ey-sy,ex-sx);r=11
        d.line((ex-r*math.cos(ang-.48),ey-r*math.sin(ang-.48),ex,ey,ex-r*math.cos(ang+.48),ey-r*math.sin(ang+.48)),fill=color,width=width)

def base(p):
    im=Image.new('RGB',(W,H),WHITE);d=ImageDraw.Draw(im)
    d.text((48,21),'BELLE LI',font=font(17,True,True),fill=INK)
    d.text((208,21),tx('文献与判断 / 两个可复用的 skill','PAPERS & JUDGMENTS / TWO REUSABLE SKILLS'),font=font(17),fill=GREY)
    meta=f"{p['chapter']:02d} / {COUNT:02d}"
    d.text((1450,21),meta,font=font(17,mono=True),fill=GREY)
    d.line((48,58,1552,58),fill=LINE,width=1)
    return im,d

def footer(im,p,note):
    d=ImageDraw.Draw(im)
    d.rectangle((0,798,W,H),fill=WHITE);d.line((48,798,1552,798),fill=LINE,width=1)
    subtitles=lines(p['speech'],28,1488)
    if len(subtitles)>2:raise ValueError('Subtitle overflow: '+p['speech'])
    top=819 if len(subtitles)==1 else 805
    for i,s in enumerate(subtitles):
        tw=d.textlength(s,font=font(28));d.text(((W-tw)/2,top+i*35),s,font=font(28),fill=INK)
    # Small provenance stays outside the source screen; full details live beside the player.
    text(d,note,48,877,1250,14,color=GREY,maxheight=20)
    d.text((1385,877),'HUMANS IN CHARGE.',font=font(12,mono=True),fill=GREY)
    return im

def journey(d,p):
    active=0 if p['chapter']<=5 else 1 if p['chapter']==6 else 2 if p['chapter']<=9 else 3
    labs=tx(['准备来源','发展规则','审阅核验','回传与裁决'],['Prepare sources','Develop rules','Review evidence','Return & resolve'])
    for i,s in enumerate(labs):
        x=64+i*390;d.line((x,748,x+342,748),fill=ORANGE if i==active else LINE,width=2 if i==active else 1)
        d.text((x,762),f'0{i+1}',font=font(15,mono=True),fill=ORANGE if i==active else QUIET)
        d.text((x+38,757),s,font=font(19,i==active),fill=INK if i==active else GREY)

def ui(p,t):
    im,d=base(p);X,Y=284,68;VW,VH=1280,720
    path=DOCS/'intro'/p['frame'] if KIND=='intro' else DOCS/'demo/frames'/(p['frame']+'.jpg')
    target=list(p.get('camera',[0,0,1280,720]));start=list(p.get('start_camera',[0,0,1280,720]))
    for c in (target,start):
        if c[3]>720:c[1]-=c[3]-720;c[3]=720
    k=ease(t/1.1);cam=[a+(b-a)*k for a,b in zip(start,target)]
    x0,y0,x1,y1=cam;sx=VW/(x1-x0);sy=VH/(y1-y0)
    shot=img(path).crop(tuple(cam)).resize((VW,VH),Image.Resampling.BICUBIC)
    im.paste(shot,(X,Y))
    def pt(a,b):return (X+(a-x0)*sx,Y+(b-y0)*sy)
    def box(v):
        a,b=pt(v[0]-5,v[1]-5),pt(v[2]+5,v[3]+5)
        return [max(X+2,a[0]),max(Y+2,a[1]),min(X+VW-2,b[0]),min(Y+VH-2,b[1])]
    boxes=[box(p['box'])]+([box(p['second'])] if p.get('second') else [])
    mask=Image.new('L',(W,H),0);md=ImageDraw.Draw(mask)
    md.rectangle((X,Y,X+VW,Y+VH),fill=int(32*ease(t/.7)))
    for b in boxes:
        if b[2]>b[0] and b[3]>b[1]:md.rectangle(b,fill=0)
    im=Image.composite(Image.new('RGB',(W,H),INK),im,mask);d=ImageDraw.Draw(im)
    d.line((264,82,264,765),fill=LINE,width=1)
    d.text((38,87),f"{p['chapter']:02d}",font=font(60,True),fill=INK)
    title_end=text(d,p['title'],38,178,208,32,bold=True,maxheight=208)
    labels=[p['label']]+([p.get('second_label',tx('对应原文','Source passage'))] if len(boxes)>1 else [])
    for i,(b,label) in enumerate(zip(boxes,labels)):
        color=ORANGE if i==0 else BLUE;yy=max(440,title_end+40)+i*152
        d.ellipse((38,yy,62,yy+24),fill=color)
        d.text((45,yy+3),str(i+1),font=font(13,True),fill=WHITE)
        text(d,re.sub(r'^\d+[.、]\s*', '', label),38,yy+37,208,23,color=INK,maxheight=103)
        if b[2]<=b[0] or b[3]<=b[1]:continue
        if p.get('shape')=='circle' and i==0:d.arc(b,start=-80,end=-80+359*ease(t/.7),fill=color,width=3)
        else:d.rounded_rectangle(b,5,outline=color,width=2)
        # Small numbered pin matches the annotation rail without covering the quote.
        bx=max(X+3,min(X+VW-27,b[0]-12));by=max(Y+3,b[1]-28)
        d.ellipse((bx,by,bx+24,by+24),fill=color);d.text((bx+7,by+3),str(i+1),font=font(13,True),fill=WHITE)
    if p.get('link') and t>.45:
        b=boxes[-1];arrow(d,pt(*p['link']),(b[0]+7,(b[1]+b[3])/2),BLUE,ease((t-.45)/1.0))
    if p.get('click') and .25<t<1.6:
        cx,cy=pt(*p['click']);r=7+22*(t-.25)/1.35;d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=ORANGE,width=2)
    if p.get('drag'):
        a,b,y=p['drag'];arrow(d,pt(a,y),pt(b,y),ORANGE,ease((t-.2)/1.2));cx,cy=pt(a+(b-a)*ease((t-.5)/1.5),y)
        d.ellipse((cx-7,cy-7,cx+7,cy+7),fill=ORANGE)
    if p.get('scroll'):
        # One directional movement, then hold; avoids a distracting perpetual loop.
        xx=1548;yy=530;arrow(d,(xx,yy-80),(xx,yy+55),ORANGE)
        cy=yy-70+110*ease((t-.3)/1.5);d.ellipse((xx-5,cy-5,xx+5,cy+5),fill=ORANGE)
    note=p.get('source_note',tx('真实界面 · 后期引导标注 · 演示反馈单独保存','Real UI · editorial guidance · separate demo responses'))
    return footer(im,p,note)

def heading(d,label):text(d,label,64,106,1460,52,bold=True,maxheight=122)

def intro(p,t):
    if p['kind']=='ui':return ui(p,t)
    im,d=base(p);k=p['kind'];a=p.get('active',0)
    note=tx('流程示意 · 人掌握规则与最终判断','Workflow illustration · people own rules and final judgments')
    if k in ('story','case'):
        case=k=='case'; ximg=676 if not case else 562
        fit(im,DOCS/'intro'/p['image'],(ximg,141,1552,694));d=ImageDraw.Draw(im)
        d.text((64,124),p.get('case',tx('从你的研究出发','START WITH YOUR RESEARCH')),font=font(20,True),fill=GREY)
        y=text(d,p['headline'],64,205,(560 if LANG=='zh-CN' else 490) if not case else 444,56,bold=True,leading=1.14,maxheight=236)+45
        for s in p['points']:
            d.line((64,y,120,y),fill=ORANGE,width=2)
            y=text(d,s,64,y+20,478 if not case else 425,26,color=GREY,maxheight=88)+28
        note=tx('Belle 概念插画','Belle concept illustration') if not case else tx('真实来源的通用工作台适配示例 · 非历史审阅现场','Real-source adaptation in the portable UI · not a historical review session')
    elif k=='pair':
        heading(d,tx('两个入口，一条工作流','Two entry points. One connected workflow.'))
        d.line((800,275,800,654),fill=LINE,width=1)
        for i in range(2):
            x=64+i*792
            d.text((x,263),f'0{i+1}',font=font(64,True),fill=ORANGE if i==a else GREY)
            title=['Literature PDF\nRetrieval','Review Evidence\nWorkflow'][i]
            y=text(d,title,x,359,666,48,bold=True,leading=1.08)
            desc=tx(['准备能用的全文','组织人能核对的审阅'],['Prepare usable full texts','Organize review people can check'])[i]
            text(d,desc,x,508,668,30,maxheight=78)
            detail=tx(['检索 · 访问接力 · 身份核对','规则 · 审阅包 · 回传 · 裁决'],['Retrieval · access handoff · identity checks','Rules · packages · returns · adjudication'])[i]
            text(d,detail,x,612,667,23,color=GREY,maxheight=75)
        arrow(d,(732,309),(837,309),ORANGE,ease((t-.15)/1.1))
    elif k in ('intake','flow'):
        heading(d,p['headline']);ls=p['nodes'];n=len(ls);width=1472/n;active=min(a,int(t/1.4))
        for i,s in enumerate(ls):
            x=64+i*width;col=ORANGE if i==active else GREY
            d.text((x,316),f'{i+1:02}',font=font(60,True),fill=col)
            text(d,s,x,432,width-46,38,bold=True,maxheight=132)
            d.line((x,574,x+width-42,574),fill=col if i==active else LINE,width=2 if i==active else 1)
            if i<n-1:arrow(d,(x+width-88,354),(x+width-27,354),ORANGE,ease((t-i*.25)/1.1))
        text(d,p.get('footer',tx('已有全文？可以直接开始来源核对或规则校准。','Already have PDFs? Start with source checks or calibration.')),64,633,1430,26,color=BLUE,maxheight=80)
    elif k=='prompt':
        heading(d,p['headline']);d.rectangle((64,255,1536,682),fill=INK)
        d.text((98,282),tx('给 agent 的一段话','A REQUEST TO YOUR AGENT'),font=font(18,True),fill='#bfbfbf')
        text(d,p['prompt'],98,352,1370,36,color=WHITE,leading=1.55,maxheight=242)
        d.text((99,633),p['tag'],font=font(21),fill='#e3aa8b');note=p['tag']
    elif k=='handoff':
        heading(d,tx('把需要你做的那一步，说具体','Make the human step specific.'))
        text(d,tx('R017 · 交接示例','R017 · illustrative handoff'),64,226,1400,22,color=GREY)
        rows=tx([('遇到什么','文章入口到了登录页；还没拿到文件'),('你做什么','打开已核对的入口 → 登录 → 保存 PDF'),('交回哪里','R017.pdf → 约定的 incoming 文件夹'),('AI 接着做','核对文章身份与文件 → 更新清单')],[('Obstacle','The article route reaches sign-in; no PDF yet'),('Your step','Open the checked page → sign in → save the PDF'),('Return','R017.pdf → the agreed incoming folder'),('Agent resumes','Check identity and the file → update the queue')])
        focus=(0 if t<1.6 else 1) if not a else (2 if t<1.6 else 3)
        for i,(label,value) in enumerate(rows):
            y=292+i*99;d.line((64,y,1536,y),fill=LINE,width=1)
            d.text((64,y+28),f'0{i+1}',font=font(22,mono=True),fill=ORANGE if i==focus else GREY)
            text(d,label,148,y+24,266,27,bold=i==focus)
            text(d,value,449,y+23,1050,28,maxheight=74)
        note=tx('交接模板 · 手动保存不等于人工确认身份','Handoff template · saving a file does not confirm its identity')
    elif k=='checks':
        heading(d,tx('拿到了，还要确认拿对了','You have the file. Is it the right one?'))
        d.text((64,299),'PDF',font=font(102,True),fill=INK)
        text(d,tx('能打开，只是起点','Readable is only the start'),64,462,477,36,bold=True,maxheight=110)
        text(d,tx('文件名、扩展名、下载成功，都还不够。','A filename or successful download is not identity evidence.'),64,575,478,26,color=GREY,maxheight=95)
        ls=tx(['文章 / 章节身份','DOI 与题名证据','版本与完整性','页数与文件哈希'],['Article / chapter identity','DOI and title evidence','Version and completeness','Page count and file hash'])
        focus=2 if a else min(3,int(t/1.4))
        for i,s in enumerate(ls):
            y=282+i*91;d.line((636,y+77,1536,y+77),fill=LINE,width=1)
            d.text((638,y+10),f'0{i+1}',font=font(24,mono=True),fill=ORANGE if i==focus else GREY)
            text(d,s,717,y,810,32,bold=i==focus,maxheight=76)
        text(d,tx('有疑点 → 换方法检查；仍不清楚 → 保留待核对','Uncertain? Corroborate it. Still unresolved? Keep it pending.'),636,670,902,22,color=BLUE,maxheight=60)
        note=tx('脚本做初筛；版本、完整性与解释仍需证据和判断','Scripts provide triage; version, completeness and interpretation need judgment')
    elif k=='outputs':
        heading(d,tx('交给下一步的，不只是 PDF','More than a folder of PDFs.'))
        rows=tx([('核对过的来源','ID、来源、页数、哈希和身份依据'),('当前状态 + 尝试历史','知道做到哪里，也知道试过什么'),('仍待处理的清单','每条有原因和下一步；不保证全都能找到')],[('Checked sources','IDs, provenance, pages, hashes and identity evidence'),('Current state + attempt history','Know where the work stands and which routes were tried'),('An actionable remaining queue','Each item has a reason and next step; full coverage is not promised')])
        for i,(title,desc) in enumerate(rows):
            y=274+i*144;d.line((64,y+126,1536,y+126),fill=LINE,width=1)
            d.text((64,y),f'0{i+1}',font=font(44,True),fill=ORANGE if i==min(2,int(t/1.8)) else GREY)
            text(d,title,184,y,1300,34,bold=True);text(d,desc,184,y+57,1300,25,color=GREY,maxheight=70)
    elif k in ('modes','assign'):
        heading(d,tx('每一轮，都可以重新选择','Choose again for each round.') if k=='modes' else tx('让每个人拿到适合自己的任务','A different brief for each reviewer.'))
        groups=tx([('AI 辅助核验',['看 AI 建议与出处','人确认、修订或保留不确定']),('独立审阅',['看规则、原文和空白表单','包内不放建议与他人反馈'])],[('Assisted verification',['See proposals and evidence','Confirm, revise or flag uncertainty']),('Independent review',['Rules, sources and blank forms','No proposals or other reviewers’ feedback'])]) if k=='modes' else tx([('审阅者 A',['分配的文献 · 方法字段','本人的说明与审阅模式']),('审阅者 B',['分配的文献 · 概念字段','本人的说明与审阅模式'])],[('Reviewer A',['Assigned reports · methods fields','Personal instructions and review mode']),('Reviewer B',['Assigned reports · concept fields','Personal instructions and review mode'])])
        d.line((800,285,800,683),fill=LINE,width=1)
        for i,(title,ls) in enumerate(groups):
            x=64+i*792;d.text((x,291),f'0{i+1}',font=font(26,mono=True),fill=ORANGE)
            yy=text(d,title,x,367,660,44,bold=True,maxheight=136)+54
            for s in ls:yy=text(d,s,x,yy,651,28,color=GREY,maxheight=86)+30
        note=tx('包的内容可以隔离；软件不能证明人的行为独立','Package contents can be isolated; software cannot prove behavioral independence') if k=='modes' else tx('任务配置示意 · 由 agent 准备配置，不是可视化设置页面','Assignment illustration · prepared by the agent, not a settings screen')
    elif k=='start':
        heading(d,tx('从你现在这一步开始','Start where you are.'))
        rows=tx([('缺全文，或不确定文件是否找对','literature-pdf-retrieval'),('准备规则、审阅包、回传与裁决','review-evidence-workflow')],[('Missing or uncertain full texts','literature-pdf-retrieval'),('Rules, review packages, returns and decisions','review-evidence-workflow')])
        for i,(title,repo) in enumerate(rows):
            y=282+i*211;d.line((64,y+174,1536,y+174),fill=LINE,width=1)
            d.text((64,y),f'0{i+1}',font=font(52,True),fill=ORANGE if i==a else GREY)
            text(d,title,184,y,1290,38,bold=True,maxheight=98)
            d.text((184,y+106),'github.com/Beeeeeeelle/'+repo,font=font(27),fill=BLUE)
        note=tx('协调者安装 skill；审阅者只需打开自己的浏览器包','Coordinators install the skill; reviewers open their browser package')
    else:raise ValueError(k)
    journey(d,p)
    return footer(im,p,note)

def frame(p,t):return intro(p,t) if KIND=='intro' else ui(p,t)

def configure(args):
    global LANG,KIND,COUNT
    LANG=args.lang;KIND=args.kind;COUNT=12 if KIND=='intro' else 16;font.cache_clear()
    timeline=json.loads((args.build/'timeline.json').read_text())
    # Read current approved storyboard; timing and narration must be identical.
    path=DOCS/KIND/f'storyboard.{LANG}.json' if KIND=='intro' else DOCS/'demo'/('storyboard.en.json' if LANG=='en' else 'storyboard.json')
    scenes=json.loads(path.read_text());parts=[dict(p,chapter=i+1,title=s['title'],stage=s.get('stage','')) for i,s in enumerate(scenes) for p in s['parts']]
    assert len(parts)==len(timeline)
    for i,(p,s) in enumerate(zip(parts,timeline)):
        assert p['speech']==s['speech'],f'Narration changed in beat {i}'
        for key in ['index','start','duration','nframes','speech_duration']:p[key]=s[key]
        if i and parts[i-1]['chapter']==p['chapter']:p['start_camera']=parts[i-1].get('camera',[0,0,1280,720])
    args.out.mkdir(parents=True,exist_ok=True)
    return parts

def render(args,parts):
    target=args.out/f'{args.kind}.{args.lang}.mp4'
    proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-i',str(args.build/'narration.wav'),'-map','0:v','-map','1:a','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','112k','-ar','48000','-af','loudnorm=I=-16:TP=-1.5:LRA=9','-movflags','+faststart','-shortest',str(target)],stdin=subprocess.PIPE)
    for p in parts:
        previous=None
        for n in range(p['nframes']):
            # Only the first six seconds animate. Hold the final composition for reading.
            if n<144:previous=frame(p,n/FPS).tobytes()
            proc.stdin.write(previous)
        print(f"{KIND}/{LANG}: {p['index']+1}/{len(parts)}",flush=True)
    proc.stdin.close()
    if proc.wait():raise RuntimeError('ffmpeg render failed')
    print(target,flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['preview','render']);ap.add_argument('--kind',choices=['intro','pilot'],required=True);ap.add_argument('--lang',choices=['en','zh-CN'],required=True);ap.add_argument('--build',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();parts=configure(args)
    if args.mode=='preview':
        for p in parts:frame(p,4.8).save(args.out/f"{KIND}.{LANG}.{p['index']:02d}.jpg",quality=92)
    else:render(args,parts)
    if OVERFLOWS:raise ValueError('Text overflows: '+str(sorted(set(OVERFLOWS))))
