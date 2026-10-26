from pathlib import Path
import re
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfgen.canvas import Canvas

root = Path(__file__).parent
sources = [root / 'The_Price_of_Marble_Chapter_01.md', root / 'The_Price_of_Marble_Chapter_02.md']
out = root / 'output' / 'The_Price_of_Marble_Expanded_Chapters_01-02.pdf'
out.parent.mkdir(exist_ok=True)
pdfmetrics.registerFont(TTFont('Book', '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'))
pdfmetrics.registerFont(TTFont('Book-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'))
W, H = A5

def decorate(c: Canvas, doc):
    c.saveState()
    if c.getPageNumber() > 1:
        c.setStrokeColor(colors.HexColor('#c9c0b1'))
        c.setLineWidth(.45)
        c.line(20*mm, 15*mm, W-20*mm, 15*mm)
        c.setFont('Book', 8)
        c.setFillColor(colors.HexColor('#71695f'))
        c.drawString(20*mm, 10.5*mm, 'THE PRICE OF MARBLE')
        c.drawRightString(W-20*mm, 10.5*mm, str(c.getPageNumber()-1))
    c.restoreState()

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Cover', fontName='Book-Bold', fontSize=26, leading=33, alignment=TA_CENTER, textColor=colors.HexColor('#302a23')))
styles.add(ParagraphStyle(name='Sub', fontName='Book', fontSize=11, leading=17, alignment=TA_CENTER, textColor=colors.HexColor('#756650')))
styles.add(ParagraphStyle(name='Chapter', fontName='Book-Bold', fontSize=17, leading=23, alignment=TA_CENTER, textColor=colors.HexColor('#342d25'), spaceAfter=18))
styles.add(ParagraphStyle(name='Scene', fontName='Book-Bold', fontSize=10, leading=14, alignment=TA_CENTER, textColor=colors.HexColor('#8c6d43'), spaceBefore=8, spaceAfter=10))
styles.add(ParagraphStyle(name='BodyNovel', fontName='Book', fontSize=9.3, leading=14.1, alignment=TA_JUSTIFY, firstLineIndent=5*mm, spaceAfter=7, textColor=colors.HexColor('#24211e'), allowWidows=0, allowOrphans=0))

story = [Spacer(1, 43*mm), Paragraph('THE PRICE<br/>OF MARBLE', styles['Cover']), Spacer(1, 6*mm),
         Paragraph('A HISTORICAL NOVEL', styles['Sub']), Spacer(1, 18*mm),
         Paragraph('ROME  ·  AD 112', styles['Sub']), Spacer(1, 26*mm),
         Paragraph('MATURE / 18+', styles['Sub']), Spacer(1, 10*mm),
         Paragraph('EXPANDED CHAPTERS I–II', styles['Sub']), PageBreak()]
word_count = 0
chapter_seen = False
for source in sources:
    raw = source.read_text(encoding='utf-8')
    word_count += len(re.findall(r"\b[\w’'-]+\b", raw))
    buf = []
    def flush():
        if buf:
            story.append(Paragraph(' '.join(buf), styles['BodyNovel']))
            buf.clear()
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith('# Chapter '):
            flush()
            if chapter_seen:
                story.append(PageBreak())
            chapter_seen = True
            story.extend([Spacer(1, 12*mm), Paragraph(line[2:].replace('&', '&amp;'), styles['Chapter'])])
        elif line.startswith('## Scene '):
            flush()
            story.append(Paragraph(line[3:], styles['Scene']))
        elif not line or line == '---' or line.startswith('# THE PRICE') or line.startswith('### A Historical') or line.startswith('*Rome,') or line.startswith('*End*'):
            flush()
        else:
            buf.append(line.replace('&', '&amp;'))
    flush()

doc = SimpleDocTemplate(str(out), pagesize=A5, rightMargin=20*mm, leftMargin=20*mm, topMargin=20*mm, bottomMargin=22*mm, title='The Price of Marble — Expanded Chapters I–II', author='Historical Novel')
doc.build(story, onFirstPage=decorate, onLaterPages=decorate)
print(f'{out} | manuscript_words={word_count} | bytes={out.stat().st_size}')
