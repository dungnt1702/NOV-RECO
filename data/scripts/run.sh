#!/bin/bash

# NOV-RECO Script Manager for macOS/Linux
echo "🎯 NOV-RECO Script Manager"
echo "=========================="

# Màu sắc
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Di chuyển đến thư mục gốc của dự án
cd "$(dirname "$0")/../.."

# Hiển thị menu
show_menu() {
    echo -e "${BLUE}Chọn script để chạy:${NC}"
    echo "1) Quick Start (Khởi động nhanh)"
    echo "2) Setup Complete Data (Thiết lập dữ liệu đầy đủ)"
    echo "3) Start Server Only (Chỉ khởi động server)"
    echo "4) Start with Browser (Khởi động và mở browser)"
    echo "5) Run Server (Python script)"
    echo "6) Start Server (Advanced Python script)"
    echo "0) Exit"
    echo
}

# Chạy script được chọn
run_script() {
    case $1 in
        1)
            echo -e "${GREEN}🚀 Chạy Quick Start...${NC}"
            ./data/scripts/quick_start_mac.sh
            ;;
        2)
            echo -e "${GREEN}🔧 Chạy Setup Complete Data...${NC}"
            ./data/scripts/setup_complete_data.sh
            ;;
        3)
            echo -e "${GREEN}🖥️  Chạy Start Server Only...${NC}"
            ./data/scripts/start_server.sh
            ;;
        4)
            echo -e "${GREEN}🌐 Chạy Start with Browser...${NC}"
            ./data/scripts/start_reco_local.sh
            ;;
        5)
            echo -e "${GREEN}🐍 Chạy Run Server (Python)...${NC}"
            python3 data/scripts/run_server.py
            ;;
        6)
            echo -e "${GREEN}⚡ Chạy Start Server (Advanced)...${NC}"
            python3 data/scripts/start_server.py
            ;;
        0)
            echo -e "${YELLOW}👋 Tạm biệt!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Lựa chọn không hợp lệ!${NC}"
            ;;
    esac
}

# Vòng lặp chính
while true; do
    show_menu
    read -p "Nhập lựa chọn (0-6): " choice
    echo
    
    if [[ "$choice" =~ ^[0-6]$ ]]; then
        run_script $choice
        echo
        read -p "Nhấn Enter để tiếp tục..."
        echo
    else
        echo -e "${RED}❌ Vui lòng nhập số từ 0-6${NC}"
        echo
    fi
done
