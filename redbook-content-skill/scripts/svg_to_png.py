#!/usr/bin/env python3
"""
redbook — SVG → PNG 栅格化（小红书 3:4 图文）

把 svg_output/ 下的设计稿渲染成手机可用的 PNG。自动多后端回退：
  Playwright (chromium)  →  resvg  →  cairosvg
按保真度从高到低。无可用后端时报错并给出安装指引。

用法:
    python svg_to_png.py <svg_file_or_dir> [--out <dir>] [--scale 2] [--backend auto]
    python svg_to_png.py 01_封面.svg --out ./png --scale 2
    python svg_to_png.py ./svg_output --out ./png

Windows 注意事项:
    - Python 命令：Windows 上 python3 可能不存在，用 python 代替。
      若使用 Anaconda，确保 conda 环境已激活：conda activate <env>
    - 编码：Windows 默认 GBK 编码无法输出 emoji（✅❌等），
      脚本会自动设置 stdout/stderr 为 UTF-8；
      若手动运行，也可先设置环境变量：set PYTHONIOENCODING=utf-8
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# Windows GBK 编码无法输出 emoji，强制切 UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CANVAS_W, CANVAS_H = 1242, 1660


def _html_wrapper(svg_path: Path) -> str:
    """用 <img> 嵌入 SVG，固定画布尺寸，白底兜底。"""
    return f"""<!doctype html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;width:{CANVAS_W}px;height:{CANVAS_H}px;background:#ffffff;overflow:hidden">
<img src="file:///{svg_path.resolve().as_posix()}" width="{CANVAS_W}" height="{CANVAS_H}" style="display:block"/>
</body>
</html>"""


def render_playwright(svg_path: Path, png_path: Path, scale: int) -> bool:
    try:
        from playwright.sync_api import sync_playwright  # noqa
    except Exception:
        return False
    import tempfile
    html = _html_wrapper(svg_path)
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html)
        html_path = Path(f.name)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(
                viewport={"width": CANVAS_W, "height": CANVAS_H},
                device_scale_factor=scale,
            )
            page.goto(html_path.as_uri())
            page.wait_for_timeout(400)  # 等字体/外链资源
            page.screenshot(
                path=str(png_path),
                clip={"x": 0, "y": 0, "width": CANVAS_W, "height": CANVAS_H},
            )
            browser.close()
        return png_path.exists()
    except Exception as e:  # noqa
        print(f"  [playwright] 失败: {e}", file=sys.stderr)
        return False
    finally:
        html_path.unlink(missing_ok=True)


def render_resvg(svg_path: Path, png_path: Path, scale: int) -> bool:
    if not shutil.which("resvg"):
        return False
    out_w = CANVAS_W * scale
    out_h = CANVAS_H * scale
    try:
        r = subprocess.run(
            ["resvg", str(svg_path), str(png_path),
             "--width", str(out_w), "--height", str(out_h)],
            capture_output=True, text=True,
        )
        # 某些 resvg 版本不支持 --width/--height，退化为不带尺寸
        if r.returncode != 0:
            r = subprocess.run(["resvg", str(svg_path), str(png_path)],
                               capture_output=True, text=True)
        return png_path.exists()
    except Exception as e:  # noqa
        print(f"  [resvg] 失败: {e}", file=sys.stderr)
        return False


def render_cairosvg(svg_path: Path, png_path: Path, scale: int) -> bool:
    try:
        import cairosvg  # noqa
    except Exception:
        return False
    try:
        cairosvg.svg2png(
            url=str(svg_path),
            write_to=str(png_path),
            output_width=CANVAS_W * scale,
            output_height=CANVAS_H * scale,
            background_color="white",
        )
        return png_path.exists()
    except Exception as e:  # noqa
        print(f"  [cairosvg] 失败: {e}", file=sys.stderr)
        return False


BACKENDS = {
    "playwright": render_playwright,
    "resvg": render_resvg,
    "cairosvg": render_cairosvg,
}


def rasterize_one(svg_path: Path, png_path: Path, scale: int, backend: str) -> bool:
    png_path.parent.mkdir(parents=True, exist_ok=True)
    if backend == "auto":
        for name in ("playwright", "resvg", "cairosvg"):
            fn = BACKENDS[name]
            if fn(svg_path, png_path, scale):
                print(f"  ✅ {svg_path.name} → {png_path.name}  (backend: {name})")
                return True
        return False
    fn = BACKENDS.get(backend)
    if not fn:
        print(f"  ❌ 未知后端: {backend}", file=sys.stderr)
        return False
    if fn(svg_path, png_path, scale):
        print(f"  ✅ {svg_path.name} → {png_path.name}  (backend: {backend})")
        return True
    print(f"  ❌ 后端 {backend} 不可用或失败", file=sys.stderr)
    return False


def main():
    ap = argparse.ArgumentParser(description="小红书 SVG → PNG 栅格化")
    ap.add_argument("input", help="SVG 文件或目录")
    ap.add_argument("--out", default=None, help="输出目录（默认 ./png 或同名目录）")
    ap.add_argument("--scale", type=int, default=2, help="倍率 1 或 2（默认 2 = 2484×3320）")
    ap.add_argument("--backend", default="auto", help="auto / playwright / resvg / cairosvg")
    args = ap.parse_args()

    src = Path(args.input)
    if src.is_dir():
        svgs = sorted(src.glob("*.svg"))
        if not svgs:
            print("未找到 SVG 文件。", file=sys.stderr)
            sys.exit(1)
        out_dir = Path(args.out) if args.out else src.parent / "png"
        print(f"批量栅格化 {len(svgs)} 张 → {out_dir}")
        ok = 0
        for s in svgs:
            p = out_dir / (s.stem + ".png")
            if rasterize_one(s, p, args.scale, args.backend):
                ok += 1
        print(f"\n完成：{ok}/{len(svgs)} 张成功。")
        sys.exit(0 if ok == len(svgs) else 1)
    else:
        if not src.exists():
            print(f"文件不存在: {src}", file=sys.stderr)
            sys.exit(1)
        out_dir = Path(args.out) if args.out else src.parent
        p = out_dir / (src.stem + ".png")
        if not rasterize_one(src, p, args.scale, args.backend):
            print("\n所有后端均不可用。安装其一后重试：", file=sys.stderr)
            print("  pip install playwright && playwright install chromium", file=sys.stderr)
            print("  # 或下载 resvg 二进制加入 PATH", file=sys.stderr)
            print("  pip install cairosvg", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
