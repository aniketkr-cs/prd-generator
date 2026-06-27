"""
utils/report_generator.py
---------------------------
Generates a clean, professional PDF version of the PRD using ReportLab.

IMPORTANT: even though the app's on-screen UI is a dark theme, the PDF
itself uses a WHITE background with dark text. This is intentional -
dark-background PDFs print badly and look unprofessional when shared
with stakeholders, so PRD documents always use a light, paper-style theme.
"""

import io
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    ListFlowable,
    ListItem,
    HRFlowable,
)

# ---------- Color palette for the PDF (light theme, NOT the app's dark theme) ----------
DARK_TEXT = colors.HexColor("#111111")
MUTED_TEXT = colors.HexColor("#555555")
ACCENT_GREEN = colors.HexColor("#16803c")  # slightly darker green for print contrast
LIGHT_BORDER = colors.HexColor("#dddddd")
LIGHT_FILL = colors.HexColor("#f5f5f5")

PRIORITY_COLORS = {
    "High": colors.HexColor("#b91c1c"),
    "Medium": colors.HexColor("#a16207"),
    "Low": colors.HexColor("#555555"),
}


def _build_styles():
    """Builds and returns a dict of all paragraph styles used in the PDF."""
    base = getSampleStyleSheet()
    styles = {}

    styles["DocTitle"] = ParagraphStyle(
        "DocTitle", parent=base["Title"],
        fontName="Helvetica-Bold", fontSize=22, leading=26,
        textColor=DARK_TEXT, spaceAfter=4,
    )
    styles["DocSubtitle"] = ParagraphStyle(
        "DocSubtitle", parent=base["Normal"],
        fontName="Helvetica", fontSize=10, leading=14,
        textColor=MUTED_TEXT, spaceAfter=18,
    )
    styles["SectionHeading"] = ParagraphStyle(
        "SectionHeading", parent=base["Heading2"],
        fontName="Helvetica-Bold", fontSize=13, leading=16,
        textColor=ACCENT_GREEN, spaceBefore=16, spaceAfter=8,
    )
    styles["Body"] = ParagraphStyle(
        "Body", parent=base["Normal"],
        fontName="Helvetica", fontSize=10, leading=15,
        textColor=DARK_TEXT, alignment=TA_LEFT,
    )
    styles["BodyMuted"] = ParagraphStyle(
        "BodyMuted", parent=base["Normal"],
        fontName="Helvetica-Oblique", fontSize=9.5, leading=14,
        textColor=MUTED_TEXT,
    )
    styles["BulletItem"] = ParagraphStyle(
        "BulletItem", parent=base["Normal"],
        fontName="Helvetica", fontSize=10, leading=14,
        textColor=DARK_TEXT,
    )
    styles["PersonaName"] = ParagraphStyle(
        "PersonaName", parent=base["Normal"],
        fontName="Helvetica-Bold", fontSize=11, leading=14,
        textColor=DARK_TEXT,
    )
    styles["PersonaRole"] = ParagraphStyle(
        "PersonaRole", parent=base["Normal"],
        fontName="Helvetica-Oblique", fontSize=9, leading=12,
        textColor=MUTED_TEXT, spaceAfter=4,
    )
    styles["StoryText"] = ParagraphStyle(
        "StoryText", parent=base["Normal"],
        fontName="Helvetica", fontSize=10, leading=14,
        textColor=DARK_TEXT,
    )
    styles["TableHeader"] = ParagraphStyle(
        "TableHeader", parent=base["Normal"],
        fontName="Helvetica-Bold", fontSize=9.5, leading=12,
        textColor=colors.white,
    )
    styles["TableCell"] = ParagraphStyle(
        "TableCell", parent=base["Normal"],
        fontName="Helvetica", fontSize=9.5, leading=13,
        textColor=DARK_TEXT,
    )
    return styles


def _section_divider():
    """A thin horizontal line used to visually separate sections."""
    return HRFlowable(width="100%", thickness=0.6, color=LIGHT_BORDER, spaceBefore=2, spaceAfter=10)


