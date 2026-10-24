"""產生第 6 週團隊繳交的「系統需求設計規格書（SRS／SDD）」PDF。

用法：python tools/make_srs_sdd.py
輸出：docs/03_週報/第6週_系統需求設計規格書.pdf

版面依老師提供的 SRS／SDD 範例：封面、目錄、簡介、系統、軟體設計、專案管理、
Glossary、References、Appendix。附錄中的執行輸出與測試結果、版本控管的 git log
都是產生 PDF 時實際執行取得的。成員姓名請修改下方 MEMBERS 後重新執行。
需要 reportlab，以及 Windows 的標楷體（kaiu.ttf）與微軟正黑體（msjh.ttc、msjhbd.ttc）。
"""
from __future__ import annotations

import html
import subprocess
import sys
from pathlib import Path

from reportlab.graphics.shapes import Drawing, Ellipse, Line, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, KeepTogether, NextPageTemplate, PageBreak, PageTemplate,
    Paragraph, Spacer, Table, TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "03_週報" / "第6週_系統需求設計規格書.pdf"
PHOTO = ROOT / "docs" / "05_會議" / "第6週_團隊討論照片.jpg"
DATE = "2026/10/16"

# 成員資料（角色依序為 A～E）
MEMBERS = [
    ("A", "張庭瑄", "111590042", "t111590042@ntut.org.tw"),
    ("B", "黃韻玲", "115590045", "t115590045@ntut.org.tw"),
    ("C", "張芷芸", "115590035", "t115590035@ntut.org.tw"),
    ("D", "何子宏", "113540031", "t113540031@ntut.org.tw"),
    ("E", "林尚威", "114540049", "t114540049@ntut.org.tw"),
]

FONTS = {
    "KAI": Path(r"C:\Windows\Fonts\kaiu.ttf"),
    "JH": Path(r"C:\Windows\Fonts\msjh.ttc"),
    "JHB": Path(r"C:\Windows\Fonts\msjhbd.ttc"),
}
for name, path in FONTS.items():
    if not path.exists():
        raise SystemExit(f"找不到字型：{path}")
    pdfmetrics.registerFont(TTFont(name, str(path), subfontIndex=0) if path.suffix == ".ttc" else TTFont(name, str(path)))

GREY_BG = colors.HexColor("#D9D9D9")
BLUE_BG = colors.HexColor("#DCE6F2")
LINE = colors.HexColor("#4472C4")
DARK = colors.HexColor("#1E1E1E")

S = {
    "cover_title": ParagraphStyle("ct", fontName="KAI", fontSize=22, leading=30, alignment=1),
    "cover_sub": ParagraphStyle("cs", fontName="KAI", fontSize=20, leading=28, alignment=1),
    "cover_en": ParagraphStyle("ce", fontName="JHB", fontSize=14, leading=22, alignment=1),
    "cover_member": ParagraphStyle("cm", fontName="KAI", fontSize=12, leading=18, alignment=1),
    "toc_title": ParagraphStyle("tt", fontName="JHB", fontSize=15, leading=22, spaceAfter=12),
    "h1": ParagraphStyle("h1", fontName="JHB", fontSize=15, leading=22, spaceBefore=6, spaceAfter=10, keepWithNext=1),
    "h2": ParagraphStyle("h2", fontName="JHB", fontSize=12, leading=18, spaceBefore=8, spaceAfter=4, keepWithNext=1),
    "h3": ParagraphStyle("h3", fontName="KAI", fontSize=11.5, leading=17, spaceBefore=6, spaceAfter=3, keepWithNext=1),
    "h4": ParagraphStyle("h4", fontName="JHB", fontSize=11, leading=17, spaceBefore=8, spaceAfter=3, keepWithNext=1),
    "label": ParagraphStyle("label", fontName="KAI", fontSize=11.5, leading=20, spaceAfter=4, keepWithNext=1, wordWrap="CJK"),
    "body": ParagraphStyle("body", fontName="KAI", fontSize=11.5, leading=20, spaceAfter=4, wordWrap="CJK"),
    "item": ParagraphStyle("item", fontName="KAI", fontSize=11.5, leading=19, leftIndent=14, firstLineIndent=-14, wordWrap="CJK"),
    "cell": ParagraphStyle("cell", fontName="KAI", fontSize=10, leading=14, wordWrap="CJK"),
    "caption": ParagraphStyle("cap", fontName="KAI", fontSize=11, leading=16, alignment=1, spaceBefore=4, spaceAfter=10),
    "code": ParagraphStyle("code", fontName="JH", fontSize=8.6, leading=12.5, wordWrap="CJK"),
    "term": ParagraphStyle("term", fontName="JH", fontSize=8.2, leading=11.5, textColor=colors.HexColor("#E6E6E6"), wordWrap="CJK"),
}
FRAME_W = A4[0] - 2 * 25 * mm


# ---------- 小工具 ----------

def esc(text: str) -> str:
    return html.escape(text, quote=False)


def P(text: str, style: str = "body") -> Paragraph:
    return Paragraph(text, S[style])


def items(lines: list[str]) -> list[Paragraph]:
    return [P(esc(line), "item") for line in lines]


def table(rows: list[list[str]], widths: list[float], header: bool = True) -> Table:
    data = [[Paragraph(esc(c).replace("\n", "<br/>"), S["cell"]) for c in row] for row in rows]
    total = sum(widths)
    t = Table(data, colWidths=[FRAME_W * w / total for w in widths], repeatRows=1 if header else 0)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.6, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), GREY_BG))
    t.setStyle(TableStyle(style))
    return t


def code_block(text: str) -> Table:
    lines = [esc(line).replace(" ", "&nbsp;") or "&nbsp;" for line in text.strip("\n").splitlines()]
    t = Table([[Paragraph("<br/>".join(lines), S["code"])]], colWidths=[FRAME_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F2F2F2")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#BFBFBF")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def terminal_block(text: str) -> Table:
    rows = []
    for line in text.rstrip().splitlines():
        safe = esc(line).replace(" ", "&nbsp;") or "&nbsp;"
        if line.startswith("commit "):
            safe = f'<font color="#E5C07B">{safe}</font>'
        elif line.startswith("$"):
            safe = f'<font color="#98C379">{safe}</font>'
        rows.append([Paragraph(safe, S["term"])])
    t = Table(rows, colWidths=[FRAME_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DARK),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 0.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 0.5),
        ("TOPPADDING", (0, 0), (-1, 0), 6), ("BOTTOMPADDING", (0, -1), (-1, -1), 6),
    ]))
    return t


def run(cmd: list[str]) -> str:
    python = ROOT / ".venv" / "Scripts" / "python.exe"
    exe = str(python) if python.exists() else sys.executable
    env = {"PYTHONIOENCODING": "utf-8", **__import__("os").environ}
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run([exe, *cmd], cwd=ROOT, capture_output=True, encoding="utf-8", env=env)
    return (result.stdout + result.stderr).strip()


