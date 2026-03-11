#!/usr/bin/env python3
"""
Workflow Comparator for OpenClaw Skill Evolution v2
Compares different workflows to find the best execution strategy
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

class WorkflowComparator:
    """Compares workflows to identify the best execution strategy"""
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        self.workspace_path = workspace_path
        self.qdrant_client = QdrantClient(host="localhost", port=6333)
    
    def group_trajectories_by_task_type(self, trajectories: List[Dict]) -> Dict[str, List[Dict]]:
        """Group trajectories by task type"""
        grouped = {}
        for trajectory in trajectories:
            task_type = trajectory.get("task_type", "unknown")
            if task_type not in grouped:
                grouped[task_type] = []
            grouped[task_type].append(trajectory)
        return grouped
    
    def calculate_workflow_metrics(self, trajectories: List[Dict]) -> Dict[str, Any]:
        """Calculate success rate and average score for a set of trajectories"""
        if not trajectories:
            return {"success_rate": 0.0, "avg_score": 0.0, "count": 0}
        
        success_count = sum(1 for t in trajectories if t.get("success", False))
        total_score = sum(t.get("final_score", 0) for t in trajectories)
        
        success_rate = success_count / len(trajectories)
        avg_score = total_score / len(trajectories)
        
        return {
            "success_rate": success_rate,
            "avg_score": avg_score,
            "count": len(trajectories)
        }
    
    def extract_workflow_pattern(self, trajectories: List[Dict]) -> List[str]:
        """Extract common workflow pattern from trajectories"""
        if not trajectories:
            return []
        
        # Get steps from first trajectory as reference
        reference_steps = trajectories[0].get("steps", [])
        if not reference_steps:
            return []
        
        # Extract action descriptions from steps
        workflow_pattern = []
        for step in reference_steps:
            action_desc = f"{step.get('action', 'unknown')} using {step.get('tool', 'unknown')}"
            workflow_pattern.append(action_desc)
        
        return workflow_pattern
    
    def compare_workflows(self, trajectories: List[Dict]) -> Dict[str, Any]:
        """Compare workflows and identify the best one"""
        logger.info(f"🔍 Comparing {len(trajectories)} trajectories for workflow optimization")
        
        # Group by task type
        grouped_trajectories = self.group_trajectories_by_task_type(trajectories)
        
        best_workflows = {}
        
        for task_type, task_trajectories in grouped_trajectories.items():
            if len(task_trajectories) < 3:
                logger.info(f"⚠️ Skipping task type '{task_type}': only {len(task_trajectories)} trajectories (need >= 3)")
                continue
            
            # Calculate metrics
            metrics = self.calculate_workflow_metrics(task_trajectories)
            
            # Check if metrics meet quality thresholds
            if metrics["success_rate"] < 0.8 or metrics["avg_score"] < 0.7:
                logger.info(f"⚠️ Skipping task type '{task_type}': metrics below threshold (success_rate: {metrics['success_rate']:.2f}, avg_score: {metrics['avg_score']:.2f})")
                continue
            
            # Extract workflow pattern
            workflow_pattern = self.extract_workflow_pattern(task_trajectories)
            
            best_workflows[task_type] = {
                "workflow_id": f"{task_type}_workflow_v1",
                "task_type": task_type,
                "description": f"Optimized workflow for {task_type} tasks",
                "steps": workflow_pattern,
                "tool_order": list(set(tool for t in task_trajectories for tool in t.get("tools_used", []))),
                "success_rate": metrics["success_rate"],
                "avg_score": metrics["avg_score"],
                "usage_count": metrics["count"],
                "version": 1,
                "status": "active",
                "source_trajectory_ids": [t.get("trajectory_id") for t in task_trajectories],
                "created_at": None,
                "updated_at": None
            }
            
            logger.info(f"✅ Identified best workflow for '{task_type}': success_rate={metrics['success_rate']:.2f}, avg_score={metrics['avg_score']:.2f}")
        
        return best_workflows
    
    def get_best_workflow_for_task_type(self, task_type: str) -> Optional[Dict]:
        """Get the best workflow for a specific task type from Qdrant"""
        try:
            # Search for workflows in Qdrant
            search_result = self.qdrant_client.query_points(
                collection_name="workflows",
                query=[0.1] * 1536,  # placeholder embedding
                limit=1,
                query_filter={
                    "must": [
                        {"key": "task_type", "match": {"value": task_type}},
                        {"key": "status", "match": {"value": "active"}}
                    ]
                }
            )
            
            if search_result.points:
                return search_result.points[0].payload
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to get best workflow for task type '{task_type}': {e}")
            return None

def main():
    """Test the workflow comparator"""
    comparator = WorkflowComparator()
    
    # Test trajectories
    test_trajectories = [
        {
            "trajectory_id": "test-1",
            "task": "Debug Python code error",
            "task_type": "debug",
            "steps": [
                {"step": 1, "action": "analyze_error", "tool": "read", "success": True, "score": 0.9},
                {"step": 2, "action": "inspect_code", "tool": "read", "success": True, "score": 0.8},
                {"step": 3, "action": "fix_error", "tool": "edit", "success": True, "score": 0.9}
            ],
            "tools_used": ["read", "edit"],
            "success": True,
            "final_score": 0.87
        },
        {
            "trajectory_id": "test-2",
            "task": "Fix JavaScript bug",
            "task_type": "debug", 
            "steps": [
                {"step": 1, "action": "analyze_error", "tool": "read", "success": True, "score": 0.8},
                {"step": 2, "action": "inspect_code", "tool": "read", "success": True, "score": 0.9},
                {"step": 3, "action": "fix_error", "tool": "edit", "success": True, "score": 0.8}
            ],
            "tools_used": ["read", "edit"],
            "success": True,
            "final_score": 0.83
        },
        {
            "trajectory_id": "test-3",
            "task": "Resolve TypeScript compilation error",
            "task_type": "debug",
            "steps": [
                {"step": 1, "action": "analyze_error", "tool": "read", "success": True, "score": 0.9},
                {"step": 2, "action": "inspect_code", "tool": "read", "success": True, "score": 0.9},
                {"step": 3, "action": "fix_error", "tool": "edit", "success": True, "score": 0.9}
            ],
            "tools_used": ["read", "edit"],
            "success": True,
            "final_score": 0.9
        }
    ]
    
    # Compare workflows
    best_workflows = comparator.compare_workflows(test_trajectories)
    
    if best_workflows:
        print("Best workflows identified:")
        for task_type, workflow in best_workflows.items():
            print(f"  {task_type}: success_rate={workflow['success_rate']:.2f}, avg_score={workflow['avg_score']:.2f}")
            print(f"    Steps: {workflow['steps']}")
    else:
        print("No best workflows identified")

if __name__ == "__main__":
    main()