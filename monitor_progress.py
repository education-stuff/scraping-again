#!/usr/bin/env python3
"""
Monitor scraping progress by checking the log file
"""

import time
import os

log_file = "math_rescrape.log"

if os.path.exists(log_file):
    # Get last 20 lines
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    print("📋 Last 20 log entries:")
    print("=" * 60)
    for line in lines[-20:]:
        print(line.strip())
else:
    print("Log file not found yet...")
