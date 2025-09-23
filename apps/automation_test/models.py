from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class TestSession(models.Model):
    """Test session model to track test runs"""
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    session_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_tests = models.IntegerField(default=0)
    passed_tests = models.IntegerField(default=0)
    failed_tests = models.IntegerField(default=0)
    skipped_tests = models.IntegerField(default=0)
    duration = models.FloatField(null=True, blank=True)  # in seconds
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Test Session {self.session_id} - {self.status}"
    
    @property
    def success_rate(self):
        if self.total_tests == 0:
            return 0
        return (self.passed_tests / self.total_tests) * 100


class TestResult(models.Model):
    """Individual test result model"""
    STATUS_CHOICES = [
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
        ('error', 'Error'),
    ]
    
    session = models.ForeignKey(TestSession, on_delete=models.CASCADE, related_name='results')
    test_name = models.CharField(max_length=200)
    module = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    duration = models.FloatField(null=True, blank=True)  # in seconds
    error_message = models.TextField(blank=True)
    stack_trace = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.test_name} - {self.status}"


class TestLog(models.Model):
    """Test log model for detailed logging"""
    LOG_LEVELS = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]
    
    session = models.ForeignKey(TestSession, on_delete=models.CASCADE, related_name='logs')
    level = models.CharField(max_length=20, choices=LOG_LEVELS)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    test_name = models.CharField(max_length=200, blank=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"[{self.level}] {self.message[:50]}..."
