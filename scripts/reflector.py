#!/usr/bin/env python3
"""
Reflection Engine for OpenClaw Skill Evolution
Analyzes task trajectories and generates insights for improvement
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging

# Add the virtual environment to Python path
venv_path = os.path.join(os.path.dirname(__file__), '..', '.venv')
if os.path.exists(venv_path):
    site_packages = os.path.join(venv_path, 'lib', 'python3.14', 'site-packages')
    if os.path.exists(site_packages):
        sys.path.insert(0, site_packages)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Reflector:
    """Analyzes task trajectories and generates reflection insights"""
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        self.workspace_path = workspace_path
        self.reflections_log_dir = os.path.join(workspace_path, "logs", "reflections")
        self.thresholds_config = self.load_thresholds_config()
        
        # Ensure log directory exists
        os.makedirs(self.reflections_log_dir, exist_ok=True)
    
    def load_thresholds_config(self) -> Dict:
        """Load thresholds configuration from file"""
        config_path = "/Users/lst01/Desktop/开发工作区/openclaw-skill-evolution/config/thresholds.json"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load thresholds config: {e}. Using defaults.")
            return {
                "experience": {"min_final_score": 0.8},
                "skill": {"min_similar_tasks": 3}
            }
    
    def create_reflection_id(self) -> str:
        """Generate a unique reflection ID"""
        import uuid
        return str(uuid.uuid4())
    
    def get_current_date_str(self) -> str:
        """Get current date in YYYY-MM-DD format"""
        return datetime.now().strftime("%Y-%m-%d")
    
    def get_date_log_dir(self) -> str:
        """Get the log directory for current date"""
        date_str = self.get_current_date_str()
        date_log_dir = os.path.join(self.reflections_log_dir, date_str)
        os.makedirs(date_log_dir, exist_ok=True)
        return date_log_dir
    
    def analyze_step_effectiveness(self, step: Dict) -> Tuple[bool, str]:
        """Analyze if a step was effective"""
        if not step.get("success", False):
            return False, "step_failed"
        
        score = step.get("score", 0)
        if score >= 0.2:
            return True, "highly_effective"
        elif score >= 0.1:
            return True, "moderately_effective"
        else:
            return False, "ineffective"
    
    def identify_redundant_steps(self, steps: List[Dict]) -> List[int]:
        """Identify redundant or repeated steps"""
        redundant_indices = []
        seen_actions = set()
        
        for i, step in enumerate(steps):
            action_key = f"{step.get('action', '')}:{step.get('tool', '')}:{step.get('input_summary', '')}"
            if action_key in seen_actions:
                redundant_indices.append(i)
            else:
                seen_actions.add(action_key)
        
        return redundant_indices
    
    def identify_missing_steps(self, trajectory: Dict) -> List[str]:
        """Identify potentially missing steps based on task type"""
        task_type = trajectory.get("task_type", "")
        tools_used = trajectory.get("tools_used", [])
        missing_steps = []
        
        # Simple heuristics for common task types
        if task_type == "web_search" and "web_fetch" not in tools_used:
            missing_steps.append("content_extraction")
        elif task_type == "file_edit" and "read" not in [t for t in tools_used if "read" in t]:
            missing_steps.append("initial_file_reading")
        elif task_type == "code_generation" and "validate" not in [t for t in tools_used if "validate" in t]:
            missing_steps.append("code_validation")
        
        return missing_steps
    
    def should_store_experience(self, trajectory: Dict) -> bool:
        """Determine if this trajectory should be stored as experience"""
        success = trajectory.get("success", False)
        final_score = trajectory.get("final_score", 0)
        min_score = self.thresholds_config["experience"]["min_final_score"]
        
        return success and final_score >= min_score
    
    def should_generate_skill(self, trajectory: Dict) -> bool:
        """Determine if this trajectory suggests a new skill should be generated"""
        # This is a simplified check - in practice, this would look at similar trajectories
        success = trajectory.get("success", False)
        final_score = trajectory.get("final_score", 0)
        min_score = self.thresholds_config["experience"]["min_final_score"]
        
        return success and final_score >= min_score
    
    def generate_optimized_workflow(self, trajectory: Dict) -> List[Dict]:
        """Generate an optimized workflow based on the trajectory"""
        steps = trajectory.get("steps", [])
        redundant_indices = self.identify_redundant_steps(steps)
        
        optimized_steps = []
        for i, step in enumerate(steps):
            if i not in redundant_indices:
                optimized_steps.append(step)
        
        return optimized_steps
    
    def generate_reflection(self, trajectory: Dict) -> Dict:
        """Generate a complete reflection for a trajectory"""
        reflection_id = self.create_reflection_id()
        created_at = datetime.now().isoformat()
        
        steps = trajectory.get("steps", [])
        success = trajectory.get("success", False)
        
        # Analyze steps
        best_steps = []
        redundant_steps = []
        for i, step in enumerate(steps):
            is_effective, reason = self.analyze_step_effectiveness(step)
            if is_effective:
                best_steps.append(i)
            if i in self.identify_redundant_steps(steps):
                redundant_steps.append(i)
        
        # Identify missing steps
        missing_steps = self.identify_missing_steps(trajectory)
        
        # Generate optimized workflow
        optimized_workflow = self.generate_optimized_workflow(trajectory)
        
        # Determine storage decisions
        should_store_experience = self.should_store_experience(trajectory)
        should_generate_skill = self.should_generate_skill(trajectory)
        
        reflection = {
            "reflection_id": reflection_id,
            "trajectory_id": trajectory.get("trajectory_id"),
            "success_reason": "Task completed successfully" if success else "Task failed",
            "failure_risk": "Low" if success else "High",
            "best_steps": best_steps,
            "redundant_steps": redundant_steps,
            "missing_steps": missing_steps,
            "optimized_workflow": optimized_workflow,
            "should_store_experience": should_store_experience,
            "should_generate_skill": should_generate_skill,
            "improvement_notes": self.generate_improvement_notes(trajectory, redundant_steps, missing_steps),
            "created_at": created_at
        }
        
        return reflection
    
    def generate_improvement_notes(self, trajectory: Dict, redundant_steps: List[int], missing_steps: List[str]) -> str:
        """Generate human-readable improvement notes"""
        notes = []
        
        if redundant_steps:
            notes.append(f"Remove redundant steps at indices: {redundant_steps}")
        if missing_steps:
            notes.append(f"Consider adding missing steps: {', '.join(missing_steps)}")
        if not trajectory.get("success", False):
            notes.append("Task failed - consider alternative approaches")
        
        return "; ".join(notes) if notes else "No significant improvements needed"
    
    def save_reflection_to_file(self, reflection: Dict) -> str:
        """Save reflection to local file"""
        date_log_dir = self.get_date_log_dir()
        reflection_file = os.path.join(date_log_dir, f"{reflection['reflection_id']}.json")
        
        with open(reflection_file, 'w', encoding='utf-8') as f:
            json.dump(reflection, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Saved reflection to file: {reflection_file}")
        return reflection_file
    
    def reflect_trajectory(self, trajectory: Dict) -> Dict:
        """Complete reflection workflow for a trajectory"""
        logger.info(f"🔍 Reflecting on trajectory: {trajectory.get('trajectory_id', 'unknown')}")
        
        # Generate reflection
        reflection = self.generate_reflection(trajectory)
        
        # Save to file
        self.save_reflection_to_file(reflection)
        
        logger.info(f"🎯 Reflection completed: {reflection['reflection_id']}")
        return reflection

def main():
    """Test the reflector"""
    reflector = Reflector()
    
    # Test trajectory (similar to what we created in trajectory_logger)
    test_trajectory = {
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
        "final_score": 1.7,
        "duration_ms": 2000
    }
    
    # Generate reflection
    reflection = reflector.reflect_trajectory(test_trajectory)
    
    print(f"Reflection created: {reflection['reflection_id']}")
    print(f"Should store experience: {reflection['should_store_experience']}")
    print(f"Should generate skill: {reflection['should_generate_skill']}")
    print(f"Improvement notes: {reflection['improvement_notes']}")

if __name__ == "__main__":
    main()