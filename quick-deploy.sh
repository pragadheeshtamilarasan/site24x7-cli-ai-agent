#!/bin/bash

# Site24x7 CLI AI Agent - Quick Interactive Deployment
# For Ubuntu machines - Interactive setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Site24x7 CLI AI Agent - Quick Deploy${NC}"
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

# Interactive configuration
echo -e "${BLUE}📝 Configuration Setup${NC}"
echo "Enter your GitHub credentials (required):"

read -p "GitHub Username: " GITHUB_USER
while [ -z "$GITHUB_USER" ]; do
    echo -e "${RED}GitHub username is required${NC}"
    read -p "GitHub Username: " GITHUB_USER
done

echo -n "GitHub Personal Access Token: "
read -s GITHUB_TOKEN
echo
while [ -z "$GITHUB_TOKEN" ]; do
    echo -e "${RED}GitHub token is required${NC}"
    echo -n "GitHub Personal Access Token: "
    read -s GITHUB_TOKEN
    echo
done

# Optional AI configuration
echo
echo -e "${YELLOW}AI Configuration (Optional):${NC}"
echo "1) Skip (no AI features)"
echo "2) OpenAI API"
echo "3) Local LLM (OpenAI compatible)"
read -p "Choose option (1-3): " AI_CHOICE

AI_CONFIG=""
case $AI_CHOICE in
    2)
        echo -n "OpenAI API Key: "
        read -s OPENAI_KEY
        echo
        AI_CONFIG="OPENAI_API_KEY=${OPENAI_KEY}"
        ;;
    3)
        echo -n "Local LLM API Key: "
        read -s LOCAL_KEY
        echo
        read -p "Local LLM Base URL (e.g., http://localhost:3100/v1): " LOCAL_URL
        AI_CONFIG="OPENAI_API_KEY=${LOCAL_KEY}
OPENAI_BASE_URL=${LOCAL_URL}
USE_LOCAL_LLM=true"
        ;;
    *)
        echo -e "${YELLOW}Skipping AI configuration - features will be disabled${NC}"
        ;;
esac

# Create .env file
cat > .env << EOF
# GitHub Configuration
GITHUB_PERSONAL_ACCESS_TOKEN=${GITHUB_TOKEN}
GITHUB_USERNAME=${GITHUB_USER}

# AI Configuration
${AI_CONFIG}

# Application Settings
SECRET_KEY=auto-generated
SCRAPER_INTERVAL_HOURS=6
MAINTENANCE_INTERVAL_HOURS=24
LOG_LEVEL=INFO
DEBUG=false
EOF

echo -e "${GREEN}✅ Configuration saved${NC}"

# Create data directory
mkdir -p data

# Build and start
echo -e "${BLUE}🔨 Building application...${NC}"
docker-compose build --no-cache

echo -e "${BLUE}🚀 Starting Site24x7 CLI AI Agent...${NC}"
docker-compose up -d

# Wait and verify
echo -e "${YELLOW}⏳ Starting up...${NC}"
sleep 15

if curl -f http://localhost:5000/api/v1/status > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    echo
    echo -e "${BLUE}🌐 Access your application:${NC}"
    echo -e "   Dashboard: ${GREEN}http://localhost:5000${NC}"
    echo -e "   Configuration: ${GREEN}http://localhost:5000/config${NC}"
    echo -e "   Logs: ${GREEN}http://localhost:5000/logs${NC}"
    echo
    echo -e "${BLUE}📊 Management commands:${NC}"
    echo -e "   View logs: ${YELLOW}docker-compose logs -f${NC}"
    echo -e "   Stop: ${YELLOW}docker-compose down${NC}"
    echo -e "   Restart: ${YELLOW}docker-compose restart${NC}"
else
    echo -e "${RED}❌ Deployment failed${NC}"
    echo -e "${YELLOW}Check logs: docker-compose logs${NC}"
    exit 1
fi

echo
echo -e "${GREEN}🎉 Site24x7 CLI AI Agent is running!${NC}"