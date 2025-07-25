# Site24x7 CLI AI Agent

## Overview

This is an autonomous AI agent that scrapes Site24x7 API documentation, generates a comprehensive CLI tool, and maintains a GitHub repository automatically. The system uses OpenAI for intelligent analysis, scheduled tasks for automation, and provides a web dashboard for monitoring and control.

## Current Status (July 25, 2025)

✅ **Complete UI-Based Configuration System**
- All settings moved from environment variables to web UI
- Real-time configuration testing with connection validation
- Database-first storage with environment variable fallbacks
- Modern, professional interface with comprehensive validation
- Zero environment variable setup required

✅ **GitHub Polling for Local Deployment**
- Replaced webhooks with intelligent polling system for local machines
- Configurable polling intervals (5-60 minutes, default 15 minutes)
- Automatic detection of new issues, PRs, comments, and releases
- Smart AI-powered responses to GitHub activity
- Perfect for local development and home lab deployment

✅ **Optimized for Local Development**
- Complete local deployment guide created (LOCAL_DEPLOYMENT_GUIDE.md)
- Works perfectly on localhost without external webhook setup
- Supports both OpenAI and local LLM configurations
- Self-contained with SQLite database and local file storage
- Ready for deployment on personal machines, Raspberry Pi, etc.

## Recent Changes

### Scheduler Tasks & AI Responses Fully Working (July 25, 2025)
- **GitHub AI Responses Active**: Automated AI-powered responses to all new GitHub issues, PRs, and comments
- **Real-time Issue Detection**: System detects and responds to new GitHub activity within minutes
- **Intelligent Fallbacks**: Works with or without OpenAI API key using smart fallback responses
- **Complete Workflow Integration**: Polling → Analysis → Response → GitHub comment posting
- **Autonomous Operation**: Fully automated GitHub repository management and user engagement

### GitHub Integration Successfully Fixed (July 25, 2025)
- **Repository Connection Fixed**: GitHub manager now properly initializes and connects to target repository
- **CLI Generation Working**: Successfully generates complete CLI projects with 14+ files
- **GitHub Deployment Active**: Automatically deploys generated CLI to https://github.com/pragadheeshtamilarasan/site24x7-cli
- **Real CLI Creation**: Creates fully functional Python CLI package with commands, authentication, and documentation
- **Repository Status Live**: Dashboard now shows actual repository information and recent commits
- **Manual Generation Endpoint**: Added `/api/v1/actions/generate-cli` for on-demand CLI generation

### Enhanced Local LLM Support & Comprehensive Logging (July 25, 2025)
- **Complete Local LLM Configuration**: Added API key, model name, and base URL fields for local LLM setup
- **Smart AI Provider Switching**: Dynamic form that switches between OpenAI and Local LLM configurations
- **Local LLM Examples**: Support for Ollama, LM Studio, and custom OpenAI-compatible endpoints
- **Comprehensive Logging System**: New `/logs` page with real-time workflow error monitoring
- **Advanced Log Filtering**: Filter by task type, status, and auto-refresh capabilities
- **System Health Dashboard**: Live status monitoring for scheduler, AI service, GitHub, and database

### Complete Modern UI Redesign (July 25, 2025)
- **Contemporary Design System**: Implemented modern design language with Inter and JetBrains Mono fonts
- **Advanced CSS Framework**: Created comprehensive CSS system with CSS variables, gradients, and modern shadows
- **Enhanced Animations**: Added smooth transitions, fade-in effects, slide animations, and ripple effects
- **Interactive Components**: Modern buttons, cards, tables, alerts with hover effects and micro-interactions
- **Professional Typography**: Improved font hierarchy and spacing throughout the application
- **Modern Enhancements Script**: Created comprehensive JavaScript for modern UI interactions

### Simplified Mac Deployment (July 25, 2025)
- **Mac-Focused Deployment**: Removed all corporate network complexity, focused on local Mac deployment
- **Simple Deployment Script**: Created mac-deploy.sh for easy local setup with Python or Docker
- **Streamlined Setup**: One script handles both virtual environment and Docker deployment options
- **Simplified Documentation**: Updated README to focus on Mac-specific installation and setup
- **Complete Uninstall Support**: Added comprehensive uninstallation with cleanup of all components

### Local LLM Support Added (July 24, 2025)
- **AI Configuration**: Added support for local LLM with OpenAI API compatibility
- **Configuration Fields**: Added `openai_base_url`, `use_local_llm`, and dynamic model selection
- **Web Interface**: Updated configuration page with radio buttons for OpenAI vs Local LLM
- **Dynamic Configuration**: Form automatically switches between OpenAI and Local LLM fields
- **Example Support**: Supports local LLM endpoints with OpenAI API compatibility

