import socket
import dns.resolver
import dns.query
import dns.zone
import requests
from rich.console import Console
from rich.progress import Progress
from concurrent.futures import ThreadPoolExecutor

console = Console()

class SubdomainDiscovery:
    def __init__(self, target):
        self.target = target
        self.subdomains = set()

    def discover(self):
        results = "## Subdomain Discovery Results\n\n"

        if self._is_ip_address(self.target):
            return "Subdomain discovery requires a domain name, not an IP address."

        results += f"Target Domain: {self.target}\n\n"

        with Progress() as progress:
            task = progress.add_task("[green]Discovering subdomains...", total=3)

            console.log(f"Brute forcing common subdomains for {self.target}")
            self._brute_force_subdomains()
            progress.update(task, advance=1)

            console.log("Checking certificate transparency logs")
            self._check_certificate_transparency()
            progress.update(task, advance=1)

            console.log("Attempting DNS zone transfer")
            self._attempt_zone_transfer()
            progress.update(task, advance=1)

        results += "### Discovered Subdomains\n\n"
        if self.subdomains:
            results += "| Subdomain | IP Address | Status |\n"
            results += "|-----------|------------|--------|\n"

            for subdomain in sorted(self.subdomains):
                try:
                    ip = socket.gethostbyname(subdomain)
                    status = self._check_http_status(subdomain)
                    results += f"| {subdomain} | {ip} | {status} |\n"
                except socket.gaierror:
                    results += f"| {subdomain} | Could not resolve | N/A |\n"
        else:
            results += "No subdomains discovered.\n"

        return results

    def _is_ip_address(self, address):
        try:
            socket.inet_aton(address)
            return True
        except socket.error:
            return False

    def _brute_force_subdomains(self):
        common_subdomains = [
            "www", "mail", "remote", "blog", "webmail", "server", "ns1", "ns2",
            "smtp", "secure", "vpn", "m", "shop", "ftp", "cdn", "api",
            "dev", "staging", "app", "test", "admin", "portal", "intranet"
        ]

        def resolve(sub):
            full_domain = f"{sub}.{self.target}"
            try:
                ip = socket.gethostbyname(full_domain)
                self.subdomains.add(full_domain)
                console.log(f"Discovered subdomain: {full_domain} ({ip})")
            except socket.gaierror:
                pass

        with ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(resolve, common_subdomains)

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

    def _check_http_status(self, subdomain):
        for protocol in ['https', 'http']:
            try:
                response = requests.get(f"{protocol}://{subdomain}", timeout=5, allow_redirects=True, verify=False)
                return f"{response.status_code} ({response.reason})"
            except requests.exceptions.RequestException:
                continue
        return "Connection failed"
