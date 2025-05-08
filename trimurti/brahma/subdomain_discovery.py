import socket
import dns.resolver
import dns.query
import dns.zone
import requests
import subprocess
import json
import os
from rich.console import Console
from rich.progress import Progress
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Set

console = Console()

class SubdomainDiscovery:
    def __init__(self, target):
        self.target = target
        self.subdomains = set()
        self.live_subdomains = set()
        self.status_codes = {
            '2xx': [200, 201, 202, 203],
            '4xx': [400, 401, 402, 403],
            '5xx': [500, 501, 502, 503]
        }
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
            task = progress.add_task("[green]Discovering subdomains...", total=4)

            # Subfinder enumeration
            console.log(f"Running Subfinder for {self.target}")
            self._run_subfinder()
            progress.update(task, advance=1)

            # HTTPX probing
            console.log("Probing subdomains with HTTPX")
            self._probe_with_httpx()
            progress.update(task, advance=1)

            # Certificate transparency
            console.log("Checking certificate transparency logs")
            self._check_certificate_transparency()
            progress.update(task, advance=1)

            # Zone transfer
            console.log("Attempting DNS zone transfer")
            self._attempt_zone_transfer()
            progress.update(task, advance=1)

        # Format results
        results += self._format_results()
        return results

    def _run_subfinder(self):
        """Run Subfinder for subdomain enumeration"""
        try:
            # Run Subfinder with various options
            cmd = f"subfinder -d {self.target} -silent -o subfinder_results.txt"
            subprocess.run(cmd, shell=True, check=True)
            
            # Parse results
            if os.path.exists('subfinder_results.txt'):
                with open('subfinder_results.txt', 'r') as f:
                    for line in f:
                        subdomain = line.strip()
                        if subdomain:
                            self.subdomains.add(subdomain)
            else:
                console.log("[red]Subfinder results file not found[/red]")
        except Exception as e:
            console.log(f"[red]Error running Subfinder: {str(e)}[/red]")

    def _probe_with_httpx(self):
        """Probe subdomains with HTTPX using two-step approach"""
        try:
            # Save subdomains to temporary file
            with open('temp_subdomains.txt', 'w') as f:
                for subdomain in self.subdomains:
                    f.write(f"{subdomain}\n")

            console.print("[yellow]Running HTTPX probe (Step 1: Finding live hosts)...[/yellow]")
            
            # Step 1: Find live hosts with 2xx status codes
            cmd1 = (
                "cat temp_subdomains.txt | httpx "
                "-status-code -ip -tech-detect "
                "-match-status 200,201,202,203 "
                "-silent "
                "> live_hosts.txt"
            )
            
            process1 = subprocess.run(cmd1, shell=True, capture_output=True, text=True)
            if process1.returncode != 0:
                console.print(f"[red]HTTPX Step 1 error: {process1.stderr}[/red]")
                return

            console.print("[yellow]Running HTTPX probe (Step 2: Getting detailed information)...[/yellow]")
            
            # Step 2: Get detailed information for all hosts
            cmd2 = (
                "cat temp_subdomains.txt | httpx "
                "-location -status-code -server -title "
                "-filter-status 400,401,402,403 "
                "-json "
                "-o httpx_results.json"
            )
            
            process2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True)
            if process2.returncode != 0:
                console.print(f"[red]HTTPX Step 2 error: {process2.stderr}[/red]")
                return

            # Process live hosts
            if os.path.exists('live_hosts.txt'):
                with open('live_hosts.txt', 'r') as f:
                    for line in f:
                        subdomain = line.strip()
                        if subdomain:
                            self.live_subdomains.add(subdomain)
                            console.print(f"[green]Found live subdomain: {subdomain}[/green]")

            # Clean up temporary files
            for file in ['temp_subdomains.txt', 'live_hosts.txt']:
                if os.path.exists(file):
                    os.remove(file)

        except Exception as e:
            console.print(f"[red]Error running HTTPX: {str(e)}[/red]")

    def _format_results(self) -> str:
        """Format the discovery results"""
        results = "### Discovered Subdomains\n\n"
        results += "| Subdomain | IP Address | Status Code | Server | Title |\n"
        results += "|:----------|:-----------|:------------|:-------|:------|\n"

        if not self.subdomains:
            results += "| No subdomains discovered | | | | |\n"
            return results

        try:
            if os.path.exists('httpx_results.json'):
                with open('httpx_results.json', 'r') as f:
                    for line in f:
                        try:
                            result = json.loads(line.strip())
                            subdomain = result.get('url', '').replace('https://', '').replace('http://', '')
                            ip = result.get('ip', 'N/A')
                            status = result.get('status_code', 'N/A')
                            server = result.get('server', 'N/A')
                            title = result.get('title', 'N/A')
                            
                            # Format the row with proper alignment
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
        
        return results

    def _is_ip_address(self, address):
        try:
            socket.inet_aton(address)
            return True
        except socket.error:
            return False

    def _check_certificate_transparency(self):
        url = f"https://crt.sh/?q=%.{self.target}&output=json"
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                try:
                    data = response.json()
                    for entry in data:
                        domain = entry.get('name_value', '').lower()
                        if domain.startswith('*.'):
                            domain = domain[2:]
                        if domain.endswith(self.target) and domain != self.target:
                            self.subdomains.add(domain.strip())
                except ValueError:
                    console.log("Failed to parse JSON from crt.sh")
        except Exception as e:
            console.log(f"Error checking certificate transparency: {str(e)}")

    def _attempt_zone_transfer(self):
        try:
            ns_records = dns.resolver.resolve(self.target, 'NS')
            for ns in ns_records:
                nameserver = str(ns).rstrip('.')
                console.log(f"Trying zone transfer on {nameserver}")
                try:
                    zone = dns.zone.from_xfr(dns.query.xfr(nameserver, self.target))
                    for name, _ in zone.nodes.items():
                        subdomain = f"{name}.{self.target}".lower()
                        if subdomain != self.target:
                            self.subdomains.add(subdomain)
                    console.log(f"Zone transfer successful on {nameserver}")
                except Exception:
                    console.log(f"Zone transfer failed or denied on {nameserver}")
        except Exception as e:
            console.log(f"Error retrieving NS records: {str(e)}")
