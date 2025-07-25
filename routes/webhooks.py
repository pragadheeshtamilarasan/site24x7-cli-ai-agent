"""
GitHub Webhook Handler for Site24x7 CLI AI Agent
Handles real-time notifications from GitHub repository events
"""

import hashlib
import hmac
import json
import logging
from typing import Dict, Any
from datetime import datetime

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from config import settings
from database import TaskLogger, GitHubOperationLogger
from services.github_manager import GitHubManager
from services.ai_analyzer import AIAnalyzer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks", tags=["webhooks"])

def verify_github_signature(payload_body: bytes, signature_header: str) -> bool:
    """Verify GitHub webhook signature"""
    if not settings.github_webhook_secret:
        logger.warning("GitHub webhook secret not configured - skipping signature verification")
        return True
    
    if not signature_header:
        return False
    
    hash_object = hmac.new(
        settings.github_webhook_secret.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    
    return hmac.compare_digest(expected_signature, signature_header)

async def handle_issue_event(payload: Dict[str, Any], github_manager: GitHubManager):
    """Handle issue-related events"""
    action = payload.get("action")
    issue = payload.get("issue", {})
    
    logger.info(f"Handling issue event: {action} for issue #{issue.get('number')}")
    
    if action == "opened":
        # New issue created - analyze and respond
        issue_title = issue.get("title", "")
        issue_body = issue.get("body", "")
        issue_labels = [label.get("name") for label in issue.get("labels", [])]
        
        # Check if this requires immediate attention
        high_priority_keywords = ["crash", "error", "urgent", "security", "breaking"]
        is_high_priority = any(keyword in issue_title.lower() or keyword in issue_body.lower() 
                              for keyword in high_priority_keywords)
        
        if is_high_priority:
            TaskLogger.log(
                "webhook_handler", 
                "high_priority_issue", 
                f"High priority issue detected: #{issue.get('number')} - {issue_title}",
                {"issue_number": issue.get('number'), "labels": issue_labels}
            )
        
        # Log for manual review - AI response can be implemented later
        TaskLogger.log(
            "webhook_handler",
            "issue_needs_response",
            f"Issue #{issue.get('number')} may need AI response: {issue_title[:100]}",
            {"issue_number": issue.get('number'), "priority": "high" if is_high_priority else "normal"}
        )
    
    elif action in ["edited", "labeled"]:
        # Issue updated - log for monitoring
        TaskLogger.log(
            "webhook_handler",
            "issue_updated", 
            f"Issue #{issue.get('number')} was {action}",
            {"issue_number": issue.get('number'), "action": action}
        )

async def handle_pull_request_event(payload: Dict[str, Any], github_manager: GitHubManager):
    """Handle pull request events"""
    action = payload.get("action")
    pr = payload.get("pull_request", {})
    
    logger.info(f"Handling PR event: {action} for PR #{pr.get('number')}")
    
    if action == "opened":
        # New PR created - analyze for conflicts or issues
        pr_title = pr.get("title", "")
        pr_body = pr.get("body", "")
        
        # Check if this is a generated PR from the agent
        if "automated CLI update" in pr_title.lower():
            # This is our own PR - minimal handling needed
            TaskLogger.log(
                "webhook_handler",
                "agent_pr_created", 
                f"Agent-generated PR created: #{pr.get('number')}"
            )
        else:
            # External PR - needs review
            TaskLogger.log(
                "webhook_handler",
                "external_pr_created",
                f"External PR requires review: #{pr.get('number')} - {pr_title}",
                {"pr_number": pr.get('number'), "author": pr.get("user", {}).get("login")}
            )
            
            # Log for manual review - automated PR review can be implemented later
            TaskLogger.log(
                "webhook_handler",
                "pr_needs_review",
                f"External PR #{pr.get('number')} needs review: {pr_title[:100]}",
                {"pr_number": pr.get('number'), "author": pr.get("user", {}).get("login")}
            )
    
    elif action == "review_requested":
        # Review requested - notify about manual intervention needed
        reviewer = payload.get("requested_reviewer", {}).get("login", "")
        TaskLogger.log(
            "webhook_handler",
            "review_requested",
            f"Manual review requested for PR #{pr.get('number')} from {reviewer}",
            {"pr_number": pr.get('number'), "reviewer": reviewer}
        )

async def handle_push_event(payload: Dict[str, Any], github_manager: GitHubManager):
    """Handle push events"""
    ref = payload.get("ref", "")
    commits = payload.get("commits", [])
    pusher = payload.get("pusher", {}).get("name", "")
    
    if ref == "refs/heads/main" or ref == "refs/heads/master":
        # Push to main branch
        logger.info(f"Push to main branch by {pusher} with {len(commits)} commits")
        
        # Check if this was pushed by the agent
        agent_keywords = ["automated", "cli update", "api changes", "site24x7-cli-ai-agent"]
        is_agent_push = any(keyword in commit.get("message", "").lower() 
                           for commit in commits for keyword in agent_keywords)
        
        if not is_agent_push:
            # External push to main - log for monitoring
            TaskLogger.log(
                "webhook_handler",
                "external_push",
                f"External push to main branch by {pusher}",
                {"commit_count": len(commits), "pusher": pusher}
            )
            
            # Schedule re-scraping to ensure we're up to date
            TaskLogger.log(
                "webhook_handler",
                "sync_requested",
                f"Immediate sync requested due to external push by {pusher}",
                {"pusher": pusher, "commit_count": len(commits)}
            )

async def handle_release_event(payload: Dict[str, Any]):
    """Handle release events"""
    action = payload.get("action")
    release = payload.get("release", {})
    
    if action == "published":
        # New release published
        tag_name = release.get("tag_name", "")
        release_name = release.get("name", "")
        
        TaskLogger.log(
            "webhook_handler",
            "release_published",
            f"New release published: {tag_name} - {release_name}",
            {"tag": tag_name, "name": release_name}
        )

@router.post("/github")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    """Handle GitHub webhook events"""
    try:
        # Get payload and headers
        payload_body = await request.body()
        signature = request.headers.get("X-Hub-Signature-256", "")
        event_type = request.headers.get("X-GitHub-Event", "")
        
        # Verify webhook signature
        if not verify_github_signature(payload_body, signature):
            logger.warning("Invalid webhook signature")
            raise HTTPException(status_code=403, detail="Invalid signature")
        
        # Parse payload
        try:
            payload = json.loads(payload_body.decode('utf-8'))
        except json.JSONDecodeError:
            logger.error("Invalid JSON payload")
            raise HTTPException(status_code=400, detail="Invalid JSON")
        
        logger.info(f"Received GitHub webhook: {event_type}")
        
        # Initialize GitHub manager for handling
        github_manager = None
        try:
            github_manager = GitHubManager()
        except Exception as e:
            logger.warning(f"GitHub manager initialization failed: {e}")
        
        # Handle different event types
        if event_type == "ping":
            logger.info("GitHub webhook ping received")
            return {"message": "pong"}
        
        elif event_type == "issues":
            if github_manager:
                background_tasks.add_task(handle_issue_event, payload, github_manager)
        
        elif event_type == "pull_request":
            if github_manager:
                background_tasks.add_task(handle_pull_request_event, payload, github_manager)
        
        elif event_type == "push":
            if github_manager:
                background_tasks.add_task(handle_push_event, payload, github_manager)
        
        elif event_type == "release":
            background_tasks.add_task(handle_release_event, payload)
        
        elif event_type == "issue_comment":
            # Handle comments on issues and PRs
            action = payload.get("action")
            if action == "created":
                comment = payload.get("comment", {})
                issue = payload.get("issue", {})
                
                # Check if this is a mention or requires response
                comment_body = comment.get("body", "")
                if "@" in comment_body:
                    TaskLogger.log(
                        "webhook_handler",
                        "mention_detected",
                        f"Mention detected in comment on issue #{issue.get('number')}",
                        {"issue_number": issue.get('number'), "comment_id": comment.get('id')}
                    )
        
        else:
            logger.info(f"Unhandled webhook event: {event_type}")
        
        # Log successful webhook processing
        GitHubOperationLogger.log(
            "webhook",
            "processed",
            message=f"Successfully processed {event_type} webhook"
        )
        
        return {"status": "success", "event": event_type}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/status")
async def webhook_status():
    """Health check endpoint for webhooks"""
    return {
        "status": "healthy",
        "service": "GitHub Webhook Handler",
        "timestamp": datetime.utcnow().isoformat(),
        "github_configured": bool(settings.github_token),
        "webhook_secret_configured": bool(getattr(settings, 'github_webhook_secret', None))
    }

@router.post("/site24x7")
async def site24x7_webhook(request: Request, background_tasks: BackgroundTasks):
    """Handle Site24x7 API change notifications (if available)"""
    try:
        payload = await request.json()
        
        logger.info("Received Site24x7 API change notification")
        
        # Log the API change notification
        TaskLogger.log(
            "webhook_handler",
            "api_change_notification",
            "Site24x7 API change notification received",
            payload
        )
        
        # Trigger immediate scraping and CLI update
        from services.scheduler import SchedulerService
        scheduler = SchedulerService()
        background_tasks.add_task(scheduler._scrape_and_update_cli)
        
        return {"status": "success", "message": "API change notification processed"}
    
    except Exception as e:
        logger.error(f"Site24x7 webhook error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")