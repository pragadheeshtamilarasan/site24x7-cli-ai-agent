# Uninstalling Site24x7 CLI AI Agent

This guide provides comprehensive instructions for completely removing the Site24x7 CLI AI Agent from your Mac.

## 🚀 Quick Uninstall (Recommended)

The easiest way to uninstall is using the deployment script:

```bash
cd site24x7-cli-ai-agent
./mac-deploy.sh uninstall
```

This will automatically:
- Stop and remove Docker containers (if used)
- Remove Docker images
- Delete Python virtual environment
- Remove database and log files
- Clean up cache files

## 🔧 Manual Uninstall

If you prefer to uninstall manually or the script doesn't work:

### Step 1: Stop the Application
```bash
# If running in terminal, press Ctrl+C
# If running in background, find and kill the process
ps aux | grep "python main.py"
kill <process_id>
```

### Step 2: Remove Docker Components (if used)
```bash
# Stop the container
docker stop site24x7-cli-ai-agent

# Remove the container
docker rm site24x7-cli-ai-agent

# Remove the image
docker rmi site24x7-cli-ai-agent

# Verify removal
docker ps -a | grep site24x7
docker images | grep site24x7
```

### Step 3: Remove Python Virtual Environment (if used)
```bash
# Deactivate if currently active
deactivate

# Remove the virtual environment directory
rm -rf venv
```

### Step 4: Remove Data Files
```bash
# Remove database
rm -f site24x7_agent.db

# Remove log files
rm -f site24x7_agent.log

# Remove any backup files
rm -f *.db.backup
rm -f *.log.backup
```

### Step 5: Clean Cache Files
```bash
# Remove Python cache directories
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

# Remove Python compiled files
find . -name "*.pyc" -delete 2>/dev/null

# Remove any .DS_Store files (Mac)
find . -name ".DS_Store" -delete 2>/dev/null
```

### Step 6: Remove Project Directory
```bash
# Go up one directory
cd ..

# Remove the entire project directory
rm -rf site24x7-cli-ai-agent
```

## 🧹 Deep Clean (Optional)

For a complete removal including any system-wide configurations:

### Remove from PATH (if added)
If you added the project to your PATH, edit your shell profile:
```bash
# For bash
nano ~/.bashrc

# For zsh
nano ~/.zshrc

# Remove any lines referencing site24x7-cli-ai-agent
```

### Remove from Startup Services (if configured)
If you configured the app to start automatically:
```bash
# Check for launchd services (Mac)
ls ~/Library/LaunchAgents/ | grep site24x7

# Remove any found services
rm ~/Library/LaunchAgents/com.site24x7.cli.agent.plist
```

### Clear Browser Data
If you want to remove saved configurations from your browser:
1. Open your browser
2. Go to Settings → Privacy → Clear browsing data
3. Select "Cookies and site data" for localhost:5000

## ✅ Verification

To verify complete removal:

1. **Check for running processes:**
   ```bash
   ps aux | grep site24x7
   ps aux | grep "python main.py"
   ```

2. **Check for Docker artifacts:**
   ```bash
   docker ps -a | grep site24x7
   docker images | grep site24x7
   ```

3. **Check for project directory:**
   ```bash
   ls -la | grep site24x7
   ```

4. **Test port availability:**
   ```bash
   lsof -i :5000
   ```

If all commands return no results, the uninstallation is complete.

## 🚨 Troubleshooting Uninstall Issues

### Permission Denied Errors
```bash
# Use sudo for system files
sudo rm -rf /path/to/file

# Fix ownership if needed
sudo chown -R $(whoami) .
```

### Docker Permission Issues
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login again, or restart terminal
```

### Force Remove Stubborn Files
```bash
# Force remove with extreme prejudice
sudo rm -rf site24x7-cli-ai-agent

# If files are locked
sudo lsof +D site24x7-cli-ai-agent
sudo kill -9 <process_id>
```

### Reset File Permissions
```bash
# Fix permissions recursively
chmod -R 755 site24x7-cli-ai-agent
sudo rm -rf site24x7-cli-ai-agent
```

## 📞 Support

If you encounter issues during uninstallation:

1. Check the project logs: `site24x7_agent.log`
2. Use the verbose uninstall: `./mac-deploy.sh uninstall -v`
3. Open an issue on the GitHub repository
4. Contact support with error details

## 🔄 Reinstallation

After uninstalling, you can reinstall anytime by:
```bash
git clone https://github.com/pragadheeshtamilarasan/site24x7-cli-ai-agent.git
cd site24x7-cli-ai-agent
./mac-deploy.sh
```

Your previous configuration will be lost, so you'll need to reconfigure the application.