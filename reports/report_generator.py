"""
reports/report_generator.py — Utilities for persisting AI-generated reports.
"""
import os
from datetime import datetime
from fpdf import FPDF


# ── Colours for PDF ──────────────────────────────────────────────
_PDF_ACCENT = (55, 65, 185)
_PDF_DARK = (30, 30, 30)
_PDF_MUTED = (120, 120, 120)
_PDF_BG = (248, 249, 252)


def save_report(report_text: str, mode: str = "detailed", output_dir: str = "reports") -> str:
    """
    Save *report_text* to a timestamped Markdown file inside *output_dir*.

    - mode is used to prefix the filename (summary_ or detailed_)
    Returns the absolute path of the saved file.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{mode}_report_{timestamp}.md"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report_text)
    return os.path.abspath(filepath)


def generate_pdf(report_text: str, mode: str = "detailed") -> bytes:
    """Convert a markdown report (bold headers + bullet points) to a professional PDF."""

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=24)

    # ── Title page ──────────────────────────────────────────────
    pdf.add_page()
    pdf.set_fill_color(*_PDF_ACCENT)
    pdf.rect(0, 0, 210, 80, "F")
    pdf.set_y(22)
    pdf.set_font("Helvetica", "B", 26)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 14, "Business Analysis Report", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 14)
    pdf.cell(0, 10, ("Summary" if mode == "summary" else "Detailed"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(210, 215, 240)
    pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}", align="C", new_x="LMARGIN", new_y="NEXT")

    # ── Content pages ───────────────────────────────────────────
    pdf.add_page()
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*_PDF_DARK)

    lines = report_text.strip().split("\n")
    first = True

    for line in lines:
        stripped = line.strip()

        if not stripped:
            pdf.ln(3)
            continue

        # Bold section header: **HEADER**
        if stripped.startswith("**") and stripped.endswith("**"):
            header = stripped.strip("*").strip()
            if first:
                first = False
            else:
                pdf.ln(4)
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(*_PDF_ACCENT)
            pdf.cell(0, 8, header, new_x="LMARGIN", new_y="NEXT")
            pdf.set_draw_color(*_PDF_ACCENT)
            pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 60, pdf.get_y())
            pdf.ln(3)
            continue

        # Bullet point: - text
        if stripped.startswith("- "):
            text = stripped[2:]
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(*_PDF_DARK)
            # Wrap text
            x0 = pdf.get_x() + 5
            pdf.set_x(x0)
            pdf.cell(4, 5, "-", new_x="END")
            pdf.multi_cell(0, 5, text, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
            continue

        # Plain text fallback
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*_PDF_MUTED)
        pdf.multi_cell(0, 5, stripped, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

    return pdf.output()
