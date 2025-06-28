# TrimurtiSec - Advanced Penetration Testing Framework

![TrimurtiSec Logo](./Images/logo.png)

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/mnshchtri/TrimurtiSec)
[![Python](https://img.shields.io/badge/python-3.9+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-red.svg)](LICENSE)
[![Security](https://img.shields.io/badge/security-professional-orange.svg)](https://github.com/mnshchtri/TrimurtiSec)

A comprehensive, enterprise-grade penetration testing framework inspired by the Hindu trinity concept (Brahma, Vishnu, and Shiva), with an additional "God Mode" for complete system control. TrimurtiSec is designed to be a modular, extensible, and powerful tool for ethical hacking, security assessment, and professional penetration testing engagements.

## 🔮 Concept

The framework is divided into four powerful modes, each representing a different phase of penetration testing:

### 1. Brahma Mode (Creation/Reconnaissance)
- **Comprehensive Subdomain Discovery**: Advanced enumeration using Subfinder with multiple data sources
- **Live Subdomain Probing**: Active verification using HTTPX with detailed response analysis
- **Professional PDF Reports**: Enterprise-grade penetration test reports with TrimurtiSec branding
- **Automated Vulnerability Scanning**: Industry-standard security assessment using Nuclei
- **SSL/TLS Security Analysis**: Certificate validation and encryption configuration testing
- **Technology Fingerprinting**: Web application stack detection and analysis
- **Risk-Based Assessment**: CRITICAL/HIGH/MEDIUM/LOW severity classification
- **Multi-Tool Integration**: Seamless integration of reconnaissance and security tools

### 2. Vishnu Mode (Persistence)
- Multi-platform backdoor implementation
- System service manipulation with privilege escalation
- Advanced cron job persistence techniques
- Stealth persistence mechanisms
- Long-term access maintenance with fail-safes

### 3. Shiva Mode (Destruction)
- Exploit execution with payload customization
- Advanced SQL injection attack vectors
- Remote Code Execution (RCE) with multiple vectors
- System compromise with privilege escalation
- Service disruption with minimal footprint

### 4. God Mode (Full Control)
- Advanced privilege escalation techniques
- Network pivoting with multiple protocols
- Domain administrator access acquisition
- Data exfiltration with encryption
- Anti-forensics with log manipulation

## 🚀 Installation

### Prerequisites
- Python 3.9+
- pip package manager
- nmap (for port scanning)
- Root/Administrator privileges (for certain operations)
- Git (for cloning the repository)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/mnshchtri/TrimurtiSec.git
cd TrimurtiSec
```

2. Create and activate a virtual environment:
```bash
# Create virtual environment
python -m venv venv

# Activate on Linux/macOS
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Trimurti:
```bash
pip install -e .
```

## 💫 Usage

### New Command Structure (v2.0+)

#### Brahma Mode - Advanced Reconnaissance & Vulnerability Assessment

**Subdomain Discovery:**
```bash
# Comprehensive subdomain enumeration
python -m trimurti run-trimurti -t example.com -m brahma --subdomain

# With verbose output
python -m trimurti run-trimurti -t example.com -m brahma --subdomain -v
```

**Vulnerability Scanning:**
```bash
# Automated vulnerability assessment
python -m trimurti run-trimurti -t example.com -m brahma --vulnerability-scan

# Scan with detailed logging
python -m trimurti run-trimurti -t example.com -m brahma --vulnerability-scan -v

# Quiet mode (minimal output)
python -m trimurti run-trimurti -t example.com -m brahma --vulnerability-scan -q
```

**IP Address Vulnerability Scanning:**
```bash
# Direct IP vulnerability assessment
python -m trimurti run-trimurti -t 192.168.1.100 -m brahma --vulnerability-scan
```

### Legacy Command Structure (Still Supported)

**Traditional Modes:**
```bash
# Basic reconnaissance
python -m trimurti run -t example.com -m brahma

# Persistence setup
python -m trimurti run -t 192.168.1.100 -m vishnu --method cron

# Exploitation
python -m trimurti run -t target.com -m shiva --exploit sql

# Full control
python -m trimurti run -t 10.0.0.1 -m god --action pivot
```

### Command Options
- `-t, --target`: Target IP address or domain (required)
- `-m, --mode`: Operation mode [brahma|vishnu|shiva|god] (required)
- `-o, --output`: Custom output file path (default: report.md)
- `-s, --subdomain-discovery`: Perform subdomain discovery (Brahma mode only)
- `--method`: Specific persistence method (Vishnu mode)
- `--exploit`: Specific exploit type (Shiva mode)
- `--action`: Specific control action (God mode)
- `-v, --verbose`: Increase output verbosity
- `-q, --quiet`: Suppress all output except errors

### Specialized Commands

1. Subdomain Discovery:
```bash
trimurti discover_subdomains -t example.com
```

## 📊 Professional Reports

TrimurtiSec generates **enterprise-grade PDF reports** with professional formatting and TrimurtiSec branding:

### Report Types Generated:

1. **Subdomain Discovery Report** (`reports/subdomain_discovery_report_[target].pdf`):
   - Executive summary with risk assessment
   - Complete subdomain inventory (live vs non-responsive)
   - Technical methodology documentation
   - Professional security recommendations
   - Confidentiality and classification notices

2. **Vulnerability Assessment Report** (`reports/vulnerability_scan_report_[target].pdf`):
   - Risk-based vulnerability analysis (CRITICAL/HIGH/MEDIUM/LOW)
   - Executive summary for business stakeholders
   - Detailed technical findings by severity
   - SSL/TLS configuration analysis
   - Technology fingerprinting results
   - Prioritized remediation recommendations (P1-P5)
   - Professional formatting with logos and headers

### Report Features:
- **Professional PDF formatting** with TrimurtiSec branding
- **Logo integration** on every page
- **Risk-based assessment** with color-coded severity levels
- **Executive summaries** for business stakeholders
- **Technical details** for security teams
- **Remediation timelines** and priority classifications
- **Confidentiality notices** and proper classification
- **Multi-page layouts** with consistent formatting

### Generated Files Structure:
```
reports/
├── subdomain_discovery_report_[target].pdf     # Professional reconnaissance report
├── vulnerability_scan_report_[target].pdf      # Comprehensive vulnerability assessment
├── subfinder_results.txt                       # Raw subdomain enumeration data
├── httpx_results.json                          # Live subdomain verification results
├── nuclei_vulnerability_results.json           # Detailed vulnerability findings
└── live_targets.txt                            # Target URLs for vulnerability scanning
```

## 🛠️ Features

### Brahma Mode Features
- TCP port scanning (1-1000)
- Service version detection
- OS fingerprinting
- Subdomain discovery and enumeration
  - Brute force common subdomains
  - Certificate transparency log checking
  - DNS zone transfer attempts
  - HTTP/HTTPS status verification
- Progress tracking
- Detailed port mapping

### Vishnu Mode Features
- Cron job backdoors
- Systemd service persistence
- SSH key backdoors
- Reverse shell implementation
- Service manipulation

### Shiva Mode Features
- SQL injection attacks
- Remote Code Execution
- Service disruption
- System compromise
- Data destruction capabilities

### God Mode Features
- Privilege escalation (CVE-2021-4034)
- Network pivoting
- Domain admin access
- Data exfiltration
- Log cleanup and anti-forensics

## 🔧 Development

### Project Structure
```
trimurti-pentest/
├── requirements.txt
├── setup.py
└── trimurti/
    ├── __init__.py
    ├── cli.py
    ├── brahma/
    │   ├── __init__.py
    │   └── port_scanner.py
    ├── vishnu/
    │   ├── __init__.py
    │   └── c2_server.py
    ├── shiva/
    │   ├── __init__.py
    │   └── exploit.py
    ├── god_mode/
    │   ├── __init__.py
    │   └── full_control.py
    └── utils/
        ├── __init__.py
        └── report_gen.py
```

### Dependencies
```python
click>=8.0.0
markdown>=3.3.0
requests>=2.26.0
scapy>=2.4.5
python-nmap>=0.7.1
paramiko>=2.8.1
colorama>=0.4.4
rich>=10.12.0
dnspython>=2.2.0
reportlab>=4.0.0
weasyprint>=65.0
jinja2>=3.1.0
fpdf2
```

### External Tools (Auto-Installed)
```bash
# Reconnaissance Tools
Subfinder    # Subdomain discovery with multiple data sources
HTTPX        # Fast and versatile HTTP toolkit

# Vulnerability Assessment Tools
Nuclei       # Fast vulnerability scanner with extensive templates
WhatWeb      # Web application fingerprinting (optional)
OpenSSL      # SSL/TLS certificate analysis

# Installation via Go (automated)
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
```

## 📚 Documentation

For detailed documentation, visit our [official documentation](https://trimurti-pentest.readthedocs.io).

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Legal Disclaimer

This tool is for educational and authorized security testing purposes only. Usage of Trimurti for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state, and federal laws. The developers assume no liability and are not responsible for any misuse or damage caused by this program.

## 🔒 Security Considerations

1. Never use this tool against unauthorized targets
2. Always obtain proper authorization before testing
3. Use appropriate logging and documentation
4. Follow responsible disclosure practices
5. Maintain proper access controls
6. Regularly update dependencies
7. Follow secure coding practices

## 🚀 Getting Started

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Install Trimurti
pip install -e .

# Run a basic scan
trimurti run -t example.com -m brahma
```

### Advanced Usage

```bash
# Detailed reconnaissance with all options
trimurti run -t example.com -m brahma \
    --subdomain-discovery \
    --verbose \
    -o detailed_report.md

# Persistence with specific method
trimurti run -t 192.168.1.100 -m vishnu \
    --method cron \
    --verbose

# Exploitation with specific vector
trimurti run -t target.com -m shiva \
    --exploit sql \
    --verbose
```

## 🛠️ Development Setup

### Setting Up Development Environment

1. Clone the repository:
```bash
git clone https://github.com/yourusername/trimurti-pentest.git
cd trimurti-pentest
```

2. Create a virtual environment:
```bash
python -m venv venv
cd venv
source bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -r requirements.txt
pip install -r dev-requirements.txt
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_brahma.py

# Run with coverage
python -m pytest --cov=trimurti
```

## 📊 Performance Considerations

1. Use appropriate timeouts for network operations
2. Implement rate limiting for sensitive operations
3. Use asynchronous operations where possible
4. Implement proper error handling and retries
5. Monitor resource usage during operations

## 🔄 Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/yourusername/trimurti-pentest/tags).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- n30x (@mnshchtri)

## 🙏 Acknowledgments

- Named after the Hindu trinity: Brahma (Creator), Vishnu (Preserver), and Shiva (Destroyer)
- Inspired by various open-source security tools
- Thanks to all contributors and the security research community

## 📞 Support

For support, please open an issue in the GitHub repository or contact the maintainers directly.

## 🎯 Vulnerability Scanning Features

### Comprehensive Security Assessment

**Multi-Tool Integration:**
- **Nuclei**: Industry-standard vulnerability scanner with 4000+ templates
- **SSL/TLS Analysis**: Certificate validation and encryption security
- **Technology Detection**: Web application stack fingerprinting
- **Smart Target Discovery**: Automatic live subdomain detection

**Vulnerability Categories Detected:**
- CVE-based vulnerabilities (Critical/High/Medium/Low)
- Cross-Site Scripting (XSS) vectors
- SQL Injection vulnerabilities
- Remote Code Execution (RCE) flaws
- Local File Inclusion (LFI) vulnerabilities
- Server-Side Request Forgery (SSRF)
- Security misconfigurations
- Information disclosure issues
- Authentication bypass vulnerabilities
- Directory traversal attacks

**Professional Risk Assessment:**
- **CRITICAL**: Immediate action required (P1 - Fix Immediately)
- **HIGH**: High risk (P2 - Fix Within 24h)
- **MEDIUM**: Medium risk (P3 - Fix Within 1 Week)
- **LOW**: Low risk (P4 - Fix Within 1 Month)
- **INFO**: Informational (P5 - Monitor)

### Vulnerability Scanning Workflow

1. **Target Discovery**: Load from previous subdomain scans or discover live targets
2. **Tool Installation**: Automatically install and update Nuclei templates
3. **Comprehensive Scanning**: Multi-vector vulnerability assessment
4. **SSL/TLS Analysis**: Certificate and encryption security validation
5. **Technology Fingerprinting**: Web application stack detection
6. **Risk Assessment**: Severity-based vulnerability classification
7. **Professional Reporting**: Enterprise-grade PDF report generation

### Example Vulnerability Scan Output

```bash
$ python -m trimurti run-trimurti -t example.com -m brahma --vulnerability-scan

🔱 TrimurtiSec - Advanced Penetration Testing Framework 🔱
✅ Framework ready for cyber operations!

🔴 Initiating vulnerability assessment on example.com

[●●●●●●●●●●] 100% Loading vulnerability databases...
[●●●●●●●●●●] 100% Installing and updating vulnerability databases...
[●●●●●●●●●●] 100% Performing comprehensive security assessment...
[●●●●●●●●●●] 100% Analyzing SSL/TLS configurations...
[●●●●●●●●●●] 100% Detecting web technologies and frameworks...
[●●●●●●●●●●] 100% Compiling vulnerability findings...

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                            MISSION ACCOMPLISHED                        ┃
┃                                                                         ┃
┃   Target: example.com                                                   ┃
┃   Targets Scanned: 5                                                    ┃
┃   Total Vulnerabilities: 12                                             ┃
┃   Critical Issues: 2                                                     ┃
┃   High Severity: 3                                                       ┃
┃   Medium Severity: 4                                                     ┃
┃   Low Severity: 3                                                        ┃
┃   Status: Vulnerability Scan Complete                                    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Vulnerability report saved to: reports/vulnerability_scan_report_example_com.pdf
Vulnerability scanning complete. Found 12 potential security issues.
```

## 🔄 Version History

### v2.0.0 (Latest) - Enterprise Vulnerability Assessment
- **NEW**: Separate vulnerability scanning command structure
- **NEW**: Professional PDF report generation with TrimurtiSec branding
- **NEW**: Automated Nuclei integration with 4000+ vulnerability templates
- **NEW**: SSL/TLS security analysis and certificate validation
- **NEW**: Risk-based vulnerability assessment (CRITICAL/HIGH/MEDIUM/LOW)
- **NEW**: Smart target discovery from previous subdomain scans
- **NEW**: Technology fingerprinting with WhatWeb integration
- **NEW**: Professional remediation recommendations with P1-P5 priorities
- **NEW**: Enterprise-grade executive summaries for business stakeholders
- **NEW**: Logo integration and professional formatting on all reports
- **ENHANCED**: Command structure with `run-trimurti` for advanced operations
- **ENHANCED**: Comprehensive error handling and graceful failures
- **ENHANCED**: Progress tracking with enhanced animations

### v1.1.0 - Advanced Subdomain Discovery
- Added comprehensive subdomain discovery functionality
- Subfinder integration with multiple data sources
- HTTPX integration for live subdomain verification
- Professional PDF report generation
- Certificate transparency log checking
- DNS zone transfer attempts
- Dedicated CLI command structure

### v1.0.0 - Initial Release
- Four operational modes (Brahma, Vishnu, Shiva, God)
- Basic penetration testing capabilities
- Markdown report generation
- Port scanning and service enumeration
- Network reconnaissance features
