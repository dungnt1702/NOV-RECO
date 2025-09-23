"""
File watcher for automatic test execution
Monitors file changes and runs relevant tests
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class TestFileHandler(FileSystemEventHandler):
    """File system event handler for test execution"""
    
    def __init__(self, project_root):
        self.project_root = project_root
        self.last_run = {}
        self.min_interval = 2  # Minimum 2 seconds between runs
        
    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
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
        
        print(f"\n🔄 File changed in {module_name} module: {event.src_path}")
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
                timeout=60  # 1 minute timeout
            )
            
            if result.returncode == 0:
                print(f"✅ {module_name} tests passed!")
            else:
                print(f"❌ {module_name} tests failed!")
                print(f"Error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {module_name} tests timed out!")
        except Exception as e:
            print(f"💥 Error running {module_name} tests: {e}")


def start_watcher():
    """Start file watcher"""
    project_root = Path(__file__).parent.parent.parent
    
    print("👀 Starting file watcher...")
    print(f"📁 Watching: {project_root}")
    print("Press Ctrl+C to stop")
    
    event_handler = TestFileHandler(project_root)
    observer = Observer()
    
    # Watch the entire project directory
    observer.schedule(event_handler, str(project_root), recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping file watcher...")
        observer.stop()
        
    observer.join()
    print("✅ File watcher stopped")


if __name__ == '__main__':
    start_watcher()
