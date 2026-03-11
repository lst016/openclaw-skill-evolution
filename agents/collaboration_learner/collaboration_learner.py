#!/usr/bin/env python3
"""
Collaboration Policy Learner for OpenClaw Skill Evolution v4
Learns optimal role collaboration patterns from execution trajectories
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

class CollaborationPolicyLearner:
    """Learns and manages collaboration policies for multi-role workflows"""
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        self.workspace_path = workspace_path
        self.policies_dir = os.path.join(workspace_path, "policies")
        self.qdrant_client = QdrantClient(host="localhost", port=6333)
        
        # Ensure policies directory exists
        os.makedirs(self.policies_dir, exist_ok=True)
        
        # Load existing policies
        self.role_policy = self.load_policy("role_policy.json")
        self.handoff_policy = self.load_policy("handoff_policy.json") 
        self.collaboration_policy = self.load_policy("collaboration_policy.json")
    
    def load_policy(self, policy_file: str) -> Dict[str, Any]:
        """Load policy from JSON file"""
        policy_path = os.path.join(self.policies_dir, policy_file)
        if os.path.exists(policy_path):
            with open(policy_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {}
    
    def save_policy(self, policy: Dict[str, Any], policy_file: str) -> None:
        """Save policy to JSON file"""
        policy_path = os.path.join(self.policies_dir, policy_file)
        with open(policy_path, 'w', encoding='utf-8') as f:
            json.dump(policy, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Saved {policy_file}: {policy_path}")
    
    def analyze_collaboration_patterns(self, trajectories: List[Dict]) -> Dict[str, Any]:
        """Analyze trajectories to extract collaboration patterns"""
        collaboration_patterns = {}
        
        for trajectory in trajectories:
            task_type = trajectory.get("task_type", "unknown")
            role_sequence = trajectory.get("role_sequence", [])
            
            if not role_sequence:
                continue
            
            # Create pattern key
            pattern_key = f"{task_type}_{'_'.join(role_sequence)}"
            
            if pattern_key not in collaboration_patterns:
                collaboration_patterns[pattern_key] = {
                    "task_type": task_type,
                    "role_sequence": role_sequence,
                    "success_count": 0,
                    "total_count": 0,
                    "avg_score": 0.0,
                    "total_score": 0.0
                }
            
            # Update statistics
            pattern = collaboration_patterns[pattern_key]
            pattern["total_count"] += 1
            if trajectory.get("success", False):
                pattern["success_count"] += 1
            pattern["total_score"] += trajectory.get("final_score", 0.0)
            pattern["avg_score"] = pattern["total_score"] / pattern["total_count"]
        
        return collaboration_patterns
    
    def evaluate_pattern_quality(self, pattern: Dict[str, Any]) -> float:
        """Evaluate the quality of a collaboration pattern"""
        success_rate = pattern["success_count"] / pattern["total_count"] if pattern["total_count"] > 0 else 0.0
        avg_score = pattern["avg_score"]
        
        # Weighted score: 60% success rate + 40% average score
        quality_score = (success_rate * 0.6) + (avg_score * 0.4)
        return quality_score
    
    def generate_collaboration_policy(self, collaboration_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Generate collaboration policy from patterns"""
        collaboration_policy = {}
        
        # Group patterns by task_type
        task_patterns = {}
        for pattern_key, pattern in collaboration_patterns.items():
            task_type = pattern["task_type"]
            if task_type not in task_patterns:
                task_patterns[task_type] = []
            task_patterns[task_type].append(pattern)
        
        # Select best pattern for each task type
        for task_type, patterns in task_patterns.items():
            if not patterns:
                continue
            
            # Sort by quality score
            patterns.sort(key=self.evaluate_pattern_quality, reverse=True)
            best_pattern = patterns[0]
            
            collaboration_policy[task_type] = {
                "role_sequence": best_pattern["role_sequence"],
                "success_rate": best_pattern["success_count"] / best_pattern["total_count"],
                "avg_score": best_pattern["avg_score"],
                "usage_count": best_pattern["total_count"],
                "confidence": self.evaluate_pattern_quality(best_pattern),
                "version": 1,
                "status": "candidate"
            }
        
        return collaboration_policy
    
    def update_role_policy(self, collaboration_policy: Dict[str, Any]) -> None:
        """Update role policy based on collaboration policy"""
        for task_type, policy in collaboration_policy.items():
            self.role_policy[task_type] = {
                "role_sequence": policy["role_sequence"],
                "confidence": policy["confidence"]
            }
    
    def update_handoff_policy(self, trajectories: List[Dict]) -> None:
        """Update handoff policy based on trajectory analysis"""
        handoff_stats = {}
        
        for trajectory in trajectories:
            handoffs = trajectory.get("handoffs", [])
            for handoff in handoffs:
                from_role = handoff.get("from_role")
                to_role = handoff.get("to_role")
                if not from_role or not to_role:
                    continue
                
                handoff_key = f"{from_role}_{to_role}"
                if handoff_key not in handoff_stats:
                    handoff_stats[handoff_key] = {
                        "success_count": 0,
                        "total_count": 0,
                        "avg_quality": 0.0,
                        "total_quality": 0.0
                    }
                
                stats = handoff_stats[handoff_key]
                stats["total_count"] += 1
                if handoff.get("success", False):
                    stats["success_count"] += 1
                stats["total_quality"] += handoff.get("quality_score", 0.0)
                stats["avg_quality"] = stats["total_quality"] / stats["total_count"]
        
        # Update handoff policy
        for handoff_key, stats in handoff_stats.items():
            from_role, to_role = handoff_key.split("_")
            if from_role not in self.handoff_policy:
                self.handoff_policy[from_role] = {}
            
            success_rate = stats["success_count"] / stats["total_count"]
            self.handoff_policy[from_role][to_role] = {
                "success_rate": success_rate,
                "avg_quality": stats["avg_quality"],
                "usage_count": stats["total_count"]
            }
    
    def learn_from_trajectories(self, trajectories: List[Dict]) -> bool:
        """Learn collaboration policies from trajectories"""
        logger.info(f"🧠 Learning from {len(trajectories)} trajectories")
        
        # Analyze collaboration patterns
        collaboration_patterns = self.analyze_collaboration_patterns(trajectories)
        if not collaboration_patterns:
            logger.info("⚠️ No collaboration patterns found")
            return False
        
        # Generate collaboration policy
        new_collaboration_policy = self.generate_collaboration_policy(collaboration_patterns)
        if not new_collaboration_policy:
            logger.info("⚠️ No valid collaboration policy generated")
            return False
        
        # Update policies
        self.update_role_policy(new_collaboration_policy)
        self.update_handoff_policy(trajectories)
        self.collaboration_policy = new_collaboration_policy
        
        # Save policies
        self.save_policy(self.role_policy, "role_policy.json")
        self.save_policy(self.handoff_policy, "handoff_policy.json")
        self.save_policy(self.collaboration_policy, "collaboration_policy.json")
        
        # Save to Qdrant
        self.save_collaborations_to_qdrant(new_collaboration_policy)
        
        logger.info(f"✅ Learned collaboration policies for {len(new_collaboration_policy)} task types")
        return True
    
    def save_collaborations_to_qdrant(self, collaboration_policy: Dict[str, Any]) -> None:
        """Save collaboration policies to Qdrant"""
        try:
            for task_type, policy in collaboration_policy.items():
                # Create embedding content
                embedding_content = f"{task_type} {' '.join(policy['role_sequence'])}"
                placeholder_embedding = [0.1] * 1536
                
                # Create point for Qdrant
                point = PointStruct(
                    id=f"collab_{task_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    vector=placeholder_embedding,
                    payload={
                        "collaboration_id": f"collab_{task_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        "task_type": task_type,
                        "role_sequence": policy["role_sequence"],
                        "handoff_points": [],  # Can be populated from detailed analysis
                        "success_rate": policy["success_rate"],
                        "avg_score": policy["avg_score"],
                        "usage_count": policy["usage_count"],
                        "version": policy["version"],
                        "status": policy["status"],
                        "created_at": datetime.now().isoformat()
                    }
                )
                
                # Upsert to Qdrant
                self.qdrant_client.upsert(
                    collection_name="collaborations",
                    points=[point]
                )
            
            logger.info(f"✅ Saved {len(collaboration_policy)} collaboration policies to Qdrant")
            
        except Exception as e:
            logger.error(f"❌ Failed to save collaborations to Qdrant: {e}")
    
    def get_best_collaboration_for_task(self, task_type: str) -> Optional[Dict[str, Any]]:
        """Get the best collaboration pattern for a task type"""
        return self.collaboration_policy.get(task_type)

