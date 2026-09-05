# 小红书配图与发布（阶段5-7）

## 阶段5 · 配图（Kami 纸感设计系统）

**设计约束**（对标 tw93/Kami 的纸感文档风格）：
- 画布 3:4（1242×1656，导出 device_scale_factor=2 得 2484×3312）
- 底色羊皮纸 `#f5f4ed`，唯一强调色墨蓝 `#1B365D`，近黑 `#141413`，辅助灰 `#6b6a64`
- 中文衬线字体（如仓耳今楷 TsangerJinKai02 / 思源宋体），标题 weight 500
- 组件：eyebrow（蓝色小字标签）、编号条目（**编号与标题同行、正文悬挂缩进**）、底部引文 callout（浅蓝底+左蓝边）、页脚（账号名+页码）
- 结构：①封面（大字观点+内容预览卡）②解决什么问题 ③核心观点 ④质疑和联想 ⑤可执行行动

**生成管线**：改 [scripts/xhs_cards_template.py](../scripts/xhs_cards_template.py) 顶部的内容区（标题/各卡条目），运行生成 HTML；再跑 [scripts/render_cards.py](../scripts/render_cards.py) 用 Playwright 截图。

**渲染坑**：
- Edge 无头 `--screenshot` 不稳定，不用；
- chromium 连续渲染多张会崩，**每张图独立 launch 浏览器实例**；
- 截图前 `document.fonts.ready` + 短暂等待，确保衬线字体加载完成。

## 阶段5 · 文案适配与风格守恒

- 标题 ≤20 字（问题型/结论型/身份型三选一备选）；
- **发布版正文 ≤935 字**（小红书计数器 ≈ Python len()+38~48，随标点/特殊字符构成浮动：实测982→1020(+38)、954→1002(+48)，上限1000）；
- 标签约 10 个，垂直标签（书名/作者/领域）+ 泛流量标签（读书笔记/个人成长等）混合；
- 干货放卡片图，正文只留短引子 + 四部分精华 + 结尾互动问题 + 来源说明。

**风格守恒清单**（发布前自查）：
- 竞品只学"形"（3:4卡片图、收藏钩子、标签结构），**不学焦虑营销腔**（"看完失眠""淘汰""逆袭"类标题一律不用）；
- 保留：四部分结构、边界词（"现阶段""我目前的猜想""暂时"）、真实经历、结尾真实经验提问、来源说明；
- 调整仅限形式：字数压缩、图卡化、标签组合。

**审核闸门**：封面图 + 内容卡 + 终稿文案交用户审核，明确"确认发布"后才进入阶段6。"继续"不算授权。

## 阶段6 · 发布（直连 API 法）

**发布前预检**：①服务存活——没起则跑 xiaohongshu-mcp 目录的 `start-service.bat`（开机自启不可靠）；②登录态——`curl http://localhost:18060/api/v1/login/status` 确认 `is_logged_in: true`。

**为什么不用 MCP 工具层**：客户端 60 秒工具超时会掐断多图上传（服务端流程随之中断），5 张图必超。直连本地 MCP 服务的 HTTP 端口（配置可用脚本从 05 自动组装）：

```bash
python scripts/build_publish_config.py <运行文件夹>   # 生成 正文.txt + publish_config.json
python scripts/publish_direct.py <运行文件夹>/publish_config.json
```

配置文件示例（publish_config.json，build 脚本自动生成，也可手写）：
```json
{
  "port": 18060,
  "title": "20字以内标题",
  "content_file": "正文.txt",
  "images": ["01_封面.png", "02.png", "03.png", "04.png", "05.png"],
  "tags": ["读书笔记", "AI", "..."]
}
```

协议要点（脚本已实现）：
1. `POST http://localhost:<port>/mcp`，头必须带 `Accept: application/json, text/event-stream`；
2. 先 `initialize` 握手，从响应头取 `mcp-session-id`，后续请求带上；再发 `notifications/initialized`；
3. `tools/call` 调 `publish_content`，超时给 280 秒；
4. 响应是 SSE 帧，取 `data:` 行解析 JSON。

**发布前核验**：`/api/v1/login/status` 确认登录态；发布返回里出现"发布完成"字样即为成功，随后调服务工具 `get_my_profile` 核对主页可见，取 note id 与 xsec_token 拼链接：`https://www.xiaohongshu.com/explore/<id>?xsec_token=<token>&xsec_source=pc_user`。

**红线与坑**：
- **绝不调用 `delete_cookies`**——会清空登录态，只能重新扫码。恢复登录：运行 MCP 服务目录下的登录辅助程序（形如 `xiaohongshu-login.exe`，会弹出可见窗口扫码，cookies 文件自动回写，服务无需重启）。
- **风控 300012"IP存在风险"**：自建 playwright/chromium 自动化（无论有头、直连、注入会话）会被指纹风控拦截。MCP 服务自带浏览器带指纹一致性伪装，是可信环境——**一切读写操作都走 MCP，不要用自己的浏览器硬闯**。
- `get_login_qrcode` 不弹窗且每次调用作废上一个二维码；等用户扫码一律用登录辅助程序弹窗。
- 发布失败若提示字数超限，按上文 ≤935 安全线删减；**用户"确认发布"之后的删减必须最小化，删改处记录进 05-发布稿.md 并在交付时明确告知用户**。

## 阶段7 · 复盘回填

发布成功后立即记录：笔记链接、发布时间、过程中的新坑（写进用户的知识库/经验文档）。
数据积累 3-7 天后复盘四问：
1. 哪一条"我的质疑"最能引发讨论？
2. 哪一条行动真正执行了？留下了什么产出？
3. 哪些表述像真实判断，哪些仍像通用 AI 文本？
4. 下一篇是否需要调整篇幅、问题深度或平台格式？
