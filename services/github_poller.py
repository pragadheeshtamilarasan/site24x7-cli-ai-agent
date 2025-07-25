"""
GitHub Polling Service for Local Deployment
Periodically checks GitHub repository for new issues, PRs, and activity
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from database import ConfigurationManager, TaskLogger, GitHubOperationLogger

logger = logging.getLogger(__name__)

class GitHubPoller:
    """Poll GitHub repository for new activity instead of using webhooks"""
    
    def __init__(self):
        self.github = None
        self.repo = None
        self.last_check = {}
        self._initialize_github()
    
    def _initialize_github(self):
        """Initialize GitHub client"""
        try:
            github_token = ConfigurationManager.get_with_env_fallback('github_token', 'GITHUB_PERSONAL_ACCESS_TOKEN')
            if not github_token:
                logger.warning("No GitHub token available - polling disabled")
                return False
            
            from github import Github
            self.github = Github(github_token)
            
            # Get repository
            repo_name = ConfigurationManager.get('github_repo_name', 'site24x7-cli')
            github_username = ConfigurationManager.get('github_username')
            
            if github_username:
                full_repo_name = f"{github_username}/{repo_name}"
            else:
                # Try to get authenticated user's username
                user = self.github.get_user()
                full_repo_name = f"{user.login}/{repo_name}"
            
            self.repo = self.github.get_repo(full_repo_name)
            logger.info(f"GitHub poller initialized for repository: {full_repo_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize GitHub poller: {e}")
            return False
    
    async def poll_all_activity(self):
        """Poll for all types of GitHub activity"""
        if not self.github or not self.repo:
            logger.warning("GitHub not initialized - skipping poll")
            return
        
        try:
            results = {
                'issues': await self._poll_issues(),
                'pull_requests': await self._poll_pull_requests(), 
                'commits': await self._poll_commits(),
                'releases': await self._poll_releases(),
                'comments': await self._poll_comments()
            }
            
            # Log polling results
            total_new = sum(len(items) for items in results.values())
            if total_new > 0:
                TaskLogger.log(
                    "github_poll",
                    "completed",
                    f"Found {total_new} new GitHub activities",
                    results
                )
                logger.info(f"GitHub polling completed - {total_new} new activities found")
            
            return results
            
        except Exception as e:
            logger.error(f"GitHub polling error: {e}")
            TaskLogger.log("github_poll", "error", f"Polling failed: {str(e)}")
            return {}
    
    async def _poll_issues(self) -> List[Dict[str, Any]]:
        """Poll for new issues"""
        try:
            since = self._get_last_check('issues')
            issues = list(self.repo.get_issues(state='all', since=since))
            
            new_issues = []
            for issue in issues:
                if not issue.pull_request:  # Exclude PRs from issues
                    issue_data = {
                        'number': issue.number,
                        'title': issue.title,
                        'body': issue.body,
                        'state': issue.state,
                        'created_at': issue.created_at.isoformat(),
                        'updated_at': issue.updated_at.isoformat(),
                        'author': issue.user.login,
                        'labels': [label.name for label in issue.labels],
                        'assignees': [assignee.login for assignee in issue.assignees]
                    }
                    new_issues.append(issue_data)
                    
                    # Process new issue
                    await self._handle_new_issue(issue_data)
            
            self._update_last_check('issues')
            return new_issues
            
        except Exception as e:
            logger.error(f"Error polling issues: {e}")
            return []
    
    async def _poll_pull_requests(self) -> List[Dict[str, Any]]:
        """Poll for new pull requests"""
        try:
            since = self._get_last_check('pull_requests')
            pulls = list(self.repo.get_pulls(state='all', sort='updated', direction='desc'))
            
            new_prs = []
            for pr in pulls:
                if pr.updated_at >= since:
                    pr_data = {
                        'number': pr.number,
                        'title': pr.title,
                        'body': pr.body,
                        'state': pr.state,
                        'created_at': pr.created_at.isoformat(),
                        'updated_at': pr.updated_at.isoformat(),
                        'author': pr.user.login,
                        'head_ref': pr.head.ref,
                        'base_ref': pr.base.ref,
                        'mergeable': pr.mergeable,
                        'draft': pr.draft
                    }
                    new_prs.append(pr_data)
                    
                    # Process new/updated PR
                    await self._handle_new_pr(pr_data)
                else:
                    break  # PRs are sorted by updated date
            
            self._update_last_check('pull_requests')
            return new_prs
            
        except Exception as e:
            logger.error(f"Error polling pull requests: {e}")
            return []
    
    async def _poll_commits(self) -> List[Dict[str, Any]]:
        """Poll for new commits"""
        try:
            since = self._get_last_check('commits')
            commits = list(self.repo.get_commits(since=since))
            
            new_commits = []
            for commit in commits:
                commit_data = {
                    'sha': commit.sha,
                    'message': commit.commit.message,
                    'author': commit.commit.author.name,
                    'date': commit.commit.author.date.isoformat(),
                    'url': commit.html_url
                }
                new_commits.append(commit_data)
            
            self._update_last_check('commits')
            return new_commits
            
        except Exception as e:
            logger.error(f"Error polling commits: {e}")
            return []
    
    async def _poll_releases(self) -> List[Dict[str, Any]]:
        """Poll for new releases"""
        try:
            releases = list(self.repo.get_releases())
            since = self._get_last_check('releases')
            
            new_releases = []
            for release in releases:
                if release.created_at >= since:
                    release_data = {
                        'tag_name': release.tag_name,
                        'name': release.title,
                        'body': release.body,
                        'draft': release.draft,
                        'prerelease': release.prerelease,
                        'created_at': release.created_at.isoformat(),
                        'published_at': release.published_at.isoformat() if release.published_at else None,
                        'author': release.author.login if release.author else None
                    }
                    new_releases.append(release_data)
            
            self._update_last_check('releases')
            return new_releases
            
        except Exception as e:
            logger.error(f"Error polling releases: {e}")
            return []
    
    async def _poll_comments(self) -> List[Dict[str, Any]]:
        """Poll for new issue and PR comments"""
        try:
            since = self._get_last_check('comments')
            
            # Get issue comments
            issue_comments = []
            for issue in self.repo.get_issues(state='all', since=since):
                for comment in issue.get_comments():
                    if comment.created_at >= since:
                        comment_data = {
                            'type': 'issue_comment',
                            'issue_number': issue.number,
                            'comment_id': comment.id,
                            'body': comment.body,
                            'author': comment.user.login,
                            'created_at': comment.created_at.isoformat(),
                            'updated_at': comment.updated_at.isoformat()
                        }
                        issue_comments.append(comment_data)
                        
                        # Process new comment
                        await self._handle_new_comment(comment_data)
            
            self._update_last_check('comments')
            return issue_comments
            
        except Exception as e:
            logger.error(f"Error polling comments: {e}")
            return []
    
    async def _handle_new_issue(self, issue_data: Dict[str, Any]):
        """Handle a new issue"""
        try:
            # Check if auto-response is enabled
            auto_respond = ConfigurationManager.get('enable_issue_auto_response', True)
            if not auto_respond:
                return
            
            # Log the new issue
            GitHubOperationLogger.log(
                "issue_detected",
                "new",
                message=f"New issue #{issue_data['number']}: {issue_data['title']}",
                details=issue_data
            )
            
            logger.info(f"New issue detected: #{issue_data['number']} - {issue_data['title']}")
            
            # Generate AI response to the issue
            try:
                from services.ai_analyzer import AIAnalyzer
                ai_analyzer = AIAnalyzer()
                
                # Analyze the issue
                analysis = await ai_analyzer.analyze_github_issue(
                    issue_data.get('title', ''),
                    issue_data.get('body', '') or 'No description provided'
                )
                
                # Generate response
                response_data = await ai_analyzer.generate_issue_response(analysis)
                
                # Post the comment to GitHub
                if response_data.get('comment'):
                    await self._post_issue_comment(issue_data['number'], response_data['comment'])
                    
                    GitHubOperationLogger.log(
                        "issue_response",
                        "posted",
                        message=f"AI response posted to issue #{issue_data['number']}",
                        details={'analysis': analysis, 'response': response_data}
                    )
                    
                    logger.info(f"AI response posted to issue #{issue_data['number']}")
                
            except Exception as ai_error:
                logger.error(f"AI response generation failed for issue #{issue_data['number']}: {ai_error}")
                
                # Post a simple fallback response
                fallback_comment = """Thank you for opening this issue! 🤖

