#!/bin/bash

# Script để khởi động Django server với port tùy chỉnh
# Sử dụng: ./start_server.sh [port]

# Màu sắc cho output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Port mặc định
DEFAULT_PORT=3000

# Lấy port từ argument hoặc sử dụng default
if [ $# -eq 0 ]; then
    PORT=$DEFAULT_PORT
else
    PORT=$1
fi

echo -e "${BLUE}🚀 Khởi động Django server...${NC}"
echo -e "${GREEN}📱 Server sẽ chạy trên: http://localhost:$PORT${NC}"
echo -e "${YELLOW}⏹️  Nhấn Ctrl+C để dừng server${NC}"
echo ""

# Kiểm tra xem virtual environment có tồn tại không
if [ -d "venv" ]; then
    echo -e "${BLUE}🔧 Kích hoạt virtual environment...${NC}"
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo -e "${BLUE}🔧 Kích hoạt virtual environment...${NC}"
    source .venv/bin/activate
fi

# Chạy migrations nếu cần
echo -e "${BLUE}🔄 Kiểm tra migrations...${NC}"
python manage.py migrate

# Khởi động server
echo -e "${GREEN}🌟 Khởi động server trên port $PORT...${NC}"
python manage.py runserver 0.0.0.0:$PORT
