#!/usr/bin/env python3
"""
Agent Registry for OpenClaw Skill Evolution v6
Manages and tracks all agents in the organization system.

English: 
This module maintains a registry of all specialized agents in the system,
tracking their capabilities, performance metrics, and current workload.

中文注释:
代理注册表 - 管理和跟踪组织系统中的所有代理。
此模块维护系统中所有专业化代理的注册表，跟踪其能力、性能指标和当前工作负载。
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
from qdrant_client.models import PointStruct

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentRegistry:
    """
    Manages the registry of all agents in the organization.
    
    English: 
    Maintains a comprehensive registry of agents with their roles, 
    capabilities, performance metrics, and availability status.
    
    中文: 
    维护代理的综合注册表，包含其角色、能力、性能指标和可用性状态。
    """
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        """
        Initialize the Agent Registry.
        
        English: 
        Sets up the registry with Qdrant connection and workspace paths.
        
        中文: 
        使用 Qdrant 连接和工作区路径设置注册表。
        """
        self.workspace_path = workspace_path
        self.registry_dir = os.path.join(workspace_path, "organization", "registry")
        self.agents_file = os.path.join(self.registry_dir, "agents.json")
        self.qdrant_client = QdrantClient(host="localhost", port=6333)
        
        # Ensure registry directory exists
        os.makedirs(self.registry_dir, exist_ok=True)
        
        # Load existing agents or create empty registry
        self.agents = self._load_agents()
        
        logger.info("✅ Agent Registry initialized")
        logger.info(f"   Registry file: {self.agents_file}")
        logger.info(f"   Qdrant connection: localhost:6333")
        logger.info(f"   Registered agents: {len(self.agents)}")
    
    def _load_agents(self) -> Dict[str, Any]:
        """
        Load existing agents from file.
        
        English: 
        Loads agent registry from JSON file or returns empty dict if not exists.
        
        中文: 
        从 JSON 文件加载代理注册表，如果不存在则返回空字典。
        """
        if os.path.exists(self.agents_file):
            with open(self.agents_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_agents(self) -> None:
        """
        Save agents to file.
        
        English: 
        Persists the current agent registry to JSON file.
        
        中文: 
        将当前代理注册表持久化到 JSON 文件。
        """
        with open(self.agents_file, 'w', encoding='utf-8') as f:
            json.dump(self.agents, f, indent=2, ensure_ascii=False)
    
    def register_agent(
        self,
        agent_id: str,
        role: str,
        skills: List[str],
        capabilities: List[str],
        description: str = "",
        success_rate: float = 0.0,
        current_load: int = 0,
        max_load: int = 10
    ) -> Dict[str, Any]:
        """
        Register a new agent in the organization.
        
        English: 
        Adds a new specialized agent to the registry with its capabilities and metrics.
        
        中文: 
        将新的专业化代理添加到注册表中，包含其能力和指标。
        
        Args:
            agent_id (str): Unique identifier for the agent
            role (str): Primary role of the agent (e.g., "debug_agent", "coding_agent")
            skills (List[str]): List of skills the agent possesses
            capabilities (List[str]): List of capabilities the agent can perform
            description (str): Detailed description of the agent's purpose
            success_rate (float): Historical success rate (0.0 to 1.0)
            current_load (int): Current number of active tasks
            max_load (int): Maximum concurrent tasks the agent can handle
            
        Returns:
            Dict[str, Any]: The registered agent record
        """
        created_at = datetime.now().isoformat()
        
        agent_record = {
            "agent_id": agent_id,
            "role": role,
            "skills": skills,
            "capabilities": capabilities,
            "description": description,
            "success_rate": success_rate,
            "current_load": current_load,
            "max_load": max_load,
            "availability": "available" if current_load < max_load else "busy",
            "created_at": created_at,
            "updated_at": created_at,
            "metrics": {
                "total_tasks": 0,
                "completed_tasks": 0,
                "failed_tasks": 0,
                "avg_response_time": 0.0,
                "last_activity": created_at
            },
            "metadata": {
                "version": "v6.0",
                "source": "agent_registry",
                "tags": ["v6", "organization"]
            }
        }
        
        # Add to local registry
        self.agents[agent_id] = agent_record
        
        # Save to file
        self._save_agents()
        
        # Save to Qdrant
        self._save_agent_to_qdrant(agent_record)
        
        logger.info(f"✅ Registered agent: {agent_id}")
        logger.info(f"   Role: {role}")
        logger.info(f"   Skills: {len(skills)}")
        logger.info(f"   Capabilities: {len(capabilities)}")
        
        return agent_record
    
    def _save_agent_to_qdrant(self, agent_record: Dict[str, Any]) -> bool:
        """
        Save agent record to Qdrant vector database.
        
        English: 
        Stores the agent record in Qdrant for semantic search and retrieval.
        
        中文: 
        将代理记录存储在 Qdrant 中以进行语义搜索和检索。
        """
        try:
            # Create embedding content (role + description + skills + capabilities)
            embedding_content = f"{agent_record['role']} {agent_record['description']} {' '.join(agent_record['skills'])} {' '.join(agent_record['capabilities'])}"
            
            # For now, use placeholder embedding
            # In production, this would be generated by an embedding model
            placeholder_embedding = [0.1] * 1536
            
            # Create point for Qdrant
            point = PointStruct(
                id=agent_record["agent_id"],
                vector=placeholder_embedding,
                payload={
                    "agent_id": agent_record["agent_id"],
                    "role": agent_record["role"],
                    "skills": agent_record["skills"],
                    "capabilities": agent_record["capabilities"],
                    "description": agent_record["description"],
                    "success_rate": agent_record["success_rate"],
                    "current_load": agent_record["current_load"],
                    "max_load": agent_record["max_load"],
                    "availability": agent_record["availability"],
                    "created_at": agent_record["created_at"],
                    "updated_at": agent_record["updated_at"]
                }
            )
            
            # Upsert to Qdrant
            self.qdrant_client.upsert(
                collection_name="agents",
                points=[point]
            )
            
            logger.info(f"✅ Saved agent to Qdrant: {agent_record['agent_id']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save agent to Qdrant: {e}")
            return False
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an agent by ID.
        
        English: 
        Returns the agent record if found, None otherwise.
        
        中文: 
        如果找到则返回代理记录，否则返回 None。
        """
        return self.agents.get(agent_id)
    
    def find_best_agent_for_task(
        self,
        task_type: str,
        required_skills: List[str] = None,
        required_capabilities: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Find the best available agent for a given task.
        
        English: 
        Selects the most suitable agent based on skills, capabilities, 
        success rate, and current availability.
        
        中文: 
        根据技能、能力、成功率和当前可用性选择最合适的代理。
        """
        best_agent = None
        best_score = -1
        
        for agent_id, agent in self.agents.items():
            # Skip if agent is busy
            if agent["availability"] == "busy":
                continue
            
            # Calculate compatibility score
            score = 0
            
            # Role matching
            if task_type.lower() in agent["role"].lower():
                score += 0.5
            
            # Skills matching
            if required_skills:
                skill_matches = len(set(required_skills) & set(agent["skills"]))
                score += skill_matches * 0.3
            
            # Capabilities matching  
            if required_capabilities:
                cap_matches = len(set(required_capabilities) & set(agent["capabilities"]))
                score += cap_matches * 0.2
            
            # Success rate bonus
            score += agent["success_rate"] * 0.5
            
            # Prefer less loaded agents
            load_factor = 1.0 - (agent["current_load"] / agent["max_load"])
            score *= load_factor
            
            if score > best_score:
                best_score = score
                best_agent = agent
        
        if best_agent:
            logger.info(f"🎯 Found best agent for task '{task_type}': {best_agent['agent_id']} (score: {best_score:.2f})")
        
        return best_agent
    
    def update_agent_metrics(
        self,
        agent_id: str,
        success: bool = True,
        response_time: float = 0.0
    ) -> bool:
        """
        Update agent performance metrics.
        
        English: 
        Updates the agent's success rate, task counts, and response time metrics.
        
        中文: 
        更新代理的成功率、任务计数和响应时间指标。
        """
        if agent_id not in self.agents:
            logger.warning(f"⚠️ Agent {agent_id} not found in registry")
            return False
        
        agent = self.agents[agent_id]
        metrics = agent["metrics"]
        
        # Update task counts
        metrics["total_tasks"] += 1
        if success:
            metrics["completed_tasks"] += 1
        else:
            metrics["failed_tasks"] += 1
        
        # Update success rate
        if metrics["total_tasks"] > 0:
            agent["success_rate"] = metrics["completed_tasks"] / metrics["total_tasks"]
        
        # Update response time (exponential moving average)
        if metrics["total_tasks"] == 1:
            metrics["avg_response_time"] = response_time
        else:
            alpha = 0.1  # Smoothing factor
            metrics["avg_response_time"] = (
                alpha * response_time + 
                (1 - alpha) * metrics["avg_response_time"]
            )
        
        # Update last activity
        metrics["last_activity"] = datetime.now().isoformat()
        agent["updated_at"] = datetime.now().isoformat()
        
        # Update availability based on load
        if agent["current_load"] >= agent["max_load"]:
            agent["availability"] = "busy"
        else:
            agent["availability"] = "available"
        
        # Save updates
        self._save_agents()
        
        logger.info(f"📊 Updated metrics for agent {agent_id}: success_rate={agent['success_rate']:.2f}, load={agent['current_load']}/{agent['max_load']}")
        return True

def main():
    """Test the Agent Registry"""
    registry = AgentRegistry()
    
    # Test registering agents
    debug_agent = registry.register_agent(
        agent_id="debug_agent_001",
        role="debug_agent",
        skills=["code_analysis", "error_diagnosis", "fix_suggestion"],
        capabilities=["analyze_logs", "debug_code", "suggest_fixes"],
        description="Specialized agent for debugging and error analysis",
        success_rate=0.85
    )
    
    coding_agent = registry.register_agent(
        agent_id="coding_agent_001", 
        role="coding_agent",
        skills=["code_generation", "code_review", "refactoring"],
        capabilities=["write_code", "review_code", "optimize_code"],
        description="Specialized agent for code generation and review",
        success_rate=0.92
    )
    
    # Test finding best agent
    best_agent = registry.find_best_agent_for_task(
        task_type="debug",
        required_skills=["code_analysis", "error_diagnosis"]
    )
    
    print(f"Best agent for debug task: {best_agent['agent_id'] if best_agent else 'None'}")

if __name__ == "__main__":
    main()