I'm the Site24x7 CLI AI agent, and I've detected your issue. While I'm currently having trouble generating a detailed response, I want to acknowledge that I've received your issue and it will be reviewed.

For immediate assistance with installation issues, please check:
1. The README.md file for installation instructions
2. The requirements.txt file for dependencies
3. Any error messages during installation

A human maintainer will review this issue soon."""
                
                try:
                    await self._post_issue_comment(issue_data['number'], fallback_comment)
                    logger.info(f"Fallback response posted to issue #{issue_data['number']}")
                except Exception as fallback_error:
                    logger.error(f"Failed to post fallback response: {fallback_error}")
            
        except Exception as e:
            logger.error(f"Error handling new issue: {e}")
    
    async def _handle_new_pr(self, pr_data: Dict[str, Any]):
        """Handle a new pull request"""
        try:
            # Log the new PR
            GitHubOperationLogger.log(
                "pull_request_detected",
                "new",
                message=f"PR #{pr_data['number']}: {pr_data['title']}",
                details=pr_data
            )
            
            # TODO: Integrate with AI analyzer for PR review
            logger.info(f"Pull request detected: #{pr_data['number']} - {pr_data['title']}")
            
        except Exception as e:
            logger.error(f"Error handling new PR: {e}")
    
    async def _handle_new_comment(self, comment_data: Dict[str, Any]):
        """Handle a new comment"""
        try:
            # Log the new comment
            GitHubOperationLogger.log(
                "comment_detected",
                "new",
                message=f"New comment on issue #{comment_data['issue_number']}",
                details=comment_data
            )
            
            logger.info(f"New comment on issue #{comment_data['issue_number']}")
            
        except Exception as e:
            logger.error(f"Error handling new comment: {e}")
    
    def _get_last_check(self, activity_type: str) -> datetime:
        """Get the last check time for an activity type"""
        if activity_type not in self.last_check:
            # Default to 24 hours ago for first run
            self.last_check[activity_type] = datetime.utcnow() - timedelta(hours=24)
        return self.last_check[activity_type]
    
    def _update_last_check(self, activity_type: str):
        """Update the last check time for an activity type"""
        self.last_check[activity_type] = datetime.utcnow()
    
    async def _post_issue_comment(self, issue_number: int, comment_text: str):
        """Post a comment to a GitHub issue"""
        try:
            issue = self.repo.get_issue(issue_number)
            comment = issue.create_comment(comment_text)
            logger.info(f"Comment posted to issue #{issue_number}: {comment.id}")
            return comment
        except Exception as e:
            logger.error(f"Failed to post comment to issue #{issue_number}: {e}")
            raise
    
    async def get_repository_stats(self) -> Dict[str, Any]:
        """Get current repository statistics"""
        if not self.repo:
            return {}
        
        try:
            return {
                'name': self.repo.name,
                'full_name': self.repo.full_name,
                'description': self.repo.description,
                'stars': self.repo.stargazers_count,
                'forks': self.repo.forks_count,
                'open_issues': self.repo.open_issues_count,
                'language': self.repo.language,
                'updated_at': self.repo.updated_at.isoformat(),
                'clone_url': self.repo.clone_url,
                'default_branch': self.repo.default_branch
            }
        except Exception as e:
            logger.error(f"Error getting repository stats: {e}")
            return {}