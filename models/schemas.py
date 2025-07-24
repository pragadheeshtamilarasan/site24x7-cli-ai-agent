"""
Pydantic models and schemas for Site24x7 CLI AI Agent
Data validation and serialization models
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator


class TaskStatus(str, Enum):
    """Task execution status"""
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
    NO_CHANGES = "no_changes"


class TaskType(str, Enum):
    """Task types"""
    API_SCRAPER = "api_scraper"
    CLI_GENERATOR = "cli_generator"
    GITHUB_MANAGER = "github_manager"
    SCHEDULER = "scheduler"
    CONFIGURATION = "configuration"
    HEALTH_CHECK = "health_check"
    DEEP_ANALYSIS = "deep_analysis"


class OperationType(str, Enum):
    """GitHub operation types"""
    REPOSITORY = "repository"
    DEPLOYMENT = "deployment"
    ISSUE_HANDLING = "issue_handling"
    PR_HANDLING = "pr_handling"
    COMMIT = "commit"
    RELEASE = "release"


class HealthStatus(str, Enum):
    """System health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    ERROR = "error"
    UNKNOWN = "unknown"


class SchedulerStatusEnum(str, Enum):
    """Scheduler status"""
    RUNNING = "running"
    STOPPED = "stopped"
    NOT_INITIALIZED = "not_initialized"
    ERROR = "error"


class APIEndpoint(BaseModel):
    """API endpoint model"""
    path: str = Field(..., description="API endpoint path")
    methods: List[str] = Field(default=["GET"], description="Supported HTTP methods")
    category: str = Field(..., description="Endpoint category")
    name: str = Field(..., description="Human-readable endpoint name")
    description: str = Field(..., description="Endpoint description")
    parameters: Dict[str, List[str]] = Field(default_factory=dict, description="Endpoint parameters")
    auth_required: bool = Field(default=True, description="Whether authentication is required")
    rate_limited: bool = Field(default=True, description="Whether endpoint is rate limited")


