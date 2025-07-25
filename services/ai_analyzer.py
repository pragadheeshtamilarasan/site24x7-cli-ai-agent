"""
AI Analysis Service using OpenAI
Provides intelligent analysis for API documentation, issues, and pull requests
"""

import json
import logging
from typing import Dict, List, Any, Optional
import os

from openai import OpenAI

from config import settings

logger = logging.getLogger(__name__)

class AIAnalyzer:
    """AI-powered analysis service using OpenAI"""
    
    def __init__(self):
        self.use_local_llm = settings.use_local_llm
        self.base_url = settings.openai_base_url
        self.client = None
        
        if self.use_local_llm:
            # Configure for local LLM
            self.api_key = settings.local_api_key or "dummy-key"  # Some local LLMs don't need real keys
            self.model = settings.local_model
            
            if self.base_url:
                try:
                    logger.info(f"Initializing local LLM client with base URL: {self.base_url}")
                    self.client = OpenAI(
                        api_key=self.api_key,
                        base_url=self.base_url
                    )
                    logger.info(f"Local LLM client initialized successfully with model: {self.model}")
                except Exception as e:
                    logger.error(f"Failed to initialize local LLM client: {e}")
                    self.client = None
            else:
                logger.warning("Local LLM selected but no base URL provided - AI features will be disabled")
        else:
            # Configure for OpenAI
            self.api_key = settings.openai_api_key
            self.model = settings.openai_model
            
            if self.api_key:
                try:
                    logger.info("Initializing OpenAI client")
                    self.client = OpenAI(api_key=self.api_key)
                    logger.info("OpenAI client initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize OpenAI client: {e}")
                    self.client = None
            else:
                logger.warning("AI API key not provided - AI features will be disabled")
    
    def is_available(self) -> bool:
        """Check if AI services are available"""
        return self.client is not None
    
    async def analyze_api_structure(self, documentation: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze API documentation structure using AI"""
        if not self.is_available():
            logger.warning("AI analysis not available - using fallback structure")
            return self._get_fallback_structure(documentation)
            
        try:
            prompt = f"""
            Analyze the following Site24x7 API documentation and provide a structured analysis 
            for generating a comprehensive CLI tool. Focus on:
            
            1. Categorize all endpoints into logical groups
            2. Identify CRUD operations for each resource type
            3. Suggest hierarchical command structure
            4. Identify common parameters and patterns
            5. Suggest CLI command names and descriptions
            
            Documentation:
            {json.dumps(documentation, indent=2)}
            
            Please provide the analysis in JSON format with the following structure:
            {{
                "categories": [
                    {{
                        "name": "Category Name",
                        "description": "Category description",
                        "subcategories": [
                            {{
                                "name": "Subcategory Name",
                                "endpoint": "/api/endpoint",
                                "operations": ["create", "read", "update", "delete"],
                                "cli_commands": ["command-name"]
                            }}
                        ]
                    }}
                ],
                "common_parameters": {{
                    "authentication": ["oauth_token"],
                    "pagination": ["page", "limit"],
                    "filtering": ["status", "type"]
                }},
                "command_patterns": {{
                    "list": "site24x7 <category> <resource> list",
                    "get": "site24x7 <category> <resource> get <id>",
                    "create": "site24x7 <category> <resource> create [options]",
                    "update": "site24x7 <category> <resource> update <id> [options]",
                    "delete": "site24x7 <category> <resource> delete <id>"
                }}
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert CLI architect analyzing API documentation to design comprehensive command-line interfaces. Provide detailed, actionable analysis for CLI generation."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=4000
            )
            
            content = response.choices[0].message.content
            analysis = json.loads(content) if content else {}
            logger.info("Completed AI analysis of API structure")
            
            return analysis
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            # Return fallback structure
            return self._get_fallback_structure(documentation)
    
    async def analyze_github_issue(self, title: str, body: str) -> Dict[str, Any]:
        """Analyze GitHub issue using AI"""
        if not self.is_available():
            logger.warning("AI analysis not available - using fallback issue analysis")
            return self._get_fallback_issue_analysis(title, body)
            
        try:
            prompt = f"""
            Analyze the following GitHub issue for the Site24x7 CLI project and provide analysis:
            
            Title: {title}
            Body: {body}
            
            Please analyze and provide JSON response with:
            {{
                "type": "bug|feature|question|documentation",
                "priority": "low|medium|high|critical",
                "category": "cli|api|documentation|installation",
                "is_duplicate": false,
                "requires_code_changes": true,
                "estimated_complexity": "simple|moderate|complex",
                "suggested_labels": ["bug", "priority-medium"],
                "can_be_automated": true,
                "summary": "Brief summary of the issue"
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert software maintainer analyzing GitHub issues for a CLI project. Provide accurate classification and assessment."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content) if content else {
                "type": "question",
                "priority": "medium",
                "category": "general",
                "summary": "Issue analysis failed"
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze GitHub issue: {e}")
            return {
                "type": "question",
                "priority": "medium",
                "category": "general",
                "summary": "Issue analysis failed"
            }
    
    async def generate_issue_response(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate appropriate response to GitHub issue"""
        if not self.is_available():
            logger.warning("AI analysis not available - using fallback issue response")
            return self._get_fallback_issue_response(analysis)
            
        try:
            prompt = f"""
            Based on the following issue analysis, generate an appropriate response:
            
            Analysis: {json.dumps(analysis, indent=2)}
            
            Generate a helpful, professional response that:
            1. Acknowledges the issue
            2. Provides relevant information or solution if possible
            3. Asks for clarification if needed
            4. Sets appropriate expectations
            
            Respond in JSON format:
            {{
                "comment": "The response comment text",
                "labels": ["suggested", "labels"],
                "should_close": false,
                "follow_up_needed": true
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI maintainer responding to GitHub issues. Be professional, helpful, and accurate."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content) if content else {
                "comment": "Thank you for reporting this issue. I'll analyze it and provide an update soon.",
                "labels": ["needs-review"],
                "should_close": False
            }
            
        except Exception as e:
            logger.error(f"Failed to generate issue response: {e}")
            return {
                "comment": "Thank you for reporting this issue. I'll analyze it and provide an update soon.",
                "labels": ["needs-review"],
                "should_close": False
            }
    
    async def analyze_pull_request(self, title: str, body: str, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze pull request using AI"""
        if not self.is_available():
            logger.warning("AI analysis not available - using fallback PR analysis")
            return self._get_fallback_pr_analysis(title, body, files)
            
        try:
            prompt = f"""
            Analyze the following pull request for the Site24x7 CLI project:
            
            Title: {title}
            Description: {body}
            
            Files changed: {json.dumps(files, indent=2)}
            
            Provide analysis in JSON format:
            {{
                "type": "bugfix|feature|improvement|documentation",
                "impact": "low|medium|high",
                "code_quality": "good|needs_improvement|poor",
                "breaks_compatibility": false,
                "has_tests": false,
                "has_documentation": false,
                "security_concerns": false,
                "performance_impact": "none|positive|negative",
                "suggested_improvements": ["suggestion1", "suggestion2"],
                "overall_assessment": "approve|request_changes|needs_review"
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert code reviewer analyzing pull requests for a Python CLI project. Focus on code quality, security, and compatibility."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content) if content else {
                "type": "improvement",
                "impact": "medium",
                "overall_assessment": "needs_review"
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze pull request: {e}")
            return {
                "type": "improvement",
                "impact": "medium",
                "overall_assessment": "needs_review"
            }
    
    async def generate_pr_response(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate appropriate response to pull request"""
        if not self.is_available():
            logger.warning("AI analysis not available - using fallback PR response")
            return self._get_fallback_pr_response(analysis)
            
        try:
            prompt = f"""
            Based on the following PR analysis, generate an appropriate review response:
            
            Analysis: {json.dumps(analysis, indent=2)}
            
            Generate response in JSON format:
            {{
                "comment": "Review comment for the PR",
                "review_comment": "Detailed review feedback",
                "approve": false,
                "request_changes": false,
                "suggested_labels": ["improvement", "needs-tests"]
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a constructive code reviewer providing helpful feedback on pull requests."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content) if content else {
                "comment": "Thank you for the contribution! I'll review this thoroughly and provide feedback.",
                "approve": False,
                "request_changes": False
            }
            
        except Exception as e:
            logger.error(f"Failed to generate PR response: {e}")
            return {
                "comment": "Thank you for the contribution! I'll review this thoroughly and provide feedback.",
                "approve": False,
                "request_changes": False
            }
    
    async def generate_commit_message(self, changes: Dict[str, Any]) -> str:
        """Generate intelligent commit message based on changes"""
        if not self.is_available():
            logger.warning("AI analysis not available - using fallback commit message")
            return self._get_fallback_commit_message(changes)
            
        try:
            prompt = f"""
            Generate a concise, descriptive git commit message for the following changes:
            
            Changes: {json.dumps(changes, indent=2)}
            
            Follow conventional commit format where appropriate:
            - feat: new feature
            - fix: bug fix
            - docs: documentation
            - style: formatting
            - refactor: code restructuring
            - test: adding tests
            - chore: maintenance
            
            Provide just the commit message, no explanation.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at writing clear, concise git commit messages following best practices."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100
            )
            
            content = response.choices[0].message.content
            return content.strip() if content else "AI Update: CLI improvements and fixes"
            
        except Exception as e:
            logger.error(f"Failed to generate commit message: {e}")
            return "AI Update: CLI improvements and fixes"
    
    def _get_fallback_structure(self, documentation: Dict[str, Any]) -> Dict[str, Any]:
        """Provide fallback structure if AI analysis fails"""
        return {
            "categories": [
                {
                    "name": "Monitor Management",
                    "description": "Manage various types of monitors",
                    "subcategories": [
                        {
                            "name": "Website Monitors",
                            "endpoint": "/api/website_monitor",
                            "operations": ["create", "read", "update", "delete"],
                            "cli_commands": ["website"]
                        },
                        {
                            "name": "API Monitors", 
                            "endpoint": "/api/rest_api_monitor",
                            "operations": ["create", "read", "update", "delete"],
                            "cli_commands": ["api"]
                        }
                    ]
                },
                {
                    "name": "Reports",
                    "description": "Generate and retrieve reports",
                    "subcategories": [
                        {
                            "name": "Performance Reports",
                            "endpoint": "/api/reports/performance",
                            "operations": ["read"],
                            "cli_commands": ["performance"]
                        }
                    ]
                }
            ],
            "common_parameters": {
                "authentication": ["oauth_token"],
                "pagination": ["page", "limit"],
                "filtering": ["status", "type"]
            },
            "command_patterns": {
                "list": "site24x7 <category> <resource> list",
                "get": "site24x7 <category> <resource> get <id>",
                "create": "site24x7 <category> <resource> create [options]",
                "update": "site24x7 <category> <resource> update <id> [options]",
                "delete": "site24x7 <category> <resource> delete <id>"
            }
        }
    
    def _get_fallback_issue_analysis(self, title: str, body: str) -> Dict[str, Any]:
        """Provide fallback issue analysis when AI is not available"""
        # Simple keyword-based analysis
        issue_type = "question"
        priority = "medium"
        category = "general"
        
        if any(word in title.lower() or word in body.lower() for word in ["bug", "error", "fail", "crash", "broken"]):
            issue_type = "bug"
            priority = "high"
        elif any(word in title.lower() or word in body.lower() for word in ["feature", "enhancement", "improve", "add"]):
            issue_type = "feature"
        elif any(word in title.lower() or word in body.lower() for word in ["doc", "documentation", "readme"]):
            issue_type = "documentation"
            category = "documentation"
        
        return {
            "type": issue_type,
            "priority": priority,
            "category": category,
            "is_duplicate": False,
            "requires_code_changes": issue_type in ["bug", "feature"],
            "estimated_complexity": "moderate",
            "suggested_labels": [issue_type, f"priority-{priority}"],
            "can_be_automated": False,
            "summary": f"Automated analysis: {issue_type} issue requiring review"
        }
    
    def _get_fallback_issue_response(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Provide fallback issue response when AI is not available"""
        return {
            "comment": "Thank you for reporting this issue. Our automated system has categorized this as a " + 
                      analysis.get("type", "general") + " issue. We'll review it and provide updates soon.",
            "labels": analysis.get("suggested_labels", ["needs-review"]),
            "should_close": False,
            "follow_up_needed": True
        }
    
    def _get_fallback_pr_analysis(self, title: str, body: str, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Provide fallback PR analysis when AI is not available"""
        pr_type = "improvement"
        if any(word in title.lower() for word in ["fix", "bug", "error"]):
            pr_type = "bugfix"
        elif any(word in title.lower() for word in ["feat", "feature", "add"]):
            pr_type = "feature"
        elif any(word in title.lower() for word in ["doc", "documentation"]):
            pr_type = "documentation"
        
        return {
            "type": pr_type,
            "impact": "medium",
            "code_quality": "needs_review",
            "breaks_compatibility": False,
            "has_tests": any("test" in f.get("filename", "").lower() for f in files),
            "has_documentation": any("readme" in f.get("filename", "").lower() or "doc" in f.get("filename", "").lower() for f in files),
            "security_concerns": False,
            "performance_impact": "none",
            "suggested_improvements": ["Please ensure tests are included", "Consider adding documentation"],
            "overall_assessment": "needs_review"
        }
    
    def _get_fallback_pr_response(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Provide fallback PR response when AI is not available"""
        return {
            "comment": "Thank you for this contribution! Our automated system has identified this as a " + 
                      analysis.get("type", "improvement") + ". We'll review the changes and provide feedback.",
            "review_comment": "Automated review: Please ensure tests and documentation are included where appropriate.",
            "approve": False,
            "request_changes": False,
            "suggested_labels": [analysis.get("type", "improvement"), "needs-review"]
        }
    
    def _get_fallback_commit_message(self, changes: Dict[str, Any]) -> str:
        """Provide fallback commit message when AI is not available"""
        return "chore: Update Site24x7 CLI with automated changes"
    

