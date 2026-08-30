# -*- coding: utf-8 -*-
"""Kami 纸感读书笔记卡片生成器（小红书 3:4, 1242x1656）。

用法:
    1. 修改下方 CONTENT（封面文案 + 4张内容卡的条目）
    2. python xhs_cards_template.py <输出目录>
    3. 再用 render_cards.py 把生成的 HTML 渲染成 PNG

可选环境变量:
    KAMI_FONT_DIR  指向含中文衬线字体(如 TsangerJinKai02-W04/W05.ttf)的目录；
                   未设置时回退系统字体（思源宋体/宋体）。

设计约束: 羊皮纸底 #f5f4ed + 唯一强调色墨蓝 #1B365D + 衬线字体；
编号与标题同行、正文悬挂缩进；底部引文 callout；页脚含页码。
"""
import pathlib, sys

# ============ 替换这里：本次笔记的全部内容 ============
COVER = {
    "eyebrow": "×××研究生的读书笔记",          # 身份行
    "big1": "执行会贬值",                        # 封面大字（第一行）
    "big2": "判断力不会",                        # 封面大字（第二行，强调色）
    "subtitle": ["AI 把执行变便宜之后，", "基本功还值不值得练？"],
    "metrics": [                                 # 内容预览三卡
        ("3 个", "作者核心观点<br>一句话概括"),
        ("3 个", "质疑和联想<br>来自真实体感"),
        ("3 条", "可执行行动<br>48 小时内可开始"),
    ],
    "quote": "「这里放全书最核心的一句官方简介或书中原话。」",
    "quote_src": "—— 书名与出处",
}
BOOK_HEADER = ("《书名》读书笔记", "作者 著<br>出版社 · 年.月")
CARDS = [
    # (编号, 标题, [(编号或None, 加粗导语, 正文), ...], 底部引文, 引文出处或None)
    ("PART 01", "这本书解决什么问题", [
        (None, "共同的困境：", "一两句话写普通读者会卡住的现状。"),
        (None, "两个常见的坑：", "写读者容易犯的两种错误。"),
        (None, "作者的判断：", "写全书立论的核心判断。"),
        (None, "这本书给什么：", "框架/方法论/工具，明确不是什么。"),
    ], "「这里放一句官方或书中的定位性引文。」", "—— 出处"),
    ("PART 02", "作者核心观点", [
        ("1.", "观点一（短语）", "底层逻辑+现实意义，并写清适用边界。"),
        ("2.", "观点二（短语）", "同上结构。"),
        ("3.", "观点三（短语）", "同上结构。"),
    ], "「书中的关键引文（位置待核对时须标注）。」", "—— 原书依据"),
    ("PART 03", "我的质疑和联想", [
        ("1.", "质疑一（短语）", "联想书本+联系现实，猜想以「我目前的猜想：」开头。"),
        ("2.", "质疑二（短语）", "同上结构，保留用户真实表述。"),
        ("3.", "质疑三（短语）", "同上结构。"),
    ], "一句收束性的话。", None),
    ("PART 04", "我的可执行行动", [
        ("1.", "行动一 + 时间盒", "具体做什么、产出、判断指标、停止条件。"),
        ("2.", "行动二", "同上。"),
        ("3.", "现阶段不做的", "明确不做什么，体现克制。"),
    ], "先积累基础能力，再追求短期成果；允许「现阶段暂时不行动」的结论。", None),
]
FOOTER_NAME = "账号名 · 读书笔记"   # 页脚署名
# ============ 内容区结束 ============

OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("cards_out")
OUT.mkdir(parents=True, exist_ok=True)
FONT_DIR = __import__("os").environ.get("KAMI_FONT_DIR", "")

FONTFACE = ""
if FONT_DIR:
    fd = pathlib.Path(FONT_DIR).as_posix()
    FONTFACE = (f'@font-face {{ font-family:"KamiSerif"; src:url("file:///{fd}/TsangerJinKai02-W04.ttf"); font-weight:400; }}'
                f'@font-face {{ font-family:"KamiSerif"; src:url("file:///{fd}/TsangerJinKai02-W05.ttf"); font-weight:500; }}')
SERIF = '"KamiSerif","Source Han Serif SC","Source Han Serif CN","SimSun",Georgia,serif'

