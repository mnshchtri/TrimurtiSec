# Trimurti Penetration Testing Framework

![TrimurtiSec Logo](./Images/coverimage.png)

A comprehensive penetration testing framework inspired by the Hindu trinity concept (Brahma, Vishnu, and Shiva), with an additional "God Mode" for complete system control. Trimurti is designed to be a modular, extensible, and powerful tool for ethical hacking and security assessment.

## 🔮 Concept

The framework is divided into four powerful modes, each representing a different phase of penetration testing:

### 1. Brahma Mode (Creation/Reconnaissance)
- **Enhanced Port Scanning**: Comprehensive port scanning with intelligent timeout handling and adaptive scan strategies
- **Multi-Tier Scanning**: Quick, comprehensive, and aggressive scan modes with automatic optimization for external targets
- **Smart Target Detection**: Automatic responsiveness checks and adaptive port selection for external vs internal targets
- **Robust Error Handling**: Graceful timeout management and recovery mechanisms for unreliable network conditions
- Advanced OS detection using multiple techniques
- Detailed service version detection with configurable intensity levels
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

### Basic Commands

1. **Run Command** - Main operation command:
   ```bash
   trimurti run --target example.com --mode brahma
   ```
   
   **Available Modes:**
   - `brahma` - Reconnaissance and discovery
   - `vishnu` - Persistence establishment
   - `shiva` - Exploitation and destruction
   - `god` - Full system control

2. **Enhanced Brahma Mode Examples:**
   ```bash
   # Basic reconnaissance (optimized for external targets)
   trimurti run -t example.com -m brahma
   
   # Quick scan for fast results
   trimurti run -t example.com -m brahma --scan-type quick
   
   # Comprehensive scan with version detection
   trimurti run -t example.com -m brahma --scan-type comprehensive
   
   # Aggressive scan with all features
   trimurti run -t example.com -m brahma --scan-type aggressive
   
   # Custom port range
   trimurti run -t example.com -m brahma --ports "80,443,8080,8443"
   
   # Extended timeout for slow networks
   trimurti run -t example.com -m brahma --timeout 900
   
   # With subdomain discovery
   trimurti run -t example.com -m brahma --subdomain
   
   # With vulnerability scanning
   trimurti run -t example.com -m brahma --vulnerability-scan
   
   # With legacy subdomain discovery flag
   trimurti run -t example.com -m brahma --subdomain-discovery
   ```

3. **Other Mode Examples:**
   ```bash
   # Vishnu mode (persistence)
   trimurti run -t 192.168.1.100 -m vishnu --method cron
   
   # Shiva mode (exploitation)
   trimurti run -t target.com -m shiva --exploit sql
   
   # God mode (full control)
   trimurti run -t 10.0.0.1 -m god --action pivot
   ```

4. **Standalone Subdomain Discovery:**
   ```bash
   trimurti discover_subdomains --target example.com
   ```

### Command Options
- `-t, --target`: Target IP address or domain (required)
- `-m, --mode`: Operation mode [brahma|vishnu|shiva|god] (required)
- `-o, --output`: Custom output file path (default: report.md)
- `--scan-type`: Scan intensity [quick|comprehensive|aggressive] (Brahma mode only)
- `--ports`: Custom port range or comma-separated ports (Brahma mode only)
- `--timeout`: Scan timeout in seconds (default: 600)
- `-s, --subdomain-discovery`: Perform subdomain discovery (Brahma mode only)
- `--vulnerability-scan`: Perform vulnerability scanning (Brahma mode only)
- `--trivy-path`: Path to directory or container image for Trivy scan (optional, for vulnerability/misconfiguration scanning of filesystems or containers)
- `--shodan-api-key`: Shodan API key for public exposure checks (optional, for checking if your target IP is exposed on Shodan)
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

## 🛠️ Enhanced Port Scanning Features

### Scan Types

1. **Quick Scan** (Default for External Targets):
   - Fast TCP connect scan
   - Common ports only for external targets
   - Conservative timeout settings
   - Ideal for initial reconnaissance

2. **Comprehensive Scan**:
   - Full service version detection
   - Extended port ranges
   - Balanced speed and accuracy
   - Recommended for internal networks

