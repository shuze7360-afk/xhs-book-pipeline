# Z-Library 抓书与转 Markdown（阶段1-2）

## 前置条件

- `zlibrary` MCP 已在客户端配置（stdio，node + zlibrary-mcp），env 里设置：
  - `ZLIBRARY_EMAIL` / `ZLIBRARY_PASSWORD`（账号凭据走环境变量，**绝不写进任何文档或代码**）
  - `HTTPS_PROXY` / `HTTP_PROXY` 指向本地代理（如 `http://127.0.0.1:<本地代理端口>`）
- 本地代理进程必须运行中，否则全部网络错误。
- 免费账号每日约 10 本下载额度（`get_download_limits` 可查）；登录接口限流约 10 次/小时。

## 常用工具调用

| 工具 | 用途 |
|---|---|
| `search_books(query, count)` | 首选搜索 |
| `full_text_search` / `search_by_author` / `search_advanced` | 搜不到书名时的替代（全文/作者/ISBN） |
| `download_book_to_file` | 下载（优先 epub，其次 pdf） |
| `get_download_limits` / `get_download_history` | 额度与历史 |
| `process_document_for_rag` | 对下载文件直接做文本化（阶段2首选） |

## 已知的网络坑（速查）

1. **DNS 污染**：常见 z-lib 域名解析到 Facebook/Dropbox 网段是教科书级污染特征。鉴别法：`socket.getaddrinfo` 看 IP 网段 → 看页面 title（真站反爬页通常是 "Verifying your browser"）→ 直连/代理/DoH 三方对照。MCP 自带候选域名自动探测，会选健康域名，**不要手动访问可疑域名**。
2. **反爬墙（DiamWall）**：API 端点也会被拦。MCP 已内置适配；若报 `DiamWallError`，用 `ZLIBRARY_EAPI_DOMAIN` 环境变量钉死一个新可用域名（新域名从 `/eapi/info/domains` 返回列表里逐个探测）。
3. **Windows + 新版 Python 的依赖雷**：venv 里 aiodns 在 Windows DNS 罢工（删依赖声明即可，aiohttp 会回退系统解析器）；numpy 在过新 Python 版本会拉到 MINGW 实验轮子直接段错误（降到成熟 Python 版本重建 venv）。
4. 报错信息和包源码注释是第一手文档，先 grep 再上网搜。

## 阶段2 · 转 Markdown 再读取

**原则：先转 MD、后读取。** 直接读二进制浪费上下文且易乱码。

转换路径（按优先级）：
1. MCP 自带 `process_document_for_rag` 直接文本化；
2. PDF：`pip install pymupdf4llm` → `pymupdf4llm.to_markdown("书.pdf")` 写出 .md；
3. EPUB：`pip install ebooklib beautifulsoup4` 提取章节转 MD，或装 pandoc 后 `pandoc 书.epub -o 书.md`；
4. 扫描版 PDF（无文字层）→ 先问用户是否接受 OCR（成本高、有错字，必须在完整性声明注明）。

## 产出规范

- 转出的 MD 存放约定：`<笔记库>/书籍原文MD/书名.md`（按用户实际目录）。
- 文件头部写转换元信息：来源格式、转换工具、日期、**损耗记录**（插图丢失/表格变形/页码错位/OCR错字）。
- 生成交接给阅读分析阶段的**完整性声明**：书名/作者/版本/出版社、实际读取范围（全书逐章/部分章节/仅目录+简介）、损耗清单、引文标注规则（有页码标页码→无页码标章节→都没有标"位置待核对"）。

## 失败处理

搜不到原书 → 问用户：换版本？换来源？还是仅凭公开资料（目录+官方简介+作者公开发言）走流水线？最后一种情况完整性声明必须写明"未获取原书"，且分析里不得出现只有正文才有的细节。
