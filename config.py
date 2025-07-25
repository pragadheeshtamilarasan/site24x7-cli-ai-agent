"""
Configuration management for Site24x7 CLI AI Agent
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from fastapi import Request

class Settings(BaseSettings):
    """Application settings with database and environment variable support"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize database defaults on first run
        self._ensure_db_configs()
    
    def _ensure_db_configs(self):
        """Ensure database configurations are initialized"""
        try:
            from database import ConfigurationManager
            ConfigurationManager.initialize_defaults()
        except Exception as e:
            # Silent fail during initialization
            pass
    
    def get_config(self, key: str, default=None):
        """Get configuration from database with fallback to environment"""
        try:
            from database import ConfigurationManager
            return ConfigurationManager.get_with_env_fallback(key, default=default)
        except Exception:
            return default
    
    # Database
    database_url: str = Field(default="sqlite:///site24x7_agent.db")
    
    # GitHub Configuration - now sourced from database
    @property
    def github_token(self) -> str:
        return self.get_config('github_token', os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", ""))
    
    @property
    def github_username(self) -> Optional[str]:
        return self.get_config('github_username', None)
    
    @property
    def github_repo_name(self) -> str:
        return self.get_config('github_repo_name', "site24x7-cli")
    
    # Site24x7 Configuration
    @property
    def site24x7_docs_url(self) -> str:
        return self.get_config('site24x7_docs_url', "https://www.site24x7.com/help/api/")
    
    # AI Configuration
    @property
    def openai_api_key(self) -> str:
        return self.get_config('openai_api_key', os.getenv("OPENAI_API_KEY", ""))
    
    @property
    def openai_model(self) -> str:
        return self.get_config('openai_model', "gpt-4o")
    
    @property
    def openai_base_url(self) -> Optional[str]:
        return self.get_config('openai_base_url', os.getenv("OPENAI_BASE_URL", None))
    
    @property
    def use_local_llm(self) -> bool:
        return self.get_config('use_local_llm', False)
    
    @property
    def local_api_key(self) -> str:
        return self.get_config('local_api_key', "")
    
    @property
    def local_model(self) -> str:
        return self.get_config('local_model', "llama2")
    
    # Scheduler Configuration
    @property
    def scraper_interval_hours(self) -> int:
        return self.get_config('scraper_interval_hours', 6)
    
    @property
    def maintenance_interval_hours(self) -> int:
        return self.get_config('maintenance_interval_hours', 24)
    
    # Security
    secret_key: str = Field(default_factory=lambda: os.getenv("SECRET_KEY", "site24x7-cli-agent-secret-key"))
    
    @property
    def github_webhook_secret(self) -> str:
        return self.get_config('github_webhook_secret', os.getenv("GITHUB_WEBHOOK_SECRET", ""))
    
    # Logging
    log_level: str = Field(default="INFO")
    
    # Local Development
    @property
    def debug(self) -> bool:
        return self.get_config('debug_mode', False)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global settings instance
settings = Settings()
