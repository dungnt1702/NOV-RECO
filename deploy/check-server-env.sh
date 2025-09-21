#!/bin/bash

# NOV-RECO Server Environment Check
# Check server configuration and provide appropriate instructions

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 NOV-RECO Server Environment Check${NC}"
echo -e "${BLUE}====================================${NC}"

# Check domain resolution
echo -e "${YELLOW}📡 Checking domain resolution...${NC}"
if ping -c 1 checkin.taylaibui.vn &> /dev/null; then
    echo -e "${GREEN}✅ Domain checkin.taylaibui.vn is reachable${NC}"
else
    echo -e "${RED}❌ Domain checkin.taylaibui.vn is not reachable${NC}"
fi

# Check web servers
echo -e "${YELLOW}🌐 Checking web servers...${NC}"

APACHE_RUNNING=false
NGINX_RUNNING=false

if pgrep -x "httpd" > /dev/null || pgrep -x "apache2" > /dev/null; then
    echo -e "${GREEN}✅ Apache is running${NC}"
    APACHE_RUNNING=true
fi

if pgrep -x "nginx" > /dev/null; then
    echo -e "${GREEN}✅ Nginx is running${NC}"
    NGINX_RUNNING=true
fi

if [ "$APACHE_RUNNING" = false ] && [ "$NGINX_RUNNING" = false ]; then
    echo -e "${YELLOW}ℹ️  No web server detected (Apache/Nginx)${NC}"
fi

# Check ports
echo -e "${YELLOW}🔌 Checking port availability...${NC}"

check_port() {
    local port=$1
    if netstat -tuln 2>/dev/null | grep ":$port " > /dev/null; then
        echo -e "${RED}❌ Port $port is in use${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Port $port is available${NC}"
        return 0
    fi
}

# Check common ports
for port in 80 443 8000 8080 8888 3000; do
    check_port $port
done

# Check current directory and project
echo -e "${YELLOW}📁 Checking project directory...${NC}"
if [ -f "manage.py" ]; then
    echo -e "${GREEN}✅ Django project detected${NC}"
else
    echo -e "${RED}❌ Django project not found (manage.py missing)${NC}"
    echo -e "${YELLOW}   Make sure you're in the project directory${NC}"
fi

# Check Python
echo -e "${YELLOW}🐍 Checking Python...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1)
echo -e "${BLUE}   Python version: $PYTHON_VERSION${NC}"

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo -e "${GREEN}✅ Virtual environment found${NC}"
else
    echo -e "${YELLOW}ℹ️  Virtual environment not found${NC}"
fi

# Recommendations
echo ""
echo -e "${BLUE}📋 Recommendations:${NC}"
echo -e "${BLUE}==================${NC}"

if [ "$APACHE_RUNNING" = true ] || [ "$NGINX_RUNNING" = true ]; then
    echo -e "${GREEN}🌐 Web server detected - Domain-based setup:${NC}"
    echo -e "${YELLOW}   1. Configure web server to proxy to Django${NC}"
    echo -e "${YELLOW}   2. Run Django on internal port (8000)${NC}"
    echo -e "${YELLOW}   3. Access via: https://checkin.taylaibui.vn${NC}"
    echo ""
    echo -e "${BLUE}📝 Web server configuration needed:${NC}"
    echo -e "${YELLOW}   - Apache: VirtualHost with ProxyPass${NC}"
    echo -e "${YELLOW}   - Nginx: server block with proxy_pass${NC}"
else
    echo -e "${YELLOW}🔧 Direct port access setup:${NC}"
    echo -e "${YELLOW}   1. Run Django on public port${NC}"
    echo -e "${YELLOW}   2. Open firewall port if needed${NC}"
    echo -e "${YELLOW}   3. Access via: http://IP:8000 or http://domain:8000${NC}"
fi

echo ""
echo -e "${BLUE}🚀 Next steps:${NC}"
echo -e "${GREEN}   1. Run setup script: ./deploy/setup-server-py36.sh${NC}"
echo -e "${GREEN}   2. Start server: ./start_server.sh${NC}"

if [ "$APACHE_RUNNING" = true ] || [ "$NGINX_RUNNING" = true ]; then
    echo -e "${GREEN}   3. Configure web server proxy${NC}"
    echo -e "${GREEN}   4. Test: https://checkin.taylaibui.vn${NC}"
else
    echo -e "${GREEN}   3. Test: http://$(hostname -I | awk '{print $1}'):8000${NC}"
fi

echo ""
echo -e "${BLUE}💡 Tips:${NC}"
echo -e "${YELLOW}   - For production: Use web server proxy${NC}"
echo -e "${YELLOW}   - For testing: Direct port access is OK${NC}"
echo -e "${YELLOW}   - Check firewall settings if external access fails${NC}"