def git_log() -> str:
    result = subprocess.run(
        ["git", "-c", "core.quotepath=false", "log",
         "--format=commit %H%nAuthor: %an%nDate:   %ad%n%n    %s%n", "--date=format:%a %b %d %H:%M:%S %Y %z"],
        cwd=ROOT, capture_output=True, encoding="utf-8",
    )
    return "$ git log\n" + result.stdout.strip()


# ---------- 圖 ----------

def _text(d: Drawing, x: float, y: float, s: str, size: float = 8.5, anchor: str = "middle", font: str = "JH") -> None:
    d.add(String(x, y, s, fontName=font, fontSize=size, textAnchor=anchor))


def _actor(d: Drawing, x: float, y: float, label: str) -> None:
    d.add(Ellipse(x, y + 22, 5, 5, fillColor=colors.white, strokeColor=colors.black))
    d.add(Line(x, y + 17, x, y + 4))
    d.add(Line(x - 8, y + 12, x + 8, y + 12))
    d.add(Line(x, y + 4, x - 6, y - 6))
    d.add(Line(x, y + 4, x + 6, y - 6))
    _text(d, x, y - 17, label, 8)


def _uc(d: Drawing, x: float, y: float, label: str, w: float = 80, h: float = 24) -> None:
    d.add(Ellipse(x, y, w / 2, h / 2, fillColor=colors.white, strokeColor=colors.black, strokeWidth=0.8))
    _text(d, x, y - 3, label, 8)


def _arrow(d: Drawing, x1, y1, x2, y2, dashed=False, color=LINE, head=True) -> None:
    d.add(Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=0.8, strokeDashArray=[3, 2] if dashed else None))
    if head:
        import math
        a = math.atan2(y2 - y1, x2 - x1)
        p1 = (x2 - 6 * math.cos(a - 0.4), y2 - 6 * math.sin(a - 0.4))
        p2 = (x2 - 6 * math.cos(a + 0.4), y2 - 6 * math.sin(a + 0.4))
        d.add(Polygon([x2, y2, *p1, *p2], fillColor=color, strokeColor=color, strokeWidth=0.5))


def use_case_diagram() -> Drawing:
    d = Drawing(FRAME_W, 300)
    for x0, title in ((52, "課程管理（Course Management）"), (236, "學生與教室管理（Student／Classroom）")):
        d.add(Rect(x0, 8, 176, 284, rx=14, ry=14, fillColor=BLUE_BG, strokeColor=colors.HexColor("#1F3864")))
        _text(d, x0 + 88, 278, title, 7.5, font="JHB")
    # 課程管理：左欄基本用例、右欄 include
    base_l = {"新增課程": 245, "修改課程": 205, "刪除課程": 165, "取消課程": 125, "查詢課程": 72}
    for name, y in base_l.items():
        _uc(d, 96, y, name, 78)
    _uc(d, 186, 225, "驗證課程資料", 78)
    _uc(d, 186, 145, "刪除限制檢查", 78)
    for src in ("新增課程", "修改課程"):
        _arrow(d, 135, base_l[src], 150, 225 + (6 if src == "新增課程" else -6), dashed=True, color=colors.black)
    _arrow(d, 135, base_l["刪除課程"], 148, 147, dashed=True, color=colors.black)
    _text(d, 160, 196, "«include»", 6.5)
    _text(d, 158, 170, "«include»", 6.5)
    _text(d, 96, 102, "（先退選再刪除）", 6.5)
    # 學生與教室：右欄基本用例、左欄 include
    base_r = {"新增學生": 245, "修改學生": 205, "刪除學生": 165, "查詢學生": 125, "新增教室": 72, "查詢教室": 34}
    for name, y in base_r.items():
        _uc(d, 368, y, name, 78)
    _uc(d, 278, 225, "驗證學生資料", 78)
    _uc(d, 278, 72, "驗證教室資料", 78)
    for src in ("新增學生", "修改學生"):
        _arrow(d, 329, base_r[src], 316, 225 + (6 if src == "新增學生" else -6), dashed=True, color=colors.black)
    _arrow(d, 329, base_r["新增教室"], 317, 72, dashed=True, color=colors.black)
    _text(d, 306, 200, "«include»", 6.5)
    _text(d, 323, 84, "«include»", 6.5)
    # 參與者
    _actor(d, 20, 175, "教務助理")
    _actor(d, 20, 50, "學生")
    _actor(d, FRAME_W - 20, 175, "教務助理")
    for y in base_l.values():
        _arrow(d, 30, 187, 57, y)
    _arrow(d, 30, 60, 57, base_l["查詢課程"])
    for y in base_r.values():
        _arrow(d, FRAME_W - 30, 187, 407, y)
    return d


def _box(d, cx, cy, w, h, title, sub="", fill=colors.HexColor("#FFE699"), dashed=False):
    d.add(Rect(cx - w / 2, cy - h / 2, w, h, rx=6, ry=6, fillColor=fill, strokeColor=colors.black,
               strokeWidth=0.8, strokeDashArray=[4, 2] if dashed else None))
    if sub:
        _text(d, cx, cy + 2, title, 8.5, font="JHB")
        _text(d, cx, cy - 10, sub, 7.5)
    else:
        _text(d, cx, cy - 3, title, 8.5, font="JHB")


def architecture_diagram() -> Drawing:
    d = Drawing(FRAME_W, 290)
    d.add(Rect(70, 6, 260, 278, rx=18, ry=18, fillColor=colors.HexColor("#FBE4D5"), strokeColor=colors.HexColor("#C55A11")))
    _text(d, 200, 272, "campus_planner 核心（可獨立測試的純函式）", 7.5, font="JHB")
    _actor(d, 25, 228, "使用者")
    _box(d, 200, 238, 170, 34, "命令列介面 CLI", "main.py", colors.HexColor("#5B9BD5"))
    _box(d, 200, 178, 170, 34, "F1 資料管理", "data_manager.py（SchoolCatalog）", colors.HexColor("#FFD966"))
    _box(d, 135, 118, 110, 34, "資料驗證", "validation.py", colors.HexColor("#A9D18E"))
    _box(d, 265, 118, 110, 34, "資料模型", "models.py", colors.HexColor("#A9D18E"))
    _box(d, 200, 52, 170, 34, "資料存取", "data_store.py（JSON 讀寫）", colors.HexColor("#FFD966"))
    # JSON 檔（圓柱）
    cx, cy = 395, 52
    d.add(Rect(cx - 32, cy - 20, 64, 36, fillColor=colors.HexColor("#C9C9F0"), strokeColor=colors.black, strokeWidth=0.8))
    d.add(Ellipse(cx, cy + 16, 32, 6, fillColor=colors.HexColor("#DADAF7"), strokeColor=colors.black, strokeWidth=0.8))
    d.add(Ellipse(cx, cy - 20, 32, 6, fillColor=colors.HexColor("#C9C9F0"), strokeColor=colors.black, strokeWidth=0.8))
    _text(d, cx, cy - 2, "JSON 資料檔", 7.5, font="JHB")
    _text(d, cx, cy - 13, "data/*.json", 6.5)
    # 後續模組
    _box(d, 395, 178, 100, 40, "F2～F11 後續模組", "C、D、E 依週次加入", colors.HexColor("#F4B183"), dashed=True)
    _box(d, 395, 118, 100, 34, "課表雛形（F3）", "timetable.py", colors.HexColor("#F4B183"), dashed=True)
    # 連線
    _arrow(d, 38, 238, 113, 238)
    _arrow(d, 200, 221, 200, 196)
    _arrow(d, 160, 161, 140, 136)
    _arrow(d, 240, 161, 260, 136)
    _arrow(d, 200, 161, 200, 70)
    _arrow(d, 286, 52, 361, 52)
    _arrow(d, 344, 178, 287, 178, dashed=True)
    _arrow(d, 345, 118, 321, 118, dashed=True)
    return d


