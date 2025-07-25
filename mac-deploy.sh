#!/bin/bash

# Site24x7 CLI AI Agent - Mac Deployment Script
# Simple deployment for local Mac development

set -e

echo "🚀 Site24x7 CLI AI Agent - Mac Deployment"
echo "========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    echo "   Please install Python 3 from https://python.org"
    exit 1
fi

# Check if Docker is installed (optional)
if command -v docker &> /dev/null; then
    echo "✅ Docker found - you can use Docker deployment"
    DOCKER_AVAILABLE=true
else
    echo "ℹ️  Docker not found - using Python virtual environment"
    DOCKER_AVAILABLE=false
fi

echo ""
echo "Choose deployment method:"
echo "1) Docker (recommended if Docker is installed)"
echo "2) Python virtual environment"
echo ""

if [ "$DOCKER_AVAILABLE" = true ]; then
    read -p "Enter choice (1 or 2): " choice
else
    choice=2
    echo "Using Python virtual environment (Docker not available)"
fi

case $choice in
    1)
        if [ "$DOCKER_AVAILABLE" = true ]; then
            echo ""
            echo "🐳 Using Docker deployment..."
            
            # Build and run with Docker
            echo "Building Docker image..."
            docker build -t site24x7-cli-ai-agent .
            
            echo "Starting container..."
            docker run -d \
                --name site24x7-cli-ai-agent \
                -p 5000:5000 \
                --restart unless-stopped \
                site24x7-cli-ai-agent
            
            echo ""
            echo "✅ Docker deployment complete!"
            echo "🌐 Application running at: http://localhost:5000"
            echo ""
            echo "Useful commands:"
            echo "  View logs: docker logs site24x7-cli-ai-agent"
            echo "  Stop: docker stop site24x7-cli-ai-agent"
            echo "  Start: docker start site24x7-cli-ai-agent"
            echo "  Remove: docker rm -f site24x7-cli-ai-agent"
        else
            echo "❌ Docker not available"
            exit 1
        fi
        ;;
    2)
        echo ""
        echo "🐍 Using Python virtual environment..."
        
        # Create virtual environment
        if [ ! -d "venv" ]; then
            echo "Creating virtual environment..."
            python3 -m venv venv
        fi
        
        # Activate virtual environment
        echo "Activating virtual environment..."
        source venv/bin/activate
        
        # Install dependencies
        echo "Installing dependencies..."
        pip install --upgrade pip
        pip install -r <(grep -v "^-e" requirements.txt 2>/dev/null || echo "
fastapi
uvicorn[standard]
pydantic
pydantic-settings
jinja2
python-multipart
requests
beautifulsoup4
trafilatura
openai
pygithub
gitpython
apscheduler
")
        
        # Start the application
        echo ""
        echo "🚀 Starting Site24x7 CLI AI Agent..."
        echo ""
        echo "✅ Application starting..."
        echo "🌐 Application will be available at: http://localhost:5000"
        echo ""
        echo "Press Ctrl+C to stop the application"
        echo ""
        
        python main.py
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac