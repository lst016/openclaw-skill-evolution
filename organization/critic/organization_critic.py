#!/usr/bin/env python3
"""
Organization Critic Module for OpenClaw Skill Evolution v6

组织批评家模块 - 评估整个组织结构的合理性

This module evaluates the overall organization structure and performance,
identifying bottlenecks, inefficiencies, and optimization opportunities.

该模块评估整体组织结构和性能，识别瓶颈、低效环节和优化机会。

Author: 牛牛 (Niuniu)
Version: v6.0
"""

import sys
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

# Add the virtual environment to Python path
venv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.venv')
if os.path.exists(venv_path):
    site_packages = os.path.join(venv_path, 'lib', 'python3.14', 'site-packages')
    if os.path.exists(site_packages):
        sys.path.insert(0, site_packages)

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, QueryResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentPerformance:
    """Agent performance metrics.
    
    Agent 性能指标。
    """
    agent_id: str
    role: str
    success_rate: float
    avg_response_time: float
    workload: int
    error_rate: float
    last_active: datetime

@dataclass  
class TeamPerformance:
    """Team performance metrics.
    
    团队性能指标。
    """
    team_id: str
    roles: List[str]
    success_rate: float
    avg_completion_time: float
    collaboration_score: float
    member_count: int

class OrganizationCritic:
    """
    Organization Critic evaluates the overall AI organization structure.
    
    组织批评家评估整体 AI 组织结构。
    
    Responsibilities:
    职责：
    - Monitor agent performance and workload
    - 监控 agent 性能和工作负载
    - Evaluate team effectiveness
    - 评估团队有效性  
    - Identify organizational bottlenecks
    - 识别组织瓶颈
    - Recommend structural improvements
    - 推荐结构改进
    - Update organization policies based on performance data
    - 基于性能数据更新组织策略
    """
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        """
        Initialize the Organization Critic.
        
        初始化组织批评家。
        
        Args:
            workspace_path (str): Path to the OpenClaw workspace
                                OpenClaw 工作区路径
        """
        self.workspace_path = workspace_path
        self.qdrant_client = QdrantClient(host="localhost", port=6333)
        self.organization_log_dir = os.path.join(workspace_path, "logs", "organization")
        os.makedirs(self.organization_log_dir, exist_ok=True)
        
        # Performance thresholds
        # 性能阈值
        self.low_performance_threshold = 0.7  # Success rate below 70%
        self.high_workload_threshold = 10     # More than 10 active tasks
        self.slow_response_threshold = 30.0   # Response time > 30 seconds
        self.high_error_threshold = 0.1       # Error rate > 10%
        
        logger.info("✅ Organization Critic initialized")
    
    def collect_agent_performance(self) -> List[AgentPerformance]:
        """
        Collect performance metrics for all registered agents.
        
        收集所有注册 agent 的性能指标。
        
        Returns:
            List[AgentPerformance]: List of agent performance metrics
                                  agent 性能指标列表
        """
        logger.info("📊 Collecting agent performance metrics...")
        
        # In a real implementation, this would query actual agent performance data
        # 在实际实现中，这将查询实际的 agent 性能数据
        # For now, we'll simulate some performance data
        # 现在，我们将模拟一些性能数据
        
        simulated_agents = [
            AgentPerformance(
                agent_id="planner_agent_001",
                role="planner",
                success_rate=0.85,
                avg_response_time=15.2,
                workload=3,
                error_rate=0.05,
                last_active=datetime.now()
            ),
            AgentPerformance(
                agent_id="executor_agent_001", 
                role="executor",
                success_rate=0.92,
                avg_response_time=8.7,
                workload=12,  # High workload!
                error_rate=0.03,
                last_active=datetime.now()
            ),
            AgentPerformance(
                agent_id="critic_agent_001",
                role="critic", 
                success_rate=0.78,  # Low performance!
                avg_response_time=25.1,
                workload=2,
                error_rate=0.12,  # High error rate!
                last_active=datetime.now() - timedelta(hours=2)
            ),
            AgentPerformance(
                agent_id="debug_agent_001",
                role="debug",
                success_rate=0.88,
                avg_response_time=18.3,
                workload=5,
                error_rate=0.04,
                last_active=datetime.now()
            )
        ]
        
        logger.info(f"✅ Collected performance data for {len(simulated_agents)} agents")
        return simulated_agents
    
    def collect_team_performance(self) -> List[TeamPerformance]:
        """
        Collect performance metrics for all teams.
        
        收集所有团队的性能指标。
        
        Returns:
            List[TeamPerformance]: List of team performance metrics
                                 团队性能指标列表
        """
        logger.info("📊 Collecting team performance metrics...")
        
        # Simulate team performance data
        # 模拟团队性能数据
        simulated_teams = [
            TeamPerformance(
                team_id="debug_team_001",
                roles=["debug", "analysis", "executor"],
                success_rate=0.82,
                avg_completion_time=45.2,
                collaboration_score=0.75,
                member_count=3
            ),
            TeamPerformance(
                team_id="feature_team_001",
                roles=["planner", "executor", "critic", "reviewer"],
                success_rate=0.89,
                avg_completion_time=62.8,
                collaboration_score=0.82,
                member_count=4
            ),
            TeamPerformance(
                team_id="ops_team_001", 
                roles=["monitor", "alert", "executor"],
                success_rate=0.76,  # Low performance!
                avg_completion_time=38.5,
                collaboration_score=0.68,  # Low collaboration!
                member_count=3
            )
        ]
        
        logger.info(f"✅ Collected performance data for {len(simulated_teams)} teams")
        return simulated_teams
    
    def identify_problematic_agents(self, agents: List[AgentPerformance]) -> List[Dict[str, Any]]:
        """
        Identify agents with performance issues.
        
        识别存在性能问题的 agent。
        
        Args:
            agents (List[AgentPerformance]): List of agent performance data
                                          agent 性能数据列表
            
        Returns:
            List[Dict[str, Any]]: List of problematic agents with issues
                                存在问题的 agent 列表及其问题
        """
        logger.info("🔍 Identifying problematic agents...")
        
        problematic_agents = []
        
        for agent in agents:
            issues = []
            
            # Check success rate
            if agent.success_rate < self.low_performance_threshold:
                issues.append(f"low_success_rate ({agent.success_rate:.2f})")
            
            # Check workload
            if agent.workload > self.high_workload_threshold:
                issues.append(f"high_workload ({agent.workload})")
                
            # Check response time
            if agent.avg_response_time > self.slow_response_threshold:
                issues.append(f"slow_response ({agent.avg_response_time:.1f}s)")
                
            # Check error rate
            if agent.error_rate > self.high_error_threshold:
                issues.append(f"high_error_rate ({agent.error_rate:.2f})")
                
            # Check activity
            if datetime.now() - agent.last_active > timedelta(hours=1):
                issues.append("inactive")
            
            if issues:
                problematic_agents.append({
                    "agent_id": agent.agent_id,
                    "role": agent.role,
                    "issues": issues,
                    "performance": {
                        "success_rate": agent.success_rate,
                        "workload": agent.workload,
                        "response_time": agent.avg_response_time,
                        "error_rate": agent.error_rate
                    }
                })
        
        logger.info(f"⚠️ Found {len(problematic_agents)} problematic agents")
        return problematic_agents
    
    def identify_problematic_teams(self, teams: List[TeamPerformance]) -> List[Dict[str, Any]]:
        """
        Identify teams with performance issues.
        
        识别存在性能问题的团队。
        
        Args:
            teams (List[TeamPerformance]): List of team performance data
                                        团队性能数据列表
            
        Returns:
            List[Dict[str, Any]]: List of problematic teams with issues
                                存在问题的团队列表及其问题
        """
        logger.info("🔍 Identifying problematic teams...")
        
        problematic_teams = []
        
        for team in teams:
            issues = []
            
            # Check success rate
            if team.success_rate < self.low_performance_threshold:
                issues.append(f"low_success_rate ({team.success_rate:.2f})")
                
            # Check collaboration score
            if team.collaboration_score < 0.7:
                issues.append(f"low_collaboration ({team.collaboration_score:.2f})")
            
            if issues:
                problematic_teams.append({
                    "team_id": team.team_id,
                    "roles": team.roles,
                    "issues": issues,
                    "performance": {
                        "success_rate": team.success_rate,
                        "completion_time": team.avg_completion_time,
                        "collaboration_score": team.collaboration_score
                    }
                })
        
        logger.info(f"⚠️ Found {len(problematic_teams)} problematic teams")
        return problematic_teams
    
    def generate_organization_recommendations(self, 
                                           problematic_agents: List[Dict[str, Any]],
                                           problematic_teams: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate recommendations for organizational improvements.
        
        生成组织改进建议。
        
        Args:
            problematic_agents (List[Dict[str, Any]]): Problematic agents
                                                    存在问题的 agent
            problematic_teams (List[Dict[str, Any]]): Problematic teams  
                                                    存在问题的团队
            
        Returns:
            Dict[str, Any]: Recommendations for organizational improvements
                          组织改进建议
        """
        logger.info("💡 Generating organization recommendations...")
        
        recommendations = {
            "agent_recommendations": [],
            "team_recommendations": [],
            "structural_changes": [],
            "policy_updates": []
        }
        
        # Agent recommendations
        for agent in problematic_agents:
            if "high_workload" in agent["issues"]:
                recommendations["agent_recommendations"].append({
                    "action": "redistribute_workload",
                    "target": agent["agent_id"],
                    "reason": f"Agent {agent['agent_id']} has high workload ({agent['performance']['workload']})"
                })
            
            if "low_success_rate" in agent["issues"] or "high_error_rate" in agent["issues"]:
                recommendations["agent_recommendations"].append({
                    "action": "retrain_or_replace",
                    "target": agent["agent_id"],
                    "reason": f"Agent {agent['agent_id']} has poor performance (success: {agent['performance']['success_rate']:.2f}, errors: {agent['performance']['error_rate']:.2f})"
                })
            
            if "inactive" in agent["issues"]:
                recommendations["agent_recommendations"].append({
                    "action": "investigate_inactivity",
                    "target": agent["agent_id"],
                    "reason": f"Agent {agent['agent_id']} has been inactive for over 1 hour"
                })
        
        # Team recommendations
        for team in problematic_teams:
            if "low_success_rate" in team["issues"]:
                recommendations["team_recommendations"].append({
                    "action": "restructure_team",
                    "target": team["team_id"],
                    "reason": f"Team {team['team_id']} has low success rate ({team['performance']['success_rate']:.2f})"
                })
            
            if "low_collaboration" in team["issues"]:
                recommendations["team_recommendations"].append({
                    "action": "improve_collaboration",
                    "target": team["team_id"],
                    "reason": f"Team {team['team_id']} has poor collaboration score ({team['performance']['collaboration_score']:.2f})"
                })
        
        # Structural changes
        if len(problematic_agents) > len([a for a in problematic_agents if "high_workload" in a["issues"]]):
            recommendations["structural_changes"].append({
                "action": "create_specialized_agents",
                "reason": "Multiple agents showing performance issues, consider creating more specialized agents"
            })
        
        if len(problematic_teams) > 0:
            recommendations["structural_changes"].append({
                "action": "review_team_composition",
                "reason": "Multiple teams showing collaboration issues, review team composition strategies"
            })
        
        # Policy updates
        recommendations["policy_updates"].append({
            "action": "update_workload_balancing_policy",
            "reason": "Workload distribution needs optimization based on current agent performance"
        })
        
        recommendations["policy_updates"].append({
            "action": "update_team_formation_policy", 
            "reason": "Team formation policies need adjustment based on collaboration performance"
        })
        
        logger.info(f"✅ Generated {len(recommendations['agent_recommendations'])} agent recommendations")
        logger.info(f"✅ Generated {len(recommendations['team_recommendations'])} team recommendations")
        logger.info(f"✅ Generated {len(recommendations['structural_changes'])} structural changes")
        logger.info(f"✅ Generated {len(recommendations['policy_updates'])} policy updates")
        
        return recommendations
    
    def update_organization_policies(self, recommendations: Dict[str, Any]) -> bool:
        """
        Update organization policies based on recommendations.
        
        基于建议更新组织策略。
        
        Args:
            recommendations (Dict[str, Any]): Organization recommendations
                                            组织建议
            
        Returns:
            bool: True if policies were successfully updated
                如果策略成功更新则返回 True
        """
        logger.info("🔄 Updating organization policies...")
        
        try:
            # Load existing organization policy
            policy_file = os.path.join(self.workspace_path, "policies", "organization_policy.json")
            
            if os.path.exists(policy_file):
                with open(policy_file, 'r', encoding='utf-8') as f:
                    policy = json.load(f)
            else:
                policy = {"version": "1.0", "last_updated": "", "policies": {}}
            
            # Apply recommendations to policy
            # This is a simplified implementation - in reality, this would be more complex
            # 这是一个简化的实现 - 实际上会更复杂
            
            current_time = datetime.now().isoformat()
            policy["last_updated"] = current_time
            policy["version"] = "2.0"  # Increment version
            
            # Add new policies based on recommendations
            # 基于建议添加新策略
            if "workload_balancing" not in policy["policies"]:
                policy["policies"]["workload_balancing"] = {
                    "max_workload_per_agent": 8,  # Reduced from 10
                    "auto_redistribution": True,
                    "updated_at": current_time
                }
            
            if "team_formation" not in policy["policies"]:
                policy["policies"]["team_formation"] = {
                    "min_collaboration_score": 0.75,  # Increased from 0.7
                    "max_team_size": 5,
                    "updated_at": current_time
                }
            
            # Save updated policy
            with open(policy_file, 'w', encoding='utf-8') as f:
                json.dump(policy, f, indent=2, ensure_ascii=False)
            
            # Also save to Qdrant for vector search capabilities
            # 也保存到 Qdrant 以支持向量搜索功能
            policy_embedding = [0.1] * 1536  # Placeholder embedding
            policy_point = PointStruct(
                id=f"org_policy_{current_time.replace(':', '-')}",
                vector=policy_embedding,
                payload={
                    "policy_type": "organization",
                    "version": policy["version"],
                    "last_updated": policy["last_updated"],
                    "policies": str(policy["policies"]),  # Convert to string for storage
                    "recommendations_applied": len(recommendations["policy_updates"])
                }
            )
            
            self.qdrant_client.upsert(
                collection_name="organization_policies",
                points=[policy_point]
            )
            
            logger.info("✅ Organization policies updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update organization policies: {e}")
            return False
    
    def evaluate_organization(self) -> Dict[str, Any]:
        """
        Complete organization evaluation workflow.
        
        完整的组织评估工作流。
        
        Returns:
            Dict[str, Any]: Complete organization evaluation results
                          完整的组织评估结果
        """
        logger.info("🎯 Starting complete organization evaluation...")
        
        # Step 1: Collect performance data
        # 步骤 1: 收集性能数据
        agents = self.collect_agent_performance()
        teams = self.collect_team_performance()
        
        # Step 2: Identify problems
        # 步骤 2: 识别问题
        problematic_agents = self.identify_problematic_agents(agents)
        problematic_teams = self.identify_problematic_teams(teams)
        
        # Step 3: Generate recommendations
        # 步骤 3: 生成建议
        recommendations = self.generate_organization_recommendations(
            problematic_agents, problematic_teams
        )
        
        # Step 4: Update policies
        # 步骤 4: 更新策略
        policies_updated = self.update_organization_policies(recommendations)
        
        # Step 5: Save evaluation report
        # 步骤 5: 保存评估报告
        evaluation_report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_agents_evaluated": len(agents),
                "problematic_agents": len(problematic_agents),
                "total_teams_evaluated": len(teams),
                "problematic_teams": len(problematic_teams),
                "policies_updated": policies_updated
            },
            "problematic_agents": problematic_agents,
            "problematic_teams": problematic_teams,
            "recommendations": recommendations
        }
        
        report_file = os.path.join(
            self.organization_log_dir,
            f"organization_evaluation_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        )
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(evaluation_report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Organization evaluation completed. Report saved to: {report_file}")
        
        return evaluation_report

def main():
    """Test the Organization Critic module."""
    logger.info("🧪 Testing Organization Critic module...")
    
    critic = OrganizationCritic()
    evaluation_results = critic.evaluate_organization()
    
    print(f"Organization Evaluation Results:")
    print(f"- Agents evaluated: {evaluation_results['summary']['total_agents_evaluated']}")
    print(f"- Problematic agents: {evaluation_results['summary']['problematic_agents']}")
    print(f"- Teams evaluated: {evaluation_results['summary']['total_teams_evaluated']}")
    print(f"- Problematic teams: {evaluation_results['summary']['problematic_teams']}")
    print(f"- Policies updated: {evaluation_results['summary']['policies_updated']}")
    
    logger.info("🎉 Organization Critic test completed successfully!")

if __name__ == "__main__":
    main()