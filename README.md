# Trimurti Penetration Testing Framework

A comprehensive penetration testing framework inspired by the Hindu trinity concept (Brahma, Vishnu, and Shiva), with an additional "God Mode" for complete system control. Trimurti is designed to be a modular, extensible, and powerful tool for ethical hacking and security assessment.

## 🔮 Concept

The framework is divided into four powerful modes, each representing a different phase of penetration testing:

### 1. Brahma Mode (Creation/Reconnaissance)
- Comprehensive port scanning and service enumeration
- Advanced OS detection using multiple techniques
- Detailed service version detection
- Intelligent subdomain discovery and enumeration
- Network mapping with visualization capabilities
- Vulnerability assessment with CVE correlation

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
git clone https://github.com/yourusername/trimurti-pentest.git
cd trimurti-pentest
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

### Basic Commands

1. Brahma Mode (Reconnaissance):
```bash
# Basic reconnaissance
trimurti run -t example.com -m brahma

# With subdomain discovery
trimurti run -t example.com -m brahma --subdomain-discovery

# With custom output file
trimurti run -t example.com -m brahma -o custom_report.md
```

2. Vishnu Mode (Persistence):
```bash
# Basic persistence setup
trimurti run -t 192.168.1.100 -m vishnu

# With specific persistence method
trimurti run -t 192.168.1.100 -m vishnu --method cron
```

3. Shiva Mode (Destruction):
```bash
# Basic exploitation
trimurti run -t target.com -m shiva

# With specific exploit type
trimurti run -t target.com -m shiva --exploit sql
```

4. God Mode (Full Control):
```bash
# Basic full control
trimurti run -t 10.0.0.1 -m god

# With specific control action
trimurti run -t 10.0.0.1 -m god --action pivot
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

## 📊 Reports

The framework generates detailed markdown reports for each operation. Reports include:

1. Executive Summary
2. Mode-specific results:
   - Brahma: Port scan results, OS detection, service versions, subdomain discovery
   - Vishnu: Persistence mechanisms established
   - Shiva: Exploitation results and system compromise details
   - God Mode: Complete system control and data exfiltration details

Example report structure:
```markdown
# Trimurti Penetration Test Report
Generated on: [Timestamp]

## Executive Summary
[Summary of operations]

## [Mode] Results
[Detailed findings and results]
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

## 🔄 Version History

- 1.1.0: Added subdomain discovery functionality
  - Brute force enumeration
  - Certificate transparency log checking
  - DNS zone transfer attempts
  - Dedicated CLI command
- 1.0.0: Initial release
  - Four operational modes
  - Markdown report generation
  - Basic penetration testing capabilities 