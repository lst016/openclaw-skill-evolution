#!/usr/bin/env python3
"""
Evaluator for OpenClaw Skill Evolution
Implements dual-layer scoring: task-level and step-level scoring
"""

import sys
import os
import json
from typing import Dict, List, Any, Tuple
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

class Evaluator:
    """Evaluates task execution with dual-layer scoring"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "/Users/lst01/Desktop/开发工作区/openclaw-skill-evolution/config/thresholds.json"
        self.scoring_config = self.load_scoring_config()
    
    def load_scoring_config(self) -> Dict[str, float]:
        """Load scoring configuration from thresholds.json"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('scoring', {})
        except Exception as e:
            logger.warning(f"❌ Failed to load scoring config: {e}. Using defaults.")
            return self.get_default_scoring_config()
    
    def get_default_scoring_config(self) -> Dict[str, float]:
        """Get default scoring configuration"""
        return {
            "task_success": 1.0,
            "task_failure": -1.0,
            "validation_passed": 0.3,
            "high_quality_result": 0.2,
            "unnecessary_steps": -0.2,
            "introduced_errors": -0.5,
            "no_validation": -0.2,
            "correct_context": 0.1,
            "correct_target": 0.1,
            "effective_tool_call": 0.1,
            "effective_modification": 0.2,
            "completed_verification": 0.2,
            "ineffective_search": -0.1,
            "repeated_action": -0.1,
            "wrong_tool": -0.2,
            "circular_attempts": -0.3
        }
    
    def evaluate_step(
        self,
        step: Dict[str, Any],
        previous_steps: List[Dict[str, Any]] = None
    ) -> float:
        """
        Evaluate a single step and return step score
        
        Args:
            step: Step dictionary with evaluation criteria
            previous_steps: List of previous steps for context analysis
            
        Returns:
            float: Step score
        """
        score = 0.0
        previous_steps = previous_steps or []
        
        # Extract step evaluation flags (these would be set by the execution system)
        # For now, we'll use the step's success field and some heuristics
        
        # Base score from step success
        if step.get('success', False):
            score += self.scoring_config['effective_tool_call']
        else:
            score += self.scoring_config['wrong_tool']
        
        # Check for repeated actions
        current_action = step.get('action', '')
        current_tool = step.get('tool', '')
        repeated = any(
            prev_step.get('action') == current_action and 
            prev_step.get('tool') == current_tool
            for prev_step in previous_steps
        )
        if repeated:
            score += self.scoring_config['repeated_action']
        
        # Check for circular attempts (same action repeated multiple times)
        same_action_count = sum(
            1 for prev_step in previous_steps 
            if prev_step.get('action') == current_action
        )
        if same_action_count >= 2:
            score += self.scoring_config['circular_attempts']
        
        # Check for ineffective search (search with no results)
        if current_tool == 'web_search' and 'no results' in step.get('output_summary', '').lower():
            score += self.scoring_config['ineffective_search']
        
        # Add step-specific score if provided
        if 'score' in step:
            # Use provided score as base, then apply adjustments
            score = float(step['score'])
        
        # Ensure score is within reasonable bounds
        score = max(-1.0, min(1.0, score))
        
        logger.debug(f"Step {step.get('step', '?')} score: {score:.2f}")
        return score
    
    def evaluate_task_level(
        self,
        trajectory: Dict[str, Any],
        validation_passed: bool = False,
        high_quality_result: bool = False,
        unnecessary_steps: bool = False,
        introduced_errors: bool = False
    ) -> float:
        """
        Evaluate task-level score based on overall execution quality
        
        Args:
            trajectory: Complete trajectory dictionary
            validation_passed: Whether result was validated
            high_quality_result: Whether result quality is high
            unnecessary_steps: Whether execution had unnecessary steps
            introduced_errors: Whether execution introduced errors
            
        Returns:
            float: Task-level score
        """
        score = 0.0
        
        # Base score from task success
        if trajectory.get('success', False):
            score += self.scoring_config['task_success']
        else:
            score += self.scoring_config['task_failure']
        
        # Validation bonus/penalty
        if validation_passed:
            score += self.scoring_config['validation_passed']
        elif trajectory.get('success', False):  # Successful but not validated
            score += self.scoring_config['no_validation']
        
        # Quality bonus
        if high_quality_result:
            score += self.scoring_config['high_quality_result']
        
        # Penalty for unnecessary steps
        if unnecessary_steps:
            score += self.scoring_config['unnecessary_steps']
        
        # Penalty for introduced errors
        if introduced_errors:
            score += self.scoring_config['introduced_errors']
        
        # Ensure score is within reasonable bounds
        score = max(-2.0, min(2.0, score))
        
        logger.debug(f"Task-level score: {score:.2f}")
        return score
    
    def calculate_final_score(
        self,
        task_score: float,
        step_scores: List[float],
        quality_adjustment: float = 0.0
    ) -> float:
        """
        Calculate final score using the formula:
        final_score = task_score + sum(step_scores) + quality_adjustment
        
        Args:
            task_score: Task-level score
            step_scores: List of step-level scores
            quality_adjustment: Additional quality adjustment
            
        Returns:
            float: Final score
        """
        final_score = task_score + sum(step_scores) + quality_adjustment
        # Normalize to reasonable range (-2.0 to 2.0)
        final_score = max(-2.0, min(2.0, final_score))
        return final_score
    
    def evaluate_trajectory(
        self,
        trajectory: Dict[str, Any],
        validation_passed: bool = None,
        high_quality_result: bool = None,
        unnecessary_steps: bool = None,
        introduced_errors: bool = None
    ) -> Dict[str, Any]:
        """
        Complete trajectory evaluation workflow
        
        Args:
            trajectory: Trajectory to evaluate
            validation_passed: Override validation status
            high_quality_result: Override quality assessment  
            unnecessary_steps: Override unnecessary steps flag
            introduced_errors: Override error introduction flag
            
        Returns:
            Dict: Evaluation results with scores
        """
        logger.info(f"🔍 Evaluating trajectory: {trajectory.get('trajectory_id', 'unknown')}")
        
        # Determine evaluation flags (these would typically come from reflection or manual review)
        # For now, we'll use trajectory data and some heuristics
        if validation_passed is None:
            validation_passed = trajectory.get('success', False) and 'validated' in trajectory.get('outputs_summary', '').lower()
        
        if high_quality_result is None:
            high_quality_result = trajectory.get('final_score', 0) > 0.7 if 'final_score' in trajectory else False
            
        if unnecessary_steps is None:
            unnecessary_steps = len(trajectory.get('steps', [])) > 10  # Heuristic: too many steps
            
        if introduced_errors is None:
            introduced_errors = 'error' in trajectory.get('outputs_summary', '').lower()
        
        # Evaluate task level
        task_score = self.evaluate_task_level(
            trajectory,
            validation_passed=validation_passed,
            high_quality_result=high_quality_result,
            unnecessary_steps=unnecessary_steps,
            introduced_errors=introduced_errors
        )
        
        # Evaluate each step
        step_scores = []
        previous_steps = []
        for step in trajectory.get('steps', []):
            step_score = self.evaluate_step(step, previous_steps)
            step_scores.append(step_score)
            previous_steps.append(step)
            
            # Update step with calculated score if not already present
            if 'score' not in step:
                step['score'] = step_score
        
        # Calculate final score
        final_score = self.calculate_final_score(task_score, step_scores)
        
        # Update trajectory with scores
        trajectory['task_score'] = task_score
        trajectory['step_scores'] = step_scores
        trajectory['final_score'] = final_score
        
        evaluation_result = {
            'trajectory_id': trajectory.get('trajectory_id'),
            'task_score': task_score,
            'step_scores': step_scores,
            'final_score': final_score,
            'evaluation_timestamp': trajectory.get('created_at', ''),
            'validation_passed': validation_passed,
            'high_quality_result': high_quality_result,
            'unnecessary_steps': unnecessary_steps,
            'introduced_errors': introduced_errors
        }
        
        logger.info(f"✅ Evaluation complete - Final score: {final_score:.2f}")
        return evaluation_result

