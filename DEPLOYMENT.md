# Site24x7 CLI AI Agent - Deployment Guide

## Overview

The Site24x7 CLI AI Agent is an autonomous system that scrapes Site24x7 API documentation, generates a comprehensive CLI tool, and maintains a GitHub repository automatically. This guide provides complete deployment instructions for local setup.

## Technology Stack

### Backend Framework
- **FastAPI** - Modern Python web framework for building APIs
- **Uvicorn** - ASGI server for running FastAPI applications
- **Python 3.11+** - Primary programming language

### Database
- **SQLite** - Lightweight, serverless database for local development
- **Custom ORM** - Hand-built database managers for each data type
- **Database file**: `site24x7_agent.db` (created automatically)

### AI & External Services
- **OpenAI GPT-4o** - AI analysis and code generation (optional)
- **GitHub API** - Repository management via PyGithub
- **Site24x7 API** - Documentation scraping target

### Scheduling & Automation
- **APScheduler** - Advanced Python Scheduler for automated tasks
- **AsyncIO** - Asynchronous programming for concurrent operations

### Web Scraping & Content Processing
- **BeautifulSoup4** - HTML parsing for documentation extraction
- **Trafilatura** - Content extraction from web pages
- **Requests** - HTTP library for API calls

### Frontend
- **Jinja2** - Template engine for HTML generation
- **Bootstrap 5** - CSS framework for responsive UI
- **JavaScript** - Frontend interactivity and API calls

## Database Schema

The application uses SQLite with the following tables:

