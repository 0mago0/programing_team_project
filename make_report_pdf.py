from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import getSampleStyleSheet

ROOT = Path(r"c:\Users\Eve\Downloads\校園選課專題_Codex移交包\campus-planner")
INPUT_MD = ROOT / "docs" / "第5週報告.md"
OUTPUT_PDF = ROOT / "docs" / "第5週報告.pdf"

font_candidates = [
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\msjh.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
    r"C:\Windows\Fonts\kaiu.ttc",
    r"C:\Windows\Fonts\simsun.ttc",
]
font_path = next((p for p in font_candidates if Path(p).exists()), None)
if font_path is None:
    raise FileNotFoundError("No Chinese font found in default Windows fonts.")

pdfmetrics.registerFont(TTFont("CustomCJK", font_path))
styles = getSampleStyleSheet()

def make_style(name: str, font_size: int, leading: int, space_after: int = 8, bold: bool = False):
    style = styles[name].clone("CustomStyle")
    style.fontName = "CustomCJK"
    style.fontSize = font_size
    style.leading = leading
    style.spaceAfter = space_after
    style.fontName = "CustomCJK"
    if bold:
        style.fontName = "CustomCJK"
    return style

normal = make_style("Normal", 11, 16, 8)
heading1 = make_style("Title", 22, 28, 18)
heading2 = make_style("Heading2", 15, 20, 10)

story = []
content = INPUT_MD.read_text(encoding="utf-8")
lines = content.splitlines()

for line in lines:
    stripped = line.strip()
    if not stripped:
        story.append(Spacer(1, 6))
        continue
    if line.startswith("# "):
        story.append(Paragraph(line[2:], heading1))
    elif line.startswith("## "):
        story.append(Paragraph(line[3:], heading2))
    elif line.startswith("### "):
        story.append(Paragraph(line[4:], heading2))
    elif line.startswith("- "):
        story.append(Paragraph(stripped, normal))
    else:
        story.append(Paragraph(stripped, normal))

pdf = SimpleDocTemplate(
    str(OUTPUT_PDF),
    pagesize=A4,
    leftMargin=20,
    rightMargin=20,
    topMargin=20,
    bottomMargin=20,
)
pdf.build(story)
print(f"Generated PDF: {OUTPUT_PDF}")
