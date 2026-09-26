"""Bilingual introductory film using existing illustrations, diagrams and real captures.

Requires Pillow, edge-tts, ffmpeg. No source UI, quoted text or research decisions
are generated. Diagram scenes and fictional examples are explicitly identified.
"""
from pathlib import Path
import argparse, asyncio, importlib.util, json, math, os, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('guided',ROOT.parent/'demo/tools/render_guided_video.py')
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
W,H,FPS=1280,900,24
BG='#172026';PAPER='#faf9f6';INK='#172026';MUTED='#5d6b70';ORANGE='#d96f32';TEAL='#087f7d';LINE='#d8dcda'
LANG='zh-CN';F={};OUT=None;PARTS=[];SCENES=[];IMAGES={}

def text(zh,en):return en if LANG=='en' else zh

def wrapped(draw,value,x,y,width,size=30,color=INK,gap=10):
    for paragraph in str(value).split('\n'):
        for line in g.lines(paragraph,F[size],width,draw):
            draw.text((x,y),line,font=F[size],fill=color)
            y+=size+gap
    return y

def fit_image(canvas,path,box):
    if path not in IMAGES:IMAGES[path]=Image.open(ROOT/path).convert('RGB')
    im=ImageOps.contain(IMAGES[path],(box[2]-box[0],box[3]-box[1]),Image.Resampling.LANCZOS)
    canvas.paste(im,(box[0]+(box[2]-box[0]-im.width)//2,box[1]+(box[3]-box[1]-im.height)//2))

def line_arrow(d,a,b,color=TEAL,width=4):g.arrow(d,a,b,color,1,width)

def panel(d,box,active=False):
    d.rectangle(box,fill='#ffffff',outline=ORANGE if active else LINE,width=3 if active else 1)
    if active:d.rectangle((box[0],box[1],box[0]+6,box[3]),fill=ORANGE)

def nodes(d,labels,active=0,y=330,width=330):
    n=len(labels);gap=56;left=(W-(width*n+gap*(n-1)))/2
    for i,label in enumerate(labels):
        x=left+i*(width+gap)
        panel(d,(x,y,x+width,y+145),i==active)
        d.text((x+24,y+17),f'{i+1:02}',font=F[20],fill=ORANGE if i==active else MUTED)
        wrapped(d,label,x+24,y+54,width-48,28,gap=6)
        if i<n-1:line_arrow(d,(x+width+8,y+74),(x+width+gap-9,y+74))

def journey(d,p):
    active=0 if p['chapter']<=5 else 1 if p['chapter']==6 else 2 if p['chapter']<=9 else 3
    labels=text(['准备来源','发展规则','审阅核验','回传与裁决'],['Prepare sources','Develop rules','Review evidence','Return and resolve'])
    d.line((82,728,1198,728),fill=LINE,width=2)
    for i,label in enumerate(labels):
        x=82+i*372
        if i==3:x=1198
        d.ellipse((x-7,721,x+7,735),fill=ORANGE if i==active else '#ccd3d2')
        tw=d.textlength(label,font=F[18]);lx=max(45,min(W-tw-45,x-tw/2))
        d.text((lx,746),label,font=F[18],fill=ORANGE if i==active else MUTED)

def shell(p):
    im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
    meta=f"{p['chapter']:02d} / {len(SCENES):02d}  ·  "+text('入门导览','Introduction')
    mw=d.textlength(meta,font=F[18])
    f=next((F[s] for s in [29,27,25,22] if d.textlength(p['title'],font=F[s])<W-mw-75),F[22])
    d.text((25,17),p['title'],font=f,fill='#f4f1e9');d.text((W-mw-24,24),meta,font=F[18],fill='#ffac73')
    d.rectangle((0,70,W,790),fill=PAPER)
    return im,d

def frame(p,t):
    if p['kind']=='ui':
        key=p['frame']
        if key not in IMAGES:IMAGES[key]=Image.open(ROOT/key).convert('RGB')
        im=g.render(p,t,IMAGES[key]);d=ImageDraw.Draw(im)
        if p.get('source_note'):
            d.rectangle((0,870,1040,900),fill=BG);d.text((24,874),p['source_note'],font=F[16],fill='#bac4c8')
        return im
    im,d=shell(p);k=p['kind'];active=p.get('active',0)
    tag=text('流程示意 · 人掌握规则与最终判断','Workflow illustration · people own rules and final judgments')
    if k in ('story','case'):
        fit_image(im,p['image'],(475,168,1255,681));d=ImageDraw.Draw(im)
        d.text((48,140),p.get('case',text('从你的研究出发','START WITH YOUR RESEARCH')),font=F[20],fill=ORANGE)
        y=wrapped(d,p['headline'],48,200,418,40,gap=13)+34
        for point in p['points']:
            d.line((48,y+15,65,y+15),fill=ORANGE,width=3)
            y=wrapped(d,point,82,y,350,25,gap=9)+18
        tag=text('Belle 概念插画 · 与真实界面分开标注','Belle concept illustration · distinct from real interface captures') if k=='story' else text('真实来源的通用工作台适配示例 · 非历史审阅现场','Real-source adaptation in the portable UI · not a historical review session')
    elif k=='pair':
        wrapped(d,text('两个入口，接成一条工作流','Two entry points, one connected workflow'),55,126,1165,40)
        for i,(title,desc,detail) in enumerate([
          ('Literature PDF\nRetrieval',text('准备能用的全文','Prepare usable full texts'),text('检索 · 访问接力 · 身份核对','Retrieval · access handoff · identity checks')),
          ('Review Evidence\nWorkflow',text('组织人能核对的审阅','Organize review that people can check'),text('规则 · 审阅包 · 回传 · 裁决','Rules · packages · returns · adjudication'))]):
            x=55+i*624;panel(d,(x,230,x+546,625),i==active)
            d.text((x+28,252),f'0{i+1}',font=F[24],fill=ORANGE if i==active else TEAL)
            y=wrapped(d,title,x+28,304,492,40,gap=8)
            y=wrapped(d,desc,x+28,y+34,488,27,gap=8)
            wrapped(d,detail,x+28,y+22,488,22,gap=6,color=MUTED)
        g.arrow(d,(608,425),(669,425),TEAL,g.ease((t-.2)/1.25),4)
    elif k in ('flow','intake'):
        wrapped(d,p['headline'],55,144,1170,40)
        focus=min(active,max(0,int(t/1.6)))
        nodes(d,p['nodes'],focus,y=330,width=250 if len(p['nodes'])==4 else 335)
        wrapped(d,p.get('footer',text('已有全文？可以直接开始来源核对或规则校准。','Already have the PDFs? Start with source checks or calibration.')),65,570,1150,26,color=TEAL)
    elif k=='prompt':
        wrapped(d,p['headline'],55,138,1170,40)
        d.text((58,231),text('把材料交给 agent，然后说：','Give the agent your materials, then ask:'),font=F[24],fill=MUTED)
        panel(d,(55,292,1225,580),True)
        wrapped(d,p['prompt'],86,333,1094,29,gap=22)
        wrapped(d,p['tag'],60,629,1140,22,color=TEAL)
        tag=p['tag']
    elif k=='handoff':
        wrapped(d,text('把“需要你帮忙”说成具体的一步','Turn “I need help” into one specific step'),55,123,1170,38)
        d.text((59,200),text('R017 · 示例交接；不是一次真实下载记录','R017 · illustrative handoff, not an observed download'),font=F[22],fill=MUTED)
        rows=[(text('遇到什么','Obstacle'),text('文章入口到了登录页；还没拿到文件','The article route reaches sign-in; no PDF yet')),
        (text('你做什么','Your step'),text('打开已核对的入口 → 登录 → 保存 PDF','Open the checked landing page → sign in → save the PDF')),
        (text('交回哪里','Return'),text('R017.pdf → 约定的 incoming 文件夹','R017.pdf → the agreed incoming folder')),
        (text('AI 接着做','Agent resumes'),text('核对文章身份与文件 → 更新清单','Check identity and the file → update the queue'))]
        for i,(name,value) in enumerate(rows):
            y=268+i*96;focus=(0 if t<1.6 else 1) if active==0 else (2 if t<1.6 else 3);selected=i==focus
            panel(d,(55,y,1225,y+78),selected)
            d.text((82,y+23),name,font=F[25],fill=ORANGE if selected else MUTED)
            wrapped(d,value,282,y+23,907,25,gap=4)
        tag=text('交接模板 · 手动保存不等于人工确认身份','Handoff template · saving a file does not confirm its identity')
    elif k=='checks':
        wrapped(d,text('文件拿到了，下一步是核对','You have the file. Now check it.'),55,123,1170,40)
        panel(d,(55,260,398,633),False)
        wrapped(d,text('候选 PDF','Candidate PDF'),87,300,280,38)
        wrapped(d,text('文件名、扩展名、下载成功\n都还不够','A filename, extension,\nor successful download\nis not enough'),87,405,278,27,gap=10,color=MUTED)
        line_arrow(d,(420,445),(508,445))
        checks=text(['文章 / 章节身份','DOI 与题名证据','版本与完整性','页数与文件哈希'],['Article / chapter identity','DOI and title evidence','Version and completeness','Page count and file hash'])
        for i,label in enumerate(checks):
            focus=2 if active else min(3,max(0,int(t/1.6)))
            y=254+i*83;panel(d,(540,y,1225,y+65),i==focus)
            d.text((565,y+17),f'{i+1:02}',font=F[22],fill=TEAL);d.text((620,y+15),label,font=F[28],fill=INK)
        wrapped(d,text('有疑点 → 换方法检查；仍不清楚 → 保留待核对','Uncertain? Corroborate it. Still unresolved? Keep it pending.'),545,615,665,24,color=ORANGE)
        tag=text('脚本做初筛；版本、完整性与解释仍需证据和判断','Scripts provide triage; version, completeness and interpretation need judgment')
    elif k=='outputs':
        wrapped(d,text('交给下一步的，不只是 PDF','The handoff includes more than PDFs'),55,136,1170,40)
        labels=[('01',text('核对过的来源','Checked sources'),text('ID、来源、页数、哈希和身份依据','IDs, provenance, pages, hashes and identity evidence')),
                ('02',text('当前状态 + 尝试历史','Current state + attempt history'),text('知道做到哪里，也知道试过什么','Know where the work stands and which routes were tried')),
                ('03',text('仍待处理的清单','An actionable remaining queue'),text('每条有原因和下一步；不保证全都能找到','Each item has a reason and next step; full coverage is not promised'))]
        for i,(num,title,detail) in enumerate(labels):
            y=270+i*132;d.line((55,y+115,1225,y+115),fill=LINE,width=1)
            if i==min(2,max(0,int(t/2))):d.line((48,y,48,y+93),fill=ORANGE,width=5)
            d.text((62,y+10),num,font=F[32],fill=ORANGE)
            wrapped(d,title,145,y,1030,30);wrapped(d,detail,145,y+49,1030,25,color=MUTED)
    elif k=='modes':
        wrapped(d,text('每一轮都可以重新选择','Choose again for each round'),55,128,1170,40)
        groups=[(text('AI 辅助核验','Assisted verification'),text(['看 AI 建议与出处','人确认、修订或保留不确定'],['See proposals and evidence','Confirm, revise or flag uncertainty'])),
                (text('独立审阅','Independent review'),text(['看规则、原文和空白表单','包内不放建议与他人反馈'],['See rules, sources and blank forms','No proposals or other reviewers’ feedback in the package']))]
        for i,(title,points) in enumerate(groups):
            x=55+624*i;panel(d,(x,259,x+546,620),i==1)
            y=wrapped(d,title,x+26,294,494,34,gap=8)+43
            for point in points:y=wrapped(d,point,x+26,y,485,27,gap=8)+28
        tag=text('包的内容可以隔离；软件不能证明人的行为独立','Package contents can be isolated; software cannot prove behavioral independence')
    elif k=='assign':
        wrapped(d,text('同一项目，不必给每个人同一份任务','One project; different tasks for different people'),55,128,1170,38)
        for i in range(2):
            x=55+i*624;panel(d,(x,260,x+546,637),i==0)
            d.text((x+28,287),text('审阅者 ','Reviewer ')+('A' if i==0 else 'B'),font=F[36],fill=ORANGE)
            vals=text(['分配的文献','方法字段' if i==0 else '概念字段','本人的说明和审阅模式'],['Assigned reports','Methods fields' if i==0 else 'Concept fields','Personal instructions and review mode'])
            y=372
            for v in vals:y=wrapped(d,v,x+28,y,477,28)+25
        tag=text('任务配置示意 · 由 agent 准备配置，不是可视化设置页面','Assignment illustration · the agent prepares configuration; this is not a settings screen')
    elif k=='start':
        wrapped(d,text('从你现在这一步开始','Start where you are'),55,123,1170,42)
        groups=[('PDF RETRIEVAL','literature-pdf-retrieval',text('缺全文，或不确定文件是否找对','Missing or uncertain full texts')),
                ('REVIEW WORKFLOW','review-evidence-workflow',text('准备规则、审阅包、回传与裁决','Rules, reviewer packages, returns and decisions'))]
        for i,(label,repo,desc) in enumerate(groups):
            y=259+i*196;panel(d,(55,y,1225,y+156),active==i)
            d.text((83,y+21),label,font=F[20],fill=ORANGE)
            wrapped(d,desc,83,y+55,1090,30)
            d.text((83,y+111),'github.com/Beeeeeeelle/'+repo,font=F[22],fill=TEAL)
        tag=text('协调者安装 skill；审阅者只需打开自己的浏览器包','Coordinators install the skill; reviewers open their browser package')
    else:raise ValueError(k)
    # Editorial marker enters once, then settles; no invented application transitions.
    d.line((55,96,55+int(180*g.ease(t/.75)),96),fill=ORANGE,width=4)
    journey(d,p)
    d.rectangle((0,790,W,H),fill=BG)
    sub=g.lines(p['speech'],F[27],1140,d)
    if len(sub)>2:raise ValueError('Narration needs shorter beats: '+p['speech'])
    for j,line in enumerate(sub):
        tw=d.textlength(line,font=F[27]);d.text(((W-tw)/2,801+j*35),line,font=F[27],fill='#f4f1e9')
    size=16 if d.textlength(tag,font=F[16])<1230 else 14
    d.text((24,875),tag,font=F[size],fill='#bac4c8')
    return im

def configure(lang,out):
    global LANG,OUT,F,PARTS,SCENES
    LANG=lang;OUT=out;OUT.mkdir(parents=True,exist_ok=True)
    font=os.environ.get('GUIDE_FONT','/System/Library/Fonts/Supplemental/Arial.ttf' if lang=='en' else '/System/Library/Fonts/Hiragino Sans GB.ttc')
    F={n:ImageFont.truetype(font,n) for n in [14,16,18,20,22,24,25,26,27,28,29,30,32,34,36,38,40,42]}
    SCENES=json.loads((ROOT/f'storyboard.{lang}.json').read_text())
    PARTS=[dict(p,chapter=i+1,title=s['title'],stage=text('入门导览','Introduction')) for i,s in enumerate(SCENES) for p in s['parts']]
    for i,p in enumerate(PARTS):
        if i and p['kind']=='ui' and PARTS[i-1]['kind']=='ui' and PARTS[i-1]['chapter']==p['chapter']:
            p['start_camera']=PARTS[i-1].get('camera',[0,0,1280,720])
    g.LANG=LANG;g.VOICE='en-US-JennyNeural' if LANG=='en' else 'zh-CN-XiaoxiaoNeural';g.RATE='-2%'
    g.OUT=OUT;g.PARTS=PARTS;g.SCENES=SCENES;g.FONTS={n:ImageFont.truetype(font,n) for n in (16,18,20,22,25,27,29)}

def film(segments,limit=None):
    selected=segments if limit is None else segments[:limit]
    dest=OUT/('overview.mp4' if limit is None else 'proof.mp4')
    proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-i',str(OUT/'narration.wav'),'-map','0:v','-map','1:a','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','112k','-ar','48000','-af','loudnorm=I=-16:TP=-1.5:LRA=9','-movflags','+faststart','-shortest',str(dest)],stdin=subprocess.PIPE)
    for s in selected:
        static=frame(s,max(6,s['duration'])).tobytes()
        for n in range(s['nframes']):
            # After the short guide animation, narrative diagrams hold still for reading.
            pixels=frame(s,n/FPS).tobytes() if n<144 or s['kind']=='ui' else static
            proc.stdin.write(pixels)
        print(f"Rendered {s['index']+1}/{len(selected)} — {s['title']}",flush=True)
    proc.stdin.close()
    if proc.wait():raise RuntimeError('ffmpeg render failed')
    print(dest,flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['preview','voice','proof','render']);parser.add_argument('--lang',choices=['zh-CN','en'],required=True);parser.add_argument('--out-dir',type=Path)
    args=parser.parse_args();configure(args.lang,args.out_dir or ROOT/'tools/.build'/args.lang)
    if args.mode=='voice':asyncio.run(g.voices())
    elif args.mode=='preview':
        for i,p in enumerate(PARTS):frame(p,2).save(OUT/f'preview-{i:02}.jpg',quality=94)
    else:film(g.timing(),3 if args.mode=='proof' else None)
