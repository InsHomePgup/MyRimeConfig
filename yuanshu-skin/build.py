#!/usr/bin/env python3
"""生成元书输入法（iOS）键盘皮肤「MyRime」。

用法:
    python3 yuanshu-skin/build.py

输出到 yuanshu-skin/build/（已被 .gitignore 忽略）：
    build/MyRime/        皮肤目录，deploy-yuanshu.py --skin 会把它传到手机 Skins/MyRime/
    build/MyRime.cskin   皮肤包，也可以 AirDrop / 隔空投送到手机，用元书打开导入

设计目标（仿微信输入法的手感）：
- 字母键不绑上划 / 下划，不加缩放动画。轻微拖动不会触发别的功能，按键位置也不会跳。
- 每个按键的点击区域铺满整个格子（键与键之间的缝隙也算），A / L、Shift / 删除
  的点击区域延伸到屏幕边缘；看得见的键帽只是格子里缩进去的一块。
- 外观跟 iOS 26/27 原生键盘一致：键盘区透明，透出系统的液态玻璃；按键同色、无底边。
- 中英切换用 RIME 的 ascii_mode（虎码、双拼都有这个开关），只有一套字母键盘。

布局、尺寸、颜色都集中在下面的常量里，改完重新运行即可。
目前只做了 iPhone 竖屏；横屏和 iPad 暂时沿用竖屏布局（不配会是空白键盘）。

依赖：只用标准库；装了 Pillow 时会画一张示意图当 demo.png，否则用纯色占位图。
"""

import json
import os
import shutil
import struct
import zipfile
import zlib

SKIN_NAME = "MyRime"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_ROOT = os.path.join(HERE, "build")

# ---------------------------------------------------------------- 配色
# 跟 iOS 26/27 原生键盘保持一致：键盘区不画背景，透出系统的液态玻璃容器
# （画了不透明背景会和系统容器的圆弧顶边出现接缝）；所有按键同一种颜色，没有底边。
# 颜色可写 #RRGGBBAA，最后两位是不透明度。
ACCENT = "#007AFF"               # 系统蓝：发送键、返回键、中英键的“英”

COLORS = {
    "light": {
        "keyboard_bg": "#FFFFFF03",  # 几乎全透明；完全透明时空白处可能收不到点击
        "key": "#FFFFFF",
        "key_hl": "#D1D4DA",
        "func": "#FFFFFF",
        "func_hl": "#D1D4DA",
        "shadow": "#00000026",       # 键帽下的细阴影，原生浅色键盘有一点
        "text": "#000000",
        "text_dim": "#8E8E93",
        "accent": ACCENT,
        "accent_hl": "#0062CC",
        "accent_text": "#FFFFFF",
        "toolbar_btn": "#FFFFFF03",
        "toolbar_btn_hl": "#0000001A",
        "hint_bg": "#FFFFFF",
        "hint_border": "#C6C6C8",
        "separator": "#C6C6C8",
        "candidate_hl": "#0000001A",
        "preview_glass": "#E3E5EA",  # 只用于电脑上的预览图，模拟系统玻璃
    },
    "dark": {
        "keyboard_bg": "#FFFFFF03",
        "key": "#FFFFFF33",          # 半透明浅灰，透出深色玻璃
        "key_hl": "#FFFFFF1A",
        "func": "#FFFFFF33",
        "func_hl": "#FFFFFF1A",
        "shadow": None,
        "text": "#FFFFFF",
        "text_dim": "#98989D",
        "accent": ACCENT,
        "accent_hl": "#0062CC",
        "accent_text": "#FFFFFF",
        "toolbar_btn": "#FFFFFF03",
        "toolbar_btn_hl": "#FFFFFF1A",
        "hint_bg": "#6C6C70",
        "hint_border": "#6C6C70",
        "separator": "#48484A",
        "candidate_hl": "#FFFFFF1A",
        "preview_glass": "#2C2C2E",
    },
}

# ---------------------------------------------------------------- 尺寸（单位 pt）
PREEDIT_HEIGHT = 25
TOOLBAR_HEIGHT = 46
KEYBOARD_HEIGHT = 216            # 4 行，每行约 52pt
KEYBOARD_INSETS = {"top": 3, "bottom": 3, "left": 2, "right": 2}
KEY_INSETS = {"top": 5, "bottom": 5, "left": 3, "right": 3}   # 键帽在格子里缩进，缝隙仍可点击
CORNER = 8
LETTER_FONT = 24
FUNC_FONT = 16
ICON_FONT = 19
TOOLBAR_BTN = 34                 # 工具栏圆形按钮直径
TOOLBAR_CELL = 48

ROW1 = "qwertyuiop"
ROW2 = "asdfghjkl"
ROW3 = "zxcvbnm"

# 发送 / 搜索 / 前往 等回车类型用强调色，其余（默认、换行）用功能键颜色
RETURN_ACCENT = [1, 4, 7, 9, 10]
RETURN_PLAIN = [0, 2, 3, 5, 6, 8, 11]


def pct(x):
    return {"percentage": round(x, 5)}


