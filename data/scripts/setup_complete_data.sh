#!/bin/bash

# NOV-RECO Complete Data Setup Script for macOS/Linux
echo "================================================"
echo "        NOV-RECO COMPLETE DATA SETUP"
echo "================================================"
echo

# Màu sắc
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Di chuyển đến thư mục gốc của dự án
cd "$(dirname "$0")/../.."

echo -e "${BLUE}[1/3] Setting up user groups and permissions...${NC}"
python3 manage.py setup_user_groups
echo

echo -e "${BLUE}[2/3] Creating sample users...${NC}"
python3 manage.py create_sample_users
echo

echo -e "${BLUE}[3/3] Creating sample areas...${NC}"
python3 manage.py create_sample_areas
echo

echo -e "${GREEN}===============================================${NC}"
echo -e "${GREEN}           SETUP COMPLETE!${NC}"
echo -e "${GREEN}===============================================${NC}"
echo

echo -e "${YELLOW}THÔNG TIN ĐĂNG NHẬP:${NC}"
echo

echo -e "${RED}🔴 Super Admin: superadmin / admin123${NC}"
echo "   - Toàn quyền hệ thống"
echo

echo -e "${YELLOW}🟡 Quản lý: quanly / quanly123${NC}"
echo "   - Xem và sửa toàn bộ"
echo

echo -e "${GREEN}🟢 Thư ký: thuky / thuky123${NC}"
echo "   - Xem và sửa toàn bộ (trừ user management)"
echo

echo -e "${BLUE}🔵 Nhân viên 1: nhanvien1 / nhanvien123${NC}"
echo "   - Xem và checkin"
echo

echo -e "${BLUE}🔵 Nhân viên 2: nhanvien2 / nhanvien123${NC}"
echo "   - Xem và checkin"
echo

echo -e "${GREEN}===============================================${NC}"
echo -e "${GREEN}Access: http://localhost:3000${NC}"
echo -e "${GREEN}Admin:  http://localhost:3000/admin${NC}"
echo -e "${GREEN}===============================================${NC}"
echo

read -p "Press any key to continue..."
