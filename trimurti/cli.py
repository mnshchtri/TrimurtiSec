import click
import logging
import datetime
from trimurti.utils.report_gen import ReportGenerator
from trimurti.brahma.port_scanner import PortScanner
from trimurti.brahma.subdomain_discovery import SubdomainDiscovery
from trimurti.brahma.vulnerability_scanner import VulnerabilityScanner
from trimurti.vishnu.c2_server import C2Server
from trimurti.shiva.exploit import Exploiter
from trimurti.god_mode.full_control import GodMode
from trimurti.utils.enhanced_progress import (
    TrimurtiProgressTracker, AnimatedSpinner, create_hacking_simulation_progress
)
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from trimurti.utils.ai_analysis import analyze_recon_output, analyze_vulnerabilities
import os
import pathlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('trimurti')

@click.group(help="""
████████╗██████╗ ██╗███╗   ███╗██╗   ██╗██████╗ ████████╗██╗
╚══██╔══╝██╔══██╗██║████╗ ████║██║   ██║██╔══██╗╚══██╔══╝██║
   ██║   ██████╔╝██║██╔████╔██║██║   ██║██████╔╝   ██║   ██║
   ██║   ██╔══██╗██║██║╚██╔╝██║██║   ██║██╔══██╗   ██║   ██║
   ██║   ██║  ██║██║██║ ╚═╝ ██║╚██████╔╝██║  ██║   ██║   ██║
   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝

    TrimurtiSec - Advanced Penetration Testing Framework
    Version: 1.0.0

TrimurtiSec - Advanced Penetration Testing Framework

Usage:
  trimurti run --target example.com --mode brahma
  trimurti run --target 192.168.1.1 --mode vishnu
  trimurti run --target target.com --mode shiva
  trimurti run --target 10.0.0.1 --mode god
""")
def cli():
    """TrimurtiSec - Advanced Penetration Testing Framework
    
    Usage:
      trimurti run --target example.com --mode brahma
      trimurti run --target 192.168.1.1 --mode vishnu
      trimurti run --target target.com --mode shiva
      trimurti run --target 10.0.0.1 --mode god
    """
    console = Console()
    
    # Enhanced banner with dramatic presentation
    banner_text = """
████████╗██████╗ ██╗███╗   ███╗██╗   ██╗██████╗ ████████╗██╗
╚══██╔══╝██╔══██╗██║████╗ ████║██║   ██║██╔══██╗╚══██╔══╝██║
   ██║   ██████╔╝██║██╔████╔██║██║   ██║██████╔╝   ██║   ██║
   ██║   ██╔══██╗██║██║╚██╔╝██║██║   ██║██╔══██╗   ██║   ██║
   ██║   ██║  ██║██║██║ ╚═╝ ██║╚██████╔╝██║  ██║   ██║   ██║
   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝

🔱 TrimurtiSec - Advanced Penetration Testing Framework 🔱
                        Version: 1.0.0
    """
    
    banner_panel = Panel(
        Align.center(Text(banner_text, style="bold red")),
        border_style="red",
        padding=(1, 2)
    )
    
    console.print(banner_panel)
    
    # Animated initialization
    with AnimatedSpinner("🚀 Initializing TrimurtiSec Framework...", "dots12"):
        import time
        time.sleep(1.5)  # Dramatic pause
    
    console.print("✅ [bold green]Framework ready for cyber operations![/bold green]\n")