def generate_pdf(prd_data: dict, product_name: str) -> bytes:
    """
    Builds a full PDF report from the PRD data dict (the same dict returned
    by gemini_client.generate_prd) and returns it as raw bytes, ready to be
    handed to st.download_button.
    """
    buffer = io.BytesIO()
    styles = _build_styles()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        title=f"PRD - {product_name}",
    )

    elements = []

    # ---------- Title block ----------
    elements.append(Paragraph(f"Product Requirements Document", styles["DocTitle"]))
    elements.append(Paragraph(f"{product_name}", styles["DocSubtitle"]))
    elements.append(
        Paragraph(
            f"Generated on {datetime.now().strftime('%B %d, %Y')}",
            styles["BodyMuted"],
        )
    )
    elements.append(Spacer(1, 10))
    elements.append(_section_divider())

    # ---------- Executive Summary ----------
    elements.append(Paragraph("Executive Summary", styles["SectionHeading"]))
    elements.append(Paragraph(prd_data.get("executive_summary", ""), styles["Body"]))

    # ---------- Problem Statement ----------
    elements.append(Paragraph("Problem Statement", styles["SectionHeading"]))
    elements.append(Paragraph(prd_data.get("problem_statement", ""), styles["Body"]))

    # ---------- Goals ----------
    elements.append(Paragraph("Goals and Objectives", styles["SectionHeading"]))
    goal_items = [
        ListItem(Paragraph(goal, styles["BulletItem"]), leftIndent=8)
        for goal in prd_data.get("goals", [])
    ]
    elements.append(ListFlowable(goal_items, bulletType="1", start="1"))

    # ---------- Personas ----------
    elements.append(Paragraph("User Personas", styles["SectionHeading"]))
    for persona in prd_data.get("personas", []):
        elements.append(
            Paragraph(f"{persona.get('name', '')}", styles["PersonaName"])
        )
        elements.append(
            Paragraph(f"{persona.get('role', '')}", styles["PersonaRole"])
        )
        elements.append(Paragraph(f"<b>Description:</b> {persona.get('description', '')}", styles["Body"]))
        elements.append(Paragraph(f"<b>Needs:</b> {persona.get('needs', '')}", styles["Body"]))
        elements.append(Paragraph(f"<b>Pain Points:</b> {persona.get('pain_points', '')}", styles["Body"]))
        elements.append(Spacer(1, 8))

    # ---------- User Stories ----------
    elements.append(Paragraph("User Stories", styles["SectionHeading"]))
    story_items = []
    for story in prd_data.get("user_stories", []):
        text = (
            f"<b>As a</b> {story.get('as_a', '')}, "
            f"<b>I want</b> {story.get('i_want', '')}, "
            f"<b>so that</b> {story.get('so_that', '')}."
        )
        story_items.append(ListItem(Paragraph(text, styles["StoryText"]), leftIndent=8))
    elements.append(ListFlowable(story_items, bulletType="bullet"))

    # ---------- Feature List (table with priority) ----------
    elements.append(Paragraph("Feature List", styles["SectionHeading"]))
    feature_rows = [
        [
            Paragraph("Feature", styles["TableHeader"]),
            Paragraph("Description", styles["TableHeader"]),
            Paragraph("Priority", styles["TableHeader"]),
        ]
    ]
    for feature in prd_data.get("features", []):
        priority = feature.get("priority", "Medium")
        priority_color = PRIORITY_COLORS.get(priority, MUTED_TEXT)
        priority_style = ParagraphStyle(
            "PriorityCell", parent=styles["TableCell"],
            textColor=priority_color, fontName="Helvetica-Bold",
        )
        feature_rows.append([
            Paragraph(feature.get("name", ""), styles["TableCell"]),
            Paragraph(feature.get("description", ""), styles["TableCell"]),
            Paragraph(priority, priority_style),
        ])

    feature_table = Table(feature_rows, colWidths=[4.2 * cm, 9.3 * cm, 2.5 * cm])
    feature_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT_GREEN),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_FILL]),
        ("GRID", (0, 0), (-1, -1), 0.5, LIGHT_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(feature_table)
    elements.append(Spacer(1, 10))

    # ---------- Out of Scope ----------
    elements.append(Paragraph("Out of Scope", styles["SectionHeading"]))
    scope_items = [
        ListItem(Paragraph(item, styles["BulletItem"]), leftIndent=8)
        for item in prd_data.get("out_of_scope", [])
    ]
    elements.append(ListFlowable(scope_items, bulletType="bullet"))

    # ---------- Success Metrics ----------
    elements.append(Paragraph("Success Metrics", styles["SectionHeading"]))
    metric_items = [
        ListItem(Paragraph(item, styles["BulletItem"]), leftIndent=8)
        for item in prd_data.get("success_metrics", [])
    ]
    elements.append(ListFlowable(metric_items, bulletType="bullet"))

    # ---------- Timeline Estimate ----------
    elements.append(Paragraph("Timeline Estimate", styles["SectionHeading"]))
    elements.append(Paragraph(prd_data.get("timeline_estimate", ""), styles["Body"]))

    # ---------- Risks and Mitigation ----------
    elements.append(Paragraph("Risks and Mitigation", styles["SectionHeading"]))
    risk_rows = [
        [
            Paragraph("Risk", styles["TableHeader"]),
            Paragraph("Mitigation", styles["TableHeader"]),
        ]
    ]
    for risk in prd_data.get("risks", []):
        risk_rows.append([
            Paragraph(risk.get("risk", ""), styles["TableCell"]),
            Paragraph(risk.get("mitigation", ""), styles["TableCell"]),
        ])
    risk_table = Table(risk_rows, colWidths=[7.5 * cm, 8.5 * cm])
    risk_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT_GREEN),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_FILL]),
        ("GRID", (0, 0), (-1, -1), 0.5, LIGHT_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(risk_table)

    # ---------- Footer note ----------
    elements.append(Spacer(1, 16))
    elements.append(_section_divider())
    elements.append(
        Paragraph(
            "Generated with PRD Generator - AI-assisted draft. Review and edit before sharing with stakeholders.",
            styles["BodyMuted"],
        )
    )

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
