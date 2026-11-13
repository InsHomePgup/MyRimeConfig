"""把生成的键盘配置画成示意图（demo.png），左浅色右深色。需要 Pillow。

只是近似预览：按 iPhone 393pt 宽度计算布局，SF Symbols 图标画不出来，用图标名缩写代替。
也可以单独运行，输出到 build/preview-<键盘>.png，在电脑上检查布局：
    python3 yuanshu-skin/demo.py
"""

import os

from PIL import Image, ImageDraw, ImageFont

WIDTH = 393
SCALE = 3
GAP = 24

FONT_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "build", "MyRime", "fonts", "MiSans-Regular.ttf"),
    "/mnt/c/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/msyh.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
ICONS = {
    "shift": "⇧", "shift.fill": "⇧", "capslock.fill": "⇪", "delete.left": "⌫",
    "face.smiling": "☺", "keyboard": "⌨", "text.bubble": "…", "doc.on.clipboard": "▤",
    "chevron.down": "∨", "arrow.left": "←", "xmark": "×", "return": "↵",
}


SYMBOL_FONTS = ["/mnt/c/Windows/Fonts/seguisym.ttf", "C:/Windows/Fonts/seguisym.ttf",
                "/System/Library/Fonts/Apple Symbols.ttf"]


def _font(size, symbol=False):
    for f in (SYMBOL_FONTS if symbol else []) + FONT_CANDIDATES:
        if os.path.exists(f):
            return ImageFont.truetype(f, int(size * SCALE))
    return ImageFont.load_default()


def _rgb(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + ((int(c[6:8], 16),) if len(c) == 8 else (255,))


def _first_style(ref):
    """条件样式取第一个分支。"""
    if isinstance(ref, list) and ref and isinstance(ref[0], dict):
        name = ref[0]["styleName"]
        return name if isinstance(name, list) else [name]
    if isinstance(ref, list):
        return ref
    return [ref] if ref else []


def _width(spec, total):
    if isinstance(spec, dict):
        return spec["percentage"] * total
    return float(spec)


def _layout_row(sheet, cells, total):
    widths = []
    for c in cells:
        size = sheet[c].get("size", {})
        widths.append(_width(size["width"], total) if "width" in size else None)
    fixed = sum(w for w in widths if w is not None)
    flex = [w for w in widths if w is None]
    rest = (total - fixed) / len(flex) if flex else 0
    return [w if w is not None else rest for w in widths]


def _draw_cell(draw, sheet, name, x, y, w, h):
    node = sheet[name]
    bounds = node.get("bounds")
    if bounds:
        bw = _width(bounds["width"], w)
        if bounds.get("alignment") == "right":
            x += w - bw
        elif bounds.get("alignment") != "left":
            x += (w - bw) / 2
        w = bw
    for bg in _first_style(node.get("backgroundStyle")):
        st = sheet[bg]
        ins = st.get("insets", {})
        r = [x + ins.get("left", 0), y + ins.get("top", 0),
             x + w - ins.get("right", 0), y + h - ins.get("bottom", 0)]
        rad = st.get("cornerRadius", 0) * SCALE
        box = [v * SCALE for v in r]
        if st.get("normalShadowColor"):
            draw.rounded_rectangle([box[0], box[1] + SCALE, box[2], box[3] + SCALE], rad,
                                   fill=_rgb(st["normalShadowColor"]))
        if st.get("normalLowerEdgeColor"):
            draw.rounded_rectangle([box[0], box[1] + SCALE, box[2], box[3] + SCALE], rad,
                                   fill=_rgb(st["normalLowerEdgeColor"]))
        draw.rounded_rectangle(box, rad, fill=_rgb(st["normalColor"]))
    for fg in _first_style(node.get("foregroundStyle")):
        st = sheet[fg]
        if st["buttonStyleType"] == "text":
            text = st["text"]
            if text.startswith("$"):
                text = {"$returnKeyType": "换行", "$rimeSchemaName": "虎码官方单字"}.get(text, "")
            size = st.get("fontSize", 16)
        else:
            text = ICONS.get(st["systemImageName"], "?")
            size = st.get("fontSize", 18)
        c = st.get("center", {})
        cx = (x + w * c.get("x", 0.5)) * SCALE
        cy = (y + h * c.get("y", 0.5)) * SCALE
        font = _font(size, symbol=st["buttonStyleType"] != "text")
        draw.text((cx, cy), text, fill=_rgb(st["normalColor"]), font=font, anchor="mm")


def _draw_area(draw, sheet, layout, x, y, w, h):
    rows = layout
    rh = h / len(rows)
    for i, r in enumerate(rows):
        cells = [c["Cell"] for c in r["HStack"]["subviews"]]
        cx = x
        for name, cw in zip(cells, _layout_row(sheet, cells, w)):
            _draw_cell(draw, sheet, name, cx, y + i * rh, cw, rh)
            cx += cw


def _draw_keyboard(img, sheet, ox, colors):
    draw = ImageDraw.Draw(img, "RGBA")   # RGBA 模式按透明度叠加
    th, kh = sheet["toolbarHeight"], sheet["keyboardHeight"]
    # 皮肤背景是透明的，预览时用一块纯色模拟系统玻璃
    draw.rounded_rectangle([ox * SCALE, 0, (ox + WIDTH) * SCALE, (th + kh) * SCALE], 28 * SCALE,
                           fill=_rgb(colors["preview_glass"]))
    ti = sheet["toolbarStyle"].get("insets", {})
    _draw_area(draw, sheet, sheet["toolbarLayout"], ox + ti.get("left", 0), 0,
               WIDTH - ti.get("left", 0) - ti.get("right", 0), th)
    ki = sheet["keyboardStyle"]["insets"]
    _draw_area(draw, sheet, sheet["keyboardLayout"], ox + ki["left"], th + ki["top"],
               WIDTH - ki["left"] - ki["right"], kh - ki["top"] - ki["bottom"])


def render(path, light, dark, colors):
    h = light["toolbarHeight"] + light["keyboardHeight"]
    img = Image.new("RGB", ((WIDTH * 2 + GAP) * SCALE, h * SCALE), (255, 255, 255))
    _draw_keyboard(img, light, 0, colors["light"])
    _draw_keyboard(img, dark, WIDTH + GAP, colors["dark"])
    img.save(path)


if __name__ == "__main__":
    import build
    os.makedirs(build.OUT_ROOT, exist_ok=True)
    for kind, (_, fn) in build.KEYBOARDS.items():
        out = os.path.join(build.OUT_ROOT, "preview-%s.png" % kind)
        render(out, fn("light"), fn("dark"), build.COLORS)
        print("已生成 %s" % out)
