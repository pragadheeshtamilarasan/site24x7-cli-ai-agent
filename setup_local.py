#!/usr/bin/env python3
"""
Site24x7 CLI AI Agent - Local Setup Script
Automates the local deployment process
"""

import os
import sys
import subprocess
import secrets
from pathlib import Path

def check_python_version():
    """Check if Python 3.11+ is installed"""
    if sys.version_info < (3, 11):
        print("❌ Python 3.11 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_dependencies():
    """Install required Python packages"""
    packages = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0", 
        "pydantic==2.5.0",
        "pydantic-settings==2.1.0",
        "python-multipart==0.0.6",
        "jinja2==3.1.2",
        "openai==1.3.7",
        "requests==2.31.0",
        "beautifulsoup4==4.12.2",
        "trafilatura==1.6.3",
        "pygithub==2.1.1",
        "apscheduler==3.10.4",
        "gitpython==3.1.40"
    ]
    
    print("📦 Installing dependencies...")
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ Installed {package.split('==')[0]}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    return True

def create_env_file():
    """Create .env file with user input"""
    env_path = Path(".env")
    
    if env_path.exists():
        response = input("⚠️  .env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("📁 Using existing .env file")
            return True
    
    print("🔧 Setting up environment configuration...")
    print("Please provide the following information:")
    
    # Required settings
    github_token = input("GitHub Personal Access Token (required): ").strip()
    if not github_token:
        print("❌ GitHub token is required")
        return False
    
    github_username = input("GitHub Username (required): ").strip()
    if not github_username:
        print("❌ GitHub username is required") 
        return False
    
    # Optional settings
    openai_key = input("OpenAI API Key (optional, press Enter to skip): ").strip()
    
    # Generate secret key
    secret_key = secrets.token_urlsafe(32)
    
    # Create .env content
    env_content = f"""# Site24x7 CLI AI Agent Configuration

# Database
DATABASE_URL=sqlite:///site24x7_agent.db

# Required: GitHub Configuration
GITHUB_PERSONAL_ACCESS_TOKEN={github_token}
GITHUB_USERNAME={github_username}
GITHUB_REPO_NAME=site24x7-cli

# Site24x7 Configuration - Public documentation scraping (no authentication needed)
SITE24X7_API_BASE=https://www.site24x7.com/api/
SITE24X7_DOCS_URL=https://www.site24x7.com/help/api/

# OpenAI Configuration (AI features disabled without this)
{f'OPENAI_API_KEY={openai_key}' if openai_key else '# OPENAI_API_KEY=your_key_here'}
OPENAI_MODEL=gpt-4o

# Scheduler Configuration
SCRAPER_INTERVAL_HOURS=6
MAINTENANCE_INTERVAL_HOURS=24

# Security
SECRET_KEY={secret_key}

# Logging
LOG_LEVEL=INFO
DEBUG=false
"""
    
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        print("✅ Environment file created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def check_required_files():
    """Check if all required project files exist"""
    required_files = [
        "main.py",
        "config.py", 
        "database.py",
        "services/scheduler.py",
        "services/ai_analyzer.py",
        "services/api_scraper.py",
        "services/cli_generator.py",
        "services/github_manager.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    print("✅ All required project files found")
    return True

def create_startup_script():
    """Create startup script for easy running"""
    if os.name == 'nt':  # Windows
        script_content = """@echo off
echo Starting Site24x7 CLI AI Agent...
python main.py
pause
"""
        script_name = "start.bat" 
    else:  # Unix/Linux/macOS
        script_content = """#!/bin/bash
echo "Starting Site24x7 CLI AI Agent..."
python main.py
"""
        script_name = "start.sh"
    
    try:
        with open(script_name, 'w') as f:
            f.write(script_content)
        
        if os.name != 'nt':
            os.chmod(script_name, 0o755)  # Make executable
            
        print(f"✅ Startup script created: {script_name}")
        return True
    except Exception as e:
        print(f"❌ Failed to create startup script: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Site24x7 CLI AI Agent - Local Setup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Check required files
    if not check_required_files():
        print("\n❌ Setup failed: Missing required project files")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed: Could not install dependencies")
        sys.exit(1)
    
    # Create environment file
    if not create_env_file():
        print("\n❌ Setup failed: Could not create environment configuration")
        sys.exit(1)
    
    # Create startup script
    create_startup_script()
    
    print("=" * 50)
    print("🎉 Setup completed successfully!")
    print()
    print("Next steps:")
    print("1. Review your .env file and update any settings as needed")
    print("2. Start the application with: python main.py")
    print("3. Or use the startup script: ./start.sh (Linux/macOS) or start.bat (Windows)")
    print("4. Access the dashboard at: http://localhost:5000")
    print()
    print("For detailed documentation, see:")
    print("- README.md - Quick start guide")
    print("- DEPLOYMENT.md - Comprehensive deployment guide")

if __name__ == "__main__":
    main()