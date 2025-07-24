"""
Site24x7 API Documentation Scraper
Extracts comprehensive API endpoint information from Site24x7 documentation
"""

import hashlib
import logging
import re
from typing import Dict, List, Any, Optional
import trafilatura
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from config import settings
from database import APISnapshotManager, TaskLogger

logger = logging.getLogger(__name__)

class Site24x7APIScraper:
    """Scraper for Site24x7 API documentation"""
    
    def __init__(self):
        self.base_url = settings.site24x7_docs_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Site24x7-CLI-Agent/1.0.0 (Autonomous Documentation Scraper)'
        })
    
    async def scrape_full_documentation(self) -> Dict[str, Any]:
        """Scrape complete API documentation"""
        try:
            TaskLogger.log("api_scraper", "started", "Starting comprehensive API documentation scrape")
            
            # Get main documentation page
            main_content = await self._fetch_page_content(self.base_url)
            if not main_content:
                raise Exception("Failed to fetch main documentation page")
            
            # Parse main page structure
            soup = BeautifulSoup(main_content, 'html.parser')
            
            # Extract table of contents
            toc_data = self._extract_table_of_contents(soup)
            
            # Extract all API endpoints and categories
            endpoints = await self._extract_all_endpoints(soup)
            
            # Get detailed endpoint information
            detailed_endpoints = await self._get_detailed_endpoint_info(endpoints)
            
            # Compile comprehensive documentation
            documentation = {
                'base_url': 'https://www.site24x7.com/api/',
                'version': '2.0',
                'authentication': {
                    'type': 'OAuth 2.0',
                    'header': 'Authorization: Zoho-oauthtoken [TOKEN]',
                    'content_type': 'application/json;charset=UTF-8',
                    'accept': 'application/json; version=2.0'
                },
                'categories': toc_data,
                'endpoints': detailed_endpoints,
                'http_methods': ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'PROPFIND'],
                'scraped_at': self._get_current_timestamp(),
                'total_endpoints': len(detailed_endpoints)
            }
            
            # Save snapshot
            content_str = str(documentation)
            content_hash = hashlib.md5(content_str.encode()).hexdigest()
            
            if APISnapshotManager.has_content_changed(content_hash):
                APISnapshotManager.save_snapshot(
                    content_str, 
                    content_hash, 
                    len(detailed_endpoints)
                )
                TaskLogger.log(
                    "api_scraper", 
                    "completed", 
                    f"Successfully scraped {len(detailed_endpoints)} endpoints",
                    {"endpoints_count": len(detailed_endpoints), "content_hash": content_hash}
                )
            else:
                TaskLogger.log("api_scraper", "no_changes", "No changes detected in API documentation")
            
            return documentation
            
        except Exception as e:
            logger.error(f"Failed to scrape API documentation: {e}")
            TaskLogger.log("api_scraper", "failed", str(e))
            raise
    
    async def _fetch_page_content(self, url: str) -> str:
        """Fetch page content using trafilatura for better text extraction"""
        try:
            # First get raw HTML
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Use trafilatura for clean text extraction
            text_content = trafilatura.extract(response.text)
            
            # Also return raw HTML for structure parsing
            return response.text
            
        except Exception as e:
            logger.error(f"Failed to fetch content from {url}: {e}")
            return ""
    
    def _extract_table_of_contents(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract hierarchical table of contents structure"""
        categories = []
        
        # Find the main navigation or TOC structure
        toc_elements = soup.find_all(['ul', 'ol'], class_=re.compile(r'toc|nav|menu', re.I))
        
        if not toc_elements:
            # Fallback: look for any list structure in the main content
            toc_elements = soup.find_all(['ul', 'ol'])
        
        for toc in toc_elements:
            category_items = self._parse_toc_level(toc)
            if category_items:
                categories.extend(category_items)
        
        # If no TOC found, parse from known structure based on web content
        if not categories:
            categories = self._extract_known_categories()
        
        return categories
    
    def _parse_toc_level(self, element) -> List[Dict[str, Any]]:
        """Parse a single level of table of contents"""
        items = []
        
        for li in element.find_all('li', recursive=False):
            link = li.find('a')
            if link:
                item = {
                    'name': link.get_text(strip=True),
                    'url': link.get('href', ''),
                    'subcategories': []
                }
                
                # Check for nested ul/ol
                nested_list = li.find(['ul', 'ol'])
                if nested_list:
                    item['subcategories'] = self._parse_toc_level(nested_list)
                
                items.append(item)
        
        return items
    
    def _extract_known_categories(self) -> List[Dict[str, Any]]:
        """Extract known API categories based on Site24x7 documentation structure"""
        return [
            {
                'name': 'Monitor Management',
                'subcategories': [
                    {'name': 'Website Monitors', 'endpoint': '/api/website_monitor'},
                    {'name': 'REST API Monitors', 'endpoint': '/api/rest_api_monitor'},
                    {'name': 'DNS Server Monitors', 'endpoint': '/api/dns_server_monitor'},
                    {'name': 'SSL Certificate Monitors', 'endpoint': '/api/ssl_monitor'},
                    {'name': 'Domain Expiry Monitors', 'endpoint': '/api/domain_expiry_monitor'},
                    {'name': 'Port Monitors', 'endpoint': '/api/port_monitor'},
                    {'name': 'FTP Transfer Monitors', 'endpoint': '/api/ftp_transfer_monitor'},
                    {'name': 'WebSocket Monitors', 'endpoint': '/api/websocket_monitor'},
                    {'name': 'SOAP Web Services', 'endpoint': '/api/soap_monitor'},
                    {'name': 'gRPC Monitors', 'endpoint': '/api/grpc_monitor'}
                ]
            },
            {
                'name': 'AWS Monitoring',
                'subcategories': [
                    {'name': 'EC2 Instance Monitors', 'endpoint': '/api/amazon_monitor'},
                    {'name': 'RDS Instance Monitors', 'endpoint': '/api/amazon_monitor'},
                    {'name': 'Lambda Function Monitors', 'endpoint': '/api/amazon_monitor'},
                    {'name': 'S3 Bucket Monitors', 'endpoint': '/api/amazon_monitor'},
                    {'name': 'CloudFront Distribution Monitors', 'endpoint': '/api/amazon_monitor'}
                ]
            },
            {
                'name': 'Reports & Analytics',
                'subcategories': [
                    {'name': 'Performance Reports', 'endpoint': '/api/reports/performance'},
                    {'name': 'Uptime Reports', 'endpoint': '/api/reports/uptime'},
                    {'name': 'Summary Reports', 'endpoint': '/api/reports/summary'},
                    {'name': 'Availability Reports', 'endpoint': '/api/reports/availability'}
                ]
            },
            {
                'name': 'User & Group Management',
                'subcategories': [
                    {'name': 'Users', 'endpoint': '/api/users'},
                    {'name': 'User Groups', 'endpoint': '/api/user_groups'},
                    {'name': 'On-Call Schedules', 'endpoint': '/api/on_call_schedules'}
                ]
            },
            {
                'name': 'MSP Operations',
                'subcategories': [
                    {'name': 'Customer Management', 'endpoint': '/api/msp/customers'},
                    {'name': 'Global Monitor Status', 'endpoint': '/api/msp/monitors/status'},
                    {'name': 'Customer Portal Access', 'endpoint': '/api/msp/portals'}
                ]
            }
        ]
    
    async def _extract_all_endpoints(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract all API endpoints from documentation"""
        endpoints = []
        
        # Look for API endpoint patterns in the content
        text_content = soup.get_text()
        
        # Common API endpoint patterns
        api_patterns = [
            r'/api/[a-z_/]+',
            r'https://www\.site24x7\.com/api/[a-z_/]+',
            r'GET|POST|PUT|DELETE|PATCH\s+/api/[a-z_/]+'
        ]
        
        for pattern in api_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            for match in matches:
                endpoint_path = match.replace('https://www.site24x7.com', '').strip()
                if endpoint_path.startswith('/api/'):
                    endpoints.append({
                        'path': endpoint_path,
                        'methods': self._determine_http_methods(endpoint_path),
                        'category': self._categorize_endpoint(endpoint_path)
                    })
        
        # Remove duplicates
        seen = set()
        unique_endpoints = []
        for endpoint in endpoints:
            key = (endpoint['path'], tuple(endpoint['methods']))
            if key not in seen:
                seen.add(key)
                unique_endpoints.append(endpoint)
        
        return unique_endpoints
    
    def _determine_http_methods(self, endpoint_path: str) -> List[str]:
        """Determine HTTP methods for an endpoint based on its path"""
        methods = ['GET']  # Default to GET
        
        if any(keyword in endpoint_path.lower() for keyword in ['create', 'add', 'new']):
            methods.append('POST')
        
        if any(keyword in endpoint_path.lower() for keyword in ['update', 'modify', 'edit']):
            methods.extend(['PUT', 'PATCH'])
        
        if any(keyword in endpoint_path.lower() for keyword in ['delete', 'remove']):
            methods.append('DELETE')
        
        return list(set(methods))
    
    def _categorize_endpoint(self, endpoint_path: str) -> str:
        """Categorize endpoint based on its path"""
        path_lower = endpoint_path.lower()
        
        if 'monitor' in path_lower:
            if 'aws' in path_lower or 'amazon' in path_lower:
                return 'AWS Monitoring'
            elif any(t in path_lower for t in ['website', 'api', 'dns', 'ssl', 'port']):
                return 'Website Monitoring'
            else:
                return 'Monitor Management'
        elif 'report' in path_lower:
            return 'Reports & Analytics'
        elif 'user' in path_lower:
            return 'User Management'
        elif 'msp' in path_lower:
            return 'MSP Operations'
        elif 'status' in path_lower:
            return 'Status & Health'
        else:
            return 'General API'
    
    async def _get_detailed_endpoint_info(self, endpoints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get detailed information for each endpoint"""
        detailed_endpoints = []
        
        for endpoint in endpoints:
            try:
                # Add detailed information based on endpoint analysis
                detailed_info = {
                    'path': endpoint['path'],
                    'methods': endpoint['methods'],
                    'category': endpoint['category'],
                    'name': self._generate_endpoint_name(endpoint['path']),
                    'description': self._generate_endpoint_description(endpoint['path']),
                    'parameters': self._extract_endpoint_parameters(endpoint['path']),
                    'auth_required': True,  # All Site24x7 API endpoints require auth
                    'rate_limited': True
                }
                
                detailed_endpoints.append(detailed_info)
                
            except Exception as e:
                logger.warning(f"Failed to get details for endpoint {endpoint['path']}: {e}")
                detailed_endpoints.append(endpoint)  # Use basic info as fallback
        
        return detailed_endpoints
    
    def _generate_endpoint_name(self, path: str) -> str:
        """Generate human-readable name for endpoint"""
        parts = path.strip('/').split('/')
        if len(parts) >= 2:
            resource = parts[-1].replace('_', ' ').title()
            return resource
        return path.strip('/').replace('_', ' ').title()
    
    def _generate_endpoint_description(self, path: str) -> str:
        """Generate description for endpoint"""
        name = self._generate_endpoint_name(path)
        if 'monitor' in path.lower():
            return f"Manage {name} monitoring operations"
        elif 'report' in path.lower():
            return f"Generate and retrieve {name} reports"
        elif 'user' in path.lower():
            return f"Handle {name} management operations"
        else:
            return f"Perform {name} operations"
    
    def _extract_endpoint_parameters(self, path: str) -> Dict[str, Any]:
        """Extract common parameters for endpoint"""
        params = {
            'query': [],
            'path': [],
            'body': []
        }
        
        # Common query parameters
        if 'monitor' in path.lower():
            params['query'].extend(['monitor_id', 'group_id', 'location_profile_id'])
        
        if 'report' in path.lower():
            params['query'].extend(['period', 'start_date', 'end_date'])
        
        # Path parameters (look for {id} patterns)
        path_params = re.findall(r'\{([^}]+)\}', path)
        params['path'].extend(path_params)
        
        return params
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
