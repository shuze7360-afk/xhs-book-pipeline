# -*- coding: utf-8 -*-
"""小红书直连发布脚本：绕开 MCP 客户端 60 秒工具超时。

用法:
    python publish_direct.py publish_config.json

配置文件字段:
    port          本地 xiaohongshu-mcp 服务端口（默认 18060）
    title         笔记标题（<=20字）
    content_file  正文文本文件路径（<=960字，见 references/xhs-publish.md）
    images        图片绝对路径列表
    tags          话题标签列表

协议: JSON-RPC over HTTP (streamable MCP)
  1. initialize 握手 -> 取响应头 mcp-session-id
  2. notifications/initialized
  3. tools/call publish_content，超时 280s
"""
import json, sys, pathlib, urllib.request, urllib.error

def rpc(base, session, payload, timeout=280):
    headers = {"Content-Type": "application/json",
               "Accept": "application/json, text/event-stream"}
    if session:
        headers["mcp-session-id"] = session
    req = urllib.request.Request(base, data=json.dumps(payload).encode("utf-8"), headers=headers)
    try:
        r = urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code}: {e.read().decode('utf-8')[:300]}")
    sid = r.headers.get("mcp-session-id")
    raw = r.read().decode("utf-8")
    if not raw.strip():
        return {}, sid
    if "data:" in raw:  # SSE 帧
        for line in raw.splitlines():
            if line.startswith("data:"):
                return json.loads(line[5:].strip()), sid
        raise SystemExit(f"无法解析的SSE响应: {raw[:300]}")
    return json.loads(raw), sid

def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    cfg = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    port = cfg.get("port", 18060)
    base = f"http://localhost:{port}/mcp"
    content = pathlib.Path(cfg["content_file"]).read_text(encoding="utf-8").strip()
    if len(content) > 960:
        raise SystemExit(f"正文 {len(content)} 字超过 960 安全线，先删减（小红书计数器约为 len()+38，上限1000）")

    session = None
    _, session = rpc(base, session, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": "2024-11-05", "capabilities": {},
        "clientInfo": {"name": "direct-publish", "version": "1.0"}}})
    rpc(base, session, {"jsonrpc": "2.0", "method": "notifications/initialized"})

    res, _ = rpc(base, session, {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {
        "name": "publish_content",
        "arguments": {"title": cfg["title"], "content": content,
                      "images": cfg["images"], "tags": cfg.get("tags", [])}}})
    text = json.dumps(res, ensure_ascii=False)
    print(text[:2000])
    if '"isError": true' in text:
        raise SystemExit(1)
    print("\n发布指令已完成。请到小红书主页核对笔记是否可见，并记录链接。")

if __name__ == "__main__":
    main()
