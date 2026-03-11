#!/usr/bin/env python3
"""
Policy Optimizer for OpenClaw Skill Evolution v2
Automatically optimizes policies based on trajectory analysis and skill performance
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
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

class PolicyOptimizer:
    """Optimizes policies based on performance metrics"""
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        self.workspace_path = workspace_path
        self.policies_dir = os.path.join(workspace_path, "policies")
        self.qdrant_client = QdrantClient(host="localhost", port=6333)
        
        # Ensure policies directory exists
        os.makedirs(self.policies_dir, exist_ok=True)
        
        # Load current policies
        self.current_policies = self.load_policies()
    
    def load_policies(self) -> Dict[str, Any]:
        """Load current policies from files"""
        policies = {
            "task_policy": {},
            "skill_policy": {},
            "tool_policy": {},
            "routing_policy": {}
        }
        
        for policy_name in policies.keys():
            policy_file = os.path.join(self.policies_dir, f"{policy_name}.json")
            if os.path.exists(policy_file):
                with open(policy_file, 'r', encoding='utf-8') as f:
                    policies[policy_name] = json.load(f)
        
        return policies
    
    def save_policies(self, policies: Dict[str, Any]) -> None:
        """Save updated policies to files"""
        for policy_name, policy_data in policies.items():
            policy_file = os.path.join(self.policies_dir, f"{policy_name}.json")
            # Add metadata
            policy_with_metadata = {
                "version": "2.0",
                "last_updated": datetime.now().isoformat(),
                "policies": policy_data
            }
            with open(policy_file, 'w', encoding='utf-8') as f:
                json.dump(policy_with_metadata, f, indent=2, ensure_ascii=False)
        
        logger.info("✅ Policies saved successfully")
    
    def analyze_skill_performance(self, task_type: str) -> List[Dict]:
        """Analyze skill performance for a given task type"""
        try:
            # Query skills collection for this task type
            # For now, we'll simulate this with placeholder data
            # In production, this would query Qdrant for actual skill performance
            
            # Simulate skill performance data
            skills_performance = [
                {
                    "skill_id": "structured_problem_solving_v1",
                    "skill_name": "structured_problem_solving",
                    "task_type": task_type,
                    "success_rate": 0.95,
                    "avg_score": 1.8,
                    "usage_count": 15,
                    "version": 1
                },
                {
                    "skill_id": "basic_debug_v1", 
                    "skill_name": "basic_debug",
                    "task_type": task_type,
                    "success_rate": 0.75,
                    "avg_score": 1.2,
                    "usage_count": 8,
                    "version": 1
                }
            ]
            
            # Sort by success rate and average score
            sorted_skills = sorted(
                skills_performance,
                key=lambda s: (s["success_rate"], s["avg_score"]),
                reverse=True
            )
            
            return sorted_skills
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze skill performance: {e}")
            return []
    
    def should_update_policy(self, old_skill: Dict, new_skill: Dict) -> bool:
        """Determine if policy should be updated based on performance metrics"""
        # Only update if new skill has better success rate AND better average score
        if (new_skill["success_rate"] > old_skill["success_rate"] and 
            new_skill["avg_score"] > old_skill["avg_score"]):
            return True
        return False
    
    def optimize_task_policy(self, task_type: str) -> bool:
        """Optimize task policy for a specific task type"""
        logger.info(f"🔄 Optimizing task policy for: {task_type}")
        
        # Get current policy
        current_skill = self.current_policies["task_policy"].get(task_type, None)
        
        # Analyze skill performance
        skills_performance = self.analyze_skill_performance(task_type)
        if not skills_performance:
            logger.info(f"⚠️ No skill performance data for {task_type}")
            return False
        
        # Get best skill
        best_skill = skills_performance[0]
        
        # Check if update is needed
        if current_skill:
            # Find current skill performance
            current_skill_perf = None
            for skill in skills_performance:
                if skill["skill_name"] == current_skill:
                    current_skill_perf = skill
                    break
            
            if current_skill_perf and not self.should_update_policy(current_skill_perf, best_skill):
                logger.info(f"✅ Current policy is optimal for {task_type}")
                return False
        
        # Update policy
        self.current_policies["task_policy"][task_type] = best_skill["skill_name"]
        logger.info(f"🎯 Updated task policy for {task_type}: {best_skill['skill_name']}")
        return True
    
    def optimize_all_policies(self) -> Dict[str, Any]:
        """Optimize all policies based on recent trajectory data"""
        logger.info("🚀 Starting policy optimization...")
        
        # Get all unique task types from trajectories
        task_types = self.get_unique_task_types()
        
        updated_policies = {
            "task_policy": 0,
            "skill_policy": 0,
            "tool_policy": 0,
            "routing_policy": 0
        }
        
        # Optimize task policies
        for task_type in task_types:
            if self.optimize_task_policy(task_type):
                updated_policies["task_policy"] += 1
        
        # Save updated policies
        self.save_policies(self.current_policies)
        
        logger.info(f"✅ Policy optimization completed. Updated: {updated_policies}")
        return updated_policies
    
    def get_unique_task_types(self) -> List[str]:
        """Get unique task types from recent trajectories"""
        # For now, return some common task types
        # In production, this would query Qdrant trajectories collection
        return ["web_search", "debug", "code_generation", "file_edit", "analysis"]
    
    def generate_optimization_report(self, updated_policies: Dict[str, Any]) -> str:
        """Generate optimization report"""
        report = f"""
# Policy Optimization Report
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Task Policies Updated: {updated_policies['task_policy']}
- Skill Policies Updated: {updated_policies['skill_policy']}
- Tool Policies Updated: {updated_policies['tool_policy']}
- Routing Policies Updated: {updated_policies['routing_policy']}

## Recommendations
- Monitor policy performance over next 24 hours
- Review any unexpected policy changes
- Consider manual override for critical tasks

## Next Steps
- Run daily evolution loop
- Continue collecting trajectory data
- Refine optimization thresholds
"""
        return report

def main():
    """Test the policy optimizer"""
    optimizer = PolicyOptimizer()
    
    # Optimize all policies
    updated_policies = optimizer.optimize_all_policies()
    
    # Generate report
    report = optimizer.generate_optimization_report(updated_policies)
    print(report)
    
    print("✅ Policy optimization test completed")

if __name__ == "__main__":
    main()