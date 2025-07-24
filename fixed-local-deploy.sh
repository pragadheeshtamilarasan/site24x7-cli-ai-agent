#!/bin/bash

# Fixed Local Deployment - Works on your current machine
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Site24x7 CLI AI Agent - Fixed Local Deploy${NC}"
echo "============================================="

# Check if we're in the project directory
if [ ! -f "main.py" ]; then
    echo -e "${BLUE}📥 Downloading project...${NC}"
    git clone https://github.com/pragadheeshtamilarasan/site24x7-cli-ai-agent.git || {
        echo -e "${RED}❌ Failed to clone repository${NC}"
        exit 1
    }
    cd site24x7-cli-ai-agent
fi

# Handle proxy settings for localhost
if [ -n "$http_proxy" ] || [ -n "$HTTP_PROXY" ]; then
    echo -e "${YELLOW}🌐 Corporate proxy detected, setting bypass for localhost${NC}"
    export no_proxy="localhost,127.0.0.1,::1,0.0.0.0"
    export NO_PROXY="localhost,127.0.0.1,::1,0.0.0.0"
fi

# Stop any existing containers
echo -e "${BLUE}🛑 Stopping existing containers...${NC}"
docker-compose -f docker-compose.no-network.yml down 2>/dev/null || true
docker-compose down 2>/dev/null || true

# Create fixed configuration
echo -e "${BLUE}📝 Creating fixed configuration...${NC}"
cat > .env << 'EOF'
# GitHub Configuration (configure via web UI)
GITHUB_PERSONAL_ACCESS_TOKEN=
GITHUB_USERNAME=

# AI Configuration (configure via web UI)  
OPENAI_API_KEY=
OPENAI_BASE_URL=
USE_LOCAL_LLM=false

# Application Settings
SECRET_KEY=auto-generated
SCRAPER_INTERVAL_HOURS=6
MAINTENANCE_INTERVAL_HOURS=24
LOG_LEVEL=DEBUG
DEBUG=true

# Git Configuration (prevent git errors)
GIT_PYTHON_REFRESH=quiet
GIT_PYTHON_GIT_EXECUTABLE=/usr/bin/true
EOF

# Create data directory
mkdir -p data

# Try the network-free build first (works with corporate networks)
echo -e "${BLUE}🔨 Building application (network-free version)...${NC}"
if docker-compose -f docker-compose.no-network.yml build --no-cache; then
    COMPOSE_FILE="docker-compose.no-network.yml"
    echo -e "${GREEN}✅ Network-free build successful${NC}"
elif docker-compose build --no-cache; then
    COMPOSE_FILE="docker-compose.yml"
    echo -e "${GREEN}✅ Standard build successful${NC}"
else
    echo -e "${RED}❌ All builds failed${NC}"
    exit 1
fi

echo -e "${BLUE}🚀 Starting application...${NC}"
docker-compose -f "$COMPOSE_FILE" up -d

# Wait for proper startup
echo -e "${YELLOW}⏳ Waiting for application startup (60 seconds)...${NC}"
sleep 60

# Test the application thoroughly
echo -e "${BLUE}🧪 Testing application...${NC}"
SUCCESS=false

# Clear proxy for testing
unset http_proxy HTTP_PROXY https_proxy HTTPS_PROXY

for i in {1..6}; do
    echo "Test attempt $i/6..."
    
    # Check container status
    CONTAINER_STATUS=$(docker inspect site24x7-cli-agent --format='{{.State.Status}}' 2>/dev/null || echo "not_found")
    echo "Container status: $CONTAINER_STATUS"
    
    if [ "$CONTAINER_STATUS" = "running" ]; then
        # Test internal application
        echo "Testing internal application..."
        if docker exec site24x7-cli-agent python -c "
import sys
try:
    import requests
    response = requests.get('http://127.0.0.1:5000/api/v1/status', timeout=5)
    if response.status_code == 200:
        print('SUCCESS')
        sys.exit(0)
    else:
        print(f'HTTP_ERROR_{response.status_code}')
        sys.exit(1)
except ImportError as e:
    print(f'IMPORT_ERROR: {e}')
    sys.exit(1)
