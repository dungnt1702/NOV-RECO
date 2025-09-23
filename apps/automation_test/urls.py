from django.urls import path
from . import views

app_name = 'automation_test'

urlpatterns = [
    path('', views.test_dashboard, name='dashboard'),
    path('api/sessions/', views.get_sessions, name='sessions_api'),
    path('session/<str:session_id>/', views.test_session_detail, name='session_detail'),
    path('api/start-session/', views.start_test, name='start_session_api'),
    path('api/session-status/<str:session_id>/', views.get_test_status, name='session_status_api'),
    path('api/session-logs/<str:session_id>/', views.get_test_logs, name='session_logs_api'),
]
