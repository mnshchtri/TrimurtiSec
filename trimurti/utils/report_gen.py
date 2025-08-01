import markdown
from datetime import datetime
import os
import tempfile
import json
from jinja2 import Template
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas

class ReportGenerator:
    def __init__(self, target=None):
        self.sections = []
        self.timestamp = datetime.now()
        self.target = target or "Unknown Target"
        self.logo_path = None
        
    def add_section(self, title, content):
        self.sections.append({
            "title": title,
            "content": content
        })
    
    def set_target(self, target):
        """Set the target for the report"""
        self.target = target
    
    def generate(self, output_file):
        """Generate a report in the specified format based on file extension"""
        file_ext = os.path.splitext(output_file)[1].lower()
        
        if file_ext == '.pdf':
            return self._generate_pdf_reportlab(output_file)
        elif file_ext == '.html':
            return self._generate_html(output_file)
        else:
            return self._generate_markdown(output_file)
    
    def _generate_markdown(self, output_file):
        """Generate a markdown report with a table of contents"""
        report = f"""# TrimurtiSec Penetration Test Report
Generated on: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
Target: {self.target}

## Executive Summary
This report was generated using the TrimurtiSec Advanced Penetration Testing Framework.

"""
        # Table of Contents
        if self.sections:
            report += "## Table of Contents\n"
            for i, section in enumerate(self.sections, 1):
                anchor = section['title'].lower().replace(' ', '-').replace('.', '').replace(',', '')
                report += f"{i}. [{section['title']}](#{anchor})\n"
            report += "\n"
        for section in self.sections:
            report += f"## {section['title']}\n"
            report += f"{section['content']}\n\n"
        
        # Try to write to the specified file, fallback to temp directory if permission denied
        try:
            with open(output_file, 'w') as f:
                f.write(report)
        except PermissionError:
            # Fallback to temp directory
            temp_file = os.path.join(tempfile.gettempdir(), os.path.basename(output_file))
            with open(temp_file, 'w') as f:
                f.write(report)
            print(f"Warning: Permission denied for {output_file}, report saved to {temp_file}")
            return temp_file
        
        return output_file
    
    def _generate_html(self, output_file):
        """Generate an HTML report with enhanced styling and a table of contents"""
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TrimurtiSec Penetration Test Report</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 40px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            border-bottom: 3px solid #2c3e50;
            padding-bottom: 30px;
            margin-bottom: 30px;
        }
        .logo {
            font-size: 2.5em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #7f8c8d;
            font-size: 1.2em;
        }
        .meta-info {
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 30px;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            background-color: #f8f9fa;
            padding: 15px;
            border-left: 5px solid #3498db;
            margin-top: 30px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: white;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #34495e;
            color: white;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        tr:hover {
            background-color: #e8f4fd;
        }
        .status-live {
            color: #27ae60;
            font-weight: bold;
        }
        .status-dead {
            color: #e74c3c;
        }
        .vulnerability-high {
            background-color: #e74c3c;
            color: white;
            padding: 3px 8px;
            border-radius: 3px;
        }
        .vulnerability-medium {
            background-color: #f39c12;
            color: white;
            padding: 3px 8px;
            border-radius: 3px;
        }
        .vulnerability-low {
            background-color: #f1c40f;
            color: black;
            padding: 3px 8px;
            border-radius: 3px;
        }
        .footer {
            text-align: center;
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #bdc3c7;
            color: #7f8c8d;
        }
        code {
            background-color: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        .summary-box {
            background-color: #e8f6f3;
            border: 1px solid #16a085;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .toc {
            background-color: #f8f9fa;
            border-left: 5px solid #3498db;
            padding: 20px;
            margin-bottom: 30px;
        }
        .toc h2 {
            margin-top: 0;
        }
        .toc ul {
            list-style-type: decimal;
            margin-left: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">TrimurtiSec</div>
            <div class="subtitle">Advanced Penetration Testing Framework</div>
        </div>
        
        <div class="meta-info">
            <strong>Target:</strong> {{ target }}<br>
            <strong>Generated:</strong> {{ timestamp }}<br>
            <strong>Framework Version:</strong> 1.0.0
        </div>
        
        <h1>Executive Summary</h1>
        <div class="summary-box">
            This report was generated using the TrimurtiSec Advanced Penetration Testing Framework.
            The framework provides comprehensive security assessment capabilities across multiple domains.
        </div>
        {% if sections %}
        <div class="toc">
            <h2>Table of Contents</h2>
            <ul>
            {% for section in sections %}
                <li><a href="#{{ section.title | lower | replace(' ', '-') | replace('.', '') | replace(',', '') }}">{{ section.title }}</a></li>
            {% endfor %}
            </ul>
        </div>
        {% endif %}
        
        {% for section in sections %}
        <h2 id="{{ section.title | lower | replace(' ', '-') | replace('.', '') | replace(',', '') }}">{{ section.title }}</h2>
        <div class="content">
            {{ section.content | safe }}
        </div>
        {% endfor %}
        
        <div class="footer">
            <p>Generated by TrimurtiSec Framework v1.0.0</p>
            <p>For more information, visit <a href="https://github.com/mnshchtri/TrimurtiSec">TrimurtiSec on GitHub</a></p>
        </div>
    </div>
</body>
</html>
        """
        
        template = Template(html_template)
        html_content = template.render(
            target=self.target,
            timestamp=self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            sections=self.sections
        )
        
        try:
            with open(output_file, 'w') as f:
                f.write(html_content)
        except PermissionError:
            temp_file = os.path.join(tempfile.gettempdir(), os.path.basename(output_file))
            with open(temp_file, 'w') as f:
                f.write(html_content)
            print(f"Warning: Permission denied for {output_file}, report saved to {temp_file}")
            return temp_file
        
        return output_file
    
    def _generate_pdf_reportlab(self, output_file):
        """Generate a visually optimized PDF report using FPDF, with improved alignment, color, and layout."""
        from fpdf import FPDF
        from datetime import datetime
        import os
        class PDF(FPDF):
            def __init__(self):
                super().__init__()
                self.logo_path = 'Images/logo.png' if os.path.exists('Images/logo.png') else None
            def header(self):
                self.set_fill_color(27, 45, 72)
                self.rect(0, 0, self.w, self.h, 'F')
                if self.logo_path:
                    try:
                        logo_width = 18
                        logo_height = 18
                        x_pos = (self.w - logo_width) / 2
                        self.image(self.logo_path, x_pos, 10, logo_width, logo_height)
                    except Exception:
                        pass
                self.set_y(30)
            def footer(self):
                self.set_y(-20)
                self.set_draw_color(34, 58, 95)
                self.set_line_width(0.5)
                self.line(10, self.get_y(), self.w - 10, self.get_y())
                self.set_y(-15)
                self.set_font('Arial', '', 9)
                self.set_text_color(180, 180, 180)
                self.cell(0, 10, f'TrimurtiSec Report | Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")} | Page {self.page_no()}', 0, 0, 'C')
        pdf = PDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=20)
        font_family = 'Arial'
        # Title Page (centered, visually consistent)
        pdf.set_y(40)
        if pdf.logo_path:
            try:
                logo_width = 40
                logo_height = 40
                x_pos = (pdf.w - logo_width) / 2
                pdf.image(pdf.logo_path, x_pos, pdf.get_y(), logo_width, logo_height)
                pdf.ln(logo_height + 5)
            except Exception:
                pdf.ln(45)
        pdf.set_font(font_family, 'B', 26)
        pdf.set_text_color(0, 255, 0)
        pdf.cell(0, 18, 'TrimurtiSec Penetration Test Report', 0, 1, 'C')
        pdf.set_font(font_family, 'I', 14)
        pdf.set_text_color(255, 215, 0)
        pdf.cell(0, 12, '"Three faces, one mission - Secure Everything."', 0, 1, 'C')
        pdf.ln(5)
        pdf.set_font(font_family, '', 13)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 10, f"Target: {self.target}", 0, 1, 'C')
        pdf.cell(0, 10, f"Assessment Date: {self.timestamp.strftime('%B %d, %Y')}", 0, 1, 'C')
        pdf.cell(0, 10, f"Report Generated: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}", 0, 1, 'C')
        pdf.ln(5)
        pdf.set_font(font_family, 'B', 12)
        pdf.set_text_color(255, 85, 85)
        pdf.cell(0, 10, 'CONFIDENTIAL - PENETRATION TEST REPORT', 0, 1, 'C')
        pdf.ln(2)
        pdf.set_font(font_family, 'I', 10)
        pdf.set_text_color(220, 220, 220)
        confidentiality_text = (
            "This document contains confidential and proprietary information. "
            "Distribution is restricted to authorized personnel only. "
            "This report is intended solely for the organization that commissioned the assessment."
        )
        words = confidentiality_text.split()
        line = ""
        for word in words:
            if pdf.get_string_width(line + word + " ") < 180:
                line += word + " "
            else:
                pdf.cell(0, 6, line.strip(), 0, 1, 'C')
                line = word + " "
        if line:
            pdf.cell(0, 6, line.strip(), 0, 1, 'C')
        pdf.ln(10)
        pdf.set_draw_color(34, 58, 95)
        pdf.set_line_width(1)
        pdf.line(20, pdf.get_y(), pdf.w - 20, pdf.get_y())
        pdf.ln(8)
        # Executive Summary
        pdf.add_page()
        pdf.set_y(25)
        pdf.set_font(font_family, 'B', 20)
        pdf.set_text_color(255, 215, 0)
        pdf.cell(0, 15, 'EXECUTIVE SUMMARY', 0, 1, 'L')
        pdf.ln(2)
        pdf.set_draw_color(34, 58, 95)
        pdf.set_line_width(0.7)
        pdf.line(15, pdf.get_y(), pdf.w - 15, pdf.get_y())
        pdf.ln(5)
        pdf.set_font(font_family, '', 11)
        pdf.set_text_color(255, 255, 255)
        summary_text = (
            "This report was generated using the TrimurtiSec Advanced Penetration Testing Framework. "
            "The framework provides comprehensive security assessment capabilities including reconnaissance, "
            "vulnerability assessment, exploitation, and persistence testing. This report contains detailed "
            "findings and recommendations for improving the security posture of the target system."
        )
        words = summary_text.split()
        line = ""
        for word in words:
            if pdf.get_string_width(line + word + " ") < 180:
                line += word + " "
            else:
                pdf.cell(0, 6, line.strip(), 0, 1, 'L')
                line = word + " "
        if line:
            pdf.cell(0, 6, line.strip(), 0, 1, 'L')
        pdf.ln(8)
        # Key Findings
        pdf.set_font(font_family, 'B', 16)
        pdf.set_text_color(255, 215, 0)
        pdf.cell(0, 10, 'KEY FINDINGS', 0, 1, 'L')
        pdf.ln(2)
        pdf.set_font(font_family, '', 12)
        for section in self.sections:
            pdf.set_text_color(0, 255, 0)
            pdf.cell(8, 8, '-', 0, 0, 'L')
            pdf.set_text_color(255, 255, 255)
            pdf.set_font(font_family, 'B', 12)
            pdf.cell(0, 8, f"{section['title']}", 0, 1, 'L')
            pdf.set_font(font_family, '', 12)
        pdf.ln(8)
        # Table of Contents
        if self.sections:
            pdf.set_font(font_family, 'B', 18)
            pdf.set_text_color(0, 255, 0)
            pdf.cell(0, 15, 'TABLE OF CONTENTS', 0, 1, 'L')
            pdf.ln(2)
            pdf.set_font(font_family, '', 12)
            for i, section in enumerate(self.sections, 1):
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 8, f"{i}. {section['title']}", 0, 1, 'L')
            pdf.ln(8)
        pdf.set_draw_color(34, 58, 95)
        pdf.set_line_width(1)
        pdf.line(20, pdf.get_y(), pdf.w - 20, pdf.get_y())
        pdf.ln(8)
        # Detailed Results
        for section in self.sections:
            pdf.set_font(font_family, 'B', 18)
            pdf.set_text_color(255, 215, 0)
            pdf.cell(0, 15, section['title'], 0, 1, 'L')
            pdf.ln(2)
            pdf.set_draw_color(34, 58, 95)
            pdf.set_line_width(0.7)
            pdf.line(15, pdf.get_y(), pdf.w - 15, pdf.get_y())
            pdf.ln(3)
            pdf.set_font(font_family, '', 12)
            pdf.set_text_color(255, 255, 255)
            # Improved content rendering: parse markdown for headings, bold, lists
            lines = section['content'].split('\n')
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if not line:
                    pdf.ln(2)
                    i += 1
                    continue
                # Markdown headings
                if line.startswith('### '):
                    pdf.set_font(font_family, 'B', 14)
                    pdf.set_text_color(255, 215, 0)
                    pdf.cell(0, 10, line[4:].strip(), 0, 1, 'L')
                    pdf.set_font(font_family, '', 12)
                    pdf.set_text_color(255, 255, 255)
                    i += 1
                    continue
                elif line.startswith('## '):
                    pdf.set_font(font_family, 'B', 16)
                    pdf.set_text_color(255, 215, 0)
                    pdf.cell(0, 12, line[3:].strip(), 0, 1, 'L')
                    pdf.set_font(font_family, '', 12)
                    pdf.set_text_color(255, 255, 255)
                    i += 1
                    continue
                elif line.startswith('# '):
                    pdf.set_font(font_family, 'B', 18)
                    pdf.set_text_color(255, 215, 0)
                    pdf.cell(0, 14, line[2:].strip(), 0, 1, 'L')
                    pdf.set_font(font_family, '', 12)
                    pdf.set_text_color(255, 255, 255)
                    i += 1
                    continue
                # Markdown bullet lists
                elif line.startswith('- ') or line.startswith('* '):
                    pdf.set_font(font_family, '', 12)
                    pdf.cell(8, 8, '-', 0, 0, 'L')
                    # Wrap bullet content
                    bullet_content = line[2:].strip()
                    words = bullet_content.split()
                    wrap_line = ""
                    for word in words:
                        if pdf.get_string_width(wrap_line + word + " ") < 170:
                            wrap_line += word + " "
                        else:
                            pdf.cell(0, 8, wrap_line.strip(), 0, 1, 'L')
                            wrap_line = word + " "
                    if wrap_line:
                        pdf.cell(0, 8, wrap_line.strip(), 0, 1, 'L')
                    i += 1
                    continue
                # Markdown bold (**text**)
                elif line.startswith('**') and line.endswith('**') and len(line) > 4:
                    pdf.set_font(font_family, 'B', 12)
                    # Wrap bold line
                    bold_line = line[2:-2].strip()
                    words = bold_line.split()
                    wrap_line = ""
                    for word in words:
                        if pdf.get_string_width(wrap_line + word + " ") < 170:
                            wrap_line += word + " "
                        else:
                            pdf.cell(0, 8, wrap_line.strip(), 0, 1, 'L')
                            wrap_line = word + " "
                    if wrap_line:
                        pdf.cell(0, 8, wrap_line.strip(), 0, 1, 'L')
                    pdf.set_font(font_family, '', 12)
                    i += 1
                    continue
                # Inline bold (**text**) in a line
                elif '**' in line:
                    import re
                    bold_parts = re.split(r'(\*\*[^*]+\*\*)', line)
                    wrap_line = ""
                    for part in bold_parts:
                        if part.startswith('**') and part.endswith('**'):
                            pdf.set_font(font_family, 'B', 12)
                            part_text = part[2:-2]
                        else:
                            pdf.set_font(font_family, '', 12)
                            part_text = part
                        words = part_text.split()
                        for word in words:
                            if pdf.get_string_width(wrap_line + word + " ") < 170:
                                wrap_line += word + " "
                            else:
                                pdf.cell(0, 8, wrap_line.strip(), 0, 1, 'L')
                                wrap_line = word + " "
                    if wrap_line:
                        pdf.cell(0, 8, wrap_line.strip(), 0, 1, 'L')
                    i += 1
                    continue
                # Paragraphs and wrapped lines
                else:
                    words = line.split()
                    wrap_line = ""
                    for word in words:
                        if pdf.get_string_width(wrap_line + word + " ") < 170:
                            wrap_line += word + " "
                        else:
                            pdf.cell(0, 8, wrap_line.strip(), 0, 1, 'L')
                            wrap_line = word + " "
                    if wrap_line:
                        pdf.cell(0, 8, wrap_line.strip(), 0, 1, 'L')
                    i += 1
            pdf.ln(5)
        try:
            pdf.output(output_file)
        except Exception as e:
            print(f"[bold red]Error generating PDF report: {e}[/bold red]")
        return output_file