CSS = f"""
{FONTFACE}
* {{ box-sizing:border-box; margin:0; padding:0; }}
:root {{ --parchment:#f5f4ed; --ivory:#faf9f5; --near-black:#141413; --dark-warm:#3d3d3a;
  --olive:#504e49; --stone:#6b6a64; --brand:#1B365D; --border:#e8e6dc; --tag-bg:#E4ECF5;
  --serif:{SERIF}; }}
html,body {{ width:1242px; height:1656px; overflow:hidden; background:var(--parchment);
  color:var(--near-black); font-family:var(--serif); letter-spacing:0.5px; }}
.page {{ width:1242px; height:1656px; padding:88px 92px 72px; display:flex; flex-direction:column; }}
.eyebrow {{ font-size:22px; color:var(--brand); letter-spacing:4px; font-weight:500; margin-bottom:18px; }}
.header {{ padding-bottom:26px; border-bottom:1px solid var(--border);
  display:flex; align-items:flex-end; justify-content:space-between; gap:24px; }}
h2 {{ font-size:52px; font-weight:500; line-height:1.18; }}
.meta {{ font-size:22px; color:var(--stone); text-align:right; line-height:1.5; white-space:nowrap; }}
.content {{ flex:1; padding-top:30px; display:flex; flex-direction:column; justify-content:space-evenly; }}
.item {{ display:grid; grid-template-columns:58px 1fr; gap:0 6px; }}
.item .no {{ font-size:46px; font-weight:500; color:var(--brand); line-height:1.35; }}
.item .txt {{ font-size:35px; line-height:1.72; color:var(--dark-warm); }}
.item .txt b, .dash .txt b {{ color:var(--near-black); font-weight:500; }}
.hl {{ color:var(--brand); font-weight:500; }}
.dash {{ display:grid; grid-template-columns:34px 1fr; }}
.dash .bar {{ color:var(--brand); font-size:31px; line-height:1.72; }}
.dash .txt {{ font-size:31px; line-height:1.72; color:var(--dark-warm); }}
.callout {{ background:var(--tag-bg); border-left:5px solid var(--brand); padding:26px 32px;
  font-size:29px; line-height:1.6; color:var(--brand); margin-top:24px; }}
.callout .src {{ display:block; margin-top:8px; font-size:22px; color:var(--stone); }}
.metrics {{ display:flex; gap:20px; margin-top:56px; }}
.metric {{ flex:1; background:var(--ivory); border:1px solid var(--border); border-radius:6px; padding:26px 28px; }}
.metric .v {{ font-size:34px; font-weight:500; color:var(--brand); margin-bottom:8px; }}
.metric .l {{ font-size:23px; color:var(--olive); line-height:1.45; }}
.footer {{ border-top:1px solid var(--border); padding-top:22px;
  display:flex; justify-content:space-between; font-size:21px; color:var(--stone); }}
"""

def shell(body, page_no, total=5, header=True):
    h = (f'<div class="header"><h2>{BOOK_HEADER[0]}</h2>'
         f'<div class="meta">{BOOK_HEADER[1]}</div></div>') if header else ""
    f = (f'<div class="footer"><span>{FOOTER_NAME}</span>'
         f'<span>{page_no:02d} / {total:02d}</span></div>')
    return (f'<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">'
            f'<style>{CSS}</style></head><body><div class="page">{h}{body}{f}</div></body></html>')

def callout(quote, src=None):
    s = f'<span class="src">{src}</span>' if src else ""
    return f'<div class="callout">{quote}{s}</div>'

pages = {}
c = COVER
pages["01_封面"] = shell(f"""
  <div style="flex:1; display:flex; flex-direction:column; justify-content:center;">
    <div class="eyebrow">{c['eyebrow']}</div>
    <div style="font-size:118px; font-weight:500; line-height:1.22;">{c['big1']}</div>
    <div style="font-size:118px; font-weight:500; line-height:1.22; color:var(--brand);">{c['big2']}</div>
    <div style="margin-top:52px; font-size:42px; color:var(--olive); line-height:1.5;">
      {c['subtitle'][0]}<br>{c['subtitle'][1]}</div>
    <div class="metrics">{''.join(f'<div class="metric"><div class="v">{v}</div><div class="l">{l}</div></div>' for v, l in c['metrics'])}</div>
  </div>{callout(c['quote'], c['quote_src'])}""", 1, header=False)

for i, (part, title, items, quote, qsrc) in enumerate(CARDS, start=2):
    body = f'<div class="content"><div class="eyebrow">{part}</div>'
    for num, lead, text in items:
        if num:
            body += (f'<div class="item"><div class="no">{num}</div>'
                     f'<div class="txt"><b>{lead}</b>{text}</div></div>')
        else:
            body += f'<div class="dash"><div class="bar">—</div><div class="txt"><b>{lead}</b>{text}</div></div>'
    body += "</div>" + callout(quote, qsrc)
    pages[f"{i:02d}_{title}"] = shell(body, i)

for name, html in pages.items():
    (OUT / f"{name}.html").write_text(html, encoding="utf-8")
print(f"生成 {len(pages)} 页 HTML -> {OUT}")
print("下一步: python render_cards.py", OUT)