# ---------------------------------------------------------------- 样式构建
class Sheet:
    """一个键盘文件：根节点下平铺所有样式。"""

    def __init__(self, mode):
        self.c = COLORS[mode]
        self.d = {}

    def add(self, name, node):
        if name in self.d and self.d[name] != node:
            raise ValueError("样式重名: " + name)
        self.d[name] = node
        return name

    # --- 背景
    def bg(self, kind):
        c = self.c
        normal, hl = {
            "key": (c["key"], c["key_hl"]),
            "func": (c["func"], c["func_hl"]),
            "accent": (c["accent"], c["accent_hl"]),
        }[kind]
        node = {
            "buttonStyleType": "geometry",
            "insets": KEY_INSETS,
            "normalColor": normal,
            "highlightColor": hl,
            "cornerRadius": CORNER,
        }
        if c["shadow"]:
            node.update({"normalShadowColor": c["shadow"], "highlightShadowColor": c["shadow"],
                         "shadowRadius": 0.5, "shadowOffset": {"x": 0, "y": 1}})
        return self.add(kind + "Background", node)

    # --- 前景
    def text(self, name, text, size=FUNC_FONT, color="text", weight=None, center=None):
        node = {
            "buttonStyleType": "text",
            "text": text,
            "fontSize": size,
            "normalColor": self.c[color],
            "highlightColor": self.c[color],
        }
        if weight:
            node["fontWeight"] = weight
        if center:
            node["center"] = center
        return self.add(name, node)

    def icon(self, name, symbol, size=ICON_FONT, color="text", hl_symbol=None):
        node = {
            "buttonStyleType": "systemImage",
            "systemImageName": symbol,
            "fontSize": size,
            "normalColor": self.c[color],
            "highlightColor": self.c[color],
        }
        if hl_symbol:
            node["highlightSystemImageName"] = hl_symbol
        return self.add(name, node)

    # --- 按键
    def hint(self, name, label):
        self.add("hintBackground", {
            "buttonStyleType": "geometry",
            "normalColor": self.c["hint_bg"],
            "cornerRadius": 10,
            "borderSize": 0.5,
            "normalBorderColor": self.c["hint_border"],
        })
        fg = self.text(name + "HintForeground", label, size=30)
        return self.add(name + "Hint", {
            "size": {"width": 52, "height": 56},
            "backgroundStyle": "hintBackground",
            "foregroundStyle": fg,
        })

    def letter(self, ch, width=None, bounds=None):
        name = ch + "Button"
        node = {
            "action": {"character": ch},
            "uppercasedStateAction": {"character": ch.upper()},
            "backgroundStyle": self.bg("key"),
            "foregroundStyle": self.text(ch + "Foreground", ch, size=LETTER_FONT),
            "uppercasedStateForegroundStyle": self.text(ch + "UpperForeground", ch.upper(), size=LETTER_FONT),
            "capsLockedStateForegroundStyle": ch + "UpperForeground",
            "hintStyle": self.hint(name, ch.upper()),
        }
        if width is not None:
            node["size"] = {"width": pct(width)}
        if bounds:
            node["bounds"] = bounds
        return self.add(name, node)

    def symbol_key(self, name, label, action, width=None, kind="key", size=22):
        node = {
            "action": action,
            "backgroundStyle": self.bg(kind),
            "foregroundStyle": self.text(name + "Foreground", label, size=size),
            "hintStyle": self.hint(name, label),
        }
        if width is not None:
            node["size"] = {"width": pct(width)}
        return self.add(name, node)

    def func_key(self, name, fg, action, width=None, bounds=None, kind="func", **extra):
        node = {
            "action": action,
            "backgroundStyle": self.bg(kind),
            "foregroundStyle": fg,
        }
        if width is not None:
            node["size"] = {"width": pct(width)}
        if bounds:
            node["bounds"] = bounds
        node.update(extra)
        return self.add(name, node)

    # --- 公共部件
    def backspace(self, width=None, bounds=None):
        fg = self.icon("backspaceForeground", "delete.left", hl_symbol="delete.left.fill")
        return self.func_key("backspaceButton", fg, "backspace", width, bounds,
                             repeatAction="backspace")

    def enter(self, width):
        plain = self.icon("enterForeground", "return", size=20)
        accent = self.text("enterAccentForeground", "$returnKeyType", color="accent_text")
        self.bg("accent")
        bg_cond = [
            {"conditionKey": "$returnKeyType", "conditionValue": RETURN_PLAIN, "styleName": "funcBackground"},
            {"conditionKey": "$returnKeyType", "conditionValue": RETURN_ACCENT, "styleName": "accentBackground"},
        ]
        fg_cond = [
            {"conditionKey": "$returnKeyType", "conditionValue": RETURN_PLAIN, "styleName": plain},
            {"conditionKey": "$returnKeyType", "conditionValue": RETURN_ACCENT, "styleName": accent},
        ]
        self.add("returnKeyTypeNotification", {
            "notificationType": "returnKeyType",
            "returnKeyType": RETURN_ACCENT,
            "backgroundStyle": "accentBackground",
            "foregroundStyle": accent,
            "action": "enter",
        })
        return self.add("enterButton", {
            "action": "enter",
            "size": {"width": pct(width)},
            "backgroundStyle": bg_cond,
            "foregroundStyle": fg_cond,
            "notification": ["returnKeyTypeNotification"],
        })

    def area_background(self):
        return self.add("keyboardBackground", {
            "buttonStyleType": "geometry",
            "normalColor": self.c["keyboard_bg"],
        })

    def candidates(self):
        """横向 / 纵向候选栏，所有键盘共用。"""
        c = self.c
        bg = self.area_background()
        self.add("horizontalCandidateStyle", {
            "insets": {"left": 6, "right": 6},
            "backgroundCornerRadius": 6,
            "highlightBackgroundColor": c["candidate_hl"],
            "preferredBackgroundColor": "#00000000",
            "preferredTextColor": c["text"],
            "preferredCommentColor": c["text_dim"],
            "preferredIndexColor": "#00000000",
            "textColor": c["text"],
            "commentColor": c["text_dim"],
            "indexColor": "#00000000",              # 原生不显示序号
            "textFontSize": 20,
            "commentFontSize": 12,
            "indexFontSize": 1,
        })
        self.add("horizontalCandidates", {
            "type": "horizontalCandidates",
            "candidateStyle": "horizontalCandidateStyle",
        })
        self.add("expandButton", {
            "action": {"shortcut": "#candidatesBarStateToggle"},
            "size": {"width": 44},
            "foregroundStyle": self.icon("expandForeground", "chevron.down"),
        })
        self.add("verticalCandidateStyle", {
            "insets": {"top": 6, "bottom": 6, "left": 8, "right": 8},
            "highlightBackgroundColor": c["candidate_hl"],
            "preferredBackgroundColor": "#00000000",
            "preferredTextColor": c["text"],
            "preferredCommentColor": c["text_dim"],
            "preferredIndexColor": "#00000000",
            "textColor": c["text"],
            "commentColor": c["text_dim"],
            "indexColor": "#00000000",              # 原生不显示序号
            "textFontSize": 20,
            "commentFontSize": 12,
            "indexFontSize": 1,
        })
        self.add("verticalCandidates", {
            "type": "verticalCandidates",
            "candidateStyle": "verticalCandidateStyle",
            "insets": {"top": 6, "bottom": 6, "left": 6, "right": 6},
            "maxRows": 5,
            "maxColumns": 6,
            "separatorColor": c["separator"],
        })
        self.add("verticalLastRow", {"size": {"height": 50}})
        self.func_key("verticalPageUp", self.icon("pageUpForeground", "chevron.up"),
                      {"shortcut": "#verticalCandidatesPageUp"})
        self.func_key("verticalPageDown", self.icon("pageDownForeground", "chevron.down"),
                      {"shortcut": "#verticalCandidatesPageDown"})
        self.func_key("verticalReturn", self.icon("collapseForeground", "chevron.up.circle"),
                      {"shortcut": "#candidatesBarStateToggle"})
        self.func_key("verticalBackspace", "backspaceForeground", "backspace",
                      repeatAction="backspace")
        self.icon("backspaceForeground", "delete.left", hl_symbol="delete.left.fill")
        self.d.update({
            "horizontalCandidatesStyle": {"backgroundStyle": bg, "insets": {"left": 4, "top": 4, "bottom": 2}},
            "horizontalCandidatesLayout": [
                {"HStack": {"subviews": [{"Cell": "horizontalCandidates"}, {"Cell": "expandButton"}]}},
            ],
            "verticalCandidatesStyle": {"backgroundStyle": bg},
            "verticalCandidatesLayout": [
                {"HStack": {"subviews": [{"Cell": "verticalCandidates"}]}},
                {"HStack": {"style": "verticalLastRow", "subviews": [
                    {"Cell": "verticalPageUp"}, {"Cell": "verticalPageDown"},
                    {"Cell": "verticalReturn"}, {"Cell": "verticalBackspace"}]}},
            ],
        })

    def frame(self, toolbar_layout, keyboard_layout):
        bg = self.area_background()
        self.add("preeditForeground", {
            "buttonStyleType": "text", "fontSize": 16, "normalColor": self.c["text"],
            "textColor": self.c["text"],
        })
        self.d.update({
            "preeditHeight": PREEDIT_HEIGHT,
            "toolbarHeight": TOOLBAR_HEIGHT,
            "keyboardHeight": KEYBOARD_HEIGHT,
            "preeditStyle": {"backgroundStyle": bg, "foregroundStyle": "preeditForeground",
                             "insets": {"left": 10, "top": 3}},
            "toolbarStyle": {"backgroundStyle": bg, "insets": {"left": 6, "right": 6}},
            "toolbarLayout": toolbar_layout,
            "keyboardStyle": {"backgroundStyle": bg, "insets": KEYBOARD_INSETS},
            "keyboardLayout": keyboard_layout,
        })
        self.candidates()
        return self.d

    # --- 工具栏
    def toolbar_button(self, name, symbol, action):
        self.add("toolbarButtonBackground", {
            "buttonStyleType": "geometry",
            "insets": {"top": (TOOLBAR_HEIGHT - TOOLBAR_BTN) / 2, "bottom": (TOOLBAR_HEIGHT - TOOLBAR_BTN) / 2,
                       "left": (TOOLBAR_CELL - TOOLBAR_BTN) / 2, "right": (TOOLBAR_CELL - TOOLBAR_BTN) / 2},
            "normalColor": self.c["toolbar_btn"],
            "highlightColor": self.c["toolbar_btn_hl"],
            "cornerRadius": TOOLBAR_BTN / 2,
        })
        return self.add(name, {
            "action": action,
            "size": {"width": TOOLBAR_CELL},
            "backgroundStyle": "toolbarButtonBackground",
            "foregroundStyle": self.icon(name + "Foreground", symbol, size=19, color="text_dim"),
        })

    def toolbar_spacer(self):
        return self.add("toolbarSpacer", {"action": "none"})


