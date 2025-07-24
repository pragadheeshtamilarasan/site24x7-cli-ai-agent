#!/bin/bash

# Ultra Minimal Deployment - Handles corporate networks with git dependency
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Site24x7 CLI AI Agent - Ultra Minimal Deploy${NC}"
echo "=================================================="

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
docker-compose -f docker-compose.minimal.yml down 2>/dev/null || true

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
GIT_PYTHON_REFRESH=quiet
EOF

# Create data directory
mkdir -p data

# Build with updated Dockerfile
echo -e "${BLUE}🔨 Building application with git support...${NC}"
docker-compose -f docker-compose.minimal.yml build --no-cache

echo -e "${BLUE}🚀 Starting application...${NC}"
docker-compose -f docker-compose.minimal.yml up -d

# Wait for container startup
echo -e "${YELLOW}⏳ Waiting for startup (30 seconds)...${NC}"
sleep 30

# Test connectivity
echo -e "${BLUE}🌐 Testing application...${NC}"
unset http_proxy HTTP_PROXY https_proxy HTTPS_PROXY

# Multiple test attempts
for i in {1..3}; do
    echo "Test attempt $i..."
    
    # Check container status
    CONTAINER_STATUS=$(docker inspect site24x7-cli-agent --format='{{.State.Status}}' 2>/dev/null || echo "not_found")
    echo "Container status: $CONTAINER_STATUS"
    
    if [ "$CONTAINER_STATUS" = "running" ]; then
        # Test from inside container
        if docker exec site24x7-cli-agent python -c "import requests; print('SUCCESS' if requests.get('http://127.0.0.1:5000/api/v1/status', timeout=5).status_code == 200 else 'FAIL')" 2>/dev/null | grep -q "SUCCESS"; then
            echo -e "${GREEN}✅ Application is running inside container!${NC}"
            
            # Test external access
            if curl -s --connect-timeout 5 --max-time 10 http://localhost:5000/api/v1/status > /dev/null 2>&1; then
                echo -e "${GREEN}✅ External access working!${NC}"
                APP_STATUS="fully_working"
            else
                echo -e "${YELLOW}⚠️  Application running but external access blocked by proxy${NC}"
                APP_STATUS="internal_only"
            fi
            break
        else
            echo "Internal test failed, waiting 10 seconds..."
            sleep 10
        fi
    else
        echo "Container not running, checking logs..."
        docker-compose -f docker-compose.minimal.yml logs --tail=10
        sleep 10
    fi
    
    if [ $i -eq 3 ]; then
        APP_STATUS="failed"
    fi
done

# Show results
if [ "$APP_STATUS" = "fully_working" ]; then
    echo
    echo -e "${GREEN}🎉 DEPLOYMENT SUCCESSFUL!${NC}"
    echo -e "${BLUE}🌐 Access your application:${NC}"
    echo -e "   Dashboard: ${GREEN}http://localhost:5000${NC}"
    echo -e "   Configuration: ${GREEN}http://localhost:5000/config${NC}"
    echo -e "   Logs: ${GREEN}http://localhost:5000/logs${NC}"
    
elif [ "$APP_STATUS" = "internal_only" ]; then
    echo
    echo -e "${GREEN}🎉 APPLICATION IS RUNNING!${NC}"
    echo -e "${YELLOW}📋 Corporate Network Notice:${NC}"
    echo "Application is running inside Docker but external access is blocked by your corporate proxy."
    echo
    echo -e "${BLUE}🌐 Access Solutions:${NC}"
    echo "1. Configure your browser to bypass proxy for localhost:5000"
    echo "2. Add localhost to your proxy bypass list"
    echo "3. Try accessing directly: http://localhost:5000"
    echo "4. Contact IT to whitelist localhost in proxy settings"
    
else
    echo
    echo -e "${RED}❌ DEPLOYMENT FAILED${NC}"
    echo -e "${BLUE}📋 Debug Information:${NC}"
    docker-compose -f docker-compose.minimal.yml ps
    echo
    echo -e "${BLUE}📋 Application Logs:${NC}"
    docker-compose -f docker-compose.minimal.yml logs --tail=20
fi

echo
echo -e "${BLUE}📊 Management Commands:${NC}"
echo -e "   View logs: ${YELLOW}docker-compose -f docker-compose.minimal.yml logs -f${NC}"
echo -e "   Stop: ${YELLOW}docker-compose -f docker-compose.minimal.yml down${NC}"
echo -e "   Restart: ${YELLOW}docker-compose -f docker-compose.minimal.yml restart${NC}"
echo -e "   Status: ${YELLOW}docker-compose -f docker-compose.minimal.yml ps${NC}"