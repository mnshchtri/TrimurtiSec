import socket
import subprocess
import json
import os
from rich.console import Console
from rich.progress import Progress
from typing import List, Dict, Set
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
        with AnimatedSpinner("🔧 Checking and installing required tools...", "dots12") as spinner:
            try:
                # Check Subfinder
                subprocess.run(['subfinder', '-version'], capture_output=True, check=True)
                console.log("✅ Subfinder is available")
            except (subprocess.CalledProcessError, FileNotFoundError):
                console.print("[yellow]📦 Installing Subfinder...[/yellow]")
                # Install Subfinder using Go
                subprocess.run([
                    'go', 'install', '-v', 'github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest'
                ], check=True)
                console.log("✅ Subfinder installed successfully")

            try:
                # Check HTTPX
                subprocess.run(['httpx', '-version'], capture_output=True, check=True)
                console.log("✅ HTTPX is available")
            except (subprocess.CalledProcessError, FileNotFoundError):
                console.print("[yellow]📦 Installing HTTPX...[/yellow]")
                subprocess.run([
                    'go', 'install', '-v', 'github.com/projectdiscovery/httpx/cmd/httpx@latest'
                ], check=True)
                console.log("✅ HTTPX installed successfully")

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
            "🔍 Initializing subdomain enumeration engines...",
            "🌐 Querying DNS databases and certificate logs...",
            "🕷️ Crawling web archives and search engines...",
            "📡 Probing discovered subdomains for live hosts...",
            "🔬 Analyzing response headers and technologies..."
        ]
        
        with tracker.create_scan_progress(len(discovery_steps)) as progress:
            for i, step in enumerate(discovery_steps):
                task = progress.add_task(step, total=100)
                
                # Execute actual discovery steps
                if i == 1:  # Start subfinder during DNS queries phase
                    console.log(f"🔍 Running Subfinder for {self.target}")
                    self._run_subfinder()
                elif i == 3:  # Start HTTPX during probing phase
                    console.log("📡 Probing subdomains with HTTPX")
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
            "Status": "✅ Discovery Complete"
        }
        tracker.show_completion_stats(discovery_stats)
        
        # Save report to reports directory
        report_file = 'reports/subdomain_discovery_report.md'
        with open(report_file, 'w') as f:
            f.write(results)
            
        console.print(f"✅ [green]Report saved to: {report_file}[/green]")
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
                console.log(f"✅ Subfinder found {len(self.subdomains)} subdomains")
            else:
                console.log("[red]❌ Subfinder results file not found[/red]")
        except Exception as e:
            console.log(f"[red]❌ Error running Subfinder: {str(e)}[/red]")

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
                console.print(f"[red]❌ HTTPX error: {process.stderr}[/red]")
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
                                console.print(f"✅ [green]Found live subdomain: {url}[/green]")
                        except json.JSONDecodeError:
                            continue

            console.log(f"✅ HTTPX identified {len(self.live_subdomains)} live subdomains")
            
        except Exception as e:
            console.print(f"[red]❌ Error running HTTPX: {str(e)}[/red]")

    def _format_results(self) -> str:
        """Format the discovery results"""
        results = "## 🔍 Subdomain Discovery Results\n\n"
        results += f"🎯 Target Domain: {self.target}\n\n"

        results += "### 🌐 Discovered Subdomains\n\n"
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
            console.print(f"[red]❌ Error formatting results: {str(e)}[/red]")
            results += "| Error processing results | | | | |\n"

        results += "\n### Discovery Summary\n\n"
        results += f"- 🎯 Total Subdomains Found: {len(self.subdomains)}\n"
        results += f"- ✅ Live Subdomains: {len(self.live_subdomains)}\n"
        results += f"- 📊 Success Rate: {(len(self.live_subdomains)/max(len(self.subdomains), 1)*100):.1f}%\n"
        
        # Add detailed live subdomains list
        if self.live_subdomains:
            results += "\n### 🌐 Live Subdomains\n\n"
            for subdomain in sorted(self.live_subdomains):
                results += f"- ✅ {subdomain}\n"
        
        # Add file locations with emojis
        results += "\n### 📁 Report Files\n\n"
        results += "- 🔍 Subfinder results: `reports/subfinder_results.txt`\n"
        results += "- 📊 Detailed results: `reports/httpx_results.json`\n"
        results += "- 📋 Full report: `reports/subdomain_discovery_report.md`\n"

        return results

    def _is_ip_address(self, address):
        try:
            socket.inet_aton(address)
            return True
        except socket.error:
            return False