# 第三行两端的功能键（Shift / 删除 / 符号 / 123）：格子占 EDGE_CELL，键帽只画 EDGE_VISUAL 宽、靠外侧，
# 多出来的部分仍可点击。所有键盘共用，保证这几个键一样宽（同微信）。
EDGE_CELL = 0.15
EDGE_VISUAL = 0.13


def edge_bounds(side):
    return {"alignment": side, "width": pct(EDGE_VISUAL / EDGE_CELL)}


def row(*cells):
    return {"HStack": {"subviews": [{"Cell": c} for c in cells]}}


# ---------------------------------------------------------------- 中文（字母）键盘
def pinyin_keyboard(mode):
    s = Sheet(mode)
    k = 0.1                                   # 一个字母键占整行宽度的比例
    side = (1 - 9 * k) / 2                    # 第二行两端多出来的半个键
    r1 = [s.letter(ch, k) for ch in ROW1]
    r2 = ([s.letter("a", k + side, {"alignment": "right", "width": pct(k / (k + side))})]
          + [s.letter(ch, k) for ch in ROW2[1:-1]]
          + [s.letter("l", k + side, {"alignment": "left", "width": pct(k / (k + side))})])

    edge = EDGE_CELL                          # 第三行 Shift / 删除
    shift = s.func_key(
        "shiftButton", s.icon("shiftForeground", "shift"), "shift", edge,
        edge_bounds("left"),
        uppercasedStateForegroundStyle=s.icon("shiftUpperForeground", "shift.fill"),
        capsLockedStateForegroundStyle=s.icon("capsLockForeground", "capslock.fill"),
    )
    r3 = [shift] + [s.letter(ch, k) for ch in ROW3] + [s.backspace(edge, edge_bounds("right"))]

    # 底行：123 / ，。 / 空格 / 中英 / 回车（比例取自微信输入法；不放 Emoji 键，用 iOS 自带的 Emoji 键盘）
    # 同微信：123 进符号键盘（数字行 + 标点），符号键盘上的「12/34」再进九宫格数字键盘
    num = s.func_key("numericButton", s.text("numericForeground", "123"),
                     {"keyboardType": "symbolic"}, 0.15)
    punct = s.add("punctButton", {
        "action": {"character": ","},
        "swipeUpAction": {"character": "."},          # 唯一保留的划动：逗号键上划出句号，和微信一样
        "size": {"width": pct(0.1)},
        "backgroundStyle": s.bg("key"),
        "foregroundStyle": [
            s.text("punctForeground", "，", size=20, center={"x": 0.5, "y": 0.6}),
            s.text("punctUpForeground", "。", size=12, color="text_dim", center={"x": 0.5, "y": 0.25}),
        ],
        "hintStyle": s.hint("punctButton", "，"),
    })
    space = s.add("spaceButton", {
        "action": "space",
        "backgroundStyle": s.bg("key"),
        "foregroundStyle": s.text("spaceForeground", "$rimeSchemaName", size=13, color="text_dim"),
        "notification": [s.add("schemaChangedNotification", {
            "notificationType": "rime",
            "rimeNotificationType": "schemaChanged",
            "backgroundStyle": "keyBackground",
            "foregroundStyle": "spaceForeground",
            "action": "space",
        })],
    })

    # 中英键：大字是当前状态，小字是另一种
    zh_big = s.text("zhBigForeground", "中", size=17, center={"x": 0.38, "y": 0.42})
    en_small = s.text("enSmallForeground", "英", size=11, color="text_dim", center={"x": 0.66, "y": 0.64})
    zh_small = s.text("zhSmallForeground", "中", size=11, color="text_dim", center={"x": 0.34, "y": 0.36})
    en_big = s.text("enBigForeground", "英", size=17, center={"x": 0.62, "y": 0.58})
    zh_state = [zh_big, en_small]
    en_state = [zh_small, en_big]
    ascii_action = {"shortcut": "#中英切换"}
    for value, fg in ((False, zh_state), (True, en_state)):
        s.add("ascii%sNotification" % ("On" if value else "Off"), {
            "notificationType": "rime",
            "rimeNotificationType": "optionChanged",
            "rimeOptionName": "ascii_mode",
            "rimeOptionValue": value,
            "backgroundStyle": "keyBackground",
            "foregroundStyle": fg,
            "action": ascii_action,
        })
    lang = s.add("asciiModeButton", {
        "action": ascii_action,
        "size": {"width": pct(0.11)},
        "backgroundStyle": s.bg("key"),
        "foregroundStyle": [
            {"conditionKey": "rime$ascii_mode", "conditionValue": False, "styleName": zh_state},
            {"conditionKey": "rime$ascii_mode", "conditionValue": True, "styleName": en_state},
        ],
        "notification": ["asciiOffNotification", "asciiOnNotification"],
    })
    enter = s.enter(0.22)

    toolbar = [row(
        s.toolbar_button("schemaButton", "keyboard", {"shortcut": "#方案切换"}),
        s.toolbar_spacer(),
        s.toolbar_button("phraseButton", "text.bubble", {"shortcut": "#showPhraseView"}),
        s.toolbar_button("pasteboardButton", "doc.on.clipboard", {"shortcut": "#showPasteboardView"}),
        s.toolbar_button("dismissButton", "chevron.down", "dismissKeyboard"),
    )]
    return s.frame(toolbar, [row(*r1), row(*r2), row(*r3),
                             row(num, punct, space, lang, enter)])


