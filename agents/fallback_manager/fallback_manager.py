#!/usr/bin/env python3
"""
Fallback Manager for OpenClaw Skill Evolution v3
Manages fallback strategies when current policy underperforms
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

class FallbackManager:
    """Manages fallback strategies for failed executions"""
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        self.workspace_path = workspace_path
        self.qdrant_client = QdrantClient(host="localhost", port=6333)
        self.policies_dir = os.path.join(os.path.dirname(__file__), "..", "..", "policies")
        self.fallback_policy_file = os.path.join(self.policies_dir, "fallback_policy.json")
        
        # Load fallback policy
        self.fallback_policy = self.load_fallback_policy()
    
    def load_fallback_policy(self) -> Dict[str, Any]:
        """Load fallback policy from file"""
        if os.path.exists(self.fallback_policy_file):
            with open(self.fallback_policy_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {"version": "1.0", "policies": {}}
    
    def save_fallback_policy(self) -> None:
        """Save fallback policy to file"""
        with open(self.fallback_policy_file, 'w', encoding='utf-8') as f:
            json.dump(self.fallback_policy, f, indent=2, ensure_ascii=False)
        logger.info("✅ Saved fallback policy")
    
    def should_trigger_fallback(self, task_type: str, failure_count: int, consecutive_failures: int) -> bool:
        """Determine if fallback should be triggered"""
        # Trigger fallback after 2 consecutive failures
        if consecutive_failures >= 2:
            logger.info(f"⚠️ Triggering fallback for task type '{task_type}': {consecutive_failures} consecutive failures")
            return True
        
        # Trigger fallback if failure rate is too high (more than 50% in last 5 attempts)
        if failure_count >= 3 and consecutive_failures >= 1:
            logger.info(f"⚠️ Triggering fallback for task type '{task_type}': high failure rate")
            return True
        
        return False
    
    def get_fallback_strategy(self, task_type: str) -> Optional[Dict[str, Any]]:
        """Get fallback strategy for a task type"""
        if task_type in self.fallback_policy["policies"]:
            return self.fallback_policy["policies"][task_type]
        else:
            # Generate fallback from historical data
            fallback = self.generate_fallback_from_history(task_type)
            if fallback:
                self.fallback_policy["policies"][task_type] = fallback
                self.save_fallback_policy()
            return fallback
    
    def generate_fallback_from_history(self, task_type: str) -> Optional[Dict[str, Any]]:
        """Generate fallback strategy from historical trajectories"""
        try:
            # Search for successful trajectories of this task type
            search_result = self.qdrant_client.query_points(
                collection_name="trajectories",
                query=[0.1] * 1536,  # placeholder embedding
                limit=10,
                query_filter={
                    "must": [
                        {"key": "task_type", "match": {"value": task_type}},
                        {"key": "success", "match": {"value": True}}
                    ]
                }
            )
            
            if not search_result.points:
                logger.warning(f"❌ No successful trajectories found for task type '{task_type}'")
                return None
            
            # Find the second-best performing skill/workflow combination
            trajectories = [hit.payload for hit in search_result.points]
            
            # Sort by score (descending)
            sorted_trajectories = sorted(trajectories, key=lambda t: t.get("final_score", 0), reverse=True)
            
            if len(sorted_trajectories) < 2:
                # Use the best one if only one exists
                best_trajectory = sorted_trajectories[0]
            else:
                # Use the second-best as fallback
                best_trajectory = sorted_trajectories[1]
            
            fallback_strategy = {
                "fallback_skill": best_trajectory.get("skill_name"),
                "fallback_workflow": best_trajectory.get("workflow_name"),
                "fallback_tool_order": best_trajectory.get("tools_used", []),
                "confidence": best_trajectory.get("final_score", 0),
                "reason": "Second-best historical performance"
            }
            
            logger.info(f"✅ Generated fallback strategy for task type '{task_type}': {fallback_strategy['fallback_skill']}")
            return fallback_strategy
            
        except Exception as e:
            logger.error(f"❌ Failed to generate fallback for task type '{task_type}': {e}")
            return None
    
    def record_failure(self, trajectory: Dict[str, Any], failure_reason: str) -> None:
        """Record a failure for learning purposes"""
        try:
            failure_id = f"failure_{trajectory.get('trajectory_id', 'unknown')}"
            created_at = trajectory.get("created_at", None)
            
            failure_record = {
                "failure_id": failure_id,
                "task_type": trajectory.get("task_type", "unknown"),
                "wrong_skill": trajectory.get("skill_name"),
                "wrong_workflow": trajectory.get("workflow_name"),
                "wrong_tool_order": trajectory.get("tools_used", []),
                "failure_reason": failure_reason,
                "trajectory_id": trajectory.get("trajectory_id"),
                "score": trajectory.get("final_score", 0),
                "created_at": created_at
            }
            
            # Save to Qdrant failures collection
            placeholder_embedding = [0.1] * 1536
            embedding_content = f"{failure_record['task_type']} {failure_record['failure_reason']}"
            
            from qdrant_client.models import PointStruct
            point = PointStruct(
                id=failure_id,
                vector=placeholder_embedding,
                payload=failure_record
            )
            
            self.qdrant_client.upsert(
                collection_name="failures",
                points=[point]
            )
            
            logger.info(f"✅ Recorded failure: {failure_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to record failure: {e}")
    
    def get_failure_history(self, task_type: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get failure history for a task type"""
        try:
            search_result = self.qdrant_client.query_points(
                collection_name="failures",
                query=[0.1] * 1536,
                limit=limit,
                query_filter={
                    "must": [
                        {"key": "task_type", "match": {"value": task_type}}
                    ]
                }
            )
            
            failures = [hit.payload for hit in search_result.points]
            logger.info(f"🔍 Found {len(failures)} failures for task type '{task_type}'")
            return failures
            
        except Exception as e:
            logger.error(f"❌ Failed to get failure history for task type '{task_type}': {e}")
            return []
    
    def adjust_tool_order_based_on_failures(self, task_type: str, current_tool_order: List[str]) -> List[str]:
        """Adjust tool order based on failure patterns"""
        failures = self.get_failure_history(task_type, limit=10)
        
        if not failures:
            return current_tool_order
        
        # Analyze which tools are causing failures
        problematic_tools = {}
        for failure in failures:
            wrong_tools = failure.get("wrong_tool_order", [])
            for tool in wrong_tools:
                if tool not in problematic_tools:
                    problematic_tools[tool] = 0
                problematic_tools[tool] += 1
        
        # If we have problematic tools, try to reorder
        if problematic_tools:
            # Move problematic tools to the end
            adjusted_order = []
            problematic_list = list(problematic_tools.keys())
            
            for tool in current_tool_order:
                if tool not in problematic_list:
                    adjusted_order.append(tool)
            
            for tool in problematic_list:
                if tool in current_tool_order and tool not in adjusted_order:
                    adjusted_order.append(tool)
            
            if adjusted_order != current_tool_order:
                logger.info(f"🔄 Adjusted tool order for task type '{task_type}': {current_tool_order} → {adjusted_order}")
                return adjusted_order
        
        return current_tool_order

def main():
    """Test the fallback manager"""
    manager = FallbackManager()
    
    # Test fallback strategy generation
    test_task_type = "debug"
    fallback = manager.get_fallback_strategy(test_task_type)
    
    if fallback:
        print(f"Fallback strategy for '{test_task_type}':")
        print(f"  Skill: {fallback['fallback_skill']}")
        print(f"  Workflow: {fallback['fallback_workflow']}")
        print(f"  Tool Order: {fallback['fallback_tool_order']}")
        print(f"  Confidence: {fallback['confidence']}")
        print(f"  Reason: {fallback['reason']}")
    else:
        print(f"No fallback strategy available for '{test_task_type}'")

if __name__ == "__main__":
    main()