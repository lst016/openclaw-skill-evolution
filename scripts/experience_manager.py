#!/usr/bin/env python3
"""
Experience Manager for OpenClaw Skill Evolution
Handles experience deduplication, merging, and storage
"""

import sys
import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging

# Add the virtual environment to Python path
venv_path = os.path.join(os.path.dirname(__file__), '..', '.venv')
if os.path.exists(venv_path):
    site_packages = os.path.join(venv_path, 'lib', 'python3.14', 'site-packages')
    if os.path.exists(site_packages):
        sys.path.insert(0, site_packages)

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, SearchRequest, Filter, FieldCondition, Range

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExperienceManager:
    """Manages experience deduplication, merging, and storage"""
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        self.workspace_path = workspace_path
        self.experiences_log_dir = os.path.join(workspace_path, "logs", "experiences")
        self.qdrant_client = QdrantClient(host="localhost", port=6333)
        
        # Load thresholds from config
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "thresholds.json")
        with open(config_path, 'r') as f:
            self.thresholds = json.load(f)
        
        # Ensure log directory exists
        os.makedirs(self.experiences_log_dir, exist_ok=True)
    
    def create_experience_id(self) -> str:
        """Generate a unique experience ID"""
        return str(uuid.uuid4())
    
    def get_current_date_str(self) -> str:
        """Get current date in YYYY-MM-DD format"""
        return datetime.now().strftime("%Y-%m-%d")
    
    def get_date_log_dir(self) -> str:
        """Get the log directory for current date"""
        date_str = self.get_current_date_str()
        date_log_dir = os.path.join(self.experiences_log_dir, date_str)
        os.makedirs(date_log_dir, exist_ok=True)
        return date_log_dir
    
    def should_store_experience(self, trajectory: Dict, reflection: Dict) -> bool:
        """Check if experience should be stored based on criteria"""
        min_score = self.thresholds["experience"]["min_final_score"]
        similarity_threshold = self.thresholds["experience"]["similarity_threshold"]
        
        # Check trajectory score
        if trajectory.get("final_score", 0) < min_score:
            logger.info(f"❌ Trajectory score {trajectory.get('final_score', 0)} below threshold {min_score}")
            return False
        
        # Check reflection decision
        if not reflection.get("should_store_experience", False):
            logger.info("❌ Reflection indicates not to store experience")
            return False
        
        # Check if workflow is clear and reusable
        if not trajectory.get("steps") or len(trajectory.get("steps", [])) == 0:
            logger.info("❌ No steps in trajectory, not storing experience")
            return False
        
        return True
    
    def create_experience_from_trajectory(self, trajectory: Dict, reflection: Dict) -> Dict:
        """Create experience from trajectory and reflection"""
        experience_id = self.create_experience_id()
        created_at = datetime.now().isoformat()
        
        # Extract key information
        title = f"Experience: {trajectory['task_type']} - {trajectory['task'][:50]}"
        problem_summary = f"Task: {trajectory['task']}"
        solution_summary = trajectory.get("outputs_summary", "")
        workflow = str(trajectory.get("steps", []))
        score = trajectory.get("final_score", 0)
        source_trajectory_id = trajectory.get("trajectory_id", "")
        tags = [trajectory.get("task_type", "general")]
        
        experience = {
            "experience_id": experience_id,
            "title": title,
            "problem_summary": problem_summary,
            "solution_summary": solution_summary,
            "workflow": workflow,
            "score": score,
            "success_count": 1,
            "fail_count": 0 if trajectory.get("success", False) else 1,
            "last_used_at": created_at,
            "source_trajectory_id": source_trajectory_id,
            "tags": tags,
            "status": "active",
            "created_at": created_at,
            "updated_at": created_at
        }
        
        return experience
    
    def search_similar_experiences(self, experience: Dict, similarity_threshold: float = 0.88) -> List[Dict]:
        """Search for similar experiences in Qdrant"""
        try:
            # Create embedding content (title + problem_summary + solution_summary + tags)
            embedding_content = f"{experience['title']} {experience['problem_summary']} {experience['solution_summary']} {' '.join(experience['tags'])}"
            
            # For now, use placeholder embedding
            placeholder_embedding = [0.1] * 1536
            
            # Search in Qdrant
            search_result = self.qdrant_client.query_points(
                collection_name="experiences",
                query=placeholder_embedding,
                limit=5,
                score_threshold=similarity_threshold
            )
            
            similar_experiences = []
            for hit in search_result.points:
                similar_experiences.append(hit.payload)
            
            logger.info(f"🔍 Found {len(similar_experiences)} similar experiences")
            return similar_experiences
            
        except Exception as e:
            logger.error(f"❌ Failed to search similar experiences: {e}")
            return []
    
    def merge_experiences(self, existing_experience: Dict, new_experience: Dict) -> Dict:
        """Merge two similar experiences"""
        merged = existing_experience.copy()
        
        # Update counts
        merged["success_count"] += new_experience["success_count"]
        merged["fail_count"] += new_experience["fail_count"]
        
        # Update score (weighted average)
        total_count = merged["success_count"] + merged["fail_count"]
        if total_count > 0:
            merged["score"] = (merged["score"] * (total_count - 1) + new_experience["score"]) / total_count
        
        # Update solution summary (keep the better one)
        if new_experience["score"] > merged["score"]:
            merged["solution_summary"] = new_experience["solution_summary"]
            merged["workflow"] = new_experience["workflow"]
        
        # Update last used timestamp
        merged["last_used_at"] = datetime.now().isoformat()
        merged["updated_at"] = datetime.now().isoformat()
        
        logger.info(f"🔄 Merged experience {existing_experience['experience_id']} with new experience")
        return merged
    
    def save_experience_to_file(self, experience: Dict) -> str:
        """Save experience to local file"""
        date_log_dir = self.get_date_log_dir()
        experience_file = os.path.join(date_log_dir, f"{experience['experience_id']}.json")
        
        with open(experience_file, 'w', encoding='utf-8') as f:
            json.dump(experience, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Saved experience to file: {experience_file}")
        return experience_file
    
    def save_experience_to_qdrant(self, experience: Dict) -> bool:
        """Save experience to Qdrant vector database"""
        try:
            # Create embedding content
            embedding_content = f"{experience['title']} {experience['problem_summary']} {experience['solution_summary']} {' '.join(experience['tags'])}"
            
            # For now, use placeholder embedding
            placeholder_embedding = [0.1] * 1536
            
            # Create point for Qdrant
            point = PointStruct(
                id=experience["experience_id"],
                vector=placeholder_embedding,
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
            
            # Upsert to Qdrant
            self.qdrant_client.upsert(
                collection_name="experiences",
                points=[point]
            )
            
            logger.info(f"✅ Saved experience to Qdrant: {experience['experience_id']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save experience to Qdrant: {e}")
            return False
    
    def store_experience(self, trajectory: Dict, reflection: Dict) -> Optional[Dict]:
        """Complete experience storage workflow with deduplication"""
        logger.info("📝 Processing experience storage")
        
        # Check if experience should be stored
        if not self.should_store_experience(trajectory, reflection):
            logger.info("❌ Experience does not meet storage criteria")
            return None
        
        # Create experience
        experience = self.create_experience_from_trajectory(trajectory, reflection)
        logger.info(f"✨ Created experience: {experience['experience_id']}")
        
        # Search for similar experiences
        similarity_threshold = self.thresholds["experience"]["similarity_threshold"]
        similar_experiences = self.search_similar_experiences(experience, similarity_threshold)
        
        if similar_experiences:
            # Merge with existing experience
            existing_experience = similar_experiences[0]  # Take the most similar
            merged_experience = self.merge_experiences(existing_experience, experience)
            
            # Save merged experience
            self.save_experience_to_file(merged_experience)
            self.save_experience_to_qdrant(merged_experience)
            
            logger.info(f"🎯 Merged and stored experience: {merged_experience['experience_id']}")
            return merged_experience
        else:
            # Store new experience
            self.save_experience_to_file(experience)
            self.save_experience_to_qdrant(experience)
            
            logger.info(f"🎯 Stored new experience: {experience['experience_id']}")
            return experience

def main():
    """Test the experience manager"""
    # Load test trajectory and reflection
    trajectory = {
        "trajectory_id": "test-123",
        "task": "Search for information about OpenClaw Skill Evolution",
        "task_type": "web_search",
        "selected_skill": "agent-reach",
        "selected_workflow": "search_workflow_v1",
        "steps": [
            {
                "step": 1,
                "action": "search_web",
                "tool": "web_search",
                "input_summary": "query: OpenClaw Skill Evolution",
                "output_summary": "Found 5 relevant results about skill evolution",
                "success": True,
                "score": 0.8,
                "duration_ms": 1200
            },
            {
                "step": 2,
                "action": "fetch_content",
                "tool": "web_fetch",
                "input_summary": "url: https://example.com/openclaw-skill-evolution",
                "output_summary": "Extracted content about skill evolution framework",
                "success": True,
                "score": 0.9,
                "duration_ms": 800
            }
        ],
        "tools_used": ["web_search", "web_fetch"],
        "outputs_summary": "Successfully found and extracted information about OpenClaw Skill Evolution",
        "success": True,
        "final_score": 0.85,
        "duration_ms": 2000
    }
    
    reflection = {
        "success_reason": "Used appropriate tools and got relevant results",
        "failure_risk": "None",
        "best_steps": [1, 2],
        "redundant_steps": [],
        "missing_steps": [],
        "optimized_workflow": "Same as original",
        "should_store_experience": True,
        "should_generate_skill": True,
        "improvement_notes": "No significant improvements needed"
    }
    
    # Test experience storage
    manager = ExperienceManager()
    experience = manager.store_experience(trajectory, reflection)
    
    if experience:
        print(f"Experience stored: {experience['experience_id']}")
        print(f"Score: {experience['score']}")
        print(f"Success count: {experience['success_count']}")
    else:
        print("Experience not stored (didn't meet criteria)")

if __name__ == "__main__":
    main()