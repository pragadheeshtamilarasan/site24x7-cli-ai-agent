# Site24x7 CLI AI Agent

An autonomous AI-powered system that scrapes Site24x7 API documentation, generates comprehensive CLI tools, and maintains GitHub repositories automatically.

## 🚀 Quick Start

### 🐳 Docker Deployment (Recommended)

**One-line deployment for Ubuntu:**
```bash
curl -fsSL https://raw.githubusercontent.com/pragadheeshtamilarasan/site24x7-cli-ai-agent/main/simple-deploy.sh | bash
```

**For any local machine (handles corporate networks automatically):**
```bash
curl -fsSL https://raw.githubusercontent.com/pragadheeshtamilarasan/site24x7-cli-ai-agent/main/fixed-local-deploy.sh | bash
```

Both commands automatically:
- Install Docker and Docker Compose (if needed)
- Download and build the application using network-resilient strategies
- Start the service on port 5000
- No terminal configuration needed - configure via web UI!

**Access Points:**
- Dashboard: http://localhost:5000
- Configuration: http://localhost:5000/config
- Logs: http://localhost:5000/logs

For detailed Docker deployment instructions, see [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)

---

### 🐍 Manual Python Installation

### Prerequisites
- Python 3.11+
- Git
- GitHub Personal Access Token
- OpenAI API Key (optional, for AI features)

### Installation

1. **Clone the repository**
```bash
git clone <your-repository-url>
cd site24x7-cli-ai-agent
```

2. **Set up virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install fastapi uvicorn pydantic pydantic-settings python-multipart
pip install jinja2 openai requests beautifulsoup4 trafilatura
pip install pygithub apscheduler gitpython
```

4. **Create environment file**
Create `.env` file in project root:
```env
# Required: GitHub Configuration
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token_here
GITHUB_USERNAME=your_github_username

# Optional: AI Configuration (choose one)
# For OpenAI:
OPENAI_API_KEY=your_openai_api_key_here

# For Local LLM (OpenAI compatible):
OPENAI_API_KEY=your_local_llm_api_key
OPENAI_BASE_URL=http://localhost:3100/v1
USE_LOCAL_LLM=true

# Site24x7 - No authentication needed for documentation scraping

