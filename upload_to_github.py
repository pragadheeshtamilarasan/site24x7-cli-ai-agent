#!/usr/bin/env python3
"""
Upload all project files to GitHub repository
"""

import os
import base64
import requests
import json
from pathlib import Path

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
REPO_OWNER = "pragadheeshtamilarasan"
REPO_NAME = "site24x7-cli-ai-agent"
BASE_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"

# Files to skip
SKIP_FILES = {
    '.git', '__pycache__', '.cache', '.local', '.pythonlibs', '.upm',
    'site24x7_agent.db', 'site24x7_agent.log', 'uv.lock', '.replit'
}

def encode_file_content(file_path):
    """Encode file content to base64"""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        return base64.b64encode(content).decode('utf-8')
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def upload_file_to_github(file_path, github_path):
    """Upload a single file to GitHub"""
    content = encode_file_content(file_path)
    if content is None:
        return False
    
    # Check if file already exists
    check_url = f"{BASE_URL}/contents/{github_path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(check_url, headers=headers)
        sha = None
        if response.status_code == 200:
            sha = response.json().get('sha')
    except:
        pass
    
    # Upload file
    data = {
        "message": f"Add {github_path}",
        "content": content
    }
    
    if sha:
        data["sha"] = sha
        data["message"] = f"Update {github_path}"
    
    response = requests.put(check_url, headers=headers, json=data)
    
    if response.status_code in [200, 201]:
        print(f"✅ Uploaded: {github_path}")
        return True
    else:
        print(f"❌ Failed to upload {github_path}: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        return False

def get_all_files():
    """Get all files to upload"""
    files_to_upload = []
    
    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        dirs[:] = [d for d in dirs if d not in SKIP_FILES]
        
        for file in files:
            if file in SKIP_FILES:
                continue
                
            file_path = os.path.join(root, file)
            # Convert to GitHub path (remove ./ prefix)
            github_path = file_path[2:] if file_path.startswith('./') else file_path
            
            files_to_upload.append((file_path, github_path))
    
    return files_to_upload

def main():
    """Main upload function"""
    if not GITHUB_TOKEN:
        print("❌ GitHub token not found in environment variables")
        return
    
    print("🚀 Starting upload to GitHub...")
    print(f"Repository: {REPO_OWNER}/{REPO_NAME}")
    
    files_to_upload = get_all_files()
    print(f"Found {len(files_to_upload)} files to upload")
    
    success_count = 0
    for file_path, github_path in files_to_upload:
        if upload_file_to_github(file_path, github_path):
            success_count += 1
    
    print(f"\n🎉 Upload complete!")
    print(f"✅ Successfully uploaded: {success_count} files")
    print(f"❌ Failed uploads: {len(files_to_upload) - success_count} files")
    print(f"\nRepository URL: https://github.com/{REPO_OWNER}/{REPO_NAME}")

if __name__ == "__main__":
    main()