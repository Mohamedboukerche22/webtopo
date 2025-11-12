# WebTopo 

<img width="741" height="314" alt="image" src="https://github.com/user-attachments/assets/af90b6d9-e89b-49b9-8ccb-fbdd10f4471b" />



## What is WebTopo?

WebTopo is a command-line tool that maps website structure and identifies security-related endpoints. It creates a visual tree of any website and highlights admin panels, API endpoints, and sensitive files.

## Quick Start

### Installation

```bash
git clone https://github.com/Mohamedboukerche22/webtopo && cd webtopo
chmod +x install.sh
sudo ./install.sh
```
## Basic Usage
```bash
# Scan a website
webtopo https://example.com

# Scan with more depth
webtopo https://example.com --depth 3

# Save results to file
webtopo https://example.com --output report.txt

# Only show security findings
webtopo https://example.com --report-only

```
## Command Options
Option	Description	Default:

`url`=>Website to scan (required)	-

`--depth`=>How deep to crawl =>(1-5 recommended)	2

`--delay`=>Seconds between requests =>1

`--output`=>Save results to file	-

`--report-only`=>Show only security findings=>false

Understanding the Output
Tree Symbols:

`[ROOT]` - Starting point

`[ADMIN]` - Admin panel or backend

`[AUTH]` - Login or authentication page

`[API]` - API endpoint

`[CONFIG]` - Configuration file

`[BACKUP]` - Backup file

`[DB]` - Database file

`[RES]` - Resource directory

Risk Indicators:

`[!]` - Medium risk

`[!!]` - High risk

`[!!!]` - Critical risk

## Examples
### Example 1: Basic Scan
```bash
webtopo https://testsite.com
```
Shows the website tree with security classifications.

### Example 2: Deep Scan with Report
```bash
webtopo https://testsite.com --depth 3 --output security_scan.txt
```
Crawls 3 levels deep and saves everything to a file.

### Example 3: Quick Security Check
```bash
webtopo https://testsite.com --report-only
```
Only displays the security findings without the full tree.

## What WebTopo Finds

Admin Panels: `/admin`, `/wp-admin`, `/dashboard`

Login Pages: `/login`, `/signin`, `/auth`

API Endpoints: `/api/`, `/rest/`, `/graphql`

Config Files: `.env`, `config.php`, `.yml`

Backup Files: `.bak`, `.backup`, `.old`

Database Files: `.sql`, `.db`, `.mdb`

## Legal Notice
FOR EDUCATIONAL USE ONLY

Only scan websites you own or have permission to test

Respect robots.txt and terms of service

Follow responsible disclosure practices

Misuse may violate laws and policies

## Troubleshooting
### Common Issues
"Command not found" after installation:

Try running: source ~/.bashrc or reopen your terminal

### SSL errors:

The tool uses secure connections by default

### Connection timeouts:

Increase delay with --delay 2

Check your internet connection

### Website blocks requests:

Some sites block automated tools

Respect the site's terms of service

### Need Help?
Run `webtopo` without arguments to see usage instructions.

## File Structure
`webtopo.py` - Main program

`install.sh` - Installation script

`requirements.txt` - Python dependencies
