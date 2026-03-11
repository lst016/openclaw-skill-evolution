#!/usr/bin/env python3
"""
Long Task Manager for OpenClaw Skill Evolution v5
Manages long-running tasks that span multiple sessions and environment states.

中文注释:
长任务管理器 - 管理跨多个会话和环境状态的长期运行任务
"""

import sys
import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging

# Add the virtual environment to Python path
venv_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '.venv')
if os.path.exists(venv_path):
    site_packages = os.path.join(venv_path, 'lib', 'python3.14', 'site-packages')
    if os.path.exists(site_packages):
        sys.path.insert(0, site_packages)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LongTaskManager:
    """
    Manages long-running tasks that can span multiple sessions.
    
    English: Manages long-running tasks with persistence across sessions.
    中文: 管理跨会话持久化的长期运行任务。
    """
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        """
        Initialize the Long Task Manager.
        
        English: Initialize with workspace path and ensure directories exist.
        中文: 使用工作区路径初始化并确保目录存在。
        """
        self.workspace_path = workspace_path
        self.long_tasks_dir = os.path.join(workspace_path, "long_tasks")
        self.active_tasks_dir = os.path.join(self.long_tasks_dir, "active")
        self.completed_tasks_dir = os.path.join(self.long_tasks_dir, "completed")
        self.archived_tasks_dir = os.path.join(self.long_tasks_dir, "archived")
        
        # Ensure all directories exist
        os.makedirs(self.active_tasks_dir, exist_ok=True)
        os.makedirs(self.completed_tasks_dir, exist_ok=True)
        os.makedirs(self.archived_tasks_dir, exist_ok=True)
        
        logger.info("✅ Long Task Manager initialized")
        logger.info(f"   Active tasks: {self.active_tasks_dir}")
        logger.info(f"   Completed tasks: {self.completed_tasks_dir}")
        logger.info(f"   Archived tasks: {self.archived_tasks_dir}")
    
    def create_long_task_id(self) -> str:
        """
        Generate a unique long task ID.
        
        English: Generate UUID-based task ID for uniqueness.
        中文: 生成基于 UUID 的任务 ID 以确保唯一性。
        """
        return str(uuid.uuid4())
    
    def get_current_timestamp(self) -> str:
        """
        Get current timestamp in ISO format.
        
        English: Return current time as ISO string for consistency.
        中文: 返回当前时间的 ISO 字符串以保持一致性。
        """
        return datetime.now().isoformat()
    
    def create_long_task(
        self,
        goal: str,
        description: str = "",
        priority: str = "normal",
        estimated_duration: str = "unknown",
        environment_state: Optional[Dict] = None,
        initial_steps: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Create a new long-running task.
        
        English: Create a structured long task with goal, steps, and state tracking.
        中文: 创建结构化的长期任务，包含目标、步骤和状态跟踪。
        
        Args:
            goal (str): The main goal of the long task
            description (str): Detailed description of the task
            priority (str): Task priority (low, normal, high, critical)
            estimated_duration (str): Estimated duration (hours, days, weeks)
            environment_state (Dict): Initial environment state snapshot
            initial_steps (List[Dict]): Initial breakdown of steps
            
        Returns:
            Dict[str, Any]: The created long task structure
        """
        task_id = self.create_long_task_id()
        created_at = self.get_current_timestamp()
        
        # Default steps if none provided
        if initial_steps is None:
            initial_steps = [
                {
                    "step_id": "step_1",
                    "description": "Analyze current situation and requirements",
                    "status": "pending",
                    "assigned_to": "planner",
                    "estimated_duration": "1-2 hours",
                    "dependencies": [],
                    "outputs": []
                }
            ]
        
        long_task = {
            "task_id": task_id,
            "goal": goal,
            "description": description,
            "priority": priority,
            "estimated_duration": estimated_duration,
            "status": "active",
            "current_stage": "initial_analysis",
            "created_at": created_at,
            "updated_at": created_at,
            "completed_at": None,
            "environment_state": environment_state or {},
            "steps": initial_steps,
            "completed_steps": [],
            "pending_steps": [step["step_id"] for step in initial_steps],
            "failed_steps": [],
            "dependencies": [],
            "metrics": {
                "total_steps": len(initial_steps),
                "completed_steps": 0,
                "success_rate": 0.0,
                "elapsed_time": 0,
                "last_activity": created_at
            },
            "metadata": {
                "version": "v5.0",
                "source": "long_task_manager",
                "tags": ["v5", "long_running"]
            }
        }
        
        logger.info(f"✅ Created long task: {task_id}")
        logger.info(f"   Goal: {goal}")
        logger.info(f"   Steps: {len(initial_steps)}")
        logger.info(f"   Priority: {priority}")
        
        return long_task
    
    def save_long_task(self, long_task: Dict[str, Any]) -> str:
        """
        Save a long task to file system.
        
        English: Persist long task to appropriate directory based on status.
        中文: 根据状态将长期任务持久化到适当的目录。
        """
        task_id = long_task["task_id"]
        status = long_task["status"]
        
        if status == "active":
            task_dir = self.active_tasks_dir
        elif status == "completed":
            task_dir = self.completed_tasks_dir
        else:
            task_dir = self.archived_tasks_dir
        
        task_file = os.path.join(task_dir, f"{task_id}.json")
        
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(long_task, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Saved long task to: {task_file}")
        return task_file
    
    def load_long_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a long task from file system.
        
        English: Load long task from any directory where it might be stored.
        中文: 从可能存储的任何目录加载长期任务。
        """
        # Check all possible directories
        directories = [self.active_tasks_dir, self.completed_tasks_dir, self.archived_tasks_dir]
        
        for directory in directories:
            task_file = os.path.join(os.path.dirname(__file__), "..", "..")/Desktop/开发工作区/openclaw-skill-evolution/long_tasks/manager/long_task_manager.py