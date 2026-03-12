#!/usr/bin/env python3
"""
Planner Module for OpenClaw Skill Evolution v2+
Selects best skill, workflow, and experience for a given task
"""

import sys
import os
import json
from typing import Dict, List, Any, Optional
import logging

# Add the virtual environment to Python path
venv_path = os.path.join(os.path.dirname(__file__), '..', '.venv')
if os.path.exists(venv_path):
    site_packages = os.path.join(venv_path, 'lib', 'python3.14', 'site-packages')
    if os.path.exists(site_packages):
        sys.path.insert(0, site_packages)

from qdrant_client import QdrantClient
from qdrant_client.models import QueryResponse
from .embedding_service import EmbeddingService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Planner:
    """Plans the best execution strategy for a task"""
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        self.workspace_path = workspace_path
        self.qdrant_client = QdrantClient(host="localhost", port=6333)
        self.embedding_service = EmbeddingService()
        
    def search_skills(self, task: str, limit: int = 5) -> List[Dict]:
        """Search for relevant skills based on task description"""
        try:
            # Generate embedding for the task
            task_embedding = self.embedding_service.generate_embedding(task)
            
            # Search in Qdrant
            results = self.qdrant_client.query_points(
                collection_name="skills",
                query=task_embedding,
                limit=limit
            )
            
            # Extract payload from results
            skills = []
            for point in results.points:
                skill = point.payload
                skills.append(skill)
            
            logger.info(f"✅ Found {len(skills)} relevant skills")
            return skills
            
        except Exception as e:
            logger.error(f"❌ Failed to search skills: {e}")
            return []
    
    def search_workflows(self, task_type: str, limit: int = 5) -> List[Dict]:
        """Search for relevant workflows based on task type"""
        try:
            # Generate embedding for the task type
            task_embedding = self.embedding_service.generate_embedding(task_type)
            
            # Search in Qdrant
            results = self.qdrant_client.query_points(
                collection_name="workflows",
                query=task_embedding,
                limit=limit
            )
            
            # Extract payload from results
            workflows = []
            for point in results.points:
                workflow = point.payload
                workflows.append(workflow)
            
            logger.info(f"✅ Found {len(workflows)} relevant workflows")
            return workflows
            
        except Exception as e:
            logger.error(f"❌ Failed to search workflows: {e}")
            return []
    
    def search_experiences(self, task: str, limit: int = 5) -> List[Dict]:
        """Search for relevant experiences based on task description"""
        try:
            # Generate embedding for the task
            task_embedding = self.embedding_service.generate_embedding(task)
            
            # Search in Qdrant
            results = self.qdrant_client.query_points(
                collection_name="experiences",
                query=task_embedding,
                limit=limit
            )
            
            # Extract payload from results
            experiences = []
            for point in results.points:
                experience = point.payload
                experiences.append(experience)
            
            logger.info(f"✅ Found {len(experiences)} relevant experiences")
            return experiences
            
        except Exception as e:
            logger.error(f"❌ Failed to search experiences: {e}")
            return []
    
    def plan_execution(self, task: str, task_type: str) -> Dict[str, Any]:
        """Plan the best execution strategy for a task"""
        logger.info(f"🎯 Planning execution for task: {task}")
        
        # Search for relevant components
        skills = self.search_skills(task)
        workflows = self.search_workflows(task_type)
        experiences = self.search_experiences(task)
        
        # Select best components (for now, just pick the first one if available)
        selected_skill = skills[0]["skill_name"] if skills else None
        selected_workflow = workflows[0]["workflow_id"] if workflows else None
        
        plan = {
            "task": task,
            "task_type": task_type,
            "candidate_skills": [s["skill_name"] for s in skills],
            "candidate_workflows": [w["workflow_id"] for w in workflows],
            "selected_skill": selected_skill,
            "selected_workflow": selected_workflow,
            "experiences": experiences
        }
        
        logger.info(f"✅ Execution plan created: {selected_skill} + {selected_workflow}")
        return plan

def main():
    """Test the planner"""
    planner = Planner()
    
    # Test planning
    plan = planner.plan_execution(
        task="Search for information about OpenClaw Skill Evolution",
        task_type="web_search"
    )
    
    print(f"Test plan created: {plan['selected_skill']}")

if __name__ == "__main__":
    main()