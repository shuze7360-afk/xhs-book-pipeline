# -*- coding: utf-8 -*-
"""阶段6辅助：从运行文件夹的 05-发布稿.md 组装发布配置。

用法:
    python build_publish_config.py <运行文件夹> [--title "标题"] [--port 18060]

行为:
    1. 从 05-发布稿.md 的 BODY-START/BODY-END 标记间提取正文（去HTML注释）写入 正文.txt；
       安全线: >935 警告（平台计数差浮动 +38~48），>960 拒绝。
    2. 标题取 --title；未给则找 05 中带 ✅【用户已选定】标记的标题行；都没有则报错。
    3. 标签取「## 标签（发布时粘贴）」节，去 # 前缀。
    4. 图片按文件名排序取 cards/*.png。
    5. 写出 <运行文件夹>/publish_config.json，随后交给 publish_direct.py 发布。
"""
import argparse, json, pathlib, re, sys

SAFE, HARD = 935, 960

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_folder")
    ap.add_argument("--title", default=None)
    ap.add_argument("--port", type=int, default=18060)
    a = ap.parse_args()
    run = pathlib.Path(a.run_folder)
    s = (run / "05-发布稿.md").read_text(encoding="utf-8")

    m = re.search(r"<!--BODY-START-->(.*?)<!--BODY-END-->", s, re.S)
    if not m:
        raise SystemExit("05 中找不到 BODY-START/BODY-END 标记")
    body = re.sub(r"<!--.*?-->", "", m.group(1), flags=re.S).strip()
    if len(body) > HARD:
        raise SystemExit(f"正文 {len(body)} 字 > {HARD}，先删减")
    warn = f"（警告：>{SAFE}，平台计数差浮动 +38~48，有超限风险）" if len(body) > SAFE else ""
    print(f"正文 {len(body)} 字{warn}")

    title = a.title
    if not title:
        cand = [l for l in s.splitlines() if "✅" in l and "【用户已选定】" in l]
        if not cand:
            raise SystemExit("未提供 --title，且 05 中没有 ✅【用户已选定】标记的标题")
        title = re.sub(r"^\d+\.\s*\*\*[^*]+?\*\*[：:]\s*", "", cand[0]).split("✅")[0].strip()
    if len(title) > 20:
        raise SystemExit(f"标题 {len(title)} 字 > 20")

    tm = re.search(r"## 标签（发布时粘贴）\s*\n\n(.+)", s)
    tags = [t.strip().lstrip("#") for t in tm.group(1).split() if t.strip()] if tm else []
    images = sorted(str(p) for p in (run / "cards").glob("*.png"))
    if not images:
        raise SystemExit("cards/ 下没有 PNG")

    cfg = {"port": a.port, "title": title, "content_file": str(run / "正文.txt"),
           "images": images, "tags": tags}
    (run / "publish_config.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    (run / "正文.txt").write_text(body, encoding="utf-8")
    print(f"已写出 publish_config.json（标题{len(title)}字 / {len(images)}图 / {len(tags)}标签）")
    print(f"下一步: python publish_direct.py \"{run / 'publish_config.json'}\"")

if __name__ == "__main__":
    main()
