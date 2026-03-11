#!/usr/bin/env python3
"""
Trajectory Logger v2 for OpenClaw Skill Evolution
Records complete task execution trajectories with enhanced v2 fields
"""

import sys
import os
import json
import uuid
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
from qdrant_client.models import PointStruct

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrajectoryLoggerV2:
    """Records and manages task execution trajectories with v2 enhanced fields"""
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        self.workspace_path = workspace_path
        self.trajectories_log_dir = os.path.join(workspace_path, "logs", "trajectories")
        self.qdrant_client = QdrantClient(host="localhost", port=6333)
        
        # Ensure log directory exists
        os.makedirs(self.trajectories_log_dir, exist_ok=True)
    
    def create_trajectory_id(self) -> str:
        """Generate a unique trajectory ID"""
        return str(uuid.uuid4())
    
    def get_current_date_str(self) -> str:
        """Get current date in YYYY-MM-DD format"""
        return datetime.now().strftime("%Y-%m-%d")
    
    def get_date_log_dir(self) -> str:
        """Get the log directory for current date"""
        date_str = self.get_current_date_str()
        date_log_dir = os.path.join(self.trajectories_log_dir, date_str)
        os.makedirs(date_log_dir, exist_ok=True)
        return date_log_dir
    
    def create_trajectory(
        self,
        task: str,
        task_type: str,
        skill_id: Optional[str] = None,
        skill_name: Optional[str] = None,
        workflow_id: Optional[str] = None,
        workflow_name: Optional[str] = None,
        steps: Optional[List[Dict]] = None,
        tools_used: Optional[List[str]] = None,
        outputs_summary: str = "",
        success: bool = False,
        final_score: float = 0.0,
        duration_ms: int = 0,
        reflection_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a trajectory record with v2 enhanced fields"""
        trajectory_id = self.create_trajectory_id()
        created_at = datetime.now().isoformat()
        
        trajectory = {
            "trajectory_id": trajectory_id,
            "task": task,
            "task_type": task_type,
            "skill_id": skill_id,
            "skill_name": skill_name,
            "workflow_id": workflow_id,
            "workflow_name": workflow_name,
            "steps": steps or [],
            "tools_used": tools_used or [],
            "outputs_summary": outputs_summary,
            "success": success,
            "final_score": final_score,
            "duration_ms": duration_ms,
            "reflection_id": reflection_id,
            "created_at": created_at
        }
        
        return trajectory
    
    def validate_step(self, step: Dict) -> bool:
        """Validate that a step has required fields"""
        required_fields = ["step", "action", "tool", "input_summary", "output_summary", "success", "score", "duration_ms"]
        return all(field in step for field in required_fields)
    
    def add_step_to_trajectory(self, trajectory: Dict, step: Dict) -> None:
        """Add a validated step to trajectory"""
        if not self.validate_step(step):
            raise ValueError(f"Invalid step format. Required fields: step, action, tool, input_summary, output_summary, success, score, duration_ms")
        
        trajectory["steps"].append(step)
        # Update tools_used if not already present
        if step["tool"] not in trajectory["tools_used"]:
            trajectory["tools_used"].append(step["tool"])
    
    def save_trajectory_to_file(self, trajectory: Dict) -> str:
        """Save trajectory to local file"""
        date_log_dir = self.get_date_log_dir()
        trajectory_file = os.path.join(date_log_dir, f"{trajectory['trajectory_id']}.json")
        
        with open(trajectory_file, 'w', encoding='utf-8') as f:
            json.dump(trajectory, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Saved trajectory to file: {trajectory_file}")
        return trajectory_file
    
    def save_trajectory_to_qdrant(self, trajectory: Dict) -> bool:
        """Save trajectory to Qdrant vector database"""
        try:
            # Create embedding content (task + task_type + outputs_summary)
            embedding_content = f"{trajectory['task']} {trajectory['task_type']} {trajectory['outputs_summary']}"
            
            # For now, we'll use a placeholder embedding
            # In production, this would be generated by an embedding model
            placeholder_embedding = [0.1] * 1536  # 1536-dimensional placeholder
            
            # Create point for Qdrant
            point = PointStruct(
                id=trajectory["trajectory_id"],
                vector=placeholder_embedding,
                payload={
                    "trajectory_id": trajectory["trajectory_id"],
                    "task": trajectory["task"],
                    "task_type": trajectory["task_type"],
                    "skill_id": trajectory["skill_id"],
                    "skill_name": trajectory["skill_name"],
                    "workflow_id": trajectory["workflow_id"],
                    "workflow_name": trajectory["workflow_name"],
                    "steps": str(trajectory["steps"]),  # Convert to string for storage
                    "tools_used": trajectory["tools_used"],
                    "outputs_summary": trajectory["outputs_summary"],
                    "success": trajectory["success"],
                    "final_score": trajectory["final_score"],
                    "duration_ms": trajectory["duration_ms"],
                    "reflection_id": trajectory["reflection_id"],
                    "created_at": trajectory["created_at"]
                }
            )
            
            # Upsert to Qdrant
            self.qdrant_client.upsert(
                collection_name="trajectories",
                points=[point]
            )
            
            logger.info(f"✅ Saved trajectory to Qdrant: {trajectory['trajectory_id']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save trajectory to Qdrant: {e}")
            return False
    
    def log_trajectory(
        self,
        task: str,
        task_type: str,
        skill_id: Optional[str] = None,
        skill_name: Optional[str] = None,
        workflow_id: Optional[str] = None,
        workflow_name: Optional[str] = None,
        steps: Optional[List[Dict]] = None,
        tools_used: Optional[List[str]] = None,
        outputs_summary: str = "",
        success: bool = False,
        final_score: float = 0.0,
        duration_ms: int = 0,
        reflection_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Complete trajectory logging workflow with v2 enhanced fields"""
        logger.info(f"📝 Logging trajectory for task: {task}")
        
        # Create trajectory
        trajectory = self.create_trajectory(
            task=task,
            task_type=task_type,
            skill_id=skill_id,
            skill_name=skill_name,
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            steps=steps,
            tools_used=tools_used,
            outputs_summary=outputs_summary,
            success=success,
            final_score=final_score,
            duration_ms=duration_ms,
            reflection_id=reflection_id
        )
        
        # Save to file
        self.save_trajectory_to_file(trajectory)
        
        # Save to Qdrant
        self.save_trajectory_to_qdrant(trajectory)
        
        logger.info(f"🎯 Trajectory logged successfully: {trajectory['trajectory_id']}")
        return trajectory

def main():
    """Test the trajectory logger v2"""
    logger = TrajectoryLoggerV2()
    
    # Test trajectory with v2 enhanced fields
    test_trajectory = logger.log_trajectory(
        task="Debug a failing API endpoint",
        task_type="debug",
        skill_id="structured_problem_solving_v1",
        skill_name="structured_problem_solving",
        workflow_id="structured_debug_v1",
        workflow_name="structured_debug_v1",
        steps=[
            {
                "step": 1,
                "action": "analyze_logs",
                "tool": "read",
                "input_summary": "path: /var/log/api/error.log",
                "output_summary": "Found 500 error with stack trace",
                "success": True,
                "score": 0.9,
                "duration_ms": 500
            },
            {
                "step": 2,
                "action": "inspect_code",
                "tool": "read",
                "input_summary": "path: src/api/handler.js",
                "output_summary": "Identified null pointer exception in line 45",
                "success": True,
                "score": 0.8,
                "duration_ms": 800
            },
            {
                "step": 3,
                "action": "fix_code",
                "tool": "edit",
                "input_summary": "path: src/api/handler.js, add null check",
                "output_summary": "Added null check before accessing property",
                "success": True,
                "score": 0.9,
                "duration_ms": 1200
            }
        ],
        tools_used=["read", "edit"],
        outputs_summary="Successfully debugged and fixed the API endpoint",
        success=True,
        final_score=1.12,
        duration_ms=2500
    )
    
    print(f"Test trajectory created: {test_trajectory['trajectory_id']}")
    print(f"Task type: {test_trajectory['task_type']}")
    print(f"Skill: {test_trajectory['skill_name']}")
    print(f"Workflow: {test_trajectory['workflow_name']}")
    print(f"Final score: {test_trajectory['final_score']}")

if __name__ == "__main__":
    main()