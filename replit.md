# Site24x7 CLI AI Agent

## Overview

This is an autonomous AI agent that scrapes Site24x7 API documentation, generates a comprehensive CLI tool, and maintains a GitHub repository automatically. The system uses OpenAI for intelligent analysis, scheduled tasks for automation, and provides a web dashboard for monitoring and control.

## Current Status (July 25, 2025)

✅ **Port Changed to 8080 (Replit-Compatible)**
- Successfully updated application to run on port 8080 (avoiding blocked port 5000)
- Port 8080 is available and commonly used in Replit deployments
- Updated all configuration files and deployment scripts
- Modified Docker containers and health checks for new port
- Updated all documentation to reflect new port configuration

✅ **Mac Deployment Simplified**
- Removed all corporate network deployment complexity
- Created simple mac-deploy.sh for local Mac development
- Supports both Python virtual environment and Docker deployment
- Clean, focused setup for individual developers
- Modern UI with contemporary design system implemented

✅ **Application Successfully Debugged and Running**
- Fixed startup crash caused by missing OpenAI API key handling
- Resolved TaskLogger import errors throughout scheduler service
- Made GitHub initialization fault-tolerant with optional git
- Disabled blocking initial tasks to ensure quick startup
- Application now runs stably on port 8080 with all services active

## Recent Changes

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