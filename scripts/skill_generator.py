#!/usr/bin/env python3
"""
Skill Generator for OpenClaw Skill Evolution
Generates reusable skills from repeated successful workflows
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
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SkillGenerator:
    """Generates and manages reusable skills"""
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        self.workspace_path = workspace_path
        self.skills_dir = os.path.join(workspace_path, "skills", "generated")
        self.qdrant_client = QdrantClient(host="localhost", port=6333)
        
        # Ensure skills directory exists
        os.makedirs(self.skills_dir, exist_ok=True)
    
    def load_thresholds(self) -> Dict[str, Any]:
        """Load thresholds from config file"""
        config_path = os.path.join(self.workspace_path, "..", "Desktop", "开发工作区", "openclaw-skill-evolution", "config", "thresholds.json")
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Default thresholds
            return {
                "skill": {
                    "min_similar_tasks": 3,
                    "min_avg_score": 0.7,
                    "min_success_rate": 0.8
                }
            }
    
    def analyze_trajectories_for_skill(self, trajectories: List[Dict]) -> Optional[Dict]:
        """Analyze similar trajectories to extract common workflow pattern"""
        if len(trajectories) < 3:
            logger.info(f"❌ Not enough trajectories ({len(trajectories)}) to generate skill. Need at least 3.")
            return None
        
        # Calculate success rate and average score
        success_count = sum(1 for t in trajectories if t.get("success", False))
        success_rate = success_count / len(trajectories)
        avg_score = sum(t.get("final_score", 0) for t in trajectories) / len(trajectories)
        
        thresholds = self.load_thresholds()["skill"]
        
        if success_rate < thresholds["min_success_rate"]:
            logger.info(f"❌ Success rate {success_rate:.2f} below threshold {thresholds['min_success_rate']}")
            return None
        
        if avg_score < thresholds["min_avg_score"]:
            logger.info(f"❌ Average score {avg_score:.2f} below threshold {thresholds['min_avg_score']}")
            return None
        
        # Extract common steps and tool order
        common_steps = self.extract_common_workflow(trajectories)
        if not common_steps:
            logger.info("❌ Could not extract common workflow pattern")
            return None
        
        # Generate skill metadata
        task_type = trajectories[0].get("task_type", "unknown")
        skill_name = f"{task_type}_skill"
        
        skill = {
            "skill_id": str(uuid.uuid4()),
            "skill_name": skill_name,
            "description": f"Automated skill for {task_type} tasks",
            "applicable_when": f"When task type is '{task_type}' and similar context",
            "steps": common_steps,
            "required_tools": list(set(tool for t in trajectories for tool in t.get("tools_used", []))),
            "success_rate": success_rate,
            "avg_score": avg_score,
            "usage_count": 0,
            "version": 1,
            "status": "active",
            "source": "auto-generated",
            "tags": [task_type, "auto-generated"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Generated skill candidate: {skill_name}")
        return skill
    
    def extract_common_workflow(self, trajectories: List[Dict]) -> List[str]:
        """Extract common workflow steps from trajectories"""
        if not trajectories:
            return []
        
        # Get steps from first trajectory as reference
        reference_steps = trajectories[0].get("steps", [])
        if not reference_steps:
            return []
        
        # Extract action descriptions from steps
        common_actions = []
        for step in reference_steps:
            action_desc = f"{step.get('action', 'unknown')} using {step.get('tool', 'unknown')}"
            common_actions.append(action_desc)
        
        return common_actions
    
    def save_skill_to_file(self, skill: Dict) -> str:
        """Save skill to local YAML file"""
        skill_name = skill["skill_name"]
        version = skill["version"]
        skill_file = os.path.join(self.skills_dir, f"{skill_name}.v{version}.yaml")
        
        # Prepare YAML content (remove ID for cleaner output)
        yaml_content = {
            "skill_name": skill["skill_name"],
            "description": skill["description"],
            "applicable_when": skill["applicable_when"],
            "steps": skill["steps"],
            "required_tools": skill["required_tools"],
            "success_rate": skill["success_rate"],
            "avg_score": skill["avg_score"],
            "usage_count": skill["usage_count"],
            "version": skill["version"],
            "status": skill["status"],
            "tags": skill["tags"],
            "created_at": skill["created_at"],
            "updated_at": skill["updated_at"]
        }
        
        with open(skill_file, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_content, f, allow_unicode=True, default_flow_style=False, indent=2)
        
        logger.info(f"✅ Saved skill to file: {skill_file}")
        return skill_file
    
    def save_skill_to_qdrant(self, skill: Dict) -> bool:
        """Save skill to Qdrant vector database"""
        try:
            # Create embedding content
            embedding_content = f"{skill['skill_name']} {skill['description']} {skill['applicable_when']} {' '.join(skill['tags'])}"
            
            # Placeholder embedding (1536-dimensional)
            placeholder_embedding = [0.1] * 1536
            
            # Create point for Qdrant
            point = PointStruct(
                id=skill["skill_id"],
                vector=placeholder_embedding,
                payload={
                    "skill_id": skill["skill_id"],
                    "skill_name": skill["skill_name"],
                    "description": skill["description"],
                    "applicable_when": skill["applicable_when"],
                    "steps": str(skill["steps"]),
                    "required_tools": skill["required_tools"],
                    "success_rate": skill["success_rate"],
                    "avg_score": skill["avg_score"],
                    "usage_count": skill["usage_count"],
                    "version": skill["version"],
                    "status": skill["status"],
                    "source": skill["source"],
                    "tags": skill["tags"],
                    "created_at": skill["created_at"],
                    "updated_at": skill["updated_at"]
                }
            )
            
            # Upsert to Qdrant
            self.qdrant_client.upsert(
                collection_name="skills",
                points=[point]
            )
            
            logger.info(f"✅ Saved skill to Qdrant: {skill['skill_id']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save skill to Qdrant: {e}")
            return False
    
    def generate_skill_from_trajectories(self, trajectories: List[Dict]) -> Optional[Dict]:
        """Complete skill generation workflow"""
        logger.info(f"🔍 Analyzing {len(trajectories)} trajectories for skill generation")
        
        # Analyze trajectories
        skill = self.analyze_trajectories_for_skill(trajectories)
        if not skill:
            logger.info("❌ Skill generation conditions not met")
            return None
        
        # Save to file
        self.save_skill_to_file(skill)
        
        # Save to Qdrant
        self.save_skill_to_qdrant(skill)
        
        logger.info(f"🎯 Skill generated successfully: {skill['skill_name']}")
        return skill

def main():
    """Test the skill generator"""
    generator = SkillGenerator()
    
    # Test trajectories (simulating 3 similar successful trajectories)
    test_trajectories = [
        {
            "trajectory_id": "test-1",
            "task": "Search and summarize web content about AI agents",
            "task_type": "web_research",
            "steps": [
                {"step": 1, "action": "search_web", "tool": "web_search", "success": True, "score": 0.8},
                {"step": 2, "action": "fetch_content", "tool": "web_fetch", "success": True, "score": 0.9}
            ],
            "tools_used": ["web_search", "web_fetch"],
            "success": True,
            "final_score": 0.85
        },
        {
            "trajectory_id": "test-2", 
            "task": "Research AI agent frameworks online",
            "task_type": "web_research",
            "steps": [
                {"step": 1, "action": "search_web", "tool": "web_search", "success": True, "score": 0.7},
                {"step": 2, "action": "fetch_content", "tool": "web_fetch", "success": True, "score": 0.8}
            ],
            "tools_used": ["web_search", "web_fetch"],
            "success": True,
            "final_score": 0.75
        },
        {
            "trajectory_id": "test-3",
            "task": "Find information about OpenClaw capabilities",
            "task_type": "web_research", 
            "steps": [
                {"step": 1, "action": "search_web", "tool": "web_search", "success": True, "score": 0.9},
                {"step": 2, "action": "fetch_content", "tool": "web_fetch", "success": True, "score": 0.8}
            ],
            "tools_used": ["web_search", "web_fetch"],
            "success": True,
            "final_score": 0.85
        }
    ]
    
    # Generate skill
    skill = generator.generate_skill_from_trajectories(test_trajectories)
    
    if skill:
        print(f"Test skill created: {skill['skill_name']}")
        print(f"Success rate: {skill['success_rate']:.2f}")
        print(f"Average score: {skill['avg_score']:.2f}")
    else:
        print("Skill generation failed")

if __name__ == "__main__":
    main()