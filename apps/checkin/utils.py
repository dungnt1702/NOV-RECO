import math
from apps.area.models import Area


def haversine_m(lat1, lon1, lat2, lon2):
    """
    Tính khoảng cách giữa hai điểm trên Trái Đất bằng công thức Haversine
    Trả về khoảng cách tính bằng mét
    """
    # Bán kính Trái Đất tính bằng mét
    R = 6371000
    
    # Chuyển đổi độ sang radian
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Tính toán
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Khoảng cách tính bằng mét
    distance = R * c
    
    return distance


def find_nearest_area(user_lat, user_lng, area_id=None):
    """
    Tìm khu vực gần nhất dựa trên tọa độ của người dùng
    
    Args:
        user_lat (float): Vĩ độ của người dùng
        user_lng (float): Kinh độ của người dùng
        area_id (int, optional): ID khu vực cụ thể nếu có
    
    Returns:
        tuple: (area, distance) - Khu vực gần nhất và khoảng cách
    """
    area = None
    distance = None
    
    # Nếu có area_id cụ thể, kiểm tra khu vực đó trước
    if area_id:
        try:
            area = Area.objects.get(id=area_id, is_active=True)
            distance = haversine_m(area.lat, area.lng, user_lat, user_lng)
            # Kiểm tra xem có trong bán kính không
            if distance <= area.radius_m:
                return area, distance
            else:
                area = None  # Không trong bán kính, tìm khu vực khác
        except Area.DoesNotExist:
            pass
    
    # Tìm khu vực gần nhất trong tất cả các khu vực hoạt động
    areas = Area.objects.filter(is_active=True)
    min_distance = float('inf')
    
    for a in areas:
        dist = haversine_m(a.lat, a.lng, user_lat, user_lng)
        # Chỉ xem xét các khu vực trong bán kính cho phép
        if dist <= a.radius_m and dist < min_distance:
            min_distance = dist
            area = a
            distance = dist
    
    return area, distance