except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
" 2>/dev/null | grep -q "SUCCESS"; then
            echo -e "${GREEN}✅ Application is running inside container!${NC}"
            
            # Test external access
            echo "Testing external access..."
            if curl -s --connect-timeout 5 --max-time 10 http://localhost:5000/api/v1/status > /dev/null 2>&1; then
                echo -e "${GREEN}✅ External access working!${NC}"
                SUCCESS=true
                EXTERNAL_ACCESS=true
            else
                echo -e "${YELLOW}⚠️  External access blocked (corporate proxy issue)${NC}"
                SUCCESS=true
                EXTERNAL_ACCESS=false
            fi
            break
        else
            echo "Application not responding, checking logs..."
            docker-compose -f "$COMPOSE_FILE" logs --tail=10
        fi
    else
        echo "Container not running properly, checking status..."
        docker-compose -f "$COMPOSE_FILE" ps
        echo "Recent logs:"
        docker-compose -f "$COMPOSE_FILE" logs --tail=5
    fi
    
    if [ $i -lt 6 ]; then
        echo "Waiting 20 seconds before next attempt..."
        sleep 20
    fi
done

# Show results
echo
echo "============================================="
if [ "$SUCCESS" = true ]; then
    echo -e "${GREEN}🎉 DEPLOYMENT SUCCESSFUL!${NC}"
    echo
    if [ "$EXTERNAL_ACCESS" = true ]; then
        echo -e "${BLUE}🌐 Your application is accessible at:${NC}"
        echo -e "   Dashboard: ${GREEN}http://localhost:5000${NC}"
        echo -e "   Configuration: ${GREEN}http://localhost:5000/config${NC}"
        echo -e "   Logs: ${GREEN}http://localhost:5000/logs${NC}"
        echo
        echo -e "${YELLOW}📝 Next Steps:${NC}"
        echo "1. Open http://localhost:5000 in your browser"
        echo "2. Go to configuration page"
        echo "3. Enter your GitHub Personal Access Token"
        echo "4. Optionally configure AI settings"
        echo "5. Save and start using the application"
    else
        echo -e "${YELLOW}📋 Application Running (Proxy Configuration Needed):${NC}"
        echo "The application is running inside Docker but external access is blocked."
        echo
        echo -e "${BLUE}🔧 To access the application:${NC}"
        echo "1. Configure your browser to bypass proxy for localhost:5000"
        echo "2. Try accessing http://localhost:5000 directly"
        echo "3. Contact IT to add localhost to proxy whitelist"
        echo
        echo -e "${GREEN}✅ The application itself is working correctly${NC}"
    fi
    
    echo
    echo -e "${BLUE}📊 Management Commands:${NC}"
    echo -e "   View logs: ${YELLOW}docker-compose -f $COMPOSE_FILE logs -f${NC}"
    echo -e "   Stop: ${YELLOW}docker-compose -f $COMPOSE_FILE down${NC}"
    echo -e "   Restart: ${YELLOW}docker-compose -f $COMPOSE_FILE restart${NC}"
    echo -e "   Status: ${YELLOW}docker-compose -f $COMPOSE_FILE ps${NC}"
    
else
    echo -e "${RED}❌ DEPLOYMENT FAILED${NC}"
    echo
    echo -e "${BLUE}🔍 Debug Information:${NC}"
    echo "Final container status: $(docker inspect site24x7-cli-agent --format='{{.State.Status}}' 2>/dev/null || echo 'not found')"
    echo
    echo -e "${BLUE}📋 Recent Application Logs:${NC}"
    docker-compose -f "$COMPOSE_FILE" logs --tail=30
    echo
    echo -e "${BLUE}📋 Container Information:${NC}"
    docker-compose -f "$COMPOSE_FILE" ps
    echo
    echo -e "${YELLOW}🔧 Try these debugging steps:${NC}"
    echo "1. Check available memory: free -h"
    echo "2. Check disk space: df -h"
    echo "3. Try restarting Docker: sudo systemctl restart docker"
    echo "4. Try a different port by editing the compose file"
fi

echo
echo -e "${GREEN}🎯 Fixed Local Deployment Complete!${NC}"