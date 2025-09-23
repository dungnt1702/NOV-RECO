from django import template
from django.contrib.auth.models import Group

register = template.Library()


@register.filter
def has_permission(user, permission_name):
    """Kiểm tra user có permission không"""
    if not user.is_authenticated:
        return False
    
    # Superuser có tất cả quyền
    if user.is_superuser:
        return True
    
    return user.has_perm(permission_name)


@register.filter
def in_group(user, group_name):
    """Kiểm tra user có thuộc group không"""
    if not user.is_authenticated:
        return False
    
    # Superuser thuộc tất cả groups
    if user.is_superuser:
        return True
    
    return user.groups.filter(name=group_name).exists()


@register.filter
def in_any_group(user, group_names):
    """Kiểm tra user có thuộc bất kỳ group nào trong danh sách không"""
    if not user.is_authenticated:
        return False
    
    # Superuser thuộc tất cả groups
    if user.is_superuser:
        return True
    
    if isinstance(group_names, str):
        group_list = [group_names]
    else:
        group_list = group_names
    
    return user.groups.filter(name__in=group_list).exists()


@register.filter
def has_any_permission(user, permission_names):
    """Kiểm tra user có bất kỳ permission nào trong danh sách không"""
    if not user.is_authenticated:
        return False
    
    # Superuser có tất cả quyền
    if user.is_superuser:
        return True
    
    if isinstance(permission_names, str):
        perm_list = [permission_names]
    else:
        perm_list = permission_names
    
    for perm in perm_list:
        if user.has_perm(perm):
            return True
    
    return False


@register.filter
def get_user_groups(user):
    """Lấy danh sách groups của user"""
    if not user.is_authenticated:
        return []
    
    return user.groups.all()


@register.filter
def get_group_permissions(user):
    """Lấy danh sách permissions của user (từ groups)"""
    if not user.is_authenticated:
        return []
    
    # Superuser có tất cả permissions
    if user.is_superuser:
        return Permission.objects.all()
    
    # Lấy permissions từ groups
    permissions = set()
    for group in user.groups.all():
        permissions.update(group.permissions.all())
    
    return list(permissions)