@cli.command()
@click.option('--target', '-t', required=True, help='Target IP or domain')
@click.option('--mode', '-m', type=click.Choice(['brahma', 'vishnu', 'shiva', 'god']), required=True)
@click.option('--output', '-o', default='report.pdf', help='Output report file')
@click.option('--subdomain-discovery', '-s', is_flag=True, help='Perform subdomain discovery (Brahma mode only)')
@click.option('--subdomain', is_flag=True, help='Perform subdomain discovery (Brahma mode only)')
@click.option('--vulnerability-scan', is_flag=True, help='Perform vulnerability scanning (Brahma mode only)')
@click.option('--trivy-path', default=None, help='Path to directory or container image for Trivy scan (optional)')
@click.option('--shodan-api-key', default=None, help='Shodan API key for public exposure checks (optional)')
@click.option('--max-targets', type=int, default=10, help='Maximum number of targets to scan for vulnerability tools (default: 10)')
@click.option('--method', '-mth', help='Specific method for Vishnu mode (cron|service|registry)')
@click.option('--action', '-a', help='Specific action for God mode (pivot|escalate|exfiltrate)')
@click.option('--exploit', '-e', help='Specific exploit type for Shiva mode (sql|buffer|command)')
@click.option('--scan-type', type=click.Choice(['quick', 'comprehensive', 'aggressive']), help='Scan type for Brahma mode')
@click.option('--timeout', type=int, default=300, help='Timeout in seconds for scan')
@click.option('--ports', help='Comma-separated port list or range (e.g., "80,443" or "1-1000")')
@click.option('--ai-analysis', is_flag=True, help='Enable AI analysis of results')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--quiet', '-q', is_flag=True, help='Suppress all output except errors')
def run(target, mode, output, subdomain_discovery, subdomain, vulnerability_scan, trivy_path, shodan_api_key, max_targets, method, exploit, action, ai_analysis, scan_type, timeout, ports, verbose, quiet):
    """Run Trimurti in specified mode with optional parameters"""
    # Configure logging level based on verbosity
    if verbose and quiet:
        raise click.BadOptionUsage('verbose/quiet', 'Cannot use --verbose and --quiet together')
    if verbose:
        logger.setLevel(logging.DEBUG)
    elif quiet:
        logger.setLevel(logging.ERROR)
    else:
        logger.setLevel(logging.INFO)
    
    report = ReportGenerator(target=target)
    console = Console()
    
    try:
        if mode == 'brahma':
            # Create dramatic initialization sequence
            brahma_steps = [
                "🔍 Initializing reconnaissance modules...",
                "🌐 Establishing network connections...",
                "🎯 Targeting reconnaissance sensors...",
                "🔬 Deploying scanning algorithms..."
            ]
            create_hacking_simulation_progress(brahma_steps, target)
            
            scanner = PortScanner(target, scan_type=scan_type, timeout=timeout, ports=ports)
            
            # Handle specific options for Brahma mode
            if subdomain_discovery or subdomain:
                console.print("\n🔍 [bold blue]Initiating Advanced Subdomain Discovery...[/bold blue]")
                discoverer = SubdomainDiscovery(target)
                subdomain_results = discoverer.discover()
                report.add_section("Subdomain Discovery Results", subdomain_results)
                console.print(f"[green]{subdomain_results}[/green]")
                # AI analysis integration
                ai_input = discoverer.get_results_for_analysis()
                ai_analysis_result = analyze_recon_output(ai_input)
                report.add_section("AI Analysis of Subdomain Discovery", ai_analysis_result)
                report.generate(output)
            
            elif vulnerability_scan:
                console.print("\n🔍 [bold red]Initiating Vulnerability Assessment...[/bold red]")
                vuln_scanner = VulnerabilityScanner(target, trivy_path=trivy_path, shodan_api_key=shodan_api_key, max_targets=max_targets)
                vuln_results = vuln_scanner.scan_vulnerabilities()
                report.add_section("Vulnerability Scan Results", vuln_results)
                console.print(f"[green]{vuln_results}[/green]")
                # AI analysis integration
                ai_input = vuln_scanner.get_results_for_analysis()
                ai_analysis_result = analyze_vulnerabilities(ai_input)
                report.add_section("AI Analysis of Vulnerability Scan", ai_analysis_result)
                # If Nmap XML exists, feed it to AI analysis and add findings
                nmap_xml_path = f"reports/nmap_{target.replace('.', '_')}.xml"
                if os.path.exists(nmap_xml_path) and os.path.getsize(nmap_xml_path) > 0:
                    with open(nmap_xml_path, 'r') as f:
                        nmap_xml_content = f.read()
                    nmap_ai = analyze_vulnerabilities(nmap_xml_content)
                    report.add_section("AI Analysis of Nmap Vulnerability Scan", nmap_ai)
                report.generate(output)
            
            else:
                # Default port scanning behavior
                results = scanner.scan()
                report.add_section("Reconnaissance Results", results)
                # AI analysis integration for port scan results
                ai_input = results
                ai_analysis_result = analyze_recon_output(ai_input)
                report.add_section("AI Analysis of Port Scan", ai_analysis_result)
                report.generate(output)
            
        elif mode == 'vishnu':
            if not method:
                raise click.BadOptionUsage('--method', 'Method is required for Vishnu mode')
            
            # Vishnu mode dramatic sequence
            vishnu_steps = [
                "🔐 Activating preservation protocols...",
                "🔗 Establishing persistent connections...",
                "🛡️ Deploying stealth mechanisms...",
                "📡 Creating command channels...",
                "🎭 Implementing evasion techniques..."
            ]
            create_hacking_simulation_progress(vishnu_steps, target)
            
            c2 = C2Server(target)
            results = c2.establish_persistence(method)
            report.add_section("Persistence Results", results)
            report.generate(output)
            
        elif mode == 'shiva':
            if not exploit:
                raise click.BadOptionUsage('--exploit', 'Exploit type is required for Shiva mode')
            
            # Shiva mode dramatic sequence
            shiva_steps = [
                "💥 Charging destructive capabilities...",
                "🎯 Identifying vulnerability vectors...",
                "⚡ Weaponizing exploit payloads...",
                "🔥 Initiating penetration sequence...",
                "💀 Executing exploitation protocols..."
            ]
            create_hacking_simulation_progress(shiva_steps, target)
            
            exploiter = Exploiter(target)
            results = exploiter.run_exploits(exploit_type=exploit)
            report.add_section("Exploitation Results", results)
            report.generate(output)
            
        elif mode == 'god':
            if not action:
                raise click.BadOptionUsage('--action', 'Action is required for God mode')
            
            # God mode ultimate sequence
            god_steps = [
                "👑 Ascending to supreme authority...",
                "⚡ Channeling omnipotent capabilities...",
                "🌟 Unlocking universal access protocols...",
                "💎 Manifesting total system domination...",
                "🔮 Achieving transcendent control...",
                "🌌 Becoming one with the digital realm..."
            ]
            create_hacking_simulation_progress(god_steps, target)
            
            god = GodMode(target)
            results = god.take_control(action)
            report.add_section("God Mode Results", results)
        
        # Generate report with final animation
        with AnimatedSpinner("📊 Generating comprehensive report...", "dots12"):
            import time
            time.sleep(1)
            report.generate(output)
        
        console.print(f"✅ [bold green]Report successfully generated: {output}[/bold green]")
        console.print("🎯 [bold cyan]Mission accomplished![/bold cyan]")
        
    except Exception as e:
        console.print(f"❌ [bold red]Critical error in {mode} mode: {str(e)}[/bold red]")
        logger.error(f"Error in {mode} mode: {str(e)}")
        raise

