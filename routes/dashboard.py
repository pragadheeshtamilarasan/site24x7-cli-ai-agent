"""
Dashboard Routes for Site24x7 CLI AI Agent
Web interface for monitoring and controlling the AI agent
"""

import logging
from typing import Dict, Any
from datetime import datetime

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from database import (
    ConfigurationManager, TaskLogger, GitHubOperationLogger,
    APISnapshotManager, CLIVersionManager
)

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    try:
        # Get system status
        system_status = await _get_system_status()
        
        # Get recent activity
        recent_logs = TaskLogger.get_recent_logs(10)
        recent_github_ops = GitHubOperationLogger.get_recent_operations(10)
        
        # Get configuration
        config = ConfigurationManager.get_all()
        
        context = {
            "request": request,
            "system_status": system_status,
            "recent_logs": recent_logs,
            "recent_github_ops": recent_github_ops,
            "config": config,
            "current_time": datetime.utcnow().isoformat()
        }
        
        return templates.TemplateResponse("dashboard.html", context)
        
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(status_code=500, detail="Dashboard unavailable")

@router.get("/config", response_class=HTMLResponse)
async def config_page(request: Request):
    """Configuration management page"""
    try:
        configs = ConfigurationManager.get_all()
        success_message = request.query_params.get('updated')
        
        context = {
            "request": request,
            "configs": configs,
            "success_message": "Configuration updated successfully!" if success_message else None
        }
        
        return templates.TemplateResponse("config_new.html", context)
        
    except Exception as e:
        logger.error(f"Config page error: {e}")
        raise HTTPException(status_code=500, detail="Configuration page unavailable")

@router.post("/config")
async def update_config(request: Request):
    """Update configuration from new UI form"""
    from fastapi.responses import RedirectResponse
    
    try:
        form_data = await request.form()
        
        # Convert form data to configuration updates
        config_updates = {}
        
        # Handle AI provider selection
        if form_data.get('ai_provider') == 'local':
            config_updates['use_local_llm'] = True
        else:
            config_updates['use_local_llm'] = False
        
        # Handle all other form fields
        field_mappings = {
            'github_token': 'github_token',
            'github_repo_name': 'github_repo_name', 
            'github_username': 'github_username',
            'github_polling_interval': 'github_polling_interval',
            'openai_api_key': 'openai_api_key',
            'openai_model': 'openai_model',
            'openai_base_url': 'openai_base_url',
            'local_api_key': 'local_api_key',
            'local_model': 'local_model',
            'site24x7_docs_url': 'site24x7_docs_url',
            'scraper_interval_hours': 'scraper_interval_hours',
            'maintenance_interval_hours': 'maintenance_interval_hours',
            'notification_email': 'notification_email',
            'slack_webhook_url': 'slack_webhook_url'
        }
        
        for form_field, config_key in field_mappings.items():
            value = form_data.get(form_field, '').strip()
            if value:
                # Convert numeric fields
                if config_key in ['scraper_interval_hours', 'maintenance_interval_hours', 'github_polling_interval']:
                    config_updates[config_key] = int(value)
                else:
                    config_updates[config_key] = value
        
        # Handle boolean checkboxes
        boolean_fields = [
            'enable_auto_deployment',
            'enable_issue_auto_response', 
            'enable_pr_auto_merge',
            'debug_mode'
        ]
        
        for field in boolean_fields:
            config_updates[field] = bool(form_data.get(field))
        
        # Save all configuration updates
        for key, value in config_updates.items():
            ConfigurationManager.set(key, value)
        
        # Log configuration update
        TaskLogger.log(
            "configuration",
            "updated", 
            "Configuration updated via new UI",
            {"updated_fields": list(config_updates.keys())}
        )
        
        # Redirect with success message
        return RedirectResponse(url="/config?updated=true", status_code=303)
        
    except Exception as e:
        logger.error(f"Configuration update error: {e}")
        configs = ConfigurationManager.get_all()
        return templates.TemplateResponse("config_new.html", {
            "request": request,
            "configs": configs,
            "error_message": f"Failed to update configuration: {str(e)}"
        })

