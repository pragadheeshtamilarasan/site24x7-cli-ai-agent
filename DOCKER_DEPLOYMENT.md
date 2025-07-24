# 🐳 Docker Deployment Guide

## One-Line Deployment for Ubuntu

### Quick Start (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/pragadheeshtamilarasan/site24x7-cli-ai-agent/main/deploy.sh | bash
```

This single command will:
- Install Docker and Docker Compose (if needed)
- Download the project
- Create configuration files
- Build and start the application
- Provide access URLs and management commands

### Manual Deployment

If you prefer manual setup:

1. **Clone the repository**
```bash
git clone https://github.com/pragadheeshtamilarasan/site24x7-cli-ai-agent.git
cd site24x7-cli-ai-agent
```

2. **Run deployment script**
```bash
chmod +x deploy.sh
./deploy.sh
```

### Configuration

Edit the `.env` file created during deployment:

```env
# Required GitHub Configuration
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token_here
GITHUB_USERNAME=your_github_username

# Optional AI Configuration (choose one)
# For OpenAI:
OPENAI_API_KEY=your_openai_api_key_here

# For Local LLM (OpenAI compatible):
OPENAI_API_KEY=your_local_llm_api_key
OPENAI_BASE_URL=http://localhost:3100/v1
USE_LOCAL_LLM=true
```

### Access Points

After successful deployment:
- **Dashboard**: http://localhost:5000
- **Configuration**: http://localhost:5000/config
- **Logs**: http://localhost:5000/logs
- **API Status**: http://localhost:5000/api/v1/status

### Management Commands

```bash
# View application logs
docker-compose logs -f

# Stop the application
docker-compose down

# Restart the application
docker-compose restart

# Update to latest version
docker-compose pull && docker-compose up -d

# View running containers
docker-compose ps

# Access container shell
docker-compose exec site24x7-agent bash
```

### Troubleshooting

#### Application won't start
```bash
# Check logs
docker-compose logs

# Check container status
docker-compose ps

# Restart services
docker-compose restart
```

#### Port 5000 already in use
Edit `docker-compose.yml` and change the port mapping:
```yaml
ports:
  - "8080:5000"  # Use port 8080 instead
```

#### Permission issues
```bash
# Fix permissions
sudo chown -R $USER:$USER data/
chmod -R 755 data/
```

### System Requirements

- **OS**: Ubuntu 18.04 or later
- **RAM**: 1GB minimum, 2GB recommended
- **Storage**: 2GB free space
- **Network**: Internet access for API calls and updates

### Security Notes

- The application runs on port 5000 by default
- Database files are stored in `./data` directory
- Environment variables contain sensitive information - keep `.env` secure
- GitHub token should have minimal required permissions

### Advanced Configuration

#### Custom Docker Build
```bash
# Build with custom tag
docker build -t my-site24x7-agent .

# Run with custom settings
docker run -d \
  --name site24x7-agent \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  --env-file .env \
  my-site24x7-agent
```

#### Health Monitoring
```bash
# Check application health
curl http://localhost:5000/api/v1/status

# Docker health check
docker-compose ps
```

#### Backup and Restore
```bash
# Backup data
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# Restore data
tar -xzf backup-20250724.tar.gz
```

### Support

For issues or questions:
1. Check the logs with `docker-compose logs`
2. Verify configuration in `.env` file
3. Ensure all required API keys are provided
4. Check GitHub repository for updates

---

**Note**: The deployment script automatically handles Docker installation and user permissions. You may need to log out and back in after first-time Docker installation.