class APICategory(BaseModel):
    """API category model"""
    name: str = Field(..., description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    subcategories: List[Dict[str, Any]] = Field(default_factory=list, description="Subcategories")


class APIDocumentation(BaseModel):
    """Complete API documentation model"""
    base_url: str = Field(..., description="API base URL")
    version: str = Field(..., description="API version")
    authentication: Dict[str, str] = Field(..., description="Authentication details")
    categories: List[APICategory] = Field(..., description="API categories")
    endpoints: List[APIEndpoint] = Field(..., description="All API endpoints")
    http_methods: List[str] = Field(..., description="Supported HTTP methods")
    scraped_at: str = Field(..., description="Scraping timestamp")
    total_endpoints: int = Field(..., description="Total number of endpoints")


class CLICommand(BaseModel):
    """CLI command model"""
    name: str = Field(..., description="Command name")
    description: str = Field(..., description="Command description")
    operations: List[Dict[str, Any]] = Field(default_factory=list, description="Command operations")
    subcommands: Dict[str, 'CLICommand'] = Field(default_factory=dict, description="Subcommands")


class CLIProject(BaseModel):
    """Complete CLI project model"""
    version: str = Field(..., description="CLI version")
    files: Dict[str, str] = Field(..., description="Generated files")
    command_structure: CLICommand = Field(..., description="Command structure")
    endpoints_covered: int = Field(..., description="Number of endpoints covered")
    generated_at: str = Field(..., description="Generation timestamp")


class ConfigurationItem(BaseModel):
    """Configuration item model"""
    key: str = Field(..., description="Configuration key")
    value: Union[str, int, bool, Dict, List] = Field(..., description="Configuration value")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")


class TaskLog(BaseModel):
    """Task log model"""
    id: Optional[int] = Field(None, description="Log ID")
    task_type: TaskType = Field(..., description="Task type")
    status: TaskStatus = Field(..., description="Task status")
    message: Optional[str] = Field(None, description="Log message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")


class GitHubOperation(BaseModel):
    """GitHub operation model"""
    id: Optional[int] = Field(None, description="Operation ID")
    operation_type: OperationType = Field(..., description="Operation type")
    status: TaskStatus = Field(..., description="Operation status")
    commit_sha: Optional[str] = Field(None, description="Commit SHA")
    message: Optional[str] = Field(None, description="Operation message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")


class APISnapshot(BaseModel):
    """API documentation snapshot model"""
    id: Optional[int] = Field(None, description="Snapshot ID")
    content_hash: str = Field(..., description="Content hash")
    content: str = Field(..., description="Snapshot content")
    endpoints_count: int = Field(default=0, description="Number of endpoints")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")


class CLIVersion(BaseModel):
    """CLI version model"""
    id: Optional[int] = Field(None, description="Version ID")
    version: str = Field(..., description="Version string")
    content: str = Field(..., description="CLI project content")
    github_commit_sha: Optional[str] = Field(None, description="GitHub commit SHA")
    endpoints_covered: int = Field(default=0, description="Endpoints covered")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")


class SystemStatus(BaseModel):
    """System status model"""
    overall_health: HealthStatus = Field(..., description="Overall system health")
    scheduler_status: SchedulerStatusEnum = Field(..., description="Scheduler status")
    api_documentation: Dict[str, Any] = Field(..., description="API documentation status")
    cli_version: Dict[str, Any] = Field(..., description="CLI version information")
    recent_activity: Dict[str, Any] = Field(..., description="Recent activity summary")
    configuration: Dict[str, Any] = Field(..., description="Configuration status")


class RepositoryInfo(BaseModel):
    """GitHub repository information"""
    name: str = Field(..., description="Repository name")
    full_name: str = Field(..., description="Full repository name")
    url: str = Field(..., description="Repository URL")
    clone_url: str = Field(..., description="Clone URL")
    ssh_url: str = Field(..., description="SSH URL")
    default_branch: str = Field(..., description="Default branch")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Update timestamp")
    stars: int = Field(default=0, description="Star count")
    forks: int = Field(default=0, description="Fork count")


class ConfigurationUpdate(BaseModel):
    """Configuration update request"""
    github_token: Optional[str] = Field(None, description="GitHub personal access token")
    github_username: Optional[str] = Field(None, description="GitHub username")
    site24x7_oauth_token: Optional[str] = Field(None, description="Site24x7 OAuth token")
    openai_api_key: Optional[str] = Field(None, description="OpenAI/Local LLM API key")
    openai_model: Optional[str] = Field(None, description="OpenAI/Local LLM model name")
    openai_base_url: Optional[str] = Field(None, description="Local LLM base URL (for OpenAI compatibility)")
    use_local_llm: Optional[bool] = Field(None, description="Whether to use local LLM instead of OpenAI")
    scraper_interval_hours: Optional[int] = Field(None, ge=1, le=168, description="Scraper interval in hours")
    maintenance_interval_hours: Optional[int] = Field(None, ge=1, le=168, description="Maintenance interval in hours")

    @validator('scraper_interval_hours', 'maintenance_interval_hours')
    def validate_intervals(cls, v):
        if v is not None and (v < 1 or v > 168):
            raise ValueError('Interval must be between 1 and 168 hours')
        return v


class ActionResponse(BaseModel):
    """Action response model"""
    status: str = Field(..., description="Action status")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional response data")


class SchedulerJob(BaseModel):
    """Scheduler job model"""
    id: str = Field(..., description="Job ID")
    name: str = Field(..., description="Job name")
    next_run: Optional[str] = Field(None, description="Next run time")
    trigger: str = Field(..., description="Job trigger")


class SchedulerStatus(BaseModel):
    """Scheduler status model"""
    running: bool = Field(..., description="Whether scheduler is running")
    jobs: List[SchedulerJob] = Field(..., description="Scheduled jobs")
    last_scrape: Optional[str] = Field(None, description="Last scrape timestamp")
    last_generation: Optional[str] = Field(None, description="Last generation timestamp")
    last_maintenance: Optional[str] = Field(None, description="Last maintenance timestamp")


class AIAnalysis(BaseModel):
    """AI analysis result model"""
    categories: List[Dict[str, Any]] = Field(..., description="Analyzed categories")
    common_parameters: Dict[str, List[str]] = Field(..., description="Common parameters")
    command_patterns: Dict[str, str] = Field(..., description="Command patterns")
    analysis_timestamp: str = Field(..., description="Analysis timestamp")


class IssueAnalysis(BaseModel):
    """GitHub issue analysis model"""
    issue_type: str = Field(..., description="Issue type")
    priority: str = Field(..., description="Issue priority")
    category: str = Field(..., description="Issue category")
    is_duplicate: bool = Field(default=False, description="Whether issue is duplicate")
    requires_code_changes: bool = Field(default=True, description="Whether code changes are required")
    estimated_complexity: str = Field(..., description="Estimated complexity")
    suggested_labels: List[str] = Field(..., description="Suggested labels")
    can_be_automated: bool = Field(default=False, description="Whether issue can be automated")
    summary: str = Field(..., description="Issue summary")


class PullRequestAnalysis(BaseModel):
    """Pull request analysis model"""
    pr_type: str = Field(..., description="PR type")
    impact: str = Field(..., description="Impact level")
    code_quality: str = Field(..., description="Code quality assessment")
    breaks_compatibility: bool = Field(default=False, description="Whether PR breaks compatibility")
    has_tests: bool = Field(default=False, description="Whether PR includes tests")
    has_documentation: bool = Field(default=False, description="Whether PR includes documentation")
    security_concerns: bool = Field(default=False, description="Whether there are security concerns")
    performance_impact: str = Field(..., description="Performance impact")
    suggested_improvements: List[str] = Field(..., description="Suggested improvements")
    overall_assessment: str = Field(..., description="Overall assessment")


class DeploymentResult(BaseModel):
    """Deployment result model"""
    status: str = Field(..., description="Deployment status")
    commit_sha: Optional[str] = Field(None, description="Commit SHA")
    files_deployed: int = Field(default=0, description="Number of files deployed")
    deployment_url: Optional[str] = Field(None, description="Deployment URL")
    message: str = Field(..., description="Deployment message")


class HealthCheck(BaseModel):
    """Health check model"""
    status: str = Field(..., description="Health status")
    timestamp: str = Field(..., description="Check timestamp")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    database: Optional[str] = Field(None, description="Database status")
    scheduler: Optional[str] = Field(None, description="Scheduler status")
    error: Optional[str] = Field(None, description="Error message if unhealthy")


# Update forward references
CLICommand.model_rebuild()
