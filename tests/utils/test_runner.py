"""
Test runner utility for automated testing
Handles test execution and reporting
"""

import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Add project root to Python path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


class TestRunner:
    """Automated test runner for all modules"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.test_results = {}
        self.start_time = None

    def run_all_tests(self):
        """Run all tests in the test suite"""
        print("🚀 Starting comprehensive test suite...")
        self.start_time = datetime.now()

        # Run different types of tests
        self.run_unit_tests()
        self.run_integration_tests()
        self.run_functional_tests()

        self.print_summary()

    def run_unit_tests(self):
        """Run unit tests for all modules"""
        print("\n📋 Running Unit Tests...")

        modules = ["users", "area", "checkin", "personal", "dashboard"]

        for module in modules:
            print(f"   Testing {module} module...")
            result = self.run_module_tests(module, "unit")
            self.test_results[f"{module}_unit"] = result

    def run_integration_tests(self):
        """Run integration tests"""
        print("\n🔗 Running Integration Tests...")

        result = self.run_module_tests("integration", "integration")
        self.test_results["integration"] = result

    def run_functional_tests(self):
        """Run functional tests"""
        print("\n⚙️ Running Functional Tests...")

        result = self.run_module_tests("functional", "functional")
        self.test_results["functional"] = result

    def run_module_tests(self, module, test_type):
        """Run tests for a specific module"""
        try:
            # Change to project directory
            os.chdir(self.project_root)

            # Run Django test command
            cmd = [
                "python",
                "manage.py",
                "test",
                f"tests.{test_type}.test_{module}",
                "--verbosity=2",
                "--keepdb",
            ]

            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300  # 5 minutes timeout
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration": time.time(),
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": "Test timeout after 5 minutes",
                "duration": time.time(),
            }
        except Exception as e:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "duration": time.time(),
            }

    def run_specific_module(self, module_name):
        """Run tests for a specific module only"""
        print(f"🎯 Running tests for {module_name} module...")

        # Check if module exists
        module_path = self.project_root / "apps" / module_name
        if not module_path.exists():
            print(f"❌ Module {module_name} not found!")
            return False

        # Run tests
        result = self.run_module_tests(module_name, "unit")

        if result["success"]:
            print(f"✅ {module_name} module tests passed!")
        else:
            print(f"❌ {module_name} module tests failed!")
            print(f"Error: {result['stderr']}")

        return result["success"]

    def print_summary(self):
        """Print test summary"""
        if not self.start_time:
            return

        end_time = datetime.now()
        duration = end_time - self.start_time

        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = sum(
            1 for result in self.test_results.values() if result["success"]
        )
        failed_tests = total_tests - passed_tests

        print(f"Total Test Suites: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"Duration: {duration}")

        print("\n📋 Detailed Results:")
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"   {test_name}: {status}")

        print("=" * 60)

    def watch_for_changes(self):
        """Watch for file changes and run tests automatically"""
        print("👀 Watching for file changes...")
        print("Press Ctrl+C to stop")

        try:
            import watchdog
            from watchdog.events import FileSystemEventHandler
            from watchdog.observers import Observer

            class TestHandler(FileSystemEventHandler):
                def __init__(self, runner):
                    self.runner = runner
                    self.last_run = 0

                def on_modified(self, event):
                    if event.is_directory:
                        return

                    # Only run tests for Python files
                    if not event.src_path.endswith(".py"):
                        return

                    # Throttle test runs (max once per 5 seconds)
                    current_time = time.time()
                    if current_time - self.last_run < 5:
                        return

                    self.last_run = current_time

                    # Extract module name from path
                    path_parts = event.src_path.split(os.sep)
                    if "apps" in path_parts:
                        app_index = path_parts.index("apps")
                        if app_index + 1 < len(path_parts):
                            module_name = path_parts[app_index + 1]
                            print(f"\n🔄 File changed in {module_name} module")
                            self.runner.run_specific_module(module_name)

            event_handler = TestHandler(self)
            observer = Observer()
            observer.schedule(event_handler, str(self.project_root), recursive=True)
            observer.start()

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()

            observer.join()

        except ImportError:
            print(
                "❌ watchdog package not installed. Install with: pip install watchdog"
            )
            print("   Falling back to manual test running...")


if __name__ == "__main__":
    runner = TestRunner()

    if len(sys.argv) > 1:
        if sys.argv[1] == "watch":
            runner.watch_for_changes()
        elif sys.argv[1] == "module" and len(sys.argv) > 2:
            runner.run_specific_module(sys.argv[2])
        else:
            print("Usage: python test_runner.py [watch|module <module_name>]")
    else:
        runner.run_all_tests()
