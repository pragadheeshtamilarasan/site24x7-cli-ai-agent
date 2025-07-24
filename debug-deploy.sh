#!/bin/bash

# Debug deployment script to check what's actually happening

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Debug Site24x7 CLI AI Agent Deployment${NC}"
echo "=============================================="

# Check if we're in the project directory
if [ ! -f "main.py" ]; then
    echo -e "${BLUE}📥 Downloading project...${NC}"
    git clone https://github.com/pragadheeshtamilarasan/site24x7-cli-ai-agent.git || {
        echo -e "${RED}❌ Failed to clone repository${NC}"
        exit 1
    }
    cd site24x7-cli-ai-agent
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
LOG_LEVEL=INFO
DEBUG=false
EOF

# Create data directory
mkdir -p data

# Try to build and start with detailed output
echo -e "${BLUE}🔨 Building application...${NC}"
if docker-compose -f docker-compose.minimal.yml build --no-cache; then
    echo -e "${GREEN}✅ Build successful${NC}"
    
    echo -e "${BLUE}🚀 Starting application...${NC}"
    docker-compose -f docker-compose.minimal.yml up -d
    
    echo -e "${BLUE}📊 Container status:${NC}"
    docker-compose -f docker-compose.minimal.yml ps
    
    echo -e "${BLUE}📋 Application logs:${NC}"
    docker-compose -f docker-compose.minimal.yml logs --tail=50
    
    echo -e "${BLUE}🔍 Port check:${NC}"
    if command -v ss >/dev/null 2>&1; then
        ss -tulpn | grep :5000 || echo "Port 5000 not found"
    elif command -v netstat >/dev/null 2>&1; then
        netstat -tulpn | grep :5000 || echo "Port 5000 not found"
    else
        echo "No port checking tools available"
    fi
    
    echo -e "${BLUE}🌐 Testing connectivity:${NC}"
    for i in {1..5}; do
        echo "Attempt $i:"
        if command -v curl >/dev/null 2>&1; then
            curl -v http://localhost:5000/api/v1/status 2>&1 || echo "Curl failed"
        elif command -v wget >/dev/null 2>&1; then
            wget -v -O- http://localhost:5000/api/v1/status 2>&1 || echo "Wget failed"
        else
            echo "No HTTP client tools available"
        fi
        echo "---"
        sleep 3
    done
    
    echo -e "${BLUE}🔧 Container inspection:${NC}"
    docker inspect site24x7-cli-agent | grep -A 5 -B 5 "IPAddress\|Health\|Status"
    
else
    echo -e "${RED}❌ Build failed${NC}"
    echo -e "${BLUE}📋 Build logs:${NC}"
    docker-compose -f docker-compose.minimal.yml build --no-cache
fi

echo -e "${BLUE}📚 Next steps:${NC}"
echo "If the application is running in the container but not accessible:"
echo "1. Check if port 5000 is already in use"
echo "2. Try a different port by editing docker-compose.minimal.yml"
echo "3. Check firewall settings"
echo "4. Try accessing from inside the container:"
echo "   docker exec -it site24x7-cli-agent curl http://localhost:5000/api/v1/status"