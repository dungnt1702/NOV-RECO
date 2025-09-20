#!/bin/bash

# NOV-RECO Start Local Server Script for macOS/Linux
echo "Starting NOV-RECO Check-in System..."
echo

# Màu sắc
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Di chuyển đến thư mục gốc của dự án
cd "$(dirname "$0")/../.."

# Khởi động Django development server
echo -e "${BLUE}Starting Django server on port 3000...${NC}"
python3 manage.py runserver 127.0.0.1:3000 &
SERVER_PID=$!

# Đợi một chút để server khởi động
sleep 3

# Mở browser với localhost
echo -e "${GREEN}Opening browser at http://localhost:3000...${NC}"
open http://localhost:3000 2>/dev/null || xdg-open http://localhost:3000 2>/dev/null || echo "Please open http://localhost:3000 in your browser"

echo
echo -e "${GREEN}NOV-RECO is now running at:${NC}"
echo -e "${GREEN}- Local: http://localhost:3000${NC}"
echo -e "${GREEN}- Admin: http://localhost:3000/admin${NC}"
echo -e "${YELLOW}- Username: superadmin${NC}"
echo -e "${YELLOW}- Password: admin123${NC}"
echo

echo -e "${YELLOW}Press Ctrl+C to stop the server...${NC}"

# Đợi người dùng nhấn Ctrl+C
trap "echo -e '\n${RED}Stopping server...${NC}'; kill $SERVER_PID 2>/dev/null; exit 0" INT
wait $SERVER_PID
