"""
Configuration management for Site24x7 CLI AI Agent
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Database
    database_url: str = Field(default="sqlite:///site24x7_agent.db")
    
    # GitHub Configuration
    github_token: str = Field(default_factory=lambda: os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", ""))
    github_username: Optional[str] = Field(default=None)
    github_repo_name: str = Field(default="site24x7-cli")
    
    # Site24x7 Configuration
    site24x7_api_base: str = Field(default="https://www.site24x7.com/api/")
    site24x7_docs_url: str = Field(default="https://www.site24x7.com/help/api/")
    
    # OpenAI Configuration
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = Field(default="gpt-4o")  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
    
    # Scheduler Configuration
    scraper_interval_hours: int = Field(default=6)
    maintenance_interval_hours: int = Field(default=24)
    
    # Security
    secret_key: str = Field(default_factory=lambda: os.getenv("SECRET_KEY", "site24x7-cli-agent-secret-key"))
    
    # Logging
    log_level: str = Field(default="INFO")
    
    # Local Development
    debug: bool = Field(default=False)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global settings instance
settings = Settings()
