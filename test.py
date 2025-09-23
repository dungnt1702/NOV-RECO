#!/usr/bin/env python3
"""
NOV-RECO Check-in System Test Runner
Main entry point for all test activities
"""

import os
import sys
import subprocess
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Main function - redirect to test manager"""
    if len(sys.argv) < 2:
        print("🚀 NOV-RECO Check-in System Test Runner")
        print("=" * 50)
        print("Usage: python test.py <command> [options]")
        print("\nAvailable commands:")
        print("  setup     - Setup test environment")
        print("  run       - Run all tests")
        print("  module    - Run tests for specific module")
        print("  watch     - Watch for file changes and auto-test")
        print("  data      - Manage test data")
        print("  status    - Show test system status")
        print("\nExamples:")
        print("  python test.py setup")
        print("  python test.py run")
        print("  python test.py module users")
        print("  python test.py watch")
        return
    
    # Get command and arguments
    command = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    # Map commands to their respective scripts
    script_map = {
        'setup': 'tests/scripts/setup_tests.py',
        'run': 'tests/scripts/run_tests.py',
        'module': 'tests/scripts/run_tests.py',
        'watch': 'tests/scripts/start_auto_test.py',
        'data': 'tests/scripts/test_data_generator.py',
        'status': 'tests/scripts/test_manager.py'
    }
    
    if command not in script_map:
        print(f"❌ Unknown command: {command}")
        print("Available commands: setup, run, module, watch, data, status")
        sys.exit(1)
    
    # Build command to run the appropriate script
    script_path = project_root / script_map[command]
    cmd = [sys.executable, str(script_path)] + args
    
    try:
        # Run the appropriate script
        result = subprocess.run(cmd, cwd=project_root)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\n🛑 Test execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running test command: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
