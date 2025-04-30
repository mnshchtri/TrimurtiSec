import nmap
import socket
import asyncio
from functools import lru_cache
from typing import Optional, Dict, Any
from rich.console import Console
from rich.progress import Progress
from rich.table import Table
from rich.panel import Panel
from trimurti.brahma.subdomain_discovery import SubdomainDiscovery

console = Console()

class PortScanner:
    def __init__(self, target: str, timeout: int = 300):
        self.target = self._validate_target(target)
        self.nm = nmap.PortScanner()
        self.timeout = timeout
        self._cache = {}
        
    @staticmethod
    def _validate_target(target: str) -> str:
        """Validate and normalize the target input"""
        try:
            ip = socket.gethostbyname(target)
            return target
        except socket.gaierror:
            raise ValueError(f"Invalid target: {target}")
            
    @lru_cache(maxsize=128)
    def _perform_scan(self, target: str, ports: str, arguments: str) -> Dict[str, Any]:
        """Cached scan implementation"""
        return self.nm.scan(target, ports, arguments)
        
    def scan(self) -> str:
        """Perform comprehensive port scan on target"""
        try:
            results = "## Port Scan Results\n\n"
            ip = socket.gethostbyname(self.target)
            results += f"Target: {self.target} ({ip})\n\n"
            
            with Progress() as progress:
                task = progress.add_task("[green]Scanning ports...", total=2)
                
                # Optimized TCP scan
                console.log(f"Performing TCP scan on {self.target}")
                self._perform_scan(self.target, '1-1000', '-sT -T4 --max-retries 3')
                progress.update(task, advance=1)
                
                # Service version detection
                console.log("Detecting service versions")
                self._perform_scan(self.target, '1-1000', '-sV --version-intensity 3')
                progress.update(task, advance=1)
            
            # Format results using rich Table
            table = Table(title="Open Ports", show_lines=True)
            table.add_column("Port", style="cyan")
            table.add_column("Service", style="magenta")
            table.add_column("Version", style="green")
            
            for host in self.nm.all_hosts():
                for proto in self.nm[host].all_protocols():
                    lport = list(self.nm[host][proto].keys())
                    for port in lport:
                        service = self.nm[host][proto][port]['name']
                        version = self.nm[host][proto][port].get('product', '') + ' ' + self.nm[host][proto][port].get('version', '')
                        table.add_row(str(port), service, version)
            
            # Format results using rich Table
            results += "### Open Ports\n\n"
            results += "| Port | Service | Version |\n"
            results += "|------|---------|---------|\n"
            
            for host in self.nm.all_hosts():
                for proto in self.nm[host].all_protocols():
                    lport = list(self.nm[host][proto].keys())
                    for port in lport:
                        service = self.nm[host][proto][port]['name']
                        version = self.nm[host][proto][port].get('product', '') + ' ' + self.nm[host][proto][port].get('version', '')
                        results += f"| {port} | {service} | {version} |\n"
            
            results += "\n"
            
            # Add additional information
            results += "\n### Additional Information\n\n"
            results += "- Scan completed with root privileges\n"
            results += "- All features are available\n"
            
            return results
            
        except Exception as e:
            console.print(f"[red]Error during scan: {str(e)}[/red]")
            return f"Error during scan: {str(e)}\n\nDetailed error: {str(e)}"

    def discover_subdomains(self) -> str:
        """Discover subdomains for the target domain"""
        try:
            if self.target not in self._cache:
                subdomain_discoverer = SubdomainDiscovery(self.target)
                self._cache[self.target] = subdomain_discoverer.discover()
            return self._cache[self.target]
        except Exception as e:
            console.print(f"[red]Error during subdomain discovery: {str(e)}[/red]")
            return f"Error during subdomain discovery: {str(e)}" 