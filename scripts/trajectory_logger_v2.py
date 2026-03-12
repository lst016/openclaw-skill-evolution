#!/usr/bin/env python3
"""
Trajectory Logger v2 for OpenClaw Skill Evolution
Records complete task execution trajectories with enhanced metadata and real embeddings
"""

import sys
import os
import json
import uuid
from datetime import datetime
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
# Import local embedding service
from .embedding_service import EmbeddingService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrajectoryLoggerV2:
    """Records and manages task execution trajectories with enhanced metadata"""
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        self.workspace_path = workspace_path
        self.trajectories_log_dir = os.path.join(workspace_path, "logs", "trajectories")
        self.qdrant_client = QdrantClient(host="localhost", port=6333)
        # Initialize embedding service
        self.embedding_service = EmbeddingService()
        
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
        """Create a trajectory record with enhanced metadata"""
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
        """Save trajectory to Qdrant vector database with real embeddings"""
        try:
            # Create embedding content (task + task_type + outputs_summary)
            embedding_content = f"{trajectory['task']} {trajectory['task_type']} {trajectory['outputs_summary']}"
            
            # Generate real embedding using local BGE model
            embedding = self.embedding_service.generate_embedding(embedding_content)
            
            # Create point for Qdrant
            point = PointStruct(
                id=trajectory["trajectory_id"],
                vector=embedding,
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
        """Complete trajectory logging workflow with real embeddings"""
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
        
        # Save to Qdrant with real embeddings
        self.save_trajectory_to_qdrant(trajectory)
        
        logger.info(f"🎯 Trajectory logged successfully: {trajectory['trajectory_id']}")
        return trajectory

def main():
    """Test the trajectory logger v2 with real embeddings"""
    logger = TrajectoryLoggerV2()
    
    # Test trajectory
    test_trajectory = logger.log_trajectory(
        task="搜索关于 OpenClaw 技能进化的中文信息",
        task_type="web_search",
        skill_id="agent-reach-001",
        skill_name="agent-reach",
        workflow_id="search-workflow-v1",
        workflow_name="search_workflow_v1",
        steps=[
            {
                "step": 1,
                "action": "search_web",
                "tool": "web_search",
                "input_summary": "query: OpenClaw 技能进化 中文",
                "output_summary": "找到 5 个相关结果关于技能进化",
                "success": True,
                "score": 0.8,
                "duration_ms": 1200
            },
            {
                "step": 2,
                "action": "fetch_content",
                "tool": "web_fetch",
                "input_summary": "url: https://example.com/openclaw-skill-evolution",
                "output_summary": "提取了关于技能进化框架的中文内容",
                "success": True,
                "score": 0.9,
                "duration_ms": 800
            }
        ],
        tools_used=["web_search", "web_fetch"],
        outputs_summary="成功找到并提取了关于 OpenClaw 技能进化的中文信息",
        success=True,
        final_score=0.85,
        duration_ms=2000
    )
    
    print(f"Test trajectory created: {test_trajectory['trajectory_id']}")

if __name__ == "__main__":
    main()