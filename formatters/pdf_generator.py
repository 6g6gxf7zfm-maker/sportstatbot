"""
PDF Generator for SportStatBot
Creates end-of-week summary booklets and formatted PDF reports
"""

import os
from datetime import datetime
from typing import Dict, List, Optional
import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration


class PDFGenerator:
    """Generate PDF reports from markdown content"""

    def __init__(self, output_dir: str = "reports/pdf"):
        """Initialize PDF generator"""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Custom CSS for PDF styling
        self.base_css = """
        @page {
            size: letter;
            margin: 1in;
            @top-center {
                content: "SportStatBot Report";
                font-family: Arial, sans-serif;
                font-size: 10pt;
                color: #666;
            }
            @bottom-center {
                content: counter(page);
                font-family: Arial, sans-serif;
                font-size: 10pt;
            }
        }

        body {
            font-family: 'Georgia', 'Times New Roman', serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
        }

        h1 {
            color: #1a1a1a;
            font-size: 24pt;
            font-weight: bold;
            margin-top: 0;
            margin-bottom: 20pt;
            border-bottom: 3pt solid #2c3e50;
            padding-bottom: 10pt;
        }

        h2 {
            color: #2c3e50;
            font-size: 18pt;
            font-weight: bold;
            margin-top: 20pt;
            margin-bottom: 12pt;
            border-bottom: 1pt solid #95a5a6;
            padding-bottom: 5pt;
        }

        h3 {
            color: #34495e;
            font-size: 14pt;
            font-weight: bold;
            margin-top: 15pt;
            margin-bottom: 8pt;
        }

        p {
            margin: 0 0 10pt 0;
            text-align: justify;
        }

        ul, ol {
            margin: 10pt 0;
            padding-left: 25pt;
        }

        li {
            margin-bottom: 5pt;
        }

        strong {
            font-weight: bold;
            color: #2c3e50;
        }

        em {
            font-style: italic;
            color: #555;
        }

        code {
            font-family: 'Courier New', monospace;
            background-color: #f5f5f5;
            padding: 2pt 4pt;
            border-radius: 3pt;
        }

        pre {
            background-color: #f8f8f8;
            border: 1pt solid #ddd;
            border-radius: 4pt;
            padding: 10pt;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 9pt;
        }

        blockquote {
            margin: 15pt 0;
            padding: 10pt 20pt;
            background-color: #f9f9f9;
            border-left: 4pt solid #2c3e50;
            font-style: italic;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15pt 0;
        }

        th {
            background-color: #2c3e50;
            color: white;
            font-weight: bold;
            padding: 8pt;
            text-align: left;
        }

        td {
            padding: 8pt;
            border-bottom: 1pt solid #ddd;
        }

        tr:nth-child(even) {
            background-color: #f9f9f9;
        }

        img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 15pt auto;
        }

        hr {
            border: none;
            border-top: 2pt solid #95a5a6;
            margin: 20pt 0;
        }

        .cover-page {
            text-align: center;
            page-break-after: always;
        }

        .cover-title {
            font-size: 36pt;
            font-weight: bold;
            margin-top: 200pt;
            color: #2c3e50;
        }

        .cover-subtitle {
            font-size: 18pt;
            margin-top: 20pt;
            color: #7f8c8d;
        }

        .cover-date {
            font-size: 14pt;
            margin-top: 30pt;
            color: #95a5a6;
        }

        .sport-section {
            page-break-before: always;
        }

        .toc {
            page-break-after: always;
        }

        .toc-item {
            margin: 10pt 0;
            font-size: 12pt;
        }

        .credits {
            margin-top: 30pt;
            padding-top: 20pt;
            border-top: 1pt solid #ddd;
            font-size: 9pt;
            color: #777;
        }
        """

        # Theme-specific CSS
        self.theme_css = {
            'espn': """
                h1, h2 { color: #c8102e; }
                h2 { border-bottom-color: #c8102e; }
                strong { color: #c8102e; }
            """,
            'athletic': """
                h1, h2 { color: #1a1a1a; }
                body { font-family: 'Helvetica', 'Arial', sans-serif; }
                strong { color: #000; }
            """,
            '538': """
                h1, h2 { color: #000; font-family: 'Arial', sans-serif; }
                body { font-family: 'Arial', sans-serif; }
                strong { color: #000; }
            """,
            'bleacher': """
                h1, h2 { color: #ff6c00; }
                h2 { border-bottom-color: #ff6c00; }
                strong { color: #ff6c00; }
            """
        }

    def markdown_to_pdf(
        self,
        markdown_content: str,
        output_filename: str,
        title: str = "Sports Report",
        theme: str = 'espn',
        include_cover: bool = True
    ) -> str:
        """Convert markdown content to PDF"""
        # Convert markdown to HTML
        html_content = markdown.markdown(
            markdown_content,
            extensions=[
                'markdown.extensions.tables',
                'markdown.extensions.fenced_code',
                'markdown.extensions.codehilite',
                'markdown.extensions.nl2br',
                'markdown.extensions.sane_lists'
            ]
        )

        # Build full HTML document
        full_html = self._build_html_document(
            html_content,
            title,
            theme,
            include_cover
        )

        # Generate PDF
        output_path = os.path.join(self.output_dir, output_filename)

        font_config = FontConfiguration()
        css_string = self.base_css + self.theme_css.get(theme, '')
        css = CSS(string=css_string, font_config=font_config)

        HTML(string=full_html).write_pdf(
            output_path,
            stylesheets=[css],
            font_config=font_config
        )

        return output_path

    def _build_html_document(
        self,
        content: str,
        title: str,
        theme: str,
        include_cover: bool
    ) -> str:
        """Build complete HTML document"""
        html = "<!DOCTYPE html>\n<html>\n<head>\n"
        html += f"<title>{title}</title>\n"
        html += '<meta charset="utf-8">\n'
        html += "</head>\n<body>\n"

        # Cover page
        if include_cover:
            html += '<div class="cover-page">\n'
            html += f'<div class="cover-title">{title}</div>\n'
            html += '<div class="cover-subtitle">Comprehensive Sports Analysis</div>\n'
            html += f'<div class="cover-date">{datetime.now().strftime("%B %d, %Y")}</div>\n'
            html += '</div>\n'

        # Content
        html += content

        html += "\n</body>\n</html>"
        return html

    def generate_weekly_booklet(
        self,
        reports: List[Dict],
        week_start: datetime,
        week_end: datetime,
        theme: str = 'espn'
    ) -> str:
        """Generate a weekly summary booklet PDF"""
        # Build booklet content
        booklet_md = self._build_weekly_booklet_markdown(reports, week_start, week_end)

        # Generate filename
        filename = f"weekly_booklet_{week_start.strftime('%Y%m%d')}-{week_end.strftime('%Y%m%d')}.pdf"

        # Create PDF
        title = f"Weekly Sports Digest: {week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}"

        return self.markdown_to_pdf(
            booklet_md,
            filename,
            title=title,
            theme=theme,
            include_cover=True
        )

    def _build_weekly_booklet_markdown(
        self,
        reports: List[Dict],
        week_start: datetime,
        week_end: datetime
    ) -> str:
        """Build markdown content for weekly booklet"""
        md = f"# Weekly Sports Digest\n\n"
        md += f"## {week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}\n\n"
        md += "---\n\n"

        # Table of contents
        md += "## Table of Contents\n\n"
        for i, report in enumerate(reports, 1):
            date = report.get('date', 'Unknown Date')
            md += f"{i}. Daily Report — {date}\n"
        md += "\n---\n\n"

        # Add each daily report
        for i, report in enumerate(reports, 1):
            date = report.get('date', 'Unknown Date')
            content = report.get('content', '')

            md += f'<div class="sport-section">\n\n'
            md += f"# Day {i}: {date}\n\n"
            md += content
            md += "\n\n</div>\n\n"

        # Week summary
        md += self._generate_week_summary(reports)

        return md

    def _generate_week_summary(self, reports: List[Dict]) -> str:
        """Generate a summary section for the week"""
        summary = "---\n\n"
        summary += "# Week in Review\n\n"
        summary += "## Key Takeaways\n\n"

        # Extract top stories (simplified)
        summary += "- Major storylines and trends from the week\n"
        summary += "- Notable performances and upsets\n"
        summary += "- Looking ahead to next week\n\n"

        summary += f"*Compiled on {datetime.now().strftime('%B %d, %Y')}*\n"

        return summary

    def generate_single_sport_pdf(
        self,
        sport: str,
        content: str,
        date: str = None,
        include_charts: List[str] = None
    ) -> str:
        """Generate a PDF for a single sport report"""
        if date is None:
            date = datetime.now().strftime('%B %d, %Y')

        # Add chart references
        md_content = content

        if include_charts:
            md_content += "\n\n## Visual Analysis\n\n"
            for chart_path in include_charts:
                if os.path.exists(chart_path):
                    md_content += f"![Chart]({chart_path})\n\n"

        # Generate filename
        filename = f"{sport}_report_{datetime.now().strftime('%Y%m%d')}.pdf"
        title = f"{sport.upper()} Report - {date}"

        return self.markdown_to_pdf(
            md_content,
            filename,
            title=title,
            include_cover=False
        )

    def compile_multiple_reports_to_pdf(
        self,
        report_files: List[str],
        output_filename: str,
        title: str = "Sports Reports Compilation"
    ) -> str:
        """Compile multiple markdown reports into a single PDF"""
        combined_md = ""

        for report_file in report_files:
            if os.path.exists(report_file):
                with open(report_file, 'r', encoding='utf-8') as f:
                    combined_md += f.read()
                    combined_md += "\n\n---\n\n"

        return self.markdown_to_pdf(
            combined_md,
            output_filename,
            title=title,
            include_cover=True
        )

    def add_custom_css(self, css_string: str):
        """Add custom CSS to the base styles"""
        self.base_css += "\n" + css_string

    def set_page_size(self, size: str = "letter"):
        """Set PDF page size (letter, legal, a4, etc.)"""
        size_map = {
            'letter': 'letter',
            'legal': 'legal',
            'a4': 'A4',
            'a3': 'A3'
        }
        page_size = size_map.get(size.lower(), 'letter')

        # Update CSS
        self.base_css = self.base_css.replace(
            'size: letter;',
            f'size: {page_size};'
        )
