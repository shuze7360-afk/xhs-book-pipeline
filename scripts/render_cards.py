# -*- coding: utf-8 -*-
"""渲染 Kami 风格卡片 HTML -> PNG (3:4, 1242x1656, 2倍清晰度)。

用法:
    python render_cards.py <html目录> [输出目录]

要求: 目录内每页一个 .html（页面尺寸 1242x1656）。
依赖: playwright（pip install playwright）+ 本机已有 chromium
      （自动在 %LOCALAPPDATA%/ms-playwright 下找 chrome.exe，找不到则用 playwright 默认浏览器）。
注意: 每张图独立启动浏览器实例——同一实例连渲多张会被目标站点/渲染器掐断。
"""
import glob, os, pathlib, sys

W, H = 1242, 1656

def find_chrome():
    local = os.environ.get("LOCALAPPDATA", "")
    for pat in ("chromium-*/chrome-win*/chrome.exe", "chromium-*/chrome-win/chrome.exe"):
        hits = sorted(glob.glob(os.path.join(local, "ms-playwright", pat)))
        if hits:
            return hits[-1]
    return None

def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    src = pathlib.Path(sys.argv[1])
    out = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else src
    out.mkdir(parents=True, exist_ok=True)
    htmls = sorted(src.glob("*.html"))
    if not htmls:
        raise SystemExit(f"{src} 下没有 .html")

    from playwright.sync_api import sync_playwright
    chrome = find_chrome()
    with sync_playwright() as p:
        for hf in htmls:
            kwargs = {"headless": True}
            if chrome:
                kwargs["executable_path"] = chrome
            browser = p.chromium.launch(**kwargs)
            page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=2)
            page.goto(f"file:///{hf.as_posix()}")
            page.evaluate("document.fonts.ready.then(()=>true)")
            page.wait_for_timeout(600)
            png = out / (hf.stem + ".png")
            page.screenshot(path=str(png))
            print("shot:", png.name)
            browser.close()  # 每张独立实例，防中途崩溃

if __name__ == "__main__":
    main()
