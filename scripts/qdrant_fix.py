#!/usr/bin/env python3
"""
Qdrant API Fix Utility
Fixes the QdrantClient API calls from 'search' to 'query_points'
"""

import sys
import os

def fix_qdrant_api_calls():
    """Fix all Python files that use QdrantClient"""
    scripts_dir = "/Users/lst01/Desktop/开发工作区/openclaw-skill-evolution/scripts"
    
    # Files that need fixing
    files_to_fix = [
        "experience_manager.py",
        "planner.py",
        "skill_generator.py"
    ]
    
    for filename in files_to_fix:
        filepath = os.path.join(scripts_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace search calls with query_points
            original_content = content
            content = content.replace(".search(", ".query_points(")
            content = content.replace("client.search(", "client.query_points(")
            
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Fixed Qdrant API calls in {filename}")
            else:
                print(f"ℹ️  No changes needed in {filename}")

if __name__ == "__main__":
    fix_qdrant_api_calls()
    print("🔧 Qdrant API fixes applied!")