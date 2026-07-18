from pathlib import Path
from reportlab.platypus import Image, Spacer, Paragraph
from backend.utils.logger import logger
from .pdf_styles import get_styles


def build_charts_section(chart_paths: list) -> list:
    """Takes a list of file paths to PNGs, returns a list of ReportLab Image objects scaled to fit the page."""
    story = []
    styles = get_styles()

    if not chart_paths:
        story.append(Paragraph("No charts were generated.", styles["BodyTextCustom"]))
        return story

    for path_str in chart_paths:
        p = Path(path_str)
        if p.exists() and p.suffix.lower() == ".png":
            try:
                # Max width for A4 page with margins is ~450
                MAX_WIDTH = 450
                MAX_HEIGHT = 300

                # Title
                title_text = p.stem.replace("_", " ").title()
                story.append(Paragraph(title_text, styles["SubsectionTitle"]))

                # Load image
                img = Image(str(p))

                # Calculate scale
                aspect = img.imageWidth / float(img.imageHeight)

                if img.imageWidth > MAX_WIDTH:
                    img.drawWidth = MAX_WIDTH
                    img.drawHeight = MAX_WIDTH / aspect

                if img.drawHeight > MAX_HEIGHT:
                    img.drawHeight = MAX_HEIGHT
                    img.drawWidth = MAX_HEIGHT * aspect

                story.append(img)
                story.append(Spacer(1, 20))

            except Exception as e:
                logger.error(f"Failed to embed chart {p.name}: {e}")
                story.append(
                    Paragraph(
                        f"[Error loading chart: {p.name}]", styles["BodyTextCustom"]
                    )
                )

    return story
