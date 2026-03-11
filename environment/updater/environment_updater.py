#!/usr/bin/env python3
"""
Environment Updater for OpenClaw Skill Evolution v5
Updates the environment model based on execution results and changes.

环境更新器 - 基于执行结果和环境变化更新环境模型

Author: 牛牛 🐮
Version: v5.0
"""

import sys
import os
import json
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

class EnvironmentUpdater:
    """
    Environment Updater - Updates environment model based on changes.
    
    环境更新器 - 根据环境变化更新环境模型。
    
    This class handles:
    - Updating environment snapshots after task execution
    - Processing environment events and updating the graph
    - Maintaining consistency between environment state and reality
    - Triggering policy updates when environment changes significantly
    
    该类处理：
    - 任务执行后更新环境快照
    - 处理环境事件并更新依赖图
    - 维护环境状态与实际情况的一致性
    - 当环境发生重大变化时触发策略更新
    """
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        """
        Initialize Environment Updater.
        
        初始化环境更新器。
        
        Args:
            workspace_path (str): Path to the OpenClaw workspace
                                OpenClaw 工作区路径
        """
        self.workspace_path = workspace_path
        self.environment_dir = os.path.join(workspace_path, "environment")
        self.qdrant_client = QdrantClient(host="localhost", port=6333)
        
        # Ensure environment directory exists
        os.makedirs(self.environment_dir, exist_ok=True)
        logger.info("🔄 Initialized Environment Updater")
    
    def update_environment_snapshot(self, 
                                 snapshot_data: Dict[str, Any], 
                                 task_id: Optional[str] = None) -> bool:
        """
        Update environment snapshot after task execution.
        
        任务执行后更新环境快照。
        
        Args:
            snapshot_data (Dict[str, Any]): New environment snapshot data
                                          新的环境快照数据
            task_id (Optional[str]): ID of the task that caused the change
                                   导致变化的任务ID
            
        Returns:
            bool: True if update successful, False otherwise
                  更新成功返回True，否则返回False
        """
        try:
            logger.info("🔄 Updating environment snapshot")
            
            # Get current timestamp
            timestamp = datetime.now().isoformat()
            
            # Add metadata
            snapshot_data["updated_at"] = timestamp
            snapshot_data["last_updated_by_task"] = task_id
            snapshot_data["version"] = snapshot_data.get("version", 0) + 1
            
            # Save to file
            snapshot_file = os.path.join(self.environment_dir, "current_snapshot.json")
            with open(snapshot_file, 'w', encoding='utf-8') as f:
                json.dump(snapshot_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Environment snapshot updated: {snapshot_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update environment snapshot: {e}")
            return False
    
    def process_environment_event(self, event: Dict[str, Any]) -> bool:
        """
        Process an environment event and update the environment model.
        
        处理环境事件并更新环境模型。
        
        Args:
            event (Dict[str, Any]): Environment event data
                                  环境事件数据
            
        Returns:
            bool: True if processing successful, False otherwise
                  处理成功返回True，否则返回False
        """
        try:
            logger.info(f"🔄 Processing environment event: {event.get('event_type', 'unknown')}")
            
            # Validate event structure
            required_fields = ["event_id", "event_type", "target", "change_summary", "timestamp"]
            if not all(field in event for field in required_fields):
                logger.error("❌ Invalid environment event structure")
                return False
            
            # Save event to file
            events_dir = os.path.join(self.environment_dir, "events")
            os.makedirs(events_dir, exist_ok=True)
            
            event_file = os.path.join(events_dir, f"{event['event_id']}.json")
            with open(event_file, 'w', encoding='utf-8') as f:
                json.dump(event, f, indent=2, ensure_ascii=False)
            
            # Update Qdrant environment_events collection
            self._save_event_to_qdrant(event)
            
            # Update environment graph if needed
            if event.get("affects_dependencies", False):
                self._update_environment_graph_from_event(event)
            
            logger.info(f"✅ Environment event processed: {event['event_id']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to process environment event: {e}")
            return False
    
    def _save_event_to_qdrant(self, event: Dict[str, Any]) -> bool:
        """
        Save environment event to Qdrant vector database.
        
        将环境事件保存到Qdrant向量数据库。
        
        Args:
            event (Dict[str, Any]): Environment event data
                                  环境事件数据
            
        Returns:
            bool: True if save successful, False otherwise
                  保存成功返回True，否则返回False
        """
        try:
            # Create embedding content from change summary
            embedding_content = event.get("change_summary", "")
            
            # For now, use placeholder embedding
            # In production, this would be generated by an embedding model
            placeholder_embedding = [0.1] * 1536
            
            # Create point for Qdrant
            point = PointStruct(
                id=event["event_id"],
                vector=placeholder_embedding,
                payload={
                    "event_id": event["event_id"],
                    "node_id": event.get("node_id"),
                    "event_type": event["event_type"],
                    "target": event["target"],
                    "change_summary": event["change_summary"],
                    "timestamp": event["timestamp"],
                    "task_id": event.get("task_id"),
                    "affects_dependencies": event.get("affects_dependencies", False)
                }
            )
            
            # Upsert to Qdrant
            self.qdrant_client.upsert(
                collection_name="environment_events",
                points=[point]
            )
            
            logger.info(f"✅ Environment event saved to Qdrant: {event['event_id']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save environment event to Qdrant: {e}")
            return False
    
    def _update_environment_graph_from_event(self, event: Dict[str, Any]) -> bool:
        """
        Update environment graph based on environment event.
        
        基于环境事件更新环境依赖图。
        
        Args:
            event (Dict[str, Any]): Environment event data
                                  环境事件数据
            
        Returns:
            bool: True if update successful, False otherwise
                  更新成功返回True，否则返回False
        """
        try:
            logger.info("🔄 Updating environment graph from event")
            
            # This would typically involve:
            # 1. Loading current environment graph
            # 2. Analyzing the event's impact on dependencies
            # 3. Updating the graph structure
            # 4. Saving the updated graph
            
            graph_file = os.path.join(self.environment_dir, "environment_graph.json")
            
            # Load existing graph or create new one
            if os.path.exists(graph_file):
                with open(graph_file, 'r', encoding='utf-8') as f:
                    graph_data = json.load(f)
            else:
                graph_data = {
                    "nodes": {},
                    "edges": [],
                    "last_updated": datetime.now().isoformat(),
                    "version": 1
                }
            
            # Update graph based on event type
            event_type = event["event_type"]
            target = event["target"]
            
            if event_type == "file_created":
                # Add new node to graph
                if target not in graph_data["nodes"]:
                    graph_data["nodes"][target] = {
                        "type": "file",
                        "name": target,
                        "created_at": event["timestamp"],
                        "last_modified": event["timestamp"]
                    }
            elif event_type == "file_modified":
                # Update existing node
                if target in graph_data["nodes"]:
                    graph_data["nodes"][target]["last_modified"] = event["timestamp"]
            elif event_type == "service_added":
                # Add service node and potential dependencies
                if target not in graph_data["nodes"]:
                    graph_data["nodes"][target] = {
                        "type": "service",
                        "name": target,
                        "added_at": event["timestamp"]
                    }
            
            # Update graph metadata
            graph_data["last_updated"] = datetime.now().isoformat()
            graph_data["version"] = graph_data.get("version", 1) + 1
            
            # Save updated graph
            with open(graph_file, 'w', encoding='utf-8') as f:
                json.dump(graph_data, f, indent=2, ensure_ascii=False)
            
            logger.info("✅ Environment graph updated from event")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update environment graph from event: {e}")
            return False
    
    def trigger_policy_update_for_environment_change(self, 
                                                   change_type: str, 
                                                   affected_components: List[str]) -> bool:
        """
        Trigger policy updates when environment changes significantly.
        
        当环境发生重大变化时触发策略更新。
        
        Args:
            change_type (str): Type of environment change
                             环境变化类型
            affected_components (List[str]): List of affected components
                                           受影响的组件列表
            
        Returns:
            bool: True if policy update triggered successfully, False otherwise
                  策略更新触发成功返回True，否则返回False
        """
        try:
            logger.info(f"🔄 Triggering policy update for environment change: {change_type}")
            
            # Determine which policies need updating
            policies_to_update = []
            
            if change_type == "new_service":
                policies_to_update.extend(["skill_policy", "workflow_policy", "role_policy"])
            elif change_type == "db_schema_change":
                policies_to_update.extend(["workflow_policy", "tool_policy"])
            elif change_type == "api_change":
                policies_to_update.extend(["skill_policy", "collaboration_policy"])
            
            # Save policy update request
            policy_updates_dir = os.path.join(self.workspace_path, "policies", "updates")
            os.makedirs(policy_updates_dir, exist_ok=True)
            
            update_request = {
                "request_id": f"env_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "change_type": change_type,
                "affected_components": affected_components,
                "policies_to_update": policies_to_update,
                "timestamp": datetime.now().isoformat(),
                "status": "pending"
            }
            
            update_file = os.path.join(policy_updates_dir, f"{update_request['request_id']}.json")
            with open(update_file, 'w', encoding='utf-8') as f:
                json.dump(update_request, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Policy update triggered for environment change: {change_type}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to trigger policy update for environment change: {e}")
            return False

def main():
    """Test the Environment Updater."""
    updater = EnvironmentUpdater()
    
    # Test environment snapshot update
    test_snapshot = {
        "project_structure": {
            "files": ["main.py", "utils.py", "config.json"],
            "directories": ["src", "tests", "docs"]
        },
        "services": ["api", "database", "cache"],
        "tools": ["git", "docker", "python"],
        "version": 1
    }
    
    success = updater.update_environment_snapshot(test_snapshot, "test_task_123")
    print(f"Snapshot update success: {success}")
    
    # Test environment event processing
    test_event = {
        "event_id": "evt_12345",
        "event_type": "file_created",
        "target": "new_feature.py",
        "change_summary": "Created new feature implementation file",
        "timestamp": datetime.now().isoformat(),
        "task_id": "test_task_123",
        "affects_dependencies": False
    }
    
    success = updater.process_environment_event(test_event)
    print(f"Event processing success: {success}")

if __name__ == "__main__":
    main()