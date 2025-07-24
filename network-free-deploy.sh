#!/bin/bash

# Network-Free Deployment - Works without external package downloads
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Site24x7 CLI AI Agent - Network-Free Deploy${NC}"
echo "=================================================="
echo -e "${YELLOW}This deployment works without external package downloads${NC}"
echo

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
docker-compose -f docker-compose.minimal.yml down 2>/dev/null || true

# Create network-free .env file
echo -e "${BLUE}📝 Creating network-free configuration...${NC}"
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
GIT_PYTHON_REFRESH=quiet
GIT_PYTHON_GIT_EXECUTABLE=/usr/bin/true
EOF

# Create data directory
mkdir -p data

# Build without network dependencies
echo -e "${BLUE}🔨 Building application (no external package downloads)...${NC}"
echo -e "${YELLOW}This avoids corporate network restrictions by not installing system packages${NC}"

if ! docker-compose -f docker-compose.no-network.yml build --no-cache; then
    echo -e "${RED}❌ Network-free build failed${NC}"
    echo -e "${YELLOW}Trying alternative: Pre-built Python dependencies${NC}"
    
    # Fallback: Use the existing minimal build but with git disabled
    export GIT_PYTHON_REFRESH=quiet
    export GIT_PYTHON_GIT_EXECUTABLE=/usr/bin/true
    
    if docker-compose -f docker-compose.minimal.yml build --no-cache; then
        COMPOSE_FILE="docker-compose.minimal.yml"
        echo -e "${GREEN}✅ Fallback build successful${NC}"
    else
        echo -e "${RED}❌ All builds failed due to network restrictions${NC}"
        echo -e "${YELLOW}Your corporate network blocks both Debian and PyPI package downloads${NC}"
        exit 1
    fi
else
    COMPOSE_FILE="docker-compose.no-network.yml"
    echo -e "${GREEN}✅ Network-free build successful${NC}"
fi

echo -e "${BLUE}🚀 Starting application...${NC}"
docker-compose -f "$COMPOSE_FILE" up -d

# Extended startup wait for network-restricted environments
echo -e "${YELLOW}⏳ Waiting for startup (45 seconds for network-restricted environment)...${NC}"
sleep 45

# Test connectivity without proxy interference
echo -e "${BLUE}🌐 Testing application...${NC}"
unset http_proxy HTTP_PROXY https_proxy HTTPS_PROXY

# Comprehensive testing
SUCCESS=false
for i in {1..5}; do
    echo "Test attempt $i/5..."
    
    # Check container status
    CONTAINER_STATUS=$(docker inspect site24x7-cli-agent --format='{{.State.Status}}' 2>/dev/null || echo "not_found")
    echo "Container status: $CONTAINER_STATUS"
    
    if [ "$CONTAINER_STATUS" = "running" ]; then
        # Test internal container health
        echo "Testing internal application health..."
        if docker exec site24x7-cli-agent python -c "
import sys
try:
    import requests
    response = requests.get('http://127.0.0.1:5000/api/v1/status', timeout=5)
    print('SUCCESS' if response.status_code == 200 else f'HTTP_{response.status_code}')
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
                echo -e "${YELLOW}⚠️  External access blocked (likely corporate proxy)${NC}"
                SUCCESS=true
                EXTERNAL_ACCESS=false
            fi
            break
        else
            echo "Application not responding yet, waiting..."
            docker-compose -f "$COMPOSE_FILE" logs --tail=5
        fi
    else
        echo "Container not running, checking logs..."
        docker-compose -f "$COMPOSE_FILE" logs --tail=10
    fi
    
    if [ $i -lt 5 ]; then
        echo "Waiting 15 seconds before next attempt..."
        sleep 15
    fi
done

# Show final results
echo
echo "=================================================="
if [ "$SUCCESS" = true ]; then
    echo -e "${GREEN}🎉 DEPLOYMENT SUCCESSFUL!${NC}"
    echo
    echo -e "${BLUE}🌐 Application Access:${NC}"
    
    if [ "$EXTERNAL_ACCESS" = true ]; then
        echo -e "   ✅ Dashboard: ${GREEN}http://localhost:5000${NC}"
        echo -e "   ✅ Configuration: ${GREEN}http://localhost:5000/config${NC}"
        echo -e "   ✅ Logs: ${GREEN}http://localhost:5000/logs${NC}"
        echo
        echo -e "${YELLOW}📝 Next Steps:${NC}"
        echo "1. Open http://localhost:5000 in your browser"
        echo "2. Configure your GitHub token at /config"
        echo "3. Optionally configure AI settings"
    else
        echo -e "${YELLOW}📋 Corporate Network Setup:${NC}"
        echo "Application is running but external access is blocked by your corporate proxy."
        echo
        echo -e "${BLUE}🔧 Access Solutions:${NC}"
        echo "1. Configure browser proxy bypass for localhost:5000"
        echo "2. Add 'localhost' to your proxy exceptions"
        echo "3. Try direct access: http://localhost:5000"
        echo "4. Contact IT for localhost proxy whitelist"
        echo
        echo -e "${GREEN}✅ The application is working correctly inside Docker${NC}"
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
    echo "Container Status: $(docker inspect site24x7-cli-agent --format='{{.State.Status}}' 2>/dev/null || echo 'not found')"
    echo
    echo -e "${BLUE}📋 Recent Logs:${NC}"
    docker-compose -f "$COMPOSE_FILE" logs --tail=20
    echo
    echo -e "${YELLOW}💡 This might be due to:${NC}"
    echo "1. Extreme network restrictions blocking all external access"
    echo "2. Docker daemon issues"
    echo "3. Port conflicts"
    echo
    echo -e "${BLUE}🔧 Try These Steps:${NC}"
    echo "1. Check available ports: sudo netstat -tulpn | grep :5000"
    echo "2. Try different port: Edit docker-compose files to use port 8080"
    echo "3. Check Docker: docker --version && docker ps"
fi

echo
echo -e "${GREEN}🎯 Network-Free Deployment Complete!${NC}"