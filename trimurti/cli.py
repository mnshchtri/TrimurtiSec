import click
import logging
import datetime
from trimurti.utils.report_gen import ReportGenerator
from trimurti.brahma.port_scanner import PortScanner
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
@click.option('--method', '-mth', help='Specific method for Vishnu mode (cron|service|registry)')
@click.option('--exploit', '-e', help='Specific exploit type for Shiva mode (sql|buffer|command)')
@click.option('--action', '-a', help='Specific action for God mode (pivot|escalate|exfiltrate)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--quiet', '-q', is_flag=True, help='Suppress all output except errors')
def run(target, mode, output, subdomain_discovery, method, exploit, action, verbose, quiet):
    """Run Trimurti in specified mode with optional parameters"""
    # Configure logging level based on verbosity
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
            
            scanner = PortScanner(target)
            
            # Perform port scanning with enhanced progress
            results = scanner.scan()
            report.add_section("Reconnaissance Results", results)
            
            # Perform subdomain discovery if requested
            if subdomain_discovery:
                console.print("\n🔍 [bold blue]Initiating Advanced Subdomain Discovery...[/bold blue]")
                subdomain_results = scanner.discover_subdomains()
                report.add_section("Subdomain Discovery Results", subdomain_results)
            
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
        
        scanner = PortScanner(target)
        results = scanner.discover_subdomains()
        
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

@cli.command()
@click.option('--target', '-t', required=True, help='Target IP or domain')
@click.option('--output', '-o', default='vuln_report.pdf', help='Output report file')
@click.option('--scan-type', default='default', help='Type of vulnerability scan to perform')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--quiet', '-q', is_flag=True, help='Suppress all output except errors')
def vulnerability_scan(target, output, scan_type, verbose, quiet):
    """Perform a detailed vulnerability scan on the target"""
    # Configure logging level based on verbosity
    if verbose:
        logger.setLevel(logging.DEBUG)
    elif quiet:
        logger.setLevel(logging.ERROR)
    else:
        logger.setLevel(logging.INFO)
    
    console = Console()
    
    try:
        console.print(f"🔍 [bold red]Initiating vulnerability assessment on {target}[/bold red]")
        
        # Create dramatic vulnerability scan sequence
        vuln_steps = [
            "🛡️ Loading vulnerability databases...",
            "🎯 Targeting security weaknesses...",
            "💥 Deploying exploit detection scripts...",
            "🔬 Analyzing security posture..."
        ]
        create_hacking_simulation_progress(vuln_steps, target)
        
        scanner = PortScanner(target)
        results = scanner.vulnerability_scan()
        
        with AnimatedSpinner("📊 Compiling vulnerability assessment...", "dots12"):
            import time
            time.sleep(1)
            report = ReportGenerator(target=target)
            report.add_section("Vulnerability Scan Results", results)
            report.generate(output)
            
        console.print(f"✅ [bold green]Vulnerability report generated: {output}[/bold green]")
        
    except Exception as e:
        console.print(f"❌ [bold red]Error in vulnerability scan: {str(e)}[/bold red]")
        logger.error(f"Error in vulnerability scan: {str(e)}")
        raise

if __name__ == '__main__':
    try:
        cli()
    except Exception as e:
        console = Console()
        console.print(f"💀 [bold red]CRITICAL SYSTEM FAILURE: {str(e)}[/bold red]")
        logger.error(f"Critical error: {str(e)}")
        raise
