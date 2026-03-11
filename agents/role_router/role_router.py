#!/usr/bin/env python3
"""
Role Router for OpenClaw Skill Evolution v4
角色路由器 - 将任务路由到最优角色序列

The Role Router routes tasks to optimal role sequences based on task type and collaboration policies.
角色路由器根据任务类型和协作策略将任务路由到最优角色序列。

作用 / Purpose:
根据任务类型和任务复杂度，确定最优的角色执行顺序。
Routes tasks to optimal role sequence based on task type and task complexity.
基于任务类型和任务复杂度，确定最优的角色执行顺序。

核心功能 / Core Functions:
- Task Complexity Classification: Classify tasks as simple, medium, or complex
任务复杂度分类：将任务分类为简单、中等或复杂
- Role Sequence Selection: Select optimal role sequence for task type
角色序列选择：为任务类型选择最优的角色序列
- Handoff Point Identification: Determine where handoffs should occur
交接点识别：确定交接应该发生的位置
- Fallback Support: Provide simple fallback sequence if main routing fails
回退支持：如果主路由失败，提供简单的回退序列

For example / 例如:
- Simple task: executor only / 简单任务：仅执行器
- Medium task: planner → executor / 中等任务：规划器 → 执行器
- Complex task: planner → executor → critic / 复杂任务：规划器 → 执行器 → 评审员
"""

import sys
import os
import json
from typing import Dict, List, Any, Optional, Tuple
import logging

# Add the virtual environment to Python path
# 添加虚拟环境到 Python 路径
venv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.venv')
if os.path.exists(venv_path):
    site_packages = os.path.join(venv_path, 'lib', 'python3.14', 'site-packages')
    if os.path.exists(site_packages):
        sys.path.insert(0, site_packages)

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

