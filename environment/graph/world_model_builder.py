#!/usr/bin/env python3
"""
World Model Builder for OpenClaw Skill Evolution v5
构建环境依赖图，支持环境推理和影响分析

World Model Builder for OpenClaw Skill Evolution v5
Builds environment dependency graphs to support environment reasoning and impact analysis
"""

import sys
import os
import json
from typing import Dict, List, Any, Optional, Set, Tuple
import logging
from datetime import datetime

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

class WorldModelBuilder:
    """
    构建和维护环境世界模型
    
    Builds and maintains the environment world model
    """
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        """
        初始化世界模型构建器
        
        Initialize the world model builder
        
        Args:
            workspace_path (str): 工作空间路径 / Workspace path
        """
        self.workspace_path = workspace_path
        self.environment_graph_dir = os.path.join(workspace_path, "environment", "graph")
        self.qdrant_client = QdrantClient(host="localhost", port=6333)
        
        # Ensure graph directory exists
        os.makedirs(self.environment_graph_dir, exist_ok=True)
    
    def create_environment_node(
        self,
        node_id: str,
        node_type: str,
        name: str,
        description: str = "",
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        创建环境节点
        
        Create an environment node
        
        Args:
            node_id (str): 节点ID / Node ID
            node_type (str): 节点类型 (file, service, database, api, module, tool) / Node type
            name (str): 节点名称 / Node name
            description (str): 节点描述 / Node description
            metadata (Dict): 元数据 / Metadata
            
        Returns:
            Dict[str, Any]: 环境节点对象 / Environment node object
        """
        node = {
            "node_id": node_id,
            "node_type": node_type,
            "name": name,
            "description": description,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        return node
    
    def save_node_to_qdrant(self, node: Dict[str, Any]) -> bool:
        """
        保存节点到Qdrant
        
        Save node to Qdrant
        
        Args:
            node (Dict): 环境节点 / Environment node
            
        Returns:
            bool: 保存是否成功 / Whether save was successful
        """
        try:
            # Create embedding content
            embedding_content = f"{node['name']} {node['description']}"
            
            # For now, we'll use a placeholder embedding
            placeholder_embedding = [0.1] * 1536
            
            # Create point for Qdrant
            point = PointStruct(
                id=node["node_id"],
                vector=placeholder_embedding,
                payload={
                    "node_id": node["node_id"],
                    "node_type": node["node_type"],
                    "name": node["name"],
                    "description": node["description"],
                    "metadata": json.dumps(node["metadata"]),
                    "created_at": node["created_at"],
                    "updated_at": node["updated_at"]
                }
            )
            
            # Upsert to Qdrant
            self.qdrant_client.upsert(
                collection_name="environment_nodes",
                points=[point]
            )
            
            logger.info(f"✅ Saved environment node to Qdrant: {node['node_id']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save environment node to Qdrant: {e}")
            return False
    
    def build_dependency_graph(self, nodes: List[Dict], relationships: List[Tuple[str, str, str]]) -> Dict[str, Any]:
        """
        构建依赖图
        
        Build dependency graph
        
        Args:
            nodes (List[Dict]): 节点列表 / List of nodes
            relationships (List[Tuple]): 关系列表 (source, target, relationship_type) / List of relationships
            
        Returns:
            Dict[str, Any]: 依赖图对象 / Dependency graph object
        """
        graph = {
            "nodes": nodes,
            "relationships": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Process relationships
        for source_id, target_id, relationship_type in relationships:
            relationship = {
                "source": source_id,
                "target": target_id,
                "type": relationship_type,
                "created_at": datetime.now().isoformat()
            }
            graph["relationships"].append(relationship)
        
        return graph
    
    def save_graph_to_file(self, graph: Dict[str, Any], graph_name: str = "environment_graph") -> str:
        """
        保存图到文件
        
        Save graph to file
        
        Args:
            graph (Dict): 依赖图 / Dependency graph
            graph_name (str): 图名称 / Graph name
            
        Returns:
            str: 保存的文件路径 / Saved file path
        """
        graph_file = os.path.join(self.environment_graph_dir, f"{graph_name}.json")
        
        with open(graph_file, 'w', encoding='utf-8') as f:
            json.dump(graph, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Saved environment graph to file: {graph_file}")
        return graph_file
    
    def analyze_impact(self, changed_node_id: str, graph: Dict[str, Any]) -> List[str]:
        """
        分析影响范围
        
        Analyze impact scope
        
        Args:
            changed_node_id (str): 变更的节点ID / Changed node ID
            graph (Dict): 依赖图 / Dependency graph
            
        Returns:
            List[str]: 受影响的节点ID列表 / List of affected node IDs
        """
        affected_nodes = set()
        visited = set()
        
        def dfs(node_id: str):
            if node_id in visited:
                return
            visited.add(node_id)
            affected_nodes.add(node_id)
            
            # Find all nodes that depend on this node
            for relationship in graph["relationships"]:
                if relationship["source"] == node_id:
                    dfs(relationship["target"])
        
        dfs(changed_node_id)
        return list(affected_nodes)
    
    def update_environment_graph(self, new_nodes: List[Dict], new_relationships: List[Tuple[str, str, str]]) -> Dict[str, Any]:
        """
        更新环境图
        
        Update environment graph
        
        Args:
            new_nodes (List[Dict]): 新节点 / New nodes
            new_relationships (List[Tuple]): 新关系 / New relationships
            
        Returns:
            Dict[str, Any]: 更新后的环境图 / Updated environment graph
        """
        # Load existing graph if exists
        graph_file = os.path.join(self.environment_graph_dir, "environment_graph.json")
        if os.path.exists(graph_file):
            with open(graph_file, 'r', encoding='utf-8') as f:
                existing_graph = json.load(f)
        else:
            existing_graph = {
                "nodes": [],
                "relationships": [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        
        # Merge new nodes (avoid duplicates)
        existing_node_ids = {node["node_id"] for node in existing_graph["nodes"]}
        for node in new_nodes:
            if node["node_id"] not in existing_node_ids:
                existing_graph["nodes"].append(node)
                existing_node_ids.add(node["node_id"])
        
        # Merge new relationships (avoid duplicates)
        existing_relationships = {(r["source"], r["target"], r["type"]) for r in existing_graph["relationships"]}
        for source, target, rel_type in new_relationships:
            if (source, target, rel_type) not in existing_relationships:
                existing_graph["relationships"].append({
                    "source": source,
                    "target": target,
                    "type": rel_type,
                    "created_at": datetime.now().isoformat()
                })
                existing_relationships.add((source, target, rel_type))
        
        # Update timestamp
        existing_graph["updated_at"] = datetime.now().isoformat()
        
        # Save updated graph
        self.save_graph_to_file(existing_graph)
        
        logger.info(f"✅ Updated environment graph with {len(new_nodes)} nodes and {len(new_relationships)} relationships")
        return existing_graph

def main():
    """Test the world model builder"""
    builder = WorldModelBuilder()
    
    # Test nodes
    nodes = [
        builder.create_environment_node("service_a", "service", "Service A", "Main business service"),
        builder.create_environment_node("service_b", "service", "Service B", "Supporting service"),
        builder.create_environment_node("db_main", "database", "Main Database", "Primary database"),
        builder.create_environment_node("api_gateway", "api", "API Gateway", "External API entry point")
    ]
    
    # Test relationships
    relationships = [
        ("api_gateway", "service_a", "calls"),
        ("service_a", "service_b", "depends_on"),
        ("service_a", "db_main", "writes"),
        ("service_b", "db_main", "reads")
    ]
    
    # Build graph
    graph = builder.build_dependency_graph(nodes, relationships)
    builder.save_graph_to_file(graph)
    
    # Save nodes to Qdrant
    for node in nodes:
        builder.save_node_to_qdrant(node)
    
    # Test impact analysis
    affected = builder.analyze_impact("service_a", graph)
    print(f"Affected nodes when service_a changes: {affected}")
    
    print("World model builder test completed successfully!")

if __name__ == "__main__":
    main()