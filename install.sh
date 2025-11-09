#!/bin/bash

echo "Installing WebTopo - Website Topology Analyzer"

# Check if Python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is required but not installed. Please install Python3 first."
    exit 1
fi

# Check if pip3 is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is required but not installed. Please install pip3 first."
    exit 1
fi

# Install required Python packages
echo "Installing required Python packages..."
pip3 install requests beautifulsoup4 lxml

# Create the webtopo script in /usr/local/bin
echo "Installing webtopo command..."
sudo tee /usr/local/bin/webtopo > /dev/null << 'EOF'
#!/usr/bin/env python3
import sys
import os

# Add the directory containing webtopo.py to Python path
sys.path.insert(0, '/usr/local/lib/webtopo')

from webtopo import main

if __name__ == "__main__":
    main()
EOF

# Create directory for the module
sudo mkdir -p /usr/local/lib/webtopo

# Copy the main module
sudo cp webtopo.py /usr/local/lib/webtopo/
sudo cp webtopo.py /usr/local/lib/webtopo/__init__.py

# Make the command executable
sudo chmod +x /usr/local/bin/webtopo

echo "Installation completed successfully!"
echo "You can now use 'webtopo' command from anywhere in the terminal."
echo ""
echo "Usage examples:"
echo "  webtopo https://example.com"
echo "  webtopo https://example.com --depth 3 --output report.txt"
echo "  webtopo https://example.com --report-only"
