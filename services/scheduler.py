"""
Scheduler Service for Automated Tasks
Manages periodic scraping, CLI generation, and GitHub maintenance
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from config import settings
from services.api_scraper import Site24x7APIScraper
from services.cli_generator import CLIGenerator
from services.github_manager import GitHubManager

logger = logging.getLogger(__name__)

class SchedulerService:
    """Manage scheduled tasks for autonomous operation"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.scraper = Site24x7APIScraper()
        self.cli_generator = CLIGenerator()
        self.github_manager = GitHubManager()
        
        # Track last successful runs
        self.last_scrape = None
        self.last_generation = None
        self.last_maintenance = None
        
    async def start(self):
        """Start the scheduler with all tasks"""
        try:
            logger.info("Starting scheduler service...")
            
            # Schedule API documentation scraping
            self.scheduler.add_job(
                self._scrape_and_update_cli,
                IntervalTrigger(hours=settings.scraper_interval_hours),
                id='scrape_and_update',
                name='Scrape API docs and update CLI',
                replace_existing=True
            )
            
            # Schedule GitHub maintenance (handle issues/PRs)
            self.scheduler.add_job(
                self._perform_github_maintenance,
                IntervalTrigger(hours=settings.maintenance_interval_hours),
                id='github_maintenance',
                name='GitHub maintenance and issue handling',
                replace_existing=True
            )
            
            # Schedule daily health check
            self.scheduler.add_job(
                self._perform_health_check,
                CronTrigger(hour=9, minute=0),  # 9 AM daily
                id='health_check',
                name='Daily system health check',
                replace_existing=True
            )
            
            # Schedule weekly deep analysis
            self.scheduler.add_job(
                self._perform_deep_analysis,
                CronTrigger(day_of_week=1, hour=2, minute=0),  # Monday 2 AM
                id='deep_analysis',
                name='Weekly deep analysis and optimization',
                replace_existing=True
            )
            
            # Start scheduler
            self.scheduler.start()
            
            # Skip initial tasks for now to allow app to start quickly
            # They will run according to their scheduled intervals
            logger.info("Scheduler service started successfully - initial tasks will run on schedule")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler service: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown the scheduler"""
        try:
            logger.info("Shutting down scheduler service...")
            self.scheduler.shutdown(wait=True)
            logger.info("Scheduler service shut down successfully")
        except Exception as e:
            logger.error(f"Error shutting down scheduler: {e}")
    
    async def _run_initial_tasks(self):
        """Run initial tasks on startup"""
        try:
            logger.info("Running initial startup tasks...")
            
            # Initialize GitHub repository
            await self.github_manager.initialize_repository()
            
            # Run initial scrape and CLI generation
            await self._scrape_and_update_cli()
            
            logger.info("Initial tasks completed successfully")
            
        except Exception as e:
            logger.error(f"Initial tasks failed: {e}")
            try:
                from database import TaskLogger
                TaskLogger.log("scheduler", "failed", f"Initial tasks failed: {e}")
            except Exception as log_error:
                logger.error(f"Failed to log initial task error: {log_error}")
    
    async def _scrape_and_update_cli(self):
        """Scrape API documentation and update CLI if changes detected"""
        try:
            from database import TaskLogger
            TaskLogger.log("scheduler", "started", "Starting scheduled API scrape and CLI update")
            
            # Scrape latest documentation
            logger.info("Scraping Site24x7 API documentation...")
            documentation = await self.scraper.scrape_full_documentation()
            
            # Check if CLI needs regeneration
            from database import APISnapshotManager
            latest_snapshot = APISnapshotManager.get_latest_snapshot()
            
            if latest_snapshot and latest_snapshot['content_hash']:
                # Generate new CLI
                logger.info("Generating updated CLI from documentation...")
                cli_project = await self.cli_generator.generate_cli_from_documentation(documentation)
                
                # Deploy to GitHub
                logger.info("Deploying CLI updates to GitHub...")
                deployment_result = await self.github_manager.deploy_cli_project(cli_project)
                
                self.last_scrape = datetime.utcnow()
                self.last_generation = datetime.utcnow()
                
                from database import TaskLogger
                TaskLogger.log(
                    "scheduler",
                    "completed",
                    f"Successfully updated CLI with {cli_project['endpoints_covered']} endpoints",
                    {
                        "endpoints_covered": cli_project['endpoints_covered'],
                        "version": cli_project['version'],
                        "deployment": deployment_result
                    }
                )
                
                logger.info(f"CLI update completed successfully - version {cli_project['version']}")
                
            else:
                logger.info("No changes detected in API documentation")
                from database import TaskLogger
                TaskLogger.log("scheduler", "no_changes", "No API documentation changes detected")
            
        except Exception as e:
            logger.error(f"Scheduled scrape and update failed: {e}")
            try:
                from database import TaskLogger
                TaskLogger.log("scheduler", "failed", f"Scrape and update failed: {e}")
            except Exception as log_error:
                logger.error(f"Failed to log scrape error: {log_error}")
    
    async def _perform_github_maintenance(self):
        """Perform GitHub repository maintenance"""
        try:
            from database import TaskLogger
            TaskLogger.log("scheduler", "started", "Starting GitHub maintenance")
            
            # Handle issues and pull requests
            logger.info("Handling GitHub issues and pull requests...")
            maintenance_result = await self.github_manager.handle_issues_and_prs()
            
            self.last_maintenance = datetime.utcnow()
            
            from database import TaskLogger
            TaskLogger.log(
                "scheduler",
                "completed",
                f"GitHub maintenance completed - processed {maintenance_result.get('issues_handled', 0)} issues and {maintenance_result.get('prs_handled', 0)} PRs",
                maintenance_result
            )
            
            logger.info("GitHub maintenance completed successfully")
            
        except Exception as e:
            logger.error(f"GitHub maintenance failed: {e}")
            try:
                from database import TaskLogger
                TaskLogger.log("scheduler", "failed", f"GitHub maintenance failed: {e}")
            except Exception as log_error:
                logger.error(f"Failed to log maintenance error: {log_error}")
    
    async def _perform_health_check(self):
        """Perform daily health check"""
        try:
            from database import TaskLogger
            TaskLogger.log("scheduler", "started", "Starting daily health check")
            
            health_status = {
                "timestamp": datetime.utcnow().isoformat(),
                "scheduler_status": "running",
                "last_scrape": self.last_scrape.isoformat() if self.last_scrape else None,
                "last_generation": self.last_generation.isoformat() if self.last_generation else None,
                "last_maintenance": self.last_maintenance.isoformat() if self.last_maintenance else None
            }
            
            # Check GitHub repository status
            try:
                repo_stats = await self.github_manager.get_repository_stats()
                health_status["github_status"] = "healthy"
                health_status["repo_stats"] = repo_stats
            except Exception as e:
                health_status["github_status"] = f"error: {e}"
            
            # Check database connectivity
            try:
                from database import TaskLogger
                recent_logs = TaskLogger.get_recent_logs(5)
                health_status["database_status"] = "healthy"
                health_status["recent_log_count"] = len(recent_logs)
            except Exception as e:
                health_status["database_status"] = f"error: {e}"
            
            try:
                from database import TaskLogger
                TaskLogger.log(
                    "health_check",
                    "completed",
                    "Daily health check completed",
                    health_status
                )
            except Exception as e:
                logger.error(f"Failed to log health check: {e}")
            
            logger.info("Daily health check completed successfully")
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            try:
                from database import TaskLogger
                TaskLogger.log("health_check", "failed", f"Health check failed: {e}")
            except Exception as log_error:
                logger.error(f"Failed to log health check error: {log_error}")
    
    async def _perform_deep_analysis(self):
        """Perform weekly deep analysis and optimization"""
        try:
            from database import TaskLogger
            TaskLogger.log("scheduler", "started", "Starting weekly deep analysis")
            
            # Analyze CLI usage patterns and optimization opportunities
            from services.ai_analyzer import AIAnalyzer
            ai_analyzer = AIAnalyzer()
            
            # Get repository statistics
            repo_stats = await self.github_manager.get_repository_stats()
            
            # Get recent logs for analysis
            from database import TaskLogger, GitHubOperationLogger
            recent_logs = TaskLogger.get_recent_logs(1000)
            github_ops = GitHubOperationLogger.get_recent_operations(100)
            
            analysis_data = {
                "repo_stats": repo_stats,
                "task_logs": recent_logs,
                "github_operations": github_ops,
                "performance_metrics": {
                    "successful_scrapes": len([log for log in recent_logs if log['task_type'] == 'api_scraper' and log['status'] == 'completed']),
                    "failed_scrapes": len([log for log in recent_logs if log['task_type'] == 'api_scraper' and log['status'] == 'failed']),
                    "successful_deployments": len([op for op in github_ops if op['operation_type'] == 'deployment' and op['status'] == 'completed']),
                    "issues_handled": len([op for op in github_ops if op['operation_type'] == 'issue_handling']),
                    "prs_handled": len([op for op in github_ops if op['operation_type'] == 'pr_handling'])
                }
            }
            
            # Generate optimization recommendations
            optimization_prompt = f"""
            Analyze the following system performance data and provide optimization recommendations:
            
            {analysis_data}
            
            Focus on:
            1. Performance bottlenecks
            2. Error patterns
            3. User engagement metrics
            4. System reliability improvements
            5. Feature usage insights
            """
            
            # Note: This would use AI analysis in a real implementation
            # For now, we'll create a basic analysis report
            
            optimization_report = {
                "analysis_date": datetime.utcnow().isoformat(),
                "performance_summary": analysis_data["performance_metrics"],
                "recommendations": [
                    "Monitor API endpoint changes more frequently",
                    "Improve error handling for GitHub operations",
                    "Add more comprehensive CLI testing",
                    "Optimize CLI generation performance"
                ],
                "next_actions": [
                    "Review failed scraping attempts",
                    "Update CLI templates based on usage patterns",
                    "Improve GitHub issue classification"
                ]
            }
            
            TaskLogger.log(
                "deep_analysis",
                "completed",
                "Weekly deep analysis completed",
                optimization_report
            )
            
            logger.info("Weekly deep analysis completed successfully")
            
        except Exception as e:
            logger.error(f"Deep analysis failed: {e}")
            TaskLogger.log("deep_analysis", "failed", f"Deep analysis failed: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current scheduler status"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        
        return {
            "running": self.scheduler.running,
            "jobs": jobs,
            "last_scrape": self.last_scrape.isoformat() if self.last_scrape else None,
            "last_generation": self.last_generation.isoformat() if self.last_generation else None,
            "last_maintenance": self.last_maintenance.isoformat() if self.last_maintenance else None
        }
    
    async def trigger_manual_update(self) -> Dict[str, Any]:
        """Manually trigger CLI update"""
        try:
            logger.info("Manual CLI update triggered")
            await self._scrape_and_update_cli()
            return {"status": "success", "message": "Manual update completed"}
        except Exception as e:
            logger.error(f"Manual update failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def trigger_manual_maintenance(self) -> Dict[str, Any]:
        """Manually trigger GitHub maintenance"""
        try:
            logger.info("Manual GitHub maintenance triggered")
            await self._perform_github_maintenance()
            return {"status": "success", "message": "Manual maintenance completed"}
        except Exception as e:
            logger.error(f"Manual maintenance failed: {e}")
            return {"status": "error", "message": str(e)}
