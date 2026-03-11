#!/usr/bin/env python3
"""
Knowledge Hub for OpenClaw Skill Evolution v6
Unified knowledge repository for all agents to share skills, workflows, experiences, and policies.

English: Centralized knowledge management system that enables knowledge sharing across all agents.
中文: 集中式知识管理系统，支持所有 Agent 之间的知识共享。
"""

import sys
import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
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

class KnowledgeHub:
    """
    Unified knowledge repository for multi-agent collaboration.
    
    English: Manages shared knowledge including skills, workflows, experiences, environment models, and policies.
    中文: 管理共享知识，包括技能、工作流、经验、环境模型和策略。
    """
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        """
        Initialize the Knowledge Hub.
        
        English: Initialize with workspace path and Qdrant connection for knowledge graph storage.
        中文: 使用工作区路径和 Qdrant 连接初始化知识图谱存储。
        """
        self.workspace_path = workspace_path
        self.knowledge_graph_dir = os.path.join(workspace_path, "knowledge", "graph")
        self.knowledge_cache_dir = os.path.join(workspace_path, "knowledge", "cache")
        
        # Ensure directories exist
        os.makedirs(self.knowledge_graph_dir, exist_ok=True)
        os.makedirs(self.knowledge_cache_dir, exist_ok=True)
        
        # Initialize Qdrant client for knowledge graph
        self.qdrant_client = QdrantClient(host="localhost", port=6333)
        
        logger.info("✅ Knowledge Hub initialized successfully")
        logger.info(f"   Knowledge graph: {self.knowledge_graph_dir}")
        logger.info(f"   Knowledge cache: {self.knowledge_cache_dir}")
        logger.info(f"   Qdrant connection: localhost:6333")
    
    def register_knowledge_entity(
        self,
        entity_type: str,
        entity_id: str,
        metadata: Dict[str, Any],
        relationships: List[Dict[str, Any]] = None
    ) -> bool:
        """
        Register a knowledge entity in the knowledge graph.
        
        English: Register entities like skills, workflows, agents, tasks with their metadata and relationships.
        中文: 注册技能、工作流、Agent、任务等实体及其元数据和关系。
        
        Args:
            entity_type (str): Type of entity (skill, workflow, agent, task, environment, policy)
            entity_id (str): Unique identifier for the entity
            metadata (Dict): Entity metadata including name, description, capabilities, etc.
            relationships (List[Dict]): List of relationships to other entities
            
        Returns:
            bool: True if registration successful, False otherwise
        """
        try:
            # Create knowledge entity
            knowledge_entity = {
                "entity_id": entity_id,
                "entity_type": entity_type,
                "metadata": metadata,
                "relationships": relationships or [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Save to local file
            entity_file = os.path.join(self.knowledge_graph_dir, f"{entity_type}_{entity_id}.json")
            with open(entity_file, 'w', encoding='utf-8') as f:
                json.dump(knowledge_entity, f, indent=2, ensure_ascii=False)
            
            # Create embedding content for vector search
            embedding_content = f"{metadata.get('name', '')} {metadata.get('description', '')} {entity_type}"
            
            # For now, use placeholder embedding (1536-dimensional)
            placeholder_embedding = [0.1] * 1536
            
            # Create point for Qdrant knowledge graph
            point = PointStruct(
                id=f"{entity_type}_{entity_id}",
                vector=placeholder_embedding,
                payload={
                    "entity_id": entity_id,
                    "entity_type": entity_type,
                    "metadata": str(metadata),  # Convert dict to string for storage
                    "relationships": str(relationships or []),
                    "created_at": knowledge_entity["created_at"],
                    "updated_at": knowledge_entity["updated_at"]
                }
            )
            
            # Upsert to Qdrant knowledge_graph collection
            self.qdrant_client.upsert(
                collection_name="knowledge_graph",
                points=[point]
            )
            
            logger.info(f"✅ Registered knowledge entity: {entity_type} - {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to register knowledge entity {entity_type} - {entity_id}: {e}")
            return False
    
    def search_knowledge_entities(
        self,
        query: str,
        entity_types: List[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for knowledge entities by query.
        
        English: Search knowledge graph for relevant entities based on semantic similarity.
        中文: 基于语义相似性在知识图谱中搜索相关实体。
        
        Args:
            query (str): Search query
            entity_types (List[str]): Filter by entity types (optional)
            limit (int): Maximum number of results to return
            
        Returns:
            List[Dict]: List of matching knowledge entities
        """
        try:
            # For now, use placeholder embedding for query
            placeholder_query_embedding = [0.1] * 1536
            
            # Query Qdrant knowledge graph
            search_results = self.qdrant_client.query_points(
                collection_name="knowledge_graph",
                query=placeholder_query_embedding,
                limit=limit
            )
            
            # Extract results
            entities = []
            for point in search_results.points:
                entity = {
                    "entity_id": point.payload["entity_id"],
                    "entity_type": point.payload["entity_type"],
                    "metadata": eval(point.payload["metadata"]),  # Convert string back to dict
                    "score": point.score if hasattr(point, 'score') else 1.0
                }
                
                # Filter by entity types if specified
                if entity_types is None or entity["entity_type"] in entity_types:
                    entities.append(entity)
            
            logger.info(f"🔍 Found {len(entities)} knowledge entities for query: {query}")
            return entities
            
        except Exception as e:
            logger.error(f"❌ Failed to search knowledge entities: {e}")
            return []
    
    def get_agent_capabilities(self, agent_id: str) -> Dict[str, Any]:
        """
        Get capabilities and skills of a specific agent.
        
        English: Retrieve detailed information about an agent's capabilities, skills, and performance metrics.
        中文: 获取特定 Agent 的能力、技能和性能指标的详细信息。
        
        Args:
            agent_id (str): Agent identifier
            
        Returns:
            Dict: Agent capabilities and metadata
        """
        try:
            # Search for agent in knowledge graph
            agents = self.search_knowledge_entities(
                query=f"agent {agent_id}",
                entity_types=["agent"],
                limit=1
            )
            
            if agents:
                return agents[0]["metadata"]
            else:
                logger.warning(f"⚠️ Agent not found in knowledge hub: {agent_id}")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Failed to get agent capabilities for {agent_id}: {e}")
            return {}
    
    def find_optimal_team_for_task(
        self,
        task_type: str,
        required_skills: List[str] = None
    ) -> List[str]:
        """
        Find the optimal team of agents for a given task type.
        
        English: Analyze task requirements and available agent capabilities to form the best team.
        中文: 分析任务需求和可用 Agent 能力，组建最佳团队。
        
        Args:
            task_type (str): Type of task to be executed
            required_skills (List[str]): Specific skills required for the task (optional)
            
        Returns:
            List[str]: List of agent IDs that form the optimal team
        """
        try:
            # Search for relevant teams in knowledge graph
            teams = self.search_knowledge_entities(
                query=f"team for {task_type}",
                entity_types=["team"],
                limit=5
            )
            
            if teams:
                # Return the first team's agent list
                optimal_team = teams[0]["metadata"].get("agents", [])
                logger.info(f"🎯 Found optimal team for {task_type}: {optimal_team}")
                return optimal_team
            
            # If no pre-defined teams, search for individual agents
            logger.info(f"🔍 No pre-defined teams found for {task_type}, searching individual agents...")
            
            # Search for agents with relevant capabilities
            relevant_agents = self.search_knowledge_entities(
                query=f"agent for {task_type}",
                entity_types=["agent"],
                limit=10
            )
            
            # Filter agents by required skills if specified
            if required_skills:
                qualified_agents = []
                for agent in relevant_agents:
                    agent_skills = agent["metadata"].get("skills", [])
                    if any(skill in agent_skills for skill in required_skills):
                        qualified_agents.append(agent["entity_id"])
                return qualified_agents[:4]  # Return top 4 qualified agents
            
            # Return top agents by relevance
            top_agents = [agent["entity_id"] for agent in relevant_agents[:4]]
            logger.info(f"🎯 Selected top agents for {task_type}: {top_agents}")
            return top_agents
            
        except Exception as e:
            logger.error(f"❌ Failed to find optimal team for {task_type}: {e}")
            return []
    
    def update_knowledge_entity(
        self,
        entity_type: str,
        entity_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update an existing knowledge entity.
        
        English: Update metadata and relationships of an existing knowledge entity.
        中文: 更新现有知识实体的元数据和关系。
        
        Args:
            entity_type (str): Type of entity to update
            entity_id (str): Entity identifier
            updates (Dict): Fields to update
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            # Load existing entity
            entity_file = os.path.join(self.knowledge_graph_dir, f"{entity_type}_{entity_id}.json")
            if not os.path.exists(entity_file):
                logger.error(f"❌ Knowledge entity not found: {entity_type}_{entity_id}")
                return False
            
            with open(entity_file, 'r', encoding='utf-8') as f:
                existing_entity = json.load(f)
            
            # Update metadata
            existing_entity["metadata"].update(updates)
            existing_entity["updated_at"] = datetime.now().isoformat()
            
            # Save updated entity
            with open(entity_file, 'w', encoding='utf-8') as f:
                json.dump(existing_entity, f, indent=2, ensure_ascii=False)
            
            # Update Qdrant record
            embedding_content = f"{existing_entity['metadata'].get('name', '')} {existing_entity['metadata'].get('description', '')} {entity_type}"
            placeholder_embedding = [0.1] * 1536
            
            point = PointStruct(
                id=f"{entity_type}_{entity_id}",
                vector=placeholder_embedding,
                payload={
                    "entity_id": entity_id,
                    "entity_type": entity_type,
                    "metadata": str(existing_entity["metadata"]),
                    "relationships": str(existing_entity["relationships"]),
                    "created_at": existing_entity["created_at"],
                    "updated_at": existing_entity["updated_at"]
                }
            )
            
            self.qdrant_client.upsert(
                collection_name="knowledge_graph",
                points=[point]
            )
            
            logger.info(f"✅ Updated knowledge entity: {entity_type} - {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update knowledge entity {entity_type} - {entity_id}: {e}")
            return False

def main():
    """Test the Knowledge Hub functionality."""
    logger.info("🚀 Testing Knowledge Hub...")
    
    # Initialize Knowledge Hub
    hub = KnowledgeHub()
    
    # Test registering a knowledge entity
    test_agent_metadata = {
        "name": "debug_agent",
        "role": "debugging",
        "skills": ["code_analysis", "error_diagnosis", "fix_implementation"],
        "success_rate": 0.87,
        "workload": "medium"
    }
    
    success = hub.register_knowledge_entity(
        entity_type="agent",
        entity_id="debug_agent_v1",
        metadata=test_agent_metadata,
        relationships=[
            {"type": "uses", "target": "code_analysis_skill"},
            {"type": "depends_on", "target": "environment_model"}
        ]
    )
    
    if success:
        logger.info("✅ Knowledge Hub test completed successfully!")
    else:
        logger.error("❌ Knowledge Hub test failed!")

if __name__ == "__main__":
    main()