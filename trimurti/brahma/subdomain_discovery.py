import socket
import subprocess
import json
import os
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
                """Add header with logo to every page"""
                if self.logo_path:
                    try:
                        # Add logo to top-right corner of every page
                        logo_width = 25
                        logo_height = 20
                        x_pos = self.w - logo_width - 10  # 10mm from right edge
                        self.image(self.logo_path, x_pos, 8, logo_width, logo_height)
                    except Exception:
                        pass  # Silently fail if logo can't be loaded
                
                # Add TrimurtiSec text header
                self.set_font('Arial', 'B', 12)
                self.set_text_color(70, 70, 70)
                self.cell(0, 10, 'TrimurtiSec Penetration Testing Framework', 0, 0, 'L')
                self.ln(15)
                
            def footer(self):
                """Add footer to every page"""
                self.set_y(-15)
                self.set_font('Arial', '', 8)
                self.set_text_color(128, 128, 128)
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
                logo_width = 60
                logo_height = 45
                x_pos = (pdf.w - logo_width) / 2  # Center on page
                pdf.set_xy(x_pos, 50)
                pdf.image(pdf.logo_path, x_pos, 50, logo_width, logo_height)
                pdf.ln(50)  # Move down after large logo
            except Exception as e:
                console.print(f"[yellow]Could not load title page logo: {e}[/yellow]")
                pdf.ln(30)
        else:
            pdf.ln(30)
        
        pdf.set_font(font_family, 'B', 28)
        pdf.set_text_color(20, 20, 20)
        pdf.cell(0, 20, 'TrimurtiSec Penetration Test Report', 0, 1, 'C')
        
        pdf.set_font(font_family, 'B', 18)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(0, 15, 'Subdomain Discovery & Reconnaissance', 0, 1, 'C')
        
        pdf.ln(20)
        pdf.set_font(font_family, '', 14)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 10, f"Target Domain: {self.target}", 0, 1, 'C')
        pdf.cell(0, 8, f"Assessment Date: {datetime.now().strftime('%B %d, %Y')}", 0, 1, 'C')
        pdf.cell(0, 8, f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}", 0, 1, 'C')
        
        # Add classification and confidentiality notice
        pdf.ln(30)
        pdf.set_font(font_family, 'B', 12)
        pdf.set_text_color(150, 0, 0)
        pdf.cell(0, 8, 'CONFIDENTIAL - PENETRATION TEST REPORT', 0, 1, 'C')
        
        pdf.set_font(font_family, '', 10)
        pdf.set_text_color(100, 100, 100)
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
        pdf.set_text_color(40, 40, 40)
        pdf.cell(0, 15, 'EXECUTIVE SUMMARY', 0, 1, 'L')
        pdf.ln(5)
        
        # Calculate risk metrics
        total_subdomains = len(self.subdomains)
        live_subdomains = len(self.live_subdomains)
        success_rate = (live_subdomains / max(total_subdomains, 1)) * 100
        
        # Executive summary content
        pdf.set_font(font_family, '', 12)
        pdf.set_text_color(60, 60, 60)
        
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
            risk_color = (0, 150, 0)
            risk_text = (
                "No live subdomains were discovered during this assessment, indicating a minimal "
                "external attack surface for subdomain-based attacks. However, this does not preclude "
                "the existence of subdomains that may be protected by WAF, require authentication, "
                "or are hosted on non-standard ports."
            )
        elif live_subdomains <= 5:
            risk_level = "MEDIUM"
            risk_color = (255, 165, 0)
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
        pdf.set_text_color(40, 40, 40)
        pdf.cell(0, 10, 'KEY FINDINGS', 0, 1, 'L')
        pdf.ln(5)
        
        pdf.set_font(font_family, '', 12)
        pdf.set_text_color(60, 60, 60)
        
        key_findings = [
            f"Total subdomains enumerated: {total_subdomains}",
            f"Live/accessible subdomains: {live_subdomains}",
            f"Subdomain accessibility rate: {success_rate:.1f}%",
            "Tools utilized: Subfinder, HTTPX",
            "Assessment methodology: Passive reconnaissance with active probing"
        ]
        
        for finding in key_findings:
            pdf.cell(8, 8, '-', 0, 0, 'L')
            pdf.cell(0, 8, finding, 0, 1, 'L')
        
        pdf.ln(10)
        
        # Add new page for detailed findings
        pdf.add_page()
        pdf.ln(10)
        
        # Detailed Technical Findings
        pdf.set_font(font_family, 'B', 20)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(0, 15, 'DETAILED TECHNICAL FINDINGS', 0, 1, 'L')
        pdf.ln(5)
        
        # Methodology section
        pdf.set_font(font_family, 'B', 14)
        pdf.cell(0, 10, '1. ASSESSMENT METHODOLOGY', 0, 1, 'L')
        pdf.ln(3)
        
        pdf.set_font(font_family, '', 11)
        pdf.set_text_color(60, 60, 60)
        
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
        pdf.set_text_color(40, 40, 40)
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
            pdf.set_text_color(255, 255, 255)
            
            col_widths = {'Subdomain': 80, 'IP Address': 40, 'Status': 20, 'Server': 50}
            for header, width in col_widths.items():
                pdf.cell(width, 10, header, 1, 0, 'C', 1)
            pdf.ln()

            pdf.set_font(font_family, '', 9)
            pdf.set_text_color(0, 0, 0)
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
        pdf.set_text_color(40, 40, 40)
        pdf.cell(0, 10, '3. COMPLETE SUBDOMAIN INVENTORY', 0, 1, 'L')
        pdf.ln(5)
        
        # Live Subdomains Analysis
        pdf.set_font(font_family, 'B', 14)
        pdf.set_text_color(0, 120, 0)
        pdf.cell(0, 10, f'3.1 Live/Accessible Subdomains ({live_subdomains} found)', 0, 1, 'L')
        pdf.ln(3)
        
        pdf.set_font(font_family, '', 11)
        pdf.set_text_color(60, 60, 60)
        
        if live_subdomains > 0:
            live_analysis = (
                "The following subdomains were confirmed as live and accessible during the assessment. "
                "Each represents a potential entry point that should be subjected to further security "
                "testing including vulnerability scanning, service enumeration, and penetration testing."
            )
            
            # Wrap live analysis text
            words = live_analysis.split()
            line = ""
            for word in words:
                if pdf.get_string_width(line + word + " ") < 180:
                    line += word + " "
                else:
                    pdf.cell(0, 6, line.strip(), 0, 1, 'L')
                    line = word + " "
            if line:
                pdf.cell(0, 6, line.strip(), 0, 1, 'L')
            
            pdf.ln(5)
            
            # List live subdomains with details
            for i, subdomain in enumerate(sorted(self.live_subdomains), 1):
                pdf.set_font(font_family, 'B', 10)
                pdf.set_text_color(0, 100, 0)
                pdf.cell(0, 8, f"{i}. {subdomain}", 0, 1, 'L')
                
                # Add technical details if available
                if os.path.exists('reports/httpx_results.json'):
                    with open('reports/httpx_results.json', 'r') as f:
                        for line in f:
                            try:
                                result = json.loads(line.strip())
                                url = result.get('url', '').replace('https://', '').replace('http://', '')
                                if url == subdomain:
                                    pdf.set_font(font_family, '', 9)
                                    pdf.set_text_color(80, 80, 80)
                                    
                                    details = [
                                        f"   IP Address: {result.get('a', ['N/A'])[0] if result.get('a') else 'N/A'}",
                                        f"   Status Code: {result.get('status_code', 'N/A')}",
                                        f"   Server: {result.get('webserver', 'N/A')}",
                                        f"   Title: {result.get('title', 'N/A')[:50]}{'...' if len(str(result.get('title', ''))) > 50 else ''}"
                                    ]
                                    
                                    for detail in details:
                                        pdf.cell(0, 6, detail, 0, 1, 'L')
                                    break
                            except (json.JSONDecodeError, KeyError):
                                continue
                pdf.ln(2)
        else:
            pdf.cell(0, 8, "No live subdomains were discovered during this assessment.", 0, 1, 'L')
        
        pdf.ln(10)
        
        # Non-responsive Subdomains
        pdf.set_font(font_family, 'B', 14)
        pdf.set_text_color(150, 150, 0)
        non_responsive = len(self.subdomains) - live_subdomains
        pdf.cell(0, 10, f'3.2 Non-Responsive Subdomains ({non_responsive} found)', 0, 1, 'L')
        pdf.ln(3)
        
        pdf.set_font(font_family, '', 11)
        pdf.set_text_color(60, 60, 60)
        
        if non_responsive > 0:
            non_responsive_analysis = (
                "The following subdomains were discovered but did not respond to HTTP/HTTPS probes. "
                "These may be inactive, behind firewalls, using non-standard ports, or configured "
                "to block automated scanning tools. Further investigation may be warranted."
            )
            
            # Wrap non-responsive analysis text
            words = non_responsive_analysis.split()
            line = ""
            for word in words:
                if pdf.get_string_width(line + word + " ") < 180:
                    line += word + " "
                else:
                    pdf.cell(0, 6, line.strip(), 0, 1, 'L')
                    line = word + " "
            if line:
                pdf.cell(0, 6, line.strip(), 0, 1, 'L')
            
            pdf.ln(5)
            
            # List non-responsive subdomains
            non_responsive_list = self.subdomains - self.live_subdomains
            for i, subdomain in enumerate(sorted(non_responsive_list), 1):
                pdf.set_font(font_family, '', 10)
                pdf.set_text_color(120, 120, 0)
                pdf.cell(0, 6, f"{i}. {subdomain}", 0, 1, 'L')
        else:
            pdf.cell(0, 8, "All discovered subdomains were confirmed as live and accessible.", 0, 1, 'L')
        
        pdf.ln(15)
        
        # Recommendations Section
        pdf.set_font(font_family, 'B', 16)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(0, 10, '4. SECURITY RECOMMENDATIONS', 0, 1, 'L')
        pdf.ln(5)
        
        pdf.set_font(font_family, '', 11)
        pdf.set_text_color(60, 60, 60)
        
        recommendations = [
            "4.1 Immediate Actions:\n"
            "- Conduct comprehensive vulnerability scanning on all live subdomains\n"
            "- Review subdomain inventory for unnecessary or forgotten services\n"
            "- Implement proper access controls and authentication mechanisms\n"
            "- Ensure all subdomains are regularly updated and patched\n\n",
            
            "4.2 Security Hardening:\n"
            "- Deploy Web Application Firewalls (WAF) where appropriate\n"
            "- Implement SSL/TLS certificates for all web services\n"
            "- Configure proper HTTP security headers\n"
            "- Review and minimize exposed services and ports\n\n",
            
            "4.3 Monitoring and Maintenance:\n"
            "- Establish continuous subdomain monitoring\n"
            "- Implement intrusion detection systems\n"
            "- Regular security assessments and penetration testing\n"
            "- Maintain an updated asset inventory\n\n",
            
            "4.4 Risk Mitigation:\n"
            "- Decommission unused subdomains and services\n"
            "- Implement network segmentation where possible\n"
            "- Regular backup and disaster recovery testing\n"
            "- Staff security awareness training"
        ]
        
        for recommendation in recommendations:
            lines = recommendation.split('\n')
            for line in lines:
                if line.strip():
                    if line.startswith('4.'):
                        pdf.set_font(font_family, 'B', 12)
                        pdf.set_text_color(40, 40, 40)
                    else:
                        pdf.set_font(font_family, '', 11)
                        pdf.set_text_color(60, 60, 60)
                    pdf.cell(0, 6, line, 0, 1, 'L')
                else:
                    pdf.ln(3)
        
        pdf.ln(10)
        
        # Conclusion
        pdf.set_font(font_family, 'B', 16)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(0, 10, '5. CONCLUSION', 0, 1, 'L')
        pdf.ln(5)
        
        pdf.set_font(font_family, '', 11)
        pdf.set_text_color(60, 60, 60)
        
        conclusion_text = (
            f"This subdomain discovery assessment has provided valuable insights into {self.target}'s "
            f"external digital footprint. The identification of {total_subdomains} subdomains, with "
            f"{live_subdomains} confirmed as accessible, establishes a baseline for further security "
            f"assessments. The findings should be used to prioritize additional penetration testing "
            f"activities and implement appropriate security controls. Regular reassessment is "
            f"recommended to maintain visibility into the evolving attack surface."
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
            # Run HTTPX to find live hosts with status code 200
            cmd = (
                f"httpx -list reports/subfinder_results.txt "
                "-silent "
                "-status-code "
                "-ip "
                "-tech-detect "
                "-mc 200,301,302 "
                "-title "
                "-server "
                "-json "
                "-o reports/httpx_results.json"
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
                                # console.print(f"✅ [green]Found live subdomain: {url}[/green]")
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
            for subdomain in sorted(self.live_subdomains):
                results += f"- {subdomain}\n"
        
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
