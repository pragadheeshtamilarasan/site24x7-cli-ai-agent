#!/bin/bash

# Site24x7 CLI AI Agent - One-Line Docker Deployment
# For Ubuntu machines

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Site24x7 CLI AI Agent - Docker Deployment${NC}"
echo "=================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${GREEN}✅ Docker installed successfully${NC}"
    echo -e "${YELLOW}⚠️  Please log out and log back in to use Docker without sudo${NC}"
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Docker Compose...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✅ Docker Compose installed successfully${NC}"
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}📝 Creating environment configuration...${NC}"
    
    # Prompt for GitHub credentials
    echo -e "${BLUE}GitHub Configuration Required:${NC}"
    echo "You need a GitHub Personal Access Token to proceed."
    echo "Get one at: https://github.com/settings/tokens"
    echo
    
    read -p "Enter your GitHub username: " GITHUB_USER
    echo -n "Enter your GitHub Personal Access Token: "
    read -s GITHUB_TOKEN
    echo
    
    # Create .env file with user input
    cat > .env << EOF
# Required: GitHub Configuration
GITHUB_PERSONAL_ACCESS_TOKEN=${GITHUB_TOKEN}
GITHUB_USERNAME=${GITHUB_USER}

# Optional: AI Configuration (choose one)
# For OpenAI:
# OPENAI_API_KEY=your_openai_api_key_here

# For Local LLM (OpenAI compatible):
# OPENAI_API_KEY=your_local_llm_api_key
# OPENAI_BASE_URL=http://localhost:3100/v1
# USE_LOCAL_LLM=true

# Application Settings (optional)
SECRET_KEY=auto-generated
SCRAPER_INTERVAL_HOURS=6
MAINTENANCE_INTERVAL_HOURS=24
LOG_LEVEL=INFO
DEBUG=false
EOF
    
    echo -e "${GREEN}✅ Configuration saved to .env file${NC}"
fi

# Create data directory
mkdir -p data

# Build and run the application
echo -e "${BLUE}🔨 Building Docker image...${NC}"
docker-compose build

echo -e "${BLUE}🚀 Starting Site24x7 CLI AI Agent...${NC}"
docker-compose up -d

# Wait for the application to start
echo -e "${YELLOW}⏳ Waiting for application to start...${NC}"
sleep 10

# Check if the application is running
if curl -f http://localhost:5000/api/v1/status > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Site24x7 CLI AI Agent is running successfully!${NC}"
    echo ""
    echo -e "${BLUE}🌐 Access your application:${NC}"
    echo -e "   Dashboard: ${GREEN}http://localhost:5000${NC}"
    echo -e "   Configuration: ${GREEN}http://localhost:5000/config${NC}"
    echo -e "   Logs: ${GREEN}http://localhost:5000/logs${NC}"
    echo ""
    echo -e "${BLUE}📊 Docker management commands:${NC}"
    echo -e "   View logs: ${YELLOW}docker-compose logs -f${NC}"
    echo -e "   Stop application: ${YELLOW}docker-compose down${NC}"
    echo -e "   Restart application: ${YELLOW}docker-compose restart${NC}"
    echo -e "   Update application: ${YELLOW}docker-compose pull && docker-compose up -d${NC}"
else
    echo -e "${RED}❌ Failed to start the application${NC}"
    echo -e "${YELLOW}📋 Check logs with: docker-compose logs${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"