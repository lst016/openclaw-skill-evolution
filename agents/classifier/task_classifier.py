#!/usr/bin/env python3
"""
Task Classifier for OpenClaw Skill Evolution v3
Classifies user tasks into standardized task types
"""

import sys
import os
import json
from typing import Dict, List, Any, Optional, Tuple
import logging

# Add the virtual environment to Python path
venv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.venv')
if os.path.exists(venv_path):
    site_packages = os.path.join(venv_path, 'lib', 'python3.14', 'site-packages')
    if os.path.exists(site_packages):
        sys.path.insert(0, site_packages)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskClassifier:
    """Classifies tasks into standardized task types"""
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        self.workspace_path = workspace_path
        self.task_taxonomy = self.load_task_taxonomy()
    
    def load_task_taxonomy(self) -> Dict[str, List[str]]:
        """Load standardized task taxonomy"""
        # Default task taxonomy
        taxonomy = {
            "debugging": [
                "debug", "fix", "error", "bug", "crash", "exception", "stack trace",
                "troubleshoot", "resolve issue", "problem solving"
            ],
            "web_search": [
                "search", "find", "look for", "research", "investigate", "explore",
                "discover", "learn about", "get information"
            ],
            "content_creation": [
                "write", "create", "generate", "compose", "draft", "author",
                "produce", "make", "build content"
            ],
            "file_edit": [
                "edit", "modify", "update", "change", "refactor", "improve",
                "rewrite", "adjust", "tweak"
            ],
            "analysis": [
                "analyze", "check", "review", "examine", "inspect", "evaluate",
                "assess", "audit", "verify"
            ],
            "automation": [
                "automate", "script", "batch", "schedule", "workflow", "pipeline",
                "integrate", "connect", "setup"
            ]
        }
        
        return taxonomy
    
    def classify_task(self, task: str) -> Dict[str, Any]:
        """Classify a task into standardized task type"""
        task_lower = task.lower()
        best_match = "general"
        best_confidence = 0.0
        best_reason = "No specific task type matched"
        
        # Check each task type in taxonomy
        for task_type, keywords in self.task_taxonomy.items():
            keyword_matches = sum(1 for keyword in keywords if keyword in task_lower)
            if keyword_matches > 0:
                confidence = min(keyword_matches / len(keywords), 1.0)
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = task_type
                    best_reason = f"Matched {keyword_matches} keywords: {', '.join([k for k in keywords if k in task_lower])}"
        
        # Set minimum confidence threshold
        if best_confidence < 0.3:
            best_match = "general"
            best_confidence = 0.0
            best_reason = "Task doesn't clearly match any specific category"
        
        result = {
            "task_type": best_match,
            "confidence": best_confidence,
            "reason": best_reason,
            "matched_keywords": [k for k in self.task_taxonomy.get(best_match, []) if k in task_lower] if best_match != "general" else []
        }
        
        logger.info(f"🔍 Classified task '{task[:50]}...' as '{best_match}' (confidence: {best_confidence:.2f})")
        return result
    
    def get_all_task_types(self) -> List[str]:
        """Get all available task types"""
        return list(self.task_taxonomy.keys()) + ["general"]
    
    def add_task_type(self, task_type: str, keywords: List[str]) -> bool:
        """Add a new task type to taxonomy"""
        if task_type in self.task_taxonomy:
            logger.warning(f"Task type '{task_type}' already exists")
            return False
        
        self.task_taxonomy[task_type] = keywords
        logger.info(f"✅ Added new task type: {task_type}")
        return True

def main():
    """Test the task classifier"""
    classifier = TaskClassifier()
    
    test_tasks = [
        "Debug a Python application error",
        "Search for information about OpenClaw Skill Evolution", 
        "Write a comprehensive README.md file",
        "Edit the configuration file to fix the bug",
        "Analyze the performance metrics",
        "Automate the deployment process"
    ]
    
    print("Task Classification Results:")
    print("-" * 50)
    for task in test_tasks:
        result = classifier.classify_task(task)
        print(f"Task: {task}")
        print(f"Type: {result['task_type']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Reason: {result['reason']}")
        print("-" * 50)

if __name__ == "__main__":
    main()