3. **Aggressive Scan**:
   - Full service and script scanning
   - Maximum detection capabilities
   - Longer scan times
   - Use with caution on external targets

### Timeout Management

The enhanced port scanner includes intelligent timeout handling:

- **Adaptive Timeouts**: Automatically adjusts based on target responsiveness
- **Host-Level Timeouts**: Prevents hanging on unresponsive hosts
- **Graceful Degradation**: Continues operation even if some scans timeout
- **Configurable Limits**: Adjustable timeout values for different network conditions

### Target Optimization

- **External Target Detection**: Automatically optimizes settings for internet-facing targets
- **Port Range Selection**: Intelligent port range selection based on target type
- **Responsiveness Checks**: Pre-scan validation to ensure target accessibility
- **Network Condition Adaptation**: Adjusts scan parameters based on network latency

### Error Recovery

- **Timeout Recovery**: Graceful handling of network timeouts
- **Partial Results**: Returns available data even if scan is incomplete
- **Retry Logic**: Intelligent retry mechanisms for transient failures
- **Diagnostic Information**: Detailed error reporting and troubleshooting recommendations

## 📊 Reports

The framework generates detailed markdown reports for each operation. Reports include:

1. Executive Summary
2. Mode-specific results:
   - **Brahma**: Enhanced port scan results with scan statistics, OS detection, service versions, subdomain discovery, and troubleshooting recommendations
   - Vishnu: Persistence mechanisms established
   - Shiva: Exploitation results and system compromise details
   - God Mode: Complete system control and data exfiltration details

### Enhanced Brahma Report Structure:
```markdown
# Trimurti Penetration Test Report
Generated on: [Timestamp]

## Executive Summary
[Summary of operations]

## Port Scan Results
Target: example.com (1.2.3.4)

### Open Ports
| Port | Service | Version | State |
|------|---------|---------|-------|
| 80   | http    | nginx 1.18.0 | open |
| 443  | https   | nginx 1.18.0 | open |

### Scan Statistics
- Scan Type: comprehensive
- Port Range: 80,443,8080,8443
- Target IP: 1.2.3.4
- Scan Duration: 45 seconds
- Timeout Setting: 600s
- Status: ✅ Completed Successfully

### Recommendations
[Included when issues are encountered]
- Try using 'quick' scan type for faster results
- Use smaller port ranges for external targets
- Consider increasing timeout for slow networks
```

## 🛠️ Features

### Enhanced Brahma Mode Features
- **Intelligent TCP Port Scanning**: Adaptive port range selection (1-1000 for internal, common ports for external)
- **Multi-Tier Scan Types**: Quick, comprehensive, and aggressive scanning modes
- **Robust Timeout Management**: Configurable timeouts with graceful degradation
- **Target Responsiveness Checking**: Pre-scan validation and optimization
- **Enhanced Error Handling**: Comprehensive error recovery and reporting
- Service version detection with configurable intensity
- OS fingerprinting with multiple techniques
- Subdomain discovery and enumeration
  - Brute force common subdomains
  - Certificate transparency log checking
  - DNS zone transfer attempts
  - HTTP/HTTPS status verification
- Advanced progress tracking with real-time updates
- Detailed diagnostic information and recommendations

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
    │   └── port_scanner.py (Enhanced with timeout management)
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
        ├── report_gen.py
        └── enhanced_progress.py
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

## 🚀 Getting Started

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Install Trimurti
pip install -e .

# Run a basic scan (optimized for external targets)
trimurti run -t example.com -m brahma
```

### Advanced Usage

```bash
# Quick scan for fast results
trimurti run -t example.com -m brahma --scan-type quick

# Comprehensive scan with extended timeout
trimurti run -t example.com -m brahma \
    --scan-type comprehensive \
    --timeout 900 \
    --verbose

# Custom port range with subdomain discovery
trimurti run -t example.com -m brahma \
    --ports "21,22,23,25,53,80,110,143,443,993,995,8080,8443" \
    --subdomain-discovery \
    --verbose \
    -o detailed_report.md

# Aggressive scan for internal networks
trimurti run -t 192.168.1.100 -m brahma \
    --scan-type aggressive \
    --ports "1-1000" \
    --verbose

