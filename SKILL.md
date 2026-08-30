---
name: xhs-book-pipeline
description: 小红书读书笔记自动化流水线：Z-Library抓原书→转Markdown→深度阅读分析（双向钢人论证+两道人工闸门）→Kami纸感配图→小红书直连API发布→经验复盘回填。当用户提到"读书笔记流水线"、"启动小红书读书笔记流水线"、"把某本书做成小红书笔记"、"发布读书笔记"、抓取电子书写笔记、或任何"从一本书到一篇小红书帖子"的端到端需求时使用——即使用户没有明说"流水线"三个字。
---

# 小红书读书笔记流水线

把一本书变成一篇符合博主人设、经过人工审核的小红书图文笔记。全程 7 个阶段、**两道人工闸门**，顺序不可打乱，闸门不可跳过。

## 流水线总览

| 阶段 | 做什么 | 产出 | 详细文档 |
|---|---|---|---|
| 0 | 确认书目（书名/作者/版本） | 本次运行目标 | 本页 |
| 1 | Z-Library 搜索并下载原书 | epub/pdf 文件 | [references/zlibrary-fetch.md](references/zlibrary-fetch.md) |
| 2 | **先转 Markdown 再读取**，生成交接完整性声明 | 书名.md + 损耗记录 | [references/zlibrary-fetch.md](references/zlibrary-fetch.md) |
| 3 | 第一阶段分析：完整性声明+问题概括+3核心观点+3双向钢人问题 | 对话中的分析输出 | [references/reading-workflow.md](references/reading-workflow.md) |
| 4 | 第二阶段成稿：四部分读书笔记+社交媒体发布稿 | 笔记文件 + 发布稿 | [references/reading-workflow.md](references/reading-workflow.md) |
| 5 | Kami 纸感配图 + 文案适配小红书，**交用户审核** | 封面+内容卡+终稿文案 | [references/xhs-publish.md](references/xhs-publish.md) |
| 6 | 小红书发布（直连 API 法） | 笔记上线 + 链接 | [references/xhs-publish.md](references/xhs-publish.md) |
| 7 | 回填链接/数据/新坑，复盘四问 | 经验沉淀 | [references/xhs-publish.md](references/xhs-publish.md) |

## 两道闸门（红线，任何情况下不可跳过）

1. **阶段3 之后必须停止**：输出【等待你的真实反应】后立即停下，等用户逐题回答。没有用户的真实回答，不得生成"我的质疑和联想"、行动建议或发布成稿——替用户制造观点是本流水线最大的失败模式。
2. **阶段5 之后必须停止**：封面、内容卡、终稿文案交用户审核，用户明确回复"确认发布"（或同等明确指令）才能执行发布。"继续"、"嗯"不算授权。

## 阶段0 · 确定书目

- 用户口述书名 → 复述确认书名、作者、版本（同书多版本/修订版要问清）。
- 用户没指明 → 列出其阅读清单/最近在读的候选，让用户选。
- 开一个运行档案记录：书目、开始时间、各阶段状态、最终笔记链接。

## 阶段1-2 · 抓书与转MD（概要）

用 `zlibrary` MCP 搜索并下载（优先 epub）；**先转 Markdown 再读取**；转换损耗（插图/表格/页码/OCR错字）必须记录并写进完整性声明。搜不到原书时问用户换源，**禁止在没读原书的情况下假装读过**。操作细节、故障排查、转换命令见 [references/zlibrary-fetch.md](references/zlibrary-fetch.md)。

## 阶段3-4 · 阅读分析与成稿（概要）

内容引擎在 [references/reading-workflow.md](references/reading-workflow.md)——博主人设、判断顺序、表达方式、四部分结构、双向钢人论证规则都在里面，执行前必读。铁律：作者观点/客观事实/AI分析/用户判断四类信息严格分开；猜想标记为"我目前的猜想"；引文无页码时标"位置待核对"。

## 阶段5 · 配图与审核（概要）

- 配图走 Kami 纸感设计系统（羊皮纸底 + 单一墨蓝强调 + 中文衬线字体），模板见 [scripts/xhs_cards_template.py](scripts/xhs_cards_template.py)，渲染见 [scripts/render_cards.py](scripts/render_cards.py)。
- 文案适配：标题≤20字、**正文≤960字**（小红书计数器比 Python len() 多算约38）、标签约10个。
- 竞品只学形式（卡片图/标题结构/标签），**不学焦虑营销腔**；过一遍风格守恒清单（见 xhs-publish.md）。

## 阶段6 · 发布（概要）

**不要用 MCP 工具层发布**（客户端60秒超时会掐断多图上传）。用 [scripts/publish_direct.py](scripts/publish_direct.py) 直连本地 MCP 服务的 JSON-RPC 接口，超时给足 280 秒。发布细节、风控规避、故障处理见 [references/xhs-publish.md](references/xhs-publish.md)。

## 阶段7 · 复盘回填

发布成功后立即回填：笔记链接、发布时间、过程中的新坑。数据积累 3-7 天后做复盘四问：哪条质疑最能引发讨论？哪条行动真正执行了？哪些表述像真实判断、哪些像通用AI文本？下一篇调整什么？
