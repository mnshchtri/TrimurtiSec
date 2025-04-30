import markdown
from datetime import datetime

class ReportGenerator:
    def __init__(self):
        self.sections = []
        self.timestamp = datetime.now()
        
    def add_section(self, title, content):
        self.sections.append({
            "title": title,
            "content": content
        })
    
    def generate(self, output_file):
        """Generate a markdown report"""
        report = f"""# Trimurti Penetration Test Report
Generated on: {self.timestamp}

## Executive Summary
This report was generated using the Trimurti Penetration Testing Framework.

"""
        
        for section in self.sections:
            report += f"## {section['title']}\n"
            report += f"{section['content']}\n\n"
            
        with open(output_file, 'w') as f:
            f.write(report) 