@cli.command()
@click.option('--target', '-t', required=True, help='Target domain (not an IP address)')
@click.option('--output', '-o', default='subdomains.pdf', help='Output report file')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--quiet', '-q', is_flag=True, help='Suppress all output except errors')
def discover_subdomains(target, output, verbose, quiet):
    """Discover subdomains for a target domain"""
    # Configure logging level based on verbosity
    if verbose:
        logger.setLevel(logging.DEBUG)
    elif quiet:
        logger.setLevel(logging.ERROR)
    else:
        logger.setLevel(logging.INFO)
    
    console = Console()
    
    try:
        console.print(f"🔍 [bold blue]Initiating subdomain discovery for {target}[/bold blue]")
        
        # Create dramatic subdomain discovery sequence
        discovery_steps = [
            "🔍 Initializing subdomain enumeration engines...",
            "🌐 Querying global DNS infrastructure...",
            "📡 Scanning certificate transparency logs...",
            "🕷️ Crawling web archives..."
        ]
        create_hacking_simulation_progress(discovery_steps, target)
        
        discoverer = SubdomainDiscovery(target)
        results = discoverer.discover()
        
        with AnimatedSpinner("📊 Compiling discovery report...", "dots12"):
            import time
            time.sleep(1)
            report = ReportGenerator(target=target)
            report.add_section("Subdomain Discovery Results", results)
            report.generate(output)
            
        console.print(f"✅ [bold green]Discovery report generated: {output}[/bold green]")
        
    except Exception as e:
        console.print(f"❌ [bold red]Error in subdomain discovery: {str(e)}[/bold red]")
        logger.error(f"Error in subdomain discovery: {str(e)}")
        raise


if __name__ == '__main__':
    try:
        cli()
    except Exception as e:
        console = Console()
        console.print(f"💀 [bold red]CRITICAL SYSTEM FAILURE: {str(e)}[/bold red]")
        logger.error(f"Critical error: {str(e)}")
        raise
