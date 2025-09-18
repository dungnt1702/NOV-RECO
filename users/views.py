from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import User, UserRole
from .forms import UserCreateForm, UserUpdateForm
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
)
from checkin.decorators import admin_required


@admin_required
def user_list_view(request):
    """Trang danh sách người dùng cho Admin"""
    search_query = request.GET.get("search", "")
    role_filter = request.GET.get("role", "")

    users = User.objects.all().order_by('username')

    if search_query:
        users = users.filter(
            Q(username__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(employee_id__icontains=search_query)
        )

    if role_filter:
        users = users.filter(role=role_filter)

    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "role_filter": role_filter,
        "role_choices": UserRole.choices,
    }
    return render(request, "users/user_list.html", context)


@admin_required
def user_create_view(request):
    """Trang tạo người dùng mới"""
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request, f"Đã tạo người dùng {user.username} thành công!"
            )
            return redirect("users:user_list")
    else:
        form = UserCreateForm()

    return render(
        request,
        "users/user_form.html",
        {
            "form": form,
            "title": "Tạo người dùng mới",
            "submit_text": "Tạo người dùng",
        },
    )


@admin_required
def user_update_view(request, user_id):
    """Trang cập nhật thông tin người dùng"""
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"Đã cập nhật thông tin {user.username} thành công!"
            )
            return redirect("users:user_list")
    else:
        form = UserUpdateForm(instance=user)

    return render(
        request,
        "users/user_form.html",
        {
            "form": form,
            "title": f"Cập nhật người dùng: {user.username}",
            "submit_text": "Cập nhật",
            "user": user,
        },
    )


@admin_required
def user_delete_view(request, user_id):
    """Xóa người dùng"""
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        username = user.username
        user.delete()
        messages.success(request, f"Đã xóa người dùng {username} thành công!")
        return redirect("users:user_list")

    return render(request, "users/user_confirm_delete.html", {"user": user})


# API Views
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_list_api(request):
    """API lấy danh sách người dùng"""
    if not request.user.can_manage_users():
        return Response({"error": "Không có quyền truy cập"}, status=403)

    search_query = request.GET.get("search", "")
    role_filter = request.GET.get("role", "")

    users = User.objects.all()

    if search_query:
        users = users.filter(
            Q(username__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(employee_id__icontains=search_query)
        )

    if role_filter:
        users = users.filter(role=role_filter)

    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def user_create_api(request):
    """API tạo người dùng mới"""
    if not request.user.can_manage_users():
        return Response({"error": "Không có quyền truy cập"}, status=403)

    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            UserSerializer(user).data, status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def user_detail_api(request, user_id):
    """API chi tiết người dùng"""
    if not request.user.can_manage_users():
        return Response({"error": "Không có quyền truy cập"}, status=403)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "Người dùng không tồn tại"}, status=404)

    if request.method == "GET":
        serializer = UserSerializer(user)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = UserUpdateSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(UserSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
