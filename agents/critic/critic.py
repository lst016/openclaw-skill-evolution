#!/usr/bin/env python3
"""
Critic for OpenClaw Skill Evolution v3
Evaluates policy quality and provides strategy-level feedback
"""

import sys
import os
import json
from typing import Dict, List, Any, Optional
import logging

# Add the virtual environment to Python path
venv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.venv')
if os.path.exists(venv_path):
    site_packages = os.path.join(venv_path, 'lib', 'python3.14', 'site-packages')
    if os.path.exists(site_packages):
        sys.path.insert(0, site_packages)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Critic:
    """Evaluates policy quality and provides strategy-level feedback"""
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        self.workspace_path = workspace_path
        self.critic_log_dir = os.path.join(workspace_path, "logs", "critic")
        
        # Ensure log directory exists
        os.makedirs(self.critic_log_dir, exist_ok=True)
    
    def evaluate_policy_quality(self, trajectory: Dict, selected_skill: str, selected_workflow: str, selected_tool_order: List[str]) -> Dict[str, float]:
        """
        Evaluate the quality of policy decisions made during execution
        
        Returns detailed policy reward scores
        """
        logger.info(f"🔍 Evaluating policy quality for trajectory: {trajectory['trajectory_id']}")
        
        # Initialize scores
        skill_fit_score = 0.0
        workflow_fit_score = 0.0
        tool_order_score = 0.0
        efficiency_score = 0.0
        
        # 1. Skill fit evaluation
        skill_fit_score = self._evaluate_skill_fit(trajectory, selected_skill)
        
        # 2. Workflow fit evaluation  
        workflow_fit_score = self._evaluate_workflow_fit(trajectory, selected_workflow)
        
        # 3. Tool order evaluation
        tool_order_score = self._evaluate_tool_order(trajectory, selected_tool_order)
        
        # 4. Efficiency evaluation
        efficiency_score = self._evaluate_efficiency(trajectory)
        
        # Calculate final policy reward
        result_reward = 1.0 if trajectory.get("success", False) else -1.0
        efficiency_reward = efficiency_score
        strategy_reward = (skill_fit_score + workflow_fit_score + tool_order_score) / 3.0
        
        # Risk penalties
        risk_penalty = self._calculate_risk_penalty(trajectory)
        
        final_policy_reward = result_reward + efficiency_reward + strategy_reward - risk_penalty
        
        critic_result = {
            "trajectory_id": trajectory["trajectory_id"],
            "skill_fit_score": skill_fit_score,
            "workflow_fit_score": workflow_fit_score,
            "tool_order_score": tool_order_score,
            "efficiency_score": efficiency_score,
            "result_reward": result_reward,
            "efficiency_reward": efficiency_reward,
            "strategy_reward": strategy_reward,
            "risk_penalty": risk_penalty,
            "final_policy_reward": final_policy_reward,
            "suggested_adjustment": self._generate_suggestions(trajectory, skill_fit_score, workflow_fit_score, tool_order_score)
        }
        
        # Save critic result
        self._save_critic_result(critic_result)
        
        logger.info(f"✅ Policy evaluation completed - Final reward: {final_policy_reward:.2f}")
        return critic_result
    
    def _evaluate_skill_fit(self, trajectory: Dict, selected_skill: str) -> float:
        """Evaluate if the selected skill was appropriate for the task"""
        task_type = trajectory.get("task_type", "unknown")
        
        # Check if skill matches task type patterns
        if task_type == "debug" and "debug" in selected_skill.lower():
            return 0.2  # Correct skill selection
        elif task_type == "web_search" and "search" in selected_skill.lower():
            return 0.2
        elif task_type == "file_edit" and ("edit" in selected_skill.lower() or "write" in selected_skill.lower()):
            return 0.2
        else:
            return -0.1  # Suboptimal skill selection
    
    def _evaluate_workflow_fit(self, trajectory: Dict, selected_workflow: str) -> float:
        """Evaluate if the workflow was stable and appropriate"""
        steps = trajectory.get("steps", [])
        success = trajectory.get("success", False)
        
        if not steps:
            return -0.1
        
        # Check for redundant or unnecessary steps
        step_count = len(steps)
        if step_count <= 4:  # Reasonable step count
            return 0.2 if success else 0.1
        elif step_count <= 6:  # Slightly verbose but acceptable
            return 0.1 if success else 0.0
        else:  # Too many steps
            return -0.1 if success else -0.2
    
    def _evaluate_tool_order(self, trajectory: Dict, selected_tool_order: List[str]) -> float:
        """Evaluate if the tool order was logical and efficient"""
        tools_used = trajectory.get("tools_used", [])
        
        if not tools_used:
            return 0.0
        
        # Check if actual tool usage matches expected order
        if len(tools_used) == 1:
            return 0.1
        
        # Simple check: read before write/edit is good
        read_tools = [t for t in tools_used if t in ["read", "web_search", "web_fetch"]]
        write_tools = [t for t in tools_used if t in ["write", "edit", "exec"]]
        
        if read_tools and write_tools:
            # Check if read tools come before write tools
            first_read_idx = next((i for i, t in enumerate(tools_used) if t in read_tools), -1)
            first_write_idx = next((i for i, t in enumerate(tools_used) if t in write_tools), -1)
            
            if first_read_idx != -1 and first_write_idx != -1 and first_read_idx < first_write_idx:
                return 0.1
            else:
                return -0.1
        else:
            return 0.05
    
    def _evaluate_efficiency(self, trajectory: Dict) -> float:
        """Evaluate execution efficiency"""
        steps = trajectory.get("steps", [])
        duration_ms = trajectory.get("duration_ms", 0)
        success = trajectory.get("success", False)
        
        efficiency_score = 0.0
        
        # Step efficiency
        if len(steps) <= 4:
            efficiency_score += 0.2
        elif len(steps) <= 6:
            efficiency_score += 0.1
        
        # Time efficiency (relative to step count)
        if duration_ms > 0:
            avg_time_per_step = duration_ms / len(steps) if steps else 0
            if avg_time_per_step < 1000:  # Less than 1 second per step
                efficiency_score += 0.2
            elif avg_time_per_step < 2000:  # Less than 2 seconds per step
                efficiency_score += 0.1
        
        # Success bonus
        if success:
            efficiency_score += 0.1
        
        return min(efficiency_score, 0.4)  # Cap at 0.4
    
    def _calculate_risk_penalty(self, trajectory: Dict) -> float:
        """Calculate risk penalties for poor execution choices"""
        penalty = 0.0
        steps = trajectory.get("steps", [])
        
        # Check for repeated actions
        actions = [step.get("action") for step in steps]
        if len(actions) != len(set(actions)):
            penalty += 0.1  # Repeated actions
        
        # Check for circular attempts (same tool used multiple times without progress)
        tools = [step.get("tool") for step in steps]
        tool_counts = {}
        for tool in tools:
            tool_counts[tool] = tool_counts.get(tool, 0) + 1
        
        for count in tool_counts.values():
            if count > 2:
                penalty += 0.1 * (count - 2)  # Penalty for excessive tool usage
        
        # Check for missing validation
        validation_actions = [step for step in steps if "validate" in step.get("action", "").lower()]
        if not validation_actions and trajectory.get("success", False):
            penalty += 0.2  # Should have validated successful results
        
        # Check for wrong tools (tools that failed)
        failed_steps = [step for step in steps if not step.get("success", False)]
        if failed_steps:
            penalty += 0.2 * len(failed_steps)
        
        return min(penalty, 1.0)  # Cap penalty at 1.0
    
    def _generate_suggestions(self, trajectory: Dict, skill_fit: float, workflow_fit: float, tool_order: float) -> Dict[str, str]:
        """Generate suggestions for policy improvement"""
        suggestions = {}
        
        if skill_fit < 0:
            suggestions["skill"] = "Consider using a more task-appropriate skill"
        
        if workflow_fit < 0:
            suggestions["workflow"] = "Workflow may be too verbose; consider streamlining steps"
        
        if tool_order < 0:
            suggestions["tool_order"] = "Tool order may be suboptimal; ensure read-before-write pattern"
        
        # Check for specific issues
        steps = trajectory.get("steps", [])
        if len(steps) > 6:
            suggestions["efficiency"] = "Consider reducing step count for better efficiency"
        
        failed_steps = [step for step in steps if not step.get("success", False)]
        if failed_steps:
            suggestions["reliability"] = f"Avoid tools that failed: {[step.get('tool') for step in failed_steps]}"
        
        return suggestions
    
    def _save_critic_result(self, critic_result: Dict):
        """Save critic result to log file"""
        import datetime
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        critic_date_dir = os.path.join(self.critic_log_dir, date_str)
        os.makedirs(critic_date_dir, exist_ok=True)
        
        critic_file = os.path.join(critic_date_dir, f"{critic_result['trajectory_id']}.json")
        with open(critic_file, 'w', encoding='utf-8') as f:
            json.dump(critic_result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Saved critic result to: {critic_file}")

def main():
    """Test the critic"""
    critic = Critic()
    
    # Test trajectory
    test_trajectory = {
        "trajectory_id": "test-123",
        "task": "Debug a Python application error",
        "task_type": "debug",
        "steps": [
            {"step": 1, "action": "analyze_error", "tool": "read", "success": True, "score": 0.9},
            {"step": 2, "action": "inspect_code", "tool": "read", "success": True, "score": 0.8},
            {"step": 3, "action": "fix_error", "tool": "edit", "success": True, "score": 0.9},
            {"step": 4, "action": "validate_fix", "tool": "exec", "success": True, "score": 0.8}
        ],
        "tools_used": ["read", "edit", "exec"],
        "success": True,
        "final_score": 2.0,
        "duration_ms": 4000
    }
    
    # Evaluate policy quality
    critic_result = critic.evaluate_policy_quality(
        test_trajectory,
        selected_skill="structured_debugging",
        selected_workflow="debug_workflow_v1",
        selected_tool_order=["read", "edit", "exec"]
    )
    
    print("Critic Result:")
    print(f"Final Policy Reward: {critic_result['final_policy_reward']:.2f}")
    print(f"Skill Fit Score: {critic_result['skill_fit_score']:.2f}")
    print(f"Workflow Fit Score: {critic_result['workflow_fit_score']:.2f}")
    print(f"Tool Order Score: {critic_result['tool_order_score']:.2f}")
    print(f"Efficiency Score: {critic_result['efficiency_score']:.2f}")
    print(f"Risk Penalty: {critic_result['risk_penalty']:.2f}")
    
    if critic_result["suggested_adjustment"]:
        print("\nSuggestions:")
        for key, suggestion in critic_result["suggested_adjustment"].items():
            print(f"  {key}: {suggestion}")

if __name__ == "__main__":
    main()