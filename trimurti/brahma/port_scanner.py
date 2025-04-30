import nmap
import socket
from rich.console import Console
from rich.progress import Progress
from trimurti.brahma.subdomain_discovery import SubdomainDiscovery

console = Console()

class PortScanner:
    def __init__(self, target):
        self.target = target
        self.nm = nmap.PortScanner()
        
    def scan(self):
        """Perform comprehensive port scan on target"""
        results = "## Port Scan Results\n\n"
        
        try:
            ip = socket.gethostbyname(self.target)
            results += f"Target: {self.target} ({ip})\n\n"
            
            with Progress() as progress:
                task = progress.add_task("[green]Scanning ports...", total=3)
                
                # Basic TCP scan
                console.log(f"Performing TCP scan on {self.target}")
                self.nm.scan(self.target, '1-1000', arguments='-sT -T4')
                progress.update(task, advance=1)
                
                # Service version detection
                console.log("Detecting service versions")
                self.nm.scan(self.target, '1-1000', arguments='-sV')
                progress.update(task, advance=1)
                
                # OS detection
                console.log("Attempting OS detection")
                self.nm.scan(self.target, arguments='-O')
                progress.update(task, advance=1)
            
            # Format results
            results += "### Open Ports\n\n"
            results += "| Port | Service | Version |\n"
            results += "|------|---------|--------|\n"
            
            for host in self.nm.all_hosts():
                for proto in self.nm[host].all_protocols():
                    lport = list(self.nm[host][proto].keys())
                    for port in lport:
                        service = self.nm[host][proto][port]['name']
                        version = self.nm[host][proto][port].get('product', '') + ' ' + self.nm[host][proto][port].get('version', '')
                        results += f"| {port} | {service} | {version} |\n"
            
            # OS detection results
            if 'osmatch' in self.nm[host]:
                results += "\n### OS Detection\n\n"
                for os in self.nm[host]['osmatch']:
                    results += f"- {os['name']} (Accuracy: {os['accuracy']}%)\n"
            
            return results
            
        except Exception as e:
            return f"Error during scan: {str(e)}"

    def discover_subdomains(self):
        """Discover subdomains for the target domain"""
        try:
            subdomain_discoverer = SubdomainDiscovery(self.target)
            return subdomain_discoverer.discover()
        except Exception as e:
            return f"Error during subdomain discovery: {str(e)}" 