@router.get("/logs", response_class=HTMLResponse)
async def logs_page(request: Request):
    """System logs and workflow errors page"""
    try:
        # Get task logs (including errors)
        task_logs = TaskLogger.get_recent_logs(100)
        
        # Get GitHub operations
        github_ops = GitHubOperationLogger.get_recent_operations(50)
        
        # Get system status
        system_status = await _get_system_status()
        
        context = {
            "request": request,
            "task_logs": task_logs,
            "github_ops": github_ops,
            "system_status": system_status
        }
        
        return templates.TemplateResponse("logs.html", context)
        
    except Exception as e:
        logger.error(f"Logs page error: {e}")
        raise HTTPException(status_code=500, detail="Logs page unavailable")

@router.post("/config/update")
async def update_config_legacy(
    request: Request,
    github_token: str = Form(None),
    github_username: str = Form(None),
    site24x7_oauth_token: str = Form(None),
    openai_api_key: str = Form(None),
    openai_model_standard: str = Form("gpt-4o"),
    openai_base_url: str = Form(None),
    openai_model_local: str = Form(None),
    local_llm_api_key: str = Form(None),
    use_local_llm: str = Form("false"),
    scraper_interval_hours: int = Form(6),
    maintenance_interval_hours: int = Form(24)
):
    """Update configuration"""
    try:
        # Update configuration values
        if github_token:
            ConfigurationManager.set("github_token", github_token)
        
        if github_username:
            ConfigurationManager.set("github_username", github_username)
        
        if site24x7_oauth_token:
            ConfigurationManager.set("site24x7_oauth_token", site24x7_oauth_token)
        
        # Handle AI configuration based on LLM type
        use_local = use_local_llm.lower() == "true"
        ConfigurationManager.set("use_local_llm", use_local)
        
        if use_local:
            # Local LLM configuration
            if local_llm_api_key:
                ConfigurationManager.set("openai_api_key", local_llm_api_key)
            if openai_model_local:
                ConfigurationManager.set("openai_model", openai_model_local)
            if openai_base_url:
                ConfigurationManager.set("openai_base_url", openai_base_url)
        else:
            # OpenAI configuration
            if openai_api_key:
                ConfigurationManager.set("openai_api_key", openai_api_key)
            ConfigurationManager.set("openai_model", openai_model_standard)
            ConfigurationManager.set("openai_base_url", "")  # Clear base URL for OpenAI
        
        ConfigurationManager.set("scraper_interval_hours", scraper_interval_hours)
        ConfigurationManager.set("maintenance_interval_hours", maintenance_interval_hours)
        
        # Log configuration update
        TaskLogger.log(
            "configuration",
            "updated",
            "Configuration updated via web interface",
            {
                "updated_fields": [k for k, v in {
                    "github_token": github_token,
                    "github_username": github_username,
                    "site24x7_oauth_token": site24x7_oauth_token,
                    "openai_api_key": openai_api_key
                }.items() if v],
                "intervals": {
                    "scraper_interval_hours": scraper_interval_hours,
                    "maintenance_interval_hours": maintenance_interval_hours
                }
            }
        )
        
        return RedirectResponse(url="/config?updated=true", status_code=303)
        
    except Exception as e:
        logger.error(f"Config update error: {e}")
        raise HTTPException(status_code=500, detail="Configuration update failed")

@router.get("/logs", response_class=HTMLResponse)
async def logs_page(request: Request, limit: int = 100):
    """System logs page"""
    try:
        task_logs = TaskLogger.get_recent_logs(limit)
        github_ops = GitHubOperationLogger.get_recent_operations(limit)
        
        context = {
            "request": request,
            "task_logs": task_logs,
            "github_ops": github_ops,
            "limit": limit
        }
        
        return templates.TemplateResponse("logs.html", context)
        
    except Exception as e:
        logger.error(f"Logs page error: {e}")
        raise HTTPException(status_code=500, detail="Logs page unavailable")

