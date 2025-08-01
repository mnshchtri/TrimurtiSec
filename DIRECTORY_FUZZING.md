# Directory Fuzzing with TrimurtiSec

## Overview

The Directory Fuzzer module in TrimurtiSec performs comprehensive directory enumeration on discovered subdomains. It automatically loads subdomains from previous discovery results and performs multi-threaded directory fuzzing using both Python-based requests and external tools like FFuf and Dirb.

## Features

- **Automatic Subdomain Integration**: Loads subdomains from subdomain discovery results
- **Multi-threaded Fuzzing**: Fast enumeration using Python threading
- **External Tool Integration**: Supports FFuf and Dirb for enhanced discovery
- **Comprehensive Wordlist**: Auto-generates wordlist if none available
- **Progress Tracking**: Real-time progress with Rich console output
- **Report Generation**: PDF and JSON reports with detailed findings
- **AI Analysis Integration**: Automatic AI analysis of results

## Usage

### Basic Directory Fuzzing

```bash
# Run directory fuzzing on discovered subdomains
trimurti run -t example.com -m brahma --dirfuzz
```

### With Custom Wordlist

```python
from trimurti.brahma.directory_fuzzer import DirectoryFuzzer

# Initialize with custom wordlist
fuzzer = DirectoryFuzzer(
    target_domain="example.com",
    wordlist_path="/path/to/custom/wordlist.txt",
    threads=20,
    timeout=5
)

# Run directory fuzzing
results = fuzzer.fuzz_directories()
```

### CLI Options

- `--dirfuzz`: Enable directory fuzzing mode
- `--target` / `-t`: Target domain
- `--mode` / `-m`: Must be 'brahma' for directory fuzzing
- `--output` / `-o`: Output report file (default: report.pdf)

## How It Works

### 1. Subdomain Loading
The fuzzer automatically loads subdomains from:
- `reports/httpx_results.json` (HTTPX discovery results)
- `reports/subfinder_results.txt` (Subfinder results)
- `reports/subdomain_discovery_report.json` (General discovery results)

### 2. Wordlist Management
- Searches for common wordlists in standard locations
- Auto-generates comprehensive wordlist if none found
- Includes common directories, files, and extensions

### 3. Multi-threaded Fuzzing
- Python-based HTTP requests with threading
- Tests both HTTP and HTTPS protocols
- Filters for interesting status codes (200, 301, 302, 403, 401, 500)

### 4. External Tool Integration
- **FFuf**: Fast web fuzzer for additional discovery
- **Dirb**: Traditional directory brute forcer
- Automatic result parsing and integration

### 5. Result Processing
- Deduplication of findings
- Comprehensive statistics
- Detailed reporting with tables

## Output Files

### Generated Reports
- `reports/directory_fuzzing_report_{target}.pdf`: Comprehensive PDF report
- `reports/directory_fuzzing_results.json`: JSON results for integration
- `reports/ffuf_{subdomain}.json`: FFuf results per subdomain
- `reports/dirb_{subdomain}.txt`: Dirb results per subdomain

### Report Contents
- Executive summary with statistics
- Summary by subdomain
- Detailed findings table
- Status code breakdown
- AI analysis results

## Example Output

```
🔍 Initiating Directory Fuzzing on Discovered Subdomains...
[cyan]Loaded 15 subdomains for directory fuzzing[/cyan]
[cyan]Starting directory fuzzing on 15 subdomains...[/cyan]
[cyan]Wordlist: reports/directory_wordlist.txt[/cyan]

[green][200] https://admin.example.com/login (1024 bytes)[/green]
[green][403] https://api.example.com/admin (0 bytes)[/green]
[green][301] https://test.example.com/backup (0 bytes)[/green]

✅ Directory fuzzing completed!
  Target Subdomains: 15
  Total Directories Found: 47
  Subdomains with Findings: 8
  Wordlist Size: 1250
  Status: Directory Fuzzing Complete

[green]Directory fuzzing report saved to: reports/directory_fuzzing_report_example.com.pdf[/green]
[green]JSON results saved to: reports/directory_fuzzing_results.json[/green]
```

## Configuration

### Wordlist Locations
The fuzzer searches for wordlists in this order:
1. `/usr/share/wordlists/dirb/common.txt`
2. `/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt`
3. `/usr/share/wordlists/SecLists/Discovery/Web-Content/common.txt`
4. `wordlist.txt` (local)
5. Auto-generated wordlist in `reports/directory_wordlist.txt`

### Threading Configuration
- Default: 20 threads
- Adjustable via constructor parameter
- Limited to 50 threads for external tools

### Timeout Settings
- Default: 5 seconds per request
- Configurable via constructor parameter
- External tools have separate timeout limits

## Integration with TrimurtiSec

### Workflow Integration
1. Run subdomain discovery: `trimurti run -t example.com -m brahma --subdomain-discovery`
2. Run directory fuzzing: `trimurti run -t example.com -m brahma --dirfuzz`
3. Run vulnerability scanning: `trimurti run -t example.com -m brahma --vulnerability-scan`

### AI Analysis
Results are automatically fed to AI analysis for:
- Pattern recognition in discovered directories
- Security implications assessment
- Recommendations for further investigation

## Troubleshooting

### Common Issues

1. **No subdomains found**
   - Ensure subdomain discovery has been run first
   - Check that subdomain files exist in `reports/` directory

2. **External tools not available**
   - FFuf and Dirb are optional
   - Python-based fuzzing will still work
   - Install tools for enhanced discovery

3. **Timeout issues**
   - Reduce thread count for slower networks
   - Increase timeout values for slower targets
   - Limit subdomain count for large discoveries

### Performance Optimization
- Use smaller wordlists for faster scanning
- Adjust thread count based on target responsiveness
- Consider running on subsets of subdomains for large discoveries

## Security Considerations

- Always obtain proper authorization before testing
- Be mindful of rate limiting and target resources
- Some directories may trigger security alerts
- Use responsibly and ethically

## Dependencies

### Required
- `requests`: HTTP requests
- `rich`: Console output and progress tracking
- `threading`: Multi-threaded operations

### Optional
- `ffuf`: Fast web fuzzer (external tool)
- `dirb`: Directory brute forcer (external tool)
- `fpdf2`: PDF report generation

## Contributing

To enhance the directory fuzzer:
1. Add new wordlist sources
2. Implement additional external tool support
3. Enhance result analysis and reporting
4. Add new detection patterns
5. Improve performance and threading 