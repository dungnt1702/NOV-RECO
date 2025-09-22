import math


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
