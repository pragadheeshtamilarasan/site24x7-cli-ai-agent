#!/bin/bash

# Corporate Network Deployment Script
# Handles proxy environments and network restrictions

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏢 Site24x7 CLI AI Agent - Corporate Network Deploy${NC}"
echo "======================================================"

# Check if we're in the project directory
if [ ! -f "main.py" ]; then
    echo -e "${BLUE}📥 Downloading project...${NC}"
    git clone https://github.com/pragadheeshtamilarasan/site24x7-cli-ai-agent.git || {
        echo -e "${RED}❌ Failed to clone repository${NC}"
        exit 1
    }
    cd site24x7-cli-ai-agent
fi

# Handle proxy settings
if [ -n "$http_proxy" ] || [ -n "$HTTP_PROXY" ]; then
    echo -e "${YELLOW}🌐 Corporate proxy detected: $http_proxy${NC}"
    echo -e "${BLUE}Setting up proxy bypass for localhost...${NC}"
    
    # Set no_proxy for localhost
    export no_proxy="localhost,127.0.0.1,::1,0.0.0.0"
    export NO_PROXY="localhost,127.0.0.1,::1,0.0.0.0"
    
    echo "Added localhost to proxy bypass"
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${GREEN}✅ Docker installed${NC}"
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Docker Compose...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✅ Docker Compose installed${NC}"
fi

# Create minimal .env file
echo -e "${BLUE}📝 Creating configuration...${NC}"
cat > .env << 'EOF'
GITHUB_PERSONAL_ACCESS_TOKEN=
GITHUB_USERNAME=
OPENAI_API_KEY=
OPENAI_BASE_URL=
USE_LOCAL_LLM=false
SECRET_KEY=auto-generated
SCRAPER_INTERVAL_HOURS=6
MAINTENANCE_INTERVAL_HOURS=24
LOG_LEVEL=DEBUG
DEBUG=true
EOF

# Create data directory
mkdir -p data

# Remove version from docker-compose to avoid warnings
if [ -f "docker-compose.minimal.yml" ]; then
    sed -i '/^version:/d' docker-compose.minimal.yml
fi

# Build and start
echo -e "${BLUE}🔨 Building application...${NC}"
docker-compose -f docker-compose.minimal.yml build --no-cache

echo -e "${BLUE}🚀 Starting application...${NC}"
docker-compose -f docker-compose.minimal.yml up -d

# Wait for container to start
echo -e "${YELLOW}⏳ Waiting for container startup...${NC}"
sleep 10

# Check container status
echo -e "${BLUE}📊 Container status:${NC}"
docker-compose -f docker-compose.minimal.yml ps

# Get container logs
echo -e "${BLUE}📋 Recent application logs:${NC}"
docker-compose -f docker-compose.minimal.yml logs --tail=20

# Test connectivity without proxy
echo -e "${BLUE}🌐 Testing application (bypassing proxy)...${NC}"
unset http_proxy
unset HTTP_PROXY
unset https_proxy
unset HTTPS_PROXY

# Wait a bit more for app to fully start
sleep 10

# Multiple connectivity tests
CONTAINER_IP=$(docker inspect site24x7-cli-agent --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}')
echo "Container IP: $CONTAINER_IP"

# Test 1: Direct localhost
echo "Test 1: Testing localhost..."
if curl -s --connect-timeout 5 --max-time 10 http://localhost:5000/api/v1/status > /dev/null 2>&1; then
    APP_STATUS="running"
else
    echo "Localhost test failed"
    APP_STATUS="failed"
fi

# Test 2: Container IP
if [ -n "$CONTAINER_IP" ] && [ "$CONTAINER_IP" != "" ]; then
    echo "Test 2: Testing container IP ($CONTAINER_IP)..."
    if curl -s --connect-timeout 5 --max-time 10 "http://$CONTAINER_IP:5000/api/v1/status" > /dev/null 2>&1; then
        APP_STATUS="running"
    else
        echo "Container IP test failed"
    fi
fi

# Test 3: From inside container
echo "Test 3: Testing from inside container..."
if docker exec site24x7-cli-agent python -c "import requests; print('OK' if requests.get('http://127.0.0.1:5000/api/v1/status', timeout=5).status_code == 200 else 'FAIL')" 2>/dev/null | grep -q "OK"; then
    APP_STATUS="running"
    INTERNAL_ACCESS="yes"
else
    echo "Internal container test failed"
    INTERNAL_ACCESS="no"
fi

if [ "$APP_STATUS" = "running" ]; then
    echo -e "${GREEN}✅ Application is running successfully!${NC}"
    echo
    echo -e "${BLUE}🌐 Access your application:${NC}"
    echo -e "   Dashboard: ${GREEN}http://localhost:5000${NC}"
    echo -e "   Configuration: ${GREEN}http://localhost:5000/config${NC}"
    echo -e "   Logs: ${GREEN}http://localhost:5000/logs${NC}"
    echo
    echo -e "${YELLOW}📝 Next Steps:${NC}"
    echo "1. Open http://localhost:5000 in your web browser"
    echo "2. If browser access fails due to proxy, configure your browser to bypass proxy for localhost"
    echo "3. Configure your GitHub token and settings at /config"
    echo
    echo -e "${BLUE}📊 Management Commands:${NC}"
    echo -e "   View logs: ${YELLOW}docker-compose -f docker-compose.minimal.yml logs -f${NC}"
    echo -e "   Stop: ${YELLOW}docker-compose -f docker-compose.minimal.yml down${NC}"
    echo -e "   Restart: ${YELLOW}docker-compose -f docker-compose.minimal.yml restart${NC}"
else
    echo -e "${RED}❌ Application connectivity issues detected${NC}"
    echo
    echo -e "${BLUE}🔍 Diagnostic Information:${NC}"
    echo "- Container Status: $(docker inspect site24x7-cli-agent --format='{{.State.Status}}')"
    echo "- Internal Access: $INTERNAL_ACCESS"
    echo "- Port Binding: $(docker port site24x7-cli-agent 2>/dev/null || echo 'Not bound')"
    echo
    echo -e "${YELLOW}📋 Troubleshooting Steps:${NC}"
    echo "1. Check container logs: docker-compose -f docker-compose.minimal.yml logs"
    echo "2. Restart container: docker-compose -f docker-compose.minimal.yml restart"
    echo "3. Try different port: Edit docker-compose.minimal.yml to use port 8080"
    echo "4. Check firewall: sudo ufw status"
    echo
    if [ "$INTERNAL_ACCESS" = "yes" ]; then
        echo -e "${GREEN}✅ Application is working inside container${NC}"
        echo -e "${YELLOW}Issue appears to be network/proxy related${NC}"
        echo "Try accessing http://localhost:5000 directly in your browser"
    fi
fi

echo
echo -e "${GREEN}🎉 Deployment completed with corporate network handling!${NC}"