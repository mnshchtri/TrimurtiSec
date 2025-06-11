import click
import logging
import datetime
from trimurti.utils.report_gen import ReportGenerator
from trimurti.brahma.port_scanner import PortScanner
from trimurti.vishnu.c2_server import C2Server
from trimurti.shiva.exploit import Exploiter
from trimurti.god_mode.full_control import GodMode

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
    banner = """
████████╗██████╗ ██╗███╗   ███╗██╗   ██╗██████╗ ████████╗██╗
╚══██╔══╝██╔══██╗██║████╗ ████║██║   ██║██╔══██╗╚══██╔══╝██║
   ██║   ██████╔╝██║██╔████╔██║██║   ██║██████╔╝   ██║   ██║
   ██║   ██╔══██╗██║██║╚██╔╝██║██║   ██║██╔══██╗   ██║   ██║
   ██║   ██║  ██║██║██║ ╚═╝ ██║╚██████╔╝██║  ██║   ██║   ██║
   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝

    TrimurtiSec - Advanced Penetration Testing Framework
    Version: 1.0.0
    """
    click.echo(banner)
    click.echo("Initializing modules...")
    click.echo("Checking dependencies...")

@cli.command()
@click.option('--target', '-t', required=True, help='Target IP or domain')
@click.option('--mode', '-m', type=click.Choice(['brahma', 'vishnu', 'shiva', 'god']), required=True)
@click.option('--output', '-o', default='report.md', help='Output report file')
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
    
    try:
        if mode == 'brahma':
            click.echo("🔍 Entering Brahma Mode - Reconnaissance Phase")
            scanner = PortScanner(target)
            
            # Perform port scanning
            results = scanner.scan()
            report.add_section("Reconnaissance Results", results)
            
            # Perform subdomain discovery if requested
            if subdomain_discovery:
                click.echo("🔍 Performing subdomain discovery")
                subdomain_results = scanner.discover_subdomains()
                report.add_section("Subdomain Discovery Results", subdomain_results)
            
        elif mode == 'vishnu':
            if not method:
                raise click.BadOptionUsage('--method', 'Method is required for Vishnu mode')
                
            click.echo(f"🔐 Entering Vishnu Mode - Persistence Phase with {method} method")
            c2 = C2Server(target)
            results = c2.establish_persistence(method)
            report.add_section("Persistence Results", results)
            
        elif mode == 'shiva':
            if not exploit:
                raise click.BadOptionUsage('--exploit', 'Exploit type is required for Shiva mode')
                
            click.echo(f"💥 Entering Shiva Mode - Destruction Phase with {exploit} exploit")
            exploiter = Exploiter(target)
            results = exploiter.run_exploits(exploit_type=exploit)
            report.add_section("Exploitation Results", results)
            
        elif mode == 'god':
            if not action:
                raise click.BadOptionUsage('--action', 'Action is required for God mode')
                
            click.echo(f"👑 Entering God Mode - Full Control with {action} action")
            god = GodMode(target)
            results = god.take_control(action)
            report.add_section("God Mode Results", results)
        
        report.generate(output)
        click.echo(f"Report generated: {output}")
        
    except Exception as e:
        logger.error(f"Error in {mode} mode: {str(e)}")
        raise

@cli.command()
@click.option('--target', '-t', required=True, help='Target domain (not an IP address)')
@click.option('--output', '-o', default='subdomains.md', help='Output report file')
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
    
    try:
        click.echo(f"🔍 Discovering subdomains for {target}")
        scanner = PortScanner(target)
        results = scanner.discover_subdomains()
        
        report = ReportGenerator(target=target)
        report.add_section("Subdomain Discovery Results", results)
        report.generate(output)
        click.echo(f"Report generated: {output}")
        
    except Exception as e:
        logger.error(f"Error in subdomain discovery: {str(e)}")
        raise

@cli.command()
@click.option('--target', '-t', required=True, help='Target IP or domain')
@click.option('--output', '-o', default='vuln_report.md', help='Output report file')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--quiet', '-q', is_flag=True, help='Suppress all output except errors')
def vulnerability_scan(target, output, verbose, quiet):
    """Perform a detailed vulnerability scan on the target"""
    # Configure logging level based on verbosity
    if verbose:
        logger.setLevel(logging.DEBUG)
    elif quiet:
        logger.setLevel(logging.ERROR)
    else:
        logger.setLevel(logging.INFO)
    
    try:
        click.echo(f"🔍 Performing vulnerability scan on {target}")
        scanner = PortScanner(target)
        results = scanner.vulnerability_scan()
        
        report = ReportGenerator(target=target)
        report.add_section("Vulnerability Scan Results", results)
        report.generate(output)
        click.echo(f"Report generated: {output}")
        
    except Exception as e:
        logger.error(f"Error in vulnerability scan: {str(e)}")
        raise

if __name__ == '__main__':
    try:
        cli()
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        raise 