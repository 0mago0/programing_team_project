"""把影片 I 的畫面圖片組成 PowerPoint（講稿放進每頁的備忘稿）與 PDF。

用法：python tools/make_video_pptx.py
輸入：docs/03_週報/影片I素材/*.png、docs/03_週報/第8週_影片I講稿.md
輸出：docs/03_週報/第8週_影片I投影片.pptx、第8週_影片I投影片.pdf

先執行 make_video_assets.py 產生圖片。需要 python-pptx 與 reportlab。
"""
from __future__ import annotations

import re
from pathlib import Path

from pptx import Presentation
from pptx.util import Emu
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
WEEK = ROOT / "docs" / "03_週報"
ASSETS = WEEK / "影片I素材"
SCRIPT = WEEK / "第8週_影片I講稿.md"
OUT = WEEK / "第8週_影片I投影片.pptx"
PDF_OUT = OUT.with_suffix(".pdf")
PDF_W, PDF_H = 960, 540  # 點，16:9
SLIDE_W, SLIDE_H = Emu(12192000), Emu(6858000)  # 16:9


def notes_by_image() -> dict[str, str]:
    """講稿中「### 第 N 頁 標題｜檔名.png」之後到下一個標題前的文字。"""
    notes, current, segment = {}, None, ""
    for line in SCRIPT.read_text(encoding="utf-8").splitlines():
        if line.startswith("## 第"):
            segment = line[3:].strip()
            continue
        m = re.match(r"###\s+(.*)｜(\S+\.png)", line)
        if m:
            current = m.group(2)
            notes[current] = [f"【{segment}】{m.group(1).strip()}"]
            continue
        if line.startswith("#"):
            current = None
        elif current and line.strip():
            notes[current].append(line.strip())
    return {k: "\n\n".join(v) for k, v in notes.items()}


def main() -> None:
    notes = notes_by_image()
    prs = Presentation()
    prs.slide_width, prs.slide_height = SLIDE_W, SLIDE_H
    blank = prs.slide_layouts[6]
    for image in sorted(ASSETS.glob("*.png")):
        slide = prs.slides.add_slide(blank)
        slide.shapes.add_picture(str(image), 0, 0, SLIDE_W, SLIDE_H)
        slide.notes_slide.notes_text_frame.text = notes.get(image.name, "")
        print(f"{image.name}：{'有' if image.name in notes else '無'}講稿")
    prs.save(OUT)
    print(f"已產生：{OUT}")

    pdf = canvas.Canvas(str(PDF_OUT), pagesize=(PDF_W, PDF_H))
    pdf.setTitle("影片 I 投影片")
    for image in sorted(ASSETS.glob("*.png")):
        pdf.drawImage(str(image), 0, 0, PDF_W, PDF_H)
        pdf.showPage()
    pdf.save()
    print(f"已產生：{PDF_OUT}")


if __name__ == "__main__":
    main()
