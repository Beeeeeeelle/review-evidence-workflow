#!/usr/bin/env python3
"""Generate editable SVG workflow illustrations. Python standard library only."""
from pathlib import Path
from html import escape
P=Path(__file__).resolve().parent
INK='#0A0A0A';GRAY='#525252';RULE='#D8DDE2';HUMAN='#D97745';AI='#5F7FA3';RED='#B94A48'
class Figure:
 def __init__(self,w,h,title):
  self.w=w;self.h=h;self.s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}"><title>{escape(title)}</title><rect width="100%" height="100%" fill="white"/><defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 Z" fill="{GRAY}"/></marker><marker id="loop" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="{HUMAN}"/></marker></defs>']
 def text(self,x,y,lines,size=23,color=INK,weight=400,anchor='start',gap=None):
  if isinstance(lines,str):lines=[lines]
  self.s.append(f'<text x="{x}" y="{y}" font-family="Helvetica Neue,Arial,PingFang SC,Noto Sans CJK SC,sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">')
  for i,line in enumerate(lines):self.s.append(f'<tspan x="{x}" dy="{0 if i==0 else gap or size*1.4}">{escape(line)}</tspan>')
  self.s.append('</text>')
 def rect(self,x,y,w,h,fill='#fff',stroke=RULE):self.s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{fill}" stroke="{stroke}"/>')
 def line(self,d,arrow=True,color=GRAY,dash=False):self.s.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2"'+(' stroke-dasharray="7 6"' if dash else '')+(f' marker-end="url(#{"loop" if color==HUMAN else "arrow"})"' if arrow else '')+'/>')
 def box(self,x,y,w,h,label,title,body,color):
  self.rect(x,y,w,h);self.s.append(f'<rect x="{x}" y="{y}" width="4" height="{h}" fill="{color}"/>');self.text(x+22,y+27,label,16,color,700);self.text(x+22,y+59,title,25,INK,650);self.text(x+22,y+89,body,20,GRAY)
 def save(self,name):P.joinpath(name).write_text(''.join(self.s)+'</svg>')

def workflow(zh=False):
 f=Figure(1160,1110,'灵活的人主导文献审阅流程' if zh else 'Flexible human-led review workflow')
 f.text(50,48,'REVIEW EVIDENCE WORKFLOW',17,GRAY,650);f.text(50,94,'人主导规则，AI 帮助执行。' if zh else 'Human-led rules. AI-assisted work.',36,INK,700)
 for x,c,t in [(50,HUMAN,'人：判断与授权' if zh else 'HUMANS · judgment'),(410,AI,'AI：整理与提案' if zh else 'AI · preparation'),(780,GRAY,'软件：核对与留痕' if zh else 'SOFTWARE · checks')]:
  f.rect(x,117,11,11,c,c);f.text(x+21,130,t,18,c)
 f.box(50,160,1030,104,'01 · 人' if zh else '01 · HUMANS','制定和发展 codebook，选择本轮任务' if zh else 'Develop the codebook. Choose this round.', ['可先用自选样本校准；10 篇只是示例，可以重复或调整。'] if zh else ['Calibrate on a chosen sample; ten papers is an example, not a required threshold.'],HUMAN)
 f.line('M565 264 V298')
 f.box(50,305,1030,103,'02 · AI 与软件' if zh else '02 · AI + SOFTWARE','准备全文并核对身份' if zh else 'Find full texts and check source identity.',['检索与获取 → DOI / 标题 / 页数 / 哈希核对；未解决的全文进入清单。'] if zh else ['Retrieve → check DOI / title / pages / hash. Unresolved sources stay in a queue.'],AI)
 f.line('M565 408 V440 H305 V467');f.line('M565 440 H825 V467')
 f.text(565,439,'',18)
 f.box(50,475,510,177,'03A · ASSISTED' if not zh else '03A · AI 辅助核验','AI 编码 → 人核验' if zh else 'AI proposes → people verify',['AI 按当前规则整理值、理由和原文证据；','人对照全文确认、修订或延后。','使用分配给自己的审阅包。'] if zh else ['AI drafts values, reasons and page evidence.','People accept, revise or defer.','Each reviewer receives their own package.'],AI)
 f.box(590,475,490,177,'03B · INDEPENDENT' if not zh else '03B · 独立审阅','人独立阅读与编码' if zh else 'People read and code',['按人的 codebook 填写空白表单；','个人包中不含 AI 建议和他人反馈。','可按轮次或审阅者选择模式。'] if zh else ['Blank form + human codebook + source.','AI and peer suggestions are omitted.','Choose mode by round or reviewer.'],HUMAN)
 f.line('M305 652 V684 H565 V713');f.line('M825 652 V684 H565',False)
 f.box(50,720,1030,102,'04 · 软件' if zh else '04 · SOFTWARE','各自导出 JSON，再发还给协调者' if zh else 'Separate JSON returns → validated comparison.',['核对来源、版本和任务范围；区分已处理、未完成和需要裁决。'] if zh else ['Check sources, versions and coverage. Preserve pending work and disagreement.'],GRAY)
 f.line('M565 822 V851')
 f.box(50,860,1030,102,'05 · 人与软件' if zh else '05 · HUMANS + SOFTWARE','人裁决并授权，软件记录结果' if zh else 'People adjudicate and authorize; software records.',['AI 整理分歧和证据；未解决项仍保留，不自动作为最终结论。'] if zh else ['AI organizes evidence and differences. Unresolved items do not silently become final.'],HUMAN)
 f.line('M565 962 V987')
 f.rect(50,994,1030,69,INK,INK);f.text(76,1037,'可追溯的结果台账 · 已授权判断 + 未解决项 + 需重新核验的依赖' if zh else 'Traceable ledger · authorized values + unresolved items + stale dependencies',23,'#fff',550)
 f.line('M1080 1030 H1121 V210 H1086',True,HUMAN,True)
 f.text(50,1094,'规则或 PDF 改变 → 新版本、重新编码与核验；旧确认不自动沿用。' if zh else 'Rule or PDF changes → a new version, recoding and re-verification; old approvals do not transfer.',18,GRAY)
 f.save('workflow-zh.svg' if zh else 'workflow-en.svg')

def tall(zh=False):
 f=Figure(1100,490,'TALL：人的修订与版本后果' if zh else 'TALL: human revision and its workflow consequence')
 f.text(40,42,'CASE 01 / TALL',16,HUMAN,700);f.text(40,87,'一个质量判断改变之后' if zh else 'When a quality judgment changes',33,INK,700)
 f.box(40,122,300,200,'01 · 历史记录' if zh else '01 · EARLIER NOTE','保留的先前状态' if zh else 'Earlier retained state',['Q2: Yes','Q4: Can’t tell','Gate: REVIEW'],GRAY)
 f.box(400,122,300,200,'02 · 人的裁决' if zh else '02 · HUMAN ADJUDICATION','更新后的状态' if zh else 'Adjudicated state',['Q2: No','Q4: No','Gate: FAIL'],HUMAN)
 f.box(760,122,300,200,'03 · SKILL 的处理' if zh else '03 · SKILL CONSEQUENCE','检查受影响的工作' if zh else 'Revisit affected work',['标记依赖字段失效','重新核验与重算','保留历史及理由'] if zh else ['Flag registered dependencies.','Reverify / recompute.','Preserve history and reasons.'],AI)
 f.line('M340 222 H392');f.line('M700 222 H752',True,GRAY,True)
 f.text(40,363,['前两框：I031 的保留记录（2026-07-20）；第三框：可复用 skill 的处理要求。','这里的 Q2/Q4 gate 是 TALL 的项目规则，不是通用 MMAT 门槛。','纳入判断保持 Include。历史修订并不等于独立基准验证了某个判断。'] if zh else ['First two boxes: the retained I031 record (2026-07-20). Third: the reusable skill’s required response.','The Q2/Q4 gate is specific to TALL; it is not a universal MMAT cutoff.','Screening remained Include. The historical revision is not an independent validity benchmark.'],19,GRAY,gap=32)
 f.save('tall-change-zh.svg' if zh else 'tall-change-en.svg')

def agency(zh=False):
 f=Figure(1100,525,'Agency：原文、编码和综合的边界' if zh else 'Agency: separate source reporting, coding and synthesis')
 f.text(40,42,'CASE 02 / AGENCY',16,AI,700);f.text(40,87,'从一篇 review 到跨 review 的判断' if zh else 'From one review to a cross-review claim',32,INK,700)
 f.box(40,122,300,246,'01 · SOURCE / 原文' if zh else '01 · SOURCE REPORTING','原文怎样报告' if zh else 'What the review reports',['Measurement types:','“self-report or','behavioural/trace”','MR00192 · PDF p. 6'],GRAY)
 f.box(400,122,300,246,'02 · CODING / 编码' if zh else '02 · DESCRIPTIVE CODING','按人的规则解释' if zh else 'Apply the team’s rule',['测量类型有明确区分','保留原文及页码','人核验这个解释'] if zh else ['Measurement types are','explicitly differentiated.','Keep the quote and location.','People verify the interpretation.'],HUMAN)
 f.box(760,122,300,246,'03 · SYNTHESIS / 综合' if zh else '03 · CROSS-REVIEW SYNTHESIS','需要多篇 review' if zh else 'Needs multiple reviews',['跨研究有哪些一致与差异？','来源是否重复？','不能从单篇直接得出','agency 增强或削弱。'] if zh else ['What converges or conflicts?','Are underlying studies shared?','One review alone cannot','establish an agency effect.'],AI)
 f.line('M340 242 H392');f.line('M700 242 H752',True,GRAY,True)
 f.text(40,408,['Agency 是 review 层级的试点适配，尚不是完成的跨 review 综合或独立验证。','复用的是原文定位、分层编码、个人审阅和回传流程；研究单位与规则由项目定义。'] if zh else ['Agency is a review-level pilot adaptation, not a completed synthesis or independent validation.','Source links, layered coding and reviewer returns transfer; units and research rules remain project-specific.'],19,GRAY,gap=32)
 f.save('agency-layers-zh.svg' if zh else 'agency-layers-en.svg')

if __name__=='__main__':
 for zh in (False,True):workflow(zh);tall(zh);agency(zh)
 print('Generated six workflow/case SVGs.')