### Previous Bug Fixes (July 24, 2025)
- **AI Analyzer**: Added graceful handling when OpenAI API key is not provided
- **Scheduler Service**: Fixed all TaskLogger import issues with proper error handling
- **GitHub Manager**: Made repository initialization more fault-tolerant
- **Startup Process**: Removed blocking initial tasks that caused application timeouts
- **Documentation**: Created comprehensive deployment guide and README

### Architecture Improvements
- Modern UI with professional design and smooth animations throughout
- AI features now support both OpenAI and local LLM configurations
- Better error logging and exception handling throughout
- More resilient startup process
- Enhanced documentation for local deployment

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: FastAPI with async/await support for high-performance web API
- **Database**: SQLite for data persistence with custom manager classes
- **Scheduler**: APScheduler for automated task execution
- **AI Integration**: OpenAI GPT-4o for intelligent analysis and code generation
- **GitHub Integration**: PyGithub for repository management and automation

### Frontend Architecture
- **Templates**: Jinja2 templating with Bootstrap 5 for responsive UI
- **Static Assets**: CSS and JavaScript for enhanced user interactions
- **Dashboard**: Real-time monitoring interface with auto-refresh capabilities

## Key Components

### Core Services
1. **API Scraper** (`services/api_scraper.py`)
   - Scrapes Site24x7 API documentation using BeautifulSoup and trafilatura
   - Extracts endpoint information, parameters, and documentation structure
   - Generates content hashes to detect changes

2. **CLI Generator** (`services/cli_generator.py`)
   - Uses AI analysis to structure CLI commands from API documentation
   - Generates complete CLI project files with proper command hierarchies
   - Creates supporting files (README, setup.py, etc.)

3. **GitHub Manager** (`services/github_manager.py`)
   - Autonomous repository creation and maintenance
   - Handles commits, pull requests, and release management
   - Integrates AI for analyzing issues and generating responses

4. **AI Analyzer** (`services/ai_analyzer.py`)
   - OpenAI GPT-4o integration for intelligent analysis
   - Structures API documentation into logical CLI command hierarchies
   - Provides insights for code generation and issue handling

5. **Scheduler Service** (`services/scheduler.py`)
   - Manages periodic tasks (scraping, generation, maintenance)
   - Configurable intervals for different operations
   - Health monitoring and error recovery

### Database Layer
- **SQLite Database** with custom manager classes
- **Tables**: configurations, api_snapshots, cli_versions, task_logs, github_operations
- **Managers**: Dedicated classes for each data type with CRUD operations

### Web Interface
- **Dashboard**: Real-time system status and monitoring
- **Configuration**: Web-based settings management
- **Logs**: Comprehensive activity logging and viewing

## Data Flow

1. **Scraping Phase**
   - Scheduler triggers API documentation scraping
   - Content is parsed and stored with hash-based change detection
   - New snapshots trigger CLI generation

2. **Generation Phase**
   - AI analyzes documentation structure
   - CLI commands and structure are generated
   - Complete project files are created

3. **GitHub Management**
   - Repository is created or updated
   - Files are committed with appropriate versioning
   - Issues and PRs are handled autonomously

4. **Monitoring**
   - All operations are logged to database
   - Dashboard provides real-time status
   - Health checks ensure system reliability

## External Dependencies

### APIs and Services
- **OpenAI API**: GPT-4o model for intelligent analysis and generation
- **GitHub API**: Repository management and automation
- **Site24x7 API**: Documentation source and target API

### Python Packages
- **FastAPI**: Web framework and API server
- **OpenAI**: AI analysis and generation
- **PyGithub**: GitHub API integration
- **APScheduler**: Task scheduling and automation
- **BeautifulSoup4**: HTML parsing for documentation scraping
- **Trafilatura**: Content extraction from web pages
- **Jinja2**: Template engine for CLI generation
- **Pydantic**: Data validation and settings management

## Deployment Strategy

### Local Development
- SQLite database for simplicity
- Environment variables for configuration
- Debug mode with detailed logging
- Auto-reload for development

### Configuration Management
- **Environment Variables**: Sensitive data (API keys, tokens)
- **Database Storage**: Application settings and state
- **Default Values**: Sensible defaults for quick setup

### Security Considerations
- API keys stored in environment variables
- Secret key for session management
- Sanitized inputs for file operations
- Secure GitHub token handling

### Monitoring and Logging
- Comprehensive logging to file and console
- Database-backed activity tracking
- Web dashboard for real-time monitoring
- Health checks and error recovery

### Scalability Notes
- Designed for single-instance deployment
- SQLite suitable for moderate loads
- Can be extended to PostgreSQL for higher concurrency
- Stateless services allow for horizontal scaling if needed