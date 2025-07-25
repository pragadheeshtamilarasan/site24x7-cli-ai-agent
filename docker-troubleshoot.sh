#!/bin/bash

echo "🔍 Docker Troubleshooting for Site24x7 CLI AI Agent"
echo "=================================================="

echo ""
echo "1. Checking if container is running..."
docker ps | grep site24x7-cli-ai-agent

echo ""
echo "2. Checking container logs..."
docker logs site24x7-cli-ai-agent --tail 20

echo ""
echo "3. Checking if port 8080 is accessible inside container..."
docker exec site24x7-cli-ai-agent curl -f http://localhost:8080/health 2>/dev/null || echo "❌ Application not responding inside container"

echo ""
echo "4. Checking container port mapping..."
docker port site24x7-cli-ai-agent

echo ""
echo "5. Checking what's listening on host port 8080..."
lsof -i :8080 2>/dev/null || netstat -tulpn | grep :8080 2>/dev/null || echo "❌ Nothing listening on port 8080"

echo ""
echo "6. Testing local connection..."
curl -f http://localhost:8080/health 2>/dev/null && echo "✅ Application accessible" || echo "❌ Application not accessible"

echo ""
echo "🛠️  Potential fixes:"
echo "   - If container is not running: docker start site24x7-cli-ai-agent"
echo "   - If app not responding inside: docker restart site24x7-cli-ai-agent"
echo "   - If port not mapped: docker stop site24x7-cli-ai-agent && docker rm site24x7-cli-ai-agent && ./mac-deploy.sh"
echo "   - If firewall blocking: check your firewall settings for port 8080"