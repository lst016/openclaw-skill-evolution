#!/usr/bin/env python3
"""
Planner Module for OpenClaw Skill Evolution v3
Intelligent task routing with policy-based decision making.

中文注释:
规划器模块 - 基于策略的智能任务路由决策
"""

import sys
import os
import json
import logging
from typing import Dict, List, Optional, Tuple

# Add the virtual environment to Python path
venv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.venv')
if os.path.exists(venv_path):
    site_packages = os.path.join(venv_path, 'lib', 'python3.14', 'site-packages')
    if os.path.exists(site_packages):
        sys.path.insert(0, site_packages)

from qdrant_client import QdrantClient
from qdrant_client.models import QueryResponse
from ..embedding_service import EmbeddingService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Planner:
    """
    English: Intelligent task planner that routes tasks to optimal skill/workflow combinations.
    
    中文: 智能任务规划器，将任务路由到最优的技能/工作流组合。
    """
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        """
        English: Initialize the planner with Qdrant client and embedding service.
        
        中文: 初始化规划器，包含 Qdrant 客户端和嵌入服务。
        """
        self.workspace_path = workspace_path
        self.qdrant_client = QdrantClient(host="localhost", port=6333)
        self.embedding_service = EmbeddingService()
        logger.info("✅ Planner initialized with local BGE embedding model")
    
    def _get_task_embedding(self, task: str) -> List[float]:
        """
        English: Generate embedding for the given task using local BGE model.
        
        中文: 使用本地 BGE 模型为给定任务生成嵌入向量。
        """
        return self.embedding_service.get_embedding(task)
    
    def search_skills(self, task: str, limit: int = 5) -> List[Dict]:
        """
        English: Search for relevant skills based on task embedding.
        
        中文: 基于任务嵌入向量搜索相关技能。
        """
        try:
            task_embedding = self._get_task_embedding(task)
            
            # Query Qdrant for similar skills
            results = self.qdrant_client.query_points(
                collection_name="skills",
                query=task_embedding,
                limit=limit
            )
            
            # Extract payloads from results
            skills = []
            if hasattr(results, 'points'):
                for point in results.points:
                    if hasattr(point, 'payload'):
                        skills.append(point.payload)
            
            logger.info(f"🔍 Found {len(skills)} relevant skills for task: {task[:50]}...")
            return skills
            
        except Exception as e:
            logger.error(f"❌ Failed to search skills: {e}")
            return []
    
    def search_workflows(self, task_type: str, limit: int = 3) -> List[Dict]:
        """
        English: Search for relevant workflows based on task type.
        
        中文: 基于任务类型搜索相关工作流。
        """
        try:
            task_embedding = self._get_task_embedding(task_type)
            
            # Query Qdrant for similar workflows  
            results = self.qdrant_client.query_points(
                collection_name="workflows",
                query=task_embedding,
                limit=limit
            )
            
            # Extract payloads from results
            workflows = []
            if hasattr(results, 'points'):
                for point in results.points:
                    if hasattr(point, 'payload'):
                        workflows.append(point.payload)
            
            logger.info(f"🔍 Found {len(workflows)} relevant workflows for task_type: {task_type}")
            return workflows
            
        except Exception as e:
            logger.error(f"❌ Failed to search workflows: {e}")
            return []
    
    def search_experiences(self, task: str, limit: int = 3) -> List[Dict]:
        """
        English: Search for relevant experiences based on task embedding.
        
        中文: 基于任务嵌入向量搜索相关经验。
        """
        try:
            task_embedding = self._get_task_embedding(task)
            
            # Query Qdrant for similar experiences
            results = self.qdrant_client.query_points(
                collection_name="experiences", 
                query=task_embedding,
                limit=limit
            )
            
            # Extract payloads from results
            experiences = []
            if hasattr(results, 'points'):
                for point in results.points:
                    if hasattr(point, 'payload'):
                        experiences.append(point.payload)
            
            logger.info(f"🔍 Found {len(experiences)} relevant experiences for task: {task[:50]}...")
            return experiences
            
        except Exception as e:
            logger.error(f"❌ Failed to search experiences: {e}")
            return []
    
    def plan_task(self, task: str, task_type: str = "general") -> Dict:
        """
        English: Create a complete execution plan for the given task.
        
        中文: 为给定任务创建完整的执行计划。
        """
        logger.info(f"📋 Planning task: {task}")
        
        # Search for relevant components
        candidate_skills = self.search_skills(task)
        candidate_workflows = self.search_workflows(task_type)
        candidate_experiences = self.search_experiences(task)
        
        # Select best options (for now, just pick the first ones)
        selected_skill = candidate_skills[0] if candidate_skills else None
        selected_workflow = candidate_workflows[0] if candidate_workflows else None
        
        plan = {
            "task": task,
            "task_type": task_type,
            "candidate_skills": candidate_skills,
            "candidate_workflows": candidate_workflows,
            "candidate_experiences": candidate_experiences,
            "selected_skill": selected_skill["skill_name"] if selected_skill else None,
            "selected_workflow": selected_workflow["workflow_id"] if selected_workflow else None,
            "planned_steps": selected_workflow["steps"] if selected_workflow else [],
            "planned_tool_order": selected_workflow["tool_order"] if selected_workflow else []
        }
        
        logger.info(f"🎯 Task plan created successfully")
        return plan

def main():
    """Test the planner module"""
    planner = Planner()
    
    # Test planning
    test_plan = planner.plan_task(
        task="Search for information about OpenClaw Skill Evolution",
        task_type="web_search"
    )
    
    print(f"Test plan created for task: {test_plan['task']}")
    print(f"Selected skill: {test_plan['selected_skill']}")
    print(f"Selected workflow: {test_plan['selected_workflow']}")

if __name__ == "__main__":
    main()