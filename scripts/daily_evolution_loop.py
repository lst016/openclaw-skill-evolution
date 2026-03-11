#!/usr/bin/env python3
"""
Daily Evolution Loop for OpenClaw Skill Evolution v2
Runs daily to analyze trajectories, compare workflows, generate skills, and optimize policies
"""

import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

# Add the virtual environment to Python path
venv_path = os.path.join(os.path.dirname(__file__), '..', '.venv')
if os.path.exists(venv_path):
    site_packages = os.path.join(venv_path, 'lib', 'python3.14', 'site-packages')
    if os.path.exists(site_packages):
        sys.path.insert(0, site_packages)

# Add agents directory to path
agents_path = os.path.join(os.path.dirname(__file__), '..', 'agents')
sys.path.insert(0, agents_path)

from comparator.workflow_comparator import WorkflowComparator
from synthesizer.skill_synthesizer_v2 import SkillSynthesizerV2  
from optimizer.policy_optimizer import PolicyOptimizer
from main.trajectory_logger_v2 import TrajectoryLoggerV2

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DailyEvolutionLoop:
    """Daily evolution loop that drives skill synthesis and policy optimization"""
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        self.workspace_path = workspace_path
        self.logs_dir = os.path.join(workspace_path, "logs")
        self.reports_dir = os.path.join(workspace_path, "reports", "evolution")
        self.daily_reports_dir = os.path.join(self.logs_dir, "daily_reports")
        
        # Ensure directories exist
        os.makedirs(self.reports_dir, exist_ok=True)
        os.makedirs(self.daily_reports_dir, exist_ok=True)
        
        # Initialize components
        self.comparator = WorkflowComparator()
        self.synthesizer = SkillSynthesizerV2()
        self.optimizer = PolicyOptimizer()
        self.logger = TrajectoryLoggerV2()
    
    def get_yesterday_date_str(self) -> str:
        """Get yesterday's date in YYYY-MM-DD format"""
        yesterday = datetime.now() - timedelta(days=1)
        return yesterday.strftime("%Y-%m-%d")
    
    def load_trajectories_from_date(self, date_str: str) -> List[Dict]:
        """Load all trajectories from a specific date"""
        trajectories_dir = os.path.join(self.logs_dir, "trajectories", date_str)
        trajectories = []
        
        if not os.path.exists(trajectories_dir):
            logger.info(f"No trajectories found for date: {date_str}")
            return trajectories
        
        for filename in os.listdir(trajectories_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(trajectories_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        trajectory = json.load(f)
                        trajectories.append(trajectory)
                except Exception as e:
                    logger.error(f"Failed to load trajectory {filepath}: {e}")
        
        logger.info(f"Loaded {len(trajectories)} trajectories from {date_str}")
        return trajectories
    
    def group_trajectories_by_task_type(self, trajectories: List[Dict]) -> Dict[str, List[Dict]]:
        """Group trajectories by task type"""
        grouped = {}
        for trajectory in trajectories:
            task_type = trajectory.get("task_type", "unknown")
            if task_type not in grouped:
                grouped[task_type] = []
            grouped[task_type].append(trajectory)
        
        logger.info(f"Grouped trajectories into {len(grouped)} task types")
        return grouped
    
    def run_evolution_cycle(self, date_str: str = None) -> Dict[str, Any]:
        """Run the complete daily evolution cycle"""
        if date_str is None:
            date_str = self.get_yesterday_date_str()
        
        logger.info(f"🚀 Starting daily evolution cycle for {date_str}")
        
        # Load trajectories
        trajectories = self.load_trajectories_from_date(date_str)
        if not trajectories:
            logger.info("No trajectories to process, skipping evolution cycle")
            return {"status": "skipped", "reason": "no_trajectories"}
        
        # Group by task type
        grouped_trajectories = self.group_trajectories_by_task_type(trajectories)
        
        # Track evolution results
        evolution_results = {
            "date": date_str,
            "total_trajectories": len(trajectories),
            "task_types_processed": 0,
            "new_skills_generated": 0,
            "policies_updated": 0,
            "workflows_compared": 0,
            "details": {}
        }
        
        # Process each task type
        for task_type, task_trajectories in grouped_trajectories.items():
            logger.info(f"Processing task type: {task_type} ({len(task_trajectories)} trajectories)")
            
            task_results = {
                "task_type": task_type,
                "trajectories_count": len(task_trajectories),
                "best_workflow": None,
                "new_skill": None,
                "policy_updated": False
            }
            
            # Compare workflows
            if len(task_trajectories) >= 2:
                best_workflow = self.comparator.compare_workflows(task_trajectories)
                if best_workflow:
                    task_results["best_workflow"] = best_workflow
                    evolution_results["workflows_compared"] += 1
            
            # Generate skill (requires at least 3 trajectories)
            if len(task_trajectories) >= 3:
                new_skill = self.synthesizer.generate_skill_from_trajectories(task_trajectories, task_type)
                if new_skill:
                    task_results["new_skill"] = new_skill
                    evolution_results["new_skills_generated"] += 1
            
            # Optimize policy
            policy_updated = self.optimizer.optimize_policy_for_task_type(task_type, task_trajectories)
            task_results["policy_updated"] = policy_updated
            if policy_updated:
                evolution_results["policies_updated"] += 1
            
            evolution_results["task_types_processed"] += 1
            evolution_results["details"][task_type] = task_results
        
        # Generate daily report
        self.generate_daily_report(evolution_results)
        
        logger.info(f"✅ Daily evolution cycle completed for {date_str}")
        return evolution_results
    
    def generate_daily_report(self, evolution_results: Dict[str, Any]):
        """Generate a daily evolution report"""
        date_str = evolution_results["date"]
        report_file = os.path.join(self.daily_reports_dir, f"{date_str}.md")
        
        report_content = f"""# Daily Evolution Report - {date_str}

## Summary
- **Total trajectories processed**: {evolution_results['total_trajectories']}
- **Task types processed**: {evolution_results['task_types_processed']}
- **New skills generated**: {evolution_results['new_skills_generated']}
- **Policies updated**: {evolution_results['policies_updated']}
- **Workflows compared**: {evolution_results['workflows_compared']}

## Details by Task Type
"""
        
        for task_type, details in evolution_results["details"].items():
            report_content += f"\n### {task_type}\n"
            report_content += f"- Trajectories: {details['trajectories_count']}\n"
            if details['best_workflow']:
                report_content += f"- Best workflow score: {details['best_workflow']['score']:.2f}\n"
            if details['new_skill']:
                report_content += f"- New skill: {details['new_skill']['skill_name']}\n"
            report_content += f"- Policy updated: {'Yes' if details['policy_updated'] else 'No'}\n"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"📝 Daily report generated: {report_file}")

def main():
    """Run daily evolution loop"""
    evolution_loop = DailyEvolutionLoop()
    results = evolution_loop.run_evolution_cycle()
    print(f"Daily evolution completed: {results}")

if __name__ == "__main__":
    main()