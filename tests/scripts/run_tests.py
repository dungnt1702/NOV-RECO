#!/usr/bin/env python3
"""
Run tests wrapper script
Runs all tests or specific module tests
"""

import os
import sys
import subprocess
from pathlib import Path

def run_tests(module=None):
    """Run tests"""
    print("🧪 Running tests...")
    
    try:
        # Change to project directory
        project_root = Path(__file__).parent.parent.parent
        os.chdir(project_root)
        
        if module:
            print(f"📦 Running tests for module: {module}")
            # Run module tests
            subprocess.run([
                sys.executable, '-c', 
                f'from tests.utils.test_runner import TestRunner; runner = TestRunner(); runner.run_module_tests("{module}", "unit")'
            ], check=True)
        else:
            print("📦 Running all tests...")
            # Run all tests
            subprocess.run([
                sys.executable, '-c', 
                'from tests.utils.test_runner import TestRunner; runner = TestRunner(); runner.run_all_tests()'
            ], check=True)
        
        print("✅ Tests completed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed: {e}")
        sys.exit(1)

def main():
    """Main function"""
    print("🚀 NOV-RECO Check-in System Test Runner")
    print("=" * 60)
    
    # Get module argument if provided
    module = sys.argv[1] if len(sys.argv) > 1 else None
    
    run_tests(module)

if __name__ == '__main__':
    main()