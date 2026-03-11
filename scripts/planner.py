#!/usr/bin/env python3
"""
Planner for OpenClaw Skill Evolution (FIXED VERSION)
Retrieves and selects optimal skills, workflows, and experiences for task execution
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
from qdrant_client.models import PointStruct

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Planner:
    """Retrieves and selects optimal skills, workflows, and experiences for task execution"""
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        self.workspace_path = workspace_path
        self.qdrant_client = QdrantClient(host="localhost", port=6333)
        
        # Load policies
        self.policies = self.load_policies()
    
    def load_policies(self) -> Dict[str, Any]:
        """Load policies from policy files"""
        policies_dir = os.path.join(os.path.dirname(__file__), "..", "policies")
        policies = {
            "task_policy": {},
            "skill_policy": {},
            "tool_policy": {},
            "routing_policy": {}
        }
        
        for policy_name in policies.keys():
            policy_file = os.path.join(policies_dir, f"{policy_name}.json")
            if os.path.exists(policy_file):
                with open(policy_file, 'r', encoding='utf-8') as f:
                    policies[policy_name] = json.load(f)
        
        return policies
    
    def search_skills(self, task: str, task_type: str = None, limit: int = 3) -> List[Dict]:
        """Search for relevant skills based on task"""
        try:
            # Create embedding content
            embedding_content = f"{task} {task_type or 'unknown'}"
            
            # Placeholder embedding
            placeholder_embedding = [0.1] * 1536
            
            # Search in Qdrant
            search_result = self.qdrant_client.query_points(
                collection_name="skills",
                query=placeholder_embedding,
                limit=limit,
                query_filter={
                    "must": [
                        {"key": "status", "match": {"value": "active"}}
                    ]
                }
            )
            
            # Extract payloads from points
            skills = []
            for point in search_result.points:
                skills.append(point.payload)
            
            logger.info(f"🔍 Found {len(skills)} relevant skills")
            return skills
            
        except Exception as e:
            logger.error(f"❌ Failed to search skills: {e}")
            return []
    
    def search_workflows(self, task_type: str, limit: int = 3) -> List[Dict]:
        """Search for relevant workflows based on task type"""
        try:
            # Create embedding content
            embedding_content = f"{task_type}"
            
            # Placeholder embedding
            placeholder_embedding = [0.1] * 1536
            
            # Search in Qdrant
            search_result = self.qdrant_client.query_points(
                collection_name="workflows",
                query=placeholder_embedding,
                limit=limit,
                query_filter={
                    "must": [
                        {"key": "status", "match": {"value": "active"}}
                    ]
                }
            )
            
            # Extract payloads from points
            workflows = []
            for point in search_result.points:
                workflows.append(point.payload)
            
            logger.info(f"🔍 Found {len(workflows)} relevant workflows")
            return workflows
            
        except Exception as e:
            logger.error(f"❌ Failed to search workflows: {e}")
            return []
    
    def search_experiences(self, task: str, limit: int = 3) -> List[Dict]:
        """Search for relevant experiences based on task"""
        try:
            # Create embedding content
            embedding_content = f"{task}"
            
            # Placeholder embedding
            placeholder_embedding = [0.1] * 1536
            
            # Search in Qdrant
            search_result = self.qdrant_client.query_points(
                collection_name="experiences",
                query=placeholder_embedding,
                limit=limit,
                query_filter={
                    "must": [
                        {"key": "status", "match": {"value": "active"}}
                    ]
                }
            )
            
            # Extract payloads from points
            experiences = []
            for point in search_result.points:
                experiences.append(point.payload)
            
            logger.info(f"🔍 Found {len(experiences)} relevant experiences")
            return experiences
            
        except Exception as e:
            logger.error(f"❌ Failed to search experiences: {e}")
            return []
    
    def identify_task_type(self, task: str) -> str:
        """Identify the task type from the task description"""
        task_lower = task.lower()
        
        # Simple task type identification
        if "search" in task_lower or "find" in task_lower or "look for" in task_lower:
            return "web_search"
        elif "write" in task_lower or "create" in task_lower or "generate" in task_lower:
            return "content_creation"
        elif "edit" in task_lower or "modify" in task_lower or "update" in task_lower:
            return "file_edit"
        elif "analyze" in task_lower or "check" in task_lower or "review" in task_lower:
            return "analysis"
        else:
            return "general"
    
    def select_best_skill(self, skills: List[Dict]) -> Optional[Dict]:
        """Select the best skill from candidates based on success rate and score"""
        if not skills:
            return None
        
        # Sort by success rate (primary) and average score (secondary)
        sorted_skills = sorted(
            skills,
            key=lambda s: (s.get("success_rate", 0), s.get("avg_score", 0)),
            reverse=True
        )
        
        return sorted_skills[0]
    
    def select_best_workflow(self, workflows: List[Dict]) -> Optional[Dict]:
        """Select the best workflow from candidates"""
        if not workflows:
            return None
        
        # Sort by success rate and usage count
        sorted_workflows = sorted(
            workflows,
            key=lambda w: (w.get("success_rate", 0), w.get("usage_count", 0)),
            reverse=True
        )
        
        return sorted_workflows[0]
    
    def select_best_experience(self, experiences: List[Dict]) -> Optional[Dict]:
        """Select the best experience from candidates"""
        if not experiences:
            return None
        
        # Sort by score and success count
        sorted_experiences = sorted(
            experiences,
            key=lambda e: (e.get("score", 0), e.get("success_count", 0)),
            reverse=True
        )
        
        return sorted_experiences[0]
    
    def generate_execution_plan(
        self,
        task: str,
        candidate_skills: List[Dict],
        candidate_workflows: List[Dict],
        candidate_experiences: List[Dict]
    ) -> Dict:
        """Generate an execution plan based on available resources"""
        # Identify task type
        task_type = self.identify_task_type(task)
        
        # Select best resources
        selected_skill = self.select_best_skill(candidate_skills)
        selected_workflow = self.select_best_workflow(candidate_workflows)
        selected_experience = self.select_best_experience(candidate_experiences)
        
        # Generate planned steps
        planned_steps = []
        planned_tool_order = []
        
        if selected_skill and "required_tools" in selected_skill:
            planned_tool_order = selected_skill["required_tools"]
            planned_steps = selected_skill.get("steps", [])
        elif selected_experience:
            # Extract steps from experience workflow
            workflow = selected_experience.get("workflow", "")
            if workflow and isinstance(workflow, str):
                try:
                    import ast
                    planned_steps = ast.literal_eval(workflow)
                except:
                    planned_steps = []
        
        execution_plan = {
            "task_type": task_type,
            "candidate_skills": candidate_skills,
            "candidate_workflows": candidate_workflows,
            "candidate_experiences": candidate_experiences,
            "selected_skill": selected_skill.get("skill_name") if selected_skill else None,
            "selected_workflow": selected_workflow.get("workflow_id") if selected_workflow else None,
            "selected_experience": selected_experience.get("experience_id") if selected_experience else None,
            "planned_steps": planned_steps,
            "planned_tool_order": planned_tool_order,
            "fallback_needed": not (selected_skill or selected_workflow)
        }
        
        return execution_plan
    
    def plan_task(self, task: str) -> Dict:
        """Complete planning workflow for a task"""
        logger.info(f"🎯 Planning task: {task}")
        
        # Identify task type
        task_type = self.identify_task_type(task)
        logger.info(f"📋 Task type identified: {task_type}")
        
        # Search for relevant resources
        candidate_skills = self.search_skills(task, task_type)
        candidate_workflows = self.search_workflows(task_type)
        candidate_experiences = self.search_experiences(task)
        
        # Generate execution plan
        execution_plan = self.generate_execution_plan(
            task,
            candidate_skills,
            candidate_workflows,
            candidate_experiences
        )
        
        logger.info(f"🎯 Execution plan generated: {len(candidate_skills)} skills, {len(candidate_workflows)} workflows, {len(candidate_experiences)} experiences")
        return execution_plan

def main():
    """Test the planner"""
    planner = Planner()
    
    # Test task planning
    test_task = "Search for information about OpenClaw Skill Evolution"
    execution_plan = planner.plan_task(test_task)
    
    print("Execution Plan:")
    print(f"Task Type: {execution_plan['task_type']}")
    print(f"Selected Skill: {execution_plan['selected_skill']}")
    print(f"Selected Workflow: {execution_plan['selected_workflow']}")
    print(f"Selected Experience: {execution_plan['selected_experience']}")
    print(f"Planned Steps: {execution_plan['planned_steps']}")
    print(f"Planned Tool Order: {execution_plan['planned_tool_order']}")
    print(f"Fallback Needed: {execution_plan['fallback_needed']}")

if __name__ == "__main__":
    main()