#!/usr/bin/env python3
"""
Setup script for test environment
Installs test dependencies and sets up test data
"""

import os
import sys
import subprocess
from pathlib import Path

def install_test_dependencies():
    """Install test dependencies"""
    print("📦 Installing test dependencies...")
    
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'tests/requirements.txt'
        ], check=True)
        print("✅ Test dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install test dependencies: {e}")
        return False
        
    return True

def setup_test_data():
    """Setup test data"""
    print("🔄 Setting up test data...")
    
    try:
        subprocess.run([
            sys.executable, 'tests/fixtures/test_data_generator.py'
        ], check=True)
        print("✅ Test data setup completed!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to setup test data: {e}")
        return False
        
    return True

def run_initial_tests():
    """Run initial tests to verify setup"""
    print("🧪 Running initial tests...")
    
    try:
        subprocess.run([
            sys.executable, 'tests/utils/test_runner.py'
        ], check=True)
        print("✅ Initial tests passed!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Initial tests failed: {e}")
        return False
        
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up NOV-RECO Check-in System Test Environment")
    print("=" * 60)
    
    # Change to project directory
    project_root = Path(__file__).parent.parent.parent
    os.chdir(project_root)
    
    success = True
    
    # Install dependencies
    if not install_test_dependencies():
        success = False
        
    # Setup test data
    if success and not setup_test_data():
        success = False
        
    # Run initial tests
    if success and not run_initial_tests():
        success = False
        
    print("\n" + "=" * 60)
    if success:
        print("🎉 Test environment setup completed successfully!")
        print("\n📋 Available commands:")
        print("   python test.py setup    - Setup test environment")
        print("   python test.py run      - Run all tests")
        print("   python test.py module <name> - Run module tests")
        print("   python test.py watch    - Watch for changes")
        print("   python test.py data     - Manage test data")
        print("   python test.py status   - Show test system status")
    else:
        print("❌ Test environment setup failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()