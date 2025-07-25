# Docker Troubleshooting Guide

## Issue: Docker container starts but application not accessible

Your Docker deployment completed successfully, but the application isn't accessible at http://localhost:8080. Here are the steps to diagnose and fix this:

## Step 1: Check Container Status

Run this command to see if the container is running:
```bash
docker ps | grep site24x7-cli-ai-agent
```

If the container is not running, restart it:
```bash
docker start site24x7-cli-ai-agent
```

## Step 2: Check Application Logs

Check if the application started properly inside the container:
```bash
docker logs site24x7-cli-ai-agent
```

Look for these key messages:
- `INFO: Application startup complete.`
- `INFO: Uvicorn running on http://0.0.0.0:8080`

## Step 3: Test Application Inside Container

Test if the application responds inside the container:
```bash
docker exec site24x7-cli-ai-agent curl -f http://localhost:8080/health
```

This should return JSON with status "healthy".

## Step 4: Check Port Mapping

Verify the port mapping is correct:
```bash
docker port site24x7-cli-ai-agent
```

This should show: `8080/tcp -> 0.0.0.0:8080`

## Step 5: Check Host Port

Check if anything is blocking port 8080 on your Mac:
```bash
lsof -i :8080
```

## Quick Fix Solutions

### Option A: Restart Everything
```bash
docker stop site24x7-cli-ai-agent
docker rm site24x7-cli-ai-agent
./mac-deploy.sh
# Choose option 1 again
```

### Option B: Use Different Port
If port 8080 is blocked, modify the deployment to use port 3000:
```bash
docker stop site24x7-cli-ai-agent
docker rm site24x7-cli-ai-agent
docker run -d --name site24x7-cli-ai-agent -p 3000:8080 --restart unless-stopped site24x7-cli-ai-agent
```
Then access at: http://localhost:3000

### Option C: Try Python Virtual Environment Instead
```bash
docker stop site24x7-cli-ai-agent
docker rm site24x7-cli-ai-agent
./mac-deploy.sh
# Choose option 2 for Python virtual environment
```

## Testing Access

Once fixed, test these URLs:
- Health check: http://localhost:8080/health
- Dashboard: http://localhost:8080/dashboard
- Main page: http://localhost:8080/

## Common Issues

1. **Port 8080 already in use**: Try Option B above
2. **Application crashed inside container**: Check logs with Step 2
3. **Firewall blocking**: Check macOS firewall settings
4. **Docker Desktop issues**: Restart Docker Desktop

Run the troubleshoot script I created:
```bash
./docker-troubleshoot.sh
```

This will automatically check all the common issues and provide specific guidance.