#!/usr/bin/env python3
"""
Policy Updater for OpenClaw Skill Evolution v3
Manages the three-state policy lifecycle: active/candidate/archived
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging

# Add the virtual environment to Python path
venv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.venv')
if os.path.exists(venv_path):
    site_packages = os.path.join(venv_path, 'lib', 'python3.14', 'site-packages')
    if os.path.exists(site_packages):
        sys.path.insert(0, site_packages)

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PolicyUpdater:
    """Manages policy updates with three-state lifecycle"""
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        self.workspace_path = workspace_path
        self.policies_dir = os.path.join(workspace_path, "policies")
        self.policy_history_dir = os.path.join(self.policies_dir, "history")
        self.logs_dir = os.path.join(workspace_path, "logs", "policy_updates")
        self.qdrant_client = QdrantClient(host="localhost", port=6333)
        
        # Ensure directories exist
        os.makedirs(self.policy_history_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Load current policies
        self.current_policies = self.load_policies()
    
    def load_policies(self) -> Dict[str, Any]:
        """Load all current policy files"""
        policies = {
            "task_policy": {},
            "skill_policy": {},
            "workflow_policy": {},
            "tool_policy": {},
            "fallback_policy": {}
        }
        
        for policy_name in policies.keys():
            policy_file = os.path.join(self.policies_dir, f"{policy_name}.json")
            if os.path.exists(policy_file):
                with open(policy_file, 'r', encoding='utf-8') as f:
                    policies[policy_name] = json.load(f)
        
        return policies
    
    def save_policy(self, policy_name: str, policy_data: Dict) -> None:
        """Save policy to file"""
        policy_file = os.path.join(self.policies_dir, f"{policy_name}.json")
        with open(policy_file, 'w', encoding='utf-8') as f:
            json.dump(policy_data, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Saved {policy_name} to {policy_file}")
    
    def archive_policy(self, policy_name: str, policy_data: Dict, reason: str = "") -> None:
        """Archive a policy with timestamp and reason"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_file = os.path.join(self.policy_history_dir, f"{policy_name}_archived_{timestamp}.json")
        
        archived_data = {
            "policy": policy_data,
            "archived_at": datetime.now().isoformat(),
            "reason": reason,
            "version": policy_data.get("version", 1)
        }
        
        with open(archive_file, 'w', encoding='utf-8') as f:
            json.dump(archived_data, f, indent=2, ensure_ascii=False)
        logger.info(f"📦 Archived {policy_name} to {archive_file}")
    
    def create_candidate_policy(self, task_type: str, new_policy: Dict, evidence: List[Dict]) -> Dict:
        """Create a candidate policy based on new evidence"""
        candidate = {
            "policy_id": f"{task_type}_candidate_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "task_type": task_type,
            "preferred_skill": new_policy.get("preferred_skill"),
            "preferred_workflow": new_policy.get("preferred_workflow"),
            "preferred_tool_order": new_policy.get("preferred_tool_order"),
            "confidence": new_policy.get("confidence", 0.0),
            "success_rate": new_policy.get("success_rate", 0.0),
            "avg_score": new_policy.get("avg_score", 0.0),
            "usage_count": len(evidence),
            "version": 1,
            "status": "candidate",
            "evidence_count": len(evidence),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "evidence_trajectories": [t.get("trajectory_id") for t in evidence]
        }
        
        return candidate
    
    def evaluate_candidate_against_active(self, candidate: Dict, active_policy: Dict) -> bool:
        """Evaluate if candidate is better than active policy"""
        # Require at least 3 successful executions
        if candidate["evidence_count"] < 3:
            logger.info(f"❌ Candidate rejected: insufficient evidence ({candidate['evidence_count']} < 3)")
            return False
        
        # Require higher success rate
        if candidate["success_rate"] <= active_policy.get("success_rate", 0.0):
            logger.info(f"❌ Candidate rejected: success rate not improved ({candidate['success_rate']:.2f} <= {active_policy.get('success_rate', 0.0):.2f})")
            return False
        
        # Require higher average score
        if candidate["avg_score"] <= active_policy.get("avg_score", 0.0):
            logger.info(f"❌ Candidate rejected: average score not improved ({candidate['avg_score']:.2f} <= {active_policy.get('avg_score', 0.0):.2f})")
            return False
        
        # Require confidence threshold
        if candidate["confidence"] < 0.8:
            logger.info(f"❌ Candidate rejected: confidence too low ({candidate['confidence']:.2f} < 0.8)")
            return False
        
        logger.info(f"✅ Candidate approved: meets all promotion criteria")
        return True
    
    def promote_candidate_to_active(self, candidate: Dict, policy_type: str) -> None:
        """Promote candidate policy to active status"""
        task_type = candidate["task_type"]
        
        # Archive current active policy
        if task_type in self.current_policies[policy_type]:
            current_active = self.current_policies[policy_type][task_type]
            self.archive_policy(policy_type, current_active, f"Replaced by candidate {candidate['policy_id']}")
        
        # Update active policy
        new_active = {
            "preferred_skill": candidate["preferred_skill"],
            "preferred_workflow": candidate["preferred_workflow"],
            "preferred_tool_order": candidate["preferred_tool_order"],
            "confidence": candidate["confidence"],
            "success_rate": candidate["success_rate"],
            "avg_score": candidate["avg_score"],
            "version": current_active.get("version", 0) + 1 if task_type in self.current_policies[policy_type] else 1
        }
        
        self.current_policies[policy_type][task_type] = new_active
        self.save_policy(policy_type, self.current_policies[policy_type])
        
        # Save to Qdrant
        self.save_policy_to_qdrant(candidate, "policies")
        
        logger.info(f"🚀 Promoted candidate {candidate['policy_id']} to active for {task_type}")
    
    def save_policy_to_qdrant(self, policy: Dict, collection_name: str = "policies") -> bool:
        """Save policy to Qdrant vector database"""
        try:
            # Create embedding content
            embedding_content = f"{policy['task_type']} {policy.get('preferred_skill', '')} {policy.get('preferred_workflow', '')}"
            
            # Placeholder embedding (1536-dimensional)
            placeholder_embedding = [0.1] * 1536
            
            # Create point for Qdrant
            point = PointStruct(
                id=policy["policy_id"],
                vector=placeholder_embedding,
                payload={
                    "policy_id": policy["policy_id"],
                    "task_type": policy["task_type"],
                    "preferred_skill": policy.get("preferred_skill"),
                    "preferred_workflow": policy.get("preferred_workflow"),
                    "preferred_tool_order": policy.get("preferred_tool_order"),
                    "confidence": policy.get("confidence"),
                    "success_rate": policy.get("success_rate"),
                    "avg_score": policy.get("avg_score"),
                    "usage_count": policy.get("usage_count"),
                    "version": policy.get("version"),
                    "status": policy.get("status"),
                    "created_at": policy.get("created_at"),
                    "updated_at": policy.get("updated_at")
                }
            )
            
            # Upsert to Qdrant
            self.qdrant_client.upsert(
                collection_name=collection_name,
                points=[point]
            )
            
            logger.info(f"✅ Saved policy to Qdrant: {policy['policy_id']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save policy to Qdrant: {e}")
            return False
    
    def update_policy_from_trajectories(self, task_type: str, trajectories: List[Dict]) -> bool:
        """Update policy based on trajectory analysis"""
        logger.info(f"🔄 Updating policy for task type: {task_type}")
        
        # Filter successful trajectories
        successful_trajectories = [t for t in trajectories if t.get("success", False)]
        if len(successful_trajectories) < 3:
            logger.info(f"⚠️ Not enough successful trajectories ({len(successful_trajectories)}) for policy update")
            return False
        
        # Calculate metrics
        success_rate = len(successful_trajectories) / len(trajectories)
        avg_score = sum(t.get("final_score", 0) for t in successful_trajectories) / len(successful_trajectories)
        
        # Extract best skill/workflow/tool order
        skill_counts = {}
        workflow_counts = {}
        tool_orders = []
        
        for traj in successful_trajectories:
            skill_name = traj.get("skill_name")
            workflow_name = traj.get("workflow_name")
            tools_used = traj.get("tools_used", [])
            
            if skill_name:
                skill_counts[skill_name] = skill_counts.get(skill_name, 0) + 1
            if workflow_name:
                workflow_counts[workflow_name] = workflow_counts.get(workflow_name, 0) + 1
            if tools_used:
                tool_orders.append(tools_used)
        
        # Get most common skill and workflow
        preferred_skill = max(skill_counts.items(), key=lambda x: x[1])[0] if skill_counts else None
        preferred_workflow = max(workflow_counts.items(), key=lambda x: x[1])[0] if workflow_counts else None
        
        # Get most stable tool order
        preferred_tool_order = tool_orders[0] if tool_orders else []
        
        # Create new policy
        new_policy = {
            "preferred_skill": preferred_skill,
            "preferred_workflow": preferred_workflow,
            "preferred_tool_order": preferred_tool_order,
            "confidence": min(1.0, len(successful_trajectories) / 5.0),  # Scale confidence
            "success_rate": success_rate,
            "avg_score": avg_score
        }
        
        # Check if we have an active policy for this task type
        has_active_policy = (
            task_type in self.current_policies["skill_policy"] or 
            task_type in self.current_policies["workflow_policy"]
        )
        
        if has_active_policy:
            # Create candidate policy
            candidate = self.create_candidate_policy(task_type, new_policy, successful_trajectories)
            
            # Evaluate against active policy
            active_skill_policy = self.current_policies["skill_policy"].get(task_type, {})
            if self.evaluate_candidate_against_active(candidate, active_skill_policy):
                # Promote to active
                self.promote_candidate_to_active(candidate, "skill_policy")
                return True
            else:
                logger.info(f"❌ Candidate not promoted for {task_type}")
                return False
        else:
            # First-time policy creation
            self.current_policies["skill_policy"][task_type] = {
                "preferred_skill": preferred_skill,
                "confidence": new_policy["confidence"],
                "success_rate": success_rate,
                "avg_score": avg_score,
                "version": 1
            }
            
            self.current_policies["workflow_policy"][task_type] = {
                "preferred_workflow": preferred_workflow,
                "version": 1
            }
            
            self.current_policies["tool_policy"][task_type] = {
                "tool_order": preferred_tool_order,
                "version": 1
            }
            
            self.save_policy("skill_policy", self.current_policies["skill_policy"])
            self.save_policy("workflow_policy", self.current_policies["workflow_policy"])
            self.save_policy("tool_policy", self.current_policies["tool_policy"])
            
            logger.info(f"🆕 Created initial policy for {task_type}")
            return True
    
    def get_policy_update_log_file(self) -> str:
        """Get the policy update log file for today"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(self.logs_dir, f"{date_str}.log")
        return log_file
    
    def log_policy_update(self, message: str) -> None:
        """Log policy update to daily log file"""
        log_file = self.get_policy_update_log_file()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")

def main():
    """Test the policy updater"""
    updater = PolicyUpdater()
    
    # Test trajectories
    test_trajectories = [
        {
            "trajectory_id": "test-1",
            "task": "Debug Python error",
            "task_type": "debug",
            "skill_name": "structured_debugging",
            "workflow_name": "structured_debug_v1",
            "tools_used": ["read", "edit", "exec"],
            "success": True,
            "final_score": 0.87
        },
        {
            "trajectory_id": "test-2",
            "task": "Fix JavaScript bug",
            "task_type": "debug",
            "skill_name": "structured_debugging",
            "workflow_name": "structured_debug_v1", 
            "tools_used": ["read", "edit", "exec"],
            "success": True,
            "final_score": 0.83
        },
        {
            "trajectory_id": "test-3",
            "task": "Resolve TypeScript error",
            "task_type": "debug",
            "skill_name": "structured_debugging",
            "workflow_name": "structured_debug_v1",
            "tools_used": ["read", "edit", "exec"],
            "success": True,
            "final_score": 0.9
        }
    ]
    
    # Update policy
    success = updater.update_policy_from_trajectories("debug", test_trajectories)
    
    if success:
        print("✅ Policy update completed successfully")
    else:
        print("⚠️ Policy update not performed (insufficient evidence)")

if __name__ == "__main__":
    main()