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
        """Generate a markdown report"""
        report = f"""# TrimurtiSec Penetration Test Report
Generated on: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
Target: {self.target}

## Executive Summary
This report was generated using the TrimurtiSec Advanced Penetration Testing Framework.

"""
        
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
        """Generate an HTML report with enhanced styling"""
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
        
        {% for section in sections %}
        <h2>{{ section.title }}</h2>
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
        """Generate a professional PDF report using ReportLab"""
        try:
            doc = SimpleDocTemplate(output_file, pagesize=A4)
            story = []
            
            # Define styles
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.white
            )
            
            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Normal'],
                fontSize=14,
                spaceAfter=20,
                alignment=TA_CENTER,
                textColor=colors.white
            )
            
            header_style = ParagraphStyle(
                'CustomHeader',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=15,
                spaceBefore=20,
                textColor=colors.white,
                backColor=colors.HexColor('#223A5F'),
                borderPadding=10
            )
            
            normal_white_style = ParagraphStyle(
                'NormalWhite',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.white
            )
            
            # Add title and header info
            story.append(Paragraph("TrimurtiSec Penetration Test Report", title_style))
            story.append(Paragraph("Advanced Security Assessment Framework by neox", subtitle_style))
            story.append(Spacer(1, 20))
            
            # Add logo to the top of the title page if available
            logo_path = 'Images/logo.png'
            if os.path.exists(logo_path):
                logo_width = 45
                logo_height = 45
                x_pos = (A4[0] - logo_width) / 2  # Center on page
                story.append(Spacer(1, 10))
                story.append(Image(logo_path, width=logo_width, height=logo_height, hAlign='CENTER'))
                story.append(Spacer(1, 20))
            
            # Add meta information table
            meta_data = [
                ['Target:', self.target],
                ['Generated:', self.timestamp.strftime('%Y-%m-%d %H:%M:%S')],
                ['Framework Version:', '1.0.0'],
                ['Report Type:', 'Comprehensive Security Assessment']
            ]
            
            meta_table = Table(meta_data, colWidths=[2*inch, 4*inch])
            meta_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#223A5F')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#1B2D48')),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#223A5F'))
            ]))
            
            story.append(meta_table)
            story.append(Spacer(1, 30))
            
            # Add Executive Summary
            story.append(Paragraph("Executive Summary", header_style))
            summary_text = (
                "This report was generated using the TrimurtiSec Advanced Penetration Testing Framework. "
                "The framework provides comprehensive security assessment capabilities including reconnaissance, "
                "vulnerability assessment, exploitation, and persistence testing. This report contains detailed "
                "findings and recommendations for improving the security posture of the target system."
            )
            story.append(Paragraph(summary_text, normal_white_style))
            story.append(Spacer(1, 20))
            
            # Add sections
            for section in self.sections:
                story.append(Paragraph(section['title'], header_style))
                content = section['content']
                # --- Markdown-style rendering for AI output ---
                lines = content.splitlines()
                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    # Render markdown-style bold heading
                    if line.startswith('**') and line.endswith('**:'):
                        heading_text = line.strip('*:').strip()
                        story.append(Paragraph(heading_text, header_style))
                        i += 1
                        continue
                    # Render markdown tables
                    if line.startswith('|') and '|' in line[1:]:
                        table_data = []
                        # Parse table header
                        header_row = [cell.strip() for cell in line.split('|')[1:-1]]
                        table_data.append(header_row)
                        i += 1
                        # Skip separator line (|------|)
                        if i < len(lines) and lines[i].strip().startswith('|') and '---' in lines[i]:
                            i += 1
                        # Parse table data rows
                        while i < len(lines) and lines[i].strip().startswith('|'):
                            data_row = [cell.strip() for cell in lines[i].split('|')[1:-1]]
                            if len(data_row) == len(header_row):  # Ensure row has correct number of columns
                                table_data.append(data_row)
                            i += 1
                        # Create PDF table
                        if table_data:
                            table = Table(table_data, colWidths=[1.2*inch, 1.5*inch, 2*inch, 0.8*inch])
                            table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#223A5F')),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                                ('FONTSIZE', (0, 0), (-1, -1), 9),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                                ('TOPPADDING', (0, 0), (-1, -1), 6),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#1B2D48')),
                                ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
                                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#223A5F'))
                            ]))
                            story.append(table)
                            story.append(Spacer(1, 10))
                        continue
                    # Render bullet list
                    if line.startswith('- '):
                        bullets = []
                        while i < len(lines) and lines[i].strip().startswith('- '):
                            bullets.append(lines[i].strip()[2:].strip())
                            i += 1
                        story.append(ListFlowable([
                            ListItem(Paragraph(b, normal_white_style)) for b in bullets
                        ], bulletType='bullet', leftIndent=20))
                        continue
                    # Render numbered list
                    if line and (line[0].isdigit() and line[1:3] == '. '):
                        numbers = []
                        while i < len(lines) and lines[i].strip() and lines[i].strip()[0].isdigit() and lines[i].strip()[1:3] == '. ':
                            numbers.append(lines[i].strip()[3:].strip())
                            i += 1
                        story.append(ListFlowable([
                            ListItem(Paragraph(n, normal_white_style)) for n in numbers
                        ], bulletType='1', leftIndent=20))
                        continue
                    # Render regular paragraph
                    if line:
                        story.append(Paragraph(line, normal_white_style))
                    i += 1
                story.append(Spacer(1, 20))
            
            # Add footer
            story.append(PageBreak())
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=10,
                alignment=TA_CENTER,
                textColor=colors.white
            )
            
            story.append(Spacer(1, 200))
            story.append(Paragraph("Generated by TrimurtiSec Framework v1.0.0", footer_style))
            story.append(Paragraph("Advanced Penetration Testing Suite", footer_style))
            
            # Draw background on every page
            def draw_background(canvas, doc):
                canvas.saveState()
                canvas.setFillColor(colors.HexColor('#1B2D48'))
                canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], fill=1, stroke=0)
                canvas.restoreState()

            # Build PDF with background
            doc.build(story, onFirstPage=draw_background, onLaterPages=draw_background)
            
        except PermissionError:
            temp_file = os.path.join(tempfile.gettempdir(), os.path.basename(output_file))
            doc = SimpleDocTemplate(temp_file, pagesize=A4)
            doc.build(story, onFirstPage=draw_background, onLaterPages=draw_background)
            print(f"Warning: Permission denied for {output_file}, report saved to {temp_file}")
            return temp_file
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            # Fallback to markdown
            return self._generate_markdown(output_file.replace('.pdf', '.md'))
        
        return output_file
