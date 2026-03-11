#!/usr/bin/env python3
"""
Long Task Scheduler for OpenClaw Skill Evolution v5
Manages scheduling and execution of long-running tasks across sessions.

中文注释:
长任务调度器 - 管理跨会话的长期任务调度和执行
"""

import sys
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add the virtual environment to Python path
venv_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '.venv')
if os.path.exists(venv_path):
    site_packages = os.path.join(venv_path, 'lib', 'python3.14', 'site-packages')
    if os.path.exists(site_packages):
        sys.path.insert(0, site_packages)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LongTaskScheduler:
    """
    English: Manages scheduling and execution of long-running tasks.
    
    中文: 管理长期任务的调度和执行。
    """
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        """
        English: Initialize the long task scheduler.
        
        中文: 初始化长任务调度器。
        """
        self.workspace_path = workspace_path
        self.long_tasks_dir = os.path.join(workspace_path, "long_tasks")
        self.schedules_dir = os.path.join(self.long_tasks_dir, "schedules")
        os.makedirs(self.schedules_dir, exist_ok=True)
        
        # Load existing schedules
        self.schedules = self._load_schedules()
    
    def _load_schedules(self) -> Dict[str, Any]:
        """
        English: Load existing task schedules from disk.
        
        中文: 从磁盘加载现有的任务调度。
        """
        schedules_file = os.path.join(self.schedules_dir, "schedules.json")
        if os.path.exists(schedules_file):
            with open(schedules_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_schedules(self):
        """
        English: Save current schedules to disk.
        
        中文: 将当前调度保存到磁盘。
        """
        schedules_file = os.path.join(self.schedules_dir, "schedules.json")
        with open(schedules_file, 'w', encoding='utf-8') as f:
            json.dump(self.schedules, f, indent=2, ensure_ascii=False)
    
    def schedule_long_task(
        self,
        task_id: str,
        goal: str,
        steps: List[Dict],
        start_time: Optional[datetime] = None,
        recurrence: Optional[str] = None
    ) -> bool:
        """
        English: Schedule a long-running task for execution.
        
        Args:
            task_id: Unique identifier for the task
            goal: The overall goal of the task
            steps: List of steps to execute
            start_time: When to start the task (default: now)
            recurrence: Recurrence pattern (e.g., "daily", "weekly")
            
        Returns:
            bool: True if scheduled successfully
        
        中文: 调度一个长期任务进行执行。
        
        参数:
            task_id: 任务的唯一标识符
            goal: 任务的总体目标
            steps: 要执行的步骤列表
            start_time: 任务开始时间（默认：现在）
            recurrence: 重复模式（例如："daily", "weekly"）
            
        返回:
            bool: 如果成功调度则返回 True
        """
        try:
            if start_time is None:
                start_time = datetime.now()
            
            schedule = {
                "task_id": task_id,
                "goal": goal,
                "steps": steps,
                "start_time": start_time.isoformat(),
                "recurrence": recurrence,
                "status": "scheduled",
                "created_at": datetime.now().isoformat(),
                "last_executed": None,
                "next_execution": start_time.isoformat()
            }
            
            self.schedules[task_id] = schedule
            self._save_schedules()
            
            logger.info(f"✅ Scheduled long task: {task_id} (goal: {goal})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to schedule long task {task_id}: {e}")
            return False
    
    def get_due_tasks(self) -> List[Dict]:
        """
        English: Get all tasks that are due for execution.
        
        Returns:
            List[Dict]: List of due tasks
            
        中文: 获取所有到期需要执行的任务。
        
        返回:
            List[Dict]: 到期任务列表
        """
        now = datetime.now()
        due_tasks = []
        
        for task_id, schedule in self.schedules.items():
            if schedule["status"] != "scheduled":
                continue
                
            next_execution = datetime.fromisoformat(schedule["next_execution"])
            if next_execution <= now:
                due_tasks.append(schedule)
        
        return due_tasks
    
    def mark_task_executed(self, task_id: str, success: bool = True):
        """
        English: Mark a task as executed and update its schedule.
        
        Args:
            task_id: The task identifier
            success: Whether the execution was successful
            
        中文: 标记任务为已执行并更新其调度。
        
        参数:
            task_id: 任务标识符
            success: 执行是否成功
        """
        if task_id not in self.schedules:
            logger.warning(f"⚠️ Task {task_id} not found in schedules")
            return
        
        schedule = self.schedules[task_id]
        schedule["last_executed"] = datetime.now().isoformat()
        schedule["status"] = "executed" if success else "failed"
        
        # Handle recurrence
        if schedule["recurrence"] and success:
            # Calculate next execution time
            next_time = self._calculate_next_execution(schedule)
            if next_time:
                schedule["next_execution"] = next_time.isoformat()
                schedule["status"] = "scheduled"
        
        self._save_schedules()
        logger.info(f"✅ Marked task {task_id} as {'executed' if success else 'failed'}")
    
    def _calculate_next_execution(self, schedule: Dict) -> Optional[datetime]:
        """
        English: Calculate the next execution time based on recurrence pattern.
        
        Args:
            schedule: The task schedule dictionary
            
        Returns:
            Optional[datetime]: Next execution time or None
            
        中文: 根据重复模式计算下一次执行时间。
        
        参数:
            schedule: 任务调度字典
            
        返回:
            Optional[datetime]: 下一次执行时间或 None
        """
        recurrence = schedule["recurrence"]
        last_executed = datetime.fromisoformat(schedule["last_executed"])
        
        if recurrence == "daily":
            return last_executed + timedelta(days=1)
        elif recurrence == "weekly":
            return last_executed + timedelta(weeks=1)
        elif recurrence == "hourly":
            return last_executed + timedelta(hours=1)
        else:
            # Custom recurrence patterns can be added here
            logger.warning(f"⚠️ Unknown recurrence pattern: {recurrence}")
            return None
    
    def resume_long_task(self, task_id: str) -> Optional[Dict]:
        """
        English: Resume a long-running task from its last state.
        
        Args:
            task_id: The task identifier
            
        Returns:
            Optional[Dict]: Task state or None if not found
            
        中文: 从最后状态恢复一个长期任务。
        
        参数:
            task_id: 任务标识符
            
        返回:
            Optional[Dict]: 任务状态或 None（如果未找到）
        """
        # This would integrate with the LongTaskManager to get the actual task state
        long_tasks_dir = os.path.join(self.workspace_path, "long_tasks", "tasks")
        task_file = os.path.join(long_tasks_dir, f"{task_id}.json")
        
        if not os.path.exists(task_file):
            logger.warning(f"⚠️ Task file not found: {task_file}")
            return None
        
        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                task_state = json.load(f)
            
            logger.info(f"✅ Resumed long task: {task_id}")
            return task_state
            
        except Exception as e:
            logger.error(f"❌ Failed to resume long task {task_id}: {e}")
            return None

def main():
    """
    English: Test the long task scheduler.
    
    中文: 测试长任务调度器。
    """
    scheduler = LongTaskScheduler()
    
    # Test scheduling a long task
    test_task_id = "test_long_task_001"
    test_goal = "Implement payment feature"
    test_steps = [
        {"step": 1, "action": "analyze_repo", "description": "Analyze repository structure"},
        {"step": 2, "action": "design_api", "description": "Design payment API"},
        {"step": 3, "action": "implement_service", "description": "Implement payment service"},
        {"step": 4, "action": "write_tests", "description": "Write unit and integration tests"},
        {"step": 5, "action": "deploy", "description": "Deploy to staging environment"}
    ]
    
    success = scheduler.schedule_long_task(
        task_id=test_task_id,
        goal=test_goal,
        steps=test_steps,
        recurrence="daily"
    )
    
    if success:
        print(f"✅ Successfully scheduled long task: {test_task_id}")
        
        # Test getting due tasks
        due_tasks = scheduler.get_due_tasks()
        print(f"📋 Found {len(due_tasks)} due tasks")
        
        # Test resuming task
        resumed_task = scheduler.resume_long_task(test_task_id)
        if resumed_task:
            print(f"🔄 Successfully resumed task: {resumed_task.get('goal', 'Unknown')}")
        else:
            print("⚠️ Could not resume task (normal for new task)")
    else:
        print("❌ Failed to schedule long task")

if __name__ == "__main__":
    main()