# ---------------------------------------------------------------- 符号栏（数字 / 符号键盘顶部）
def symbol_toolbar(s, symbols):
    cells = []
    for i, sym in enumerate(symbols):
        name = "barSymbol%d" % i
        cells.append(s.add(name, {
            "action": {"symbol": sym},
            "foregroundStyle": s.text(name + "Foreground", sym, size=18),
        }))
    cells.append(s.add("barClose", {
        "action": "returnPrimaryKeyboard",
        "size": {"width": 44},
        "foregroundStyle": s.icon("barCloseForeground", "xmark", size=17, color="text_dim"),
    }))
    return [row(*cells)]


def return_key(s, width):
    """返回中文键盘，强调色。"""
    return s.func_key("returnButton", s.icon("returnForeground", "arrow.left", color="accent_text"),
                      "returnPrimaryKeyboard", width, kind="accent")


# ---------------------------------------------------------------- 数字键盘
def numeric_keyboard(mode):
    """九宫格数字键盘，按列排：左列符号，中间 3×4 数字，右列删除 / 空格 / 换行（换行占两格高，同 iOS 数字键盘）。"""
    s = Sheet(mode)
    side = 0.17
    third = 1 / 3    # 中间列里每个键占这一行的 1/3

    def digit(d):
        return s.symbol_key("digit%sButton" % d, d, {"symbol": d}, third, size=24)

    def side_sym(name, label):
        return s.symbol_key(name, label, {"symbol": label}, kind="func", size=20)

    s.add("sideColumn", {"size": {"width": pct(side)}})
    s.add("middleColumn", {"size": {"width": pct(1 - 2 * side)}})
    symbols = s.func_key("symbolicButton", s.text("symbolicForeground", "符号"),
                         {"keyboardType": "symbolic"}, third, kind="key")
    space = s.func_key("spaceButton", s.text("spaceForeground", "空格"), "space")
    enter = s.enter(side)
    s.d[enter]["size"] = {"height": pct(0.5)}   # 在列里取高度：占两格
    backspace = s.backspace()

    def column(style, cells):
        return {"VStack": {"style": style, "subviews": cells}}

    layout = [{"HStack": {"subviews": [
        column("sideColumn", [{"Cell": c} for c in (
            side_sym("atButton", "@"), side_sym("percentButton", "%"),
            side_sym("minusButton", "-"), return_key(s, None))]),
        column("middleColumn", [
            row(digit("1"), digit("2"), digit("3")),
            row(digit("4"), digit("5"), digit("6")),
            row(digit("7"), digit("8"), digit("9")),
            row(symbols, digit("0"), s.symbol_key("dotButton", ".", {"symbol": "."}, third, size=24)),
        ]),
        column("sideColumn", [{"Cell": c} for c in (backspace, space, enter)]),
    ]}}]
    toolbar = symbol_toolbar(s, ["。", "？", "！", "…", "（", "）", ".", "-"])
    return s.frame(toolbar, layout)


