#!/usr/bin/env python3
"""
Development Tools Management Script
Cung cấp các lệnh tiện ích cho development
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def run_command(cmd, description=""):
    """Run a command and print the result"""
    print(f"\n{'='*50}")
    print(f"Running: {description or cmd}")
    print(f"{'='*50}")

    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False


def format_code():
    """Format code using Black and isort"""
    print("🎨 Formatting code...")

    # Format with Black
    success1 = run_command("black .", "Black code formatting")

    # Sort imports with isort
    success2 = run_command("isort .", "Import sorting with isort")

    return success1 and success2


def lint_code():
    """Lint code using flake8"""
    print("🔍 Linting code...")
    return run_command("flake8 .", "Code linting with flake8")


def run_tests():
    """Run tests using pytest"""
    print("🧪 Running tests...")
    return run_command("pytest", "Running tests with pytest")


def run_tests_with_coverage():
    """Run tests with coverage report"""
    print("🧪 Running tests with coverage...")
    return run_command(
        "pytest --cov=apps --cov-report=html --cov-report=term-missing",
        "Running tests with coverage",
    )


def check_code_quality():
    """Run all code quality checks"""
    print("✅ Running code quality checks...")

    success1 = format_code()
    success2 = lint_code()
    success3 = run_tests()

    if success1 and success2 and success3:
        print("\n🎉 All code quality checks passed!")
        return True
    else:
        print("\n❌ Some code quality checks failed!")
        return False


def generate_model_graph():
    """Generate model relationship graph"""
    print("📊 Generating model relationship graph...")
    return run_command(
        "python manage.py graph_models -a -o models.png", "Generating model graph"
    )


def run_django_shell():
    """Run Django shell with extensions"""
    print("🐍 Starting Django shell...")
    return run_command("python manage.py shell_plus", "Django shell with extensions")


def run_django_server():
    """Run Django development server"""
    print("🚀 Starting Django development server...")
    return run_command(
        "python manage.py runserver 0.0.0.0:3000", "Django development server"
    )


def show_help():
    """Show help information"""
    help_text = """
🔧 Django Development Tools

Available commands:
  format          Format code with Black and isort
  lint            Lint code with flake8
  test            Run tests with pytest
  test-cov        Run tests with coverage report
  check           Run all code quality checks
  graph           Generate model relationship graph
  shell           Start Django shell with extensions
  server          Start Django development server
  help            Show this help message

Examples:
  python scripts/dev_tools.py format
  python scripts/dev_tools.py check
  python scripts/dev_tools.py test-cov
  python scripts/dev_tools.py server
"""
    print(help_text)


def main():
    parser = argparse.ArgumentParser(description="Django Development Tools")
    parser.add_argument(
        "command",
        nargs="?",
        default="help",
        choices=[
            "format",
            "lint",
            "test",
            "test-cov",
            "check",
            "graph",
            "shell",
            "server",
            "help",
        ],
        help="Command to run",
    )

    args = parser.parse_args()

    # Change to project root directory
    os.chdir(PROJECT_ROOT)

    # Execute command
    if args.command == "format":
        format_code()
    elif args.command == "lint":
        lint_code()
    elif args.command == "test":
        run_tests()
    elif args.command == "test-cov":
        run_tests_with_coverage()
    elif args.command == "check":
        check_code_quality()
    elif args.command == "graph":
        generate_model_graph()
    elif args.command == "shell":
        run_django_shell()
    elif args.command == "server":
        run_django_server()
    else:
        show_help()


if __name__ == "__main__":
    main()