@router.get("/status")
async def get_status():
    """Get current system status as JSON"""
    try:
        return await _get_system_status()
    except Exception as e:
        logger.error(f"Status endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Status unavailable")

@router.post("/actions/manual-update")
async def trigger_manual_update():
    """Manually trigger CLI update"""
    try:
        # Import here to avoid circular imports
        from main import scheduler_service
        
        if scheduler_service:
            result = await scheduler_service.trigger_manual_update()
            return result
        else:
            raise HTTPException(status_code=503, detail="Scheduler service not available")
            
    except Exception as e:
        logger.error(f"Manual update error: {e}")
        raise HTTPException(status_code=500, detail="Manual update failed")

@router.post("/actions/manual-maintenance")
async def trigger_manual_maintenance():
    """Manually trigger GitHub maintenance"""
    try:
        # Import here to avoid circular imports
        from main import scheduler_service
        
        if scheduler_service:
            result = await scheduler_service.trigger_manual_maintenance()
            return result
        else:
            raise HTTPException(status_code=503, detail="Scheduler service not available")
            
    except Exception as e:
        logger.error(f"Manual maintenance error: {e}")
        raise HTTPException(status_code=500, detail="Manual maintenance failed")

@router.get("/repository")
async def get_repository_info():
    """Get GitHub repository information"""
    try:
        from services.github_manager import GitHubManager
        
        github_manager = GitHubManager()
        repo_stats = await github_manager.get_repository_stats()
        
        return repo_stats
        
    except Exception as e:
        logger.error(f"Repository info error: {e}")
        raise HTTPException(status_code=500, detail="Repository information unavailable")

async def _get_system_status() -> Dict[str, Any]:
    """Get comprehensive system status"""
    try:
        # Get latest snapshots and versions
        latest_snapshot = APISnapshotManager.get_latest_snapshot()
        latest_cli_version = CLIVersionManager.get_latest_version()
        
        # Get recent logs for status analysis
        recent_logs = TaskLogger.get_recent_logs(20)
        recent_github_ops = GitHubOperationLogger.get_recent_operations(10)
        
        # Analyze system health
        health_status = "healthy"
        failed_tasks = [log for log in recent_logs if log['status'] == 'failed']
        if len(failed_tasks) > 5:  # More than 5 failed tasks recently
            health_status = "degraded"
        
        # Get scheduler status
        scheduler_status = "unknown"
        try:
            from main import scheduler_service
            if scheduler_service:
                scheduler_info = scheduler_service.get_status()
                scheduler_status = "running" if scheduler_info["running"] else "stopped"
            else:
                scheduler_status = "not_initialized"
        except:
            scheduler_status = "error"
        
        status = {
            "overall_health": health_status,
            "scheduler_status": scheduler_status,
            "api_documentation": {
                "last_scraped": latest_snapshot['created_at'] if latest_snapshot else None,
                "endpoints_count": latest_snapshot['endpoints_count'] if latest_snapshot else 0,
                "content_hash": latest_snapshot['content_hash'][:8] if latest_snapshot else None
            },
            "cli_version": {
                "latest_version": latest_cli_version['version'] if latest_cli_version else None,
                "generated_at": latest_cli_version['created_at'] if latest_cli_version else None,
                "endpoints_covered": latest_cli_version['endpoints_covered'] if latest_cli_version else 0,
                "github_commit": latest_cli_version['github_commit_sha'][:8] if latest_cli_version and latest_cli_version['github_commit_sha'] else None
            },
            "recent_activity": {
                "total_logs": len(recent_logs),
                "failed_tasks": len(failed_tasks),
                "github_operations": len(recent_github_ops),
                "last_activity": recent_logs[0]['created_at'] if recent_logs else None
            },
            "configuration": {
                "github_configured": bool(ConfigurationManager.get("github_token")),
                "site24x7_configured": bool(ConfigurationManager.get("site24x7_oauth_token")),
                "openai_configured": bool(ConfigurationManager.get("openai_api_key"))
            }
        }
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return {
            "overall_health": "error",
            "error": str(e)
        }