# Configure logging / 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RoleRouter:
    """
    Role Router Class / 角色路由器类
    
    Routes tasks to optimal role sequences based on task type and collaboration policies.
    根据任务类型和协作策略将任务路由到最优角色序列。
    """
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        """
        Initialize the Role Router.
        初始化角色路由器。
        
        Args / 参数:
            workspace_path: Path to OpenClaw workspace directory
                           OpenClaw 工作区目录路径
        """
        self.workspace_path = workspace_path
        self.qdrant_client = QdrantClient(host="localhost", port=6333)
        
        # Load policies / 加载策略
        self.policies = self.load_policies()
        
        # Define available roles / 定义可用角色
        # / 定义可用角色
        self.available_roles = ["planner", "executor", "critic", "synthesizer", "fallback_manager"]
        logger.info(f"🎯 Role Router initialized with {len(self.available_roles)} available roles")
    
    def load_policies(self) -> Dict[str, Any]:
        """
        Load policies from policy files.
        从策略文件加载策略。
        
        Returns / 返回:
            Dictionary containing all policy types / 包含所有策略类型的字典
        """
        policies_dir = os.path.join(os.path.dirname(__file__), "..", "..", "policies")
        policies = {
            "task_policy": {},
            "skill_policy": {},
            "workflow_policy": {},
            "tool_policy": {},
            "fallback_policy": {},
            "role_policy": {},
            "handoff_policy": {},
            "collaboration_policy": {}
        }
        
        for policy_name in policies.keys():
            policy_file = os.path.join(policies_dir, f"{policy_name}.json")
            if os.path.exists(policy_file):
                with open(policy_file, 'r', encoding='utf-8') as f:
                    policies[policy_name] = json.load(f)
        
        logger.info(f"📋 Loaded policies: {list(policies.keys())}")
        return policies
    
    def classify_task_complexity(self, task: str, task_type: str) -> str:
        """
        Classify task complexity to determine role sequence.
        根据任务描述和任务类型分类任务复杂度，确定角色序列。
        
        Args / 参数:
            task: User task description / 用户任务描述
            task_type: Standardized task type / 标准化任务类型
        
        Returns / 返回:
            Task complexity level: "simple", "medium", or "complex"
            任务复杂度级别："simple"、"medium" 或 "complex"
        
        Note / 注意:
            Simple tasks: executor only / 简单任务：仅执行器
            Medium tasks: planner → executor / 中等任务：规划器 → 执行器  
            Complex tasks: planner → executor → critic / 复杂任务：规划器 → 执行器 → 评审员
        """
        task_lower = task.lower()
        
        # Simple task indicators / 简单任务指示符
        simple_keywords = ["simple", "quick", "basic", "straightforward", "easy", "fix typo", "edit file"]
        # Medium task indicators / 中等任务指示符
        medium_keywords = ["plan", "design", "create", "build", "develop", "implement", "add feature"]
        # Complex task indicators / 复杂任务指示符
        complex_keywords = ["complex", "complicated", "detailed", "thorough", "comprehensive", 
                           "analyze", "debug", "troubleshoot", "optimize", "refactor", "review"]
        
        if any(keyword in task_lower for keyword in simple_keywords):
            return "simple"
        elif any(keyword in task_lower for keyword in medium_keywords):
            return "medium"
        elif any(keyword in task_lower for keyword in complex_keywords):
            return "complex"
        
        # Default complexity based on task type / 基于任务类型的默认复杂度
        complex_task_types = ["debugging", "analysis", "optimization", "refactoring", "troubleshooting", "security"]
        if task_type in complex_task_types:
            return "complex"
        
        return "medium"
    
    def get_role_sequence_for_task_type(self, task_type: str, complexity: str) -> List[str]:
        """
        Get role sequence based on task type and complexity.
        根据任务类型和复杂度获取角色序列。
        
        Args / 参数:
            task_type: Standardized task type / 标准化任务类型
            complexity: Task complexity level / 任务复杂度级别
        
        Returns / 返回:
            Ordered list of roles that should handle the task
            应该处理该任务的角色有序列表
        """
        # Check collaboration policy first / 首先检查协作策略
        if task_type in self.policies["collaboration_policy"]:
            collaboration = self.policies["collaboration_policy"][task_type]
            if "role_sequence" in collaboration:
                return collaboration["role_sequence"]
        
        # Check role policy / 检查角色策略
        if task_type in self.policies["role_policy"]:
            role_policy = self.policies["role_policy"][task_type]
            if "role_sequence" in role_policy:
                return role_policy["role_sequence"]
        
        # Default role sequences based on complexity / 基于复杂度的默认角色序列
        # 默认角色序列 / Default role sequences
        if complexity == "simple":
            return ["executor"]
        elif complexity == "medium":
            return ["planner", "executor"]
        else:  # complex / 复杂
            return ["planner", "executor", "critic"]
    
    def validate_role_sequence(self, role_sequence: List[str]) -> bool:
        """
        Validate that all roles in sequence are available.
        验证序列中的所有角色都是可用的。
        
        Args / 参数:
            role_sequence: List of role names / 角色名称列表
        
        Returns / 返回:
            True if all roles are available, False otherwise
            如果所有角色都可用则返回 True，否则返回 False
        """
        return all(role in self.available_roles for role in role_sequence)
    
    def get_handoff_points(self, role_sequence: List[str]) -> List[Dict[str, str]]:
        """
        Get handoff points between roles.
        获取角色之间的交接点。
        
        Args / 参数:
            role_sequence: List of roles in sequence / 角色序列列表
        
        Returns / 返回:
            List of handoff configurations / 交接配置列表
        """
        handoff_points = []
        for i in range(len(role_sequence) - 1):
            from_role = role_sequence[i]
            to_role = role_sequence + 1]
            
            # Check handoff policy / 检查交接策略
            handoff_key = f"{from_role}_to_{to_role}"
            if handoff_key in self.policies["handoff_policy"]:
                handoff_config = self.policies["handoff_policy"][handoff_key]
                handoff_points.append({
                    "from_role": from_role,
                    "to_role": to_role,
                    "required_fields": handoff_config.get("required_fields", []),
                    "validation_rules": handoff_config.get("validation_rules", []),
                    "expected_inputs": handoff_config.get("expected_inputs", []),
                    "expected_outputs": handoff_config.get("expected_outputs", [])
                })
            else:
                # Default handoff / 默认交接
                handoff_points.append({
                    "from_role": from_role,
                    "to_role": to_role,
                    "required_fields": ["output", "status", "context"],
                    "validation_rules": ["output_not_empty", "status_is_success"],
                    "expected_inputs": ["plan", "requirements", "context"],
                    "expected_outputs": ["output", "status", "results"]
                })
        
        return handoff_points
    
    def route_task_to_roles(self, task: str, task_type: str) -> Dict[str, Any]:
        """
        Route task to optimal role sequence with handoff points.
        将任务路由到带有交接点的最优角色序列。
        
        Args / 参数:
            task: User task description / 用户任务描述
            task_type: Standardized task type / 标准化任务类型
        
        Returns / 返回:
            Dictionary containing role sequence, handoff points, and routing reason
            包含角色序列、交接点和路由原因的字典
        """
        logger.info(f"🔄 Routing task to roles: {task}")
        
        # Classify task complexity / 分类任务复杂度
        complexity = self.classify_task_complexity(task, task_type)
        logger.info(f"📊 Task complexity: {complexity}")
        
        # Get role sequence / 获取角色序列
        role_sequence = self.get_role_sequence_for_task_type(task_type, complexity)
        logger.info(f"👥 Role sequence: {role_sequence}")
        
        # Validate role sequence / 验证角色序列
        if not self.validate_role_sequence(role_sequence):
            logger.warning(f"⚠️ Invalid role sequence: {role_sequence}, falling back to ['executor']")
            role_sequence = ["executor"]
        
        # Get handoff points / 获取交接点
        handoff_points = self.get_handoff_points(role_sequence)
        logger.info(f"🔗 Handoff points: {len(handoff_points)}")
        
        routing_decision = {
            "task": task,
            "task_type": task_type,
            "complexity": complexity,
            "role_sequence": role_sequence,
            "handoff_points": handoff_points,
            "routing_reason": f"Task classified as {complexity} complexity for {task_type}",
            "fallback_sequence": ["executor"]  # Simple fallback / 简单回退序列
        }
        
        logger.info(f"✅ Routing decision completed for task type: {task_type}")
        return routing_decision

