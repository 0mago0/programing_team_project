"""把個人紀錄 Markdown 轉成與第 5 週個人繳交相同版面的 PDF。

用法：python tools/make_personal_pdf.py <輸入.md> [輸出.pdf]
未指定輸出時，產生在輸入檔旁邊、同檔名的 .pdf。

支援的 Markdown：
- `# 標題`（置中大標）、標題後第一段為副標
- `## 一、…`（藍色大標）、`### 1. …`（藍色小標）
- `- 項目`（• 項目）、一般段落
- 表格：儲存格內用 `<br>` 換行
- `<!-- footer: 文字 -->`：頁尾，自動加上「第 N 頁」
- `<!-- info -->`：下一個表格是基本資料表（不套表頭底色）
- `<!-- widths: 20,80 -->`：下一個表格的欄寬比例
需要 reportlab 與 Windows 的微軟正黑體（msjh.ttc）。
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

FONT_FILE = Path(r"C:\Windows\Fonts\msjh.ttc")
FONT = "MSJH"
BOLD_FILE = Path(r"C:\Windows\Fonts\msjhbd.ttc")
BOLD = "MSJHB"
BLUE = colors.HexColor("#2E74B5")
HEADER_BG = colors.HexColor("#D9E2F3")
BORDER = colors.HexColor("#A6A6A6")
TEXT = colors.HexColor("#1A1A1A")
GREY = colors.HexColor("#666666")
MARGIN = 20 * mm

STYLES = {
    "title": ParagraphStyle("title", fontName=FONT, fontSize=22, leading=30, alignment=1, textColor=TEXT, spaceAfter=10, wordWrap="CJK"),
    "subtitle": ParagraphStyle("subtitle", fontName=FONT, fontSize=9, leading=13, textColor=TEXT, spaceAfter=8, wordWrap="CJK"),
    "h1": ParagraphStyle("h1", fontName=FONT, fontSize=17, leading=24, textColor=BLUE, spaceBefore=10, spaceAfter=6, wordWrap="CJK", keepWithNext=1),
    "h2": ParagraphStyle("h2", fontName=FONT, fontSize=11.5, leading=16, textColor=BLUE, spaceBefore=6, spaceAfter=4, wordWrap="CJK", keepWithNext=1),
    "body": ParagraphStyle("body", fontName=FONT, fontSize=10, leading=16, textColor=TEXT, spaceAfter=6, wordWrap="CJK"),
    "cell": ParagraphStyle("cell", fontName=FONT, fontSize=9, leading=14, textColor=TEXT, wordWrap="CJK"),
}


def inline(text: str) -> str:
    """跳脫 HTML 特殊字元，保留 <br> 換行；**文字** 轉為粗體。"""
    parts = re.split(r"<br\s*/?>", text)
    escaped = "<br/>".join(html.escape(p.strip(), quote=False) for p in parts)
    face = BOLD if BOLD_FILE.exists() else FONT
    return re.sub(r"\*\*(.+?)\*\*", lambda m: f'<font name="{face}">{m.group(1)}</font>', escaped)


def parse_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def build_table(rows: list[list[str]], widths: list[float] | None, info: bool, frame_width: float) -> Table:
    cols = len(rows[0])
    if not widths or len(widths) != cols:
        widths = [100 / cols] * cols
    total = sum(widths)
    col_widths = [frame_width * w / total for w in widths]
    data = [[Paragraph(inline(cell), STYLES["cell"]) for cell in row] for row in rows]
    style = [
        ("GRID", (0, 0), (-1, -1), 0.6, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]
    if not info:
        style.append(("BACKGROUND", (0, 0), (-1, 0), HEADER_BG))
    table = Table(data, colWidths=col_widths, repeatRows=0 if info else 1)
    table.setStyle(TableStyle(style))
    return table


def markdown_to_story(text: str, frame_width: float) -> tuple[list, str]:
    story: list = []
    footer = ""
    widths: list[float] | None = None
    info = False
    lines = text.splitlines()
    i = 0
    after_title = False
    paragraph: list[str] = []

    def flush() -> None:
        nonlocal after_title
        if paragraph:
            content = inline(" ".join(paragraph))
            story.append(Paragraph(content, STYLES["subtitle" if after_title else "body"]))
            after_title = False
            paragraph.clear()

    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()
        comment = re.fullmatch(r"<!--\s*(\w+)\s*:?\s*(.*?)\s*-->", stripped)
        if comment:
            flush()
            key, value = comment.group(1), comment.group(2)
            if key == "footer":
                footer = value
            elif key == "info":
                info = True
            elif key == "widths":
                widths = [float(v) for v in value.split(",")]
            i += 1
            continue
        if not stripped:
            flush()
            i += 1
            continue
        if stripped.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                row = parse_row(lines[i])
                if not all(re.fullmatch(r":?-{3,}:?", c) for c in row):
                    rows.append(row)
                i += 1
            story.append(build_table(rows, widths, info, frame_width))
            story.append(Spacer(1, 8))
            widths, info = None, False
            continue
        heading = re.match(r"(#{1,3})\s+(.*)", stripped)
        if heading:
            flush()
            level = len(heading.group(1))
            style = {1: "title", 2: "h1", 3: "h2"}[level]
            story.append(Paragraph(inline(heading.group(2)), STYLES[style]))
            after_title = level == 1
            i += 1
            continue
        if stripped.startswith("- "):
            flush()
            story.append(Paragraph("• " + inline(stripped[2:]), STYLES["body"]))
            i += 1
            continue
        paragraph.append(stripped)
        i += 1
    flush()
    return story, footer


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("用法：python tools/make_personal_pdf.py <輸入.md> [輸出.pdf]")
    source = Path(sys.argv[1])
    target = Path(sys.argv[2]) if len(sys.argv) > 2 else source.with_suffix(".pdf")
    if not FONT_FILE.exists():
        raise SystemExit(f"找不到字型：{FONT_FILE}")
    pdfmetrics.registerFont(TTFont(FONT, str(FONT_FILE), subfontIndex=0))
    if BOLD_FILE.exists():
        pdfmetrics.registerFont(TTFont(BOLD, str(BOLD_FILE), subfontIndex=0))

    doc = SimpleDocTemplate(
        str(target), pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN, topMargin=18 * mm, bottomMargin=20 * mm,
    )
    story, footer = markdown_to_story(source.read_text(encoding="utf-8"), doc.width)
    title = next((m.group(1) for m in re.finditer(r"^#\s+(.*)$", source.read_text(encoding="utf-8"), re.M)), source.stem)
    doc.title = title

    def draw_footer(canvas, document) -> None:
        canvas.saveState()
        canvas.setFont(FONT, 8)
        canvas.setFillColor(GREY)
        label = f"{footer} ｜ 第 {document.page} 頁" if footer else f"第 {document.page} 頁"
        canvas.drawCentredString(A4[0] / 2, 12 * mm, label)
        canvas.restoreState()

    doc.build(story, onFirstPage=draw_footer, onLaterPages=draw_footer)
    print(f"已產生：{target}")


if __name__ == "__main__":
    main()
