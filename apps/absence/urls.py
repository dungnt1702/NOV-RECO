from django.urls import path, include
from . import views, api_views, api_views_workflow

app_name = 'absence'

urlpatterns = [
    # Web Views
    path('request/', views.absence_request_view, name='request'),
    path('list/', views.absence_list_view, name='list'),
    path('detail/<int:absence_id>/', views.absence_detail_view, name='detail'),
    path('approval/', views.approval_view, name='approval'),
    path('approve/<int:absence_id>/', views.approval_view, name='approve'),
    path('workflow-config/', views.workflow_config_view, name='workflow_config'),
    path('workflow/create/', views.workflow_create_view, name='workflow_create'),
    path('workflow/update/<int:workflow_id>/', views.workflow_update_view, name='workflow_update'),
    
    # API Views
    path('api/types/', api_views.absence_types_api, name='api_types'),
    path('api/requests/', api_views.absence_requests_api, name='api_requests'),
    path('api/create/', api_views.create_absence_request_api, name='api_create'),
    path('api/approve/<int:absence_id>/', api_views.approve_request_api, name='api_approve'),
    path('api/status/<int:absence_id>/', api_views.workflow_status_api, name='api_status'),
    
    # Workflow API
    path('api/workflow/', api_views_workflow.workflow_api, name='api_workflow'),
    path('api/workflow/<int:workflow_id>/', api_views_workflow.workflow_detail_api, name='api_workflow_detail'),
]
