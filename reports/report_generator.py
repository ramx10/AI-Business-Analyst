"""
reports/report_generator.py — Utilities for persisting AI-generated reports.
"""
import os
from datetime import datetime


def save_report(report_text: str, output_dir: str = "reports") -> str:
    """
    Save *report_text* to a timestamped Markdown file inside *output_dir*.

    Returns the absolute path of the saved file.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{timestamp}.md"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report_text)
    return os.path.abspath(filepath)
