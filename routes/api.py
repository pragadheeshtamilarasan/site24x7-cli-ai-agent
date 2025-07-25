"""
API Routes for Site24x7 CLI AI Agent
RESTful API endpoints for external integration and control
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from database import (
    ConfigurationManager, TaskLogger, GitHubOperationLogger,
    APISnapshotManager, CLIVersionManager
)
from services.api_scraper import Site24x7APIScraper
from services.cli_generator import CLIGenerator
from services.github_manager import GitHubManager

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models for API requests/responses
class ConfigUpdate(BaseModel):
    github_token: Optional[str] = None
    github_username: Optional[str] = None
    site24x7_oauth_token: Optional[str] = None
    openai_api_key: Optional[str] = None
    scraper_interval_hours: Optional[int] = None
    maintenance_interval_hours: Optional[int] = None

class SystemStatus(BaseModel):
    overall_health: str
    scheduler_status: str
    api_documentation: Dict[str, Any]
    cli_version: Dict[str, Any]
    recent_activity: Dict[str, Any]
    configuration: Dict[str, Any]

class TaskLog(BaseModel):
    id: int
    task_type: str
    status: str
    message: Optional[str]
    details: Optional[str]
    created_at: str

class GitHubOperation(BaseModel):
    id: int
    operation_type: str
    status: str
    commit_sha: Optional[str]
    message: Optional[str]
    details: Optional[str]
    created_at: str

@router.get("/status", response_model=SystemStatus)
async def get_system_status():
    """Get comprehensive system status"""
    try:
        from routes.dashboard import _get_system_status
        status = await _get_system_status()
        return status
    except Exception as e:
        logger.error(f"API status error: {e}")
        raise HTTPException(status_code=500, detail="System status unavailable")

@router.get("/logs/tasks", response_model=List[TaskLog])
async def get_task_logs(limit: int = Query(default=100, le=1000)):
    """Get recent task logs"""
    try:
        logs = TaskLogger.get_recent_logs(limit)
        return logs
    except Exception as e:
        logger.error(f"API task logs error: {e}")
        raise HTTPException(status_code=500, detail="Task logs unavailable")

@router.get("/logs/github", response_model=List[GitHubOperation])
async def get_github_operations(limit: int = Query(default=50, le=500)):
    """Get recent GitHub operations"""
    try:
        operations = GitHubOperationLogger.get_recent_operations(limit)
        return operations
    except Exception as e:
        logger.error(f"API GitHub logs error: {e}")
        raise HTTPException(status_code=500, detail="GitHub operations unavailable")

@router.get("/config")
async def get_configuration():
    """Get current configuration (sensitive values masked)"""
    try:
        config = ConfigurationManager.get_all()
        
        # Mask sensitive values
        masked_config = {}
        sensitive_keys = ['github_token', 'site24x7_oauth_token', 'openai_api_key']
        
        for key, value in config.items():
            if key in sensitive_keys and value:
                masked_config[key] = f"***{value[-4:]}" if len(value) > 4 else "***"
            else:
                masked_config[key] = value
        
        return masked_config
    except Exception as e:
        logger.error(f"API config error: {e}")
        raise HTTPException(status_code=500, detail="Configuration unavailable")

@router.put("/config")
async def update_configuration(config_update: dict):
    """Update system configuration"""
    try:
        updated_fields = []
        
        if config_update.get("github_token") is not None:
            ConfigurationManager.set("github_token", config_update.get("github_token"))
            updated_fields.append("github_token")
        
        if config_update.get("github_username") is not None:
            ConfigurationManager.set("github_username", config_update.get("github_username"))
            updated_fields.append("github_username")
        
        if config_update.get("site24x7_oauth_token") is not None:
            ConfigurationManager.set("site24x7_oauth_token", config_update.get("site24x7_oauth_token"))
            updated_fields.append("site24x7_oauth_token")
        
        if config_update.get("openai_api_key") is not None:
            ConfigurationManager.set("openai_api_key", config_update.get("openai_api_key"))
            updated_fields.append("openai_api_key")
        
        if config_update.get("openai_model") is not None:
            ConfigurationManager.set("openai_model", config_update.get("openai_model"))
            updated_fields.append("openai_model")
        
        if config_update.get("openai_base_url") is not None:
            ConfigurationManager.set("openai_base_url", config_update.get("openai_base_url"))
            updated_fields.append("openai_base_url")
        
        if config_update.get("use_local_llm") is not None:
            ConfigurationManager.set("use_local_llm", config_update.get("use_local_llm"))
            updated_fields.append("use_local_llm")
        
        if config_update.get("scraper_interval_hours") is not None:
            ConfigurationManager.set("scraper_interval_hours", config_update.get("scraper_interval_hours"))
            updated_fields.append("scraper_interval_hours")
        
        if config_update.get("maintenance_interval_hours") is not None:
            ConfigurationManager.set("maintenance_interval_hours", config_update.get("maintenance_interval_hours"))
            updated_fields.append("maintenance_interval_hours")
        
        # Log configuration update
        TaskLogger.log(
            "configuration",
            "updated",
            f"Configuration updated via API: {', '.join(updated_fields)}",
            {"updated_fields": updated_fields}
        )
        
        return {
            "status": "success",
            "message": f"Updated {len(updated_fields)} configuration fields",
            "updated_fields": updated_fields
        }
        
    except Exception as e:
        logger.error(f"API config update error: {e}")
        raise HTTPException(status_code=500, detail="Configuration update failed")

@router.post("/actions/scrape")
async def trigger_api_scrape():
    """Manually trigger API documentation scraping"""
    try:
        scraper = Site24x7APIScraper()
        documentation = await scraper.scrape_full_documentation()
        
        return {
            "status": "success",
            "message": "API documentation scraped successfully",
            "endpoints_count": len(documentation.get('endpoints', [])),
            "categories_count": len(documentation.get('categories', [])),
            "scraped_at": documentation.get('scraped_at')
        }
        
    except Exception as e:
        logger.error(f"API scrape trigger error: {e}")
        raise HTTPException(status_code=500, detail=f"API scraping failed: {str(e)}")

@router.post("/actions/generate-cli")
async def trigger_cli_generation():
    """Manually trigger CLI generation and GitHub deployment"""
    try:
        from services.scheduler import SchedulerService
        from services.cli_generator import CLIGenerator
        from services.github_manager import GitHubManager
        from database import APISnapshotManager, TaskLogger
        
        TaskLogger.log("api_action", "started", "Manual CLI generation triggered")
        
        # Get latest API snapshot
        latest_snapshot = APISnapshotManager.get_latest_snapshot()
        if not latest_snapshot:
            raise HTTPException(status_code=400, detail="No API documentation available. Please scrape first.")
        
        # Generate CLI from latest documentation
        cli_generator = CLIGenerator()
        
        # Parse the stored content back to documentation format
        import json
        import ast
        try:
            # First try to parse as JSON
            parsed_content = json.loads(latest_snapshot['content'])
            if isinstance(parsed_content, list):
                endpoints = parsed_content
            elif isinstance(parsed_content, dict) and 'endpoints' in parsed_content:
                endpoints = parsed_content['endpoints']
            else:
                endpoints = parsed_content
        except json.JSONDecodeError:
            try:
                # Try to parse as Python literal (string representation)
                parsed_content = ast.literal_eval(latest_snapshot['content'])
                if isinstance(parsed_content, dict) and 'endpoints' in parsed_content:
                    endpoints = parsed_content['endpoints']
                elif isinstance(parsed_content, list):
                    endpoints = parsed_content
                else:
                    endpoints = parsed_content
                logger.info("Successfully parsed API snapshot content as Python literal")
            except (ValueError, SyntaxError):
                # If both fail, create basic structure from endpoints count
                endpoints = []
                for i in range(min(latest_snapshot['endpoints_count'], 10)):
                    endpoints.append({
                        'path': f'/api/endpoint_{i}',
                        'methods': ['GET'],
                        'category': 'General API',
                        'name': f'Endpoint {i}',
                        'description': f'Site24x7 API endpoint {i}',
                        'parameters': [],
                        'auth_required': True,
                        'rate_limited': True
                    })
                logger.warning("Could not parse API snapshot content, using basic structure with endpoint placeholders")
        
        documentation = {
            'endpoints': endpoints,
            'scraped_at': latest_snapshot['created_at'],
            'endpoints_count': latest_snapshot['endpoints_count']
        }
        
        logger.info("Generating CLI from latest documentation...")
        cli_project = await cli_generator.generate_cli_from_documentation(documentation)
        
        # Deploy to GitHub if available
        github_manager = GitHubManager()
        if github_manager.initialized:
            logger.info("Deploying CLI to GitHub...")
            deployment_result = await github_manager.deploy_cli_project(cli_project)
            
            TaskLogger.log(
                "api_action",
                "completed",
                f"CLI generated and deployed with {cli_project['endpoints_covered']} endpoints",
                {
                    "endpoints_covered": cli_project['endpoints_covered'],
                    "version": cli_project['version'],
                    "deployment": deployment_result
                }
            )
            
            return {
                "status": "success",
                "message": f"CLI generated and deployed successfully - version {cli_project['version']}",
                "endpoints_covered": cli_project['endpoints_covered'],
                "version": cli_project['version'],
                "deployment": deployment_result
            }
        else:
            TaskLogger.log(
                "api_action",
                "completed",
                f"CLI generated with {cli_project['endpoints_covered']} endpoints (no GitHub deployment)",
                {
                    "endpoints_covered": cli_project['endpoints_covered'],
                    "version": cli_project['version'],
                    "deployment": {"status": "skipped", "reason": "GitHub not configured"}
                }
            )
            
            return {
                "status": "success",
                "message": f"CLI generated successfully - version {cli_project['version']} (GitHub deployment skipped)",
                "endpoints_covered": cli_project['endpoints_covered'],
                "version": cli_project['version'],
                "deployment": {"status": "skipped", "reason": "GitHub not configured"}
            }
        
    except Exception as e:
        logger.error(f"CLI generation trigger error: {e}")
        TaskLogger.log("api_action", "failed", f"CLI generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"CLI generation failed: {str(e)}")

@router.post("/actions/trigger-github-poll")
async def trigger_github_poll():
    """Manually trigger GitHub polling for testing"""
    try:
        from main import scheduler_service
        
        # Get the scheduler service instance
        if not scheduler_service:
            return {"status": "error", "message": "Scheduler service not available"}
        
        # Get GitHub poller from scheduler
        github_poller = scheduler_service.github_poller
        if not github_poller:
            return {"status": "error", "message": "GitHub poller not initialized"}
        
        # Trigger manual poll
        results = await github_poller.poll_all_activity()
        
        return {
            "status": "success", 
            "message": "GitHub polling triggered successfully",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Manual GitHub poll failed: {e}")
        return {"status": "error", "message": f"GitHub polling failed: {str(e)}"}

@router.post("/test-config")
async def test_config(request: Request):
    """Test configuration settings"""
    try:
        form_data = await request.form()
        test_results = {}
        
        # Test GitHub token
        github_token = form_data.get('github_token', '').strip()
        if github_token:
            try:
                import requests
                headers = {'Authorization': f'token {github_token}'}
                response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
                if response.status_code == 200:
                    test_results['GitHub Authentication'] = {
                        'success': True,
                        'message': f"Connected as {response.json().get('login', 'Unknown')}"
                    }
                else:
                    test_results['GitHub Authentication'] = {
                        'success': False,
                        'message': f"GitHub API error: {response.status_code}"
                    }
            except Exception as e:
                test_results['GitHub Authentication'] = {
                    'success': False,
                    'message': f"Connection failed: {str(e)}"
                }
        else:
            test_results['GitHub Authentication'] = {
                'success': False,
                'message': "No GitHub token provided"
            }
        
        # Test OpenAI API
        openai_key = form_data.get('openai_api_key', '').strip()
        use_local_llm = form_data.get('ai_provider') == 'local'
        
        if use_local_llm:
            base_url = form_data.get('openai_base_url', '').strip()
            if base_url:
                try:
                    import requests
                    response = requests.get(f"{base_url.rstrip('/')}/models", timeout=10)
                    if response.status_code == 200:
                        test_results['Local LLM Connection'] = {
                            'success': True,
                            'message': f"Connected to local LLM at {base_url}"
                        }
                    else:
                        test_results['Local LLM Connection'] = {
                            'success': False,
                            'message': f"Local LLM error: {response.status_code}"
                        }
                except Exception as e:
                    test_results['Local LLM Connection'] = {
                        'success': False,
                        'message': f"Connection failed: {str(e)}"
                    }
            else:
                test_results['Local LLM Connection'] = {
                    'success': False,
                    'message': "No local LLM URL provided"
                }
        elif openai_key:
            try:
                import openai
                client = openai.OpenAI(api_key=openai_key)
                models = client.models.list()
                test_results['OpenAI API'] = {
                    'success': True,
                    'message': f"Connected - {len(models.data)} models available"
                }
            except Exception as e:
                test_results['OpenAI API'] = {
                    'success': False,
                    'message': f"API error: {str(e)}"
                }
        else:
            test_results['AI Configuration'] = {
                'success': False,
                'message': "No AI provider configured"
            }
        
        # Test Site24x7 documentation URL
        docs_url = form_data.get('site24x7_docs_url', '').strip()
        if docs_url:
            try:
                import requests
                response = requests.get(docs_url, timeout=10)
                if response.status_code == 200:
                    test_results['Site24x7 Documentation'] = {
                        'success': True,
                        'message': f"Documentation accessible - {len(response.text)} characters"
                    }
                else:
                    test_results['Site24x7 Documentation'] = {
                        'success': False,
                        'message': f"HTTP error: {response.status_code}"
                    }
            except Exception as e:
                test_results['Site24x7 Documentation'] = {
                    'success': False,
                    'message': f"Connection failed: {str(e)}"
                }
        
        return test_results
        
    except Exception as e:
        logger.error(f"Config test error: {e}")
        return {'error': {'success': False, 'message': f"Test failed: {str(e)}"}}

@router.post("/reset-config")
async def reset_config():
    """Reset configuration to defaults"""
    try:
        import sqlite3
        
        # Clear all existing configurations
        with sqlite3.connect("site24x7_agent.db") as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM configurations")
            conn.commit()
        
        # Reinitialize defaults
        ConfigurationManager.initialize_defaults()
        
        # Log the action
        TaskLogger.log(
            "configuration_reset",
            "completed",
            "Configuration reset to defaults via API"
        )
        
        return {
            "success": True,
            "message": "Configuration reset to defaults"
        }
        
    except Exception as e:
        logger.error(f"Config reset error: {e}")
        return {
            "success": False,
            "message": f"Reset failed: {str(e)}"
        }

@router.post("/actions/generate-cli")
async def trigger_cli_generation():
    """Manually trigger CLI generation from latest documentation"""
    try:
        # Get latest documentation
        latest_snapshot = APISnapshotManager.get_latest_snapshot()
        if not latest_snapshot:
            raise HTTPException(status_code=400, detail="No API documentation available")
        
        # Parse documentation
        import json
        documentation = json.loads(latest_snapshot['content'])
        
        # Generate CLI
        cli_generator = CLIGenerator()
        cli_project = await cli_generator.generate_cli_from_documentation(documentation)
        
        return {
            "status": "success",
            "message": "CLI generated successfully",
            "version": cli_project['version'],
            "files_count": len(cli_project['files']),
            "endpoints_covered": cli_project['endpoints_covered'],
            "generated_at": cli_project['generated_at']
        }
        
    except Exception as e:
        logger.error(f"CLI generation trigger error: {e}")
        raise HTTPException(status_code=500, detail=f"CLI generation failed: {str(e)}")

@router.post("/actions/deploy")
async def trigger_github_deployment():
    """Manually trigger GitHub deployment of latest CLI"""
    try:
        # Get latest CLI version
        latest_cli = CLIVersionManager.get_latest_version()
        if not latest_cli:
            raise HTTPException(status_code=400, detail="No CLI version available")
        
        # Parse CLI project
        import json
        cli_project = json.loads(latest_cli['content'])
        
        # Deploy to GitHub
        github_manager = GitHubManager()
        deployment_result = await github_manager.deploy_cli_project(cli_project)
        
        return {
            "status": "success",
            "message": "CLI deployed to GitHub successfully",
            "deployment": deployment_result
        }
        
    except Exception as e:
        logger.error(f"GitHub deployment trigger error: {e}")
        raise HTTPException(status_code=500, detail=f"GitHub deployment failed: {str(e)}")

@router.post("/actions/full-update")
async def trigger_full_update():
    """Trigger complete update cycle: scrape → generate → deploy"""
    try:
        # Import scheduler service
        from main import scheduler_service
        
        if not scheduler_service:
            raise HTTPException(status_code=503, detail="Scheduler service not available")
        
        result = await scheduler_service.trigger_manual_update()
        return result
        
    except Exception as e:
        logger.error(f"Full update trigger error: {e}")
        raise HTTPException(status_code=500, detail=f"Full update failed: {str(e)}")

@router.post("/actions/github-maintenance")
async def trigger_github_maintenance():
    """Manually trigger GitHub maintenance (handle issues/PRs)"""
    try:
        from main import scheduler_service
        
        if not scheduler_service:
            raise HTTPException(status_code=503, detail="Scheduler service not available")
        
        result = await scheduler_service.trigger_manual_maintenance()
        return result
        
    except Exception as e:
        logger.error(f"GitHub maintenance trigger error: {e}")
        raise HTTPException(status_code=500, detail=f"GitHub maintenance failed: {str(e)}")

@router.get("/repository")
async def get_repository_info():
    """Get GitHub repository information and statistics"""
    try:
        github_manager = GitHubManager()
        repo_stats = await github_manager.get_repository_stats()
        return repo_stats
        
    except Exception as e:
        logger.error(f"Repository info error: {e}")
        raise HTTPException(status_code=500, detail="Repository information unavailable")

@router.get("/documentation/latest")
async def get_latest_documentation():
    """Get latest scraped API documentation"""
    try:
        latest_snapshot = APISnapshotManager.get_latest_snapshot()
        if not latest_snapshot:
            raise HTTPException(status_code=404, detail="No API documentation available")
        
        import json
        documentation = json.loads(latest_snapshot['content'])
        
        return {
            "snapshot_id": latest_snapshot['id'],
            "content_hash": latest_snapshot['content_hash'],
            "endpoints_count": latest_snapshot['endpoints_count'],
            "created_at": latest_snapshot['created_at'],
            "documentation": documentation
        }
        
    except Exception as e:
        logger.error(f"Latest documentation error: {e}")
        raise HTTPException(status_code=500, detail="Documentation unavailable")

@router.get("/cli/latest")
async def get_latest_cli():
    """Get latest generated CLI version"""
    try:
        latest_cli = CLIVersionManager.get_latest_version()
        if not latest_cli:
            raise HTTPException(status_code=404, detail="No CLI version available")
        
        import json
        cli_project = json.loads(latest_cli['content'])
        
        return {
            "version_id": latest_cli['id'],
            "version": latest_cli['version'],
            "endpoints_covered": latest_cli['endpoints_covered'],
            "github_commit_sha": latest_cli['github_commit_sha'],
            "created_at": latest_cli['created_at'],
            "files": list(cli_project['files'].keys()),
            "command_structure": cli_project.get('command_structure', {})
        }
        
    except Exception as e:
        logger.error(f"Latest CLI error: {e}")
        raise HTTPException(status_code=500, detail="CLI version unavailable")

@router.get("/scheduler")
async def get_scheduler_status():
    """Get detailed scheduler status and job information"""
    try:
        from main import scheduler_service
        
        if not scheduler_service:
            raise HTTPException(status_code=503, detail="Scheduler service not available")
        
        status = scheduler_service.get_status()
        return status
        
    except Exception as e:
        logger.error(f"Scheduler status error: {e}")
        raise HTTPException(status_code=500, detail="Scheduler status unavailable")

@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Quick health check
        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "Site24x7 CLI AI Agent",
            "version": "1.0.0"
        }
        
        # Check database connectivity
        try:
            recent_logs = TaskLogger.get_recent_logs(1)
            health_data["database"] = "connected"
        except Exception as e:
            health_data["database"] = f"error: {e}"
            health_data["status"] = "degraded"
        
        # Check scheduler
        try:
            from main import scheduler_service
            if scheduler_service and scheduler_service.scheduler.running:
                health_data["scheduler"] = "running"
            else:
                health_data["scheduler"] = "stopped"
                health_data["status"] = "degraded"
        except Exception as e:
            health_data["scheduler"] = f"error: {e}"
            health_data["status"] = "degraded"
        
        status_code = 200 if health_data["status"] == "healthy" else 503
        return health_data
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