# ---------------------------------------------------------------- 符号键盘
# 微信输入法的符号键盘分两层：
# - 主符号页（symbolic）：数字 + 常用中文标点，「符号」键进入更多符号；
# - 更多符号：底部是一排分类，每个分类在这里是一个自定义键盘，点分类就切过去。
#   第一个分类（时钟图标）照微信截图；其余分类的内容是自拟的常用符号，以后可按微信截图对齐。
SYMBOL_BAR = ["（", "）", ".", "@", "。", "？", "！", "-"]   # 符号页顶部的快捷符号

# (键盘类型名, 分类栏上的标签, 是否图标, 符号)。符号按 10 + 10 + 7 排三行，第三行两端是 123 和删除。
SYMBOL_PAGES = [
    ("symbolCommon", "clock", True,
     ["_", "—", "；", "|", "%", "+", "-", "×", "÷", "=",
      "【", "】", "{", "}", "《", "》", "#", "$", "&", "·",
      "「", "」", "<", ">", "^", "*"]),
    ("symbolZh", "中", False,
     ["，", "。", "、", "；", "：", "？", "！", "…", "—", "·",
      "“", "”", "‘", "’", "（", "）", "《", "》", "〈", "〉",
      "「", "」", "『", "』", "【", "】", "～"]),
    ("symbolEn", "英", False,
     [",", ".", ";", ":", "?", "!", "'", "\"", "`", "~",
      "(", ")", "[", "]", "{", "}", "<", ">", "/", "\\",
      "|", "_", "+", "=", "*", "&", "^"]),
    ("symbolBracket", "【】", False,
     ["（", "）", "【", "】", "《", "》", "〈", "〉", "「", "」",
      "『", "』", "〔", "〕", "［", "］", "｛", "｝", "〖", "〗",
      "(", ")", "[", "]", "{", "}", "«"]),
    ("symbolCurrency", "$¥", False,
     ["￥", "¥", "$", "€", "£", "¢", "₩", "₽", "₹", "฿",
      "₫", "₱", "₺", "₴", "₦", "₪", "₡", "₲", "₵", "₸",
      "元", "角", "分", "%", "‰", "‱"]),
    ("symbolMath", "+÷", False,
     ["+", "−", "×", "÷", "=", "≠", "≈", "±", "<", ">",
      "≤", "≥", "√", "∞", "°", "∑", "∫", "π", "∈", "∉",
      "∩", "∪", "⊂", "⊃", "∠", "⊥", "∴"]),
    ("symbolNumber", "①", False,
     ["①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩",
      "Ⅰ", "Ⅱ", "Ⅲ", "Ⅳ", "Ⅴ", "Ⅵ", "Ⅶ", "Ⅷ", "Ⅸ", "Ⅹ",
      "⑴", "⑵", "⑶", "⑷", "⑸", "⑹", "⑺"]),
]


