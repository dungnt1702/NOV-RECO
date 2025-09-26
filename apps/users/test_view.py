from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from .models import User

def test_user_update_view(request, id):
    """Test view để bypass template system"""
    try:
        user = get_object_or_404(User, id=id)
        return JsonResponse({
            'status': 'success',
            'user_id': user.id,
            'username': user.username,
            'message': f'User {id} found successfully'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def simple_user_update_view(request, id):
    """Simple view without template to bypass error"""
    try:
        user = get_object_or_404(User, id=id)
        # Return simple HTML response without template
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>User Update - {user.username}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 50px; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                h1 {{ color: #333; }}
                .info {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>User Update Page</h1>
                <div class="info">
                    <p><strong>User ID:</strong> {user.id}</p>
                    <p><strong>Username:</strong> {user.username}</p>
                    <p><strong>Email:</strong> {user.email}</p>
                    <p><strong>Full Name:</strong> {user.get_full_name()}</p>
                    <p><strong>Status:</strong> {'Active' if user.is_active else 'Inactive'}</p>
                </div>
                <p>✅ URL patterns và views hoạt động đúng!</p>
                <p>⚠️ Vấn đề là template system đang gây lỗi.</p>
                <p><a href="/users/list/">← Back to User List</a></p>
            </div>
        </body>
        </html>
        """
        return HttpResponse(html)
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)
