"""
Utility functions and helpers for Site24x7 CLI AI Agent
Common functionality used across the application
"""

import hashlib
import json
import re
import os
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone
from pathlib import Path
import difflib


logger = logging.getLogger(__name__)


def generate_content_hash(content: str) -> str:
    """Generate MD5 hash of content"""
    if isinstance(content, dict) or isinstance(content, list):
        content = json.dumps(content, sort_keys=True)
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove control characters
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sanitized)
    # Limit length
    sanitized = sanitized[:255]
    # Ensure it's not empty or just dots
    if not sanitized or sanitized in ('.', '..'):
        sanitized = 'file'
    return sanitized


def sanitize_command_name(name: str) -> str:
    """Sanitize name for CLI command usage"""
    # Convert to lowercase and replace spaces/special chars with dashes
    sanitized = re.sub(r'[^a-zA-Z0-9\s]', '', name.lower())
    sanitized = re.sub(r'\s+', '-', sanitized.strip())
    # Remove multiple consecutive dashes
    sanitized = re.sub(r'-+', '-', sanitized)
    # Remove leading/trailing dashes
    sanitized = sanitized.strip('-')
    return sanitized or 'command'


def validate_github_token(token: str) -> bool:
    """Validate GitHub personal access token format"""
    if not token:
        return False
    
    # GitHub classic tokens start with ghp_, ghc_, gho_, ghr_, or ghs_
    # Fine-grained tokens start with github_pat_
    patterns = [
        r'^ghp_[a-zA-Z0-9]{36}$',  # Classic PAT
        r'^ghc_[a-zA-Z0-9]{36}$',  # Classic PAT (client)
        r'^gho_[a-zA-Z0-9]{36}$',  # Classic PAT (OAuth)
        r'^ghr_[a-zA-Z0-9]{36}$',  # Classic PAT (refresh)
        r'^ghs_[a-zA-Z0-9]{36}$',  # Classic PAT (server)
        r'^github_pat_[a-zA-Z0-9_]{82}$',  # Fine-grained PAT
    ]
    
    return any(re.match(pattern, token) for pattern in patterns)


def validate_openai_api_key(api_key: str) -> bool:
    """Validate OpenAI API key format"""
    if not api_key:
        return False
    
    # OpenAI API keys start with sk- followed by 48 characters
    pattern = r'^sk-[a-zA-Z0-9]{48}$'
    return bool(re.match(pattern, api_key))


def format_timestamp(timestamp: Union[str, datetime]) -> str:
    """Format timestamp for display"""
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            return timestamp
    
    if isinstance(timestamp, datetime):
        # Convert to UTC if timezone aware
        if timestamp.tzinfo is not None:
            timestamp = timestamp.astimezone(timezone.utc)
        return timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')
    
    return str(timestamp)


def get_current_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.utcnow().isoformat()


def parse_version_string(version: str) -> Dict[str, int]:
    """Parse version string into components"""
    try:
        # Handle versions like "1.20241225.1430"
        parts = version.split('.')
        if len(parts) >= 3:
            return {
                'major': int(parts[0]),
                'date': int(parts[1]) if parts[1].isdigit() else 0,
                'build': int(parts[2]) if parts[2].isdigit() else 0
            }
        elif len(parts) == 2:
            return {
                'major': int(parts[0]),
                'minor': int(parts[1]),
                'patch': 0
            }
        else:
            return {'major': int(parts[0]), 'minor': 0, 'patch': 0}
    except (ValueError, IndexError):
        return {'major': 1, 'minor': 0, 'patch': 0}


def generate_version_string() -> str:
    """Generate version string based on current date and time"""
    now = datetime.utcnow()
    return f"1.{now.strftime('%Y%m%d')}.{now.strftime('%H%M')}"


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two texts"""
    if not text1 or not text2:
        return 0.0
    
    matcher = difflib.SequenceMatcher(None, text1, text2)
    return matcher.ratio()


def extract_urls_from_text(text: str) -> List[str]:
    """Extract URLs from text"""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(url_pattern, text)


def extract_email_from_text(text: str) -> List[str]:
    """Extract email addresses from text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def clean_html_tags(text: str) -> str:
    """Remove HTML tags from text"""
    html_pattern = re.compile(r'<[^>]+>')
    return html_pattern.sub('', text)


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text"""
    # Replace multiple whitespace characters with single space
    text = re.sub(r'\s+', ' ', text)
    # Strip leading/trailing whitespace
    return text.strip()


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Flatten a nested dictionary"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely parse JSON string"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """Safely serialize object to JSON"""
    try:
        return json.dumps(obj, indent=2, default=str)
    except (TypeError, ValueError):
        return default


def ensure_directory_exists(path: Union[str, Path]) -> Path:
    """Ensure directory exists, create if it doesn't"""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return Path(filename).suffix.lower()


def is_text_file(filename: str) -> bool:
    """Check if file is a text file based on extension"""
    text_extensions = {
        '.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', 
        '.yaml', '.yml', '.ini', '.cfg', '.conf', '.log', '.sql', '.sh',
        '.bat', '.ps1', '.rst', '.tex', '.csv', '.tsv'
    }
    return get_file_extension(filename) in text_extensions


def count_lines_in_text(text: str) -> int:
    """Count number of lines in text"""
    if not text:
        return 0
    return len(text.splitlines())


def count_words_in_text(text: str) -> int:
    """Count number of words in text"""
    if not text:
        return 0
    return len(text.split())


def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """Extract code blocks from markdown-style text"""
    pattern = r'```(\w+)?\n(.*?)\n```'
    matches = re.findall(pattern, text, re.DOTALL)
    
    code_blocks = []
    for language, code in matches:
        code_blocks.append({
            'language': language or 'text',
            'code': code.strip()
        })
    
    return code_blocks


def validate_url(url: str) -> bool:
    """Validate URL format"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(url_pattern.match(url))


def mask_sensitive_value(value: str, visible_chars: int = 4) -> str:
    """Mask sensitive value showing only last few characters"""
    if not value or len(value) <= visible_chars:
        return "***"
    return f"***{value[-visible_chars:]}"


def generate_random_string(length: int = 10) -> str:
    """Generate random string for IDs or tokens"""
    import secrets
    import string
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks of specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def retry_with_backoff(func, max_retries: int = 3, base_delay: float = 1.0):
    """Decorator for retrying functions with exponential backoff"""
    import time
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                delay = base_delay * (2 ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                time.sleep(delay)
        
        return None
    
    return wrapper


def get_environment_info() -> Dict[str, Any]:
    """Get information about the current environment"""
    import platform
    import sys
    
    return {
        'python_version': sys.version,
        'platform': platform.platform(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'architecture': platform.architecture()[0],
        'hostname': platform.node(),
        'current_directory': os.getcwd(),
        'environment_variables': dict(os.environ)
    }


def log_function_call(func):
    """Decorator to log function calls"""
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed with error: {e}")
            raise
    
    return wrapper


class PerformanceTimer:
    """Context manager for measuring execution time"""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = datetime.utcnow()
        logger.debug(f"Starting {self.name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.utcnow()
        duration = (self.end_time - self.start_time).total_seconds() if self.start_time else 0
        
        if exc_type is None:
            logger.info(f"{self.name} completed in {duration:.2f} seconds")
        else:
            logger.error(f"{self.name} failed after {duration:.2f} seconds: {exc_val}")
    
    @property
    def duration(self) -> Optional[float]:
        """Get duration in seconds if timer has completed"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
