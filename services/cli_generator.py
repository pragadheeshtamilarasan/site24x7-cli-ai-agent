"""
CLI Generator Service
Generates comprehensive Site24x7 CLI from API documentation
"""

import os
import json
import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

from config import settings
from database import CLIVersionManager, TaskLogger
from services.ai_analyzer import AIAnalyzer

logger = logging.getLogger(__name__)

class CLIGenerator:
    """Generate comprehensive CLI from Site24x7 API documentation"""
    
    def __init__(self):
        self.ai_analyzer = AIAnalyzer()
        self.template_env = Environment(loader=FileSystemLoader('cli_templates'))
        
    async def generate_cli_from_documentation(self, documentation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete CLI project from API documentation"""
        try:
            TaskLogger.log("cli_generator", "started", "Starting CLI generation from documentation")
            
            # Analyze documentation with AI
            analyzed_structure = await self.ai_analyzer.analyze_api_structure(documentation)
            
            # Generate CLI command structure
            command_structure = self._generate_command_structure(analyzed_structure)
            
            # Generate CLI files
            cli_files = await self._generate_cli_files(command_structure, documentation)
            
            # Generate supporting files
            supporting_files = self._generate_supporting_files(documentation)
            
            # Combine all files
            all_files = {**cli_files, **supporting_files}
            
            # Generate version string
            version = self._generate_version_string()
            
            cli_project = {
                'version': version,
                'files': all_files,
                'command_structure': command_structure,
                'endpoints_covered': len(documentation.get('endpoints', [])),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            # Save version
            CLIVersionManager.save_version(
                version,
                json.dumps(cli_project),
                endpoints_covered=len(documentation.get('endpoints', []))
            )
            
            TaskLogger.log(
                "cli_generator", 
                "completed", 
                f"Generated CLI with {len(all_files)} files covering {len(documentation.get('endpoints', []))} endpoints",
                {"version": version, "files_count": len(all_files)}
            )
            
            return cli_project
            
        except Exception as e:
            logger.error(f"Failed to generate CLI: {e}")
            TaskLogger.log("cli_generator", "failed", str(e))
            raise
    
    def _generate_command_structure(self, analyzed_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Generate hierarchical command structure"""
        structure = {
            'name': 'site24x7',
            'description': 'Site24x7 CLI - Comprehensive monitoring and management tool',
            'subcommands': {}
        }
        
        # Process categories
        for category in analyzed_structure.get('categories', []):
            category_name = self._sanitize_command_name(category['name'])
            
            structure['subcommands'][category_name] = {
                'name': category_name,
                'description': f"Manage {category['name']}",
                'subcommands': {}
            }
            
            # Process subcategories/endpoints
            for subcategory in category.get('subcategories', []):
                sub_name = self._sanitize_command_name(subcategory['name'])
                
                structure['subcommands'][category_name]['subcommands'][sub_name] = {
                    'name': sub_name,
                    'description': f"Manage {subcategory['name']}",
                    'operations': self._generate_crud_operations(subcategory)
                }
        
        return structure
    
    def _sanitize_command_name(self, name: str) -> str:
        """Sanitize name for use as CLI command"""
        # Convert to lowercase and replace spaces/special chars with dashes
        sanitized = re.sub(r'[^a-zA-Z0-9\s]', '', name.lower())
        sanitized = re.sub(r'\s+', '-', sanitized.strip())
        return sanitized
    
    def _generate_crud_operations(self, subcategory: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate CRUD operations for a subcategory"""
        operations = []
        base_endpoint = subcategory.get('endpoint', '')
        
        # Standard CRUD operations
        crud_ops = [
            {
                'name': 'list',
                'method': 'GET',
                'endpoint': base_endpoint,
                'description': f"List all {subcategory['name']}"
            },
            {
                'name': 'get',
                'method': 'GET', 
                'endpoint': f"{base_endpoint}/{{id}}",
                'description': f"Get specific {subcategory['name']} by ID"
            },
            {
                'name': 'create',
                'method': 'POST',
                'endpoint': base_endpoint,
                'description': f"Create new {subcategory['name']}"
            },
            {
                'name': 'update',
                'method': 'PUT',
                'endpoint': f"{base_endpoint}/{{id}}",
                'description': f"Update {subcategory['name']}"
            },
            {
                'name': 'delete',
                'method': 'DELETE',
                'endpoint': f"{base_endpoint}/{{id}}",
                'description': f"Delete {subcategory['name']}"
            }
        ]
        
        return crud_ops
    
    async def _generate_cli_files(self, command_structure: Dict[str, Any], documentation: Dict[str, Any]) -> Dict[str, str]:
        """Generate all CLI Python files"""
        files = {}
        
        # Generate main CLI file
        files['site24x7_cli/__init__.py'] = ''
        files['site24x7_cli/main.py'] = await self._generate_main_cli_file(command_structure)
        
        # Generate base classes
        files['site24x7_cli/base.py'] = self._generate_base_classes()
        files['site24x7_cli/auth.py'] = self._generate_auth_module()
        files['site24x7_cli/exceptions.py'] = self._generate_exceptions_module()
        files['site24x7_cli/utils.py'] = self._generate_utils_module()
        
        # Generate command modules
        command_files = await self._generate_command_modules(command_structure, documentation)
        files.update(command_files)
        
        return files
    
    async def _generate_main_cli_file(self, command_structure: Dict[str, Any]) -> str:
        """Generate main CLI entry point"""
        template = self.template_env.get_template('base_cli.py.j2')
        return template.render(
            command_structure=command_structure,
            version=self._generate_version_string()
        )
    
    def _generate_base_classes(self) -> str:
        """Generate base CLI classes"""
        return '''"""
Base classes for Site24x7 CLI
"""

import json
import os
from typing import Dict, Any, Optional
import click
import requests
from rich.console import Console
from rich.table import Table

console = Console()

class Site24x7Client:
    """Base client for Site24x7 API interactions"""
    
    def __init__(self, oauth_token: str = None):
        self.oauth_token = oauth_token or os.getenv('SITE24X7_OAUTH_TOKEN')
        self.base_url = 'https://www.site24x7.com/api'
        self.session = requests.Session()
        
        if self.oauth_token:
            self.session.headers.update({
                'Authorization': f'Zoho-oauthtoken {self.oauth_token}',
                'Accept': 'application/json; version=2.0',
                'Content-Type': 'application/json;charset=UTF-8'
            })
    
    def request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make API request"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            console.print(f"[red]API Error: {e}[/red]")
            raise
    
    def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """GET request"""
        return self.request('GET', endpoint, **kwargs)
    
    def post(self, endpoint: str, data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """POST request"""
        return self.request('POST', endpoint, json=data, **kwargs)
    
    def put(self, endpoint: str, data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """PUT request"""
        return self.request('PUT', endpoint, json=data, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """DELETE request"""
        return self.request('DELETE', endpoint, **kwargs)

class BaseCommand:
    """Base class for all CLI commands"""
    
    def __init__(self):
        self.client = Site24x7Client()
    
    def format_output(self, data: Any, output_format: str = 'table') -> None:
        """Format and display output"""
        if output_format == 'json':
            console.print_json(json.dumps(data, indent=2))
        elif output_format == 'table' and isinstance(data, list):
            self._display_table(data)
        else:
            console.print(data)
    
    def _display_table(self, data: List[Dict[str, Any]]) -> None:
        """Display data as a rich table"""
        if not data:
            console.print("[yellow]No data to display[/yellow]")
            return
        
        table = Table()
        
        # Add columns from first item keys
        for key in data[0].keys():
            table.add_column(key.replace('_', ' ').title())
        
        # Add rows
        for item in data:
            table.add_row(*[str(value) for value in item.values()])
        
        console.print(table)
'''
    
    def _generate_auth_module(self) -> str:
        """Generate authentication module"""
        return '''"""
Authentication module for Site24x7 CLI
"""

import os
import json
from typing import Optional
import click
from rich.console import Console

console = Console()

class AuthManager:
    """Manage authentication credentials"""
    
    CONFIG_FILE = os.path.expanduser('~/.site24x7/credentials.json')
    
    @classmethod
    def save_credentials(cls, oauth_token: str) -> None:
        """Save OAuth token to config file"""
        os.makedirs(os.path.dirname(cls.CONFIG_FILE), exist_ok=True)
        
        config = {
            'oauth_token': oauth_token,
            'saved_at': str(datetime.utcnow())
        }
        
        with open(cls.CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        
        console.print("[green]Credentials saved successfully[/green]")
    
    @classmethod
    def load_credentials(cls) -> Optional[str]:
        """Load OAuth token from config file"""
        if os.path.exists(cls.CONFIG_FILE):
            try:
                with open(cls.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    return config.get('oauth_token')
            except Exception as e:
                console.print(f"[red]Error loading credentials: {e}[/red]")
        
        return None
    
    @classmethod
    def clear_credentials(cls) -> None:
        """Clear saved credentials"""
        if os.path.exists(cls.CONFIG_FILE):
            os.remove(cls.CONFIG_FILE)
            console.print("[green]Credentials cleared[/green]")

@click.command()
@click.option('--token', required=True, help='Site24x7 OAuth token')
def configure(token: str):
    """Configure Site24x7 CLI with OAuth token"""
    AuthManager.save_credentials(token)

@click.command()
def clear():
    """Clear saved credentials"""
    AuthManager.clear_credentials()
'''
    
    def _generate_exceptions_module(self) -> str:
        """Generate custom exceptions"""
        return '''"""
Custom exceptions for Site24x7 CLI
"""

class Site24x7CLIError(Exception):
    """Base exception for Site24x7 CLI"""
    pass

class AuthenticationError(Site24x7CLIError):
    """Authentication related errors"""
    pass

class APIError(Site24x7CLIError):
    """API request errors"""
    pass

class ValidationError(Site24x7CLIError):
    """Input validation errors"""
    pass
'''
    
    def _generate_utils_module(self) -> str:
        """Generate utilities module"""
        return '''"""
Utility functions for Site24x7 CLI
"""

import json
import re
from typing import Any, Dict, List
from datetime import datetime

def validate_monitor_id(monitor_id: str) -> bool:
    """Validate monitor ID format"""
    return bool(re.match(r'^[0-9]+$', monitor_id))

def format_timestamp(timestamp: str) -> str:
    """Format timestamp for display"""
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
    except:
        return timestamp

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for file operations"""
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)

def parse_key_value_pairs(pairs: List[str]) -> Dict[str, str]:
    """Parse key=value pairs from command line"""
    result = {}
    for pair in pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            result[key.strip()] = value.strip()
    return result
'''
    
    async def _generate_command_modules(self, command_structure: Dict[str, Any], documentation: Dict[str, Any]) -> Dict[str, str]:
        """Generate command modules for each category"""
        files = {}
        
        for category_name, category_data in command_structure['subcommands'].items():
            module_path = f'site24x7_cli/commands/{category_name}.py'
            files[module_path] = await self._generate_category_module(category_name, category_data, documentation)
        
        # Generate commands __init__.py
        files['site24x7_cli/commands/__init__.py'] = ''
        
        return files
    
    async def _generate_category_module(self, category_name: str, category_data: Dict[str, Any], documentation: Dict[str, Any]) -> str:
        """Generate module for a specific category"""
        template = self.template_env.get_template('command_template.py.j2')
        return template.render(
            category_name=category_name,
            category_data=category_data,
            documentation=documentation
        )
    
    def _generate_supporting_files(self, documentation: Dict[str, Any]) -> Dict[str, str]:
        """Generate supporting files (setup.py, README, etc.)"""
        files = {}
        
        # Generate setup.py
        files['setup.py'] = self._generate_setup_py()
        
        # Generate README.md
        files['README.md'] = self._generate_readme(documentation)
        
        # Generate requirements.txt
        files['requirements.txt'] = self._generate_requirements()
        
        # Generate CLI entry script
        files['bin/site24x7'] = self._generate_entry_script()
        
        # Generate configuration files
        files['site24x7_cli/config.py'] = self._generate_config_module()
        
        return files
    
    def _generate_setup_py(self) -> str:
        """Generate setup.py file"""
        template = self.template_env.get_template('setup.py.j2')
        return template.render(version=self._generate_version_string())
    
    def _generate_readme(self, documentation: Dict[str, Any]) -> str:
        """Generate comprehensive README"""
        template = self.template_env.get_template('readme.md.j2')
        return template.render(
            documentation=documentation,
            endpoints_count=len(documentation.get('endpoints', [])),
            generated_at=datetime.utcnow().strftime('%Y-%m-%d')
        )
    
    def _generate_requirements(self) -> str:
        """Generate requirements.txt"""
        return '''click>=8.0.0
rich>=12.0.0
requests>=2.28.0
pydantic>=1.10.0
'''
    
    def _generate_entry_script(self) -> str:
        """Generate CLI entry script"""
        return '''#!/usr/bin/env python3
"""Site24x7 CLI Entry Point"""

import sys
from site24x7_cli.main import cli

if __name__ == '__main__':
    cli()
'''
    
    def _generate_config_module(self) -> str:
        """Generate configuration module"""
        return '''"""
Configuration management for Site24x7 CLI
"""

import os
from typing import Optional

class Config:
    """CLI configuration"""
    
    DEFAULT_BASE_URL = 'https://www.site24x7.com/api'
    DEFAULT_OUTPUT_FORMAT = 'table'
    
    @classmethod
    def get_oauth_token(cls) -> Optional[str]:
        """Get OAuth token from environment or config"""
        return os.getenv('SITE24X7_OAUTH_TOKEN')
    
    @classmethod
    def get_base_url(cls) -> str:
        """Get API base URL"""
        return os.getenv('SITE24X7_BASE_URL', cls.DEFAULT_BASE_URL)
    
    @classmethod
    def get_output_format(cls) -> str:
        """Get default output format"""
        return os.getenv('SITE24X7_OUTPUT_FORMAT', cls.DEFAULT_OUTPUT_FORMAT)
'''
    
    def _generate_version_string(self) -> str:
        """Generate version string based on current date"""
        return datetime.utcnow().strftime('1.%Y%m%d.%H%M')
