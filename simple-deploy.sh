#!/bin/bash

# Site24x7 CLI AI Agent - Simple One-Command Deployment
# Run first, configure via web UI

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Site24x7 CLI AI Agent - Simple Deploy${NC}"
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

# Create minimal .env file with no required fields
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

# Build the application (try minimal version first for network issues)
echo -e "${BLUE}🔨 Building application...${NC}"
if ! docker-compose -f docker-compose.minimal.yml build --no-cache; then
    echo -e "${YELLOW}⚠️  Minimal build failed, trying standard build...${NC}"
    docker-compose build --no-cache || {
        echo -e "${RED}❌ Docker build failed due to network connectivity${NC}"
        echo -e "${YELLOW}This might be due to corporate firewall or network restrictions${NC}"
        echo -e "${YELLOW}Try running from a different network or contact your network administrator${NC}"
        exit 1
    }
    COMPOSE_FILE="docker-compose.yml"
else
    COMPOSE_FILE="docker-compose.minimal.yml"
fi

# Start the application
echo -e "${BLUE}🚀 Starting Site24x7 CLI AI Agent...${NC}"
docker-compose -f "$COMPOSE_FILE" up -d

# Wait for startup
echo -e "${YELLOW}⏳ Starting up...${NC}"
sleep 15

# Check if running (try multiple methods)
if command -v curl >/dev/null 2>&1 && curl -f http://localhost:5000/api/v1/status > /dev/null 2>&1; then
    APP_RUNNING=true
elif command -v wget >/dev/null 2>&1 && wget -q --spider http://localhost:5000/api/v1/status; then
    APP_RUNNING=true
elif python3 -c "import requests; requests.get('http://localhost:5000/api/v1/status', timeout=5)" > /dev/null 2>&1; then
    APP_RUNNING=true
else
    APP_RUNNING=false
fi

if [ "$APP_RUNNING" = true ]; then
    echo -e "${GREEN}✅ Application is running!${NC}"
    echo
    echo -e "${BLUE}🌐 Configure your application:${NC}"
    echo -e "   Configuration Page: ${GREEN}http://localhost:5000/config${NC}"
    echo -e "   Dashboard: ${GREEN}http://localhost:5000${NC}"
    echo -e "   Logs: ${GREEN}http://localhost:5000/logs${NC}"
    echo
    echo -e "${YELLOW}📝 Next Steps:${NC}"
    echo "1. Open http://localhost:5000/config in your browser"
    echo "2. Enter your GitHub Personal Access Token and username"
    echo "3. Optionally configure AI settings (OpenAI or Local LLM)"
    echo "4. Save configuration and start using the application"
    echo
    echo -e "${BLUE}📋 To get GitHub token:${NC}"
    echo "Visit: https://github.com/settings/tokens"
    echo "Create token with: repo, workflow, write:packages scopes"
    echo
    echo -e "${BLUE}📊 Management commands:${NC}"
    echo -e "   View logs: ${YELLOW}docker-compose -f $COMPOSE_FILE logs -f${NC}"
    echo -e "   Stop: ${YELLOW}docker-compose -f $COMPOSE_FILE down${NC}"
    echo -e "   Restart: ${YELLOW}docker-compose -f $COMPOSE_FILE restart${NC}"
else
    echo -e "${RED}❌ Application failed to start${NC}"
    echo -e "${YELLOW}📋 Debugging information:${NC}"
    echo -e "   Check logs: ${YELLOW}docker-compose -f $COMPOSE_FILE logs${NC}"
    echo -e "   Container status: ${YELLOW}docker-compose -f $COMPOSE_FILE ps${NC}"
    echo -e "   Port check: ${YELLOW}docker port site24x7-cli-agent${NC}"
    echo
    echo -e "${BLUE}🔍 Quick debug steps:${NC}"
    echo "1. Check container logs: docker-compose -f $COMPOSE_FILE logs"
    echo "2. Check if container is running: docker-compose -f $COMPOSE_FILE ps"
    echo "3. Test from inside container: docker exec -it site24x7-cli-agent curl http://localhost:5000/api/v1/status"
    echo "4. Check port binding: docker port site24x7-cli-agent"
    echo
    echo -e "${YELLOW}For detailed debugging, run:${NC}"
    echo "curl -fsSL https://raw.githubusercontent.com/pragadheeshtamilarasan/site24x7-cli-ai-agent/main/debug-deploy.sh | bash"
    exit 1
fi

echo
echo -e "${GREEN}🎉 Deployment complete! Configure via web UI.${NC}"