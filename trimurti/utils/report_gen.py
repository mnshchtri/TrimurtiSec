import markdown
from datetime import datetime
import os
import tempfile
import json
from jinja2 import Template
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

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
            <div class="logo">🔱 TrimurtiSec</div>
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
            <p>For more information, visit <a href="https://github.com/yourusername/TrimurtiSec">TrimurtiSec on GitHub</a></p>
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
                textColor=colors.HexColor('#2c3e50')
            )
            
            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Normal'],
                fontSize=14,
                spaceAfter=20,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#7f8c8d')
            )
            
            header_style = ParagraphStyle(
                'CustomHeader',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=15,
                spaceBefore=20,
                textColor=colors.HexColor('#34495e'),
                backColor=colors.HexColor('#f8f9fa'),
                borderPadding=10
            )
            
            # Add title and header info
            story.append(Paragraph("🔱 TrimurtiSec Penetration Test Report", title_style))
            story.append(Paragraph("Advanced Security Assessment Framework", subtitle_style))
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
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#ecf0f1')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
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
            story.append(Paragraph(summary_text, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Add sections
            for section in self.sections:
                story.append(Paragraph(section['title'], header_style))
                
                # Convert markdown content to paragraphs
                content = section['content']
                
                # Process tables if present
                if '|' in content and '---' in content:
                    lines = content.split('\n')
                    table_data = []
                    in_table = False
                    
                    for line in lines:
                        if '|' in line and not line.strip().startswith('#'):
                            if '---' in line:
                                in_table = True
                                continue
                            if in_table:
                                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                                if cells and any(cell for cell in cells):
                                    table_data.append(cells)
                            elif not in_table and '|' in line:
                                # Header row
                                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                                if cells:
                                    table_data.append(cells)
                    
                    if table_data:
                        # Create table
                        table = Table(table_data)
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 0), (-1, -1), 9),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                            ('TOPPADDING', (0, 0), (-1, -1), 6),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f2f2f2')])
                        ]))
                        story.append(table)
                else:
                    # Regular text content
                    paragraphs = content.split('\n\n')
                    for para in paragraphs:
                        if para.strip():
                            # Handle bullet points
                            if para.strip().startswith('- '):
                                bullet_items = para.split('\n')
                                for item in bullet_items:
                                    if item.strip().startswith('- '):
                                        story.append(Paragraph(f"• {item.strip()[2:]}", styles['Normal']))
                            else:
                                story.append(Paragraph(para.strip(), styles['Normal']))
                
                story.append(Spacer(1, 20))
            
            # Add footer
            story.append(PageBreak())
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=10,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#7f8c8d')
            )
            
            story.append(Spacer(1, 200))
            story.append(Paragraph("Generated by TrimurtiSec Framework v1.0.0", footer_style))
            story.append(Paragraph("Advanced Penetration Testing Suite", footer_style))
            
            # Build PDF
            doc.build(story)
            
        except PermissionError:
            temp_file = os.path.join(tempfile.gettempdir(), os.path.basename(output_file))
            doc = SimpleDocTemplate(temp_file, pagesize=A4)
            doc.build(story)
            print(f"Warning: Permission denied for {output_file}, report saved to {temp_file}")
            return temp_file
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            # Fallback to markdown
            return self._generate_markdown(output_file.replace('.pdf', '.md'))
        
        return output_file
