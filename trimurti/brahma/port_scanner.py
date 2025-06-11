import nmap
import socket
import asyncio
from functools import lru_cache
from typing import Optional, Dict, Any, List
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
        """Cached scan implementation with error handling"""
        try:
            return self.nm.scan(target, ports, arguments, timeout=self.timeout)
        except nmap.PortScannerError as e:
            console.print(f"[red]Nmap scan error: {str(e)}[/red]")
            raise
        except Exception as e:
            console.print(f"[red]Unexpected error during scan: {str(e)}[/red]")
            raise

    def _format_scan_results(self, scan_data: Dict[str, Any]) -> str:
        """Format scan results into a markdown table"""
        results = "### Open Ports\n\n"
        results += "| Port | Service | Version | State |\n"
        results += "|------|---------|---------|-------|\n"
        
        try:
            for host in self.nm.all_hosts():
                for proto in self.nm[host].all_protocols():
                    lport = list(self.nm[host][proto].keys())
                    for port in lport:
                        port_data = self.nm[host][proto][port]
                        if port_data.get('state') == 'open':
                            service = port_data.get('name', 'unknown')
                            version = f"{port_data.get('product', '')} {port_data.get('version', '')}".strip()
                            state = port_data.get('state', 'unknown')
                            results += f"| {port} | {service} | {version} | {state} |\n"
        except Exception as e:
            console.print(f"[red]Error formatting results: {str(e)}[/red]")
            results += "| Error processing scan results | | | |\n"
        
        return results

    def scan(self, ports: str = '1-1000', scan_type: str = 'comprehensive') -> str:
        """
        Perform port scan on target with different scan types
        
        Args:
            ports: Port range to scan (default: '1-1000')
            scan_type: Type of scan ('quick', 'comprehensive', 'aggressive')
        """
        try:
            results = "## Port Scan Results\n\n"
            ip = socket.gethostbyname(self.target)
            results += f"Target: {self.target} ({ip})\n\n"
            
            scan_args = {
                'quick': '-sT -T4 --max-retries 2',
                'comprehensive': '-sT -sV -sC -T4 --max-retries 3',
                'aggressive': '-sT -sV -sC -T4 --max-retries 3'
            }
            
            with Progress() as progress:
                task = progress.add_task("[green]Scanning ports...", total=2)
                
                # Initial TCP Connect scan (no root required)
                console.log(f"Performing initial scan on {self.target}")
                initial_scan = self._perform_scan(self.target, ports, scan_args[scan_type])
                progress.update(task, advance=1)
                
                # Service version detection
                console.log("Detecting service versions")
                version_scan = self._perform_scan(self.target, ports, '-sT -sV --version-intensity 5')
                progress.update(task, advance=1)
            
            # Combine and format results
            results += self._format_scan_results(initial_scan)
            
            # Add scan statistics
            results += "\n### Scan Statistics\n\n"
            results += f"- Scan Type: {scan_type}\n"
            results += f"- Port Range: {ports}\n"
            results += f"- Scan Duration: {initial_scan.get('nmap', {}).get('scanstats', {}).get('elapsed', 'N/A')} seconds\n"
            
            return results
            
        except Exception as e:
            error_msg = f"Error during scan: {str(e)}"
            console.print(f"[red]{error_msg}[/red]")
            return error_msg

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
    
    def vulnerability_scan(self) -> str:
        """Perform vulnerability scan using nmap scripts"""
        try:
            results = "## Vulnerability Scan Results\n\n"
            ip = socket.gethostbyname(self.target)
            results += f"Target: {self.target} ({ip})\n\n"
            
            with Progress() as progress:
                task = progress.add_task("[green]Running vulnerability scripts...", total=1)
                
                # Run Nmap with vulnerability scripts
                console.log(f"Running vulnerability scan on {self.target}")
                vuln_scan = self._perform_scan(
                    self.target, 
                    '1-1000', 
                    '-sT --script vuln -T4 --max-retries 2'
                )
                progress.update(task, advance=1)
            
            # Format vulnerability results
            results += self._format_vulnerability_results(vuln_scan)
            
            return results
            
        except Exception as e:
            error_msg = f"Error during vulnerability scan: {str(e)}"
            console.print(f"[red]{error_msg}[/red]")
            return error_msg
    
    def _format_vulnerability_results(self, scan_data) -> str:
        """Format vulnerability scan results"""
        results = "### Vulnerability Assessment\n\n"
        results += "| CVE | Severity | Port | Description |\n"
        results += "|-----|----------|------|-------------|\n"
        
        try:
            for host in self.nm.all_hosts():
                if 'hostscript' in self.nm[host]:
                    for script in self.nm[host]['hostscript']:
                        script_id = script.get('id', 'unknown')
                        output = script.get('output', '')
                        
                        # Parse common vulnerability scripts
                        if 'CVE' in output:
                            lines = output.split('\n')
                            for line in lines:
                                if 'CVE-' in line:
                                    cve = line.strip()
                                    results += f"| {cve} | Medium | Multiple | {script_id} detection |\n"
                        else:
                            results += f"| N/A | Info | Multiple | {script_id} |\n"
                            
                for proto in self.nm[host].all_protocols():
                    lport = list(self.nm[host][proto].keys())
                    for port in lport:
                        port_data = self.nm[host][proto][port]
                        if 'script' in port_data:
                            for script_name, script_output in port_data['script'].items():
                                if 'vuln' in script_name.lower():
                                    results += f"| N/A | Medium | {port} | {script_name} |\n"
                                    
        except Exception as e:
            console.print(f"[red]Error formatting vulnerability results: {str(e)}[/red]")
            results += "| Error processing vulnerability results | | | |\n"
        
        results += "\n### Vulnerability Summary\n\n"
        results += "- Scan completed with Nmap vulnerability scripts\n"
        results += "- Results show potential security issues\n"
        results += "- Manual verification recommended for critical findings\n"
        
        return results
