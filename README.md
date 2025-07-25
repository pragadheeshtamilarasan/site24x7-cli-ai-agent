# Site24x7 CLI AI Agent

An autonomous AI-powered system that automatically scrapes Site24x7 API documentation, generates comprehensive CLI tools using AI analysis, and manages GitHub repositories with intelligent automation.

## 🚀 Quick Start (Mac)

### Prerequisites
- Python 3.8+ (required)
- Docker (optional, for containerized deployment)
- Git (for cloning)

### Easy Mac Deployment
```bash
git clone https://github.com/pragadheeshtamilarasan/site24x7-cli-ai-agent.git
cd site24x7-cli-ai-agent
chmod +x mac-deploy.sh
./mac-deploy.sh
```

The script will automatically:
- Detect available Python and Docker
- Set up the environment (virtual env or Docker)
- Install all dependencies
- Start the application on port 5000

### Manual Python Setup
```bash
git clone https://github.com/pragadheeshtamilarasan/site24x7-cli-ai-agent.git
cd site24x7-cli-ai-agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn[standard] pydantic pydantic-settings jinja2 python-multipart requests beautifulsoup4 trafilatura openai pygithub gitpython apscheduler

# Start the application
python main.py
```

### Docker Deployment (Optional)
```bash
git clone https://github.com/pragadheeshtamilarasan/site24x7-cli-ai-agent.git
cd site24x7-cli-ai-agent

# Build and run
docker build -t site24x7-cli-ai-agent .
docker run -d --name site24x7-cli-ai-agent -p 5000:5000 site24x7-cli-ai-agent
```

**Access the application at:** `http://localhost:5000`

## 🎯 Features

### 🤖 AI-Powered Analysis
- **OpenAI Integration**: GPT-4o for intelligent code generation
- **Local LLM Support**: Compatible with OpenAI-compatible local models
- **Smart Documentation**: Converts API docs into structured CLI commands
- **Intelligent Responses**: AI-driven issue handling and code improvements

### 🔄 Automated Workflows
- **Scheduled Scraping**: Regular API documentation updates
- **Automatic Generation**: CLI tools created from fresh documentation
- **GitHub Automation**: Repository management, commits, and deployments
- **Health Monitoring**: System status tracking and error recovery

### 🎨 Modern Web Interface
- **Contemporary Design**: Professional UI with modern aesthetics
- **Real-time Dashboard**: Live system status and activity monitoring
- **Interactive Configuration**: Web-based settings management
- **Advanced Logging**: Comprehensive activity tracking and filtering

### 🐙 GitHub Integration
- **Repository Management**: Automatic repository creation and maintenance
- **Version Control**: Intelligent commit messages and version tracking
- **Issue Handling**: AI-powered issue response and resolution
- **Release Management**: Automated releases and documentation updates

## 🏗 Architecture

### Technology Stack
- **Backend**: FastAPI + Python 3.8+
- **Database**: SQLite (auto-created)
- **AI**: OpenAI GPT-4o or Local LLM (OpenAI compatible)
- **Scheduler**: APScheduler for automated tasks
- **GitHub**: PyGithub API integration
- **Web Scraping**: BeautifulSoup4 + Trafilatura
- **Frontend**: Jinja2 + Bootstrap 5 + Modern CSS

### Core Services
1. **API Scraper** - Extracts Site24x7 API documentation with change detection
2. **CLI Generator** - Creates comprehensive CLI tools from documentation using AI
3. **GitHub Manager** - Autonomous repository management and version control
4. **AI Analyzer** - Intelligent analysis and code generation (OpenAI or Local LLM)
5. **Scheduler** - Automated task execution with configurable intervals

### Database Schema
**SQLite Database**: `site24x7_agent.db` (auto-created)
- `configurations` - Application settings and API keys
- `api_snapshots` - API documentation versions and change tracking
- `cli_versions` - Generated CLI versions and metadata
- `task_logs` - System activity logs and execution history
- `github_operations` - GitHub activity tracking and operation history

## 🔧 Configuration

### Required Configuration
1. **GitHub Personal Access Token** (for repository operations)
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Generate token with `repo`, `workflow`, `write:packages` scopes

2. **AI Configuration** (choose one):
   - **OpenAI**: API key from OpenAI Platform
   - **Local LLM**: OpenAI-compatible endpoint URL and API key

### Web Configuration
Access the configuration page at `http://localhost:5000/config` to set up:
- GitHub credentials and repository settings
- OpenAI or Local LLM configuration
- Scheduling intervals for automated tasks
- System preferences and logging levels

### Environment Variables (Optional)
Create `.env` file for environment-based configuration:
```env
# GitHub Configuration
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token
GITHUB_USERNAME=your_username

# OpenAI Configuration
OPENAI_API_KEY=your_openai_key

# Local LLM Configuration (alternative to OpenAI)
OPENAI_BASE_URL=http://localhost:3100/v1
USE_LOCAL_LLM=true

# Application Settings
SECRET_KEY=your_secret_key
SCRAPER_INTERVAL_HOURS=6
MAINTENANCE_INTERVAL_HOURS=24
```

## 🎮 Usage

### Dashboard (`/dashboard`)
- **System Status**: Real-time monitoring of all services
- **Quick Actions**: Manual trigger for scraping, generation, and maintenance
- **Activity Logs**: Recent task execution and GitHub operations
- **Repository Info**: Current CLI version and GitHub statistics

### Configuration (`/config`)
- **Service Setup**: Configure GitHub, OpenAI, and Local LLM settings
- **Scheduling**: Set intervals for automated operations
- **Testing**: Validate configuration before saving
- **Status Overview**: Visual indicators for all service connections

### Logs (`/logs`)
- **Comprehensive Logging**: All system activities with timestamps
- **Advanced Filtering**: Filter by status, type, and search terms
- **Detailed Views**: Full operation details and error information
- **Export Options**: Download logs for analysis

## 🚨 Troubleshooting

### Common Issues
1. **Import Errors**: Ensure all dependencies are installed in the active environment
2. **Port Conflicts**: Application uses port 5000 by default
3. **API Limits**: OpenAI and GitHub APIs have rate limits
4. **Permission Issues**: Ensure GitHub token has required scopes

### Logs and Debugging
- **Application Logs**: Check `site24x7_agent.log` for detailed error information
- **Console Output**: Run `python main.py` directly to see real-time logs
- **Database Logs**: Access `/logs` page for historical operation data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Site24x7** for providing comprehensive API documentation
- **OpenAI** for powerful AI capabilities
- **GitHub** for excellent API and platform support
- **FastAPI** for the robust web framework