def wbs_diagram() -> Drawing:
    d = Drawing(FRAME_W, 250)
    root_y = 228
    _box(d, FRAME_W / 2, root_y, 190, 24, "F1 課程與學生資料管理（Iteration 1）", "", BLUE_BG)
    branches = [
        ("需求分析", ["F1 細部規格 R1～R11", "Use Case 描述", "驗收條件對照"]),
        ("功能設計", ["資料格式", "函式介面", "系統架構圖", "提交分工"]),
        ("功能實作", ["課程管理", "學生管理", "教室管理", "JSON 載入", "CLI 整合 main.py"]),
        ("功能測試", ["範例資料 20／15／5", "單元測試 49 項", "Code Review", "Iteration Review"]),
    ]
    col_w = FRAME_W / 4
    d.add(Line(col_w / 2, 196, FRAME_W - col_w / 2, 196))
    d.add(Line(FRAME_W / 2, root_y - 12, FRAME_W / 2, 196))
    for i, (title, children) in enumerate(branches):
        cx = col_w * i + col_w / 2
        d.add(Line(cx, 196, cx, 186))
        _box(d, cx, 174, 90, 22, title, "", BLUE_BG)
        x_line = cx - 40
        y = 140
        d.add(Line(x_line, 163, x_line, y - 30 * (len(children) - 1)))
        for child in children:
            d.add(Line(x_line, y, x_line + 8, y))
            _box(d, cx + 8, y, 88, 20, child, "", BLUE_BG)
            y -= 30
    return d


# ---------- 內容 ----------

def cover() -> list:
    story = [Spacer(1, 70), P("校園選課與課表規劃系統", "cover_title"), Spacer(1, 26),
             P("系統需求設計規格書 V 1.0", "cover_sub"), Spacer(1, 10),
             P("Software Requirements Specification (SRS)", "cover_en"),
             P("Software Design Document (SDD)", "cover_en"), Spacer(1, 30),
             P("第 6 週 Iteration 1：F1 課程與學生資料管理", "cover_member"), Spacer(1, 150)]
    for role, name, sid, mail in MEMBERS:
        story.append(P(esc(f"{name}　{sid}　{mail}".rstrip()), "cover_member"))
    story += [Spacer(1, 50), P("計算機程式設計團體作業｜第 15 組", "cover_member"),
              P("Department of Computer Science &amp; Information Engineering", "cover_en"),
              P("National Taipei University of Technology", "cover_en"), Spacer(1, 30),
              P(DATE, "cover_en")]
    return story


def section_intro() -> list:
    return [
        P("1. 簡介 (Introduction)", "h1"),
        P("1.1 目標 (Purpose)", "h2"),
        P("本系統提供學生與教務人員一套校園選課與活動管理工具，協助管理課程、學生與教室資料，"
          "檢查選課衝突、產生個人課表並安排校園活動，以提高選課效率、減少人工排課的錯誤。"
          "本文件描述第 6 週（Iteration 1）完成的 F1 課程與學生資料管理之需求與設計，作為後續 F2～F11 開發的共同基礎。"),
        P("1.2 系統名稱 (Identification)", "h2"),
        P("校園選課與課表規劃系統（Campus Course Registration and Timetable Planning System），程式套件名稱為 campus_planner。"),
        P("1.3 概觀 (Overview)", "h2"),
        P("系統依老師規範分為 F1～F11：期中完成課程與學生資料管理（F1）、多層次衝堂與選課檢查（F2）、"
          "個人課表與空閒時段（F3）、校園活動與教室配置（F4）、多條件課程篩選（F5）及資料儲存與系統測試（F6）；"
          "期末加入最佳課表搜尋（F7）、搜尋演算法比較（F8）、校園移動路徑規劃（F9）、動態事件重新規劃（F10）"
          "與 AI 輔助品質改善（F11）。"),
        P("系統採用 Python 命令列介面（CLI）。所有核心功能以可獨立測試的函式實作，資料以參數傳遞，"
          "不使用全域變數、不依賴 input()；錯誤一次全部列出，而不是停在第一個。"),
        PageBreak(),
    ]


