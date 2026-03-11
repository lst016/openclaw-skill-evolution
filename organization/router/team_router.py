#!/usr/bin/env python3
"""
Team Router for OpenClaw Skill Evolution v6
Routes tasks to appropriate agent teams based on task requirements and team capabilities.

English: 
Team Router - Maps tasks to optimal agent teams based on task complexity, required skills, and team performance history.

中文注释:
团队路由器 - 根据任务复杂度、所需技能和团队表现历史，将任务映射到最优的代理团队。
"""

import sys
import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging

# Add the virtual environment to Python path
venv_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '.venv')
if os.path.exists(venv_path):
    site_packages = os.path.join(venv_path, 'lib', 'python3.14', 'site-packages')
    if os.path.exists(site_packages):
        sys.path.insert(0, site_packages)

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TeamRouter:
    """
    Routes tasks to appropriate agent teams.
    
    English: 
    Analyzes task requirements and selects the best agent team composition 
    based on historical performance, skill matching, and workload balancing.
    
    中文: 
    分析任务需求并基于历史表现、技能匹配和工作负载平衡选择最佳的代理团队组合。
    """
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        """
        Initialize the Team Router.
        
        English: 
        Initialize with workspace path, Qdrant connection, and load existing teams.
        
        中文: 
        使用工作区路径、Qdrant 连接初始化并加载现有团队。
        """
        self.workspace_path = workspace_path
        self.teams_dir = os.path.join(workspace_path, "teams")
        self.qdrant_client = QdrantClient(host="localhost", port=6333)
        
        # Ensure teams directory exists
        os.makedirs(self.teams_dir, exist_ok=True)
        
        logger.info("✅ Team Router initialized")
        logger.info(f"   Teams directory: {self.teams_dir}")
        logger.info(f"   Qdrant connection: localhost:6333")
    
    def create_team_id(self) -> str:
        """
        Generate a unique team ID.
        
        English: Generate UUID-based team ID for uniqueness.
        中文: 生成基于 UUID 的团队 ID 以确保唯一性。
        """
        return str(uuid.uuid4())
    
    def get_current_timestamp(self) -> str:
        """
        Get current timestamp in ISO format.
        
        English: Return current time as ISO string for consistency.
        中文: 返回当前时间的 ISO 字符串以保持一致性。
        """
        return datetime.now().isoformat()
    
    def analyze_task_requirements(self, task: str, task_type: str) -> Dict[str, Any]:
        """
        Analyze task requirements to determine needed agent roles.
        
        English: 
        Extract required skills, complexity level, and role requirements from task description.
        
        中文: 
        从任务描述中提取所需技能、复杂度级别和角色需求。
        
        Args:
            task (str): The task description
            task_type (str): The standardized task type
            
        Returns:
            Dict[str, Any]: Task requirements analysis
        """
        # In a real implementation, this would use LLM analysis
        # For now, we'll use simple rule-based analysis
        
        requirements = {
            "task": task,
            "task_type": task_type,
            "complexity": "medium",
            "required_roles": ["executor"],
            "preferred_skills": [],
            "estimated_duration": "unknown",
            "criticality": "normal"
        }
        
        # Simple rule-based analysis
        task_lower = task.lower()
        if "complex" in task_lower or "debug" in task_lower or "analyze" in task_lower:
            requirements["complexity"] = "high"
            requirements["required_roles"] = ["planner", "executor", "critic"]
            requirements["criticality"] = "high"
        elif "simple" in task_lower or "quick" in task_lower:
            requirements["complexity"] = "low"
            requirements["required_roles"] = ["executor"]
            requirements["criticality"] = "low"
        elif "implement" in task_lower or "develop" in task_lower or "code" in task_lower:
            requirements["complexity"] = "high"
            requirements["required_roles"] = ["planner", "executor", "critic", "reviewer"]
            requirements["criticality"] = "high"
            requirements["preferred_skills"] = ["coding", "testing", "documentation"]
        elif "optimize" in task_lower or "improve" in task_lower:
            requirements["complexity"] = "medium"
            requirements["required_roles"] = ["analyzer", "executor", "critic"]
            requirements["criticality"] = "medium"
            requirements["preferred_skills"] = ["analysis", "optimization"]
        
        logger.info(f"🔍 Analyzed task requirements: {requirements['complexity']} complexity, {len(requirements['required_roles'])} roles")
        return requirements
    
    def search_candidate_teams(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for candidate teams that match task requirements.
        
        English: 
        Query Qdrant for teams that can handle the required roles and complexity.
        
        中文: 
        查询 Qdrant 以找到能够处理所需角色和复杂度的团队。
        
        Args:
            requirements (Dict[str, Any]): Task requirements from analyze_task_requirements
            
        Returns:
            List[Dict[str, Any]]: List of candidate teams sorted by suitability
        """
        try:
            # Create query vector (placeholder - in real implementation would use embedding)
            query_vector = [0.1] * 1536
            
            # Search for teams
            search_result = self.qdrant_client.query_points(
                collection_name="teams",
                query=query_vector,
                limit=10
            )
            
            candidate_teams = []
            for point in search_result.points:
                team_data = point.payload
                # Calculate suitability score
                suitability_score = self.calculate_team_suitability(team_data, requirements)
                if suitability_score > 0.5:  # Only consider teams with reasonable suitability
                    team_data["suitability_score"] = suitability_score
                    candidate_teams.append(team_data)
            
            # Sort by suitability score
            candidate_teams.sort(key=lambda x: x["suitability_score"], reverse=True)
            
            logger.info(f"🎯 Found {len(candidate_teams)} candidate teams")
            return candidate_teams
            
        except Exception as e:
            logger.error(f"❌ Failed to search candidate teams: {e}")
            return []
    
    def calculate_team_suitability(self, team: Dict[str, Any], requirements: Dict[str, Any]) -> float:
        """
        Calculate how suitable a team is for given requirements.
        
        English: 
        Calculate suitability score based on role match, success rate, and workload.
        
        中文: 
        基于角色匹配、成功率和工作负载计算适合度分数。
        
        Args:
            team (Dict[str, Any]): Team data from Qdrant
            requirements (Dict[str, Any]): Task requirements
            
        Returns:
            float: Suitability score between 0.0 and 1.0
        """
        score = 0.0
        
        # Role match scoring (0.0 to 0.4)
        required_roles = set(requirements["required_roles"])
        team_roles = set(team.get("roles", []))
        if required_roles.issubset(team_roles):
            score += 0.4
        elif required_roles.intersection(team_roles):
            score += 0.2 * len(required_roles.intersection(team_roles)) / len(required_roles)
        
        # Success rate scoring (0.0 to 0.3)
        success_rate = team.get("success_rate", 0.0)
        score += 0.3 * success_rate
        
        # Complexity match scoring (0.0 to 0.2)
        team_complexity = team.get("complexity_level", "medium")
        req_complexity = requirements["complexity"]
        if team_complexity == req_complexity:
            score += 0.2
        elif (team_complexity == "high" and req_complexity in ["medium", "low"]) or \
             (team_complexity == "medium" and req_complexity == "low"):
            score += 0.1
        
        # Workload scoring (0.0 to 0.1)
        current_load = team.get("current_load", 0)
        max_load = team.get("max_load", 10)
        if max_load > 0:
            load_factor = 1.0 - (current_load / max_load)
            score += 0.1 * load_factor
        
        return min(score, 1.0)
    
    def select_optimal_team(self, candidate_teams: List[Dict[str, Any]], requirements: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Select the optimal team from candidates.
        
        English: 
        Choose the best team based on suitability score, fallback options, and policy rules.
        
        中文: 
        基于适合度分数、回退选项和策略规则选择最佳团队。
        
        Args:
            candidate_teams (List[Dict[str, Any]]): Sorted list of candidate teams
            requirements (Dict[str, Any]): Task requirements
            
        Returns:
            Optional[Dict[str, Any]]: Selected team or None if no suitable team found
        """
        if not candidate_teams:
            logger.warning("⚠️ No candidate teams found for task")
            return None
        
        # Select the highest scoring team
        optimal_team = candidate_teams[0]
        
        # Check if team meets minimum requirements
        if optimal_team["suitability_score"] < 0.6:
            logger.warning(f"⚠️ Best team suitability ({optimal_team['suitability_score']:.2f}) below threshold (0.6)")
            # Consider creating a new team
            new_team = self.create_dynamic_team(requirements)
            if new_team:
                optimal_team = new_team
        
        logger.info(f"✅ Selected optimal team: {optimal_team.get('team_id', 'unknown')}")
        logger.info(f"   Suitability score: {optimal_team['suitability_score']:.2f}")
        logger.info(f"   Roles: {optimal_team.get('roles', [])}")
        
        return optimal_team
    
    def create_dynamic_team(self, requirements: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a dynamic team for tasks that don't match existing teams.
        
        English: 
        Dynamically assemble a team based on required roles and available agents.
        
        中文: 
        基于所需角色和可用代理动态组装团队。
        
        Args:
            requirements (Dict[str, Any]): Task requirements
            
        Returns:
            Optional[Dict[str, Any]]: Newly created dynamic team
        """
        try:
            # This would normally query the Agent Registry
            # For now, we'll create a basic team structure
            team_id = self.create_team_id()
            roles = requirements["required_roles"]
            
            dynamic_team = {
                "team_id": team_id,
                "name": f"dynamic_team_{team_id[:8]}",
                "roles": roles,
                "workflow": "dynamic_workflow",
                "success_rate": 0.0,
                "avg_latency": 0,
                "complexity_level": requirements["complexity"],
                "current_load": 0,
                "max_load": len(roles) * 2,
                "created_at": self.get_current_timestamp(),
                "updated_at": self.get_current_timestamp(),
                "status": "active",
                "is_dynamic": True,
                "suitability_score": 0.7  # Assume reasonable suitability for dynamic teams
            }
            
            # Save to file system
            team_file = os.path.join(self.teams_dir, f"{team_id}.json")
            with open(team_file, 'w', encoding='utf-8') as f:
                json.dump(dynamic_team, f, indent=2, ensure_ascii=False)
            
            # Save to Qdrant (with placeholder embedding)
            placeholder_embedding = [0.1] * 1536
            point = PointStruct(
                id=team_id,
                vector=placeholder_embedding,
                payload=dynamic_team
            )
            
            self.qdrant_client.upsert(
                collection_name="teams",
                points=[point]
            )
            
            logger.info(f"🔄 Created dynamic team: {team_id}")
            return dynamic_team
            
        except Exception as e:
            logger.error(f"❌ Failed to create dynamic team: {e}")
            return None
    
    def route_task_to_team(self, task: str, task_type: str) -> Optional[Dict[str, Any]]:
        """
        Complete task routing workflow.
        
        English: 
        Analyze task, find candidate teams, and select optimal team for execution.
        
        中文: 
        分析任务，查找候选团队，并选择最佳团队执行。
        
        Args:
            task (str): The task description
            task_type (str): The standardized task type
            
        Returns:
            Optional[Dict[str, Any]]: Selected team information or None if routing failed
        """
        logger.info(f"🚀 Routing task to team: {task_type}")
        logger.info(f"   Task: {task}")
        
        # Analyze task requirements
        requirements = self.analyze_task_requirements(task, task_type)
        
        # Search for candidate teams
        candidate_teams = self.search_candidate_teams(requirements)
        
        # Select optimal team
        optimal_team = self.select_optimal_team(candidate_teams, requirements)
        
        if optimal_team:
            logger.info(f"🎯 Task routed successfully to team: {optimal_team['team_id']}")
        else:
            logger.error("❌ Task routing failed - no suitable team found")
        
        return optimal_team

def main():
    """Test the Team Router"""
    router = TeamRouter()
    
    # Test task routing
    test_task = "Implement a new payment feature with proper error handling and testing"
    test_task_type = "feature_implementation"
    
    selected_team = router.route_task_to_team(test_task, test_task_type)
    
    if selected_team:
        print(f"✅ Task routed to team: {selected_team['team_id']}")
        print(f"   Roles: {selected_team['roles']}")
        print(f"   Suitability: {selected_team['suitability_score']:.2f}")
    else:
        print("❌ Task routing failed")

if __name__ == "__main__":
    main()