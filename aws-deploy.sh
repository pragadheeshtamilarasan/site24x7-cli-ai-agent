#!/bin/bash

# AWS Deployment Script for Site24x7 CLI AI Agent
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}☁️  Site24x7 CLI AI Agent - AWS Deployment${NC}"
echo "============================================="
echo "This script deploys the application on AWS EC2"
echo

# Check if running on AWS
if curl -s --connect-timeout 2 --max-time 5 http://169.254.169.254/latest/meta-data/instance-id > /dev/null 2>&1; then
    INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
    AVAILABILITY_ZONE=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)
    INSTANCE_TYPE=$(curl -s http://169.254.169.254/latest/meta-data/instance-type)
    PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
    
    echo -e "${GREEN}✅ Running on AWS EC2${NC}"
    echo "Instance ID: $INSTANCE_ID"
    echo "Instance Type: $INSTANCE_TYPE"
    echo "Availability Zone: $AVAILABILITY_ZONE"
    echo "Public IP: $PUBLIC_IP"
    echo
else
    echo -e "${YELLOW}⚠️  Not running on AWS EC2, proceeding with standard deployment${NC}"
    PUBLIC_IP="localhost"
fi

# Update system packages
echo -e "${BLUE}📦 Updating system packages...${NC}"
sudo apt-get update

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo -e "${BLUE}🐳 Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${GREEN}✅ Docker installed${NC}"
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo -e "${BLUE}📦 Installing Docker Compose...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✅ Docker Compose installed${NC}"
fi

# Clone or update repository
if [ ! -d "site24x7-cli-ai-agent" ]; then
    echo -e "${BLUE}📥 Downloading project...${NC}"
    git clone https://github.com/pragadheeshtamilarasan/site24x7-cli-ai-agent.git
    cd site24x7-cli-ai-agent
else
    echo -e "${BLUE}🔄 Updating existing project...${NC}"
    cd site24x7-cli-ai-agent
    git pull origin main
fi

# Create production environment file
echo -e "${BLUE}📝 Creating production configuration...${NC}"
cat > .env << 'EOF'
# GitHub Configuration (configure via web UI)
GITHUB_PERSONAL_ACCESS_TOKEN=
GITHUB_USERNAME=

# AI Configuration (configure via web UI)
OPENAI_API_KEY=
OPENAI_BASE_URL=
USE_LOCAL_LLM=false

# Production Settings
SECRET_KEY=auto-generated
SCRAPER_INTERVAL_HOURS=6
MAINTENANCE_INTERVAL_HOURS=24
LOG_LEVEL=INFO
DEBUG=false
GIT_PYTHON_REFRESH=quiet
EOF

# Create data directory with proper permissions
mkdir -p data
sudo chown -R $USER:$USER data

# Stop any existing containers
echo -e "${BLUE}🛑 Stopping existing containers...${NC}"
docker-compose down 2>/dev/null || true

# Build and start the application
echo -e "${BLUE}🔨 Building application...${NC}"
docker-compose build --no-cache

echo -e "${BLUE}🚀 Starting application...${NC}"
docker-compose up -d

# Wait for startup
echo -e "${YELLOW}⏳ Waiting for application startup...${NC}"
sleep 20

# Test the application
echo -e "${BLUE}🧪 Testing application...${NC}"
for i in {1..5}; do
    if curl -f http://localhost:5000/api/v1/status > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Application is running!${NC}"
        APP_RUNNING=true
        break
    else
        echo "Attempt $i/5 failed, waiting..."
        sleep 10
    fi
done

if [ "$APP_RUNNING" = true ]; then
    echo
    echo -e "${GREEN}🎉 AWS DEPLOYMENT SUCCESSFUL!${NC}"
    echo "============================================="
    echo
    echo -e "${BLUE}🌐 Access Information:${NC}"
    if [ "$PUBLIC_IP" != "localhost" ]; then
        echo -e "   Public URL: ${GREEN}http://$PUBLIC_IP:5000${NC}"
        echo -e "   Configuration: ${GREEN}http://$PUBLIC_IP:5000/config${NC}"
        echo -e "   Dashboard: ${GREEN}http://$PUBLIC_IP:5000/dashboard${NC}"
        echo -e "   Logs: ${GREEN}http://$PUBLIC_IP:5000/logs${NC}"
        
        # Check security group
        echo
        echo -e "${YELLOW}🔒 Security Group Check:${NC}"
        echo "Ensure your EC2 security group allows inbound traffic on port 5000"
        echo "Required rule: Type: Custom TCP, Port: 5000, Source: 0.0.0.0/0 (or your IP)"
    else
        echo -e "   Local URL: ${GREEN}http://localhost:5000${NC}"
        echo -e "   Configuration: ${GREEN}http://localhost:5000/config${NC}"
        echo -e "   Dashboard: ${GREEN}http://localhost:5000/dashboard${NC}"
        echo -e "   Logs: ${GREEN}http://localhost:5000/logs${NC}"
    fi
    
    echo
    echo -e "${BLUE}📝 Next Steps:${NC}"
    echo "1. Open the configuration page in your browser"
    echo "2. Enter your GitHub Personal Access Token"
    echo "3. Optionally configure AI settings (OpenAI API key)"
    echo "4. Save configuration to start automated CLI generation"
    
    echo
    echo -e "${BLUE}🔧 GitHub Token Setup:${NC}"
    echo "Visit: https://github.com/settings/tokens"
    echo "Create token with scopes: repo, workflow, write:packages"
    
    echo
    echo -e "${BLUE}📊 Management Commands:${NC}"
    echo -e "   View logs: ${YELLOW}docker-compose logs -f${NC}"
    echo -e "   Stop: ${YELLOW}docker-compose down${NC}"
    echo -e "   Restart: ${YELLOW}docker-compose restart${NC}"
    echo -e "   Update: ${YELLOW}git pull && docker-compose up -d --build${NC}"
    
    # AWS-specific information
    if [ "$PUBLIC_IP" != "localhost" ]; then
        echo
        echo -e "${BLUE}☁️  AWS-Specific Notes:${NC}"
        echo "• Application is accessible from the internet via port 5000"
        echo "• Consider setting up a reverse proxy (nginx) for production"
        echo "• Enable HTTPS with Let's Encrypt for secure access"
        echo "• Monitor costs and set up billing alerts"
        echo "• Consider using AWS Secrets Manager for API keys"
    fi
    
else
    echo
    echo -e "${RED}❌ DEPLOYMENT FAILED${NC}"
    echo
    echo -e "${BLUE}🔍 Debug Information:${NC}"
    docker-compose ps
    echo
    echo -e "${BLUE}📋 Application Logs:${NC}"
    docker-compose logs --tail=20
    
    echo
    echo -e "${YELLOW}🔧 Troubleshooting:${NC}"
    echo "1. Check if port 5000 is available: sudo netstat -tulpn | grep :5000"
    echo "2. Verify Docker is running: docker --version && docker ps"
    echo "3. Check logs: docker-compose logs -f"
    echo "4. Try restarting: docker-compose restart"
fi

echo
echo -e "${GREEN}🎯 AWS Deployment Complete!${NC}"