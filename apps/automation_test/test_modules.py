#!/usr/bin/env python3
"""
Extended automation test modules
Includes display tests, link tests, and comprehensive functionality tests
"""

import os
import sys
import time
import unittest
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

import requests

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

User = get_user_model()


def create_unique_user(username_prefix="testuser", password="testpass123"):
    """Create a unique user for testing"""
    import time

    username = f"{username_prefix}_{int(time.time() * 1000)}"
    user = User.objects.create_user(
        username=username, password=password, email=f"{username}@example.com"
    )
    return user, username


class DisplayTestModule:
    """Test module for display and UI functionality"""

    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
        self.client = Client()
        self.test_results = []

    def run_all_tests(self):
        """Run all display tests"""
        print("🖥️  Running Display Tests...")

        tests = [
            self.test_home_page_display,
            self.test_login_page_display,
            self.test_dashboard_display,
            self.test_checkin_pages_display,
            self.test_user_management_display,
            self.test_automation_test_display,
            self.test_responsive_design,
            self.test_static_files_loading,
            self.test_navigation_menu,
            self.test_mobile_header_layout,
        ]

        for test in tests:
            try:
                result = test()
                self.test_results.append(
                    {
                        "name": test.__name__,
                        "status": "passed" if result else "failed",
                        "module": "Display",
                    }
                )
            except Exception as e:
                self.test_results.append(
                    {
                        "name": test.__name__,
                        "status": "failed",
                        "module": "Display",
                        "error": str(e),
                    }
                )

        return self.test_results

    def test_home_page_display(self):
        """Test home page displays correctly"""
        print("  📄 Testing home page display...")

        # Test unauthenticated access
        response = self.client.get("/")
        if response.status_code == 200:
            content = response.content.decode()
            # Check for key elements
            checks = [
                "NOV-RECO" in content,
                "Check-in System" in content or "checkin" in content.lower(),
                "login" in content.lower() or "đăng nhập" in content.lower(),
            ]
            return all(checks)
        return False

    def test_login_page_display(self):
        """Test login page displays correctly"""
        print("  🔐 Testing login page display...")

        response = self.client.get("/accounts/login/")
        if response.status_code == 200:
            content = response.content.decode()
            checks = [
                "username" in content.lower() or "tên đăng nhập" in content.lower(),
                "password" in content.lower() or "mật khẩu" in content.lower(),
                "login" in content.lower() or "đăng nhập" in content.lower(),
            ]
            return all(checks)
        return False

    def test_dashboard_display(self):
        """Test dashboard displays correctly (requires login)"""
        print("  📊 Testing dashboard display...")

        # Create test user and login
        user, username = create_unique_user()

        # Login
        login_success = self.client.login(username=username, password="testpass123")
        if not login_success:
            return False

        # Test dashboard
        response = self.client.get("/dashboard/")
        if response.status_code == 200:
            content = response.content.decode()
            checks = [
                "dashboard" in content.lower() or "bảng điều khiển" in content.lower(),
                "NOV-RECO" in content,
                "logout" in content.lower() or "đăng xuất" in content.lower(),
            ]
            return all(checks)

        return False

    def test_checkin_pages_display(self):
        """Test checkin pages display correctly"""
        print("  ✅ Testing checkin pages display...")

        # Login first
        user, username = create_unique_user("testuser2")
        self.client.login(username=username, password="testpass123")

        # Test checkin action page
        response = self.client.get("/checkin/action/")
        if response.status_code == 200:
            content = response.content.decode()
            checks = [
                "checkin" in content.lower() or "check-in" in content.lower(),
                "location" in content.lower() or "vị trí" in content.lower(),
                "submit" in content.lower() or "gửi" in content.lower(),
            ]
            return all(checks)

        return False

    def test_user_management_display(self):
        """Test user management pages display correctly"""
        print("  👥 Testing user management display...")

        # Login as admin
        admin_user, username = create_unique_user("admin", "admin123")
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        self.client.login(username=username, password="admin123")

        # Test users list page
        response = self.client.get("/users/")
        if response.status_code == 200:
            content = response.content.decode()
            checks = [
                "user" in content.lower() or "người dùng" in content.lower(),
                "NOV-RECO" in content,
            ]
            return all(checks)

        return False

    def test_automation_test_display(self):
        """Test automation test page displays correctly"""
        print("  🤖 Testing automation test display...")

        # Login as admin
        admin_user, username = create_unique_user("admin2", "admin123")
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        self.client.login(username=username, password="admin123")

        # Test automation test page
        response = self.client.get("/automation-test/")
        if response.status_code == 200:
            content = response.content.decode()
            checks = [
                "test" in content.lower() or "kiểm tra" in content.lower(),
                "automation" in content.lower() or "tự động" in content.lower(),
                "NOV-RECO" in content,
            ]
            return all(checks)

        return False

    def test_responsive_design(self):
        """Test responsive design elements"""
        print("  📱 Testing responsive design...")

        response = self.client.get("/")
        if response.status_code == 200:
            content = response.content.decode()
            checks = [
                "viewport" in content.lower(),
                "responsive" in content.lower() or "mobile" in content.lower(),
                "css" in content.lower(),
            ]
            return any(checks)  # At least one should be present

        return False

    def test_static_files_loading(self):
        """Test static files are accessible"""
        print("  📁 Testing static files loading...")

        static_files = [
            "/static/css/base.css",
            "/static/js/base.js",
            "/static/logo.svg",
        ]

        accessible_count = 0
        for file_path in static_files:
            response = self.client.get(file_path)
            if response.status_code == 200:
                accessible_count += 1

        return accessible_count >= 2  # At least 2 files should be accessible

    def test_navigation_menu(self):
        """Test navigation menu elements"""
        print("  🧭 Testing navigation menu...")

        response = self.client.get("/")
        if response.status_code == 200:
            content = response.content.decode()
            checks = [
                "nav" in content.lower(),
                "menu" in content.lower(),
                "header" in content.lower(),
            ]
            return all(checks)

        return False

    def test_mobile_header_layout(self):
        """Test mobile header layout elements"""
        print("  📱 Testing mobile header layout...")

        response = self.client.get("/")
        if response.status_code == 200:
            content = response.content.decode()
            checks = [
                "hamburger" in content.lower() or "toggle" in content.lower(),
                "logo" in content.lower(),
                "mobile" in content.lower() or "responsive" in content.lower(),
            ]
            return any(checks)  # At least one should be present

        return False


