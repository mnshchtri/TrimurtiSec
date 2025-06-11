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
from trimurti.utils.enhanced_progress import TrimurtiProgressTracker, EnhancedProgress, AnimatedSpinner

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
        """Cached scan implementation with error handling and progress feedback"""
        try:
            # Add a small delay to make progress animation visible
            import time
            time.sleep(0.5)  # Brief pause for visual effect
            
            result = self.nm.scan(target, ports, arguments, timeout=self.timeout)
            
            # Log scan completion
            console.log(f"✅ Scan completed for {target} with {len(result.get('scan', {}))} hosts")
            return result
            
        except nmap.PortScannerError as e:
            console.print(f"[red]❌ Nmap scan error: {str(e)}[/red]")
            raise
        except Exception as e:
            console.print(f"[red]❌ Unexpected error during scan: {str(e)}[/red]")
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
            # Create enhanced progress tracker
            tracker = TrimurtiProgressTracker('brahma', self.target)
            tracker.create_mode_header()
            
            results = "## Port Scan Results\n\n"
            ip = socket.gethostbyname(self.target)
            results += f"Target: {self.target} ({ip})\n\n"
            
            scan_args = {
                'quick': '-sT -T4 --max-retries 2',
                'comprehensive': '-sT -sV -sC -T4 --max-retries 3',
                'aggressive': '-sT -sV -sC -T4 --max-retries 3'
            }
            
            # Enhanced progress with multiple steps
            with tracker.create_scan_progress(3) as progress:
                # Phase 1: Initial TCP Connect scan
                task1 = progress.add_task("🌐 Establishing connection to target...", total=100)
                for i in range(100):
                    progress.advance(task1, 1)
                    if i == 30:  # Start actual scan partway through animation
                        initial_scan = self._perform_scan(self.target, ports, scan_args[scan_type])
                
                # Phase 2: Service version detection
                task2 = progress.add_task("🔍 Detecting service versions...", total=100)
                for i in range(100):
                    progress.advance(task2, 1)
                    if i == 40:  # Start version scan
                        version_scan = self._perform_scan(self.target, ports, '-sT -sV --version-intensity 5')
                
                # Phase 3: Analysis and formatting
                task3 = progress.add_task("📊 Analyzing results...", total=100)
                for i in range(100):
                    progress.advance(task3, 1)
            
            # Combine and format results
            results += self._format_scan_results(initial_scan)
            
            # Show completion statistics
            scan_stats = {
                "Scan Type": scan_type,
                "Port Range": ports,
                "Target IP": ip,
                "Scan Duration": f"{initial_scan.get('nmap', {}).get('scanstats', {}).get('elapsed', 'N/A')} seconds",
                "Ports Scanned": initial_scan.get('nmap', {}).get('scanstats', {}).get('totalhosts', 'N/A'),
                "Status": "✅ Completed Successfully"
            }
            tracker.show_completion_stats(scan_stats)
            
            # Add scan statistics to report
            results += "\n### Scan Statistics\n\n"
            for key, value in scan_stats.items():
                results += f"- {key}: {value}\n"
            
            return results
            
        except Exception as e:
            error_msg = f"❌ Error during scan: {str(e)}"
            console.print(f"[red]{error_msg}[/red]")
            return error_msg

    def discover_subdomains(self) -> str:
        """Discover subdomains for the target domain"""
        try:
            if self.target not in self._cache:
                # Use animated spinner for subdomain discovery
                with AnimatedSpinner(f"🔍 Discovering subdomains for {self.target}...", "dots12") as spinner:
                    subdomain_discoverer = SubdomainDiscovery(self.target)
                    self._cache[self.target] = subdomain_discoverer.discover()
                    
            return self._cache[self.target]
        except Exception as e:
            console.print(f"[red]Error during subdomain discovery: {str(e)}[/red]")
            return f"Error during subdomain discovery: {str(e)}"
    
    def vulnerability_scan(self) -> str:
        """Perform vulnerability scan using nmap scripts"""
        try:
            # Create enhanced progress tracker for vulnerability scanning
            tracker = TrimurtiProgressTracker('shiva', self.target)
            tracker.create_mode_header()
            
            results = "## Vulnerability Scan Results\n\n"
            ip = socket.gethostbyname(self.target)
            results += f"Target: {self.target} ({ip})\n\n"
            
            # Show live vulnerability scanning updates
            vuln_steps = [
                "🔍 Initializing vulnerability database...",
                "🛡️ Loading security scripts...",
                "🎯 Targeting vulnerable services...",
                "💥 Executing exploit detection...",
                "📊 Analyzing security posture..."
            ]
            
            with tracker.create_scan_progress(len(vuln_steps)) as progress:
                # Execute vulnerability scan with dramatic progress
                for i, step in enumerate(vuln_steps):
                    task = progress.add_task(step, total=100)
                    
                    if i == 2:  # Start actual scan during "targeting" phase
                        vuln_scan = self._perform_scan(
                            self.target, 
                            '1-1000', 
                            '-sT --script vuln -T4 --max-retries 2'
                        )
                    
                    # Animate progress
                    for j in range(100):
                        progress.advance(task, 1)
                        if i < 3:  # Add some realistic delay for first few steps
                            import time
                            time.sleep(0.01)
            
            # Format vulnerability results
            results += self._format_vulnerability_results(vuln_scan)
            
            # Show vulnerability scan completion
            vuln_stats = {
                "Scan Type": "Vulnerability Assessment",
                "Target": self.target,
                "Scripts Used": "Nmap Vulnerability Scripts",
                "Status": "✅ Assessment Complete"
            }
            tracker.show_completion_stats(vuln_stats)
            
            return results
            
        except Exception as e:
            error_msg = f"❌ Error during vulnerability scan: {str(e)}"
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
