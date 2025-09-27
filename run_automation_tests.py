#!/usr/bin/env python3
"""
Command line script to run automation tests
Supports both extended tests and traditional Django tests
"""

import argparse
import os
import sys
from pathlib import Path

import django

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from django.core.management import execute_from_command_line
from django.test import TestCase

from apps.automation_test.test_modules import get_test_modules, run_test_module


def run_extended_tests(test_type="comprehensive", base_url="http://localhost:3000"):
    """Run extended test modules"""
    print(f"🧪 Running {test_type} tests...")
    print("=" * 60)

    try:
        results = run_test_module(test_type, base_url)

        # Print results
        print(f"\n📊 Test Results:")
        print("-" * 40)

        passed = sum(1 for r in results if r["status"] == "passed")
        failed = sum(1 for r in results if r["status"] == "failed")
        total = len(results)

        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {passed/total*100:.1f}%")

        # Print detailed results
        print(f"\n📋 Detailed Results:")
        print("-" * 40)

        for result in results:
            status_icon = "✅" if result["status"] == "passed" else "❌"
            print(f"{status_icon} {result['name']} ({result['module']})")
            if result["status"] == "failed" and "error" in result:
                print(f"   Error: {result['error']}")

        return passed == total

    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def run_django_tests(test_pattern=None):
    """Run traditional Django tests"""
    print("🧪 Running Django tests...")
    print("=" * 60)

    try:
        # Build command
        cmd = ["test"]
        if test_pattern:
            cmd.append(test_pattern)

        # Run tests
        execute_from_command_line(["manage.py"] + cmd)
        return True

    except Exception as e:
        print(f"❌ Error running Django tests: {e}")
        return False


def run_all_tests():
    """Run all available tests"""
    print("🚀 Running All Tests")
    print("=" * 60)

    success = True

    # Run extended tests
    test_types = ["display", "links", "comprehensive"]
    for test_type in test_types:
        print(f"\n🔄 Running {test_type} tests...")
        if not run_extended_tests(test_type):
            success = False

    # Run Django tests
    print(f"\n🔄 Running Django unit tests...")
    if not run_django_tests():
        success = False

    return success


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="NOV-RECO Automation Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_automation_tests.py --type display
  python run_automation_tests.py --type comprehensive
  python run_automation_tests.py --django tests.unit.test_users
  python run_automation_tests.py --all
        """,
    )

    parser.add_argument(
        "--type",
        choices=["display", "links", "comprehensive"],
        help="Type of extended tests to run",
    )

    parser.add_argument(
        "--django",
        help="Run Django tests with specific pattern (e.g., tests.unit.test_users)",
    )

    parser.add_argument(
        "--all", action="store_true", help="Run all tests (extended + Django)"
    )

    parser.add_argument(
        "--url",
        default="http://localhost:3000",
        help="Base URL for testing (default: http://localhost:3000)",
    )

    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    print("🚀 NOV-RECO Automation Test Runner")
    print("=" * 60)
    print(f"🌐 Base URL: {args.url}")
    print(f"📁 Project: {project_root}")
    print("=" * 60)

    success = True

    if args.all:
        success = run_all_tests()
    elif args.type:
        success = run_extended_tests(args.type, args.url)
    elif args.django:
        success = run_django_tests(args.django)
    else:
        # Default: run comprehensive tests
        success = run_extended_tests("comprehensive", args.url)

    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