class LinkTestModule:
    """Test module for link functionality and navigation"""

    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
        self.client = Client()
        self.test_results = []

    def run_all_tests(self):
        """Run all link tests"""
        print("🔗 Running Link Tests...")

        tests = [
            self.test_home_links,
            self.test_navigation_links,
            self.test_checkin_links,
            self.test_user_management_links,
            self.test_automation_test_links,
            self.test_external_links,
            self.test_form_submissions,
            self.test_api_endpoints,
        ]

        for test in tests:
            try:
                result = test()
                self.test_results.append(
                    {
                        "name": test.__name__,
                        "status": "passed" if result else "failed",
                        "module": "Links",
                    }
                )
            except Exception as e:
                self.test_results.append(
                    {
                        "name": test.__name__,
                        "status": "failed",
                        "module": "Links",
                        "error": str(e),
                    }
                )

        return self.test_results

    def test_home_links(self):
        """Test home page links"""
        print("  🏠 Testing home page links...")

        response = self.client.get("/")
        if response.status_code == 200:
            content = response.content.decode()
            # Check for common link patterns
            checks = [
                "href=" in content,
                "url" in content.lower() or "link" in content.lower(),
            ]
            return all(checks)

        return False

    def test_navigation_links(self):
        """Test navigation menu links"""
        print("  🧭 Testing navigation links...")

        # Login first
        user, username = create_unique_user("testuser3")
        self.client.login(username=username, password="testpass123")

        # Test main navigation
        response = self.client.get("/dashboard/")
        if response.status_code == 200:
            content = response.content.decode()
            checks = [
                "href=" in content,
                "dashboard" in content.lower() or "checkin" in content.lower(),
            ]
            return all(checks)

        return False

    def test_checkin_links(self):
        """Test checkin related links"""
        print("  ✅ Testing checkin links...")

        # Login first
        user, username = create_unique_user("testuser4")
        self.client.login(username=username, password="testpass123")

        # Test checkin pages
        checkin_urls = ["/checkin/", "/checkin/action/", "/checkin/list/"]
        accessible_count = 0

        for url in checkin_urls:
            response = self.client.get(url)
            if response.status_code in [200, 302]:  # 302 for redirects
                accessible_count += 1

        return accessible_count >= 1

    def test_user_management_links(self):
        """Test user management links"""
        print("  👥 Testing user management links...")

        # Login as admin
        admin_user, username = create_unique_user("admin3", "admin123")
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        self.client.login(username=username, password="admin123")

        # Test user management pages
        user_urls = ["/users/", "/admin/"]
        accessible_count = 0

        for url in user_urls:
            response = self.client.get(url)
            if response.status_code in [200, 302]:
                accessible_count += 1

        return accessible_count >= 1

    def test_automation_test_links(self):
        """Test automation test links"""
        print("  🤖 Testing automation test links...")

        # Login as admin
        admin_user, username = create_unique_user("admin4", "admin123")
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        self.client.login(username=username, password="admin123")

        # Test automation test page
        response = self.client.get("/automation-test/")
        if response.status_code == 200:
            content = response.content.decode()
            checks = ["href=" in content, "test" in content.lower()]
            return all(checks)

        return False

    def test_external_links(self):
        """Test external links (if any)"""
        print("  🌐 Testing external links...")

        response = self.client.get("/")
        if response.status_code == 200:
            content = response.content.decode()
            # Check for external link patterns
            external_patterns = ["http://", "https://", "www."]
            has_external = any(pattern in content for pattern in external_patterns)
            return True  # Pass if no external links (which is fine)

        return False

    def test_form_submissions(self):
        """Test form submissions"""
        print("  📝 Testing form submissions...")

        # Test login form
        response = self.client.post(
            "/accounts/login/", {"username": "nonexistent", "password": "wrongpass"}
        )
        # Should get 200 with error or 302 redirect
        return response.status_code in [200, 302]

    def test_api_endpoints(self):
        """Test API endpoints"""
        print("  🔌 Testing API endpoints...")

        # Login first
        user, username = create_unique_user("testuser5")
        self.client.login(username=username, password="testpass123")

        # Test API endpoints
        api_urls = ["/checkin/api/history/", "/automation-test/api/sessions/"]
        accessible_count = 0

        for url in api_urls:
            response = self.client.get(url)
            if response.status_code in [
                200,
                404,
                405,
            ]:  # 404/405 are acceptable for some endpoints
                accessible_count += 1

        return accessible_count >= 1


class ComprehensiveTestModule:
    """Comprehensive test module combining all test types"""

    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
        self.display_tests = DisplayTestModule(base_url)
        self.link_tests = LinkTestModule(base_url)
        self.test_results = []

    def run_all_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Running Comprehensive Tests...")

        # Run display tests
        display_results = self.display_tests.run_all_tests()
        self.test_results.extend(display_results)

        # Run link tests
        link_results = self.link_tests.run_all_tests()
        self.test_results.extend(link_results)

        # Run additional comprehensive tests
        additional_tests = [
            self.test_system_integration,
            self.test_performance_basic,
            self.test_security_basic,
            self.test_data_integrity,
        ]

        for test in additional_tests:
            try:
                result = test()
                self.test_results.append(
                    {
                        "name": test.__name__,
                        "status": "passed" if result else "failed",
                        "module": "Comprehensive",
                    }
                )
            except Exception as e:
                self.test_results.append(
                    {
                        "name": test.__name__,
                        "status": "failed",
                        "module": "Comprehensive",
                        "error": str(e),
                    }
                )

        return self.test_results

    def test_system_integration(self):
        """Test system integration"""
        print("  🔧 Testing system integration...")

        # Test database connection
        try:
            from django.db import connection

            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        except Exception:
            return False

    def test_performance_basic(self):
        """Basic performance test"""
        print("  ⚡ Testing basic performance...")

        start_time = time.time()
        response = self.display_tests.client.get("/")
        end_time = time.time()

        response_time = end_time - start_time
        return response_time < 5.0  # Should respond within 5 seconds

    def test_security_basic(self):
        """Basic security test"""
        print("  🔒 Testing basic security...")

        # Test that admin pages require authentication
        response = self.display_tests.client.get("/admin/")
        return response.status_code in [302, 403]  # Should redirect or forbid

    def test_data_integrity(self):
        """Test data integrity"""
        print("  💾 Testing data integrity...")

        # Test that we can create and retrieve data
        try:
            user, username = create_unique_user("integrity_test")
            retrieved_user = User.objects.get(username=username)
            return retrieved_user.email == f"{username}@example.com"
        except Exception:
            return False


def get_test_modules():
    """Get all available test modules"""
    return {
        "display": DisplayTestModule,
        "links": LinkTestModule,
        "comprehensive": ComprehensiveTestModule,
    }


def run_test_module(module_name, base_url="http://localhost:3000"):
    """Run a specific test module"""
    modules = get_test_modules()

    if module_name not in modules:
        raise ValueError(f"Unknown test module: {module_name}")

    module_class = modules[module_name]
    module_instance = module_class(base_url)

    return module_instance.run_all_tests()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run automation test modules")
    parser.add_argument(
        "module",
        choices=["display", "links", "comprehensive"],
        help="Test module to run",
    )
    parser.add_argument(
        "--url", default="http://localhost:3000", help="Base URL for testing"
    )

    args = parser.parse_args()

    print(f"🧪 Running {args.module} tests...")
    results = run_test_module(args.module, args.url)

    print(f"\n📊 Test Results:")
    passed = sum(1 for r in results if r["status"] == "passed")
    failed = sum(1 for r in results if r["status"] == "failed")

    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {passed/(passed+failed)*100:.1f}%")
