"""
Generate a properly-formatted screenplay PDF from the production draft text.
Requires: pip install reportlab
"""

import os
import sys

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.pdfgen import canvas
except ImportError:
    print("reportlab not installed. Run: pip install reportlab")
    sys.exit(1)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_TXT = os.path.join(SCRIPT_DIR, "the_golden_hour_production_draft.txt")
OUTPUT_PDF = os.path.join(SCRIPT_DIR, "the_golden_hour.pdf")

# Courier 12pt, 1.5" left, 1" right, 1" top/bottom — standard screenplay margins
PAGE_W, PAGE_H = letter   # 8.5 x 11 inches
MARGIN_LEFT   = 1.5 * inch
MARGIN_RIGHT  = 1.0 * inch
MARGIN_TOP    = 1.0 * inch
MARGIN_BOTTOM = 1.0 * inch


def build_pdf(source_txt: str, output_pdf: str) -> None:
    with open(source_txt, "r", encoding="utf-8") as f:
        lines = f.readlines()

    c = canvas.Canvas(output_pdf, pagesize=letter)
    c.setFont("Courier", 12)

    x = MARGIN_LEFT
    y = PAGE_H - MARGIN_TOP
    line_height = 14   # 12pt font + 2pt leading
    page_num = 1

    def new_page():
        nonlocal y, page_num
        # Page number top-right
        c.setFont("Courier", 12)
        c.drawRightString(PAGE_W - MARGIN_RIGHT, PAGE_H - 0.6 * inch,
                          f"{page_num}.")
        c.showPage()
        c.setFont("Courier", 12)
        page_num += 1
        y = PAGE_H - MARGIN_TOP

    for raw_line in lines:
        line = raw_line.rstrip("\n")

        # Force new page on separator lines (===)
        if line.startswith("===="):
            if y < PAGE_H - MARGIN_TOP:  # don't add blank page at top
                new_page()
            continue

        # Draw the line
        if y < MARGIN_BOTTOM + line_height:
            new_page()

        c.drawString(x, y, line)
        y -= line_height

    # Final page number
    c.setFont("Courier", 12)
    c.drawRightString(PAGE_W - MARGIN_RIGHT, PAGE_H - 0.6 * inch, f"{page_num}.")
    c.save()
    print(f"PDF written: {output_pdf}")


if __name__ == "__main__":
    build_pdf(SOURCE_TXT, OUTPUT_PDF)
