#!/usr/bin/env python3
"""
System test wrapper script
Runs comprehensive system tests for all modules
"""

import os
import sys
import subprocess
from pathlib import Path

def run_system_tests():
    """Run system tests"""
    print("🧪 Running system tests...")
    
    try:
        # Change to project directory
        project_root = Path(__file__).parent.parent.parent
        os.chdir(project_root)
        
        # Run system tests
        subprocess.run([
            sys.executable, '-c', 
            'from tests.utils.test_runner import TestRunner; runner = TestRunner(); runner.run_system_tests()'
        ], check=True)
        
        print("✅ System tests completed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ System tests failed: {e}")
        sys.exit(1)

def main():
    """Main function"""
    print("🚀 NOV-RECO Check-in System Test Suite")
    print("=" * 60)
    
    run_system_tests()

if __name__ == '__main__':
    main()