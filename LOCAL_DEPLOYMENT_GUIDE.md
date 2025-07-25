# Site24x7 CLI AI Agent - Local Deployment Guide

## Overview

This guide is specifically for deploying the Site24x7 CLI AI Agent on your local machine. The agent has been optimized for local deployment with **GitHub polling** instead of webhooks, making it perfect for development and personal use.

## Why Local Deployment?

### ✅ **Perfect for Local Development**
- **No webhook setup required** - GitHub can't reach local machines
- **Complete control** - Run on your own hardware
- **Privacy** - All data stays on your machine
- **Customization** - Modify and experiment freely

### 🔄 **Intelligent GitHub Polling**
Instead of webhooks, the agent **automatically polls** your GitHub repository:
- **Configurable intervals** - Every 5-60 minutes (default: 15 minutes)
- **Smart detection** - Finds new issues, PRs, comments, and releases
- **Automatic responses** - AI handles issues and PRs intelligently
- **Local notifications** - See activity in the web dashboard

## Quick Setup (3 Steps)

### 1. **Download and Run**
```bash
# Clone the repository
git clone https://github.com/pragadheeshtamilarasan/site24x7-cli-ai-agent.git
cd site24x7-cli-ai-agent

# Run with Python (recommended)
./mac-deploy.sh

# OR run with Docker
docker-compose up
```

### 2. **Configure via Web UI**
Open http://localhost:8080/config and enter:

- **GitHub Token** - [Create here](https://github.com/settings/tokens)
- **OpenAI API Key** - [Get here](https://platform.openai.com/api-keys)
- **Repository Name** - Your `site24x7-cli` repository

### 3. **Start Monitoring**
- Visit http://localhost:8080/dashboard
- Watch the agent automatically poll GitHub every 15 minutes
- See real-time activity and AI responses

## Configuration Options

### GitHub Polling Settings
- **5 minutes** - Very responsive (for active development)
- **15 minutes** - Recommended balance
- **30 minutes** - Light polling
- **60 minutes** - Minimal resource usage

### Automation Features
- ✅ **Auto-deploy CLI updates** when API changes
- ✅ **Auto-respond to issues** with AI analysis
- ⚠️ **Auto-merge PRs** (use carefully)
- ✅ **Smart notifications** for manual intervention

## How It Works

### 🕐 **Every 15 Minutes (Configurable)**
1. **Poll GitHub** for new issues, PRs, comments
2. **Analyze content** with AI (OpenAI or local LLM)
3. **Generate responses** for issues and PRs
4. **Update dashboard** with new activity

### 🕕 **Every 6 Hours**
1. **Scrape Site24x7 API docs** for changes
2. **Generate updated CLI code** if changes found
3. **Push to GitHub** with automatic version bump
4. **Create release** with changelog

### 📊 **Real-time Dashboard**
- Live GitHub activity feed
- Configuration testing
- System health monitoring
- Manual control buttons

## Local vs Cloud Deployment

| Feature | Local Deployment | Cloud Deployment |
|---------|------------------|------------------|
| **GitHub Integration** | Polling ✅ | Webhooks ✅ |
| **Response Time** | 5-60 minutes | Instant |
| **Setup Complexity** | Simple ✅ | Complex |
| **Resource Usage** | Your machine | Cloud server |
| **Privacy** | Complete ✅ | Shared |
| **Cost** | Free ✅ | Server costs |

## Advanced Configuration

### Use Local LLM Instead of OpenAI
1. Run a local LLM server (like Ollama, LocalAI)
2. In `/config`, select "Local LLM"
3. Enter your local server URL (e.g., `http://localhost:1234/v1`)

### Customize Polling Behavior
Edit these settings in `/config`:
- **Polling Interval** - How often to check GitHub
- **Auto-deployment** - Enable/disable automatic CLI updates
- **Issue Response** - Enable/disable AI issue responses
- **Debug Mode** - Verbose logging for troubleshooting

### Multiple Repositories
To monitor multiple Site24x7 repositories:
1. Run multiple agent instances on different ports
2. Configure each with different repository names
3. Use nginx or similar for unified access

## Troubleshooting

### Common Issues

**Agent not polling GitHub:**
- Check GitHub token permissions in `/config`
- Verify repository name is correct
- Look at logs in `/logs` for errors

**AI responses not working:**
- Verify OpenAI API key or local LLM setup
- Check API quota and usage limits
- Test configuration with "Test Configuration" button

**CLI updates not deploying:**
- Ensure GitHub token has write permissions
- Check Site24x7 documentation URL accessibility
- Review deployment logs in dashboard

### Getting Help
1. **Dashboard**: Check system status and recent activity
2. **Logs**: View detailed operation logs at `/logs`
3. **Test**: Use "Test Configuration" to verify settings
4. **Reset**: "Reset to Defaults" if configuration is broken

## Benefits for Local Development

### 🔧 **Perfect for Developers**
- **Modify and test** changes instantly
- **Debug locally** with full access
- **Experiment safely** without affecting production
- **Learn the system** by running it yourself

### 🏠 **Home Lab Friendly**
- **Raspberry Pi compatible** - Runs on ARM devices
- **Low resource usage** - Minimal CPU and memory
- **Offline capable** - Works without internet (except API calls)
- **Self-contained** - SQLite database, no external dependencies

### 🔒 **Security and Privacy**
- **Your data stays local** - No cloud vendor access
- **Control all tokens** - GitHub and OpenAI keys stay with you
- **Audit everything** - Full visibility into all operations
- **Custom modifications** - Add features specific to your needs

The local deployment option makes this agent perfect for developers who want full control, privacy, and the ability to customize their CLI automation workflow!

## Next Steps

1. ✅ **Deploy locally** using this guide
2. ✅ **Configure tokens** via the web UI
3. ✅ **Test polling** by creating a test issue
4. ✅ **Monitor dashboard** for automated responses
5. ✅ **Customize settings** for your workflow

Your Site24x7 CLI will now be automatically maintained by your local AI agent!