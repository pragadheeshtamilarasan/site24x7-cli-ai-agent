#!/bin/bash

# Site24x7 CLI AI Agent - Network-Resilient Deployment
# Handles corporate networks and connectivity issues

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Site24x7 CLI AI Agent - Network-Resilient Deploy${NC}"
echo "======================================================="

# Check if we're in the project directory
if [ ! -f "main.py" ]; then
    echo -e "${BLUE}📥 Downloading project...${NC}"
    git clone https://github.com/pragadheeshtamilarasan/site24x7-cli-ai-agent.git || {
        echo -e "${RED}❌ Failed to clone repository - check network connectivity${NC}"
        exit 1
    }
    cd site24x7-cli-ai-agent
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh || {
        echo -e "${RED}❌ Failed to download Docker installer - check network connectivity${NC}"
        exit 1
    }
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${GREEN}✅ Docker installed${NC}"
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Docker Compose...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose || {
        echo -e "${RED}❌ Failed to download Docker Compose - check network connectivity${NC}"
        exit 1
    }
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✅ Docker Compose installed${NC}"
fi

# Create minimal .env file
echo -e "${BLUE}📝 Creating default configuration...${NC}"
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
LOG_LEVEL=INFO
DEBUG=false
EOF

# Create data directory
mkdir -p data

# Try different build strategies
echo -e "${BLUE}🔨 Building application (trying multiple strategies)...${NC}"

# Strategy 1: Minimal build without external system dependencies
echo -e "${YELLOW}Strategy 1: Minimal build (no git/curl dependency)${NC}"
if docker-compose -f docker-compose.minimal.yml build --no-cache; then
    COMPOSE_FILE="docker-compose.minimal.yml"
    echo -e "${GREEN}✅ Minimal build successful${NC}"
elif command -v python3 &> /dev/null && python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
    # Strategy 2: Native Python deployment
    echo -e "${YELLOW}Strategy 2: Native Python deployment${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install fastapi uvicorn pydantic pydantic-settings python-multipart
    pip install jinja2 openai requests beautifulsoup4 trafilatura
    pip install pygithub apscheduler gitpython
    
    echo -e "${GREEN}✅ Native Python setup complete${NC}"
    echo -e "${BLUE}🚀 Starting Site24x7 CLI AI Agent...${NC}"
    
    # Start in background
    nohup python3 main.py > app.log 2>&1 &
    APP_PID=$!
    
    # Wait for startup
    echo -e "${YELLOW}⏳ Starting up...${NC}"
    sleep 15
    
    if curl -f http://localhost:5000/api/v1/status > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Application is running (Native Python)!${NC}"
        echo
        echo -e "${BLUE}🌐 Configure your application:${NC}"
        echo -e "   Configuration: ${GREEN}http://localhost:5000/config${NC}"
        echo -e "   Dashboard: ${GREEN}http://localhost:5000${NC}"
        echo -e "   Logs: ${GREEN}http://localhost:5000/logs${NC}"
        echo
        echo -e "${BLUE}📊 Management commands:${NC}"
        echo -e "   View logs: ${YELLOW}tail -f app.log${NC}"
        echo -e "   Stop: ${YELLOW}kill $APP_PID${NC}"
        echo -e "   Process ID: ${YELLOW}$APP_PID${NC}"
        echo
        echo -e "${GREEN}🎉 Deployment complete! Configure via web UI.${NC}"
        exit 0
    else
        echo -e "${RED}❌ Native Python deployment failed${NC}"
        kill $APP_PID 2>/dev/null || true
    fi
else
    echo -e "${RED}❌ All build strategies failed${NC}"
    echo -e "${YELLOW}This appears to be a network connectivity issue.${NC}"
    echo -e "${YELLOW}Possible solutions:${NC}"
    echo "1. Check your internet connection"
    echo "2. Try from a different network"
    echo "3. Contact your network administrator about Docker Hub access"
    echo "4. Use a VPN if behind corporate firewall"
    exit 1
fi

# Continue with Docker if minimal build succeeded
if [ -n "$COMPOSE_FILE" ]; then
    echo -e "${BLUE}🚀 Starting Site24x7 CLI AI Agent...${NC}"
    docker-compose -f "$COMPOSE_FILE" up -d
    
    # Wait for startup
    echo -e "${YELLOW}⏳ Starting up...${NC}"
    sleep 15
    
    if curl -f http://localhost:5000/api/v1/status > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Application is running!${NC}"
        echo
        echo -e "${BLUE}🌐 Configure your application:${NC}"
        echo -e "   Configuration: ${GREEN}http://localhost:5000/config${NC}"
        echo -e "   Dashboard: ${GREEN}http://localhost:5000${NC}"
        echo -e "   Logs: ${GREEN}http://localhost:5000/logs${NC}"
        echo
        echo -e "${BLUE}📊 Management commands:${NC}"
        echo -e "   View logs: ${YELLOW}docker-compose -f $COMPOSE_FILE logs -f${NC}"
        echo -e "   Stop: ${YELLOW}docker-compose -f $COMPOSE_FILE down${NC}"
        echo -e "   Restart: ${YELLOW}docker-compose -f $COMPOSE_FILE restart${NC}"
        echo
        echo -e "${GREEN}🎉 Deployment complete! Configure via web UI.${NC}"
    else
        echo -e "${RED}❌ Application failed to start${NC}"
        echo -e "${YELLOW}Check logs: docker-compose -f $COMPOSE_FILE logs${NC}"
        exit 1
    fi
fi