from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Web Views
    path('', views.notification_list_view, name='list'),
    path('mark-read/<int:notification_id>/', views.mark_notification_read_view, name='mark_read'),
    path('mark-all-read/', views.mark_all_notifications_read_view, name='mark_all_read'),
    
    # API Views
    path('api/', views.notification_api, name='api'),
    path('api/mark-read/<int:notification_id>/', views.mark_notification_read_api, name='api_mark_read'),
    path('api/mark-all-read/', views.mark_all_notifications_read_api, name='api_mark_all_read'),
    path('api/unread-count/', views.unread_count_api, name='api_unread_count'),
]
