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

echo -e "${BLUE}[1/4] Setting up user groups and permissions...${NC}"
python3 manage.py setup_user_groups
echo

echo -e "${BLUE}[2/4] Creating superuser...${NC}"
python3 manage.py create_admin
echo

echo -e "${BLUE}[3/4] Creating complete sample data...${NC}"
python3 manage.py create_sample_data --clear
echo

echo -e "${BLUE}[4/4] Collecting static files...${NC}"
python3 manage.py collectstatic --noinput
echo

echo -e "${GREEN}===============================================${NC}"
echo -e "${GREEN}           SETUP COMPLETE!${NC}"
echo -e "${GREEN}===============================================${NC}"
echo

echo -e "${YELLOW}THÔNG TIN ĐĂNG NHẬP:${NC}"
echo

echo -e "${RED}🔴 Super Admin: admin / admin123${NC}"
echo "   - Toàn quyền hệ thống"
echo

echo -e "${YELLOW}🟡 Manager IT: manager_it / password123${NC}"
echo "   - Quản lý IT, xem check-ins"
echo

echo -e "${YELLOW}🟡 Manager HR: manager_hr / password123${NC}"
echo "   - Quản lý nhân sự, xem check-ins"
echo

echo -e "${GREEN}🟢 HCNS: hcns_main / password123${NC}"
echo "   - Quản lý users, xem check-ins"
echo

echo -e "${GREEN}🟢 HCNS Recruit: hcns_recruit / password123${NC}"
echo "   - Quản lý users, tuyển dụng"
echo

echo -e "${BLUE}🔵 Developer: dev_001 / password123${NC}"
echo "   - Nhân viên IT, check-in"
echo

echo -e "${BLUE}🔵 Accountant: accountant_001 / password123${NC}"
echo "   - Nhân viên kế toán, check-in"
echo

echo -e "${BLUE}🔵 Sales: sales_001 / password123${NC}"
echo "   - Nhân viên kinh doanh, check-in"
echo

echo -e "${GREEN}===============================================${NC}"
echo -e "${GREEN}Access: http://localhost:3000${NC}"
echo -e "${GREEN}Admin:  http://localhost:3000/admin${NC}"
echo -e "${GREEN}===============================================${NC}"
echo

read -p "Press any key to continue..."
