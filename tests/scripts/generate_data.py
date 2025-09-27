#!/usr/bin/env python3
"""
Generate data wrapper script
Generates comprehensive test data for all modules
"""

import os
import subprocess
import sys
from pathlib import Path


def generate_data():
    """Generate test data"""
    print("🔄 Generating test data...")

    try:
        # Change to project directory
        project_root = Path(__file__).parent.parent.parent
        os.chdir(project_root)

        # Run data generator
        subprocess.run(
            [sys.executable, "tests/fixtures/test_data_generator.py"], check=True
        )

        print("✅ Test data generated successfully!")

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to generate test data: {e}")
        sys.exit(1)


def main():
    """Main function"""
    print("🚀 NOV-RECO Check-in System Data Generator")
    print("=" * 60)

    generate_data()


if __name__ == "__main__":
    main()
