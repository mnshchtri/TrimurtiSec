import socket
import subprocess
import json
import os
from rich.console import Console
from rich.progress import Progress
from typing import List, Dict, Set

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
        try:
            # Check Subfinder
            subprocess.run(['subfinder', '-version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            console.print("[yellow]Installing Subfinder...[/yellow]")
            # Install Subfinder using Go
            subprocess.run([
                'go', 'install', '-v', 'github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest'
            ], check=True)

        try:
            # Check HTTPX
            subprocess.run(['httpx', '-version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            console.print("[yellow]Installing HTTPX...[/yellow]")
            subprocess.run([
                'go', 'install', '-v', 'github.com/projectdiscovery/httpx/cmd/httpx@latest'
            ], check=True)

    def discover(self) -> str:
        results = "## Subdomain Discovery Results\n\n"

        if self._is_ip_address(self.target):
            return "Subdomain discovery requires a domain name, not an IP address."

        results += f"Target Domain: {self.target}\n\n"

        with Progress() as progress:
            task = progress.add_task("[green]Discovering subdomains...", total=2)

            # Subfinder enumeration
            console.log(f"Running Subfinder for {self.target}")
            self._run_subfinder()
            progress.update(task, advance=1)

            # HTTPX probing
            console.log("Probing subdomains with HTTPX")
            self._probe_with_httpx()
            progress.update(task, advance=1)

        # Format results
        results += self._format_results()
        
        # Save report to reports directory
        report_file = 'reports/subdomain_discovery_report.md'
        with open(report_file, 'w') as f:
            f.write(results)
            
        console.print(f"[green]Report saved to: {report_file}[/green]")
        return results

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
                                console.print(f"[green]Found live subdomain: {url}[/green]")
                        except json.JSONDecodeError:
                            continue

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

        results += "\n### Scan Summary\n\n"
        results += f"- Total Subdomains Found: {len(self.subdomains)}\n"
        results += f"- Live Subdomains: {len(self.live_subdomains)}\n"
        
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
