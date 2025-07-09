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
    def __init__(self, target: str, timeout: int = 600, scan_type: str = 'quick', ports: str = '1-1000'):
        self.target = self._validate_target(target)
        self.nm = nmap.PortScanner()
        self.timeout = timeout
        self.scan_type = scan_type
        self.ports = ports
        self._cache = {}
        
    @staticmethod
    def _validate_target(target: str) -> str:
        """Validate and normalize the target input"""
        try:
            ip = socket.gethostbyname(target)
            return target
        except socket.gaierror:
            raise ValueError(f"Invalid target: {target}")
    
    def _is_target_responsive(self, target: str) -> bool:
        """Check if target is responsive before scanning"""
        try:
            # Quick ping test
            result = self.nm.scan(target, arguments='-sn', timeout=30)
            return len(result.get('scan', {})) > 0
        except Exception as e:
            console.print(f"[yellow]⚠️ Target responsiveness check failed: {str(e)}[/yellow]")
            return True  # Proceed anyway
            
    @lru_cache(maxsize=128)
    def _perform_scan(self, target: str, ports: str, arguments: str) -> Dict[str, Any]:
        """Enhanced scan implementation with better error handling and timeouts"""
        try:
            # Check target responsiveness first
            if not self._is_target_responsive(target):
                console.print(f"[yellow]⚠️ Target {target} may not be responsive, proceeding anyway...[/yellow]")
            
            # Add timeout to nmap arguments if not present
            if '--host-timeout' not in arguments:
                arguments += f' --host-timeout {self.timeout//2}s'
            
            # Add max retries if not present
            if '--max-retries' not in arguments:
                arguments += ' --max-retries 1'
            
            console.print(f"[cyan]🔍 Scanning {target} with arguments: {arguments}[/cyan]")
            
            result = self.nm.scan(target, ports, arguments, timeout=self.timeout)
            
            # Check if scan was successful
            if not result or 'scan' not in result:
                console.print(f"[yellow]⚠️ Scan returned empty results for {target}[/yellow]")
                return {'scan': {}, 'nmap': {'scanstats': {'elapsed': '0'}}}
            
            # Log scan completion
            hosts_found = len(result.get('scan', {}))
            console.log(f"✅ Scan completed for {target} with {hosts_found} hosts")
            return result
            
        except nmap.PortScannerTimeout as e:
            console.print(f"[red]⏱️ Nmap scan timeout for {target}: {str(e)}[/red]")
            console.print(f"[yellow]💡 Try using a smaller port range or increase timeout[/yellow]")
            # Return empty result instead of raising
            return {'scan': {}, 'nmap': {'scanstats': {'elapsed': 'timeout'}}}
        except nmap.PortScannerError as e:
            console.print(f"[red]❌ Nmap scan error: {str(e)}[/red]")
            return {'scan': {}, 'nmap': {'scanstats': {'elapsed': 'error'}}}
        except Exception as e:
            console.print(f"[red]❌ Unexpected error during scan: {str(e)}[/red]")
            return {'scan': {}, 'nmap': {'scanstats': {'elapsed': 'error'}}}

    def _format_scan_results(self, scan_data: Dict[str, Any]) -> str:
        """Format scan results into a markdown table"""
        results = "### Open Ports\n\n"
        
        # Check if scan has results
        if not scan_data.get('scan'):
            results += "No hosts found or scan failed.\n\n"
            return results
            
        results += "| Port | Service | Version | State |\n"
        results += "|------|---------|---------|-------|\n"
        
        port_count = 0
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
                            port_count += 1
                            
        except Exception as e:
            console.print(f"[red]Error formatting results: {str(e)}[/red]")
            results += "| Error processing scan results | | | |\n"
        
        if port_count == 0:
            results += "| No open ports found | | | |\n"
        
        return results

    def scan(self, ports: str = None, scan_type: str = None) -> str:
        """
        Perform port scan on target with different scan types
        
        Args:
            ports: Port range to scan (default: '1-1000')
            scan_type: Type of scan ('quick', 'comprehensive', 'aggressive')
        """
        ports = ports if ports is not None else self.ports
        scan_type = scan_type if scan_type is not None else self.scan_type
        try:
            # Create enhanced progress tracker
            tracker = TrimurtiProgressTracker('brahma', self.target)
            tracker.create_mode_header()
            
            results = "## Port Scan Results\n\n"
            ip = socket.gethostbyname(self.target)
            results += f"Target: {self.target} ({ip})\n\n"
            
            # Adjusted scan arguments for better timeout handling
            scan_args = {
                'quick': '-sT -sV -T4 --max-retries 1 --host-timeout 60s',  # Added -sV for version detection
                'comprehensive': '-sT -sV -T3 --max-retries 2 --host-timeout 120s',
                'aggressive': '-sT -sV -sC -T4 --max-retries 1 --host-timeout 180s'
            }
            
            # For external targets, prefer smaller port ranges
            actual_ports = ports
            if ports == '1-1000' and scan_type != 'quick':
                console.print(f"[yellow]💡 Using common ports for external target[/yellow]")
                actual_ports = '21,22,23,25,53,80,110,143,443,993,995,8080,8443'
            
            # Enhanced progress with multiple steps
            with tracker.create_scan_progress(3) as progress:
                # Phase 1: Initial TCP Connect scan
                task1 = progress.add_task("🌐 Establishing connection to target...", total=100)
                for i in range(100):
                    progress.advance(task1, 1)
                    if i == 30:  # Start actual scan partway through animation
                        initial_scan = self._perform_scan(self.target, actual_ports, scan_args[scan_type])
                
                # Phase 2: Service version detection (only if initial scan succeeded)
                task2 = progress.add_task("🔍 Detecting service versions...", total=100)
                version_scan = initial_scan  # Use same scan result if it included version detection
                
                if scan_type in ['comprehensive', 'aggressive'] and initial_scan.get('scan'):
                    for i in range(100):
                        progress.advance(task2, 1)
                        if i == 40:  # Start version scan if needed
                            version_scan = self._perform_scan(self.target, actual_ports, '-sT -sV --version-intensity 3')
                else:
                    # Skip version detection for quick scans or failed initial scans
                    for i in range(100):
                        progress.advance(task2, 1)
                
                # Phase 3: Analysis and formatting
                task3 = progress.add_task("📊 Analyzing results...", total=100)
                for i in range(100):
                    progress.advance(task3, 1)
            
            # Combine and format results - use version_scan for better version info
            results += self._format_scan_results(version_scan)
            
            # Show completion statistics
            elapsed = initial_scan.get('nmap', {}).get('scanstats', {}).get('elapsed', 'N/A')
            scan_stats = {
                "Scan Type": scan_type,
                "Port Range": actual_ports,
                "Target IP": ip,
                "Scan Duration": f"{elapsed} seconds" if elapsed != 'N/A' else elapsed,
                "Timeout Setting": f"{self.timeout}s",
                "Status": "Completed Successfully" if elapsed not in ['timeout', 'error'] else "Completed with Issues"
            }
            tracker.show_completion_stats(scan_stats)
            
            # Add scan statistics to report
            results += "\n### Scan Statistics\n\n"
            for key, value in scan_stats.items():
                results += f"- {key}: {value}\n"
            
            # Add recommendations if scan had issues
            if elapsed in ['timeout', 'error']:
                results += "\n### Recommendations\n\n"
                results += "- Try using 'quick' scan type for faster results\n"
                results += "- Use smaller port ranges (e.g., '80,443,8080')\n"
                results += "- Increase timeout value when initializing scanner\n"
                results += "- Check network connectivity to target\n"
            
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
                        # Use more conservative settings for vulnerability scanning
                        vuln_scan = self._perform_scan(
                            self.target, 
                            '80,443,8080,8443', 
                            '-sT --script vuln -T3 --max-retries 1 --host-timeout 300s'
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
        
        if not scan_data.get('scan'):
            results += "No vulnerability data available (scan may have failed or timed out).\n\n"
            return results
            
        results += "| CVE | Severity | Port | Description |\n"
        results += "|-----|----------|------|-------------|\n"
        
        vuln_count = 0
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
                                    vuln_count += 1
                        else:
                            results += f"| N/A | Info | Multiple | {script_id} |\n"
                            vuln_count += 1
                            
                for proto in self.nm[host].all_protocols():
                    lport = list(self.nm[host][proto].keys())
                    for port in lport:
                        port_data = self.nm[host][proto][port]
                        if 'script' in port_data:
                            for script_name, script_output in port_data['script'].items():
                                if 'vuln' in script_name.lower():
                                    results += f"| N/A | Medium | {port} | {script_name} |\n"
                                    vuln_count += 1
                                    
        except Exception as e:
            console.print(f"[red]Error formatting vulnerability results: {str(e)}[/red]")
            results += "| Error processing vulnerability results | | | |\n"
        
        if vuln_count == 0:
            results += "| No vulnerabilities detected | | | |\n"
        
        results += "\n### Vulnerability Summary\n\n"
        results += "- Scan completed with Nmap vulnerability scripts\n"
        results += f"- {vuln_count} potential issues found\n"
        results += "- Manual verification recommended for critical findings\n"
        results += "- External targets may have limited vulnerability exposure\n"
        
        return results