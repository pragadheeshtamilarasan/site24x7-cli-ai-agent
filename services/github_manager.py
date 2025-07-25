"""
GitHub Repository Management Service
Handles autonomous GitHub repository creation and maintenance
"""

import os
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import base64

from github import Github, GithubException
try:
    import git
    GIT_AVAILABLE = True
except ImportError:
    git = None
    GIT_AVAILABLE = False

from config import settings
from database import GitHubOperationLogger, TaskLogger
from services.ai_analyzer import AIAnalyzer

logger = logging.getLogger(__name__)

class GitHubManager:
    """Manage GitHub repository operations for Site24x7 CLI"""
    
    def __init__(self):
        self.github_token = settings.github_token
        self.github = None
        self.user = None
        self.repo_name = settings.github_repo_name
        self.repo = None
        self.ai_analyzer = AIAnalyzer()
        self.initialized = False
        
        if self.github_token:
            try:
                self.github = Github(self.github_token)
                self.user = self.github.get_user()
                self.initialized = True
                logger.info("GitHub manager initialized successfully")
                
                # Try to initialize repository immediately
                try:
                    self.repo = self.user.get_repo(self.repo_name)
                    logger.info(f"Repository connected: {self.repo.full_name}")
                except Exception as repo_e:
                    logger.warning(f"Repository connection failed: {repo_e}")
                    
            except Exception as e:
                logger.warning(f"GitHub initialization failed: {e}")
                self.github = None
                self.user = None
        else:
            logger.warning("GitHub token not provided - GitHub features will be disabled")
        
    async def initialize_repository(self) -> Dict[str, Any]:
        """Initialize or get existing repository"""
        if not self.initialized:
            return {"error": "GitHub not initialized - token not provided"}
            
        try:
            TaskLogger.log("github_manager", "started", "Initializing GitHub repository")
            
            # Try to get existing repository
            try:
                self.repo = self.user.get_repo(self.repo_name)
                GitHubOperationLogger.log("repository", "found", message="Found existing repository")
                logger.info(f"Found existing repository: {self.repo.full_name}")
            except GithubException as e:
                if e.status == 404:
                    # Repository doesn't exist, create it
                    self.repo = await self._create_repository()
                else:
                    raise e
            
            repo_info = {
                'name': self.repo.name,
                'full_name': self.repo.full_name,
                'url': self.repo.html_url,
                'clone_url': self.repo.clone_url,
                'ssh_url': self.repo.ssh_url,
                'default_branch': self.repo.default_branch,
                'created_at': self.repo.created_at.isoformat(),
                'updated_at': self.repo.updated_at.isoformat(),
                'stars': self.repo.stargazers_count,
                'forks': self.repo.forks_count
            }
            
            TaskLogger.log(
                "github_manager", 
                "completed", 
                "Repository initialized successfully",
                repo_info
            )
            
            return repo_info
            
        except Exception as e:
            logger.error(f"Failed to initialize repository: {e}")
            TaskLogger.log("github_manager", "failed", str(e))
            GitHubOperationLogger.log("repository", "failed", message=str(e))
            raise
    
    async def _create_repository(self) -> Any:
        """Create new GitHub repository"""
        try:
            logger.info(f"Creating new repository: {self.repo_name}")
            
            repo = self.github.get_user().create_repo(
                name=self.repo_name,
                description="Site24x7 CLI - Comprehensive monitoring and management tool (AI-maintained)",
                auto_init=True,
                has_issues=True,
                has_projects=True,
                has_wiki=True,
                homepage="https://www.site24x7.com",
                private=False
            )
            
            # Create initial README
            initial_readme = self._generate_initial_readme()
            repo.create_file(
                "README.md",
                "Initial commit: AI-maintained Site24x7 CLI project",
                initial_readme,
                branch="main"
            )
            
            GitHubOperationLogger.log(
                "repository", 
                "created", 
                message="Created new repository",
                details={'repo_name': self.repo_name, 'url': repo.html_url}
            )
            
            logger.info(f"Created repository: {repo.full_name}")
            return repo
            
        except Exception as e:
            logger.error(f"Failed to create repository: {e}")
            raise
    
    def _generate_initial_readme(self) -> str:
        """Generate initial README for the repository"""
        return f"""# Site24x7 CLI

![AI Maintained](https://img.shields.io/badge/Maintained%20by-AI-blue.svg)
![Site24x7](https://img.shields.io/badge/Site24x7-CLI-green.svg)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)

## 🤖 AI-Maintained Project

This repository is **autonomously created and maintained by AI**. The CLI is automatically generated from the latest Site24x7 API documentation and updated regularly.

## Overview

Comprehensive command-line interface for Site24x7 monitoring platform, covering all 300+ API endpoints across 15+ categories including:

- **Monitor Management**: Website, API, DNS, SSL, Domain monitoring
- **AWS Monitoring**: EC2, RDS, Lambda, S3, CloudFront and more
- **Reporting**: Performance, uptime, availability reports
- **User Management**: Users, groups, on-call schedules
- **MSP Operations**: Multi-tenant customer management

## Installation

```bash
pip install site24x7-cli
```

## Quick Start

```bash
# Configure your API key
site24x7 config set-token YOUR_API_TOKEN

# List all monitors
site24x7 monitors list

# Create a website monitor
site24x7 monitors create-website --url https://example.com --name "My Website"
```

## Features

- Complete API coverage for all Site24x7 services
- Intuitive command structure and help system
- JSON output for automation and scripting
- Configuration management
- Bulk operations support

## Documentation

For detailed usage instructions and API coverage, visit the [Site24x7 API Documentation](https://www.site24x7.com/help/api/).

## AI Maintenance

This project is autonomously maintained by AI, which:
- Monitors Site24x7 API changes
- Updates CLI functionality automatically
- Handles issues and feature requests
- Maintains documentation

## License

This project is open source and available under the MIT License.
"""
    
    async def deploy_cli_project(self, cli_project: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy CLI project to GitHub repository"""
        try:
            TaskLogger.log("github_manager", "started", "Deploying CLI project to GitHub")
            
            if not self.repo:
                raise Exception("Repository not initialized")
            
            # Create/update CLI files
            deployment_results = []
            
            for file_path, content in cli_project.get('files', {}).items():
                try:
                    # Try to update existing file
                    try:
                        file_obj = self.repo.get_contents(file_path)
                        if isinstance(file_obj, list):
                            file_obj = file_obj[0]  # Take first file if it's a list
                        self.repo.update_file(
                            file_path,
                            f"AI Update: {file_path}",
                            content,
                            file_obj.sha,
                            branch="main"
                        )
                        deployment_results.append(f"Updated {file_path}")
                    except GithubException as e:
                        if e.status == 404:
                            # File doesn't exist, create it
                            self.repo.create_file(
                                file_path,
                                f"AI Create: {file_path}",
                                content,
                                branch="main"
                            )
                            deployment_results.append(f"Created {file_path}")
                        else:
                            raise e
                            
                except Exception as e:
                    logger.error(f"Failed to deploy {file_path}: {e}")
                    deployment_results.append(f"Failed {file_path}: {str(e)}")
            
            # Log successful deployment
            GitHubOperationLogger.log(
                "deployment",
                "completed",
                message="CLI project deployed successfully",
                details={
                    'files_deployed': len(cli_project.get('files', {})),
                    'results': deployment_results
                }
            )
            
            TaskLogger.log(
                "github_manager", 
                "completed", 
                "CLI project deployed successfully",
                {'files_count': len(cli_project.get('files', {}))}
            )
            
            return {
                'status': 'success',
                'files_deployed': len(cli_project.get('files', {})),
                'results': deployment_results
            }
            
        except Exception as e:
            logger.error(f"Failed to deploy CLI project: {e}")
            TaskLogger.log("github_manager", "failed", str(e))
            GitHubOperationLogger.log("deployment", "failed", message=str(e))
            raise
    
    async def handle_issues_and_prs(self) -> Dict[str, Any]:
        """Handle GitHub issues and pull requests using AI"""
        try:
            TaskLogger.log("github_manager", "started", "Handling GitHub issues and PRs")
            
            if not self.repo:
                raise Exception("Repository not initialized")
            
            results = {
                'issues_handled': 0,
                'prs_handled': 0,
                'actions': []
            }
            
            # Handle open issues
            open_issues = self.repo.get_issues(state='open')
            for issue in open_issues:
                try:
                    # Use AI to analyze and respond to issue
                    analysis = await self.ai_analyzer.analyze_github_issue(
                        issue.title,
                        issue.body or ""
                    )
                    
                    if analysis.get('response'):
                        issue.create_comment(analysis['response'])
                        results['actions'].append(f"Responded to issue #{issue.number}")
                    
                    if analysis.get('close_issue'):
                        issue.edit(state='closed')
                        results['actions'].append(f"Closed issue #{issue.number}")
                    
                    results['issues_handled'] += 1
                    
                except Exception as e:
                    logger.error(f"Failed to handle issue #{issue.number}: {e}")
                    results['actions'].append(f"Failed to handle issue #{issue.number}: {str(e)}")
            
            # Handle open pull requests
            open_prs = self.repo.get_pulls(state='open')
            for pr in open_prs:
                try:
                    # Use AI to review PR
                    analysis = await self.ai_analyzer.analyze_pull_request(
                        pr.title,
                        pr.body or "",
                        [{"filename": file.filename, "changes": file.changes} for file in pr.get_files()]
                    )
                    
                    if analysis.get('review_comment'):
                        pr.create_review(body=analysis['review_comment'])
                        results['actions'].append(f"Reviewed PR #{pr.number}")
                    
                    if analysis.get('merge_pr'):
                        pr.merge()
                        results['actions'].append(f"Merged PR #{pr.number}")
                    
                    results['prs_handled'] += 1
                    
                except Exception as e:
                    logger.error(f"Failed to handle PR #{pr.number}: {e}")
                    results['actions'].append(f"Failed to handle PR #{pr.number}: {str(e)}")
            
            GitHubOperationLogger.log(
                "maintenance",
                "completed",
                message="Handled GitHub issues and PRs",
                details=results
            )
            
            TaskLogger.log(
                "github_manager",
                "completed", 
                "GitHub issues and PRs handled",
                results
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to handle issues and PRs: {e}")
            TaskLogger.log("github_manager", "failed", str(e))
            raise
    
    async def get_repository_stats(self) -> Dict[str, Any]:
        """Get repository statistics and metrics"""
        try:
            if not self.repo:
                raise Exception("Repository not initialized")
            
            # Get basic repo stats
            stats = {
                'name': self.repo.name,
                'full_name': self.repo.full_name,
                'description': self.repo.description,
                'url': self.repo.html_url,
                'stars': self.repo.stargazers_count,
                'forks': self.repo.forks_count,
                'watchers': self.repo.watchers_count,
                'open_issues': self.repo.open_issues_count,
                'size': self.repo.size,
                'language': self.repo.language,
                'created_at': self.repo.created_at.isoformat(),
                'updated_at': self.repo.updated_at.isoformat(),
                'pushed_at': self.repo.pushed_at.isoformat() if self.repo.pushed_at else None,
                'default_branch': self.repo.default_branch,
                'has_issues': self.repo.has_issues,
                'has_projects': self.repo.has_projects,
                'has_wiki': self.repo.has_wiki,
                'archived': self.repo.archived,
                'disabled': self.repo.disabled,
                'private': self.repo.private
            }
            
            # Get commit activity
            try:
                commits = list(self.repo.get_commits())[:10]  # Last 10 commits
                stats['recent_commits'] = [
                    {
                        'sha': commit.sha[:8],
                        'message': commit.commit.message.split('\n')[0][:100],
                        'author': commit.commit.author.name,
                        'date': commit.commit.author.date.isoformat()
                    }
                    for commit in commits
                ]
            except Exception as e:
                logger.warning(f"Could not get commit stats: {e}")
                stats['recent_commits'] = []
            
            # Get contributors
            try:
                contributors = list(self.repo.get_contributors())[:5]  # Top 5 contributors
                stats['contributors'] = [
                    {
                        'login': contributor.login,
                        'contributions': contributor.contributions,
                        'avatar_url': contributor.avatar_url
                    }
                    for contributor in contributors
                ]
            except Exception as e:
                logger.warning(f"Could not get contributor stats: {e}")
                stats['contributors'] = []
            
            # Get language breakdown
            try:
                languages = self.repo.get_languages()
                stats['languages'] = dict(languages)
            except Exception as e:
                logger.warning(f"Could not get language stats: {e}")
                stats['languages'] = {}
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get repository stats: {e}")
            raise
