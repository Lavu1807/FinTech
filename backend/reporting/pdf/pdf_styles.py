from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import TableStyle

# Colors
BRAND_DARK = colors.HexColor("#0f172a")
BRAND_ACCENT = colors.HexColor("#3b82f6")
BRAND_TEXT = colors.HexColor("#334155")
BRAND_LIGHT_BG = colors.HexColor("#f8fafc")
BRAND_GREEN = colors.HexColor("#10b981")
BRAND_RED = colors.HexColor("#ef4444")
BRAND_YELLOW = colors.HexColor("#f59e0b")


def get_styles():
    styles = getSampleStyleSheet()

    # Title Page
    styles.add(
        ParagraphStyle(
            name="CoverTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=36,
            textColor=BRAND_DARK,
            alignment=TA_CENTER,
            spaceAfter=30,
        )
    )

    styles.add(
        ParagraphStyle(
            name="CoverSubtitle",
            parent=styles["Heading2"],
            fontName="Helvetica",
            fontSize=20,
            textColor=BRAND_TEXT,
            alignment=TA_CENTER,
            spaceAfter=50,
        )
    )

    # Headings
    styles.add(
        ParagraphStyle(
            name="SectionTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=24,
            textColor=BRAND_DARK,
            spaceBefore=20,
            spaceAfter=15,
            borderColor=BRAND_ACCENT,
            borderWidth=0,
            borderPadding=0,
        )
    )

    styles.add(
        ParagraphStyle(
            name="SubsectionTitle",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=16,
            textColor=BRAND_DARK,
            spaceBefore=15,
            spaceAfter=10,
        )
    )

    # Body Text
    styles.add(
        ParagraphStyle(
            name="BodyTextCustom",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            textColor=BRAND_TEXT,
            leading=16,
            spaceBefore=6,
            spaceAfter=6,
        )
    )

    # Bullet Lists
    styles.add(
        ParagraphStyle(
            name="BulletCustom",
            parent=styles["BodyTextCustom"],
            leftIndent=20,
            bulletIndent=10,
        )
    )

    # Highlight/Cards
    styles.add(
        ParagraphStyle(
            name="CardTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=12,
            textColor=BRAND_DARK,
            spaceAfter=4,
        )
    )

    styles.add(
        ParagraphStyle(
            name="CardText",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            textColor=BRAND_TEXT,
            leading=14,
        )
    )

    return styles


def get_table_style():
    """Default professional table style"""
    return TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), BRAND_DARK),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, 0), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 12),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("TOPPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), BRAND_LIGHT_BG),
            ("TEXTCOLOR", (0, 1), (-1, -1), BRAND_TEXT),
            ("ALIGN", (0, 1), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
            ("TOPPADDING", (0, 1), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 1, colors.white),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BRAND_LIGHT_BG]),
        ]
    )


def get_kpi_grid_style():
    """Style for KPI boxes"""
    return TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, -1), BRAND_LIGHT_BG),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 16),
            ("TEXTCOLOR", (0, 0), (-1, -1), BRAND_ACCENT),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
            ("TOPPADDING", (0, 0), (-1, -1), 20),
            ("BOX", (0, 0), (-1, -1), 1, BRAND_ACCENT),
            ("INNERGRID", (0, 0), (-1, -1), 1, colors.white),
        ]
    )