# Application Settings
SECRET_KEY=your_secret_key_here
SCRAPER_INTERVAL_HOURS=6
MAINTENANCE_INTERVAL_HOURS=24
LOG_LEVEL=INFO
DEBUG=false
```

5. **Run the application**
```bash
python main.py
```

Access the dashboard at: http://localhost:5000

## 🏗 Architecture Overview

### Technology Stack
- **Backend**: FastAPI + Python 3.11
- **Database**: SQLite (auto-created)
- **AI**: OpenAI GPT-4o or Local LLM (OpenAI compatible)
- **Scheduler**: APScheduler
- **GitHub**: PyGithub API
- **Web Scraping**: BeautifulSoup4 + Trafilatura
- **Frontend**: Jinja2 + Bootstrap 5

### Core Services

1. **API Scraper** - Extracts Site24x7 API documentation
2. **CLI Generator** - Creates comprehensive CLI tools from documentation
3. **GitHub Manager** - Autonomous repository management
4. **AI Analyzer** - Intelligent analysis and code generation (OpenAI or Local LLM)
5. **Scheduler** - Automated task execution

### Database Schema

**SQLite Database**: `site24x7_agent.db` (auto-created)

- `configurations` - Application settings
- `api_snapshots` - API documentation versions
- `cli_versions` - Generated CLI versions
- `task_logs` - System activity logs
- `github_operations` - GitHub activity tracking

## 🔧 Configuration

### Required API Keys

#### GitHub Personal Access Token
1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Create new token with these scopes:
   - `repo` (Full repository access)
   - `workflow` (GitHub Actions)
   - `write:packages` (Package registry)

#### AI Configuration (Optional)

The application supports both OpenAI and local LLM configurations:

**Option 1: OpenAI (Cloud)**
1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create new API key
3. Add to `.env` file:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

**Option 2: Local LLM (OpenAI Compatible)**
1. Set up your local LLM with OpenAI API compatibility
2. Add to `.env` file:
   ```env
   OPENAI_API_KEY=your_local_llm_api_key
   OPENAI_BASE_URL=http://localhost:3100/v1
   USE_LOCAL_LLM=true
   ```

**Supported Local LLM Providers:**
- LM Studio
- Ollama with OpenAI compatibility
- vLLM
- Any OpenAI-compatible endpoint

AI features are disabled if no configuration is provided.

# Site24x7 Configuration
No additional authentication is required. The application scrapes publicly available API documentation.

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `GITHUB_PERSONAL_ACCESS_TOKEN` | Yes | GitHub API access | - |
| `GITHUB_USERNAME` | Yes | Your GitHub username | - |
| `OPENAI_API_KEY` | No | OpenAI/Local LLM API key | - |
| `OPENAI_BASE_URL` | No | Local LLM base URL (OpenAI compatible) | - |
| `USE_LOCAL_LLM` | No | Use local LLM instead of OpenAI | false |
| `SECRET_KEY` | No | Application security | auto-generated |
| `SCRAPER_INTERVAL_HOURS` | No | API scraping frequency | 6 |
| `MAINTENANCE_INTERVAL_HOURS` | No | GitHub maintenance frequency | 24 |
| `LOG_LEVEL` | No | Logging level | INFO |
| `DEBUG` | No | Debug mode | false |

## 📁 Project Structure

```
site24x7-cli-ai-agent/
├── main.py                    # Application entry point
├── config.py                  # Configuration management
├── database.py                # Database models and managers
├── DEPLOYMENT.md              # Detailed deployment guide
├── DOCKER_DEPLOYMENT.md       # Docker deployment guide
├── README.md                  # This file
│
├── services/                  # Core business logic
│   ├── ai_analyzer.py         # AI integration (OpenAI/Local LLM)
│   ├── api_scraper.py         # Site24x7 API scraping
│   ├── cli_generator.py       # CLI code generation
│   ├── github_manager.py      # GitHub repository management
│   └── scheduler.py           # Automated task scheduling
│
├── routes/                    # Web API endpoints
│   ├── api.py                # REST API routes
│   └── dashboard.py          # Web dashboard routes
│
├── templates/                 # HTML templates
│   ├── dashboard.html        # Main dashboard
│   ├── config.html           # Configuration page
│   └── logs.html             # Logs viewer
│
├── static/                   # Static web assets
│   ├── style.css            # Application styles
│   └── script.js            # Frontend JavaScript
│
├── cli_templates/            # CLI generation templates
├── models/                   # Data models
└── utils/                    # Utility functions
```

## 🔄 How It Works

### Automated Workflow

1. **API Documentation Scraping**
   - Scheduled every 6 hours (configurable)
   - Extracts Site24x7 API endpoints and documentation
   - Detects changes using content hashing

2. **CLI Generation**
   - AI analyzes API structure (when OpenAI key provided)
   - Generates comprehensive CLI tool with proper command hierarchy
   - Creates supporting files (README, setup.py, etc.)

3. **GitHub Repository Management**
   - Automatically creates/updates repository
   - Handles commits, releases, and versioning
   - Manages issues and pull requests autonomously

4. **Monitoring & Maintenance**
   - Daily health checks
   - Weekly deep analysis and optimization
   - Comprehensive logging and error handling

### Web Dashboard Features

- **Real-time Status** - System health and service status
- **Configuration** - Web-based settings management
- **Logs Viewer** - Activity logs and debugging
- **API Documentation** - Interactive API explorer

## 🌐 API Endpoints

### Web Interface
- `GET /` - Redirects to dashboard
- `GET /dashboard` - Main dashboard
- `GET /config` - Configuration page
- `GET /logs` - Logs viewer
- `GET /health` - Health check

### REST API
- `GET /api/v1/status` - System status
- `GET /api/v1/repository` - GitHub repository info
- `GET /api/v1/logs` - Recent logs
- `POST /api/v1/config` - Update configuration
- `POST /api/v1/trigger-scrape` - Manual scrape trigger

## 🛠 Development

### Development Mode
```bash
# Install with development dependencies
pip install uvicorn[standard]

