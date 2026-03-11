#!/usr/bin/env python3
"""
Coordination Critic for OpenClaw Skill Evolution v4
Evaluates the quality of multi-role collaboration patterns
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

class CoordinationCritic:
    """Evaluates coordination quality in multi-role workflows"""
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        self.workspace_path = workspace_path
        self.critic_log_dir = os.path.join(workspace_path, "logs", "critic")
        self.qdrant_client = QdrantClient(host="localhost", port=6333)
        
        # Ensure log directory exists
        os.makedirs(self.critic_log_dir, exist_ok=True)
    
    def get_current_date_str(self) -> str:
        """Get current date in YYYY-MM-DD format"""
        return datetime.now().strftime("%Y-%m-%d")
    
    def get_date_log_dir(self) -> str:
        """Get the log directory for current date"""
        date_str = self.get_current_date_str()
        date_log_dir = os.path.join(self.critic_log_dir, date_str)
        os.makedirs(date_log_dir, exist_ok=True)
        return date_log_dir
    
    def evaluate_role_assignment_quality(self, trajectory: Dict, role_sequence: List[str]) -> float:
        """
        Evaluate if the role assignment was appropriate for the task
        
        Scoring criteria:
        - Simple tasks should not use complex role sequences (+0.2 for simple tasks with 1 role)
        - Complex tasks should use multiple roles (+0.3 for complex tasks with 3+ roles)
        - Role sequence should match task complexity (-0.2 for mismatch)
        """
        task_type = trajectory.get("task_type", "unknown")
        task_complexity = self.assess_task_complexity(task_type, trajectory.get("task", ""))
        sequence_length = len(role_sequence)
        
        if task_complexity == "simple" and sequence_length == 1:
            return 0.2
        elif task_complexity == "complex" and sequence_length >= 3:
            return 0.3
        elif task_complexity == "medium" and sequence_length == 2:
            return 0.25
        else:
            return -0.2
    
    def assess_task_complexity(self, task_type: str, task_description: str) -> str:
        """Assess task complexity based on type and description"""
        complex_indicators = ["debug", "analyze", "research", "optimize", "refactor"]
        simple_indicators = ["read", "write", "list", "check", "get"]
        
        task_lower = task_description.lower()
        
        if any(indicator in task_lower for indicator in complex_indicators):
            return "complex"
        elif any(indicator in task_lower for indicator in simple_indicators):
            return "simple"
        else:
            return "medium"
    
    def evaluate_handoff_quality(self, trajectory: Dict, handoffs: List[Dict]) -> float:
        """
        Evaluate the quality of handoffs between roles
        
        Scoring criteria:
        - Smooth handoffs with clear input/output (+0.2 per good handoff)
        - Failed or unclear handoffs (-0.3 per bad handoff)
        - Excessive handoffs for simple tasks (-0.1 per extra handoff)
        """
        if not handoffs:
            return 0.0
        
        total_score = 0.0
        for handoff in handoffs:
            if handoff.get("success", False):
                total_score += 0.2
            else:
                total_score -= 0.3
        
        # Penalize excessive handoffs for simple tasks
        task_complexity = self.assess_task_complexity(
            trajectory.get("task_type", "unknown"), 
            trajectory.get("task", "")
        )
        if task_complexity == "simple" and len(handoffs) > 1:
            total_score -= 0.1 * (len(handoffs) - 1)
        
        return total_score / len(handoffs) if handoffs else 0.0
    
    def evaluate_collaboration_efficiency(self, trajectory: Dict, role_sequence: List[str], handoffs: List[Dict]) -> float:
        """
        Evaluate overall collaboration efficiency
        
        Scoring criteria:
        - Total execution time vs expected (+0.2 for fast, -0.2 for slow)
        - Number of roles vs task complexity (+0.1 for optimal, -0.1 for suboptimal)
        - Handoff overhead (-0.1 per handoff for simple tasks)
        """
        duration_ms = trajectory.get("duration_ms", 0)
        task_complexity = self.assess_task_complexity(
            trajectory.get("task_type", "unknown"), 
            trajectory.get("task", "")
        )
        
        # Expected duration based on complexity
        expected_duration = {
            "simple": 2000,
            "medium": 5000, 
            "complex": 10000
        }.get(task_complexity, 5000)
        
        time_score = 0.2 if duration_ms <= expected_duration else -0.2
        
        # Role count efficiency
        optimal_roles = {"simple": 1, "medium": 2, "complex": 3}.get(task_complexity, 2)
        role_count_score = 0.1 if len(role_sequence) == optimal_roles else -0.1
        
        # Handoff overhead penalty
        handoff_penalty = 0.0
        if task_complexity == "simple" and len(handoffs) > 0:
            handoff_penalty = -0.1 * len(handoffs)
        
        return time_score + role_count_score + handoff_penalty
    
    def evaluate_coordination_quality(
        self, 
        trajectory: Dict, 
        role_sequence: List[str], 
        handoffs: List[Dict]
    ) -> Dict[str, Any]:
        """
        Complete coordination quality evaluation
        
        Returns detailed assessment with scores and suggestions
        """
        logger.info(f"🔍 Evaluating coordination quality for trajectory: {trajectory.get('trajectory_id', 'unknown')}")
        
        # Evaluate different aspects
        role_assignment_score = self.evaluate_role_assignment_quality(trajectory, role_sequence)
        handoff_quality_score = self.evaluate_handoff_quality(trajectory, handoffs)
        collaboration_efficiency_score = self.evaluate_collaboration_efficiency(trajectory, role_sequence, handoffs)
        
        # Calculate final coordination reward
        final_coordination_reward = (
            role_assignment_score + 
            handoff_quality_score + 
            collaboration_efficiency_score
        )
        
        # Generate suggestions
        suggestions = []
        if role_assignment_score < 0:
            suggestions.append("Consider using fewer roles for simple tasks or more roles for complex tasks")
        if handoff_quality_score < 0:
            suggestions.append("Improve handoff clarity and structure between roles")
        if collaboration_efficiency_score < 0:
            suggestions.append("Optimize role sequence and reduce unnecessary handoffs")
        
        # Determine if collaboration pattern should be learned
        should_learn_collaboration = final_coordination_reward > 0.3
        
        result = {
            "role_assignment_score": role_assignment_score,
            "handoff_quality_score": handoff_quality_score,
            "collaboration_efficiency_score": collaboration_efficiency_score,
            "final_coordination_reward": final_coordination_reward,
            "suggestions": suggestions,
            "should_learn_collaboration": should_learn_collaboration,
            "evaluation_timestamp": datetime.now().isoformat()
        }
        
        # Save to log file
        self.save_critic_result(trajectory.get("trajectory_id", "unknown"), result)
        
        logger.info(f"✅ Coordination evaluation completed - Final reward: {final_coordination_reward:.2f}")
        return result
    
    def save_critic_result(self, trajectory_id: str, result: Dict) -> str:
        """Save critic result to local file"""
        date_log_dir = self.get_date_log_dir()
        critic_file = os.path.join(date_log_dir, f"{trajectory_id}.json")
        
        with open(critic_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Saved critic result to: {critic_file}")
        return critic_file
    
    def save_to_qdrant(self, trajectory_id: str, result: Dict) -> bool:
        """Save critic result to Qdrant"""
        try:
            # Create embedding content (for future semantic search)
            embedding_content = f"coordination_critic {trajectory_id}"
            placeholder_embedding = [0.1] * 1536
            
            point = PointStruct(
                id=f"critic_{trajectory_id}",
                vector=placeholder_embedding,
                payload={
                    "critic_id": f"critic_{trajectory_id}",
                    "trajectory_id": trajectory_id,
                    "role_assignment_score": result["role_assignment_score"],
                    "handoff_quality_score": result["handoff_quality_score"],
                    "collaboration_efficiency_score": result["collaboration_efficiency_score"],
                    "final_coordination_reward": result["final_coordination_reward"],
                    "should_learn_collaboration": result["should_learn_collaboration"],
                    "suggestions": result["suggestions"],
                    "evaluation_timestamp": result["evaluation_timestamp"]
                }
            )
            
            self.qdrant_client.upsert(
                collection_name="critic_results",
                points=[point]
            )
            
            logger.info(f"✅ Saved critic result to Qdrant: critic_{trajectory_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save critic result to Qdrant: {e}")
            return False

def main():
    """Test the coordination critic"""
    critic = CoordinationCritic()
    
    # Test trajectory
    test_trajectory = {
        "trajectory_id": "test-collab-123",
        "task": "Debug a complex distributed system issue",
        "task_type": "debugging",
        "steps": [
            {"step": 1, "role": "planner", "action": "analyze_system", "success": True},
            {"step": 2, "role": "executor", "action": "inspect_logs", "success": True},
            {"step": 3, "role": "critic", "action": "validate_fix", "success": True}
        ],
        "success": True,
        "final_score": 1.8,
        "duration_ms": 8000
    }
    
    test_role_sequence = ["planner", "executor", "critic"]
    test_handoffs = [
        {"from_role": "planner", "to_role": "executor", "success": True},
        {"from_role": "executor", "to_role": "critic", "success": True}
    ]
    
    # Evaluate coordination quality
    result = critic.evaluate_coordination_quality(test_trajectory, test_role_sequence, test_handoffs)
    
    print("Coordination Critic Test Results:")
    print(f"Role Assignment Score: {result['role_assignment_score']:.2f}")
    print(f"Handoff Quality Score: {result['handoff_quality_score']:.2f}")
    print(f"Collaboration Efficiency Score: {result['collaboration_efficiency_score']:.2f}")
    print(f"Final Coordination Reward: {result['final_coordination_reward']:.2f}")
    print(f"Should Learn Collaboration: {result['should_learn_collaboration']}")
    print("Suggestions:")
    for suggestion in result["suggestions"]:
        print(f"  - {suggestion}")

if __name__ == "__main__":
    main()