# Persistence with specific method
trimurti run -t 192.168.1.100 -m vishnu \
    --method cron \
    --verbose

# Exploitation with specific vector
trimurti run -t target.com -m shiva \
    --exploit sql \
    --verbose
```

## 🔧 Troubleshooting

### Common Issues and Solutions

1. **Timeout Errors**:
   ```bash
   # Use quick scan for faster results
   trimurti run -t example.com -m brahma --scan-type quick
   
   # Increase timeout for slow networks
   trimurti run -t example.com -m brahma --timeout 900
   
   # Use smaller port ranges
   trimurti run -t example.com -m brahma --ports "80,443,8080"
   ```

2. **External Target Issues**:
   - Framework automatically optimizes for external targets
   - Uses common ports instead of full range
   - Implements conservative timeout settings
   - Provides detailed error reporting and recommendations

3. **Network Connectivity**:
   - Pre-scan responsiveness checks
   - Graceful handling of network failures
   - Detailed diagnostic information in reports

## 📚 Documentation

For detailed documentation, visit our [official documentation](https://trimurti-pentest.readthedocs.io).

## 🔍 Advanced Vulnerability Scanning: Trivy & Shodan Integration

Trimurti now supports advanced scanning with [Trivy](https://github.com/aquasecurity/trivy) and [Shodan](https://www.shodan.io/):

### Trivy (Filesystem/Container Vulnerability & Misconfiguration Scanner)
- Use `--trivy-path` to specify a directory or container image to scan for vulnerabilities and misconfigurations.
- Example (scan a Docker image):
  ```bash
  trimurti run -t example.com -m brahma --vulnerability-scan --trivy-path nginx:latest
  ```
- Example (scan a local directory):
  ```bash
  trimurti run -t example.com -m brahma --vulnerability-scan --trivy-path /var/www/html
  ```

### Shodan (Public Exposure Check)
- Use `--shodan-api-key` to provide your Shodan API key. Trimurti will check if your target IP is exposed on Shodan and report open ports, vulnerabilities, and public data.
- Example:
  ```bash
  trimurti run -t 1.2.3.4 -m brahma --vulnerability-scan --shodan-api-key YOUR_SHODAN_API_KEY
  ```
- Only IP addresses are checked with Shodan (not domains).

**Note:** You must have Trivy and Shodan CLI installed and accessible in your PATH. For Shodan, you need a valid API key (get one at https://account.shodan.io/).

These integrations help you:
- Find vulnerabilities and misconfigurations in web roots, containers, or filesystems (Trivy)
- Check if your target is exposed to the public internet and what information is available (Shodan)

## 📊 Performance Considerations

1. **Adaptive Scanning**: Framework automatically adjusts scan parameters based on target type
2. **Intelligent Timeouts**: Configurable timeout management with graceful degradation
3. **Resource Optimization**: Efficient resource usage with progress tracking
4. **Error Recovery**: Robust error handling and retry mechanisms
5. **Network Awareness**: Automatic optimization for different network conditions

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
8. Use conservative settings for external targets

## 🔄 Version History

- **1.2.0**: Enhanced Port Scanner with Intelligent Timeout Management
  - Adaptive scan types (quick, comprehensive, aggressive)
  - Robust timeout handling and error recovery
  - Target responsiveness checks and optimization
  - Enhanced progress tracking and reporting
  - Automatic external target optimization
  - Improved diagnostic information and recommendations
- 1.1.0: Added subdomain discovery functionality
  - Brute force enumeration
  - Certificate transparency log checking
  - DNS zone transfer attempts
  - Dedicated CLI command
- 1.0.0: Initial release
  - Four operational modes
  - Markdown report generation
  - Basic penetration testing capabilities

## 👥 Authors

- n30x (@mnshchtri)

## 🙏 Acknowledgments

- Named after the Hindu trinity: Brahma (Creator), Vishnu (Preserver), and Shiva (Destroyer)
- Inspired by various open-source security tools
- Thanks to all contributors and the security research community

## 📞 Support

For support, please open an issue in the GitHub repository or contact the maintainers directly.

**Common Support Topics:**
- Timeout configuration and troubleshooting
- Scan type selection and optimization
- Network connectivity issues
- External target scanning best practices