def main():
    """Test the evaluator with sample trajectory"""
    # Load test trajectory
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
                "duration_ms": 1200
            },
            {
                "step": 2, 
                "action": "fetch_content",
                "tool": "web_fetch",
                "input_summary": "url: https://example.com/openclaw-skill-evolution",
                "output_summary": "Extracted content about skill evolution framework",
                "success": True,
                "duration_ms": 800
            }
        ],
        "tools_used": ["web_search", "web_fetch"],
        "outputs_summary": "Successfully found and extracted information about OpenClaw Skill Evolution",
        "success": True,
        "duration_ms": 2000,
        "created_at": "2026-03-11T21:25:00+08:00"
    }
    
    # Evaluate trajectory
    evaluator = Evaluator()
    result = evaluator.evaluate_trajectory(
        test_trajectory,
        validation_passed=True,
        high_quality_result=True,
        unnecessary_steps=False,
        introduced_errors=False
    )
    
    print("Evaluation Result:")
    print(f"Task Score: {result['task_score']:.2f}")
    print(f"Step Scores: {[f'{s:.2f}' for s in result['step_scores']]}")
    print(f"Final Score: {result['final_score']:.2f}")
    
    # Verify trajectory was updated
    print(f"\nUpdated Trajectory Final Score: {test_trajectory['final_score']:.2f}")

if __name__ == "__main__":
    main()