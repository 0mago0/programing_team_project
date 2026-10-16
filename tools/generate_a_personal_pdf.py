import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import HRFlowable, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

root = Path(__file__).resolve().parents[1]
md_path = root / 'docs' / '04_個人紀錄' / '成員A' / '第5週_個人紀錄.md'
out_path = root / 'docs' / '04_個人紀錄' / '成員A' / '第5週_個人紀錄.pdf'

font_candidates = [
    r'C:\Windows\Fonts\msyh.ttc',
    r'C:\Windows\Fonts\mingliu.ttc',
    r'C:\Windows\Fonts\simhei.ttf',
]
font_path = next((p for p in font_candidates if Path(p).exists()), None)
if font_path is None:
    raise FileNotFoundError('No valid Chinese font found in Windows fonts directory.')

pdfmetrics.registerFont(TTFont('MSYH', font_path))
styles = getSampleStyleSheet()

cover_title = ParagraphStyle(
    'CoverTitle',
    parent=styles['Title'],
    fontName='MSYH',
    fontSize=28,
    leading=34,
    alignment=1,
    textColor='#123B63',
    spaceAfter=10,
)
cover_subtitle = ParagraphStyle(
    'CoverSubtitle',
    parent=styles['Title'],
    fontName='MSYH',
    fontSize=20,
    leading=26,
    alignment=1,
    textColor='#1F2937',
    spaceAfter=8,
)
cover_role = ParagraphStyle(
    'CoverRole',
    parent=styles['BodyText'],
    fontName='MSYH',
    fontSize=12,
    leading=18,
    alignment=1,
    textColor='#4b5563',
    spaceAfter=16,
)
section = ParagraphStyle(
    'Section',
    parent=styles['Heading2'],
    fontName='MSYH',
    fontSize=15,
    leading=20,
    textColor='#0F172A',
    spaceBefore=14,
    spaceAfter=8,
    borderPadding=6,
)
body = ParagraphStyle(
    'Body',
    parent=styles['BodyText'],
    fontName='MSYH',
    fontSize=11.5,
    leading=19,
    spaceAfter=6,
    textColor='#222222',
)
bullet = ParagraphStyle(
    'Bullet',
    parent=body,
    leftIndent=18,
    firstLineIndent=-6,
    bulletIndent=8,
)


def make_table(data):
    if not data:
        return None
    table = Table(data, colWidths=[150, 380])
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1D4E89')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'MSYH'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTNAME', (0, 1), (-1, -1), 'MSYH'),
        ('FONTSIZE', (0, 1), (-1, -1), 10.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F8FAFC'), colors.HexColor('#EEF6FF')]),
        ('GRID', (0, 0), (-1, -1), 0.7, colors.HexColor('#B6C5D8')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ])
    table.setStyle(table_style)
    return table


story = []

lines = md_path.read_text(encoding='utf-8').splitlines()
current_table = []

def flush_table():
    global current_table
    if current_table:
        table = make_table(current_table)
        if table is not None:
            story.append(Spacer(1, 10))
            story.append(table)
            story.append(Spacer(1, 10))
        current_table = []

for raw_line in lines:
    line = raw_line.rstrip()
    stripped = line.strip()

    if stripped.startswith('# '):
        flush_table()
        if story and story[-1].__class__.__name__ != 'PageBreak':
            story.append(HRFlowable(width='100%', thickness=1.2, color='#D4DCE6', spaceBefore=8, spaceAfter=8))
        story.append(Paragraph(stripped[2:], section))
        continue

    if stripped.startswith('## '):
        flush_table()
        story.append(HRFlowable(width='100%', thickness=1.2, color='#D4DCE6', spaceBefore=8, spaceAfter=8))
        story.append(Paragraph(stripped[3:], section))
        continue

    if stripped.startswith('### '):
        flush_table()
        story.append(Paragraph(stripped[4:], ParagraphStyle('Subhead', parent=section, fontSize=12, leading=18, spaceBefore=6, spaceAfter=6, textColor='#334155')))
        continue

    if stripped.startswith('|'):
        cells = [cell.strip() for cell in stripped.strip('|').split('|')]
        if len(cells) >= 2 and not re.fullmatch(r':?-{3,}:?', cells[0].strip()) and not re.fullmatch(r':?-{3,}:?', cells[1].strip()):
            current_table.append(cells)
        continue

    if stripped == '---':
        flush_table()
        story.append(HRFlowable(width='100%', thickness=1.2, color='#9DB9C8', spaceBefore=8, spaceAfter=8))
        continue

    if stripped.startswith('- '):
        flush_table()
        story.append(Paragraph(stripped[2:], bullet))
        continue

    if re.match(r'^[0-9]+\.\s', stripped):
        flush_table()
        story.append(Paragraph(stripped, body))
        continue

    if stripped == '':
        flush_table()
        story.append(Spacer(1, 6))
        continue

    flush_table()
    story.append(Paragraph(stripped, body))

flush_table()

doc = SimpleDocTemplate(
    str(out_path),
    pagesize=A4,
    leftMargin=48,
    rightMargin=48,
    topMargin=42,
    bottomMargin=42,
)
doc.build(story)
print(f'Generated PDF: {out_path}')
