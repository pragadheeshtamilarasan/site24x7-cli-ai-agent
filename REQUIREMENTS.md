# Site24x7 CLI AI Agent - Requirements

## Python Dependencies

The following packages are required to run the application:

### Core Framework
```
fastapi==0.104.1          # Modern web framework for APIs
uvicorn[standard]==0.24.0  # ASGI server for FastAPI
```

### Data Validation & Settings
```
pydantic==2.5.0           # Data validation using Python type annotations
pydantic-settings==2.1.0  # Settings management for Pydantic
python-multipart==0.0.6   # Multipart form data parsing
```

### Template Engine
```
jinja2==3.1.2             # Template engine for HTML generation
```

### AI Integration
```
openai==1.3.7             # OpenAI API client (optional)
```

### HTTP & Web Scraping
```
requests==2.31.0          # HTTP library for Python
beautifulsoup4==4.12.2    # HTML/XML parsing library
trafilatura==1.6.3        # Web content extraction
```

### GitHub Integration
```  
pygithub==2.1.1           # GitHub API wrapper
gitpython==3.1.40         # Git command wrapper
```

### Task Scheduling
```
apscheduler==3.10.4       # Advanced Python Scheduler
```

## Installation Methods

### Method 1: Automatic Setup (Recommended)
```bash
python setup_local.py
```

### Method 2: Manual Installation
```bash
pip install fastapi==0.104.1 uvicorn[standard]==0.24.0
pip install pydantic==2.5.0 pydantic-settings==2.1.0 python-multipart==0.0.6
pip install jinja2==3.1.2 openai==1.3.7 requests==2.31.0
pip install beautifulsoup4==4.12.2 trafilatura==1.6.3
pip install pygithub==2.1.1 apscheduler==3.10.4 gitpython==3.1.40
```

### Method 3: From requirements file
If you have access to edit requirements.txt:
```bash
pip install -r requirements.txt
```

## System Requirements

### Operating System
- Windows 10+ 
- macOS 10.15+ (Catalina)
- Linux (Ubuntu 18.04+, CentOS 7+, or equivalent)

### Python Version
- **Python 3.11+** (Required)
- Python 3.10 may work but is not officially supported

### Hardware Requirements
- **Memory**: Minimum 2GB RAM, 4GB recommended
- **Storage**: At least 1GB free space
- **Network**: Internet connection for API access

### Additional Software
- **Git** - For repository management
- **Text Editor** - VS Code, PyCharm, or similar (optional)

## Environment Variables

Create a `.env` file with the following variables:

### Required Variables
```env
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token_here
GITHUB_USERNAME=your_github_username
```

### Optional Variables (Recommended)
```env
OPENAI_API_KEY=your_openai_api_key_here
SITE24X7_OAUTH_TOKEN=your_site24x7_token_here
SECRET_KEY=your_secret_key_here
```

### Configuration Variables
```env
DATABASE_URL=sqlite:///site24x7_agent.db
SCRAPER_INTERVAL_HOURS=6
MAINTENANCE_INTERVAL_HOURS=24
LOG_LEVEL=INFO
DEBUG=false
```

## API Keys Setup

### GitHub Personal Access Token (Required)
1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select scopes:
   - `repo` - Full control of private repositories
   - `workflow` - Update GitHub Action workflows  
   - `write:packages` - Upload packages to GitHub Package Registry
4. Copy token and add to `.env` file

### OpenAI API Key (Optional but Recommended)
1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create new API key
3. Copy key and add to `.env` file
4. **Note**: Without this key, AI features are disabled but the app still works

### Site24x7 Configuration
No authentication required. The application accesses publicly available API documentation from Site24x7.

## Verification

After installation, verify everything is working:

```bash
# Check Python version
python --version

# Test imports
python -c "import fastapi, uvicorn, pydantic, jinja2, requests, bs4, github, apscheduler; print('All imports successful')"

# Start application
python main.py
```

The application should start and be accessible at http://localhost:5000

## Troubleshooting

### Common Installation Issues

**Python version error:**
```
Solution: Install Python 3.11+ from python.org
```

**Package installation fails:**
```
Solution: Upgrade pip first: python -m pip install --upgrade pip
```

**Permission denied errors:**
```
Solution: Use virtual environment or --user flag: pip install --user <package>
```

**GitHub API authentication fails:**
```
Solution: Verify GitHub token has correct scopes and is not expired
```

**OpenAI API errors:**
```
Solution: Check API key validity and account credits; app works without OpenAI
```

For more detailed troubleshooting, see [DEPLOYMENT.md](DEPLOYMENT.md).