def section_system() -> list:
    uc_add = [
        "Use Case ID：UC-F1-01",
        "Use Case 名稱：新增課程（Add Course）",
        "主要參與者（Actor）：教務助理",
        "目的（Goal）：建立一筆新的課程資料",
        "前置條件（Precondition）：系統已載入課程資料（SchoolCatalog）",
        "觸發事件（Trigger）：教務助理執行新增課程功能",
        "後置條件（Postcondition）：新課程加入 catalog，可依代號、教師、星期、必選修、剩餘名額查詢",
    ]
    flow = [
        "1. 教務助理提供課程代號、名稱、學分、必選修、授課教師、人數上限、教室及上課時段。",
        "2. 系統檢查所有欄位是否合法，並一次收集所有錯誤。",
        "3. 系統確認課程代號沒有重複。",
        "4. 全部通過時新增課程，回傳空的錯誤清單。",
    ]
    alt = [
        "- 2a. 學分不是正整數（0、-3、3.5、True、\"3\"）：回傳「學分必須為正整數」，不新增。",
        "- 2b. 星期不在 1～7 或節次不在 1～9、a、b、c：回傳「星期不合法」或「節次不合法」。",
        "- 2c. 人數上限小於 1：回傳「人數上限不得小於 1」。",
        "- 2d. 同一門課重複列出同一時段：回傳「時段重複」。",
        "- 3a. 課程代號已存在：回傳「課程代號不得重複」，原有資料不變。",
    ]
    uc_del = [
        "Use Case ID：UC-F1-02　名稱：刪除課程（Delete Course）",
        "主要流程：教務助理指定課程代號 → 系統確認課程存在且沒有學生選修 → 刪除課程。",
        "例外流程：仍有學生選修時拒絕刪除，資料不變；需先退選，或執行「課程取消」程序"
        "（cancel_course：先替所有選修學生退選，再刪除課程，並回傳受影響的學號）。",
    ]
    student_fmt = [["id", "name", "department", "enrolled_courses", "credit_limit"],
                   ["學號（str，不可重複）", "姓名（str）", "系級（str）", "已選課程代號（list[str]，須存在、不可重複）", "學分上限（正整數）"]]
    student_ex = [["id", "name", "department", "enrolled_courses", "credit_limit"],
                  ["S001", "王小明", "資工系", "CS101、CS102、CS201、GE101", "24"],
                  ["S007", "吳志明", "電機系", "EE101、EE102、MA102、GE101", "24"],
                  ["S011", "鄭宇翔", "數學系", "MA101、MA102、MA201、MA202", "22"],
                  ["…", "…", "…", "…", "…"]]
    course_fmt = [["欄位", "中文", "型別與限制"],
                  ["course_id", "課程代號", "str，不可空白、不可重複"],
                  ["name／teacher／classroom", "名稱／授課教師／教室", "str，不可空白"],
                  ["credits", "學分", "正整數（不接受 0、小數、布林值）"],
                  ["required", "必選修", "bool（true＝必修）"],
                  ["capacity", "人數上限", "正整數，至少 1；修改時不得小於目前選課人數"],
                  ["time_slots", "上課時段", "list[{day, period}]；day 為 1～7，period 為 1～9、a、b、c；同課程不得重複"]]
    course_ex = [["course_id", "name", "credits", "required", "teacher", "capacity", "classroom", "time_slots"],
                 ["CS101", "Python 程式設計", "3", "必修", "林老師", "40", "A101", "週一 2、3、4"],
                 ["MA101", "微積分", "4", "必修", "張老師", "50", "C305", "週一 2、3；週三 3、4"],
                 ["CS399", "專題研究", "1", "選修", "林老師", "1", "A102", "週五 9"],
                 ["GE301", "夜間通識講座", "1", "選修", "許老師", "60", "B202", "週日 a、b、c"]]
    room_fmt = [["room_id", "capacity", "equipment", "building"],
                ["教室代號（str，不可重複）", "容量（正整數）", "設備（list[str]）", "建築物（str）"],
                ["A101", "50", "投影機、白板", "資訊大樓"],
                ["B202", "60", "投影機、白板、麥克風", "工程大樓"]]
    return [
        P("2 系統 (System)", "h1"),
        P("2.1 系統描述 (System Description)", "h2"),
        P("本系統為「校園選課與課表規劃系統」。第 6 週完成 F1：課程、學生與教室資料的新增、修改、刪除與查詢，"
          "並提供課程取消程序與 JSON 資料載入。"),
        P("系統採分層架構：命令列介面（main.py）負責展示與操作；F1 資料管理模組（data_manager.py）"
          "以 SchoolCatalog 保存三類資料並提供操作函式；驗證模組（validation.py）與資料模型（models.py）"
          "定義欄位規則與資料結構；資料存取模組（data_store.py）負責 JSON 讀寫。後續 F2～F11 一律沿用同一個 SchoolCatalog，"
          "不另建一套資料。"),
        P("2.1.1 使用案例模型 (Use Case Model)", "h3"),
        P("本系統 F1 之 Use Case Diagram 如圖一所示，分為課程管理與學生、教室管理兩部分。"),
        use_case_diagram(),
        P("圖一、系統使用案例圖（F1）", "caption"),
        P("F1 Use Case 描述：新增課程", "h4"),
        *items(uc_add),
        P("主要成功流程（Main Success Scenario）", "label"), *items(flow),
        P("替代流程（Alternative／Exception Flow）", "label"), *items(alt),
        P("輸入資料（Input）", "label"),
        code_block('Course("CS101", "Python 程式設計", 3, True, "林老師", 40, "A101",\n'
                   '       [TimeSlot(1, "2"), TimeSlot(1, "3"), TimeSlot(1, "4")])'),
        P("預期輸出（Output）", "label"),
        code_block("[]　　# 空清單代表新增成功，可用 find_courses(catalog, course_id=\"CS101\") 查到\n"
                   "[\"課程代號不得重複\"]　　# 再新增一次相同代號時"),
        P("F1 Use Case 描述：刪除課程", "h4"),
        *items(uc_del),
        P("2.1.2 系統架構圖 (System Architecture Diagram)", "h3"),
        P("本系統之系統架構如圖二所示，實線為第 6 週已完成的模組，虛線為後續週次加入的模組。"),
        architecture_diagram(),
        P("圖二、系統架構圖", "caption"),
        P("2.2 系統資料 (System Data)", "h2"),
        P("2.2.1 資料格式 (Data Format)", "h3"),
        P("資料以 JSON 儲存於 data/sample_school_data.json，包含 courses、students、classrooms 三個清單；"
          "範例資料共 20 門課程、15 名學生、5 間教室。"),
        P("學生（Student）", "label"), table(student_fmt, [14, 14, 14, 34, 18]), Spacer(1, 6),
        P("Example", "label"), table(student_ex, [10, 12, 12, 46, 16]), Spacer(1, 8),
        P("課程（Course）", "label"), table(course_fmt, [26, 20, 54]), Spacer(1, 6),
        P("Example", "label"), table(course_ex, [11, 17, 8, 8, 10, 9, 10, 27]), Spacer(1, 8),
        P("教室（Classroom）", "label"), table(room_fmt, [25, 18, 32, 25]),
        P("2.3 F1 需求規格 (Requirements)", "h2"),
        P("老師規範中未明訂的細部規則，第 6 週實作時採下列做法，R1～R11 已經團隊會議確認；"
          "之後若有修改，記錄於 2.3.2。"),
        P("2.3.1 細部規格 (Detailed Rules)", "h3"),
        table(RULES, [8, 18, 46, 18, 10]), Spacer(1, 6),
        P("2.3.2 需求／設計修改紀錄 (Change Log)", "h3"),
        table(CHANGES, [14, 20, 22, 26, 18]),
        PageBreak(),
    ]


