# summarizer/render.py
# HTML renderer and asset embedding logic for summarization reports.

from pathlib import Path
from typing import Dict
from datetime import datetime

def render_markdown_report(narrative_sections: Dict[str, str], output_path: Path) -> Path:
    """
    Assemble full Markdown report from narrative sections and write to file.
    """
    header = "# AutoStat-Agent Report\n\n"
    header += f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    body = "\n".join(narrative_sections.values())
    full_report = header + body

    output_path.write_text(full_report)
    return output_path

def render_html_from_markdown(markdown_path: Path, html_path: Path) -> Path:
    """
    Convert Markdown to HTML with basic styling.
    """
    import markdown

    md_text = markdown_path.read_text()
    html_content = markdown.markdown(md_text, extensions=["fenced_code", "tables"])

    full_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>AutoStat-Agent Report</title>
  <style>
    body {{ font-family: sans-serif; margin: 2em; line-height: 1.6; }}
    pre {{ background: #f5f5f5; padding: 1em; overflow-x: auto; }}
    img {{ max-width: 100%; height: auto; margin: 1em 0; }}
    h2, h3 {{ margin-top: 2em; }}
  </style>
</head>
<body>
{html_content}
</body>
</html>"""

    html_path.write_text(full_html)
    return html_path
