#!/usr/bin/env python3
"""
Auto test wrapper script
Runs tests automatically when files change
"""

import os
import sys
import subprocess
from pathlib import Path

def run_auto_test():
    """Run auto test with file watcher"""
    print("🔄 Starting auto test with file watcher...")
    
    try:
        # Change to project directory
        project_root = Path(__file__).parent.parent.parent
        os.chdir(project_root)
        
        # Run auto test
        subprocess.run([
            sys.executable, 'tests/utils/auto_test.py'
        ], check=True)
        
    except KeyboardInterrupt:
        print("\n⏹️  Auto test stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Auto test failed: {e}")
        sys.exit(1)

def main():
    """Main function"""
    print("🚀 NOV-RECO Check-in System Auto Test")
    print("=" * 60)
    print("📁 Watching for file changes...")
    print("🔄 Running tests automatically when files change")
    print("⏹️  Press Ctrl+C to stop")
    print("=" * 60)
    
    run_auto_test()

if __name__ == '__main__':
    main()