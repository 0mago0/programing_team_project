from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import getSampleStyleSheet

ROOT = Path(r"c:\Users\Eve\Downloads\校園選課專題_Codex移交包\campus-planner")
SRC = ROOT / "docs" / "第5週報告_正式版.md"
OUT = ROOT / "docs" / "第5週報告_正式版.pdf"

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

h1 = styles['Title'].clone('H1')
h1.fontName = 'CustomCJK'
h1.fontSize = 22
h1.leading = 28
h1.spaceAfter = 16

h2 = styles['Heading2'].clone('H2')
h2.fontName = 'CustomCJK'
h2.fontSize = 15
h2.leading = 20
h2.spaceBefore = 12
h2.spaceAfter = 8

body = styles['Normal'].clone('Body')
body.fontName = 'CustomCJK'
body.fontSize = 11
body.leading = 16
body.spaceAfter = 8

story = []
for line in SRC.read_text(encoding='utf-8').splitlines():
    stripped = line.strip()
    if not stripped:
        story.append(Spacer(1, 6))
        continue
    if line.startswith('# '):
        story.append(Paragraph(line[2:], h1))
    elif line.startswith('## '):
        story.append(Paragraph(line[3:], h2))
    elif line.startswith('### '):
        story.append(Paragraph(line[4:], h2))
    elif line.startswith('- '):
        story.append(Paragraph(stripped, body))
    else:
        story.append(Paragraph(stripped, body))

pdf = SimpleDocTemplate(
    str(OUT),
    pagesize=A4,
    leftMargin=20,
    rightMargin=20,
    topMargin=20,
    bottomMargin=20,
)
pdf.build(story)
print(f"PDF created: {OUT}")
