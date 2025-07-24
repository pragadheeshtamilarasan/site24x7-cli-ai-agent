# AWS Deployment Guide

This guide provides step-by-step instructions for deploying the Site24x7 CLI AI Agent on AWS EC2.

## Quick AWS Deployment

### One-Line Deployment
```bash
curl -fsSL https://raw.githubusercontent.com/pragadheeshtamilarasan/site24x7-cli-ai-agent/main/aws-deploy.sh | bash
```

## Manual AWS Setup

### 1. Launch EC2 Instance

**Recommended Configuration:**
- **Instance Type**: t3.small or larger (minimum 2GB RAM)
- **Operating System**: Ubuntu 20.04 LTS or Ubuntu 22.04 LTS
- **Storage**: 20GB GP3 SSD (minimum)
- **Security Group**: Create or modify to allow:
  - SSH (port 22) from your IP
  - HTTP (port 5000) from anywhere (0.0.0.0/0) or your IP range

### 2. Connect to Instance

```bash
# Connect via SSH
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y
```

### 3. Run Deployment Script

```bash
# Download and run the AWS deployment script
curl -fsSL https://raw.githubusercontent.com/pragadheeshtamilarasan/site24x7-cli-ai-agent/main/aws-deploy.sh | bash
```

### 4. Configure Security Group

Ensure your EC2 security group has the following inbound rules:

| Type        | Protocol | Port Range | Source      | Description                    |
|-------------|----------|------------|-------------|--------------------------------|
| SSH         | TCP      | 22         | Your IP     | SSH access                     |
| Custom TCP  | TCP      | 5000       | 0.0.0.0/0   | Site24x7 CLI AI Agent Web UI  |

### 5. Access Your Application

After successful deployment:
- **Web Interface**: `http://your-ec2-public-ip:5000`
- **Configuration**: `http://your-ec2-public-ip:5000/config`
- **Dashboard**: `http://your-ec2-public-ip:5000/dashboard`

## Configuration

### GitHub Integration
1. Visit: https://github.com/settings/tokens
2. Create a Personal Access Token with these scopes:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
   - `write:packages` (Upload packages to GitHub Package Registry)
3. Enter the token in the web configuration interface

### AI Configuration (Optional)
- **OpenAI**: Enter your OpenAI API key for GPT-4 powered analysis
- **Local LLM**: Configure a local LLM endpoint with OpenAI API compatibility

## Production Considerations

### SSL/HTTPS Setup
```bash
# Install Certbot for Let's Encrypt
sudo apt install certbot nginx -y

# Configure Nginx as reverse proxy
sudo tee /etc/nginx/sites-available/site24x7-agent << 'EOF'
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable site and get SSL certificate
sudo ln -s /etc/nginx/sites-available/site24x7-agent /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d your-domain.com
```

### Domain Configuration
1. Point your domain to the EC2 instance's public IP
2. Update security group to allow HTTP (80) and HTTPS (443)
3. Configure SSL certificate using the commands above

### Auto-Start on Boot
```bash
# Create systemd service
sudo tee /etc/systemd/system/site24x7-agent.service << 'EOF'
[Unit]
Description=Site24x7 CLI AI Agent
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ubuntu/site24x7-cli-ai-agent
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=ubuntu

[Install]
WantedBy=multi-user.target
EOF

# Enable auto-start
sudo systemctl enable site24x7-agent
sudo systemctl start site24x7-agent
```

## Cost Optimization

### Instance Sizing
- **Development**: t3.micro (1GB RAM) - May be slow
- **Light Usage**: t3.small (2GB RAM) - Recommended minimum
- **Production**: t3.medium (4GB RAM) - Better performance

### Storage Optimization
- Use GP3 storage for better price/performance
- Monitor disk usage with CloudWatch
- Consider EBS snapshots for backups

### Monitoring and Alerts
```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb

# Configure monitoring (requires IAM role)
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
```

## Troubleshooting

### Application Not Accessible
1. **Check Security Group**: Ensure port 5000 is open
2. **Verify Application**: `curl http://localhost:5000/api/v1/status`
3. **Check Logs**: `docker-compose logs -f`

### Build Failures
1. **Network Issues**: Try running on a different AWS region
2. **Disk Space**: Ensure at least 10GB free space
3. **Memory**: Increase instance size if build fails

### Performance Issues
1. **Monitor Resources**: `htop` or `docker stats`
2. **Check Logs**: Look for memory/CPU warnings
3. **Scale Up**: Use larger instance type

## Management Commands

```bash
# View application status
docker-compose ps

# View logs
docker-compose logs -f

# Restart application
docker-compose restart

# Stop application
docker-compose down

# Update application
cd site24x7-cli-ai-agent
git pull origin main
docker-compose up -d --build

# Backup data
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# Clean up Docker resources
docker system prune -a
```

## Security Best Practices

1. **Regular Updates**: Keep OS and Docker updated
2. **Firewall**: Use AWS Security Groups restrictively
3. **SSH Keys**: Use key-based authentication, disable password auth
4. **Monitoring**: Enable CloudTrail and VPC Flow Logs  
5. **Backups**: Regular snapshots of EBS volumes
6. **Secrets**: Use AWS Secrets Manager for API keys

## Estimated Costs

**Monthly costs (us-east-1):**
- t3.small instance: ~$15-20/month
- 20GB GP3 storage: ~$2/month
- Data transfer: ~$1-5/month (depending on usage)

**Total**: ~$18-27/month for light to moderate usage

Use the AWS Pricing Calculator for precise estimates based on your usage patterns.