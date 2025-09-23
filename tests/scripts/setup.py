#!/usr/bin/env python3
"""
NOV-RECO Test Environment Setup
Setup test environment and install dependencies
"""

import os
import sys
import subprocess
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def install_dependencies():
    """Install test dependencies"""
    print("📦 Installing test dependencies...")
    
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'tests/requirements.txt'
        ], check=True, cwd=project_root)
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
            sys.executable, 'tests/scripts/generate_data.py'
        ], check=True, cwd=project_root)
        print("✅ Test data setup completed!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to setup test data: {e}")
        return False
        
    return True

def main():
    """Main function"""
    print("🔧 NOV-RECO Test Environment Setup")
    print("=" * 40)
    
    success = True
    
    # Install dependencies
    if not install_dependencies():
        success = False
        
    # Setup test data
    if success and not setup_test_data():
        success = False
        
    print("\n" + "=" * 40)
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
