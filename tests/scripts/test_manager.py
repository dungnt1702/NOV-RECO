#!/usr/bin/env python3
"""
Test manager wrapper script
Manages test execution and reporting
"""

import os
import sys
import subprocess
from pathlib import Path

def run_test_manager():
    """Run test manager"""
    print("🔧 Running test manager...")
    
    try:
        # Change to project directory
        project_root = Path(__file__).parent.parent.parent
        os.chdir(project_root)
        
        # Run test manager
        subprocess.run([
            sys.executable, 'tests/utils/module_manager.py'
        ], check=True)
        
        print("✅ Test manager completed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Test manager failed: {e}")
        sys.exit(1)

def main():
    """Main function"""
    print("🚀 NOV-RECO Check-in System Test Manager")
    print("=" * 60)
    
    run_test_manager()

if __name__ == '__main__':
    main()