def symbolic_keyboard(mode):
    """主符号页，照微信截图。"""
    s = Sheet(mode)
    k = 0.1

    def sym_row(prefix, chars, width):
        return [s.symbol_key("%s%dButton" % (prefix, i), ch, {"symbol": ch}, width)
                for i, ch in enumerate(chars)]

    r1 = sym_row("num", "1234567890", k)
    r2 = sym_row("sym", ["-", "/", "：", "～", "（", "）", "…", "@", "“", "”"], k)
    edge = EDGE_CELL
    more = s.func_key("moreSymbolsButton", s.text("moreSymbolsForeground", "符号"),
                      {"keyboardType": SYMBOL_PAGES[0][0]}, edge, edge_bounds("left"))
    r3 = ([more] + sym_row("punct", ["。", "，", "、", "？", "！", "."], (1 - 2 * edge) / 6)
          + [s.backspace(edge, edge_bounds("right"))])
    # 「12 / 34」上下两行（微信的九宫格数字键盘图标），用两层文字叠出来
    num = s.func_key("numericButton", [
        s.text("numericTopForeground", "12", size=13, center={"x": 0.5, "y": 0.34}),
        s.text("numericBottomForeground", "34", size=13, center={"x": 0.5, "y": 0.66}),
    ], {"keyboardType": "numeric"}, 0.1, kind="key")
    space = s.add("spaceButton", {
        "action": "space",
        "backgroundStyle": s.bg("key"),
        "foregroundStyle": s.text("spaceForeground", "空格", color="text_dim"),
    })
    layout = [row(*r1), row(*r2), row(*r3), row(return_key(s, 0.15), num, space, s.enter(0.22))]
    return s.frame(symbol_toolbar(s, SYMBOL_BAR), layout)


def symbol_page(mode, index):
    """更多符号里的一个分类页。"""
    s = Sheet(mode)
    _, _, _, chars = SYMBOL_PAGES[index]
    chars = (list(chars) + [""] * 27)[:27]

    def key(i, ch, width):
        if not ch:
            return s.add("emptyCell%d" % i, {"action": "none", "size": {"width": pct(width)}})
        return s.symbol_key("pageSym%dButton" % i, ch, {"symbol": ch}, width)

    k = 0.1
    r1 = [key(i, ch, k) for i, ch in enumerate(chars[:10])]
    r2 = [key(10 + i, ch, k) for i, ch in enumerate(chars[10:20])]
    edge = EDGE_CELL
    num = s.func_key("symbolicButton", s.text("symbolicForeground", "123"),
                     {"keyboardType": "symbolic"}, edge, edge_bounds("left"))
    # 第三行按实际符号个数均分 123 和删除键之间的宽度（同微信：6 个符号时每个键加宽，不留空格）
    row3 = [ch for ch in chars[20:27] if ch]
    w3 = (1 - 2 * edge) / max(len(row3), 1)
    r3 = ([num] + [key(20 + i, ch, w3) for i, ch in enumerate(row3)]
          + [s.backspace(edge, edge_bounds("right"))])

    # 分类栏：当前分类加灰色圆底
    s.add("tabSelectedBackground", {
        "buttonStyleType": "geometry",
        "insets": {"top": 7, "bottom": 7, "left": 2, "right": 2},
        "normalColor": s.c["toolbar_btn_hl"],
        "highlightColor": s.c["toolbar_btn_hl"],
        "cornerRadius": 17,
    })
    s.add("tabBackground", {
        "buttonStyleType": "geometry",
        "normalColor": "#FFFFFF03",
        "highlightColor": s.c["toolbar_btn_hl"],
        "insets": {"top": 7, "bottom": 7, "left": 2, "right": 2},
        "cornerRadius": 17,
    })
    # 每个分类都写明宽度：不写宽度时元书没有把剩余空间分满，右侧会留空隙
    back = 0.15
    tab_width = (1 - back) / len(SYMBOL_PAGES)
    tabs = [return_key(s, back)]
    for i, (kb, label, is_icon, _) in enumerate(SYMBOL_PAGES):
        fg = (s.icon("tab%dForeground" % i, label, size=19, color="text_dim") if is_icon
              else s.text("tab%dForeground" % i, label, size=17 if len(label) == 1 else 13, color="text_dim"))
        tabs.append(s.add("tab%dButton" % i, {
            "action": {"keyboardType": kb},
            "size": {"width": pct(tab_width)},
            "backgroundStyle": "tabSelectedBackground" if i == index else "tabBackground",
            "foregroundStyle": fg,
        }))
    layout = [row(*r1), row(*r2), row(*r3), row(*tabs)]
    return s.frame(symbol_toolbar(s, SYMBOL_BAR), layout)


