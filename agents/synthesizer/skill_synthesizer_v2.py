#!/usr/bin/env python3
"""
Skill Synthesizer v2 for OpenClaw Skill Evolution
Generates skills from multiple successful workflows with noise removal
"""

import sys
import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
import logging
from collections import Counter

# Add the virtual environment to Python path
venv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.venv')
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

class SkillSynthesizerV2:
    """Advanced skill synthesizer that generates skills from multiple trajectories"""
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        self.workspace_path = workspace_path
        self.skills_dir = os.path.join(workspace_path, "skills", "generated")
        self.qdrant_client = QdrantClient(host="localhost", port=6333)
        
        # Ensure skills directory exists
        os.makedirs(self.skills_dir, exist_ok=True)
    
    def load_thresholds(self) -> Dict[str, Any]:
        """Load thresholds from config file"""
        config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config", "thresholds.json")
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                "skill": {
                    "min_similar_tasks": 3,
                    "min_avg_score": 0.7,
                    "min_success_rate": 0.8
                }
            }
    
    def group_trajectories_by_task_type(self, trajectories: List[Dict]) -> Dict[str, List[Dict]]:
        """Group trajectories by task type"""
        grouped = {}
        for trajectory in trajectories:
            task_type = trajectory.get("task_type", "unknown")
            if task_type not in grouped:
                grouped[task_type] = []
            grouped[task_type].append(trajectory)
        return grouped
    
    def filter_high_quality_trajectories(self, trajectories: List[Dict], min_score: float = 0.7) -> List[Dict]:
        """Filter trajectories with score above threshold"""
        return [t for t in trajectories if t.get("final_score", 0) >= min_score]
    
    def extract_step_intersection(self, trajectories: List[Dict]) -> List[str]:
        """Extract common steps across multiple trajectories (noise removal)"""
        if not trajectories:
            return []
        
        # Get all step sequences
        all_step_sequences = []
        for trajectory in trajectories:
            steps = trajectory.get("steps", [])
            step_sequence = []
            for step in steps:
                # Create normalized step representation
                step_repr = f"{step.get('action', 'unknown')}:{step.get('tool', 'unknown')}"
                step_sequence.append(step_repr)
            all_step_sequences.append(step_sequence)
        
        if not all_step_sequences:
            return []
        
        # Find most common step sequence length
        lengths = [len(seq) for seq in all_step_sequences]
        if not lengths:
            return []
        
        # Use the most frequent length as reference
        from collections import Counter
        length_counter = Counter(lengths)
        most_common_length = length_counter.most_common(1)[0][0]
        
        # Filter sequences with the most common length
        filtered_sequences = [seq for seq in all_step_sequences if len(seq) == most_common_length]
        
        if not filtered_sequences:
            # If no common length, use the first sequence as reference
            reference_seq = all_step_sequences[0]
        else:
            reference_seq = filtered_sequences[0]
        
        # Extract common steps at each position
        common_steps = []
        for i in range(len(reference_seq)):
            step_at_position = []
            for seq in filtered_sequences:
                if i < len(seq):
                    step_at_position.append(seq[i])
            
            if step_at_position:
                # Get the most common step at this position
                step_counter = Counter(step_at_position)
                most_common_step = step_counter.most_common(1)[0][0]
                # Convert back to action description
                if ':' in most_common_step:
                    action, tool = most_common_step.split(':', 1)
                    common_steps.append(f"{action} using {tool}")
                else:
                    common_steps.append(most_common_step)
        
        return common_steps
    
    def generate_skill_name(self, task_type: str) -> str:
        """Generate a descriptive skill name based on task type"""
        # Clean task type name
        clean_task_type = task_type.replace("_", " ").replace("-", " ")
        return f"{clean_task_type.replace(' ', '_')}_skill"
    
    def synthesize_skill_from_trajectories(self, trajectories: List[Dict], task_type: str) -> Optional[Dict]:
        """Synthesize a skill from multiple high-quality trajectories"""
        logger.info(f"🔍 Synthesizing skill for task type: {task_type} from {len(trajectories)} trajectories")
        
        # Calculate success rate and average score
        success_count = sum(1 for t in trajectories if t.get("success", False))
        success_rate = success_count / len(trajectories) if trajectories else 0
        avg_score = sum(t.get("final_score", 0) for t in trajectories) / len(trajectories) if trajectories else 0
        
        thresholds = self.load_thresholds()["skill"]
        
        if success_rate < thresholds["min_success_rate"]:
            logger.info(f"❌ Success rate {success_rate:.2f} below threshold {thresholds['min_success_rate']}")
            return None
        
        if avg_score < thresholds["min_avg_score"]:
            logger.info(f"❌ Average score {avg_score:.2f} below threshold {thresholds['min_avg_score']}")
            return None
        
        # Extract common workflow pattern
        common_steps = self.extract_step_intersection(trajectories)
        if not common_steps:
            logger.info("❌ Could not extract common workflow pattern")
            return None
        
        # Generate skill metadata
        skill_name = self.generate_skill_name(task_type)
        
        skill = {
            "skill_id": str(uuid.uuid4()),
            "skill_name": skill_name,
            "description": f"Automated skill for {task_type} tasks",
            "applicable_when": f"When task type is '{task_type}' and similar context",
            "steps": common_steps,
            "required_tools": list(set(tool for t in trajectories for step in t.get("steps", []) for tool in [step.get("tool")] if tool)),
            "success_rate": success_rate,
            "avg_score": avg_score,
            "usage_count": 0,
            "version": 1,
            "status": "active",
            "source": "auto-generated-v2",
            "tags": [task_type, "auto-generated-v2"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Synthesized skill candidate: {skill_name}")
        return skill
    
    def save_skill_to_file(self, skill: Dict) -> str:
        """Save skill to local YAML file"""
        skill_name = skill["skill_name"]
        version = skill["version"]
        skill_file = os.path.join(self.skills_dir, f"{skill_name}.v{version}.yaml")
        
        # Prepare YAML content
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
            embedding_content = f"{skill['skill_name']} {skill['description']} {skill['applicable_when']} {' '.join(skill['tags'])}"
            placeholder_embedding = [0.1] * 1536
            
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
            
            self.qdrant_client.upsert(collection_name="skills", points=[point])
            logger.info(f"✅ Saved skill to Qdrant: {skill['skill_id']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save skill to Qdrant: {e}")
            return False
    
    def synthesize_skills_from_all_trajectories(self, all_trajectories: List[Dict]) -> List[Dict]:
        """Main entry point: synthesize skills from all available trajectories"""
        logger.info(f"🎯 Starting skill synthesis from {len(all_trajectories)} trajectories")
        
        # Group by task type
        grouped_trajectories = self.group_trajectories_by_task_type(all_trajectories)
        synthesized_skills = []
        
        for task_type, trajectories in grouped_trajectories.items():
            if len(trajectories) < 3:
                logger.info(f"⚠️ Skipping task type '{task_type}': only {len(trajectories)} trajectories (need ≥3)")
                continue
            
            # Filter high-quality trajectories
            high_quality_trajectories = self.filter_high_quality_trajectories(trajectories)
            if len(high_quality_trajectories) < 3:
                logger.info(f"⚠️ Skipping task type '{task_type}': only {len(high_quality_trajectories)} high-quality trajectories")
                continue
            
            # Synthesize skill
            skill = self.synthesize_skill_from_trajectories(high_quality_trajectories, task_type)
            if skill:
                # Save skill
                self.save_skill_to_file(skill)
                self.save_skill_to_qdrant(skill)
                synthesized_skills.append(skill)
                logger.info(f"✨ Successfully synthesized skill: {skill['skill_name']}")
            else:
                logger.info(f"❌ Failed to synthesize skill for task type: {task_type}")
        
        logger.info(f"🎯 Skill synthesis completed. Generated {len(synthesized_skills)} new skills.")
        return synthesized_skills

def main():
    """Test the skill synthesizer v2"""
    synthesizer = SkillSynthesizerV2()
    
    # Test trajectories with different quality levels
    test_trajectories = [
        {
            "trajectory_id": "test-1",
            "task": "Debug Python code error",
            "task_type": "debug",
            "steps": [
                {"step": 1, "action": "analyze_error", "tool": "read", "success": True, "score": 0.9},
                {"step": 2, "action": "inspect_code", "tool": "read", "success": True, "score": 0.8},
                {"step": 3, "action": "generate_fix", "tool": "write", "success": True, "score": 0.9}
            ],
            "tools_used": ["read", "write"],
            "success": True,
            "final_score": 0.87
        },
        {
            "trajectory_id": "test-2",
            "task": "Fix JavaScript bug",
            "task_type": "debug", 
            "steps": [
                {"step": 1, "action": "analyze_error", "tool": "read", "success": True, "score": 0.8},
                {"step": 2, "action": "inspect_code", "tool": "read", "success": True, "score": 0.9},
                {"step": 3, "action": "generate_fix", "tool": "write", "success": True, "score": 0.8}
            ],
            "tools_used": ["read", "write"],
            "success": True,
            "final_score": 0.83
        },
        {
            "trajectory_id": "test-3",
            "task": "Resolve TypeScript compilation error",
            "task_type": "debug",
            "steps": [
                {"step": 1, "action": "analyze_error", "tool": "read", "success": True, "score": 0.9},
                {"step": 2, "action": "inspect_code", "tool": "read", "success": True, "score": 0.7},
                {"step": 3, "action": "generate_fix", "tool": "write", "success": True, "score": 0.9}
            ],
            "tools_used": ["read", "write"],
            "success": True,
            "final_score": 0.83
        },
        {
            "trajectory_id": "test-4",  # Low quality - should be filtered out
            "task": "Quick debug attempt",
            "task_type": "debug",
            "steps": [
                {"step": 1, "action": "guess_fix", "tool": "write", "success": False, "score": 0.3}
            ],
            "tools_used": ["write"],
            "success": False,
            "final_score": 0.3
        }
    ]
    
    # Synthesize skills
    skills = synthesizer.synthesize_skills_from_all_trajectories(test_trajectories)
    
    print(f"\nGenerated {len(skills)} skills:")
    for skill in skills:
        print(f"- {skill['skill_name']} (success_rate: {skill['success_rate']:.2f}, avg_score: {skill['avg_score']:.2f})")

if __name__ == "__main__":
    main()