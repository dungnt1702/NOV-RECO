from math import radians, sin, cos, sqrt, atan2
from apps.location.models import Location


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Tính khoảng cách giữa hai điểm trên Trái Đất bằng công thức Haversine
    Trả về khoảng cách tính bằng mét
    """
    # Bán kính Trái Đất tính bằng mét
    R = 6371000
    
    # Chuyển đổi độ sang radian
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Tính toán sự khác biệt
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Công thức Haversine
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    # Khoảng cách tính bằng mét
    distance = R * c
    return distance


def find_best_location_for_checkin(checkin_lat, checkin_lng):
    """
    Tìm location phù hợp nhất cho một checkin dựa trên tọa độ lat/lng
    
    Args:
        checkin_lat (float): Vĩ độ của checkin
        checkin_lng (float): Kinh độ của checkin
    
    Returns:
        tuple: (location_name, distance_m) hoặc ("Không xác định", None) nếu không tìm thấy
    """
    if not checkin_lat or not checkin_lng:
        return "Không xác định", None
    
    # Lấy tất cả locations đang hoạt động
    active_locations = Location.objects.filter(is_active=True)
    
    if not active_locations.exists():
        return "Không xác định", None
    
    best_location = None
    best_distance = float('inf')
    
    # Tìm location gần nhất trong phạm vi radius
    for location in active_locations:
        distance = haversine_distance(
            checkin_lat, checkin_lng,
            location.lat, location.lng
        )
        
        # Chỉ xem xét locations trong phạm vi radius
        if distance <= location.radius_m:
            if distance < best_distance:
                best_distance = distance
                best_location = location
    
    if best_location:
        return best_location.name, best_distance
    else:
        return "Không xác định", None


def get_location_name_for_checkin(checkin):
    """
    Lấy tên location cho một checkin object
    
    Args:
        checkin: Checkin object
    
    Returns:
        str: Tên location hoặc "Không xác định"
    """
    location_name, _ = find_best_location_for_checkin(checkin.lat, checkin.lng)
    return location_name