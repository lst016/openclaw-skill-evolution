#!/usr/bin/env python3
"""
Experience Manager for OpenClaw Skill Evolution v2+
Manages high-value experience storage with deduplication
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# Add the virtual environment to Python path
venv_path = os.path.join(os.path.dirname(__file__), '..', '.venv')
if os.path.exists(venv_path):
    site_packages = os.path.join(venv_path, 'lib', 'python3.14', 'site-packages')
    if os.path.exists(site_packages):
        sys.path.insert(0, site_packages)

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from .embedding_service import EmbeddingService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExperienceManager:
    """Manages experience storage, deduplication, and retrieval"""
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        self.workspace_path = workspace_path
        self.experiences_log_dir = os.path.join(workspace_path, "logs", "experiences")
        self.qdrant_client = QdrantClient(host="localhost", port=6333)
        self.embedding_service = EmbeddingService()
        
        # Ensure log directory exists
        os.makedirs(self.experiences_log_dir, exist_ok=True)
        
        # Lowered threshold for Chinese tasks
        self.quality_threshold = 0.7  # Reduced from 0.8
    
    def should_store_experience(self, trajectory: Dict) -> bool:
        """Determine if a trajectory should be stored as experience"""
        # Check if reflection indicates it should store experience
        if not trajectory.get("reflection_id"):
            return False
            
        # Check final score against lowered threshold
        if trajectory.get("final_score", 0) < self.quality_threshold:
            logger.info(f"Trajectory score {trajectory.get('final_score', 0)} < threshold {self.quality_threshold}, skipping storage")
            return False
            
        # Check if task was successful
        if not trajectory.get("success", False):
            return False
            
        return True
    
    def create_experience_from_trajectory(self, trajectory: Dict) -> Dict:
        """Create an experience from a high-quality trajectory"""
        experience_id = f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{trajectory['trajectory_id'][:8]}"
        created_at = datetime.now().isoformat()
        
        # Extract key information from trajectory
        task = trajectory.get("task", "")
        task_type = trajectory.get("task_type", "")
        outputs_summary = trajectory.get("outputs_summary", "")
        steps_summary = " ".join([str(step.get("output_summary", "")) for step in trajectory.get("steps", [])])
        
        # Create experience summary
        title = f"{task_type} - {task[:50]}..." if len(task) > 50 else f"{task_type} - {task}"
        problem_summary = f"Task: {task}. Type: {task_type}."
        solution_summary = f"Solution: {outputs_summary}. Steps: {steps_summary[:200]}..."
        
        experience = {
            "experience_id": experience_id,
            "title": title,
            "problem_summary": problem_summary,
            "solution_summary": solution_summary,
            "workflow": str(trajectory.get("steps", [])),
            "score": trajectory.get("final_score", 0),
            "success_count": 1,
            "fail_count": 0,
            "last_used_at": created_at,
            "source_trajectory_id": trajectory["trajectory_id"],
            "tags": [task_type],
            "status": "active",
            "created_at": created_at,
            "updated_at": created_at
        }
        
        return experience
    
    def generate_embedding(self, experience: Dict) -> List[float]:
        """Generate embedding for experience"""
        # Combine title, problem, and solution for embedding
        text_to_embed = f"{experience['title']} {experience['problem_summary']} {experience['solution_summary']} {' '.join(experience['tags'])}"
        embedding = self.embedding_service.embed(text_to_embed)
        return embedding
    
    def find_similar_experiences(self, experience: Dict, similarity_threshold: float = 0.85) -> List[Dict]:
        """Find similar experiences using Qdrant vector search"""
        try:
            embedding = self.generate_embedding(experience)
            
            # Search for similar experiences
            search_results = self.qdrant_client.query_points(
                collection_name="experiences",
                query=embedding,
                limit=5,
                score_threshold=similarity_threshold
            )
            
            similar_experiences = []
            for point in search_results.points:
                similar_experiences.append(point.payload)
            
            return similar_experiences
            
        except Exception as e:
            logger.error(f"Failed to find similar experiences: {e}")
            return []
    
    def merge_experiences(self, existing_exp: Dict, new_exp: Dict) -> Dict:
        """Merge two similar experiences"""
        merged_exp = existing_exp.copy()
        merged_exp["success_count"] += new_exp["success_count"]
        merged_exp["score"] = (existing_exp["score"] + new_exp["score"]) / 2
        merged_exp["solution_summary"] = new_exp["solution_summary"]  # Use latest solution
        merged_exp["workflow"] = new_exp["workflow"]  # Use latest workflow
        merged_exp["last_used_at"] = new_exp["created_at"]
        merged_exp["updated_at"] = datetime.now().isoformat()
        return merged_exp
    
    def save_experience_to_file(self, experience: Dict) -> str:
        """Save experience to local file"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        date_log_dir = os.path.join(self.experiences_log_dir, date_str)
        os.makedirs(date_log_dir, exist_ok=True)
        
        experience_file = os.path.join(date_log_dir, f"{experience['experience_id']}.json")
        
        with open(experience_file, 'w', encoding='utf-8') as f:
            json.dump(experience, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Saved experience to file: {experience_file}")
        return experience_file
    
    def save_experience_to_qdrant(self, experience: Dict) -> bool:
        """Save experience to Qdrant vector database"""
        try:
            embedding = self.generate_embedding(experience)
            
            point = PointStruct(
                id=experience["experience_id"],
                vector=embedding,
                payload={
                    "experience_id": experience["experience_id"],
                    "title": experience["title"],
                    "problem_summary": experience["problem_summary"],
                    "solution_summary": experience["solution_summary"],
                    "workflow": experience["workflow"],
                    "score": experience["score"],
                    "success_count": experience["success_count"],
                    "fail_count": experience["fail_count"],
                    "last_used_at": experience["last_used_at"],
                    "source_trajectory_id": experience["source_trajectory_id"],
                    "tags": experience["tags"],
                    "status": experience["status"],
                    "created_at": experience["created_at"],
                    "updated_at": experience["updated_at"]
                }
            )
            
            self.qdrant_client.upsert(
                collection_name="experiences",
                points=[point]
            )
            
            logger.info(f"✅ Saved experience to Qdrant: {experience['experience_id']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save experience to Qdrant: {e}")
            return False
    
    def store_experience(self, trajectory: Dict) -> Optional[Dict]:
        """Complete experience storage workflow with deduplication"""
        logger.info(f"📝 Processing trajectory for experience storage: {trajectory['trajectory_id']}")
        
        # Check if should store experience
        if not self.should_store_experience(trajectory):
            logger.info("❌ Skipping experience storage due to quality threshold")
            return None
        
        # Create experience
        experience = self.create_experience_from_trajectory(trajectory)
        logger.info(f"✨ Created experience: {experience['experience_id']}")
        
        # Find similar experiences (with lowered similarity threshold for Chinese)
        similar_exps = self.find_similar_experiences(experience, similarity_threshold=0.80)
        
        if similar_exps:
            # Merge with existing experience
            existing_exp = similar_exps[0]
            merged_exp = self.merge_experiences(existing_exp, experience)
            
            # Update both file and Qdrant
            self.save_experience_to_file(merged_exp)
            self.save_experience_to_qdrant(merged_exp)
            
            logger.info(f"🔄 Merged experience with existing: {existing_exp['experience_id']}")
            return merged_exp
        else:
            # Save new experience
            self.save_experience_to_file(experience)
            self.save_experience_to_qdrant(experience)
            
            logger.info(f"🆕 Stored new experience: {experience['experience_id']}")
            return experience

def main():
    """Test the experience manager"""
    logger = ExperienceManager()
    
    # Test trajectory
    test_trajectory = {
        "trajectory_id": "test_traj_001",
        "task": "优化数据库查询性能",
        "task_type": "performance_optimization",
        "steps": [
            {
                "step": 1,
                "action": "analyze_query",
                "tool": "sql_analyzer",
                "input_summary": "分析慢查询SQL",
                "output_summary": "发现缺少索引",
                "success": True,
                "score": 0.9,
                "duration_ms": 1200
            },
            {
                "step": 2,
                "action": "optimize_index",
                "tool": "database_optimizer", 
                "input_summary": "添加缺失的索引",
                "output_summary": "查询性能提升80%",
                "success": True,
                "score": 0.95,
                "duration_ms": 800
            }
        ],
        "outputs_summary": "成功优化数据库查询性能，响应时间减少80%",
        "success": True,
        "final_score": 1.85,  # High score to pass threshold
        "reflection_id": "test_reflection_001",
        "created_at": datetime.now().isoformat()
    }
    
    result = logger.store_experience(test_trajectory)
    if result:
        print(f"Test experience created: {result['experience_id']}")
    else:
        print("Test experience not created (below threshold)")

if __name__ == "__main__":
    main()