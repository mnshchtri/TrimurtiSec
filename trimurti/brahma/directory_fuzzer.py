import os
import json
import requests
import threading
from urllib.parse import urljoin, urlparse
from queue import Queue
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from typing import List, Dict, Set
from datetime import datetime
import time
import subprocess
import sys

# Import TrimurtiSec components
try:
    from trimurti.utils.enhanced_progress import TrimurtiProgressTracker, AnimatedSpinner
except ImportError:
    # Fallback if trimurti utils not available
    class TrimurtiProgressTracker:
        def __init__(self, mode, target):
            self.mode = mode
            self.target = target
            
        def create_mode_header(self):
            console.print(f"[cyan]TrimurtiSec {self.mode.upper()} Mode - Directory Fuzzing[/cyan]")
            
        def create_scan_progress(self, total):
            return Progress()
            
        def show_completion_stats(self, stats):
            console.print("[green]Directory fuzzing completed![/green]")
            for key, value in stats.items():
                console.print(f"  {key}: {value}")
    
    class AnimatedSpinner:
        def __init__(self, message, style):
            self.message = message
            
        def __enter__(self):
            console.print(f"[cyan]{self.message}[/cyan]")
            return self
            
        def __exit__(self, *args):
            pass

console = Console()

class DirectoryFuzzer:
    def __init__(self, target_domain=None, wordlist_path=None, threads=20, timeout=5):
        self.target_domain = target_domain
        self.wordlist_path = wordlist_path or self._get_default_wordlist()
        self.threads = threads
        self.timeout = timeout
        self.subdomains = set()
        self.directory_results = {}
        self.all_findings = []
        
        # Create reports directory
        os.makedirs('reports', exist_ok=True)
        
    def _get_default_wordlist(self):
        """Get default wordlist path or create one"""
        default_paths = [
            '/usr/share/wordlists/dirb/common.txt',
            '/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt',
            '/usr/share/wordlists/SecLists/Discovery/Web-Content/common.txt',
            'wordlist.txt'
        ]
        
        for path in default_paths:
            if os.path.exists(path):
                return path
                
        # Create default wordlist if none found
        return self._create_default_wordlist()

    def _create_default_wordlist(self):
        """Create a comprehensive default wordlist"""
        # Ensure reports directory exists
        os.makedirs('reports', exist_ok=True)
        wordlist_path = 'wordlist/directory_wordlist.txt'
        
        default_words = [
            # Common directories
            'admin', 'administrator', 'login', 'backup', 'config', 'test',
            'dev', 'development', 'staging', 'uploads', 'upload', 'images', 'img',
            'css', 'js', 'javascript', 'assets', 'static', 'media', 'files',
            'api', 'v1', 'v2', 'docs', 'documentation', 'help', 'support',
            'downloads', 'download', 'tmp', 'temp', 'cache', 'logs', 'log',
            'database', 'db', 'sql', 'old', 'new', 'beta', 'alpha', 'demo',
            'sample', 'example', 'dashboard', 'panel', 'control', 'manage',
            'user', 'users', 'profile', 'account', 'accounts', 'settings',
            'preference', 'preferences', 'security', 'auth', 'oauth', 'token',
            'private', 'public', 'www', 'ftp', 'mail', 'email', 'forum',
            'blog', 'news', 'video', 'audio', 'photo', 'gallery', 'shop',
            'store', 'cart', 'checkout', 'payment', 'invoice', 'report',
            'reports', 'stats', 'statistics', 'monitor', 'monitoring',
            
            # Common files
            'index', 'home', 'default', 'main', 'login', 'logout', 'register',
            'signup', 'signin', 'contact', 'about', 'info', 'readme',
            'install', 'setup', 'config', 'configuration', 'phpinfo',
            'test', 'debug', 'error', 'robots', 'sitemap', 'favicon',
            
            # Extensions and patterns
            'wp-content', 'wp-admin', 'wp-includes', 'wordpress', 'wp',
            'phpmyadmin', 'pma', 'mysql', 'adminer', 'phpMyAdmin',
            'backup', 'backups', 'old', 'bak', 'orig', 'copy',
            'cgi-bin', 'scripts', 'includes', 'inc', 'lib', 'libraries',
            'vendor', 'node_modules', 'bower_components', 'packages',
            
            # Security-related
            'security', 'secure', 'protected', 'restricted', 'hidden',
            'secret', 'confidential', 'internal', 'staff', 'employee',
            'management', 'executive', 'board', 'director', 'ceo',
            
            # Technology-specific
            'api', 'rest', 'graphql', 'soap', 'rpc', 'json', 'xml',
            'ajax', 'xhr', 'websocket', 'socket', 'realtime', 'live',
            'stream', 'streaming', 'feed', 'feeds', 'rss', 'atom',
            
            # Framework-specific
            'laravel', 'symfony', 'codeigniter', 'cakephp', 'yii',
            'zend', 'phalcon', 'slim', 'lumen', 'app', 'application',
            'framework', 'mvc', 'controller', 'model', 'view',
            
            # CMS-specific
            'drupal', 'joomla', 'magento', 'prestashop', 'opencart',
            'woocommerce', 'shopify', 'squarespace', 'weebly', 'wix'
        ]
        
        # Add common file extensions
        extensions = ['.php', '.html', '.htm', '.asp', '.aspx', '.jsp', 
                     '.do', '.action', '.cgi', '.pl', '.py', '.rb', '.js',
                     '.txt', '.xml', '.json', '.csv', '.sql', '.bak', '.old']
        
        all_words = set(default_words)
        
        # Add words with extensions
        for word in default_words[:50]:  # Limit to avoid too large wordlist
            for ext in extensions[:8]:  # Common extensions only
                all_words.add(word + ext)
        
        # Add directory variations
        for word in default_words[:30]:
            all_words.add(word + '/')
            all_words.add('.' + word)
            all_words.add(word + '_backup')
            all_words.add(word + '_old')
            all_words.add(word + '2')
            all_words.add(word + '_test')
        
        with open(wordlist_path, 'w') as f:
            for word in sorted(all_words):
                f.write(word + '\n')
        
        console.print(f"[cyan]Created comprehensive wordlist: {wordlist_path} ({len(all_words)} entries)[/cyan]")
        return wordlist_path

    def load_subdomains_from_discovery(self):
        """Load subdomains from subdomain discovery results"""
        subdomain_files = [
            'reports/httpx_results.json',
            'reports/subfinder_results.txt',
            'reports/subdomain_discovery_report.json'
        ]
        
        for file_path in subdomain_files:
            if os.path.exists(file_path):
                if file_path.endswith('.json'):
                    self._load_from_json(file_path)
                else:
                    self._load_from_text(file_path)
        
        # If target domain provided but no subdomains found, use the domain itself
        if self.target_domain and not self.subdomains:
            self.subdomains.add(self.target_domain)
            console.print(f"[yellow]Using target domain directly: {self.target_domain}[/yellow]")
        
        console.print(f"[cyan]Loaded {len(self.subdomains)} subdomains for directory fuzzing[/cyan]")
        return len(self.subdomains) > 0

    def _load_from_json(self, file_path):
        """Load subdomains from HTTPX JSON results"""
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    try:
                        result = json.loads(line.strip())
                        url = result.get('url', '')
                        if url:
                            # Extract domain from URL
                            parsed = urlparse(url)
                            domain = parsed.netloc or parsed.path
                            if domain:
                                self.subdomains.add(domain)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            console.print(f"[yellow]Error loading JSON file {file_path}: {e}[/yellow]")

    def _load_from_text(self, file_path):
        """Load subdomains from text file"""
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    subdomain = line.strip()
                    if subdomain and not subdomain.startswith('#'):
                        self.subdomains.add(subdomain)
        except Exception as e:
            console.print(f"[yellow]Error loading text file {file_path}: {e}[/yellow]")

    def fuzz_directories(self) -> str:
        """Main directory fuzzing function"""
        if not self.subdomains:
            if not self.load_subdomains_from_discovery():
                return "No subdomains found for directory fuzzing. Please run subdomain discovery first."
        
        # Create enhanced progress tracker
        tracker = TrimurtiProgressTracker('brahma', self.target_domain or 'multiple_subdomains')
        tracker.create_mode_header()
        
        console.print(f"[cyan]Starting directory fuzzing on {len(self.subdomains)} subdomains...[/cyan]")
        console.print(f"[cyan]Wordlist: {self.wordlist_path}[/cyan]")
        
        # Enhanced directory fuzzing with progress tracking
        fuzzing_steps = [
            "Initializing directory fuzzing engines...",
            "Loading wordlist and preparing payloads...",
            "Starting multi-threaded directory enumeration...",
            "Analyzing HTTP responses and filtering results...",
            "Compiling comprehensive directory findings..."
        ]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            
            for i, step in enumerate(fuzzing_steps):
                task = progress.add_task(step, total=100)
                
                if i == 2:  # Start actual fuzzing during enumeration phase
                    self._run_directory_fuzzing(progress, task)
                elif i == 3:  # Process results during analysis phase
                    self._process_results(progress, task)
                else:
                    # Animate progress for other steps
                    for j in range(100):
                        progress.advance(task, 1)
                        time.sleep(0.01)
        
        # Format results
        results = self._format_directory_results()
        
        # Show completion statistics
        fuzzing_stats = {
            "Target Subdomains": len(self.subdomains),
            "Total Directories Found": len(self.all_findings),
            "Subdomains with Findings": len([k for k, v in self.directory_results.items() if v]),
            "Wordlist Size": self._count_wordlist_entries(),
            "Status": "Directory Fuzzing Complete"
        }
        tracker.show_completion_stats(fuzzing_stats)
        
        # Generate comprehensive reports
        report_file = f'reports/directory_fuzzing_report_{self.target_domain or "subdomains"}.pdf'
        self._generate_pdf_report(fuzzing_stats, report_file)
        
        # Save JSON results for integration
        json_report = f'reports/directory_fuzzing_results.json'
        self._save_json_results(json_report)
        
        console.print(f"[green]Directory fuzzing report saved to: {report_file}[/green]")
        console.print(f"[green]JSON results saved to: {json_report}[/green]")
        
        return results

    def _run_directory_fuzzing(self, progress, task):
        """Run directory fuzzing on all subdomains"""
        # Use both Python implementation and external tools
        self._run_python_fuzzer(progress, task)
        self._run_external_tools()

    def _run_python_fuzzer(self, progress, task):
        """Run Python-based directory fuzzing"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        wordlist = self._load_wordlist()
        if not wordlist:
            console.print("[red]No wordlist available for fuzzing[/red]")
            return
        
        # Create queue for threading
        queue = Queue()
        
        # Add all subdomain/directory combinations to queue
        total_combinations = len(self.subdomains) * len(wordlist)
        progress.update(task, total=total_combinations)
        
        for subdomain in self.subdomains:
            self.directory_results[subdomain] = []
            for word in wordlist:
                queue.put((subdomain, word))
        
        # Start worker threads
        threads = []
        for _ in range(self.threads):
            t = threading.Thread(target=self._fuzzer_worker, args=(queue, session, progress, task))
            t.daemon = True
            t.start()
            threads.append(t)
        
        # Wait for completion
        queue.join()
        
        console.print(f"[green]Python fuzzer completed. Found {len(self.all_findings)} directories.[/green]")

    def _fuzzer_worker(self, queue, session, progress, task):
        """Worker thread for directory fuzzing"""
        while True:
            try:
                subdomain, directory = queue.get(timeout=1)
            except:
                break
                
            try:
                # Construct URLs with different schemes
                urls_to_test = [
                    f"https://{subdomain}/{directory}",
                    f"http://{subdomain}/{directory}"
                ]
                
                for url in urls_to_test:
                    try:
                        response = session.get(url, timeout=self.timeout, allow_redirects=False)
                        
                        # Check for interesting status codes
                        if response.status_code in [200, 301, 302, 403, 401, 500]:
                            finding = {
                                'subdomain': subdomain,
                                'url': url,
                                'directory': directory,
                                'status_code': response.status_code,
                                'content_length': len(response.content),
                                'content_type': response.headers.get('content-type', ''),
                                'server': response.headers.get('server', ''),
                                'timestamp': datetime.now().isoformat()
                            }
                            
                            self.directory_results[subdomain].append(finding)
                            self.all_findings.append(finding)
                            
                            console.print(f"[green][{response.status_code}] {url} ({len(response.content)} bytes)[/green]")
                            break  # Don't test HTTP if HTTPS worked
                            
                    except requests.RequestException:
                        continue
                        
            except Exception as e:
                pass
            finally:
                queue.task_done()
                progress.advance(task, 1)

    def _run_external_tools(self):
        """Run external directory fuzzing tools if available"""
        # Try to run FFuf if available
        self._run_ffuf()
        
        # Try to run Dirb if available  
        self._run_dirb()

    def _run_ffuf(self):
        """Run FFuf for directory fuzzing"""
        try:
            subprocess.run(['ffuf', '-V'], capture_output=True, check=True)
            console.print("[cyan]Running FFuf for additional directory discovery...[/cyan]")
            
            for subdomain in list(self.subdomains)[:5]:  # Limit to avoid timeout
                try:
                    output_file = f'reports/ffuf_{subdomain.replace(".", "_")}.json'
                    cmd = [
                        'ffuf',
                        '-u', f'https://{subdomain}/FUZZ',
                        '-w', self.wordlist_path,
                        '-of', 'json',
                        '-o', output_file,
                        '-mc', '200,301,302,403',
                        '-t', str(min(self.threads, 50)),
                        '-timeout', str(self.timeout),
                        '-sf'  # Silent mode
                    ]
                    
                    process = subprocess.run(cmd, capture_output=True, timeout=120)
                    
                    if os.path.exists(output_file):
                        self._parse_ffuf_results(output_file, subdomain)
                        
                except subprocess.TimeoutExpired:
                    console.print(f"[yellow]FFuf timeout for {subdomain}[/yellow]")
                except Exception as e:
                    console.print(f"[yellow]FFuf error for {subdomain}: {e}[/yellow]")
                    
        except (subprocess.CalledProcessError, FileNotFoundError):
            console.print("[yellow]FFuf not available, skipping[/yellow]")

    def _run_dirb(self):
        """Run Dirb for directory fuzzing"""
        try:
            subprocess.run(['dirb'], capture_output=True, check=False)
            console.print("[cyan]Running Dirb for additional directory discovery...[/cyan]")
            
            for subdomain in list(self.subdomains)[:3]:  # Limit to avoid timeout
                try:
                    output_file = f'reports/dirb_{subdomain.replace(".", "_")}.txt'
                    cmd = [
                        'dirb',
                        f'https://{subdomain}',
                        self.wordlist_path,
                        '-o', output_file,
                        '-S',  # Silent mode
                        '-r',  # Non-recursive
                        '-t'   # Don't check for certificate
                    ]
                    
                    process = subprocess.run(cmd, capture_output=True, timeout=180)
                    
                    if os.path.exists(output_file):
                        self._parse_dirb_results(output_file, subdomain)
                        
                except subprocess.TimeoutExpired:
                    console.print(f"[yellow]Dirb timeout for {subdomain}[/yellow]")
                except Exception as e:
                    console.print(f"[yellow]Dirb error for {subdomain}: {e}[/yellow]")
                    
        except FileNotFoundError:
            console.print("[yellow]Dirb not available, skipping[/yellow]")

    def _parse_ffuf_results(self, output_file, subdomain):
        """Parse FFuf JSON results"""
        try:
            with open(output_file, 'r') as f:
                data = json.load(f)
                
            for result in data.get('results', []):
                finding = {
                    'subdomain': subdomain,
                    'url': result.get('url', ''),
                    'directory': result.get('input', {}).get('FUZZ', ''),
                    'status_code': result.get('status', 0),
                    'content_length': result.get('length', 0),
                    'content_type': '',
                    'server': '',
                    'timestamp': datetime.now().isoformat(),
                    'tool': 'ffuf'
                }
                
                if subdomain not in self.directory_results:
                    self.directory_results[subdomain] = []
                    
                self.directory_results[subdomain].append(finding)
                self.all_findings.append(finding)
                
        except Exception as e:
            console.print(f"[yellow]Error parsing FFuf results: {e}[/yellow]")

    def _parse_dirb_results(self, output_file, subdomain):
        """Parse Dirb text results"""
        try:
            with open(output_file, 'r') as f:
                lines = f.readlines()
                
            for line in lines:
                if '+ https://' in line or '+ http://' in line:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        url = parts[1]
                        status_code = 200  # Dirb typically only shows found directories
                        
                        # Extract directory from URL
                        parsed = urlparse(url)
                        directory = parsed.path.lstrip('/')
                        
                        finding = {
                            'subdomain': subdomain,
                            'url': url,
                            'directory': directory,
                            'status_code': status_code,
                            'content_length': 0,
                            'content_type': '',
                            'server': '',
                            'timestamp': datetime.now().isoformat(),
                            'tool': 'dirb'
                        }
                        
                        if subdomain not in self.directory_results:
                            self.directory_results[subdomain] = []
                            
                        self.directory_results[subdomain].append(finding)
                        self.all_findings.append(finding)
                        
        except Exception as e:
            console.print(f"[yellow]Error parsing Dirb results: {e}[/yellow]")

    def _load_wordlist(self):
        """Load wordlist from file"""
        try:
            with open(self.wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                words = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            return words[:2000]  # Limit wordlist size to avoid timeout
        except Exception as e:
            console.print(f"[red]Error loading wordlist: {e}[/red]")
            return []

    def _count_wordlist_entries(self):
        """Count entries in wordlist"""
        try:
            with open(self.wordlist_path, 'r') as f:
                return len([line for line in f if line.strip() and not line.startswith('#')])
        except:
            return 0

    def _process_results(self, progress, task):
        """Process and deduplicate results"""
        progress.update(task, description="Processing and deduplicating results...")
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_findings = []
        
        for finding in self.all_findings:
            url = finding.get('url', '')
            if url not in seen_urls:
                seen_urls.add(url)
                unique_findings.append(finding)
        
        self.all_findings = unique_findings
        
        # Update progress
        for i in range(100):
            progress.advance(task, 1)
            time.sleep(0.01)
            
        console.print(f"[cyan]Processed results: {len(self.all_findings)} unique findings[/cyan]")

    def _format_directory_results(self) -> str:
        """Format directory fuzzing results"""
        results = "## Directory Fuzzing Results\n\n"
        
        if not self.all_findings:
            results += "No directories found during fuzzing.\n"
            return results
        
        # Summary by subdomain
        results += "#### Summary by Subdomain\n\n"
        results += "| Subdomain | Directories Found | Status Codes | Tools Used |\n"
        results += "|:----------|:------------------|:-------------|:-----------|\n"
        
        for subdomain, findings in self.directory_results.items():
            if findings:
                status_codes = set([str(f.get('status_code', '')) for f in findings])
                tools = set([f.get('tool', 'python') for f in findings])
                results += f"| {subdomain} | {len(findings)} | {', '.join(sorted(status_codes))} | {', '.join(sorted(tools))} |\n"
        
        results += "\n#### Detailed Findings\n\n"
        results += "| URL | Status | Length | Content-Type | Server |\n"
        results += "|:----|:-------|:-------|:-------------|:-------|\n"
        
        # Sort findings by status code and subdomain
        sorted_findings = sorted(self.all_findings, key=lambda x: (x.get('status_code', 999), x.get('subdomain', '')))
        
        for finding in sorted_findings[:100]:  # Limit to first 100 for readability
            url = finding.get('url', '')
            status = finding.get('status_code', '')
            length = finding.get('content_length', 0)
            content_type = finding.get('content_type', '').split(';')[0]  # Remove charset info
            server = finding.get('server', '')
            
            results += f"| {url} | {status} | {length} | {content_type} | {server} |\n"
        
        if len(self.all_findings) > 100:
            results += f"\n*... and {len(self.all_findings) - 100} more findings (see full report)*\n"
        
        results += f"\n#### Statistics\n\n"
        results += f"- Total Directories Found: {len(self.all_findings)}\n"
        results += f"- Subdomains Scanned: {len(self.subdomains)}\n"
        results += f"- Subdomains with Findings: {len([k for k, v in self.directory_results.items() if v])}\n"
        
        # Status code breakdown
        status_counts = {}
        for finding in self.all_findings:
            status = finding.get('status_code', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        results += f"- Status Code Breakdown:\n"
        for status, count in sorted(status_counts.items()):
            results += f"  - {status}: {count}\n"
        
        return results

    def _save_json_results(self, output_path):
        """Save results in JSON format for integration"""
        try:
            json_data = {
                'target_domain': self.target_domain,
                'scan_timestamp': datetime.now().isoformat(),
                'total_subdomains': len(self.subdomains),
                'total_findings': len(self.all_findings),
                'wordlist_path': self.wordlist_path,
                'wordlist_size': self._count_wordlist_entries(),
                'subdomains': list(self.subdomains),
                'findings': self.all_findings,
                'results_by_subdomain': self.directory_results
            }
            
            with open(output_path, 'w') as f:
                json.dump(json_data, f, indent=2)
                
            console.print(f"[green]JSON results saved to: {output_path}[/green]")
            
        except Exception as e:
            console.print(f"[red]Error saving JSON results: {e}[/red]")

    def _generate_pdf_report(self, stats: dict, output_path: str):
        """Generate comprehensive PDF report for directory fuzzing"""
        try:
            from fpdf import FPDF
            
            class DirectoryPDF(FPDF):
                def __init__(self):
                    super().__init__()
                    self.logo_path = 'Images/logo.png' if os.path.exists('Images/logo.png') else None
                    
                def header(self):
                    # Simulate a vertical gradient background from #1B2D48 to #223A5F
                    steps = 30
                    for i in range(steps):
                        r1, g1, b1 = 27, 45, 72  # #1B2D48
                        r2, g2, b2 = 34, 58, 95  # #223A5F
                        r = int(r1 + (r2 - r1) * i / steps)
                        g = int(g1 + (g2 - g1) * i / steps)
                        b = int(b1 + (b2 - b1) * i / steps)
                        y = self.h * i / steps
                        self.set_fill_color(r, g, b)
                        self.rect(0, y, self.w, self.h / steps + 1, 'F')
                    if self.logo_path:
                        try:
                            # Even smaller logo for header
                            logo_width = 10
                            logo_height = 10
                            x_pos = self.w - logo_width - 10
                            self.image(self.logo_path, x_pos, 8, logo_width, logo_height)
                        except Exception:
                            pass
                    self.set_font('Arial', 'B', 9)  # Smaller font size
                    self.set_text_color(0, 255, 0)  # Green
                    self.cell(0, 10, 'TrimurtiSec Directory Fuzzing Framework', 0, 0, 'L')
                    self.ln(15)
                    
                def footer(self):
                    """Add footer to every page"""
                    self.set_y(-15)
                    self.set_font('Arial', '', 8)
                    self.set_text_color(200, 200, 200)
                    self.cell(0, 10, f'TrimurtiSec Report | Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")} | Page {self.page_no()}', 0, 0, 'C')
            
            pdf = DirectoryPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)

            # Use built-in Arial font to avoid font loading issues
            font_family = 'Arial'
            console.print("[cyan]Using built-in Arial font for PDF generation[/cyan]")

            # Title Page - Large centered logo
            if pdf.logo_path:
                try:
                    # Large centered logo for title page
                    logo_width = 50
                    logo_height = 50
                    x_pos = (pdf.w - logo_width) / 2  # Center on page
                    pdf.set_xy(x_pos, 30)
                    pdf.image(pdf.logo_path, x_pos, 30, logo_width, logo_height)
                    pdf.ln(55)  # Move down after large logo
                    # Add slogan below logo
                    pdf.set_font(font_family, 'I', 14)
                    pdf.set_text_color(255, 215, 0)  # Gold
                    pdf.cell(0, 12, '"Three faces, one mission - Secure Everything."', 0, 1, 'C')
                    pdf.ln(10)
                except Exception as e:
                    console.print(f"[yellow]Could not load title page logo: {e}[/yellow]")
                    pdf.ln(30)
            else:
                pdf.ln(30)
            
            pdf.set_font(font_family, 'B', 28)
            pdf.set_text_color(0, 255, 0)  # Green
            pdf.cell(0, 20, 'TrimurtiSec Penetration Test Report', 0, 1, 'C')
            
            pdf.set_font(font_family, 'B', 18)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(0, 15, 'Directory Fuzzing & Enumeration', 0, 1, 'C')
            
            pdf.ln(20)
            pdf.set_font(font_family, '', 14)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(0, 10, f"Target Domain: {self.target_domain or 'Multiple Subdomains'}", 0, 1, 'C')
            pdf.cell(0, 8, f"Assessment Date: {datetime.now().strftime('%B %d, %Y')}", 0, 1, 'C')
            pdf.cell(0, 8, f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}", 0, 1, 'C')
            pdf.ln(10)
            
            # Add classification and confidentiality notice
            pdf.ln(30)
            pdf.set_font(font_family, 'B', 12)
            pdf.set_text_color(255, 0, 0)  # Red
            pdf.cell(0, 8, 'CONFIDENTIAL - PENETRATION TEST REPORT', 0, 1, 'C')
            
            pdf.set_font(font_family, 'I', 10)
            pdf.set_text_color(255, 255, 255)
            pdf.ln(10)
            confidentiality_text = (
                "This document contains confidential and proprietary information. "
                "Distribution is restricted to authorized personnel only. "
                "This report is intended solely for the organization that commissioned the assessment."
            )
            # Split text into multiple lines
            words = confidentiality_text.split()
            line = ""
            for word in words:
                if pdf.get_string_width(line + word + " ") < 180:
                    line += word + " "
                else:
                    pdf.cell(0, 6, line.strip(), 0, 1, 'C')
                    line = word + " "
            if line:
                pdf.cell(0, 6, line.strip(), 0, 1, 'C')
            
            # Add new page for executive summary
            pdf.add_page()
            pdf.ln(10)
            
            # Executive Summary Section
            pdf.set_font(font_family, 'B', 20)
            pdf.set_text_color(255, 215, 0)  # Gold
            pdf.cell(0, 15, 'EXECUTIVE SUMMARY', 0, 1, 'L')
            pdf.ln(5)
            
            # Calculate risk metrics
            total_subdomains = stats['Target Subdomains']
            total_directories = stats['Total Directories Found']
            subdomains_with_findings = stats['Subdomains with Findings']
            wordlist_size = stats['Wordlist Size']
            
            # Executive summary content
            pdf.set_font(font_family, '', 12)
            pdf.set_text_color(255, 255, 255)
            
            exec_summary = (
                f"This penetration test report presents the findings from a comprehensive directory enumeration "
                f"assessment conducted against {total_subdomains} subdomains of {self.target_domain or 'the target domain'}. "
                f"The assessment utilized industry-standard directory fuzzing techniques including multi-threaded "
                f"HTTP requests and external tools to identify accessible directories and files.\n\n"
                f"The enumeration successfully identified {total_directories} accessible directories across "
                f"{subdomains_with_findings} subdomains using a wordlist of {wordlist_size} entries. "
                f"This discovery phase represents a critical reconnaissance stage of penetration testing "
                f"and provides valuable intelligence about the target's web infrastructure and potential "
                f"attack vectors.\n\n"
            )
            
            # Risk assessment based on findings
            if total_directories == 0:
                risk_level = "LOW"
                risk_color = (0, 255, 0)
                risk_text = (
                    "No accessible directories were discovered during this assessment, indicating a minimal "
                    "exposed web infrastructure. However, this does not preclude the existence of hidden "
                    "directories or those protected by access controls."
                )
            elif total_directories <= 10:
                risk_level = "MEDIUM"
                risk_color = (255, 255, 0)
                risk_text = (
                    "A limited number of accessible directories were discovered. While this suggests a controlled "
                    "web presence, each discovered directory represents a potential entry point that "
                    "requires further security assessment."
                )
            else:
                risk_level = "HIGH"
                risk_color = (255, 0, 0)
                risk_text = (
                    "A significant number of accessible directories were discovered, indicating an extensive "
                    "web infrastructure. This large attack surface increases the probability "
                    "of finding exploitable vulnerabilities and requires comprehensive security review."
                )
            
            exec_summary += f"Based on the findings, the current risk level is assessed as {risk_level}. {risk_text}"
            
            # Wrap and display executive summary text
            words = exec_summary.split()
            line = ""
            for word in words:
                if pdf.get_string_width(line + word + " ") < 180:
                    line += word + " "
                else:
                    pdf.cell(0, 6, line.strip(), 0, 1, 'L')
                    line = word + " "
            if line:
                pdf.cell(0, 6, line.strip(), 0, 1, 'L')
            
            pdf.ln(10)
            
            # Risk Level Box
            pdf.set_font(font_family, 'B', 14)
            pdf.set_text_color(risk_color[0], risk_color[1], risk_color[2])
            pdf.cell(0, 10, f'OVERALL RISK LEVEL: {risk_level}', 0, 1, 'C')
            pdf.ln(10)
            
            # Key Findings Box
            pdf.set_font(font_family, 'B', 16)
            pdf.set_text_color(255, 215, 0)  # Gold
            pdf.cell(0, 10, 'KEY FINDINGS', 0, 1, 'L')
            pdf.ln(5)
            
            pdf.set_font(font_family, '', 12)
            pdf.set_text_color(255, 255, 255)
            
            key_findings = [
                f"Total subdomains scanned: {total_subdomains}",
                f"Accessible directories found: {total_directories}",
                f"Subdomains with findings: {subdomains_with_findings}",
                f"Wordlist size utilized: {wordlist_size} entries",
                "Tools utilized: Python requests, FFuf, Dirb",
                "Assessment methodology: Multi-threaded directory enumeration"
            ]
            
            for finding in key_findings:
                pdf.cell(8, 8, '-', 0, 0, 'L')
                pdf.set_text_color(255, 255, 102)  # Yellowish for subheading
                pdf.cell(0, 8, finding, 0, 1, 'L')
                pdf.set_text_color(255, 255, 255)  # Reset to white
            
            pdf.ln(10)
            
            # Add new page for detailed findings
            pdf.add_page()
            pdf.ln(10)
            
            # Detailed Technical Findings
            pdf.set_font(font_family, 'B', 20)
            pdf.set_text_color(255, 215, 0)  # Gold
            pdf.cell(0, 15, 'DETAILED TECHNICAL FINDINGS', 0, 1, 'L')
            pdf.ln(5)
            
            # Methodology section
            pdf.set_font(font_family, 'B', 14)
            pdf.cell(0, 10, '1. ASSESSMENT METHODOLOGY', 0, 1, 'L')
            pdf.ln(3)
            
            pdf.set_font(font_family, '', 11)
            pdf.set_text_color(255, 255, 255)
            
            methodology_text = (
                "The directory enumeration assessment was conducted using a multi-phase approach:\n\n"
                "Phase 1 - Subdomain Loading: Loaded discovered subdomains from previous reconnaissance "
                "results including HTTPX output and Subfinder results to establish the target scope.\n\n"
                "Phase 2 - Wordlist Preparation: Utilized comprehensive wordlists including common "
                "directories, files, and extensions to ensure thorough coverage of potential web assets.\n\n"
                "Phase 3 - Multi-threaded Enumeration: Employed Python-based HTTP requests with threading "
                "for efficient directory discovery while maintaining controlled scanning rates.\n\n"
                "Phase 4 - External Tool Integration: Leveraged additional tools including FFuf and Dirb "
                "for enhanced discovery and validation of findings."
            )
            
            # Wrap methodology text
            words = methodology_text.split()
            line = ""
            for word in words:
                if word == "\n\n":
                    pdf.cell(0, 6, line.strip(), 0, 1, 'L')
                    pdf.ln(3)
                    line = ""
                elif pdf.get_string_width(line + word + " ") < 180:
                    line += word + " "
                else:
                    pdf.cell(0, 6, line.strip(), 0, 1, 'L')
                    line = word + " "
            if line:
                pdf.cell(0, 6, line.strip(), 0, 1, 'L')
            
            pdf.ln(10)
            
            # Discovery Results Section
            pdf.set_font(font_family, 'B', 14)
            pdf.cell(0, 10, '2. DIRECTORY ENUMERATION RESULTS', 0, 1, 'L')
            pdf.ln(3)
            
            # Summary Stats Table
            pdf.set_font(font_family, 'B', 12)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(0, 10, 'Assessment Summary', 0, 1, 'L')
            
            pdf.set_font(font_family, '', 12)
            pdf.set_fill_color(245, 245, 245)
            
            for key, value in stats.items():
                pdf.set_font(font_family, 'B', 12)
                pdf.cell(60, 10, str(key), 0, 0, 'L')
                pdf.set_font(font_family, '', 12)
                pdf.cell(0, 10, str(value), 0, 1, 'L')
            pdf.ln(10)

            # Results Table
            pdf.set_font(font_family, 'B', 16)
            pdf.cell(0, 10, 'Discovered Directories', 0, 1, 'L')

            if not self.all_findings:
                pdf.set_font(font_family, '', 12)
                pdf.cell(0, 10, "No directories were discovered.", 0, 1, 'L')
            else:
                pdf.set_font(font_family, 'B', 10)
                pdf.set_fill_color(70, 130, 180) # SteelBlue
                pdf.set_text_color(0, 0, 0)  # Black
                
                col_widths = {'URL': 80, 'Status': 20, 'Length': 25, 'Content-Type': 40, 'Server': 35}
                for header, width in col_widths.items():
                    pdf.cell(width, 10, header, 1, 0, 'C', 1)
                pdf.ln()

                pdf.set_font(font_family, '', 8)
                pdf.set_text_color(0, 0, 0)  # Black
                fill = False
                
                # Show first 50 findings
                for finding in self.all_findings[:50]:
                    url = finding.get('url', '')[:35]
                    status = str(finding.get('status_code', ''))
                    length = str(finding.get('content_length', ''))
                    content_type = finding.get('content_type', '').split(';')[0][:20]
                    server = finding.get('server', '')[:15]
                    
                    pdf.set_fill_color(245, 245, 245) if fill else pdf.set_fill_color(255, 255, 255)
                    pdf.cell(col_widths['URL'], 8, url, 1, 0, 'L', 1)
                    pdf.cell(col_widths['Status'], 8, status, 1, 0, 'C', 1)
                    pdf.cell(col_widths['Length'], 8, length, 1, 0, 'C', 1)
                    pdf.cell(col_widths['Content-Type'], 8, content_type, 1, 0, 'L', 1)
                    pdf.cell(col_widths['Server'], 8, server, 1, 1, 'L', 1)
                    fill = not fill
            
            pdf.ln(10)
            
            # Add new page for status code analysis
            pdf.add_page()
            pdf.ln(10)
            
            # Status Code Analysis Section
            pdf.set_font(font_family, 'B', 16)
            pdf.set_text_color(255, 215, 0)  # Gold
            pdf.cell(0, 10, '3. STATUS CODE ANALYSIS', 0, 1, 'L')
            pdf.ln(5)
            
            # Calculate status code breakdown
            status_counts = {}
            for finding in self.all_findings:
                status = finding.get('status_code', 'Unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            pdf.set_font(font_family, 'B', 14)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(0, 10, '3.1 Status Code Distribution', 0, 1, 'L')
            pdf.ln(3)
            
            pdf.set_font(font_family, '', 11)
            pdf.set_text_color(255, 255, 255)
            
            for status, count in sorted(status_counts.items()):
                percentage = (count / len(self.all_findings)) * 100
                pdf.cell(0, 8, f"{status} - {count} findings ({percentage:.1f}%)", 0, 1, 'L')
            
            pdf.ln(10)
            
            # Subdomain Analysis
            pdf.set_font(font_family, 'B', 14)
            pdf.cell(0, 10, '3.2 Findings by Subdomain', 0, 1, 'L')
            pdf.ln(3)
            
            pdf.set_font(font_family, '', 11)
            pdf.set_text_color(255, 255, 255)
            
            for subdomain, findings in self.directory_results.items():
                if findings:
                    pdf.cell(0, 8, f"{subdomain}: {len(findings)} directories found", 0, 1, 'L')
            
            pdf.ln(15)
            
            # Recommendations Section
            pdf.set_font(font_family, 'B', 16)
            pdf.set_text_color(255, 215, 0)  # Gold
            pdf.cell(0, 10, '4. SECURITY RECOMMENDATIONS', 0, 1, 'L')
            pdf.ln(5)
            
            recommendations = [
                "4.1 Immediate Actions:",
                "- Review all discovered directories for sensitive information exposure",
                "- Implement proper access controls on administrative and sensitive directories",
                "- Remove or secure backup, test, and development directories",
                "- Ensure all directories have appropriate authentication mechanisms",
                "",
                "4.2 Security Hardening:",
                "- Deploy Web Application Firewalls (WAF) to protect against directory traversal",
                "- Implement proper HTTP security headers (X-Frame-Options, X-Content-Type-Options)",
                "- Configure server to return 404 for non-existent directories",
                "- Use robots.txt and security.txt files appropriately",
                "",
                "4.3 Monitoring and Maintenance:",
                "- Establish continuous monitoring for new directory discoveries",
                "- Implement intrusion detection for directory enumeration attempts",
                "- Regular security assessments and penetration testing",
                "- Maintain an updated inventory of web assets",
                "",
                "4.4 Risk Mitigation:",
                "- Decommission unused directories and web services",
                "- Implement network segmentation for web servers",
                "- Regular backup and disaster recovery testing",
                "- Staff security awareness training on web security"
            ]
            for line in recommendations:
                if line.startswith('- '):
                    pdf.set_font(font_family, 'I', 11)  # Italic for bullet points
                    pdf.set_text_color(255, 255, 255)
                    pdf.cell(0, 8, line, 0, 1, 'L')
                    pdf.set_font(font_family, '', 11)  # Restore normal font after bullet
                elif line.strip() == '':
                    pdf.ln(3)
                else:
                    pdf.set_font(font_family, 'B', 12)
                    pdf.set_text_color(255, 255, 255)
                    pdf.cell(0, 8, line, 0, 1, 'L')
            
            # Conclusion
            pdf.ln(15)
            pdf.set_font(font_family, 'B', 16)
            pdf.set_text_color(255, 215, 0)  # Gold for heading
            pdf.cell(0, 10, '5. CONCLUSION', 0, 1, 'L')
            pdf.ln(5)
            
            pdf.set_font(font_family, '', 11)
            pdf.set_text_color(255, 255, 255)  # White for body text
            
            conclusion_text = (
                f"This directory enumeration assessment for {self.target_domain or 'the target domain'} has mapped the organization's web infrastructure, identifying {total_directories} accessible directories across {subdomains_with_findings} subdomains. "
                f"These discovered assets represent potential entry points for threat actors and should be prioritized for further security evaluation, including vulnerability scanning and penetration testing. "
                f"Each discovered directory should be reviewed for sensitive information exposure and appropriate access controls.\n\n"
                f"The dynamic nature of web applications means that new directories may be created and existing ones may change over time. Regular automated enumeration and validation are essential to maintain an accurate inventory and reduce the risk of information disclosure.\n\n"
                f"It is recommended that the organization implements proper access controls, removes unnecessary directories, and integrates directory monitoring into its continuous security operations. "
                f"By maintaining visibility and acting on the findings of this assessment, the organization can significantly reduce its web-based attack surface and improve its overall cybersecurity posture."
            )
            
            # Wrap conclusion text
            words = conclusion_text.split()
            line = ""
            for word in words:
                if pdf.get_string_width(line + word + " ") < 180:
                    line += word + " "
                else:
                    pdf.cell(0, 6, line.strip(), 0, 1, 'L')
                    line = word + " "
            if line:
                pdf.cell(0, 6, line.strip(), 0, 1, 'L')
            
            pdf.ln(20)

            try:
                pdf.output(output_path)
                console.print(f"[green]PDF report generated: {output_path}[/green]")
            except Exception as e:
                console.print(f"[bold red]Error generating PDF report: {e}[/bold red]")
            
        except ImportError:
            console.print("[yellow]FPDF not available, skipping PDF report generation[/yellow]")
        except Exception as e:
            console.print(f"[red]Error generating PDF report: {e}[/red]")

    def get_results_for_analysis(self):
        """Get results formatted for AI analysis"""
        return {
            'target_domain': self.target_domain,
            'total_subdomains': len(self.subdomains),
            'total_findings': len(self.all_findings),
            'findings': self.all_findings,
            'results_by_subdomain': self.directory_results
        } 