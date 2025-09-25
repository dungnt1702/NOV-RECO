from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
import json

from apps.checkin.models import Checkin
from apps.users.models import User, Department, Office
from apps.area.models import Area


@login_required
@require_http_methods(["GET"])
def module_data_api(request, module_name):
    """API endpoint để lấy dữ liệu cho các module"""
    user = request.user
    
    try:
        if module_name == 'sales':
            return get_sales_data(user)
        elif module_name == 'hr':
            return get_hr_data(user)
        elif module_name == 'marketing':
            return get_marketing_data(user)
        elif module_name == 'finance':
            return get_finance_data(user)
        elif module_name == 'operations':
            return get_operations_data(user)
        else:
            return get_custom_module_data(user, module_name)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def get_sales_data(user):
    """Dữ liệu module Sales - dựa trên check-in patterns"""
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    
    # Simulate sales data based on check-ins
    daily_checkins = Checkin.objects.filter(created_at__date=today).count()
    weekly_checkins = Checkin.objects.filter(created_at__date__gte=week_start).count()
    monthly_checkins = Checkin.objects.filter(created_at__date__gte=month_start).count()
    
    # Convert check-ins to sales metrics (simulation)
    daily_sales = daily_checkins * 1000  # 1000 VND per check-in
    weekly_sales = weekly_checkins * 1000
    monthly_sales = monthly_checkins * 1000
    
    data = {
        'chart': {
            'labels': ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'],
            'datasets': [{
                'label': 'Doanh số (VNĐ)',
                'data': [
                    weekly_checkins * 1000,
                    weekly_checkins * 1200,
                    weekly_checkins * 1100,
                    weekly_checkins * 1300,
                    weekly_checkins * 1000,
                    weekly_checkins * 800,
                    weekly_checkins * 600
                ],
                'backgroundColor': 'rgba(102, 126, 234, 0.2)',
                'borderColor': '#667eea',
                'borderWidth': 2
            }]
        },
        'metrics': {
            'daily_sales': daily_sales,
            'weekly_sales': weekly_sales,
            'monthly_sales': monthly_sales,
            'growth_rate': '+15%'
        },
        'table': [
            {'product': 'Sản phẩm A', 'sales': daily_sales, 'units': daily_checkins},
            {'product': 'Sản phẩm B', 'sales': daily_sales * 0.8, 'units': int(daily_checkins * 0.8)},
            {'product': 'Sản phẩm C', 'sales': daily_sales * 0.6, 'units': int(daily_checkins * 0.6)}
        ]
    }
    
    return JsonResponse({
        'success': True,
        'data': data,
        'module': 'sales',
        'title': 'Bán hàng',
        'last_updated': timezone.now().isoformat()
    })


def get_hr_data(user):
    """Dữ liệu module HR - dựa trên user và department data"""
    total_employees = User.objects.filter(is_active=True).count()
    departments = Department.objects.annotate(employee_count=Count('user'))
    offices = Office.objects.all()
    
    # Employee distribution by department
    dept_data = []
    for dept in departments:
        dept_data.append({
            'name': dept.name,
            'count': dept.employee_count,
            'percentage': round((dept.employee_count / total_employees * 100), 1) if total_employees > 0 else 0
        })
    
    # Office distribution
    office_data = []
    for office in offices:
        office_employees = User.objects.filter(department__office=office, is_active=True).count()
        office_data.append({
            'name': office.name,
            'count': office_employees
        })
    
    data = {
        'chart': {
            'labels': [dept['name'] for dept in dept_data],
            'datasets': [{
                'label': 'Số nhân viên',
                'data': [dept['count'] for dept in dept_data],
                'backgroundColor': [
                    '#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe'
                ]
            }]
        },
        'metrics': {
            'total_employees': total_employees,
            'total_departments': departments.count(),
            'total_offices': offices.count(),
            'avg_employees_per_dept': round(total_employees / departments.count(), 1) if departments.count() > 0 else 0
        },
        'table': dept_data
    }
    
    return JsonResponse({
        'success': True,
        'data': data,
        'module': 'hr',
        'title': 'Nhân sự',
        'last_updated': timezone.now().isoformat()
    })


def get_marketing_data(user):
    """Dữ liệu module Marketing - dựa trên check-in patterns"""
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    
    # Simulate marketing campaigns based on check-ins
    daily_checkins = Checkin.objects.filter(created_at__date=today).count()
    weekly_checkins = Checkin.objects.filter(created_at__date__gte=week_start).count()
    
    # Marketing metrics simulation
    campaigns = [
        {'name': 'Campaign A', 'reach': daily_checkins * 10, 'engagement': daily_checkins * 2, 'conversion': daily_checkins * 0.1},
        {'name': 'Campaign B', 'reach': weekly_checkins * 5, 'engagement': weekly_checkins * 1.5, 'conversion': weekly_checkins * 0.08},
        {'name': 'Campaign C', 'reach': daily_checkins * 8, 'engagement': daily_checkins * 1.8, 'conversion': daily_checkins * 0.12}
    ]
    
    data = {
        'chart': {
            'labels': ['Reach', 'Engagement', 'Conversion'],
            'datasets': [{
                'label': 'Campaign Performance',
                'data': [
                    sum(c['reach'] for c in campaigns),
                    sum(c['engagement'] for c in campaigns),
                    sum(c['conversion'] for c in campaigns)
                ],
                'backgroundColor': ['#f093fb', '#f5576c', '#4facfe']
            }]
        },
        'metrics': {
            'total_reach': sum(c['reach'] for c in campaigns),
            'total_engagement': sum(c['engagement'] for c in campaigns),
            'total_conversion': sum(c['conversion'] for c in campaigns),
            'conversion_rate': '12.5%'
        },
        'table': campaigns
    }
    
    return JsonResponse({
        'success': True,
        'data': data,
        'module': 'marketing',
        'title': 'Marketing',
        'last_updated': timezone.now().isoformat()
    })


