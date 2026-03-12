from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer


def create_pdf_bytes(title: str, report_text: str, branding_line: str = "Excelsior Certification"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=48,
        rightMargin=48,
        topMargin=54,
        bottomMargin=48,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        spaceAfter=8,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#102542"),
    )
    brand_style = ParagraphStyle(
        "BrandStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        textColor=colors.HexColor("#667085"),
        spaceAfter=14,
    )
    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12.5,
        textColor=colors.HexColor("#175CD3"),
        spaceBefore=10,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#101828"),
    )
    bullet_para_style = ParagraphStyle(
        "BulletPara",
        parent=body_style,
        leftIndent=0,
        spaceBefore=0,
        spaceAfter=0,
    )

    story = [
        Paragraph(title, title_style),
        Paragraph(
            f"{branding_line} &nbsp;&nbsp;|&nbsp;&nbsp; Generated: {datetime.utcnow().strftime('%Y-%m-%d')}",
            brand_style,
        ),
    ]

    lines = [ln.rstrip() for ln in report_text.split("\n")]
    sections = []
    current_heading = None
    current_bullets = []
    current_paras = []

    def flush():
        nonlocal current_heading, current_bullets, current_paras
        if current_heading:
            sections.append((current_heading, current_bullets[:], current_paras[:]))
        current_heading = None
        current_bullets = []
        current_paras = []

    for ln in lines:
        if not ln.strip():
            continue

        is_numbered_heading = len(ln) > 2 and ln[0].isdigit() and ln[1:3] == ") "
        is_colon_heading = ln.endswith(":") and len(ln) < 80

        if is_numbered_heading or is_colon_heading:
            flush()
            current_heading = ln.split(") ", 1)[1].strip() if is_numbered_heading else ln[:-1].strip()
            continue

        if ln.lstrip().startswith(("-", "•", "*")):
            bullet = ln.lstrip()[1:].strip()
            if bullet:
                current_bullets.append(bullet)
            continue

        current_paras.append(ln.strip())

    flush()

    for heading, bullets, paras in sections:
        story.append(Paragraph(heading, heading_style))
        for p in paras:
            story.append(Paragraph(p, body_style))
            story.append(Spacer(1, 6))

        if bullets:
            items = [ListItem(Paragraph(b, bullet_para_style), leftIndent=14) for b in bullets]
            story.append(
                ListFlowable(
                    items,
                    bulletType="bullet",
                    bulletFontName="Helvetica",
                    bulletFontSize=10,
                    bulletColor=colors.HexColor("#101828"),
                    leftIndent=16,
                )
            )
            story.append(Spacer(1, 10))

    story.append(Spacer(1, 8))
    story.append(
        Paragraph(
            "Disclaimer: This report is informational and does not guarantee outcomes.",
            ParagraphStyle(
                "Disclaimer",
                parent=styles["Normal"],
                fontSize=9,
                textColor=colors.HexColor("#667085"),
                spaceBefore=10,
            ),
        )
    )

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()