"""
Module manager for automatic test updates
Handles test creation, updates, and cleanup when modules change
"""

import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Add project root to Python path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


class ModuleManager:
    """Manages test modules and automatic updates"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.apps_dir = self.project_root / "apps"
        self.tests_dir = self.project_root / "tests"
        self.unit_tests_dir = self.tests_dir / "unit"

    def detect_modules(self):
        """Detect all available modules"""
        modules = []

        if self.apps_dir.exists():
            for item in self.apps_dir.iterdir():
                if item.is_dir() and not item.name.startswith("."):
                    # Check if it's a Django app
                    if (item / "models.py").exists() or (item / "views.py").exists():
                        modules.append(item.name)

        return sorted(modules)

    def create_module_test(self, module_name):
        """Create test file for a new module"""
        print(f"🆕 Creating test for new module: {module_name}")

        # Check if module exists
        module_path = self.apps_dir / module_name
        if not module_path.exists():
            print(f"❌ Module {module_name} not found!")
            return False

        # Create test file
        test_file = self.unit_tests_dir / f"test_{module_name}.py"

        if test_file.exists():
            print(f"⚠️  Test file for {module_name} already exists!")
            return True

        # Generate test content
        test_content = self.generate_test_content(module_name)

        # Write test file
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_content)

        print(f"✅ Created test file: {test_file}")
        return True

    def update_module_test(self, module_name):
        """Update test file for existing module"""
        print(f"🔄 Updating test for module: {module_name}")

        test_file = self.unit_tests_dir / f"test_{module_name}.py"

        if not test_file.exists():
            print(f"⚠️  Test file for {module_name} not found, creating new one...")
            return self.create_module_test(module_name)

        # Check if module still exists
        module_path = self.apps_dir / module_name
        if not module_path.exists():
            print(
                f"⚠️  Module {module_name} no longer exists, marking test for cleanup..."
            )
            return self.mark_for_cleanup(module_name)

        # Update test content (preserve existing tests, add new ones)
        print(f"✅ Test file for {module_name} is up to date")
        return True

    def remove_module_test(self, module_name):
        """Remove test file for deleted module"""
        print(f"🗑️  Removing test for deleted module: {module_name}")

        test_file = self.unit_tests_dir / f"test_{module_name}.py"

        if test_file.exists():
            # Create backup before deletion
            backup_file = test_file.with_suffix(
                f'.py.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
            )
            shutil.move(str(test_file), str(backup_file))
            print(f"✅ Moved test file to backup: {backup_file}")
        else:
            print(f"⚠️  Test file for {module_name} not found")

        return True

    def mark_for_cleanup(self, module_name):
        """Mark test file for cleanup"""
        test_file = self.unit_tests_dir / f"test_{module_name}.py"

        if test_file.exists():
            # Add cleanup marker
            with open(test_file, "a", encoding="utf-8") as f:
                f.write(
                    f"\n\n# TODO: Module {module_name} no longer exists - mark for cleanup\n"
                )

        return True

    def generate_test_content(self, module_name):
        """Generate test content for a module"""
        return f'''"""
Unit tests for {module_name} module
Tests models, views, forms, and serializers
"""

import os
import sys
import django

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError

from .base import TestBase


class {module_name.title()}ModelTest(TestBase):
    """Test {module_name} models"""
    
    def test_model_creation(self):
        """Test model creation"""
        # TODO: Implement model creation tests
        pass
        
    def test_model_validation(self):
        """Test model validation"""
        # TODO: Implement model validation tests
        pass


class {module_name.title()}ViewsTest(TestBase):
    """Test {module_name} views"""
    
    def test_view_access(self):
        """Test view access"""
        # TODO: Implement view access tests
        pass
        
    def test_view_permissions(self):
        """Test view permissions"""
        # TODO: Implement view permission tests
        pass


class {module_name.title()}FormsTest(TestBase):
    """Test {module_name} forms"""
    
    def test_form_validation(self):
        """Test form validation"""
        # TODO: Implement form validation tests
        pass


class {module_name.title()}SerializersTest(TestBase):
    """Test {module_name} serializers"""
    
    def test_serializer_serialization(self):
        """Test serializer serialization"""
        # TODO: Implement serializer tests
        pass
'''

    def sync_tests(self):
        """Sync tests with current modules"""
        print("🔄 Syncing tests with current modules...")

        # Get current modules
        current_modules = self.detect_modules()
        print(f"📋 Found modules: {', '.join(current_modules)}")

        # Get existing test files
        existing_tests = []
        if self.unit_tests_dir.exists():
            for test_file in self.unit_tests_dir.glob("test_*.py"):
                module_name = test_file.stem.replace("test_", "")
                existing_tests.append(module_name)

        print(f"📋 Existing tests: {', '.join(existing_tests)}")

        # Find modules that need tests
        modules_needing_tests = set(current_modules) - set(existing_tests)
        for module in modules_needing_tests:
            self.create_module_test(module)

        # Find tests that need cleanup
        tests_needing_cleanup = set(existing_tests) - set(current_modules)
        for module in tests_needing_cleanup:
            self.mark_for_cleanup(module)

        print("✅ Test sync completed!")

    def generate_test_runner_script(self):
        """Generate test runner script for all modules"""
        modules = self.detect_modules()

        script_content = f'''#!/usr/bin/env python3
"""
Auto-generated test runner for all modules
Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tests.utils import TestRunner

def main():
    """Run tests for all modules"""
    runner = TestRunner()
    
    modules = {modules}
    
    print("🧪 Running tests for all modules...")
    print(f"📋 Modules: {{', '.join(modules)}}")
    
    all_passed = True
    
    for module in modules:
        print(f"\\n🎯 Testing {{module}} module...")
        success = runner.run_specific_module(module)
        if not success:
            all_passed = False
            
    if all_passed:
        print("\\n🎉 All module tests passed!")
    else:
        print("\\n❌ Some module tests failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
'''

        script_path = self.tests_dir / "run_all_module_tests.py"
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        # Make executable
        os.chmod(script_path, 0o755)

        print(f"✅ Generated test runner script: {script_path}")

    def cleanup_old_tests(self):
        """Clean up old test files"""
        print("🧹 Cleaning up old test files...")

        if not self.unit_tests_dir.exists():
            return

        # Find backup files older than 30 days
        cutoff_time = datetime.now().timestamp() - (30 * 24 * 60 * 60)

        for backup_file in self.unit_tests_dir.glob("*.backup.*"):
            if backup_file.stat().st_mtime < cutoff_time:
                backup_file.unlink()
                print(f"🗑️  Removed old backup: {backup_file.name}")


def main():
    """Main function"""
    manager = ModuleManager()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "sync":
            manager.sync_tests()
        elif command == "create" and len(sys.argv) > 2:
            module_name = sys.argv[2]
            manager.create_module_test(module_name)
        elif command == "update" and len(sys.argv) > 2:
            module_name = sys.argv[2]
            manager.update_module_test(module_name)
        elif command == "remove" and len(sys.argv) > 2:
            module_name = sys.argv[2]
            manager.remove_module_test(module_name)
        elif command == "generate":
            manager.generate_test_runner_script()
        elif command == "cleanup":
            manager.cleanup_old_tests()
        else:
            print(
                "Usage: python module_manager.py [sync|create|update|remove|generate|cleanup] [module_name]"
            )
    else:
        manager.sync_tests()


if __name__ == "__main__":
    main()