def main():
    """Test the collaboration policy learner"""
    learner = CollaborationPolicyLearner()
    
    # Test trajectories with role sequences
    test_trajectories = [
        {
            "trajectory_id": "test-1",
            "task": "Debug complex production issue",
            "task_type": "debugging",
            "role_sequence": ["planner", "executor", "critic"],
            "handoffs": [
                {"from_role": "planner", "to_role": "executor", "success": True, "quality_score": 0.9},
                {"from_role": "executor", "to_role": "critic", "success": True, "quality_score": 0.8}
            ],
            "success": True,
            "final_score": 0.87
        },
        {
            "trajectory_id": "test-2",
            "task": "Implement new feature",
            "task_type": "development",
            "role_sequence": ["planner", "executor", "critic"],
            "handoffs": [
                {"from_role": "planner", "to_role": "executor", "success": True, "quality_score": 0.8},
                {"from_role": "executor", "to_role": "critic", "success": True, "quality_score": 0.9}
            ],
            "success": True,
            "final_score": 0.83
        },
        {
            "trajectory_id": "test-3",
            "task": "Simple code fix",
            "task_type": "debugging",
            "role_sequence": ["executor"],
            "handoffs": [],
            "success": True,
            "final_score": 0.9
        }
    ]
    
    # Learn from trajectories
    success = learner.learn_from_trajectories(test_trajectories)
    
    if success:
        print("✅ Collaboration policy learning completed successfully")
        print(f"Role policy: {json.dumps(learner.role_policy, indent=2)}")
        print(f"Collaboration policy: {json.dumps(learner.collaboration_policy, indent=2)}")
    else:
        print("❌ Collaboration policy learning failed")

if __name__ == "__main__":
    main()