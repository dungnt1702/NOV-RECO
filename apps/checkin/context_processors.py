from datetime import datetime


def current_year(request):
    """Thêm current_year vào context"""
    return {"current_year": datetime.now().year}
