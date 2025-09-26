import math
from apps.location.models import Location


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


def find_nearest_location(user_lat, user_lng, location_id=None):
    """
    Tìm địa điểm gần nhất dựa trên tọa độ của người dùng
    
    Args:
        user_lat (float): Vĩ độ của người dùng
        user_lng (float): Kinh độ của người dùng
        location_id (int, optional): ID địa điểm cụ thể nếu có
    
    Returns:
        tuple: (location, distance) - Địa điểm gần nhất và khoảng cách
    """
    location = None
    distance = None
    
    # Nếu có location_id cụ thể, kiểm tra địa điểm đó trước
    if location_id:
        try:
            location = Location.objects.get(id=location_id, is_active=True)
            distance = haversine_m(location.lat, location.lng, user_lat, user_lng)
            # Kiểm tra xem có trong bán kính không
            if distance <= location.radius_m:
                return location, distance
            else:
                location = None  # Không trong bán kính, tìm địa điểm khác
        except Location.DoesNotExist:
            pass
    
    # Tìm địa điểm gần nhất trong tất cả các địa điểm hoạt động
    locations = Location.objects.filter(is_active=True)
    min_distance = float('inf')
    
    for loc in locations:
        dist = haversine_m(loc.lat, loc.lng, user_lat, user_lng)
        # Chỉ xem xét các địa điểm trong bán kính cho phép
        if dist <= loc.radius_m and dist < min_distance:
            min_distance = dist
            location = loc
            distance = dist
    
    return location, distance