def main():
    """
    Test the role router with sample tasks.
    使用示例任务测试角色路由器。
    
    This demonstrates how the role router determines optimal role sequences
    based on task type and complexity.
    这演示了角色路由器如何基于任务类型和复杂度确定最优角色序列。
    """
    router = RoleRouter()
    
    # Test tasks / 测试任务
    test_tasks = [
        # Simple task / 简单任务
        ("Fix a simple typo in the README file", "documentation"),
        # Complex task / 复杂任务  
        ("Debug a complex production issue in the payment system with multiple components", "debugging"),
        # Medium task / 中等任务
        ("Plan and implement a new user authentication feature with basic requirements", "development")
    ]
    
    for task, task_type in test_tasks:
        print(f"\n{'='*60}")
        print(f"Test Task / 测试任务: {task}")
        print(f"Task Type / 任务类型: {task_type}")
        print(f"{'='*60}\n")
        
        # Route task / 路由任务
        routing = router.route_task_to_roles(task, task_type)
        
        # Display results / 显示结果
        print(f"Complexity / 复杂度: {routing['complexity']}")
        print(f"Role Sequence / 角色序列: {' → '.join(routing['role_sequence'])}")
        print(f"Handoff Points / 交接点数量: {len(routing['handoff_points'])}")
        
        if routing['handoff_points']:
            print("\nHandoff Details / 交接点详情:")
            for i, handoff in enumerate(routing['handoff_points'], 1):
                print(f"  {i}. {handoff['from_role']} → {handoff['to_role']}")
                print(f"     Required fields: {', '.join(handoff['required_fields'])}")
        
        print(f"\nRouting Reason / 路由原因: {routing['routing_reason']}")

if __name__ == "__main__":
    main()