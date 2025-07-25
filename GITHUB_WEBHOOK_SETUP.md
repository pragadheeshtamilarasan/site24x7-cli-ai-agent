# GitHub Webhook and Notification Setup

This guide explains how to configure your GitHub repository (`pragadheeshtamilarasan/site24x7-cli`) to automatically notify the AI agent when manual intervention is needed.

## Overview

The AI agent will:
1. **Automatically scrape** `https://www.site24x7.com/help/api/` every 6 hours
2. **Generate updated CLI code** when API changes are detected
3. **Push changes** to your `site24x7-cli` repository
4. **Handle PRs and Issues** automatically with AI responses
5. **Notify you** when manual intervention is required

## Required GitHub Configuration

### 1. Personal Access Token (GitHub Token)

Create a GitHub Personal Access Token with these permissions:

**Repository Permissions:**
- ✅ `repo` (Full control of private repositories)
- ✅ `workflow` (Update GitHub Actions workflows)
- ✅ `write:packages` (Upload packages to GitHub Package Registry)

**Account Permissions:**
- ✅ `read:user` (Read user profile data)
- ✅ `user:email` (Access user email addresses)

**Steps to create:**
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Select the permissions above
4. Copy the token and add it to your AI agent environment as `GITHUB_PERSONAL_ACCESS_TOKEN`

### 2. Repository Webhooks for Real-time Notifications

Configure webhooks in your `site24x7-cli` repository to notify the agent:

**Webhook URL:** `https://your-agent-domain.com/webhooks/github`
**Content type:** `application/json`
**Secret:** Use a strong secret and set it as `GITHUB_WEBHOOK_SECRET` in agent environment

**Events to subscribe to:**
- ✅ `issues` - New issues created, comments added
- ✅ `pull_request` - PRs opened, synchronized, reviewed
- ✅ `issue_comment` - Comments on issues and PRs  
- ✅ `pull_request_review` - PR reviews submitted
- ✅ `release` - New releases published
- ✅ `push` - When someone pushes to main/master branch
- ✅ `fork` - Repository forked
- ✅ `watch` - Repository starred/watched

### 3. Repository Settings for AI Agent

**Branch Protection Rules (Recommended):**
- Protect `main` branch
- Require PR reviews for direct pushes
- Allow the AI agent to bypass restrictions using token permissions

**Issue Templates:**
Create `.github/ISSUE_TEMPLATE/` with:
- `bug_report.md` - For bug reports
- `feature_request.md` - For feature requests  
- `api_change.md` - For Site24x7 API changes

**PR Templates:**
Create `.github/PULL_REQUEST_TEMPLATE.md` for consistent PR format

## Required Environment Variables

Set these in your AI agent environment:

```bash
# GitHub Configuration
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token_here
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here

# OpenAI for intelligent responses
OPENAI_API_KEY=your_openai_key_here

# Notification endpoints (optional)
SLACK_WEBHOOK_URL=your_slack_webhook_for_alerts
EMAIL_SMTP_CONFIG=your_email_config_for_alerts
```

## Automatic Notifications

The agent will automatically notify you when:

### High Priority (Immediate Notification)
- **Build failures** after pushing generated code
- **API breaking changes** that require manual review
- **Security issues** detected in dependencies
- **Rate limit warnings** from GitHub or Site24x7 APIs

### Medium Priority (Daily Summary)
- **New issues** requiring clarification
- **Complex PRs** that need human review
- **Community feedback** on CLI features
- **Performance degradation** detected

### Low Priority (Weekly Summary)  
- **Usage statistics** and popular features
- **Optimization opportunities** discovered
- **Community growth** metrics

## Webhook Implementation

The agent includes webhook endpoints for real-time GitHub events:

**Available endpoints:**
- `POST /webhooks/github` - GitHub webhook events
- `POST /webhooks/site24x7` - Site24x7 API change notifications (if available)
- `GET /webhooks/status` - Webhook health check

**Example webhook payload handling:**
```json
{
  "action": "opened",
  "issue": {
    "title": "CLI crashes when using --debug flag",
    "body": "When I run site24x7-cli --debug, it crashes...",
    "labels": ["bug", "priority:high"]
  }
}
```

## Manual Intervention Triggers

The agent will request manual intervention for:

### Code Review Required
- Changes to core CLI architecture
- New authentication methods
- Breaking changes to existing commands

### Policy Decisions  
- Controversial feature requests
- License or legal questions
- Major dependency updates

### Technical Escalation
- Unresolvable merge conflicts
- Complex API deprecations
- Performance issues requiring deep analysis

## Testing the Setup

1. **Test webhook delivery:**
   ```bash
   curl -X POST https://your-agent-domain.com/webhooks/github \
     -H "Content-Type: application/json" \
     -H "X-GitHub-Event: ping" \
     -d '{"zen": "Test webhook"}'
   ```

2. **Test GitHub API access:**
   - Create a test issue in your repository
   - Verify the agent responds automatically
   - Check the agent logs for successful authentication

3. **Test notification delivery:**
   - Create a high-priority issue
   - Verify you receive the notification
   - Test response time and accuracy

## Monitoring and Maintenance

**Agent Health Monitoring:**
- Dashboard at `/dashboard` shows system status
- API endpoint `/api/v1/status` for external monitoring
- Logs available at `/logs` for debugging

**Performance Metrics:**
- API scraping frequency and success rate
- GitHub API usage and rate limit status
- Response time to issues and PRs
- Code generation accuracy metrics

## Security Considerations

**Token Security:**
- Store GitHub token in secure environment variables
- Rotate tokens regularly (quarterly recommended)
- Use repository-scoped tokens when possible

**Webhook Security:**
- Validate webhook signatures using the secret
- Filter events to only process expected ones
- Rate limit webhook endpoints to prevent abuse

**AI Responses:**
- Review generated code before merging
- Set up approval workflows for sensitive changes
- Monitor for unusual patterns in AI behavior