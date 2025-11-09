import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from collections import deque
import argparse
import re
import sys
#import everything  lol

class WebTopo:
    def __init__(self, max_depth=2, delay=1):
        self.max_depth = max_depth
        self.delay = delay
        self.visited = set()
        self.tree = {}
        #self.admin_patterns=[r'/admin',r'/.env'] -- > old one you could add more with worldlist txt file and read it 
        self.admin_patterns = [
            r'/admin', r'/administrator', r'/backend', r'/manager', r'/cp', r'/controlpanel',
            r'/dashboard', r'/console', r'/webadmin', r'/system', r'/admincp', r'/moderator',
            r'/wp-admin', r'/wp-login', r'/phpmyadmin', r'/mysql', r'/pma', r'/myadmin',
            r'/cpanel', r'/whm', r'/plesk', r'/webmail', r'/rc', r'/roundcube',
            r'/user/login', r'/admin/login', r'/administrator/login', r'/signin',
            r'/login', r'/signin', r'/auth', r'/authenticate',
            r'/api/', r'/graphql', r'/rest/', r'/v1/', r'/v2/', r'/oauth/',
            r'\.env', r'/config\.', r'/settings\.', r'/configuration',
            r'\.bak$', r'\.backup$', r'\.old$', r'\.save$',
            r'\.log$', r'/logs/', r'/debug/',
            r'\.sql$', r'\.db$', r'\.mdb$',
        ]
        
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.admin_patterns]

    def is_valid_url(self, url, base_domain):
        parsed_url = urlparse(url)
        return parsed_url.netloc == base_domain or not parsed_url.netloc
    
    def classify_url(self, url):
        classification = {
            'type': 'normal',
            'risk_level': 'low',
            'tags': []
        }
        
        url_lower = url.lower()
        path = urlparse(url).path
        
        for pattern in self.compiled_patterns:
            if pattern.search(url):
                classification['type'] = 'admin'
                classification['risk_level'] = 'high'
                classification['tags'].append('admin-panel')
                break
        
        login_indicators = ['login', 'signin', 'auth', 'authenticate', 'log-in']
        if any(indicator in url_lower for indicator in login_indicators):
            classification['type'] = 'authentication'
            classification['risk_level'] = 'medium'
            classification['tags'].append('auth')
        
        if '/api/' in url_lower or '/graphql' in url_lower or '/rest/' in url_lower:
            classification['type'] = 'api'
            classification['risk_level'] = 'medium'
            classification['tags'].append('api')
        
        config_extensions = ['.env', '.config', '.ini', '.conf', '.yml', '.yaml', '.xml']
        if any(url_lower.endswith(ext) for ext in config_extensions):
            classification['type'] = 'configuration'
            classification['risk_level'] = 'high'
            classification['tags'].append('config')
        
        backup_extensions = ['.bak', '.backup', '.old', '.save', '.tmp']
        if any(url_lower.endswith(ext) for ext in backup_extensions):
            classification['type'] = 'backup'
            classification['risk_level'] = 'high'
            classification['tags'].append('backup')
        
        db_extensions = ['.sql', '.db', '.mdb', '.sqlite', '.dbf']
        if any(url_lower.endswith(ext) for ext in db_extensions):
            classification['type'] = 'database'
            classification['risk_level'] = 'critical'
            classification['tags'].append('database')
        
        upload_indicators = ['/upload', '/uploads', '/files', '/assets', '/images']
        if any(indicator in path for indicator in upload_indicators):
            classification['type'] = 'resource'
            classification['risk_level'] = 'medium'
            classification['tags'].append('upload')
        
        return classification

    def get_links(self, url, base_domain):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = []
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                
                if (full_url.startswith('http') and 
                    self.is_valid_url(full_url, base_domain) and
                    '#' not in full_url and
                    'mailto:' not in full_url):
                    
                    classification = self.classify_url(full_url)
                    link_data = {
                        'url': full_url,
                        'classification': classification,
                        'text': link.get_text(strip=True)[:50]
                    }
                    links.append(link_data)
            
            return links
            
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return []

    def build_tree(self, start_url):
        parsed_start = urlparse(start_url)
        base_domain = parsed_start.netloc
        
        start_classification = self.classify_url(start_url)
        queue = deque([(start_url, 0, start_classification)])
        self.visited.add(start_url)
        self.tree = {start_url: {'classification': start_classification, 'children': []}}
        
        while queue:
            current_url, depth, current_class = queue.popleft()
            
            if depth >= self.max_depth:
                continue
            
            print(f"Crawling: {current_url} (depth: {depth}) - {current_class['type']}")
            
            links = self.get_links(current_url, base_domain)
            self.tree[current_url]['children'] = links
            
            for link_data in links:
                link_url = link_data['url']
                if link_url not in self.visited:
                    self.visited.add(link_url)
                    self.tree[link_url] = {
                        'classification': link_data['classification'],
                        'children': []
                    }
                    queue.append((link_url, depth + 1, link_data['classification']))
            
            time.sleep(self.delay)
        
        return self.tree

    def print_tree(self, node=None, prefix="", is_last=True, depth=0, max_print_depth=3):
        if depth > max_print_depth:
            return
            
        if node is None:
            node = list(self.tree.keys())[0]
        
        node_data = self.tree[node]
        classification = node_data['classification']
        
        if depth == 0:
            connector = "[ROOT] "
        else:
            connector = "└── " if is_last else "├── "
        
        page_name = self.get_page_name(node)
        type_symbol = {
            'admin': '[ADMIN]',
            'authentication': '[AUTH]',
            'api': '[API]',
            'configuration': '[CONFIG]',
            'backup': '[BACKUP]',
            'database': '[DB]',
            'resource': '[RES]',
            'normal': '[PAGE]'
        }.get(classification['type'], '[PAGE]')
        
        risk_symbol = {
            'low': '',
            'medium': '[!]',
            'high': '[!!]',
            'critical': '[!!!]'
        }.get(classification['risk_level'], '')
        
        print(f"{prefix}{connector}{type_symbol} {risk_symbol} {page_name}")
        print(f"{prefix}    └─ {node}")
        
        if depth > 0:
            new_prefix = prefix + ("    " if is_last else "│   ")
        else:
            new_prefix = ""
        
        if 'children' in node_data and depth < max_print_depth:
            children = node_data['children']
            for i, child_data in enumerate(children):
                child_url = child_data['url']
                if child_url in self.tree:
                    is_last_child = (i == len(children) - 1)
                    self.print_tree(child_url, new_prefix, is_last_child, depth + 1, max_print_depth)

    def get_page_name(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.find('title')
            return title.text.strip()[:60] if title else urlparse(url).path or url
        except:
            return urlparse(url).path or url

    def generate_security_report(self):
        report = {
            'admin_panels': [],
            'auth_pages': [],
            'api_endpoints': [],
            'config_files': [],
            'backup_files': [],
            'database_files': [],
            'sensitive_urls': []
        }
        
        for url, data in self.tree.items():
            classification = data['classification']
            
            if classification['type'] == 'admin':
                report['admin_panels'].append(url)
            elif classification['type'] == 'authentication':
                report['auth_pages'].append(url)
            elif classification['type'] == 'api':
                report['api_endpoints'].append(url)
            elif classification['type'] == 'configuration':
                report['config_files'].append(url)
            elif classification['type'] == 'backup':
                report['backup_files'].append(url)
            elif classification['type'] == 'database':
                report['database_files'].append(url)
            elif classification['risk_level'] in ['high', 'critical']:
                report['sensitive_urls'].append(url)
        
        return report

    def print_security_report(self):
        report = self.generate_security_report()
        
        print("\n" + "="*70)
        print("SECURITY ASSESSMENT REPORT - Educational Purposes Only")
        print("="*70)
        
        sections = [
            ("Admin Panels Found", report['admin_panels']),
            ("Authentication Pages", report['auth_pages']),
            ("API Endpoints", report['api_endpoints']),
            ("Configuration Files", report['config_files']),
            ("Backup Files", report['backup_files']),
            ("Database Files", report['database_files']),
            ("Other Sensitive URLs", report['sensitive_urls'])
        ]
        
        for title, items in sections:
            if items:
                print(f"\n{title}: {len(items)}")
                for item in items:
                    print(f"  - {item}")

    def save_tree_to_file(self, filename="webtopo_report.txt"):
        with open(filename, 'w', encoding='utf-8') as f:
            import sys
            original_stdout = sys.stdout
            sys.stdout = f
            
            print("WebTopo - Website Topology Analysis Report")
            print("=" * 70)
            self.print_tree()
            self.print_security_report()
            
            sys.stdout = original_stdout
        
        print(f"Report saved to {filename}")

def main():
    parser = argparse.ArgumentParser(description='Generate security-focused website topology map')
    parser.add_argument('url', help='Starting URL for the topology map')
    parser.add_argument('--depth', type=int, default=2, help='Maximum crawl depth')
    parser.add_argument('--delay', type=float, default=1, help='Delay between requests')
    parser.add_argument('--output', help='Output file to save the report')
    parser.add_argument('--report-only', action='store_true', help='Only generate security report')
    
    args = parser.parse_args()
    
    print(f"WebTopo Analysis for: {args.url}")
    print(f"Depth: {args.depth}, Delay: {args.delay}s")
    print("created by https://github.com/Mohamedboukerche22 ")
    print("-" * 70)
    
    analyzer = WebTopo(max_depth=args.depth, delay=args.delay)
    website_tree = analyzer.build_tree(args.url)
    
    if not args.report_only:
        analyzer.print_tree()
    
    analyzer.print_security_report()
    
    if args.output:
        analyzer.save_tree_to_file(args.output)
    
    print(f"\nAnalysis complete! Pages analyzed: {len(analyzer.visited)}")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("WebTopo - Website Topology Analyzer")
        print("Usage: webtopo <url> [--depth 2] [--delay 1] [--output file.txt]")
        print("\nExample:")
        print("webtopo https://example.com --depth 2 --output report.txt")
    else:
        main()
