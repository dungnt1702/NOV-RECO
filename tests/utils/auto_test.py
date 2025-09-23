#!/usr/bin/env python3
"""
Auto-test script that monitors file changes and runs tests
Integrates with module manager for automatic test updates
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from .module_manager import ModuleManager


class AutoTestHandler(FileSystemEventHandler):
    """File system event handler for auto-testing"""
    
    def __init__(self, project_root):
        self.project_root = project_root
        self.module_manager = ModuleManager()
        self.last_run = {}
        self.min_interval = 3  # Minimum 3 seconds between runs
        self.ignored_dirs = {'.git', '__pycache__', 'node_modules', '.pytest_cache', 'venv'}
        self.ignored_files = {'.DS_Store', '*.pyc', '*.pyo', '*.log'}
        
    def should_ignore(self, path):
        """Check if path should be ignored"""
        path_obj = Path(path)
        
        # Check if any parent directory is ignored
        for part in path_obj.parts:
            if part in self.ignored_dirs:
                return True
                
        # Check if file should be ignored
        if path_obj.name in self.ignored_files:
            return True
            
        return False
        
    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory or self.should_ignore(event.src_path):
            return
            
        # Only handle Python files
        if not event.src_path.endswith('.py'):
            return
            
        # Extract module information
        module_name = self.extract_module_name(event.src_path)
        if not module_name:
            return
            
        # Throttle test runs
        current_time = time.time()
        if module_name in self.last_run:
            if current_time - self.last_run[module_name] < self.min_interval:
                return
                
        self.last_run[module_name] = current_time
        
        print(f"\n🔄 File changed: {event.src_path}")
        print(f"🎯 Detected module: {module_name}")
        
        # Update tests if needed
        self.update_tests_if_needed(module_name)
        
        # Run tests
        self.run_module_tests(module_name)
        
    def extract_module_name(self, file_path):
        """Extract module name from file path"""
        path_parts = file_path.split(os.sep)
        
        # Look for 'apps' directory
        if 'apps' in path_parts:
            app_index = path_parts.index('apps')
            if app_index + 1 < len(path_parts):
                return path_parts[app_index + 1]
                
        # Look for 'tests' directory
        if 'tests' in path_parts:
            test_index = path_parts.index('tests')
            if test_index + 2 < len(path_parts):
                return path_parts[test_index + 2]  # tests/unit/module_name
                
        return None
        
    def update_tests_if_needed(self, module_name):
        """Update tests if module structure changed"""
        try:
            # Check if this is a new module or significant change
            if self.is_significant_change(module_name):
                print(f"🔄 Updating tests for {module_name}...")
                self.module_manager.update_module_test(module_name)
        except Exception as e:
            print(f"⚠️  Error updating tests: {e}")
            
    def is_significant_change(self, module_name):
        """Check if change is significant enough to update tests"""
        # For now, always update tests
        # In the future, we could check file modification patterns
        return True
        
    def run_module_tests(self, module_name):
        """Run tests for specific module"""
        try:
            # Change to project directory
            os.chdir(self.project_root)
            
            # Run tests
            cmd = [
                sys.executable, 'run_tests.py', 'module', module_name
            ]
            
            print(f"🧪 Running tests for {module_name}...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minutes timeout
            )
            
            if result.returncode == 0:
                print(f"✅ {module_name} tests passed!")
                self.print_success_summary(module_name, result.stdout)
            else:
                print(f"❌ {module_name} tests failed!")
                self.print_error_summary(module_name, result.stderr)
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {module_name} tests timed out!")
        except Exception as e:
            print(f"💥 Error running {module_name} tests: {e}")
            
    def print_success_summary(self, module_name, output):
        """Print success summary"""
        # Extract test count from output if available
        lines = output.split('\n')
        for line in lines:
            if 'test' in line.lower() and ('passed' in line.lower() or 'failed' in line.lower()):
                print(f"   {line.strip()}")
                
    def print_error_summary(self, module_name, error_output):
        """Print error summary"""
        # Extract relevant error information
        lines = error_output.split('\n')
        error_lines = [line for line in lines if 'error' in line.lower() or 'failed' in line.lower() or 'exception' in line.lower()]
        
        if error_lines:
            print("   Error details:")
            for line in error_lines[:5]:  # Show first 5 error lines
                print(f"   {line.strip()}")
        else:
            print("   No detailed error information available")


def start_auto_test():
    """Start auto-test system"""
    print("🚀 Starting NOV-RECO Auto-Test System")
    print("=" * 50)
    print(f"📁 Watching: {project_root}")
    print("👀 Monitoring: Python files in apps/ and tests/")
    print("🔄 Auto-updating: Tests when modules change")
    print("⏱️  Throttling: 3 seconds between runs")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    # Initialize module manager and sync tests
    module_manager = ModuleManager()
    print("\n🔄 Syncing tests with current modules...")
    module_manager.sync_tests()
    
    # Start file watcher
    event_handler = AutoTestHandler(project_root)
    observer = Observer()
    
    # Watch the entire project directory
    observer.schedule(event_handler, str(project_root), recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping auto-test system...")
        observer.stop()
        
    observer.join()
    print("✅ Auto-test system stopped")


def main():
    """Main function"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'start':
            start_auto_test()
        elif command == 'sync':
            module_manager = ModuleManager()
            module_manager.sync_tests()
        elif command == 'test' and len(sys.argv) > 2:
            module_name = sys.argv[2]
            handler = AutoTestHandler(project_root)
            handler.run_module_tests(module_name)
        else:
            print("Usage: python auto_test.py [start|sync|test <module_name>]")
    else:
        start_auto_test()


if __name__ == '__main__':
    main()