# Run with auto-reload
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

### Testing
```bash
# Test API endpoints
curl http://localhost:5000/health
curl http://localhost:5000/api/v1/status

# View logs
tail -f site24x7_agent.log
```

## 🚀 Production Deployment

### Recommended Setup
1. **Process Manager**: systemd or supervisor
2. **Reverse Proxy**: nginx with SSL
3. **Database**: PostgreSQL (for high concurrency)
4. **Monitoring**: Log rotation and health checks
5. **Backup**: Database and configuration backup

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["python", "main.py"]
```

## 🔍 Troubleshooting

### Common Issues

**Application won't start:**
- Check Python version (3.11+ required)
- Verify all dependencies installed
- Check environment variables in `.env` file

**GitHub API errors:**
- Verify personal access token is valid
- Ensure token has required scopes
- Check GitHub username is correct

**AI features not working:**
- OpenAI API key required for AI features
- Verify API key is valid and has credits
- Application works without AI key (fallback mode)

**Database errors:**
- Ensure write permissions in project directory
- Database file (`site24x7_agent.db`) created automatically
- Check disk space availability

### Log Files
- **Application logs**: `site24x7_agent.log`
- **Web interface**: http://localhost:5000/logs
- **System status**: http://localhost:5000/api/v1/status

## 📈 Monitoring

### Health Checks
- **Database connectivity**
- **GitHub API status**
- **OpenAI API status** (if configured)
- **Scheduler service status**
- **Recent task success rates**

### Performance Metrics
- API scraping success/failure rates
- CLI generation times
- GitHub operation statistics
- System resource usage

## 📖 Help Documentation

This project includes comprehensive documentation to help you get started:

### 📋 Available Guides

| Document | Description | Use Case |
|----------|-------------|----------|
| **[README.md](README.md)** | Main documentation with setup instructions | First-time users, overview |
| **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)** | Docker deployment guide with one-line command | Quick deployment on Ubuntu |
| **[DEPLOYMENT.md](DEPLOYMENT.md)** | Detailed manual deployment instructions | Advanced setup, troubleshooting |
| **[REQUIREMENTS.md](REQUIREMENTS.md)** | Technical requirements and dependencies | System administrators |

### 🚀 Quick Access Commands

**Docker Deployment (Ubuntu):**
```bash
curl -fsSL https://raw.githubusercontent.com/pragadheeshtamilarasan/site24x7-cli-ai-agent/main/simple-deploy.sh | bash
```

**Check Application Status:**
```bash
curl http://localhost:5000/api/v1/status
```

**View Live Logs:**
```bash
# Docker deployment
docker-compose logs -f

# Manual deployment  
tail -f site24x7_agent.log
```

### 🔧 Configuration Help

**Web Interface:**
- Configuration: http://localhost:5000/config
- Dashboard: http://localhost:5000/dashboard
- Logs: http://localhost:5000/logs

**Environment Variables:**
- GitHub token setup instructions in main README
- AI configuration (OpenAI/Local LLM) in configuration section
- All variables documented in environment table

### 🆘 Getting Help

1. **Check Status**: Visit http://localhost:5000/api/v1/status
2. **View Logs**: Check application logs for error details
3. **Documentation**: Review appropriate guide based on your setup
4. **Configuration**: Verify all required environment variables are set

### 📞 Support Resources

- **GitHub Issues**: Report bugs or request features
- **Documentation**: Comprehensive guides for all deployment types
- **Health Checks**: Built-in monitoring and diagnostics
- **Log Analysis**: Detailed logging for troubleshooting

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)

For issues and questions:
1. Check application logs (`site24x7_agent.log`)
2. Review web dashboard status indicators
3. Verify environment variables and API keys
4. Create GitHub issue with error details