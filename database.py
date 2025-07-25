"""
Database configuration and models for Site24x7 CLI AI Agent
"""

import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

DATABASE_PATH = "site24x7_agent.db"

def init_db():
    """Initialize the database with required tables"""
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        
        # Configuration table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configurations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # API documentation snapshots
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_hash TEXT NOT NULL,
                content TEXT NOT NULL,
                endpoints_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Generated CLI versions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cli_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT NOT NULL,
                content TEXT NOT NULL,
                github_commit_sha TEXT,
                endpoints_covered INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Task execution logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_type TEXT NOT NULL,
                status TEXT NOT NULL,
                message TEXT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # GitHub operations log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS github_operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation_type TEXT NOT NULL,
                status TEXT NOT NULL,
                commit_sha TEXT,
                message TEXT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        logger.info("Database initialized successfully")

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

class ConfigurationManager:
    """Manage application configuration in database"""
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """Get configuration value"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM configurations WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                try:
                    return json.loads(row['value'])
                except json.JSONDecodeError:
                    return row['value']
            return default
    
    @staticmethod
    def set(key: str, value: Any) -> None:
        """Set configuration value"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            json_value = json.dumps(value) if not isinstance(value, str) else value
            cursor.execute("""
                INSERT OR REPLACE INTO configurations (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, json_value))
            conn.commit()
    
    @staticmethod
    def get_all() -> Dict[str, Any]:
        """Get all configuration values"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM configurations")
            configs = {}
            for row in cursor.fetchall():
                try:
                    configs[row['key']] = json.loads(row['value'])
                except json.JSONDecodeError:
                    configs[row['key']] = row['value']
            return configs
    
    @staticmethod
    def get_with_env_fallback(key: str, env_var: str = None, default: Any = None) -> Any:
        """Get config from database first, then fallback to environment variable"""
        import os
        
        # First try database
        db_value = ConfigurationManager.get(key)
        if db_value is not None and db_value != "":
            return db_value
        
        # Fallback to environment variable
        if env_var:
            env_value = os.getenv(env_var)
            if env_value:
                # Store in database for next time
                ConfigurationManager.set(key, env_value)
                return env_value
        
        return default
    
    @staticmethod
    def initialize_defaults():
        """Initialize default configurations if they don't exist"""
        import os
        
        default_configs = {
            'github_token': os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN', ''),
            'github_repo_name': 'site24x7-cli',
            'github_username': '',
            'openai_api_key': os.getenv('OPENAI_API_KEY', ''),
            'openai_model': 'gpt-4o',
            'openai_base_url': os.getenv('OPENAI_BASE_URL', ''),
            'use_local_llm': False,
            'local_api_key': os.getenv('LOCAL_API_KEY', ''),
            'local_model': os.getenv('LOCAL_MODEL', 'llama2'),
            'site24x7_docs_url': 'https://www.site24x7.com/help/api/',
            'scraper_interval_hours': 6,
            'maintenance_interval_hours': 24,
            'github_polling_interval': 15,
            'notification_email': '',
            'slack_webhook_url': '',
            'enable_auto_deployment': True,
            'enable_pr_auto_merge': False,
            'enable_issue_auto_response': True,
            'debug_mode': False
        }
        
        existing_configs = ConfigurationManager.get_all()
        
        for key, default_value in default_configs.items():
            if key not in existing_configs:
                # Only set if we have a non-empty default or environment value
                if default_value != "" and default_value is not None:
                    ConfigurationManager.set(key, default_value)

class APISnapshotManager:
    """Manage API documentation snapshots"""
    
    @staticmethod
    def save_snapshot(content: str, content_hash: str, endpoints_count: int = 0) -> int:
        """Save API documentation snapshot"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO api_snapshots (content_hash, content, endpoints_count)
                VALUES (?, ?, ?)
            """, (content_hash, content, endpoints_count))
            conn.commit()
            return cursor.lastrowid or 0
    
    @staticmethod
    def get_latest_snapshot() -> Optional[Dict[str, Any]]:
        """Get latest API snapshot"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM api_snapshots 
                ORDER BY created_at DESC 
                LIMIT 1
            """)
            row = cursor.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def has_content_changed(content_hash: str) -> bool:
        """Check if content has changed from last snapshot"""
        latest = APISnapshotManager.get_latest_snapshot()
        return latest is None or latest['content_hash'] != content_hash

class CLIVersionManager:
    """Manage CLI versions"""
    
    @staticmethod
    def save_version(version: str, content: str, commit_sha: Optional[str] = None, endpoints_covered: int = 0) -> int:
        """Save CLI version"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO cli_versions (version, content, github_commit_sha, endpoints_covered)
                VALUES (?, ?, ?, ?)
            """, (version, content, commit_sha, endpoints_covered))
            conn.commit()
            return cursor.lastrowid or 0
    
    @staticmethod
    def get_latest_version() -> Optional[Dict[str, Any]]:
        """Get latest CLI version"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM cli_versions 
                ORDER BY created_at DESC 
                LIMIT 1
            """)
            row = cursor.fetchone()
            return dict(row) if row else None

class TaskLogger:
    """Log task execution"""
    
    @staticmethod
    def log(task_type: str, status: str, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> int:
        """Log task execution"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            details_json = json.dumps(details) if details else None
            cursor.execute("""
                INSERT INTO task_logs (task_type, status, message, details)
                VALUES (?, ?, ?, ?)
            """, (task_type, status, message, details_json))
            conn.commit()
            return cursor.lastrowid or 0
    
    @staticmethod
    def get_recent_logs(limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent task logs"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM task_logs 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

class GitHubOperationLogger:
    """Log GitHub operations"""
    
    @staticmethod
    def log(operation_type: str, status: str, commit_sha: Optional[str] = None, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> int:
        """Log GitHub operation"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            details_json = json.dumps(details) if details else None
            cursor.execute("""
                INSERT INTO github_operations (operation_type, status, commit_sha, message, details)
                VALUES (?, ?, ?, ?, ?)
            """, (operation_type, status, commit_sha, message, details_json))
            conn.commit()
            return cursor.lastrowid or 0
    
    @staticmethod
    def get_recent_operations(limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent GitHub operations"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM github_operations 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