# ---------------------------------------------------------------- 输出
def to_yaml(obj, indent=0):
    """足够用的 YAML 输出：字符串一律加双引号（JSON 字符串也是合法 YAML）。"""
    pad = "  " * indent
    if isinstance(obj, dict):
        if not obj:
            return "{}"
        lines = []
        for k, v in obj.items():
            key = json.dumps(k, ensure_ascii=False) if not k.isidentifier() else k
            inline_list = isinstance(v, list) and all(not isinstance(x, (dict, list)) for x in v)
            if isinstance(v, (dict, list)) and v and not inline_list:
                lines.append("%s%s:\n%s" % (pad, key, to_yaml(v, indent + 1)))
            else:
                lines.append("%s%s: %s" % (pad, key, to_yaml(v, 0)))
        return "\n".join(lines)
    if isinstance(obj, list):
        if not obj:
            return "[]"
        if all(not isinstance(x, (dict, list)) for x in obj):
            return "[" + ", ".join(to_yaml(x) for x in obj) + "]"
        lines = []
        for v in obj:
            body = to_yaml(v, indent + 1).lstrip()
            lines.append("%s- %s" % (pad, body))
        return "\n".join(lines)
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if isinstance(obj, float):
        return ("%g" % obj)
    if isinstance(obj, int):
        return str(obj)
    return json.dumps(obj, ensure_ascii=False)


KEYBOARDS = {
    "pinyin": ("pinyinPortrait", pinyin_keyboard),
    "numeric": ("numericPortrait", numeric_keyboard),
    "symbolic": ("symbolicPortrait", symbolic_keyboard),
}
# 更多符号的分类页是自定义键盘类型，在 config.yaml 里按名字声明
for _i, (_kb, _, _, _) in enumerate(SYMBOL_PAGES):
    KEYBOARDS[_kb] = (_kb + "Portrait", lambda mode, i=_i: symbol_page(mode, i))

README = """MyRime：仿微信输入法布局、iOS 原生外观的简洁皮肤，配合雾凇拼音（自然码双拼）使用。

- 字母键没有划动功能，避免误触
- 底行：123 / 逗号（上划句号）/ 空格 / 中英 / 回车（不做 Emoji 面板，用 iOS 自带的 Emoji 键盘）
- 中英键切换 RIME 的 ascii_mode
- 符号键盘的「符号」键进入更多符号，底部一排分类（常用 / 中 / 英 / 括号 / 货币 / 数学 / 序号）
- 工具栏：方案切换 / 常用语 / 剪贴板 / 收起键盘

此皮肤由 MyRimeConfig 仓库的 yuanshu-skin/build.py 生成，请勿直接修改 YAML。
"""


# ---------------------------------------------------------------- 检查
# 生成后自动检查，规则来自实际踩过的坑；有问题时 build() 报错退出，不写出半成品
STYLE_REF_KEYS = ("backgroundStyle", "foregroundStyle", "uppercasedStateForegroundStyle",
                  "capsLockedStateForegroundStyle", "swipeUpForegroundStyle", "swipeDownForegroundStyle",
                  "hintStyle", "hintSymbolsStyle", "notification", "candidateStyle", "cellStyle")


def _style_refs(value):
    """样式引用可以是字符串、字符串数组或条件样式数组。"""
    if isinstance(value, str):
        return [value]
    out = []
    for item in value or []:
        if isinstance(item, dict):
            name = item.get("styleName")
            out += name if isinstance(name, list) else [name]
        else:
            out.append(item)
    return out