def get_finance_data(user):
    """Dữ liệu module Finance - dựa trên employee và check-in data"""
    total_employees = User.objects.filter(is_active=True).count()
    today_checkins = Checkin.objects.filter(created_at__date=timezone.now().date()).count()
    
    # Simulate financial data
    monthly_revenue = total_employees * 50000000  # 50M VND per employee
    monthly_expenses = total_employees * 30000000  # 30M VND per employee
    profit = monthly_revenue - monthly_expenses
    
    data = {
        'chart': {
            'labels': ['Revenue', 'Expenses', 'Profit'],
            'datasets': [{
                'label': 'Financial Overview (VNĐ)',
                'data': [monthly_revenue, monthly_expenses, profit],
                'backgroundColor': ['#10b981', '#ef4444', '#3b82f6']
            }]
        },
        'metrics': {
            'revenue': monthly_revenue,
            'expenses': monthly_expenses,
            'profit': profit,
            'profit_margin': f"{(profit/monthly_revenue*100):.1f}%" if monthly_revenue > 0 else "0%"
        },
        'table': [
            {'category': 'Revenue', 'amount': monthly_revenue, 'percentage': 100},
            {'category': 'Expenses', 'amount': monthly_expenses, 'percentage': round(monthly_expenses/monthly_revenue*100, 1) if monthly_revenue > 0 else 0},
            {'category': 'Profit', 'amount': profit, 'percentage': round(profit/monthly_revenue*100, 1) if monthly_revenue > 0 else 0}
        ]
    }
    
    return JsonResponse({
        'success': True,
        'data': data,
        'module': 'finance',
        'title': 'Tài chính',
        'last_updated': timezone.now().isoformat()
    })


def get_operations_data(user):
    """Dữ liệu module Operations - dựa trên check-in và area data"""
    areas = Area.objects.filter(is_active=True)
    today = timezone.now().date()
    
    # Operations data based on areas and check-ins
    area_data = []
    for area in areas:
        area_checkins = Checkin.objects.filter(area=area, created_at__date=today).count()
        area_data.append({
            'name': area.name,
            'checkins': area_checkins,
            'efficiency': min(100, area_checkins * 10)  # Simulate efficiency
        })
    
    data = {
        'chart': {
            'labels': [area['name'] for area in area_data],
            'datasets': [{
                'label': 'Check-ins Today',
                'data': [area['checkins'] for area in area_data],
                'backgroundColor': ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe']
            }]
        },
        'metrics': {
            'total_areas': areas.count(),
            'total_checkins': sum(area['checkins'] for area in area_data),
            'avg_efficiency': round(sum(area['efficiency'] for area in area_data) / len(area_data), 1) if area_data else 0,
            'utilization_rate': '85%'
        },
        'table': area_data
    }
    
    return JsonResponse({
        'success': True,
        'data': data,
        'module': 'operations',
        'title': 'Vận hành',
        'last_updated': timezone.now().isoformat()
    })


def get_custom_module_data(user, module_name):
    """Dữ liệu cho custom modules"""
    # Generic data for custom modules
    data = {
        'chart': {
            'labels': ['Q1', 'Q2', 'Q3', 'Q4'],
            'datasets': [{
                'label': 'Custom Data',
                'data': [100, 150, 200, 180],
                'backgroundColor': 'rgba(102, 126, 234, 0.2)',
                'borderColor': '#667eea',
                'borderWidth': 2
            }]
        },
        'metrics': {
            'total': 630,
            'growth': '+15%',
            'target': 700,
            'achievement': '90%'
        },
        'table': [
            {'item': 'Item 1', 'value': 100, 'status': 'Active'},
            {'item': 'Item 2', 'value': 150, 'status': 'Active'},
            {'item': 'Item 3', 'value': 200, 'status': 'Active'}
        ]
    }
    
    return JsonResponse({
        'success': True,
        'data': data,
        'module': module_name,
        'title': module_name.title(),
        'last_updated': timezone.now().isoformat()
    })


@login_required
@require_http_methods(["GET"])
def available_modules_api(request):
    """API endpoint để lấy danh sách modules có sẵn"""
    modules = [
        {
            'name': 'sales',
            'title': 'Bán hàng',
            'description': 'Thống kê doanh số và hiệu suất bán hàng',
            'type': 'chart',
            'icon': 'fas fa-chart-line'
        },
        {
            'name': 'hr',
            'title': 'Nhân sự',
            'description': 'Quản lý nhân viên và phòng ban',
            'type': 'chart',
            'icon': 'fas fa-users'
        },
        {
            'name': 'marketing',
            'title': 'Marketing',
            'description': 'Phân tích chiến dịch marketing',
            'type': 'chart',
            'icon': 'fas fa-bullhorn'
        },
        {
            'name': 'finance',
            'title': 'Tài chính',
            'description': 'Báo cáo tài chính và ngân sách',
            'type': 'chart',
            'icon': 'fas fa-dollar-sign'
        },
        {
            'name': 'operations',
            'title': 'Vận hành',
            'description': 'Theo dõi hoạt động vận hành',
            'type': 'chart',
            'icon': 'fas fa-cogs'
        }
    ]
    
    return JsonResponse({
        'success': True,
        'modules': modules
    })