def section_design() -> list:
    iface = [["項目", "說明"],
             ["函式名稱", "add_course()"],
             ["功能描述", "新增一筆課程資料"],
             ["輸入（Input）", "目前所有資料 catalog（SchoolCatalog）、新課程 course（Course）"],
             ["輸出（Output）", "錯誤訊息清單 list[str]；空清單代表新增成功"],
             ["前置條件", "catalog 為已建立的 SchoolCatalog"],
             ["處理規則", "以 validate_course 檢查所有欄位與時段，並檢查課程代號是否重複；一次收集所有錯誤"],
             ["後置條件", "成功時 catalog.courses 增加一筆；失敗時 catalog 完全不變"]]
    others = [["函式", "輸入 → 輸出", "重點規則"],
              ["update_course(catalog, course_id, **changes)", "要修改的欄位 → 錯誤清單", "不可改代號；人數上限不得小於目前選課人數；失敗時資料不變"],
              ["delete_course(catalog, course_id)", "代號 → bool", "仍有學生選修時回傳 False"],
              ["cancel_course(catalog, course_id)", "代號 → 被退選的學號清單", "先替選修學生退選，再刪除課程"],
              ["find_courses(catalog, …)", "代號前綴、教師、星期、必選修、最少剩餘名額 → list[Course]", "條件可任意組合，結果依代號排序"],
              ["add_student／update_student／delete_student／find_students", "Student 或條件 → 錯誤清單／bool／清單", "學號不可重複；已選課程必須存在"],
              ["add_classroom／update_classroom／delete_classroom／find_classrooms", "Classroom 或條件 → 錯誤清單／bool／清單", "仍有課程使用的教室不可刪除"],
              ["load_catalog(path)", "JSON 路徑 → (catalog, errors)", "單筆錯誤只略過並記錄，不會中止"]]
    tests = [["測試編號", "測試類型", "測試情境", "預期結果"],
             ["TC01", "正常", "新增 CS101，3 學分，人數上限 30", "回傳 []，可依教師與星期查到"],
             ["TC02", "邊界", "人數上限 1", "回傳 []，成功新增"],
             ["TC03", "邊界", "時段為星期 7 第 c 節", "回傳 []，成功新增"],
             ["TC04", "錯誤", "新增已存在的 CS101", "「課程代號不得重複」，原資料不變"],
             ["TC05", "錯誤", "學分為 0、-3、3.5、True、\"3\"", "「學分必須為正整數」"],
             ["TC06", "錯誤", "節次為 d、0、10、空字串", "「節次不合法」"],
             ["TC07", "錯誤", "星期為 0、8", "「星期不合法」"],
             ["TC08", "錯誤", "同一門課重複列出星期 1 第 3 節", "「時段重複: 星期1 第3節」"]]
    return [
        P("3. 軟體設計 (Software Design)", "h1"),
        P("3.1 函式功能介面 (Functionality Interface)", "h2"),
        table(iface, [22, 78]), Spacer(1, 8),
        P("Function:", "label"),
        code_block('''def add_course(catalog: SchoolCatalog, course: Course) -> list[str]:
    """新增一筆課程資料。

    Parameters:
        catalog: 目前所有課程、學生、教室資料（SchoolCatalog）
        course:  新課程資料（Course）
    Returns:
        list[str]: 錯誤訊息清單，空清單表示新增成功；
                   失敗時 catalog 保持不變。
    """'''),
        P("使用範例", "label"),
        code_block('''catalog = SchoolCatalog()
course = Course("CS101", "Python 程式設計", 3, True, "林老師", 30, "A101",
                [TimeSlot(1, "3"), TimeSlot(1, "4")])
errors = add_course(catalog, course)
print(errors)                        # 預期：[]
print(add_course(catalog, course))   # 預期：['課程代號不得重複']'''),
        Spacer(1, 6),
        P("其他 F1 函式（完整說明見 docs/01_規格與設計/F1_函式介面.md）：", "label"),
        table(others, [36, 32, 32]),
        P("3.2 測試案例設計 (Test case design)", "h2"),
        P("針對 add_course() 設計正常、邊界及錯誤測試案例；F1 全部 41 項測試中，正常 11 項、邊界 6 項、錯誤 24 項。"),
        table(tests, [14, 12, 40, 34]), Spacer(1, 6),
        P("F1 驗收條件對照（老師規範之驗收條件與對應的自動化測試，執行結果均為通過）：", "label"),
        table(ACCEPTANCE, [34, 52, 14]), Spacer(1, 6),
        code_block('''def test_reject_duplicate_and_invalid_course_data() -> None:
    catalog = SchoolCatalog()
    valid = Course("CS101", "Python", 3, True, "林老師", 10, "A101", [TimeSlot(2, "3")])
    assert add_course(catalog, valid) == []

    duplicate = Course("CS101", "重複", 2, False, "王老師", 5, "B101", [TimeSlot(2, "4")])
    assert "課程代號不得重複" in add_course(catalog, duplicate)

    bad = Course("CS999", "Bad", 0, False, "老師", 0, "A101", [TimeSlot(8, "x")])
    errors = add_course(catalog, bad)
    assert "學分必須為正整數" in errors
    assert "人數上限不得小於 1" in errors'''),
        P("3.3 專案審查 (Iteration Review 1)", "h2"),
        P("本次 Iteration 完成哪些工作？（Completed Work）", "label"),
        *items([
            "1. 完成課程、學生、教室資料結構與 SchoolCatalog，以及 F1 新增、修改、刪除、查詢與課程取消程序。",
            "2. 支援依課程代號、教師、星期、必選修及剩餘名額查詢課程。",
            "3. 建立 20 門課程、15 名學生、5 間教室的測試資料，並確認沒有教室重複排課、學生衝堂或課程超收。",
            "4. 自動化測試 49 個全部通過（F1 41 個：正常 11、邊界 6、錯誤 24）。",
            "5. main.py 可載入範例資料並示範查詢與錯誤拒絕。",
            "6. 完成第一次 Code Review（成員 A 檢視成員 B 的 data_manager.py、validation.py），提出 7 項問題。",
        ]),
        P("哪些工作尚未完成？（Incomplete Work）", "label"),
        *items([
            "1. Code Review 提出的 7 項問題尚待修正與重新驗證，其中最嚴重的是 JSON 某個清單為 null 時載入會中止。",
            "2. CSV 格式的儲存與載入尚未實作（屬 F6）。",
        ]),
        P("本次 Iteration 遇到哪些問題？（Problems）", "label"),
        *items([
            "1. 規格未明訂：能否修改代號、刪除與取消程序的差異、學分型別等規則，需要先決定才能實作。",
            "2. 資料格式不一致：早期各角色草稿使用不同欄位名稱（如 course_name、max_credits）與 5×8 課表矩陣，與共用資料模型不一致。",
            "3. AI 產生的初版程式中，update_course 的參數名稱與欄位名稱衝突，由測試發現並修正。",
            "4. 載入資料時未檢查人數上限與學分上限，可能出現剩餘名額為負數（Code Review 發現）。",
        ]),
        P("下一次 Iteration 如何改善？（Improvements）", "label"),
        *items([
            "1. 修正 Code Review 問題後重新執行全部測試，並補上對應的測試案例。",
            "2. 統一以 models.py 的欄位為準；規格變更先寫入需求規格的修改紀錄，再實作。",
            "3. 第 7 週 F2 衝堂檢查與 F3 課表產生沿用 SchoolCatalog，先修正額滿判斷與課表索引的既有缺陷。",
            "4. 每次提交前先執行 python -m pytest -q，確認測試全部通過。",
        ]),
        PageBreak(),
    ]