def check_sheet(sheet, keyboard_types):
    problems = []

    def size_of(node, key):
        if "Cell" in node:
            return sheet.get(node["Cell"], {}).get("size", {}).get(key)
        stack = node.get("HStack") or node.get("VStack")
        style = stack.get("style")
        return sheet.get(style, {}).get("size", {}).get(key) if style else None

    def walk(nodes, where, parent, check_sizes):
        kinds = {next(iter(n)) for n in nodes}
        if len(kinds) > 1:
            problems.append("%s：同级混用了 %s" % (where, "、".join(sorted(kinds))))
        for n in nodes:
            if "Cell" in n:
                if parent is None:
                    problems.append("%s：Cell %s 直接放在根上" % (where, n["Cell"]))
                if n["Cell"] not in sheet:
                    problems.append("%s：Cell %s 未定义" % (where, n["Cell"]))
            for kind in ("HStack", "VStack"):
                if kind in n:
                    style = n[kind].get("style")
                    if style and style not in sheet:
                        problems.append("%s：style %s 未定义" % (where, style))
                    walk(n[kind]["subviews"], where, kind, check_sizes)
        # 同一行（HStack 的子节点）看宽度，同一列（VStack 的子节点）看高度
        if check_sizes and parent:
            key = "width" if parent == "HStack" else "height"
            sizes = [size_of(n, key) for n in nodes]
            fixed = sum(v["percentage"] for v in sizes if isinstance(v, dict))
            auto = sum(1 for v in sizes if v is None)
            names = [n.get("Cell", "…") for n in nodes]
            if auto == 0 and abs(fixed - 1) > 1e-3:
                problems.append("%s：%s 的%s合计 %.4f，不等于 1" % (where, names, "宽度" if key == "width" else "高度", fixed))
            if auto and fixed >= 1 - 1e-3:
                problems.append("%s：%s 固定尺寸已占满，自动尺寸的格子没有空间" % (where, names))

    for area in ("toolbarLayout", "keyboardLayout", "horizontalCandidatesLayout", "verticalCandidatesLayout"):
        walk(sheet.get(area) or [], area, None, area == "keyboardLayout")

    for name, node in sheet.items():
        if not isinstance(node, dict):
            continue
        for key in STYLE_REF_KEYS:
            for ref in _style_refs(node.get(key)):
                if ref not in sheet:
                    problems.append("%s.%s 引用了未定义的 %s" % (name, key, ref))
        for key in ("action", "swipeUpAction", "swipeDownAction", "uppercasedStateAction"):
            action = node.get(key)
            if isinstance(action, dict) and "keyboardType" in action and action["keyboardType"] not in keyboard_types:
                problems.append("%s.%s 切到未声明的键盘 %s" % (name, key, action["keyboardType"]))
    return problems


def config_yaml():
    cfg = {"name": SKIN_NAME, "author": "MyRimeConfig"}
    for kind, (fname, _) in KEYBOARDS.items():
        # 横屏、iPad 暂时沿用竖屏文件，之后单独做
        cfg[kind] = {
            "iPhone": {"portrait": fname, "landscape": fname},
            "iPad": {"portrait": fname, "landscape": fname, "floating": fname},
        }
    cfg["alphabetic"] = cfg["pinyin"]
    return to_yaml(cfg) + "\n"


def write_demo(path):
    try:
        from demo import render  # 同目录的 demo.py，需要 Pillow
        render(path, pinyin_keyboard("light"), pinyin_keyboard("dark"), COLORS)
        return
    except ImportError:
        pass
    # 没有 Pillow：写一张 2x1 的纯色 PNG 占位
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    raw = b"\x00" + bytes.fromhex(COLORS["light"]["keyboard_bg"][1:]) + bytes.fromhex(COLORS["dark"]["keyboard_bg"][1:])
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 1, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)


def build():
    skin_dir = os.path.join(OUT_ROOT, SKIN_NAME)
    shutil.rmtree(skin_dir, ignore_errors=True)
    keyboard_types = set(KEYBOARDS) | {"alphabetic"}
    sheets, problems = {}, []
    for mode in ("light", "dark"):
        for kind, (fname, fn) in KEYBOARDS.items():
            sheet = fn(mode)
            sheets[(mode, fname)] = sheet
            problems += ["%s/%s：%s" % (mode, fname, p) for p in check_sheet(sheet, keyboard_types)]
    if problems:
        raise SystemExit("!!! 皮肤检查没通过：\n" + "\n".join("    " + p for p in problems))
    for mode in ("light", "dark"):
        os.makedirs(os.path.join(skin_dir, mode))
    for (mode, fname), sheet in sheets.items():
        with open(os.path.join(skin_dir, mode, fname + ".yaml"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(to_yaml(sheet) + "\n")
    with open(os.path.join(skin_dir, "config.yaml"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(config_yaml())
    with open(os.path.join(skin_dir, "README.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(README)
    write_demo(os.path.join(skin_dir, "demo.png"))

    cskin = os.path.join(OUT_ROOT, SKIN_NAME + ".cskin")
    with zipfile.ZipFile(cskin, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(skin_dir):
            for f in sorted(files):
                full = os.path.join(root, f)
                z.write(full, os.path.relpath(full, OUT_ROOT))
    return skin_dir, cskin


if __name__ == "__main__":
    import sys
    sys.path.insert(0, HERE)
    d, c = build()
    print("已生成 %s" % d)
    print("已生成 %s" % c)
