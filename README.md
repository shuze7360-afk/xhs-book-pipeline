# xhs-book-pipeline · 小红书读书笔记自动化流水线

一个 ZCode 技能（skill）：把**一本书**自动加工成一篇**经过人工审核的小红书图文笔记**。执行采用"编辑部团队"模式——主agent任主编，五个专岗 subagent（书探/拆书分析师/执笔编辑/美编/质量审核员）干活。

```
确定书目 → 书探：Z-Library 抓原书 → 转 Markdown → 拆书分析师：深度阅读分析（双向钢人论证）
→ 【闸门1：等待作者回答真实反应】 → 执笔编辑：四部分笔记 + 发布稿
→ 美编：Kami 纸感配图 → 质量审核员：独立合规审核 → 【闸门2：用户确认发布】
→ 小红书直连 API 发布 → 经验复盘回填
```

## 安装

复制到用户级技能目录即可被 ZCode / 兼容 agent 发现：

```bash
# Windows (PowerShell)
git clone https://github.com/<你>/xhs-book-pipeline.git "$env:USERPROFILE\.agents\skills\xhs-book-pipeline"

# macOS / Linux
git clone https://github.com/<你>/xhs-book-pipeline.git ~/.agents/skills/xhs-book-pipeline
```

触发：对 AI 说「启动小红书读书笔记流水线：《书名》」或"把《XX》做成小红书读书笔记"。

### 注册编辑部 subagent（可选，推荐）

把 `agents/` 下的 5 个注册壳复制到用户级子智能体目录，团队岗位即以命名 subagent 出现（可在 Settings → Subagents 看到）：

```powershell
Copy-Item "$env:USERPROFILE\.agents\skills\xhs-book-pipeline\agents\*.md" "$env:USERPROFILE\.zcode\agents\"
```

不注册也能跑：主编会自动降级为 `general-purpose` subagent + 岗位手册路径派工（见 team/README.md 的降级模式）。

## 前置依赖

| 依赖 | 说明 |
|---|---|
| `zlibrary` MCP | 书籍抓取（npm 全局包 `zlibrary-mcp`），凭据走环境变量 `ZLIBRARY_EMAIL/ZLIBRARY_PASSWORD`，需本地代理，免费账号日限约10本 |
| `xiaohongshu-mcp` | 本地小红书服务（默认端口 18060），发布走它的 HTTP 接口；登录用其登录辅助程序弹窗扫码 |
| Python | `playwright`（配图渲染）；转换按需 `pymupdf4llm` / `ebooklib` / `pandoc` |
| 中文创线字体（可选） | 如仓耳今楷，放在任意目录并用 `KAMI_FONT_DIR` 指向，无则回退系统宋体 |

## 目录结构

```
SKILL.md                      技能入口：编辑部团队编排规则 + 7阶段总表 + 两道人工闸门
agents/                       5个subagent注册壳（复制到 ~/.zcode/agents/ 即完成岗位注册）
team/                         岗位手册（唯一事实源）：书探/拆书分析师/执笔编辑/美编/质量审核员 + 架构说明
references/
  zlibrary-fetch.md           阶段1-2：抓书、DNS污染/反爬墙排查、转MD命令、完整性声明
  reading-workflow.md         阶段3-4：内容引擎——人设、风格锚点、双向钢人、四部分结构
  xhs-publish.md              阶段5-7：Kami配图规范、风格守恒清单、直连发布协议、风控规避
scripts/
  xhs_cards_template.py       Kami纸感卡片生成器（改内容区即可复用）
  render_cards.py             HTML→PNG 渲染（每张独立浏览器实例，防中途崩溃）
  publish_direct.py           直连 MCP 的 JSON-RPC 发布（绕开客户端60秒超时）
```

## 设计要点

- **编辑部团队**：编排与执行分离——主编（主agent）只做派工、验收、和用户对话；专岗 subagent 按岗位手册干活，交接靠编号文件（00~07），上下文隔离（美编拿不到原书全文，分析师拿不到营销约束）。架构详解见 [team/README.md](team/README.md)。
- **两道人工闸门**：分析完必须停下等作者回答"真实反应"（AI 不替人制造观点）；发布前必须拿到用户明确确认。闸门是主编专属职责，永不委派给 subagent。这是内容真实性的底线。
- **先转 MD 再读取**：书籍二进制先文本化并记录损耗，分析前声明实际读取范围，禁止"没读书硬写书评"。
- **直连 API 发布**：MCP 客户端 60 秒工具超时会掐断多图上传，脚本直接走服务的 JSON-RPC 接口，超时给足 280 秒。
- **风控规避**：小红书对自建自动化浏览器做指纹风控（错误码 300012），一切读写走 MCP 自带的可信浏览器环境；**严禁调用 delete_cookies 类接口**。

## 隐私说明

本仓库**不包含**任何账号凭据、邮箱、用户昵称/ID、已发布笔记链接、本机用户名路径。所有凭据通过环境变量注入；示例中的路径均为占位符，按自己的环境替换。