### 1. configurations
```sql
CREATE TABLE configurations (
    id INTEGER PRIMARY KEY,
    key TEXT UNIQUE NOT NULL,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. api_snapshots
```sql
CREATE TABLE api_snapshots (
    id INTEGER PRIMARY KEY,
    url TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    documentation_data TEXT, -- JSON
    endpoints_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. cli_versions
```sql
CREATE TABLE cli_versions (
    id INTEGER PRIMARY KEY,
    version TEXT NOT NULL,
    endpoints_covered INTEGER,
    generation_data TEXT, -- JSON
    github_commit_sha TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. task_logs
```sql
CREATE TABLE task_logs (
    id INTEGER PRIMARY KEY,
    task_type TEXT NOT NULL,
    status TEXT NOT NULL, -- started, completed, failed
    message TEXT,
    details TEXT, -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5. github_operations
```sql
CREATE TABLE github_operations (
    id INTEGER PRIMARY KEY,
    operation_type TEXT NOT NULL,
    status TEXT NOT NULL,
    details TEXT, -- JSON
    github_reference TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Prerequisites

### System Requirements
- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Python**: 3.11 or higher
- **Memory**: Minimum 2GB RAM
- **Storage**: At least 1GB free space
- **Network**: Internet connection for API access

### Required Software
1. **Python 3.11+** - [Download from python.org](https://www.python.org/downloads/)
2. **Git** - [Download from git-scm.com](https://git-scm.com/downloads)
3. **Text Editor** - VS Code, PyCharm, or similar (optional but recommended)

## Local Deployment Steps

### 1. Clone the Repository
```bash
git clone <repository-url>
cd site24x7-cli-ai-agent
```

### 2. Set Up Python Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the project root:
```env
# Database
DATABASE_URL=sqlite:///site24x7_agent.db

# OpenAI API (Optional - AI features will be disabled if not provided)
OPENAI_API_KEY=your_openai_api_key_here

# GitHub Configuration (Required for repository management)
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token_here
GITHUB_USERNAME=your_github_username

# Site24x7 Configuration - No authentication needed for documentation scraping

# Security
SECRET_KEY=your_secret_key_here

# Scheduler Configuration
SCRAPER_INTERVAL_HOURS=6
MAINTENANCE_INTERVAL_HOURS=24

# Logging
LOG_LEVEL=INFO
DEBUG=false
```

### 5. Create Required API Keys

#### GitHub Personal Access Token (Required)
1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select these scopes:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
   - `write:packages` (Upload packages to GitHub Package Registry)
4. Copy the token and add it to your `.env` file

#### OpenAI API Key (Optional)
1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key and add it to your `.env` file
4. Note: Without this key, AI features will be disabled but the app will still work

# Site24x7 Configuration
No additional authentication is required for Site24x7 documentation scraping as the application only accesses publicly available API documentation.

### 6. Initialize Database
The database will be created automatically when you first run the application. No manual setup required.

### 7. Run the Application
```bash
# Start the application
python main.py
```

The application will be available at:
- **Web Dashboard**: http://localhost:5000
- **API Documentation**: http://localhost:5000/docs
- **Health Check**: http://localhost:5000/health

### 8. Verify Installation
1. Open http://localhost:5000 in your browser
2. You should see the Site24x7 CLI AI Agent dashboard
3. Check the status indicators to ensure services are running
4. Review logs at http://localhost:5000/logs

## Project Structure
```
site24x7-cli-ai-agent/
├── main.py                 # Application entry point
├── config.py              # Configuration management
├── database.py            # Database models and managers
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── site24x7_agent.db     # SQLite database (auto-created)
├── site24x7_agent.log    # Application logs (auto-created)
│
├── services/              # Core business logic
│   ├── ai_analyzer.py     # OpenAI integration
│   ├── api_scraper.py     # Site24x7 API scraping
│   ├── cli_generator.py   # CLI code generation
│   ├── github_manager.py  # GitHub repository management
│   └── scheduler.py       # Automated task scheduling
│
├── routes/                # Web API endpoints
│   ├── api.py            # REST API routes
│   └── dashboard.py      # Web dashboard routes
│
├── templates/             # HTML templates
│   ├── dashboard.html    # Main dashboard
│   ├── config.html       # Configuration page
│   └── logs.html         # Logs viewer
│
├── static/               # Static web assets
│   ├── style.css        # Application styles
│   └── script.js        # Frontend JavaScript
│
├── cli_templates/        # CLI generation templates
│   ├── base_cli.py.j2   # Main CLI template
│   ├── command_template.py.j2
│   ├── readme.md.j2
│   └── setup.py.j2
│
├── models/               # Data models
│   └── schemas.py       # Pydantic models
│
└── utils/               # Utility functions
    └── helpers.py       # Common helper functions
```

## Configuration Options

### Scheduler Settings
- `SCRAPER_INTERVAL_HOURS`: How often to scrape API documentation (default: 6 hours)
- `MAINTENANCE_INTERVAL_HOURS`: How often to perform GitHub maintenance (default: 24 hours)

### GitHub Settings
- `GITHUB_REPO_NAME`: Name of the repository to create/manage (default: "site24x7-cli")
- `GITHUB_USERNAME`: Your GitHub username
- `GITHUB_PERSONAL_ACCESS_TOKEN`: Your GitHub personal access token

### OpenAI Settings
- `OPENAI_API_KEY`: Your OpenAI API key for AI features
- `OPENAI_MODEL`: AI model to use (default: "gpt-4o")

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors
- Ensure the application has write permissions in the project directory
- Check if `site24x7_agent.db` file exists and is not corrupted

#### 2. GitHub API Errors
- Verify your GitHub personal access token is valid
- Ensure the token has the required scopes (repo, workflow, write:packages)
- Check if the repository already exists

#### 3. OpenAI API Errors
- Verify your OpenAI API key is valid
- Check your OpenAI account has sufficient credits
- The app will work without OpenAI, just with limited AI features

#### 4. Site24x7 Scraping Issues
- Check if Site24x7 API documentation is accessible
- Verify network connectivity
- Review logs for specific error messages

### Logs and Monitoring
- Application logs: `site24x7_agent.log`
- Web logs viewer: http://localhost:5000/logs
- System status: http://localhost:5000/api/v1/status

### Performance Tuning
- Adjust scheduler intervals based on your needs
- Monitor database size and clean old logs periodically
- Consider upgrading to PostgreSQL for high-load scenarios

## Development Mode

For development with auto-reload:
```bash
# Install development dependencies
pip install uvicorn[standard]

# Run with auto-reload
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

## Production Deployment

For production deployment:
1. Use a process manager like systemd or supervisor
2. Set up reverse proxy with nginx
3. Configure SSL certificates
4. Use PostgreSQL instead of SQLite for better concurrency
5. Set up log rotation
6. Configure backup strategies for the database

## Support

If you encounter issues:
1. Check the application logs (`site24x7_agent.log`)
2. Review the web dashboard status indicators
3. Verify all environment variables are set correctly
4. Ensure all required API keys are valid and have proper permissions