def section_pm() -> list:
    def task(no, title, desc, days, owner):
        return P(esc(f"{no} {title}：{desc}預估工作量：{days} 人天。負責人：{owner}。"), "item")
    member_rows = [["組員", "擔任角色", "主要負責工作", "協作／檢視工作"],
                   ["A", "組長／整合", "專案結構、函式介面、main.py 整合、F6 儲存載入", "Code Review 成員 B 的 F1 程式、Iteration Review"],
                   ["B", "資料管理", "課程、學生、教室管理模組與驗證規則", "檢視成員 C 的 F1 測試"],
                   ["C", "選課限制", "F1 測試設計與執行（正常、邊界、錯誤）", "檢視成員 D 的工作"],
                   ["D", "課表活動", "教室欄位檢查、F3 課表介面準備", "檢視成員 E 的範例資料"],
                   ["E（副組長）", "搜尋效能", "20 門課、15 名學生、5 間教室範例資料", "檢視成員 A 的 main.py"]]
    return [
        P("4. 專案管理 (Project Management)", "h1"),
        P("4.1 工作分解表 (Work Breakdown Structure)", "h2"),
        P("1. 課程與學生資料管理", "label"),
        P("1.1 需求分析", "label"),
        task("1.1.1", "Use Case", "分析教務助理與學生對課程、學生、教室資料的新增、修改、刪除與查詢情境，產出 Use Case Diagram 與 Use Case 描述。", 1, "A"),
        task("1.1.2", "需求規格", "整理老師未明訂的細部規則（R1～R11），包含學分型別、代號修改、刪除與取消程序，產出需求規格第 10、11 節。", 2, "A、B"),
        P("1.2 功能設計", "label"),
        task("1.2.1", "系統架構圖", "規劃命令列介面、資料管理、驗證、資料模型與資料存取的分層關係，產出系統架構圖。", 1, "A"),
        task("1.2.2", "資料格式", "定義課程、學生、教室的欄位、型別與限制條件，產出資料格式說明。", 1, "B"),
        task("1.2.3", "函式介面", "定義各函式的輸入、輸出、錯誤處理與失敗時資料不變的約定，產出 F1 函式介面文件。", 1, "A"),
        P("1.3 功能實作", "label"),
        task("1.3.1", "課程管理", "實作課程新增、修改、刪除、查詢與課程取消程序，並檢查代號、學分、人數上限與時段。", 2, "B"),
        task("1.3.2", "學生與教室管理", "實作學生與教室的新增、修改、刪除與查詢，檢查學號、教室代號與已選課程。", 2, "B"),
        task("1.3.3", "範例資料", "建立 20 門課、15 名學生、5 間教室，確認無教室重複排課、學生衝堂與超收。", 1, "E"),
        task("1.3.4", "系統整合", "main.py 載入 JSON 範例資料並示範 F1 查詢與錯誤拒絕，產出第一個可執行版本。", 1, "A"),
        P("1.4 功能測試", "label"),
        task("1.4.1", "單元測試", "針對 F1 設計正常、邊界與錯誤案例並執行，產出測試結果。", 2, "C"),
        task("1.4.2", "Code Review", "由非原開發者依 A → B → C → D → E → A 的順序檢視，產出 Code Review 紀錄。", 1, "全員"),
        task("1.4.3", "Iteration Review", "彙整第 6 週 F1 完成情況、測試結果、問題與改善項目，產出 Iteration Review 1。", 1, "A"),
        Spacer(1, 8),
        table(member_rows, [13, 14, 39, 34]),
        Spacer(1, 10),
        KeepTogether([wbs_diagram(), P("圖三、工作分解結構圖", "caption")]),
        P("4.2 版本控管 (Version Control)", "h2"),
        P("Git Repository：https://github.com/0mago0/programing_team_project"),
        P("本週主要 Commit 與負責成員（本週無 Merge）：", "label"),
        table(COMMITS, [13, 15, 10, 62]), Spacer(1, 6),
        P("完整 git log：", "label"),
        terminal_block(git_log()),
        PageBreak(),
    ]


def section_end() -> list:
    glossary = [["名詞", "說明"],
                ["CLI", "命令列介面（Command Line Interface），本系統的操作方式。"],
                ["CRUD", "新增（Create）、查詢（Read）、修改（Update）、刪除（Delete）。"],
                ["SchoolCatalog", "保存課程、學生、教室三類資料的容器，所有 F1 函式都以它作為參數。"],
                ["TimeSlot", "一個上課時段，由星期（1～7）與節次（1～9、a、b、c）組成。"],
                ["課程取消程序", "先替所有選修學生退選，再刪除課程（cancel_course）。"],
                ["剩餘名額", "人數上限減去選修學生數；選修人數只由學生的已選課程計算。"],
                ["Code Review", "由非原開發者檢視程式，找出錯誤並提出改善建議。"],
                ["Iteration Review", "每個 Iteration 結束時回顧完成、未完成、問題與改善項目。"],
                ["pytest", "Python 自動化測試工具，以 python -m pytest -q 執行。"]]
    refs = [
        "[1] 1151 計算機程式設計團體作業規範（docs/00_老師作業/assignment.pdf）。",
        "[2] 本專案需求規格 v1 與 F1 函式介面（docs/01_規格與設計/）。",
        "[3] Python 3.11 官方文件：dataclasses、json。https://docs.python.org/3.11/",
        "[4] pytest 官方文件。https://docs.pytest.org/",
    ]
    return [
        P("Glossary", "h1"), table(glossary, [24, 76]), PageBreak(),
        P("References", "h1"), *items(refs), PageBreak(),
        P("Appendix", "h1"),
        P("A. 功能完成表", "label"),
        table(FEATURES, [26, 14, 60]), Spacer(1, 8),
        P("B. 問題與缺陷紀錄", "label"),
        table(DEFECTS, [7, 47, 12, 12, 22]), Spacer(1, 8),
        P("C. Code Review 紀錄", "label"),
        table(REVIEW_INFO, [20, 80], header=False), Spacer(1, 6),
        P("發現的問題與建議（每一項均以實際執行結果確認）：", "label"),
        table(REVIEW_ISSUES, [6, 44, 10, 40]), Spacer(1, 4),
        P("另有兩點屬規格問題，列入團隊討論：同一教室同時段可新增兩門課（規格 R6，留給 F2 教室衝堂）；"
          "沒有任何上課時段的課程可以新增（是否允許待團隊決定）。"),
        table(REVIEW_STATUS, [20, 80], header=False), Spacer(1, 8),
        P("D. 執行方式", "label"),
        code_block("python main.py          # 載入範例資料並示範 F1\npython -m pytest -q     # 執行全部自動化測試"),
        P("E. main.py 執行結果", "label"),
        terminal_block("$ python main.py\n" + run(["main.py"])),
        Spacer(1, 6),
        P("F. 自動化測試結果", "label"),
        terminal_block("$ python -m pytest -q\n" + run(["-m", "pytest", "-q", "-p", "no:cacheprovider"])),
        Spacer(1, 8),
        P("G. 團隊會議紀錄與討論照片", "label"),
        table(MEETING, [18, 82], header=False), Spacer(1, 8),
        KeepTogether([
                      Image(str(PHOTO), width=FRAME_W, height=FRAME_W * 1108 / 1477),
                      P("第 6 週團隊討論（2026/10/14，科研大樓一樓）", "caption")]),
    ]


# ---------- 補充資料表 ----------

RULES = [
    ["編號", "規則", "採用做法", "理由", "狀態"],
    ["R1", "學分型別", "只接受正整數；3.5、True、\"3\" 都拒絕", "規範要求正整數；Python 的 True 會被當成 1", "已確認"],
    ["R2", "修改代號", "不允許修改課程代號、學號、教室代號，需刪除後重建", "代號是其他資料的參照鍵", "已確認"],
    ["R3", "修改人數上限", "不得小於目前選課人數", "避免已選學生超收", "已確認"],
    ["R4", "刪除課程", "有人選修則拒絕；另提供課程取消程序，先退選再刪除", "對應規範「先執行退選或課程取消程序」", "已確認"],
    ["R5", "新增學生", "已選課程必須存在於課程資料", "避免指向不存在的課程", "已確認"],
    ["R6", "課程的教室", "第 6 週不檢查教室是否存在、不比較課程與教室容量", "屬 F2 教室衝堂與 F4 場地配置範圍", "已確認"],
    ["R7", "同課程時段重複", "同一門課重複列出同一時段時拒絕", "視為資料輸入錯誤", "已確認"],
    ["R8", "代號查詢", "前綴比對，輸入 CS 可找出 CS101、CS102…", "方便依系所代碼查詢", "已確認"],
    ["R9", "星期查詢", "課程任一時段在該星期即符合", "一門課可能一週上多天", "已確認"],
    ["R10", "剩餘名額", "人數上限減選修學生數，選修人數只由學生的已選課程計算", "選課紀錄以唯一來源為準", "已確認"],
    ["R11", "載入錯誤", "單筆資料錯誤只略過並記錄原因，其他資料照常載入", "規範：單筆錯誤不得造成程式異常終止", "已確認"],
]

CHANGES = [
    ["日期", "項目", "修改前（第 5 週）", "修改後（第 6 週）", "原因"],
    ["2026/10/16", "學分驗證", "僅拒絕 0 以下，3.5 與 True 可通過", "只接受正整數", "規範要求學分為正整數"],
    ["2026/10/16", "時段驗證", "只檢查星期與節次範圍", "另拒絕同課程重複時段", "資料輸入錯誤應被擋下"],
    ["2026/10/16", "教室資料", "只有 Classroom 資料模型", "新增驗證與新增、修改、刪除、查詢", "F1 驗收需要 5 間教室"],
    ["2026/10/16", "資料容器", "各模組以 list 或 dict 傳遞", "統一使用 SchoolCatalog", "讓 F2 之後的模組共用同一份資料"],
    ["2026/10/16", "選課人數", "未定義", "由學生的已選課程推算，不另存計數", "維持唯一資料來源"],
    ["2026/10/16", "F1 細部規則", "未定義", "R1～R11（見 2.3.1）", "實作需要明確規則；已經團隊會議確認"],
]

ACCEPTANCE = [
    ["驗收條件", "對應測試（tests/）", "結果"],
    ["至少 20 門課程、15 名學生、5 間教室", "test_sample_data_meets_week6_acceptance", "通過"],
    ["拒絕重複代號", "test_reject_duplicate_and_invalid_course_data、test_reject_duplicate_student_id", "通過"],
    ["拒絕非法節次", "test_reject_invalid_period（d、0、10、空字串）", "通過"],
    ["拒絕無效學分", "test_reject_invalid_credits（0、-3、3.5、True、\"3\"）", "通過"],
    ["不得刪除已有學生選修的課程", "test_delete_course_protected_when_students_enrolled、test_cancel_course_drops_students_then_deletes", "通過"],
    ["依代號、教師、星期、必選修、剩餘名額查詢", "test_find_courses_by_each_condition、test_full_course_has_zero_remaining", "通過"],
    ["邊界：人數上限 1、星期 7、節次 c", "test_capacity_one_is_allowed、test_day_seven_and_period_c_are_valid", "通過"],
]

COMMITS = [
    ["Commit", "日期", "負責成員", "內容"],
    ["85b074f", "2026/10/16", "A", "主程式 main.py 接上 F1：載入範例資料並示範查詢與錯誤拒絕；新增 pytest.ini"],
    ["6841bc9", "2026/10/16", "B", "F1 程式：data_manager.py（課程、學生、教室管理）與 validation.py（驗證規則）"],
    ["2be7180", "2026/10/16", "A", "整理專案結構：docs 分類、合併角色資料夾、F1 規格與介面文件"],
    ["b3958a8", "2026/10/16", "C", "F1 自動化測試 test_f1_catalog.py（41 項）"],
]

FEATURES = [
    ["功能", "狀態", "說明"],
    ["F1 課程與學生資料管理", "測試通過", "49 項自動化測試全部通過；Code Review 提出的問題待修正"],
    ["F2 多層次衝堂與選課檢查", "未開始", "已有時段衝突判斷與 evaluate_enrollment 雛形（見缺陷 D1），第 7 週開發"],
    ["F3 個人課表與空閒時段", "開發中", "已有 7×12 課表矩陣雛形（見缺陷 D2、D3），第 7 週開發"],
    ["F4 校園活動與教室配置", "未開始", "第 7 週開始需求分析，第 8 週開發"],
    ["F5 多條件課程篩選", "未開始", "第 8 週開發"],
    ["F6 資料儲存與系統測試", "開發中", "JSON 載入與儲存完成，單筆錯誤不中止；CSV 尚未實作；自動化測試已有 49 項"],
    ["F7 最佳課表搜尋", "未開始", "第 10 週開發"],
    ["F8 搜尋演算法比較", "未開始", "第 11 週開發"],
    ["F9 校園移動路徑規劃", "未開始", "第 12 週開發"],
    ["F10 動態事件與重新規劃", "未開始", "第 14 週開發"],
    ["F11 AI 輔助測試與品質改善", "未開始", "第 15 週開發"],
]

DEFECTS = [
    ["編號", "問題", "影響", "狀態", "處理方式／負責"],
    ["D1", "evaluate_enrollment 以「學生已選幾門課」比較課程人數上限：無人選修、上限 2 的課，對已選 2 門其他課的學生判定為已額滿", "F2", "未處理", "改用 enrolled_count 計算；C"],
    ["D2", "place_course_in_timetable 收到星期 0 時寫入星期日的位置，未報錯；同一格兩門課時直接覆蓋", "F3", "未處理", "檢查星期範圍並回報衝突；D"],
    ["D3", "find_available_slots 從第 b 節查 3 節時，靜默截斷只回傳 2 節", "F3", "未處理", "超出範圍時回報錯誤；D"],
    ["D4", "save_catalog 只寫課程、學生、教室，資料檔的 activities 欄位不會保留", "F4／F6", "未處理", "F4 加入活動資料時一併處理；A、D"],
    ["D5", "新增課程不檢查教室是否存在，也不比較課程人數與教室容量（規格 R6）", "F2／F4", "待討論", "團隊會議決定；C、D"],
    ["D6", "早期各角色草稿的欄位名稱與共用資料模型不一致（如 course_name、max_credits、5×8 課表矩陣）", "全組", "已處理", "統一以 models.py 為準，草稿封存不再使用；A"],
    ["D7", "節次定義重複：models.py 的 VALID_PERIODS 與 timetable.py 的 PERIOD_ORDER", "共用", "未處理", "改為共用同一份定義；A"],
]


MEETING = [
    ['日期／地點', '2026/10/14（三）中午｜科研大樓一樓'],
    ['出席', 'A、B、C、D、E（全員出席）'],
    ['討論事項', '1. 第 6 週 F1 範圍與驗收條件：20 門課、15 名學生、5 間教室，須拒絕重複代號、非法節次與無效學分。\n2. F1 細部規則 R1～R11：學分型別、能否修改代號、刪除與課程取消程序、剩餘名額計算、載入錯誤處理等。\n3. 統一資料欄位：以 models.py 為準，舊角色草稿不再使用。\n4. 提交方式與 Code Review 順序（A → B → C → D → E → A）。'],
    ['工作分配', 'A：專案結構整理、F1 函式介面、main.py 整合、Iteration Review。\nB：課程、學生、教室管理模組與驗證規則。\nC：F1 自動化測試設計與執行。\nD：教室欄位檢查、F3 課表介面準備。\nE：20 門課、15 名學生、5 間教室範例資料。'],
    ['決議', '1. F1 細部規格 R1～R11 全部確認採用。\n2. 資料欄位統一以 models.py 為準。\n3. 每人提交前先執行 python -m pytest -q，確認測試全部通過。'],
    ['下週目標', '第 7 週：C 開發 F2 多層次衝堂與選課檢查，D 開發 F3 個人課表與空閒時段；先修正缺陷 D1～D3；開始 F4 活動與教室配置的需求分析。'],
]


REVIEW_INFO = [
    ["被檢視程式", "data_manager.py、validation.py（F1 資料管理）"],
    ["原開發者／提交", "成員 B｜commit 6841bc9｜2026/10/16"],
    ["檢視者／日期", "成員 A｜2026/10/16"],
    ["檢視方式", "閱讀程式邏輯；以範例資料與自製的錯誤資料執行 catalog_from_dict、add_student、remaining_seats、delete_course 等函式並記錄實際輸出；使用 AI 輔助列出可疑之處，每一項都以執行結果確認。"],
    ["優點", "新增、修改失敗時原資料保持不變；一次列出所有錯誤；選課人數只由學生的已選課程計算，沒有兩份資料不同步的問題；JSON 中節次寫成整數 3 也會正確轉為 \"3\"。"],
]

REVIEW_ISSUES = [["#", "問題（實際執行結果）", "嚴重度", "建議修改"]] + [['1', 'JSON 中某個清單是 null（例如 "courses": null）時，catalog_from_dict 丟出 TypeError，整個載入中止，違反 F6「不得因單一筆資料格式錯誤造成程式異常終止」。', '高', '清單不是 list 時記錄錯誤並視為空清單。'], ['2', '載入時不檢查人數上限：人數上限 1 的 CS399 有 3 名學生選修仍可載入，remaining_seats 回傳 -2。', '中', 'add_student 檢查每門已選課程是否額滿，或至少在載入時記錄超收警告。'], ['3', '新增學生不檢查學分上限：學分上限 1 的學生可以選 3 學分的課。', '中', '與 C 討論：由 F1 新增時檢查，或明確規定由 F2 加選時檢查，並寫入規格。'], ['4', '星期傳入 1.0（浮點數）會通過驗證；之後放進課表矩陣當索引時會出錯。', '低', '驗證星期時同時檢查型別必須是 int。'], ['5', 'remaining_seats 查詢不存在的課程直接丟出 KeyError，與其他函式「回傳錯誤訊息」的約定不一致。', '低', '改為回傳錯誤或在文件中註明呼叫前須確認課程存在。'], ['6', 'delete_course 刪除不存在的課程與刪除有人選修的課程都回傳 False，呼叫端無法分辨原因，main.py 一律顯示「需先退選」。', '低', '改為回傳錯誤清單，與新增、修改一致。'], ['7', 'update_course 修改其他欄位後，新舊課程物件共用同一個 time_slots 清單。', '低', '用 list(...) 複製一份，避免日後修改互相影響。']]

REVIEW_STATUS = [
    ["處理狀態", "第 1～7 項交給 B 修正，其中第 1 項會讓載入中止，優先處理；修正後由 A 重新執行上述檢查與全部測試，再補上修改內容與驗證結果。"],
]


# ---------- 文件組裝 ----------

class SpecDoc(BaseDocTemplate):
    def __init__(self, filename: str):
        super().__init__(filename, pagesize=A4, leftMargin=25 * mm, rightMargin=25 * mm,
                         topMargin=22 * mm, bottomMargin=22 * mm, title="系統需求設計規格書 V1.0",
                         author="第 15 組")
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="f")
        self.body_start: int | None = None
        self.addPageTemplates([
            PageTemplate("cover", [frame]),
            PageTemplate("front", [frame], onPage=self._front_footer),
            PageTemplate("body", [frame], onPage=self._body_footer),
        ])

    def _front_footer(self, canvas, doc):
        canvas.setFont("KAI", 10)
        canvas.drawCentredString(A4[0] / 2, 12 * mm, "i")

    def _body_footer(self, canvas, doc):
        if self.body_start is None:
            self.body_start = doc.page
        canvas.setFont("KAI", 10)
        canvas.drawCentredString(A4[0] / 2, 12 * mm, str(doc.page - self.body_start + 1))

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name in ("h1", "h2", "h3"):
            level = {"h1": 0, "h2": 1, "h3": 2}[flowable.style.name]
            start = self.body_start or self.page
            self.notify("TOCEntry", (level, flowable.getPlainText(), self.page - start + 1))

    def handle_documentBegin(self):
        self.body_start = None
        super().handle_documentBegin()


def build() -> None:
    toc = TableOfContents(dotsMinLevel=0)
    toc.levelStyles = [
        ParagraphStyle("t0", fontName="JHB", fontSize=11, leading=18, leftIndent=0),
        ParagraphStyle("t1", fontName="KAI", fontSize=11, leading=17, leftIndent=18),
        ParagraphStyle("t2", fontName="KAI", fontSize=10.5, leading=16, leftIndent=36),
    ]
    story = [*cover(), NextPageTemplate("front"), PageBreak(),
             P("目錄 (Table of Contents)", "toc_title"), toc,
             NextPageTemplate("body"), PageBreak(),
             *section_intro(), *section_system(), *section_design(), *section_pm(), *section_end()]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    SpecDoc(str(OUTPUT)).multiBuild(story)
    print(f"已產生：{OUTPUT}")


if __name__ == "__main__":
    build()
