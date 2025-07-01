import socket
import subprocess
import json
import os
import time
import yaml
from rich.console import Console
from rich.progress import Progress
from typing import List, Dict, Set
from datetime import datetime
from fpdf import FPDF
from trimurti.utils.enhanced_progress import TrimurtiProgressTracker, AnimatedSpinner, create_hacking_simulation_progress

console = Console()

class SubdomainDiscovery:
    def __init__(self, target):
        self.target = target
        self.subdomains = set()
        self.live_subdomains = set()
        # Create reports directory
        os.makedirs('reports', exist_ok=True)
        self._ensure_tools_installed()

    def _ensure_tools_installed(self):
        """Ensure required tools are installed"""
        with AnimatedSpinner("Checking and installing required tools...", "dots12") as spinner:
            try:
                # Check Subfinder
                subprocess.run(['subfinder', '-version'], capture_output=True, check=True)
                console.log("Subfinder is available")
            except (subprocess.CalledProcessError, FileNotFoundError):
                console.print("[yellow]Installing Subfinder...[/yellow]")
                # Install Subfinder using Go
                subprocess.run([
                    'go', 'install', '-v', 'github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest'
                ], check=True)
                console.log("Subfinder installed successfully")

            try:
                # Check HTTPX
                subprocess.run(['httpx', '-version'], capture_output=True, check=True)
                console.log("HTTPX is available")
            except (subprocess.CalledProcessError, FileNotFoundError):
                console.print("[yellow]Installing HTTPX...[/yellow]")
                subprocess.run([
                    'go', 'install', '-v', 'github.com/projectdiscovery/httpx/cmd/httpx@latest'
                ], check=True)
                console.log("HTTPX installed successfully")

    def discover(self) -> str:
        results = "## Subdomain Discovery Results\n\n"

        if self._is_ip_address(self.target):
            return "Subdomain discovery requires a domain name, not an IP address."

        # Create enhanced progress tracker for subdomain discovery
        tracker = TrimurtiProgressTracker('brahma', self.target)
        tracker.create_mode_header()
        
        results += f"Target Domain: {self.target}\n\n"

        # Enhanced subdomain discovery with dramatic progress
        discovery_steps = [
            "Initializing subdomain enumeration engines...",
            "Querying DNS databases and certificate logs...",
            "Crawling web archives and search engines...",
            "Probing discovered subdomains for live hosts...",
            "Analyzing response headers and technologies..."
        ]
        
        with tracker.create_scan_progress(len(discovery_steps)) as progress:
            for i, step in enumerate(discovery_steps):
                task = progress.add_task(step, total=100)
                
                # Execute actual discovery steps
                if i == 1:  # Start subfinder during DNS queries phase
                    console.log(f"Running Subfinder for {self.target}")
                    self._run_subfinder()
                elif i == 3:  # Start HTTPX during probing phase
                    console.log("Probing subdomains with HTTPX")
                    self._probe_with_httpx()
                
                # Animate progress with realistic timing
                for j in range(100):
                    progress.advance(task, 1)
                    if i in [1, 3]:  # Add delay for actual work phases
                        import time
                        time.sleep(0.02)

        # Format results
        results += self._format_results()
        
        # Show completion statistics
        discovery_stats = {
            "Target Domain": self.target,
            "Total Subdomains Found": len(self.subdomains),
            "Live Subdomains": len(self.live_subdomains),
            "Tools Used": "Subfinder + HTTPX",
            "Status": "Discovery Complete"
        }
        tracker.show_completion_stats(discovery_stats)
        
        # Save report to reports directory
        report_file = f'reports/subdomain_discovery_report_{self.target}.pdf'
        self._generate_pdf_report(discovery_stats, report_file)
            
        console.print(f"[green]Report saved to: {report_file}[/green]")
        
        return "Subdomain discovery complete. Report generated."

    def _generate_pdf_report(self, stats: dict, output_path: str):
        """Generate a comprehensive PDF penetration test report for subdomain discovery."""
        
        class PDF(FPDF):
            def __init__(self):
                super().__init__()
                self.logo_path = 'Images/logo.png' if os.path.exists('Images/logo.png') else None
                
            def header(self):
                # Simulate a vertical gradient background from #1B2D48 to #223A5F
                steps = 30
                for i in range(steps):
                    r1, g1, b1 = 27, 45, 72  # #1B2D48
                    r2, g2, b2 = 34, 58, 95  # #223A5F
                    r = int(r1 + (r2 - r1) * i / steps)
                    g = int(g1 + (g2 - g1) * i / steps)
                    b = int(b1 + (b2 - b1) * i / steps)
                    y = self.h * i / steps
                    self.set_fill_color(r, g, b)
                    self.rect(0, y, self.w, self.h / steps + 1, 'F')
                if self.logo_path:
                    try:
                        # Even smaller logo for header
                        logo_width = 10
                        logo_height = 10
                        x_pos = self.w - logo_width - 10
                        self.image(self.logo_path, x_pos, 8, logo_width, logo_height)
                    except Exception:
                        pass
                self.set_font('Arial', 'B', 9)  # Smaller font size
                self.set_text_color(0, 255, 0)  # Green
                self.cell(0, 10, 'TrimurtiSec Penetration Testing Framework', 0, 0, 'L')
                self.ln(15)
                
            def footer(self):
                """Add footer to every page"""
                self.set_y(-15)
                self.set_font('Arial', '', 8)
                self.set_text_color(200, 200, 200)
                self.cell(0, 10, f'TrimurtiSec Report | Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")} | Page {self.page_no()}', 0, 0, 'C')
        
        pdf = PDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Use built-in Arial font to avoid font loading issues
        font_family = 'Arial'
        console.print("[cyan]Using built-in Arial font for PDF generation[/cyan]")

        # Title Page - Large centered logo
        if pdf.logo_path:
            try:
                # Large centered logo for title page
                logo_width = 45
                logo_height = 45
                x_pos = (pdf.w - logo_width) / 2  # Center on page
                pdf.set_xy(x_pos, 30)
                pdf.image(pdf.logo_path, x_pos, 30, logo_width, logo_height)
                pdf.ln(55)  # Move down after large logo
                # Add slogan below logo
                pdf.set_font(font_family, 'I', 14)
                pdf.set_text_color(255, 215, 0)  # Gold
                pdf.cell(0, 12, '"Three faces, one mission - Secure Everything."', 0, 1, 'C')
                pdf.ln(10)
            except Exception as e:
                console.print(f"[yellow]Could not load title page logo: {e}[/yellow]")
                pdf.ln(30)
        else:
            pdf.ln(30)
        
        pdf.set_font(font_family, 'B', 28)
        pdf.set_text_color(0, 255, 0)  # Green
        pdf.cell(0, 20, 'TrimurtiSec Penetration Test Report', 0, 1, 'C')
        
        pdf.set_font(font_family, 'B', 18)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 15, 'Subdomain Discovery & Reconnaissance', 0, 1, 'C')
        
        pdf.ln(20)
        pdf.set_font(font_family, '', 14)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 10, f"Target Domain: {self.target}", 0, 1, 'C')
        pdf.cell(0, 8, f"Assessment Date: {datetime.now().strftime('%B %d, %Y')}", 0, 1, 'C')
        pdf.cell(0, 8, f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}", 0, 1, 'C')
        pdf.ln(10)
        
        # Add classification and confidentiality notice
        pdf.ln(30)
        pdf.set_font(font_family, 'B', 12)
        pdf.set_text_color(255, 0, 0)  # Red
        pdf.cell(0, 8, 'CONFIDENTIAL - PENETRATION TEST REPORT', 0, 1, 'C')
        
        pdf.set_font(font_family, 'I', 10)
        pdf.set_text_color(255, 255, 255)
        pdf.ln(10)
        confidentiality_text = (
            "This document contains confidential and proprietary information. "
            "Distribution is restricted to authorized personnel only. "
            "This report is intended solely for the organization that commissioned the assessment."
        )
        # Split text into multiple lines
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
        
        # Add new page for executive summary
        pdf.add_page()
        pdf.ln(10)
        
        # Executive Summary Section
        pdf.set_font(font_family, 'B', 20)
        pdf.set_text_color(255, 215, 0)  # Gold
        pdf.cell(0, 15, 'EXECUTIVE SUMMARY', 0, 1, 'L')
        pdf.ln(5)
        
        # Calculate risk metrics
        total_subdomains = len(self.subdomains)
        live_subdomains = len(self.live_subdomains)
        success_rate = (live_subdomains / max(total_subdomains, 1)) * 100
        
        # Executive summary content
        pdf.set_font(font_family, '', 12)
        pdf.set_text_color(255, 255, 255)
        
        exec_summary = (
            f"This penetration test report presents the findings from a comprehensive subdomain discovery "
            f"assessment conducted against {self.target}. The assessment utilized industry-standard "
            f"reconnaissance tools including Subfinder and HTTPX to identify and enumerate subdomains "
            f"associated with the target domain.\n\n"
            f"The assessment successfully identified {total_subdomains} total subdomains, of which "
            f"{live_subdomains} ({success_rate:.1f}%) were confirmed as live and accessible. "
            f"This discovery phase represents the initial reconnaissance stage of a penetration test "
            f"and provides valuable intelligence about the target's digital footprint and potential "
            f"attack surface.\n\n"
        )
        
        # Risk assessment based on findings
        if live_subdomains == 0:
            risk_level = "LOW"
            risk_color = (0, 255, 0)
            risk_text = (
                "No live subdomains were discovered during this assessment, indicating a minimal "
                "external attack surface for subdomain-based attacks. However, this does not preclude "
                "the existence of subdomains that may be protected by WAF, require authentication, "
                "or are hosted on non-standard ports."
            )
        elif live_subdomains <= 5:
            risk_level = "MEDIUM"
            risk_color = (255, 255, 0)
            risk_text = (
                "A limited number of live subdomains were discovered. While this suggests a controlled "
                "external presence, each discovered subdomain represents a potential entry point that "
                "requires further security assessment to identify vulnerabilities."
            )
        else:
            risk_level = "HIGH"
            risk_color = (255, 0, 0)
            risk_text = (
                "A significant number of live subdomains were discovered, indicating an extensive "
                "external attack surface. This large digital footprint increases the probability "
                "of finding exploitable vulnerabilities and requires comprehensive security review."
            )
        
        exec_summary += f"Based on the findings, the current risk level is assessed as {risk_level}. {risk_text}"
        
        # Wrap and display executive summary text
        words = exec_summary.split()
        line = ""
        for word in words:
            if pdf.get_string_width(line + word + " ") < 180:
                line += word + " "
            else:
                pdf.cell(0, 6, line.strip(), 0, 1, 'L')
                line = word + " "
        if line:
            pdf.cell(0, 6, line.strip(), 0, 1, 'L')
        
        pdf.ln(10)
        
        # Risk Level Box
        pdf.set_font(font_family, 'B', 14)
        pdf.set_text_color(risk_color[0], risk_color[1], risk_color[2])
        pdf.cell(0, 10, f'OVERALL RISK LEVEL: {risk_level}', 0, 1, 'C')
        pdf.ln(10)
        
        # Key Findings Box
        pdf.set_font(font_family, 'B', 16)
        pdf.set_text_color(255, 215, 0)  # Gold
        pdf.cell(0, 10, 'KEY FINDINGS', 0, 1, 'L')
        pdf.ln(5)
        
        pdf.set_font(font_family, '', 12)
        pdf.set_text_color(255, 255, 255)
        
        key_findings = [
            f"Total subdomains enumerated: {total_subdomains}",
            f"Live/accessible subdomains: {live_subdomains}",
            f"Subdomain accessibility rate: {success_rate:.1f}%",
            "Tools utilized: Subfinder, HTTPX",
            "Assessment methodology: Passive reconnaissance with active probing"
        ]
        
        for finding in key_findings:
            pdf.cell(8, 8, '-', 0, 0, 'L')
            pdf.set_text_color(255, 255, 102)  # Yellowish for subheading
            pdf.cell(0, 8, finding, 0, 1, 'L')
            pdf.set_text_color(255, 255, 255)  # Reset to white
        
        pdf.ln(10)
        
        # Add new page for detailed findings
        pdf.add_page()
        pdf.ln(10)
        
        # Detailed Technical Findings
        pdf.set_font(font_family, 'B', 20)
        pdf.set_text_color(255, 215, 0)  # Gold
        pdf.cell(0, 15, 'DETAILED TECHNICAL FINDINGS', 0, 1, 'L')
        pdf.ln(5)
        
        # Methodology section
        pdf.set_font(font_family, 'B', 14)
        pdf.cell(0, 10, '1. ASSESSMENT METHODOLOGY', 0, 1, 'L')
        pdf.ln(3)
        
        pdf.set_font(font_family, '', 11)
        pdf.set_text_color(255, 255, 255)
        
        methodology_text = (
            "The subdomain discovery assessment was conducted using a two-phase approach:\n\n"
            "Phase 1 - Passive Reconnaissance: Utilized Subfinder to query multiple data sources "
            "including certificate transparency logs, DNS databases, search engines, and threat "
            "intelligence feeds to identify potential subdomains without directly interacting "
            "with the target infrastructure.\n\n"
            "Phase 2 - Active Probing: Employed HTTPX to probe discovered subdomains for "
            "accessibility, gathering information about HTTP status codes, server technologies, "
            "IP addresses, and page titles while maintaining a low-impact scanning profile."
        )
        
        # Wrap methodology text
        words = methodology_text.split()
        line = ""
        for word in words:
            if word == "\n\n":
                pdf.cell(0, 6, line.strip(), 0, 1, 'L')
                pdf.ln(3)
                line = ""
            elif pdf.get_string_width(line + word + " ") < 180:
                line += word + " "
            else:
                pdf.cell(0, 6, line.strip(), 0, 1, 'L')
                line = word + " "
        if line:
            pdf.cell(0, 6, line.strip(), 0, 1, 'L')
        
        pdf.ln(10)
        
        # Discovery Results Section
        pdf.set_font(font_family, 'B', 14)
        pdf.cell(0, 10, '2. SUBDOMAIN DISCOVERY RESULTS', 0, 1, 'L')
        pdf.ln(3)
        
        # Summary Stats Table
        pdf.set_font(font_family, 'B', 12)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 10, 'Assessment Summary', 0, 1, 'L')
        
        pdf.set_font(font_family, '', 12)
        pdf.set_fill_color(245, 245, 245)
        
        for key, value in stats.items():
            pdf.set_font(font_family, 'B', 12)
            pdf.cell(60, 10, str(key), 0, 0, 'L')
            pdf.set_font(font_family, '', 12)
            pdf.cell(0, 10, str(value), 0, 1, 'L')
        pdf.ln(10)

        # Results Table
        pdf.set_font(font_family, 'B', 16)
        pdf.cell(0, 10, 'Live Subdomains', 0, 1, 'L')

        if not self.live_subdomains:
            pdf.set_font(font_family, '', 12)
            pdf.cell(0, 10, "No live subdomains were discovered.", 0, 1, 'L')
        else:
            pdf.set_font(font_family, 'B', 10)
            pdf.set_fill_color(70, 130, 180) # SteelBlue
            pdf.set_text_color(0, 0, 0)  # Black
            
            col_widths = {'Subdomain': 80, 'IP Address': 40, 'Status': 20, 'Server': 50}
            for header, width in col_widths.items():
                pdf.cell(width, 10, header, 1, 0, 'C', 1)
            pdf.ln()

            pdf.set_font(font_family, '', 9)
            pdf.set_text_color(0, 0, 0)  # Black
            fill = False
            
            if os.path.exists('reports/httpx_results.json'):
                with open('reports/httpx_results.json', 'r') as f:
                    for line in f:
                        try:
                            result = json.loads(line.strip())
                            subdomain = result.get('url', '').replace('https://', '').replace('http://', '')
                            if subdomain in self.live_subdomains:
                                ip = result.get('a', ['N/A'])[0]
                                status = str(result.get('status_code', 'N/A'))
                                server = result.get('webserver', 'N/A')
                                
                                pdf.set_fill_color(245, 245, 245) if fill else pdf.set_fill_color(255, 255, 255)
                                pdf.cell(col_widths['Subdomain'], 10, subdomain, 1, 0, 'L', 1)
                                pdf.cell(col_widths['IP Address'], 10, ip, 1, 0, 'L', 1)
                                pdf.cell(col_widths['Status'], 10, status, 1, 0, 'C', 1)
                                pdf.cell(col_widths['Server'], 10, server, 1, 1, 'L', 1)
                                fill = not fill
                        except (json.JSONDecodeError, KeyError):
                            continue
        
        pdf.ln(10)
        
        # Add new page for all discovered subdomains
        pdf.add_page()
        pdf.ln(10)
        
        # All Discovered Subdomains Section
        pdf.set_font(font_family, 'B', 16)
        pdf.set_text_color(255, 215, 0)  # Gold
        pdf.cell(0, 10, '3. COMPLETE SUBDOMAIN INVENTORY', 0, 1, 'L')
        pdf.ln(5)
        
        # Live Subdomains Analysis
        pdf.set_font(font_family, 'B', 14)
        pdf.set_text_color(0, 255, 0)  # Green for heading
        pdf.cell(0, 10, f'3.1 Live/Accessible Subdomains ({live_subdomains} found)', 0, 1, 'L')
        pdf.ln(3)
        
        pdf.set_font(font_family, '', 11)
        pdf.set_text_color(0, 255, 0)  # Green for list
        
        if live_subdomains > 0:
            for i, subdomain in enumerate(sorted(self.live_subdomains), 1):
                # Gather details for each live subdomain
                ip, status, server, title = 'N/A', 'N/A', 'N/A', 'N/A'
                if os.path.exists('reports/httpx_results.json'):
                    with open('reports/httpx_results.json', 'r') as f:
                        for line in f:
                            try:
                                result = json.loads(line.strip())
                                url = result.get('url', '').replace('https://', '').replace('http://', '')
                                if url == subdomain:
                                    ip = result.get('ip', 'N/A')
                                    status = result.get('status_code', 'N/A')
                                    server = result.get('server', 'N/A')
                                    title = result.get('title', 'N/A')
                                    break
                            except json.JSONDecodeError:
                                continue
                pdf.set_text_color(0, 255, 0)  # Green for subdomain
                pdf.cell(0, 8, f"{i}. {subdomain}", 0, 1, 'L')
                pdf.set_text_color(255, 255, 255)  # White for details
                pdf.cell(0, 8, f"IP Address: {ip}", 0, 1, 'L')
                pdf.cell(0, 8, f"Status Code: {status}", 0, 1, 'L')
                pdf.cell(0, 8, f"Server: {server}", 0, 1, 'L')
                pdf.cell(0, 8, f"Title: {title}", 0, 1, 'L')
                pdf.ln(2)
        else:
            pdf.set_text_color(255, 255, 255)
            pdf.cell(0, 8, "No live subdomains were discovered.", 0, 1, 'L')
        
        # Non-responsive Subdomains
        pdf.set_font(font_family, 'B', 14)
        pdf.set_text_color(255, 255, 255)  # White for heading
        non_responsive = len(self.subdomains) - live_subdomains
        pdf.cell(0, 10, f'3.2 Non-Responsive Subdomains ({non_responsive} found)', 0, 1, 'L')
        pdf.ln(3)
        
        pdf.set_font(font_family, '', 11)
        pdf.set_text_color(255, 0, 0)  # Red for list
        
        if non_responsive > 0:
            non_responsive_list = sorted(self.subdomains - self.live_subdomains)
            for i, subdomain in enumerate(non_responsive_list, 1):
                pdf.cell(0, 6, f"{i}. {subdomain}", 0, 1, 'L')
        pdf.set_text_color(255, 255, 255)  # Restore to white after list
        
        pdf.ln(15)
        
        # Recommendations Section
        pdf.set_font(font_family, 'B', 16)
        pdf.set_text_color(255, 215, 0)  # Gold
        pdf.cell(0, 10, '4. SECURITY RECOMMENDATIONS', 0, 1, 'L')
        pdf.ln(5)
        
        recommendations = [
            "4.1 Immediate Actions:",
            "- Conduct comprehensive vulnerability scanning on all live subdomains",
            "- Review subdomain inventory for unnecessary or forgotten services",
            "- Implement proper access controls and authentication mechanisms",
            "- Ensure all subdomains are regularly updated and patched",
            "",
            "4.2 Security Hardening:",
            "- Deploy Web Application Firewalls (WAF) where appropriate",
            "- Implement SSL/TLS certificates for all web services",
            "- Configure proper HTTP security headers",
            "- Review and minimize exposed services and ports",
            "",
            "4.3 Monitoring and Maintenance:",
            "- Establish continuous subdomain monitoring",
            "- Implement intrusion detection systems",
            "- Regular security assessments and penetration testing",
            "- Maintain an updated asset inventory",
            "",
            "4.4 Risk Mitigation:",
            "- Decommission unused subdomains and services",
            "- Implement network segmentation where possible",
            "- Regular backup and disaster recovery testing",
            "- Staff security awareness training"
        ]
        for line in recommendations:
            if line.startswith('- '):
                pdf.set_font(font_family, 'I', 11)  # Italic for bullet points
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 8, line, 0, 1, 'L')
                pdf.set_font(font_family, '', 11)  # Restore normal font after bullet
            elif line.strip() == '':
                pdf.ln(3)
            else:
                pdf.set_font(font_family, 'B', 12)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 8, line, 0, 1, 'L')
        
        # ... end of SECURITY RECOMMENDATIONS ...
        pdf.ln(15)  # Add extra space before CONCLUSION
        # Conclusion
        pdf.set_font(font_family, 'B', 16)
        pdf.set_text_color(255, 215, 0)  # Gold for heading
        pdf.cell(0, 10, '5. CONCLUSION', 0, 1, 'L')
        pdf.ln(5)
        
        pdf.set_font(font_family, '', 11)
        pdf.set_text_color(255, 255, 255)  # White for body text
        
        conclusion_text = (
            f"This subdomain discovery assessment for {self.target} has mapped the organization's external attack surface, identifying {total_subdomains} subdomains, of which {live_subdomains} are currently accessible. "
            f"These live assets represent potential entry points for threat actors and should be prioritized for further security evaluation, including vulnerability scanning and penetration testing. "
            f"Inactive or non-responsive subdomains, while not immediately exploitable, should be monitored for future changes or unintended exposure.\n\n"
            f"The dynamic nature of modern infrastructures means that new subdomains may appear and existing ones may change status over time. Regular automated discovery and validation are essential to maintain an accurate inventory and reduce the risk of shadow IT.\n\n"
            f"It is recommended that the organization integrates subdomain monitoring into its continuous security operations, promptly investigates any unexpected exposures, and enforces strict controls over DNS and web asset management. "
            f"By maintaining visibility and acting on the findings of this assessment, {self.target} can significantly reduce its external risk profile and improve its overall cybersecurity posture."
        )
        
        # Wrap conclusion text
        words = conclusion_text.split()
        line = ""
        for word in words:
            if pdf.get_string_width(line + word + " ") < 180:
                line += word + " "
            else:
                pdf.cell(0, 6, line.strip(), 0, 1, 'L')
                line = word + " "
        if line:
            pdf.cell(0, 6, line.strip(), 0, 1, 'L')
        
        pdf.ln(20)

        try:
            pdf.output(output_path)
        except Exception as e:
            console.print(f"[bold red]Error generating PDF report: {e}[/bold red]")

    def _run_subfinder(self):
        """Run Subfinder for subdomain enumeration"""
        try:
            # Run Subfinder with various options
            cmd = f"subfinder -d {self.target} -silent -o reports/subfinder_results.txt"
            subprocess.run(cmd, shell=True, check=True)
            
            # Parse results
            if os.path.exists('reports/subfinder_results.txt'):
                with open('reports/subfinder_results.txt', 'r') as f:
                    for line in f:
                        subdomain = line.strip()
                        if subdomain:
                            self.subdomains.add(subdomain)
                console.log(f"Subfinder found {len(self.subdomains)} subdomains")
            else:
                console.log("[red]Subfinder results file not found[/red]")
        except Exception as e:
            console.log(f"[red]Error running Subfinder: {str(e)}[/red]")

    def _probe_with_httpx(self):
        """Probe subdomains with HTTPX"""
        try:
            # Use piped input for httpx for better compatibility
            cmd = (
                f"cat reports/subfinder_results.txt | "
                "httpx -silent -status-code -ip -tech-detect -mc 200,301,302 "
                "-title -server -json -o reports/httpx_results.json"
            )
            process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if process.returncode != 0:
                console.print(f"[red]HTTPX error: {process.stderr}[/red]")
                return

            # Process results
            if os.path.exists('reports/httpx_results.json'):
                with open('reports/httpx_results.json', 'r') as f:
                    for line in f:
                        try:
                            result = json.loads(line.strip())
                            url = result.get('url', '').replace('https://', '').replace('http://', '')
                            if url:
                                self.live_subdomains.add(url)
                        except json.JSONDecodeError:
                            continue

            console.log(f"HTTPX identified {len(self.live_subdomains)} live subdomains")
        except Exception as e:
            console.print(f"[red]Error running HTTPX: {str(e)}[/red]")

    def _format_results(self) -> str:
        """Format the discovery results"""
        results = "## Subdomain Discovery Results\n\n"
        results += f"Target Domain: {self.target}\n\n"

        results += "### Discovered Subdomains\n\n"
        results += "| Subdomain | IP Address | Status Code | Server | Title |\n"
        results += "|:----------|:-----------|:------------|:-------|:------|\n"

        if not self.subdomains:
            results += "| No subdomains discovered | | | | |\n"
            return results

        try:
            if os.path.exists('reports/httpx_results.json'):
                with open('reports/httpx_results.json', 'r') as f:
                    for line in f:
                        try:
                            result = json.loads(line.strip())
                            subdomain = result.get('url', '').replace('https://', '').replace('http://', '')
                            ip = result.get('ip', 'N/A')
                            status = result.get('status_code', 'N/A')
                            server = result.get('server', 'N/A')
                            title = result.get('title', 'N/A')
                            
                            results += f"| {subdomain} | {ip} | {status} | {server} | {title} |\n"
                        except json.JSONDecodeError:
                            continue
            else:
                # If HTTPX results not available, just show discovered subdomains
                for subdomain in sorted(self.subdomains):
                    results += f"| {subdomain} | N/A | N/A | N/A | N/A |\n"
        except Exception as e:
            console.print(f"[red]Error formatting results: {str(e)}[/red]")
            results += "| Error processing results | | | | |\n"

        results += "\n### Discovery Summary\n\n"
        results += f"- Total Subdomains Found: {len(self.subdomains)}\n"
        results += f"- Live Subdomains: {len(self.live_subdomains)}\n"
        results += f"- Success Rate: {(len(self.live_subdomains)/max(len(self.subdomains), 1)*100):.1f}%\n"
        
        # Add detailed live subdomains list
        if self.live_subdomains:
            results += "\n### Live Subdomains\n\n"
            # Table header
            results += "| Subdomain | IP Address | Status | Server |\n"
            results += "|:----------|:-----------|:-------|:-------|\n"
            for subdomain in sorted(self.live_subdomains):
                # Find the corresponding entry in httpx_results.json for details
                ip, status, server = 'N/A', 'N/A', 'N/A'
                if os.path.exists('reports/httpx_results.json'):
                    with open('reports/httpx_results.json', 'r') as f:
                        for line in f:
                            try:
                                result = json.loads(line.strip())
                                url = result.get('url', '').replace('https://', '').replace('http://', '')
                                if url == subdomain:
                                    ip = result.get('ip', 'N/A')
                                    status = result.get('status_code', 'N/A')
                                    server = result.get('server', 'N/A')
                                    break
                            except json.JSONDecodeError:
                                continue
                # Use black text for table row
                results += f"| <font color='black'>{subdomain}</font> | <font color='black'>{ip}</font> | <font color='black'>{status}</font> | <font color='black'>{server}</font> |\n"
        
        # Add file locations
        results += "\n### Report Files\n\n"
        results += "- Subfinder results: `reports/subfinder_results.txt`\n"
        results += "- Detailed results: `reports/httpx_results.json`\n"
        results += "- Full report: `reports/subdomain_discovery_report.md`\n"

        return results

    def _is_ip_address(self, address):
        try:
            socket.inet_aton(address)
            return True
        except socket.error:
            return False
    
    def _run_vulnerability_scan(self) -> dict:
        """Run automated vulnerability scanning on live subdomains using multiple tools"""
        vuln_results = {
            'nuclei_findings': [],
            'nikto_findings': [],
            'whatweb_findings': [],
            'ssl_findings': [],
            'total_vulnerabilities': 0,
            'critical_count': 0,
            'high_count': 0,
            'medium_count': 0,
            'low_count': 0,
            'info_count': 0
        }
        
        if not self.live_subdomains:
            console.print("[yellow]No live subdomains to scan[/yellow]")
            return vuln_results
        
        # Ensure vulnerability scanning tools are available
        self._ensure_vuln_tools_installed()
        
        # Create URLs file for scanning
        urls_file = 'reports/live_subdomains.txt'
        with open(urls_file, 'w') as f:
            for subdomain in self.live_subdomains:
                f.write(f"https://{subdomain}\n")
                f.write(f"http://{subdomain}\n")
        
        console.print(f"[cyan]Scanning {len(self.live_subdomains)} live subdomains for vulnerabilities...[/cyan]")
        
        # Run Nuclei vulnerability scanner
        vuln_results['nuclei_findings'] = self._run_nuclei_scan(urls_file)
        
        # Run additional scans if tools are available
        vuln_results['whatweb_findings'] = self._run_whatweb_scan()
        vuln_results['ssl_findings'] = self._run_ssl_scan()
        
        # Calculate vulnerability counts
        for finding in vuln_results['nuclei_findings']:
            severity = finding.get('severity', 'info').lower()
            vuln_results['total_vulnerabilities'] += 1
            
            if severity == 'critical':
                vuln_results['critical_count'] += 1
            elif severity == 'high':
                vuln_results['high_count'] += 1
            elif severity == 'medium':
                vuln_results['medium_count'] += 1
            elif severity == 'low':
                vuln_results['low_count'] += 1
            else:
                vuln_results['info_count'] += 1
        
        console.print(f"[green]Vulnerability scanning complete. Found {vuln_results['total_vulnerabilities']} potential issues.[/green]")
        return vuln_results
    
    def _ensure_vuln_tools_installed(self):
        """Ensure vulnerability scanning tools are installed"""
        console.print("[cyan]Checking vulnerability scanning tools...[/cyan]")
        
        # Check Nuclei
        try:
            subprocess.run(['nuclei', '-version'], capture_output=True, check=True)
            console.log("Nuclei is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            console.print("[yellow]Installing Nuclei...[/yellow]")
            try:
                subprocess.run([
                    'go', 'install', '-v', 'github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest'
                ], check=True)
                console.log("Nuclei installed successfully")
            except Exception as e:
                console.print(f"[red]Failed to install Nuclei: {e}[/red]")
        
        # Update Nuclei templates
        try:
            console.print("[cyan]Updating Nuclei templates...[/cyan]")
            subprocess.run(['nuclei', '-update-templates'], capture_output=True, timeout=60)
            console.log("Nuclei templates updated")
        except Exception as e:
            console.print(f"[yellow]Could not update Nuclei templates: {e}[/yellow]")
    
    def _run_nuclei_scan(self, urls_file: str) -> list:
        """Run Nuclei vulnerability scanner"""
        nuclei_findings = []
        nuclei_output = 'reports/nuclei_results.json'
        
        try:
            console.print("[cyan]Running Nuclei vulnerability scan...[/cyan]")
            
            # Run Nuclei with comprehensive templates
            cmd = [
                'nuclei',
                '-list', urls_file,
                '-json',
                '-o', nuclei_output,
                '-severity', 'critical,high,medium,low',
                '-tags', 'cve,xss,sqli,rce,lfi,ssrf,redirect,exposure',
                '-timeout', '10',
                '-retries', '2',
                '-rate-limit', '100'
            ]
            
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if os.path.exists(nuclei_output):
                with open(nuclei_output, 'r') as f:
                    for line in f:
                        try:
                            finding = json.loads(line.strip())
                            nuclei_findings.append(finding)
                        except json.JSONDecodeError:
                            continue
                
                console.print(f"[green]Nuclei found {len(nuclei_findings)} potential vulnerabilities[/green]")
            else:
                console.print("[yellow]No Nuclei results file generated[/yellow]")
                
        except subprocess.TimeoutExpired:
            console.print("[yellow]Nuclei scan timed out after 5 minutes[/yellow]")
        except Exception as e:
            console.print(f"[red]Error running Nuclei: {str(e)}[/red]")
        
        return nuclei_findings
    
    def _run_whatweb_scan(self) -> list:
        """Run WhatWeb for technology detection"""
        whatweb_findings = []
        
        try:
            console.print("[cyan]Running WhatWeb technology detection...[/cyan]")
            
            for subdomain in list(self.live_subdomains)[:10]:  # Limit to first 10 to avoid timeout
                try:
                    cmd = ['whatweb', '--log-json=reports/whatweb_temp.json', f"https://{subdomain}"]
                    subprocess.run(cmd, capture_output=True, timeout=30)
                    
                    if os.path.exists('reports/whatweb_temp.json'):
                        with open('reports/whatweb_temp.json', 'r') as f:
                            for line in f:
                                try:
                                    finding = json.loads(line.strip())
                                    finding['subdomain'] = subdomain
                                    whatweb_findings.append(finding)
                                except json.JSONDecodeError:
                                    continue
                        os.remove('reports/whatweb_temp.json')
                        
                except subprocess.TimeoutExpired:
                    continue
                except Exception:
                    continue
                    
        except Exception as e:
            console.print(f"[yellow]WhatWeb scan failed: {str(e)}[/yellow]")
        
        return whatweb_findings
    
    def _run_ssl_scan(self) -> list:
        """Run SSL/TLS configuration analysis"""
        ssl_findings = []
        
        try:
            console.print("[cyan]Analyzing SSL/TLS configurations...[/cyan]")
            
            for subdomain in list(self.live_subdomains)[:5]:  # Limit to avoid timeout
                try:
                    # Use openssl to check SSL certificate
                    cmd = ['openssl', 's_client', '-connect', f"{subdomain}:443", '-servername', subdomain]
                    process = subprocess.run(cmd, input="\n", capture_output=True, text=True, timeout=10)
                    
                    ssl_info = {
                        'subdomain': subdomain,
                        'ssl_available': False,
                        'certificate_info': '',
                        'issues': []
                    }
                    
                    if process.returncode == 0:
                        ssl_info['ssl_available'] = True
                        
                        # Parse certificate information
                        if 'Certificate chain' in process.stdout:
                            ssl_info['certificate_info'] = 'Valid SSL certificate found'
                        
                        # Check for common SSL issues
                        if 'verify error' in process.stdout.lower():
                            ssl_info['issues'].append('Certificate verification error')
                        if 'self signed' in process.stdout.lower():
                            ssl_info['issues'].append('Self-signed certificate')
                        if 'expired' in process.stdout.lower():
                            ssl_info['issues'].append('Expired certificate')
                    else:
                        ssl_info['issues'].append('SSL/TLS not available or accessible')
                    
                    ssl_findings.append(ssl_info)
                    
                except subprocess.TimeoutExpired:
                    ssl_findings.append({
                        'subdomain': subdomain,
                        'ssl_available': False,
                        'issues': ['SSL scan timeout']
                    })
                except Exception:
                    continue
                    
        except Exception as e:
            console.print(f"[yellow]SSL scan failed: {str(e)}[/yellow]")
        
        return ssl_findings
    
    def _generate_vulnerability_report(self, vuln_results: dict, output_path: str):
        """Generate comprehensive vulnerability assessment PDF report"""
        
        class VulnPDF(FPDF):
            def __init__(self):
                super().__init__()
                self.logo_path = 'Images/logo.png' if os.path.exists('Images/logo.png') else None
                
            def header(self):
                """Add header with logo to every page"""
                if self.logo_path:
                    try:
                        logo_width = 25
                        logo_height = 20
                        x_pos = self.w - logo_width - 10
                        self.image(self.logo_path, x_pos, 8, logo_width, logo_height)
                    except Exception:
                        pass
                
                self.set_font('Arial', 'B', 12)
                self.set_text_color(255, 255, 255)
                self.cell(0, 10, 'TrimurtiSec Vulnerability Assessment Report', 0, 0, 'L')
                self.ln(15)
                
            def footer(self):
                """Add footer to every page"""
                self.set_y(-15)
                self.set_font('Arial', '', 8)
                self.set_text_color(200, 200, 200)
                self.cell(0, 10, f'TrimurtiSec Vulnerability Report | Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")} | Page {self.page_no()}', 0, 0, 'C')
        
        pdf = VulnPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        font_family = 'Arial'
        console.print("[cyan]Generating vulnerability assessment report...[/cyan]")
        
        # Title Page with Logo
        if pdf.logo_path:
            try:
                logo_width = 60
                logo_height = 45
                x_pos = (pdf.w - logo_width) / 2
                pdf.set_xy(x_pos, 50)
                pdf.image(pdf.logo_path, x_pos, 50, logo_width, logo_height)
                pdf.ln(50)
            except Exception:
                pdf.ln(30)
        else:
            pdf.ln(30)
        
        pdf.set_font(font_family, 'B', 28)
        pdf.set_text_color(0, 255, 0)  # Green
        pdf.cell(0, 20, 'TrimurtiSec Vulnerability Assessment', 0, 1, 'C')
        
        pdf.set_font(font_family, 'B', 18)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 15, 'Automated Security Vulnerability Scan', 0, 1, 'C')
        
        pdf.ln(20)
        pdf.set_font(font_family, '', 14)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 10, f"Target Domain: {self.target}", 0, 1, 'C')
        pdf.cell(0, 8, f"Scan Date: {datetime.now().strftime('%B %d, %Y')}", 0, 1, 'C')
        pdf.cell(0, 8, f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}", 0, 1, 'C')
        
        # Risk level assessment
        total_vulns = vuln_results['total_vulnerabilities']
        critical_count = vuln_results['critical_count']
        high_count = vuln_results['high_count']
        medium_count = vuln_results['medium_count']
        
        if critical_count > 0:
            risk_level = "CRITICAL"
            risk_color = (139, 0, 0)  # Dark red
        elif high_count > 0:
            risk_level = "HIGH"
            risk_color = (255, 0, 0)  # Red
        elif medium_count > 0:
            risk_level = "MEDIUM"
            risk_color = (255, 255, 0)  # Yellow
        elif total_vulns > 0:
            risk_level = "LOW"
            risk_color = (0, 255, 0)  # Green
        else:
            risk_level = "INFORMATIONAL"
            risk_color = (0, 255, 0)  # Green
        
        pdf.ln(30)
        pdf.set_font(font_family, 'B', 16)
        pdf.set_text_color(255, 215, 0)  # Gold
        pdf.cell(0, 10, f'OVERALL RISK LEVEL: {risk_level}', 0, 1, 'C')
        
        # Add new page for executive summary
        pdf.add_page()
        pdf.ln(10)
        
        # Executive Summary
        pdf.set_font(font_family, 'B', 20)
        pdf.set_text_color(255, 215, 0)  # Gold
        pdf.cell(0, 15, 'EXECUTIVE SUMMARY', 0, 1, 'L')
        pdf.ln(5)
        
        pdf.set_font(font_family, '', 12)
        pdf.set_text_color(255, 255, 255)
        
        exec_summary = (
            f"This vulnerability assessment report presents the findings from an automated security "
            f"scan conducted against {len(self.live_subdomains)} live subdomains of {self.target}. "
            f"The assessment utilized industry-standard vulnerability scanning tools including Nuclei, "
            f"SSL/TLS analysis, and technology detection to identify potential security weaknesses.\n\n"
            f"The scan identified {total_vulns} total security findings across the target infrastructure. "
            f"These findings include {critical_count} critical, {high_count} high, {medium_count} medium, "
            f"{vuln_results['low_count']} low, and {vuln_results['info_count']} informational issues. "
            f"Each finding requires appropriate remediation based on its severity level and potential impact."
        )
        
        # Wrap executive summary text
        words = exec_summary.split()
        line = ""
        for word in words:
            if pdf.get_string_width(line + word + " ") < 180:
                line += word + " "
            else:
                pdf.cell(0, 6, line.strip(), 0, 1, 'L')
                line = word + " "
        if line:
            pdf.cell(0, 6, line.strip(), 0, 1, 'L')
        
        pdf.ln(15)
        
        # Vulnerability Summary Table
        pdf.set_font(font_family, 'B', 16)
        pdf.cell(0, 10, 'VULNERABILITY SUMMARY', 0, 1, 'L')
        pdf.ln(5)
        
        # Create summary table
        pdf.set_font(font_family, 'B', 12)
        pdf.set_fill_color(70, 130, 180)
        pdf.set_text_color(255, 255, 255)
        
        col_widths = {'Severity': 40, 'Count': 30, 'Risk Level': 60, 'Priority': 60}
        for header, width in col_widths.items():
            pdf.cell(width, 10, header, 1, 0, 'C', 1)
        pdf.ln()
        
        pdf.set_font(font_family, '', 11)
        pdf.set_text_color(255, 255, 255)
        
        severity_data = [
            ('Critical', critical_count, 'Immediate Action Required', 'P1 - Fix Immediately'),
            ('High', high_count, 'High Risk', 'P2 - Fix Within 24h'),
            ('Medium', medium_count, 'Medium Risk', 'P3 - Fix Within 1 Week'),
            ('Low', vuln_results['low_count'], 'Low Risk', 'P4 - Fix Within 1 Month'),
            ('Info', vuln_results['info_count'], 'Informational', 'P5 - Monitor')
        ]
        
        fill = False
        for severity, count, risk, priority in severity_data:
            if count > 0:  # Only show rows with findings
                pdf.set_fill_color(245, 245, 245) if fill else pdf.set_fill_color(255, 255, 255)
                pdf.cell(col_widths['Severity'], 8, severity, 1, 0, 'L', 1)
                pdf.cell(col_widths['Count'], 8, str(count), 1, 0, 'C', 1)
                pdf.cell(col_widths['Risk Level'], 8, risk, 1, 0, 'L', 1)
                pdf.cell(col_widths['Priority'], 8, priority, 1, 1, 'L', 1)
                fill = not fill
        
        pdf.ln(10)
        
        # Detailed Findings Section
        if vuln_results['nuclei_findings']:
            pdf.add_page()
            pdf.ln(10)
            
            pdf.set_font(font_family, 'B', 20)
            pdf.set_text_color(255, 215, 0)  # Gold
            pdf.cell(0, 15, 'DETAILED VULNERABILITY FINDINGS', 0, 1, 'L')
            pdf.ln(5)
            
            # Group findings by severity
            findings_by_severity = {
                'critical': [],
                'high': [],
                'medium': [],
                'low': [],
                'info': []
            }
            
            for finding in vuln_results['nuclei_findings']:
                severity = finding.get('severity', 'info').lower()
                findings_by_severity[severity].append(finding)
            
            # Display findings by severity (highest first)
            for severity in ['critical', 'high', 'medium', 'low', 'info']:
                if findings_by_severity[severity]:
                    pdf.set_font(font_family, 'B', 16)
                    pdf.set_text_color(255, 215, 0)  # Gold
                    pdf.cell(0, 10, f'{severity.upper()} SEVERITY FINDINGS ({len(findings_by_severity[severity])})', 0, 1, 'L')
                    pdf.ln(3)
                    
                    for i, finding in enumerate(findings_by_severity[severity][:10], 1):  # Limit to 10 per severity
                        pdf.set_font(font_family, '', 12)
                        pdf.set_text_color(255, 255, 255)
                        
                        finding_title = finding.get('info', {}).get('name', 'Unknown Vulnerability')
                        pdf.cell(0, 8, f"{i}. {finding_title}", 0, 1, 'L')
                        
                        pdf.set_font(font_family, '', 10)
                        pdf.set_text_color(255, 255, 255)
                        
                        # Add finding details
                        details = [
                            f"Target: {finding.get('matched-at', 'N/A')}",
                            f"Template: {finding.get('template-id', 'N/A')}",
                            f"Type: {finding.get('type', 'N/A')}"
                        ]
                        
                        description = finding.get('info', {}).get('description', '')
                        if description:
                            details.append(f"Description: {description[:100]}{'...' if len(description) > 100 else ''}")
                        
                        for detail in details:
                            pdf.cell(0, 6, f"  {detail}", 0, 1, 'L')
                        
                        pdf.ln(3)
        
        # SSL/TLS Findings
        if vuln_results['ssl_findings']:
            pdf.add_page()
            pdf.ln(10)
            
            pdf.set_font(font_family, 'B', 20)
            pdf.set_text_color(255, 215, 0)  # Gold
            pdf.cell(0, 15, 'SSL/TLS CONFIGURATION ANALYSIS', 0, 1, 'L')
            pdf.ln(5)
            
            for ssl_finding in vuln_results['ssl_findings']:
                pdf.set_font(font_family, '', 12)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 8, f"Subdomain: {ssl_finding['subdomain']}", 0, 1, 'L')
                
                pdf.set_font(font_family, '', 10)
                pdf.set_text_color(255, 255, 255)
                
                if ssl_finding.get('ssl_available'):
                    pdf.cell(0, 6, f"  SSL/TLS: Available", 0, 1, 'L')
                    pdf.cell(0, 6, f"  Certificate: {ssl_finding.get('certificate_info', 'N/A')}", 0, 1, 'L')
                else:
                    pdf.cell(0, 6, f"  SSL/TLS: Not Available", 0, 1, 'L')
                
                if ssl_finding.get('issues'):
                    pdf.cell(0, 6, f"  Issues: {', '.join(ssl_finding['issues'])}", 0, 1, 'L')
                
                pdf.ln(3)
        
        # Recommendations
        pdf.add_page()
        pdf.ln(10)
        
        pdf.set_font(font_family, 'B', 20)
        pdf.set_text_color(255, 215, 0)  # Gold
        pdf.cell(0, 15, 'SECURITY RECOMMENDATIONS', 0, 1, 'L')
        pdf.ln(5)
        
        pdf.set_font(font_family, '', 11)
        pdf.set_text_color(255, 255, 255)
        
        recommendations = [
            "4.1 Immediate Actions:",
            "- Conduct comprehensive vulnerability scanning on all live subdomains",
            "- Review subdomain inventory for unnecessary or forgotten services",
            "- Implement proper access controls and authentication mechanisms",
            "- Ensure all subdomains are regularly updated and patched",
            "",
            "4.2 Security Hardening:",
            "- Deploy Web Application Firewalls (WAF) where appropriate",
            "- Implement SSL/TLS certificates for all web services",
            "- Configure proper HTTP security headers",
            "- Review and minimize exposed services and ports",
            "",
            "4.3 Monitoring and Maintenance:",
            "- Establish continuous subdomain monitoring",
            "- Implement intrusion detection systems",
            "- Regular security assessments and penetration testing",
            "- Maintain an updated asset inventory",
            "",
            "4.4 Risk Mitigation:",
            "- Decommission unused subdomains and services",
            "- Implement network segmentation where possible",
            "- Regular backup and disaster recovery testing",
            "- Staff security awareness training"
        ]
        
        for line in recommendations:
            if line.startswith('- '):
                pdf.set_font(font_family, 'I', 11)  # Italic for bullet points
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 8, line, 0, 1, 'L')
                pdf.set_font(font_family, '', 11)  # Restore normal font after bullet
            elif line.strip() == '':
                pdf.ln(3)
            else:
                pdf.set_font(font_family, 'B', 12)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 8, line, 0, 1, 'L')
        
        try:
            pdf.output(output_path)
            console.print(f"[green]Vulnerability report generated successfully: {output_path}[/green]")
        except Exception as e:
            console.print(f"[red]Error generating vulnerability report: {e}[/red]")

    def get_results_for_analysis(self):
        """
        Returns the formatted subdomain discovery results as a string,
        suitable for AI analysis or reporting.
        """
        return self._format_results()
