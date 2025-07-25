#!/bin/bash

# Site24x7 CLI AI Agent - Mac Deployment Script
# Simple deployment for local Mac development

set -e

echo "🚀 Site24x7 CLI AI Agent - Mac Deployment"
echo "========================================="

# Check for uninstall option
if [ "$1" = "uninstall" ] || [ "$1" = "--uninstall" ] || [ "$1" = "-u" ]; then
    echo "🗑️  Uninstalling Site24x7 CLI AI Agent..."
    echo ""
    
    # Stop and remove Docker container if exists
    if command -v docker &> /dev/null; then
        if docker ps -a --format "table {{.Names}}" | grep -q "site24x7-cli-ai-agent"; then
            echo "Stopping and removing Docker container..."
            docker stop site24x7-cli-ai-agent 2>/dev/null || true
            docker rm site24x7-cli-ai-agent 2>/dev/null || true
            echo "✅ Docker container removed"
        fi
        
        if docker images --format "table {{.Repository}}" | grep -q "site24x7-cli-ai-agent"; then
            echo "Removing Docker image..."
            docker rmi site24x7-cli-ai-agent 2>/dev/null || true
            echo "✅ Docker image removed"
        fi
    fi
    
    # Remove virtual environment
    if [ -d "venv" ]; then
        echo "Removing Python virtual environment..."
        rm -rf venv
        echo "✅ Virtual environment removed"
    fi
    
    # Remove database and logs
    if [ -f "site24x7_agent.db" ]; then
        echo "Removing database..."
        rm -f site24x7_agent.db
        echo "✅ Database removed"
    fi
    
    if [ -f "site24x7_agent.log" ]; then
        echo "Removing log files..."
        rm -f site24x7_agent.log
        echo "✅ Log files removed"
    fi
    
    # Remove __pycache__ directories
    if [ -d "__pycache__" ]; then
        echo "Cleaning up cache files..."
        find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
        find . -name "*.pyc" -delete 2>/dev/null || true
        echo "✅ Cache files cleaned"
    fi
    
    echo ""
    echo "🎉 Site24x7 CLI AI Agent uninstalled successfully!"
    echo ""
    echo "To completely remove the project:"
    echo "  cd .."
    echo "  rm -rf site24x7-cli-ai-agent"
    echo ""
    exit 0
fi

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
echo "3) Uninstall Site24x7 CLI AI Agent"
echo ""

if [ "$DOCKER_AVAILABLE" = true ]; then
    read -p "Enter choice (1, 2, or 3): " choice
else
    read -p "Enter choice (2 for Python venv, 3 for uninstall): " choice
fi

case $choice in
    1)
        if [ "$DOCKER_AVAILABLE" = true ]; then
            echo ""
            echo "🐳 Using Docker deployment..."
            
            # Build and run with Docker
            echo "Building Docker image..."
            if ! docker build -t site24x7-cli-ai-agent .; then
                echo "❌ Docker build failed"
                exit 1
            fi
            
            echo "Starting container..."
            # Stop and remove existing container if it exists
            docker stop site24x7-cli-ai-agent 2>/dev/null || true
            docker rm site24x7-cli-ai-agent 2>/dev/null || true
            
            if ! docker run -d \
                --name site24x7-cli-ai-agent \
                -p 8080:8080 \
                --restart unless-stopped \
                site24x7-cli-ai-agent; then
                echo "❌ Failed to start container"
                exit 1
            fi
            
            echo ""
            echo "✅ Docker deployment complete!"
            echo "🌐 Application running at: http://localhost:8080"
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
            if [ $? -ne 0 ]; then
                echo "❌ Failed to create virtual environment"
                exit 1
            fi
        fi
        
        # Activate virtual environment
        echo "Activating virtual environment..."
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate
        else
            echo "❌ Virtual environment activation failed"
            exit 1
        fi
        
        # Install dependencies
        echo "Installing dependencies..."
        python -m pip install --upgrade pip
        python -m pip install fastapi "uvicorn[standard]" pydantic pydantic-settings jinja2 python-multipart requests beautifulsoup4 trafilatura openai pygithub gitpython apscheduler
        
        # Start the application
        echo ""
        echo "🚀 Starting Site24x7 CLI AI Agent..."
        echo ""
        echo "✅ Application starting..."
        echo "🌐 Application will be available at: http://localhost:8080"
        echo ""
        echo "Press Ctrl+C to stop the application"
        echo ""
        
        python main.py
        ;;
    3)
        # Call uninstall function
        exec "$0" uninstall
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac