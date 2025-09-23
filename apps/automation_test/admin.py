from django.contrib import admin
from .models import TestSession, TestResult, TestLog


@admin.register(TestSession)
class TestSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'status', 'started_at', 'total_tests', 'passed_tests', 'failed_tests', 'success_rate']
    list_filter = ['status', 'started_at']
    search_fields = ['session_id', 'user__username']
    readonly_fields = ['session_id', 'started_at', 'completed_at', 'duration', 'success_rate']
    ordering = ['-started_at']


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ['test_name', 'module', 'status', 'duration', 'created_at']
    list_filter = ['status', 'module', 'created_at']
    search_fields = ['test_name', 'module']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(TestLog)
class TestLogAdmin(admin.ModelAdmin):
    list_display = ['level', 'message', 'test_name', 'timestamp']
    list_filter = ['level', 'timestamp']
    search_fields = ['message', 'test_name']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
