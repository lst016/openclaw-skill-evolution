#!/usr/bin/env python3
"""
Policy Router for OpenClaw Skill Evolution v3
Routes tasks to optimal skill/workflow/tool order based on learned policies
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

from qdrant_client import QdrantClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PolicyRouter:
    """Routes tasks to optimal execution paths based on learned policies"""
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        self.workspace_path = workspace_path
        self.qdrant_client = QdrantClient(host="localhost", port=6333)
        self.policies = self.load_policies()
    
    def load_policies(self) -> Dict[str, Any]:
        """Load all policy files"""
        policies_dir = os.path.join(os.path.dirname(__file__), "..", "..", "policies")
        policies = {
            "task_policy": {},
            "skill_policy": {},
            "workflow_policy": {},
            "tool_policy": {},
            "fallback_policy": {}
        }
        
        for policy_name in policies.keys():
            policy_file = os.path.join(policies_dir, f"{policy_name}.json")
            if os.path.exists(policy_file):
                with open(policy_file, 'r', encoding='utf-8') as f:
                    policies[policy_name] = json.load(f)
        
        return policies
    
    def get_candidate_skills(self, task_type: str, limit: int = 5) -> List[Dict]:
        """Get candidate skills for a task type from Qdrant"""
        try:
            # Search skills in Qdrant
            search_result = self.qdrant_client.query_points(
                collection_name="skills",
                query=[0.1] * 1536,  # placeholder embedding
                limit=limit,
                query_filter={
                    "must": [
                        {"key": "tags", "match": {"value": task_type}},
                        {"key": "status", "match": {"value": "active"}}
                    ]
                }
            )
            
            candidates = []
            for hit in search_result.points:
                candidates.append(hit.payload)
            
            # Sort by success rate and average score
            candidates.sort(key=lambda x: (x.get("success_rate", 0), x.get("avg_score", 0)), reverse=True)
            return candidates[:limit]
            
        except Exception as e:
            logger.error(f"❌ Failed to get candidate skills for {task_type}: {e}")
            return []
    
    def get_candidate_workflows(self, task_type: str, limit: int = 5) -> List[Dict]:
        """Get candidate workflows for a task type from Qdrant"""
        try:
            # Search workflows in Qdrant
            search_result = self.qdrant_client.query_points(
                collection_name="workflows",
                query=[0.1] * 1536,  # placeholder embedding
                limit=limit,
                query_filter={
                    "must": [
                        {"key": "task_type", "match": {"value": task_type}},
                        {"key": "status", "match": {"value": "active"}}
                    ]
                }
            )
            
            candidates = []
            for hit in search_result.points:
                candidates.append(hit.payload)
            
            # Sort by success rate and average score
            candidates.sort(key=lambda x: (x.get("success_rate", 0), x.get("avg_score", 0)), reverse=True)
            return candidates[:limit]
            
        except Exception as e:
            logger.error(f"❌ Failed to get candidate workflows for {task_type}: {e}")
            return []
    
    def get_preferred_skill(self, task_type: str) -> Optional[str]:
        """Get preferred skill from skill policy"""
        skill_policy = self.policies["skill_policy"].get(task_type, {})
        return skill_policy.get("preferred_skill")
    
    def get_preferred_workflow(self, task_type: str) -> Optional[str]:
        """Get preferred workflow from workflow policy"""
        workflow_policy = self.policies["workflow_policy"].get(task_type, {})
        return workflow_policy.get("preferred_workflow")
    
    def get_preferred_tool_order(self, task_type: str) -> Optional[List[str]]:
        """Get preferred tool order from tool policy"""
        tool_policy = self.policies["tool_policy"].get(task_type, {})
        return tool_policy.get("tool_order")
    
    def get_fallback_path(self, task_type: str) -> Dict[str, Any]:
        """Get fallback path from fallback policy"""
        fallback_policy = self.policies["fallback_policy"].get(task_type, {})
        return {
            "fallback_skill": fallback_policy.get("fallback_skill"),
            "fallback_workflow": fallback_policy.get("fallback_workflow")
        }
    
    def route_task(self, task_type: str, candidate_skills: List[Dict], candidate_workflows: List[Dict]) -> Dict[str, Any]:
        """Route task to optimal execution path"""
        logger.info(f"🔄 Routing task type: {task_type}")
        
        # Get preferred paths from policies
        preferred_skill = self.get_preferred_skill(task_type)
        preferred_workflow = self.get_preferred_workflow(task_type)
        preferred_tool_order = self.get_preferred_tool_order(task_type)
        fallback_path = self.get_fallback_path(task_type)
        
        # Select best skill
        selected_skill = None
        if preferred_skill:
            # Find preferred skill in candidates
            for skill in candidate_skills:
                if skill.get("skill_name") == preferred_skill:
                    selected_skill = skill
                    break
        
        # If no preferred or not found, select best available
        if not selected_skill and candidate_skills:
            selected_skill = candidate_skills[0]
        
        # Select best workflow
        selected_workflow = None
        if preferred_workflow:
            # Find preferred workflow in candidates
            for workflow in candidate_workflows:
                if workflow.get("workflow_id") == preferred_workflow:
                    selected_workflow = workflow
                    break
        
        # If no preferred or not found, select best available
        if not selected_workflow and candidate_workflows:
            selected_workflow = candidate_workflows[0]
        
        # Determine tool order
        final_tool_order = preferred_tool_order
        if not final_tool_order and selected_workflow:
            final_tool_order = selected_workflow.get("tool_order", [])
        elif not final_tool_order and selected_skill:
            final_tool_order = selected_skill.get("required_tools", [])
        
        routing_result = {
            "selected_skill": selected_skill.get("skill_name") if selected_skill else None,
            "selected_workflow": selected_workflow.get("workflow_id") if selected_workflow else None,
            "selected_tool_order": final_tool_order,
            "fallback_path": fallback_path,
            "routing_reason": self.generate_routing_reason(task_type, selected_skill, selected_workflow)
        }
        
        logger.info(f"✅ Routed to skill: {routing_result['selected_skill']}, workflow: {routing_result['selected_workflow']}")
        return routing_result
    
    def generate_routing_reason(self, task_type: str, selected_skill: Optional[Dict], selected_workflow: Optional[Dict]) -> str:
        """Generate human-readable reason for routing decision"""
        reasons = []
        
        if selected_skill:
            success_rate = selected_skill.get("success_rate", 0)
            avg_score = selected_skill.get("avg_score", 0)
            reasons.append(f"skill success_rate={success_rate:.2f}, avg_score={avg_score:.2f}")
        
        if selected_workflow:
            success_rate = selected_workflow.get("success_rate", 0)
            avg_score = selected_workflow.get("avg_score", 0)
            reasons.append(f"workflow success_rate={success_rate:.2f}, avg_score={avg_score:.2f}")
        
        if not reasons:
            reasons.append("using fallback strategy")
        
        return "; ".join(reasons)

def main():
    """Test the policy router"""
    router = PolicyRouter()
    
    # Test task routing
    test_task_type = "debug"
    candidate_skills = [
        {
            "skill_name": "structured_debugging",
            "success_rate": 0.95,
            "avg_score": 1.8,
            "required_tools": ["read", "edit", "exec"]
        },
        {
            "skill_name": "basic_debugging", 
            "success_rate": 0.85,
            "avg_score": 1.5,
            "required_tools": ["read", "edit"]
        }
    ]
    
    candidate_workflows = [
        {
            "workflow_id": "structured_debug_v1",
            "success_rate": 0.92,
            "avg_score": 1.7,
            "tool_order": ["read", "edit", "exec"]
        }
    ]
    
    routing_result = router.route_task(test_task_type, candidate_skills, candidate_workflows)
    
    print("Routing Result:")
    print(f"Selected Skill: {routing_result['selected_skill']}")
    print(f"Selected Workflow: {routing_result['selected_workflow']}")
    print(f"Tool Order: {routing_result['selected_tool_order']}")
    print(f"Reason: {routing_result['routing_reason']}")

if __name__ == "__main__":
    main()