from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Area
from .serializers import AreaSerializer
from .decorators import role_required
from users.models import UserRole


@role_required([UserRole.ADMIN, UserRole.MANAGER, UserRole.HCNS])
def area_list_view(request):
    """Danh sách khu vực cho Thư ký, Quản lý, HCNS"""
    return render(request, "area/list.html")


@role_required([UserRole.ADMIN, UserRole.MANAGER, UserRole.HCNS])
def area_form_view(request, area_id=None):
    """Form thêm/sửa khu vực cho Thư ký, Quản lý, HCNS"""
    area = None
    if area_id:
        try:
            area = Area.objects.get(id=area_id)
        except Area.DoesNotExist:
            messages.error(request, "Khu vực không tồn tại.")
            return redirect("area:list")
    
    context = {
        'area': area
    }
    return render(request, "area/form.html", context)


# API Views
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def areas_api(request):
    """API quản lý khu vực"""
    from django.core.paginator import Paginator
    from django.db.models import Q
    
    # Check permissions
    if not (request.user.is_admin() or request.user.is_manager() or request.user.is_hcns()):
        return Response({"error": "Permission denied"}, status=403)

    if request.method == "GET":
        # Get query parameters
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 25))
        status = request.GET.get('status', '')
        search = request.GET.get('search', '')
        
        # Build queryset
        queryset = Area.objects.all().order_by("-created_at")
        
        # Apply filters
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        # Pagination
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        # Serialize data
        serializer = AreaSerializer(page_obj, many=True)
        
        return Response({
            'results': serializer.data,
            'count': paginator.count,
            'page': page,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous()
        })

    elif request.method == "POST":
        serializer = AreaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def area_detail_api(request, area_id):
    """API chi tiết khu vực"""
    # Check permissions
    if not (request.user.is_admin() or request.user.is_manager() or request.user.is_hcns()):
        return Response({"error": "Permission denied"}, status=403)
    
    try:
        area = Area.objects.get(id=area_id)
    except Area.DoesNotExist:
        return Response({"error": "Area not found"}, status=404)

    if request.method == "GET":
        serializer = AreaSerializer(area)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = AreaSerializer(area, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == "DELETE":
        area.delete()
        return Response({"message": "Area deleted successfully"}, status=200)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_checkins_areas_api(request):
    """API cập nhật tất cả check-in dựa trên area hiện có"""
    from django.core.management import call_command
    from io import StringIO
    import sys

    if not (request.user.is_admin() or request.user.is_manager()):
        return Response(
            {"error": "Không có quyền thực hiện thao tác này"}, status=403
        )

    try:
        # Capture output
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        # Run the management command
        call_command('update_checkin_areas')
        
        # Get the output
        output = captured_output.getvalue()
        sys.stdout = old_stdout
        
        # Parse the output to get updated count
        updated_count = 0
        for line in output.split('\n'):
            if 'Updated' in line and 'check-ins' in line:
                try:
                    updated_count = int(line.split('Updated')[1].split('check-ins')[0].strip())
                except:
                    pass
                break
        
        return Response({
            "message": "Cập nhật check-in thành công",
            "updated_count": updated_count,
            "output": output
        })
        
    except Exception as e:
        return Response(
            {"error": f"Lỗi khi cập nhật check-in: {str(e)}"}, status=500
        )
