#!/usr/bin/env python3
"""
State Tracker for OpenClaw Skill Evolution v5
Tracks and records environment changes and events.

环境状态追踪器 - 记录和追踪环境变化事件

Author: 牛牛 (Niuniu)
Version: v5.0
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

class StateTracker:
    """
    State Tracker for Environment Change Tracking
    环境状态追踪器 - 用于追踪环境变化
    
    This module records environment events such as:
    - File modifications
    - Database updates  
    - Service restarts
    - Configuration changes
    - API modifications
    
    该模块记录环境事件，例如：
    - 文件修改
    - 数据库更新
    - 服务重启
    - 配置变更
    - API 修改
    """
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        """
        Initialize State Tracker
        初始化状态追踪器
        
        Args:
            workspace_path (str): Path to OpenClaw workspace
                                OpenClaw 工作区路径
        """
        self.workspace_path = workspace_path
        self.events_log_dir = os.path.join(workspace_path, "logs", "environment_events")
        self.qdrant_client = QdrantClient(host="localhost", port=6333)
        
        # Ensure log directory exists
        os.makedirs(self.events_log_dir, exist_ok=True)
        
        logger.info("✅ State Tracker initialized successfully")
        logger.info(f"📁 Events log directory: {self.events_log_dir}")
        logger.info(f"📡 Qdrant connection: localhost:6333")
    
    def create_event_id(self) -> str:
        """
        Generate a unique event ID
        生成唯一的事件ID
        
        Returns:
            str: Unique event identifier
                 唯一事件标识符
        """
        return str(uuid.uuid4())
    
    def get_current_date_str(self) -> str:
        """
        Get current date in YYYY-MM-DD format
        获取当前日期（YYYY-MM-DD 格式）
        
        Returns:
            str: Current date string
                 当前日期字符串
        """
        return datetime.now().strftime("%Y-%m-%d")
    
    def get_date_log_dir(self) -> str:
        """
        Get the log directory for current date
        获取当前日期的日志目录
        
        Returns:
            str: Date-specific log directory path
                 日期特定的日志目录路径
        """
        date_str = self.get_current_date_str()
        date_log_dir = os.path.join(self.events_log_dir, date_str)
        os.makedirs(date_log_dir, exist_ok=True)
        return date_log_dir
    
    def create_environment_event(
        self,
        event_type: str,
        target: str,
        change_summary: str,
        source_task: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Create an environment event record
        创建环境事件记录
        
        Args:
            event_type (str): Type of environment event (e.g., 'file_modified', 'service_restarted')
                            环境事件类型（例如：'file_modified', 'service_restarted'）
            target (str): Target of the change (e.g., file path, service name)
                         变更目标（例如：文件路径、服务名称）
            change_summary (str): Summary of what changed
                                变更摘要
            source_task (str, optional): ID of the task that caused this change
                                       导致此变更的任务ID
            metadata (dict, optional): Additional metadata about the event
                                     事件的额外元数据
        
        Returns:
            dict: Environment event record
                  环境事件记录
        """
        event_id = self.create_event_id()
        timestamp = datetime.now().isoformat()
        
        event = {
            "event_id": event_id,
            "event_type": event_type,
            "target": target,
            "change_summary": change_summary,
            "timestamp": timestamp,
            "source_task": source_task,
            "metadata": metadata or {},
            "created_at": timestamp
        }
        
        logger.info(f"📝 Created environment event: {event_type} -> {target}")
        return event
    
    def validate_environment_event(self, event: Dict) -> bool:
        """
        Validate that an environment event has required fields
        验证环境事件是否包含必需字段
        
        Args:
            event (dict): Environment event to validate
                         要验证的环境事件
        
        Returns:
            bool: True if valid, False otherwise
                  如果有效返回True，否则返回False
        """
        required_fields = ["event_id", "event_type", "target", "change_summary", "timestamp"]
        return all(field in event for field in required_fields)
    
    def save_event_to_file(self, event: Dict) -> str:
        """
        Save environment event to local file
        将环境事件保存到本地文件
        
        Args:
            event (dict): Environment event to save
                         要保存的环境事件
        
        Returns:
            str: Path to the saved event file
                 保存的事件文件路径
        """
        date_log_dir = self.get_date_log_dir()
        event_file = os.path.join(date_log_dir, f"{event['event_id']}.json")
        
        with open(event_file, 'w', encoding='utf-8') as f:
            json.dump(event, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Saved environment event to file: {event_file}")
        return event_file
    
    def save_event_to_qdrant(self, event: Dict) -> bool:
        """
        Save environment event to Qdrant vector database
        将环境事件保存到Qdrant向量数据库
        
        Args:
            event (dict): Environment event to save
                         要保存的环境事件
        
        Returns:
            bool: True if successful, False otherwise
                  如果成功返回True，否则返回False
        """
        try:
            # Create embedding content from change summary
            # 从变更摘要创建嵌入内容
            embedding_content = event["change_summary"]
            
            # For now, use placeholder embedding
            # 目前使用占位符嵌入
            placeholder_embedding = [0.1] * 1536
            
            # Create point for Qdrant
            # 为Qdrant创建点
            point = PointStruct(
                id=event["event_id"],
                vector=placeholder_embedding,
                payload={
                    "event_id": event["event_id"],
                    "event_type": event["event_type"],
                    "target": event["target"],
                    "change_summary": event["change_summary"],
                    "timestamp": event["timestamp"],
                    "source_task": event["source_task"],
                    "metadata": str(event["metadata"]),  # Convert to string for storage
                    "created_at": event["created_at"]
                }
            )
            
            # Upsert to Qdrant
            # 更新到Qdrant
            self.qdrant_client.upsert(
                collection_name="environment_events",
                points=[point]
            )
            
            logger.info(f"✅ Saved environment event to Qdrant: {event['event_id']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save environment event to Qdrant: {e}")
            return False
    
    def record_environment_event(
        self,
        event_type: str,
        target: str,
        change_summary: str,
        source_task: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Complete environment event recording workflow
        完整的环境事件记录工作流
        
        Args:
            event_type (str): Type of environment event
                            环境事件类型
            target (str): Target of the change
                         变更目标
            change_summary (str): Summary of what changed
                                变更摘要
            source_task (str, optional): Source task ID
                                       源任务ID
            metadata (dict, optional): Additional metadata
                                     额外元数据
        
        Returns:
            dict: Recorded environment event
                  记录的环境事件
        """
        logger.info(f"🔍 Recording environment event: {event_type} on {target}")
        
        # Create environment event
        # 创建环境事件
        event = self.create_environment_event(
            event_type=event_type,
            target=target,
            change_summary=change_summary,
            source_task=source_task,
            metadata=metadata
        )
        
        # Validate event
        # 验证事件
        if not self.validate_environment_event(event):
            raise ValueError("Invalid environment event format")
        
        # Save to file
        # 保存到文件
        self.save_event_to_file(event)
        
        # Save to Qdrant
        # 保存到Qdrant
        self.save_event_to_qdrant(event)
        
        logger.info(f"🎯 Environment event recorded successfully: {event['event_id']}")
        return event
    
    def search_similar_events(self, change_summary: str, limit: int = 5) -> List[Dict]:
        """
        Search for similar environment events in Qdrant
        在Qdrant中搜索相似的环境事件
        
        Args:
            change_summary (str): Change summary to search for
                                要搜索的变更摘要
            limit (int): Maximum number of results to return
                        要返回的最大结果数
        
        Returns:
            list: List of similar environment events
                  相似的环境事件列表
        """
        try:
            # Create placeholder embedding
            # 创建占位符嵌入
            placeholder_embedding = [0.1] * 1536
            
            # Search in Qdrant
            # 在Qdrant中搜索
            search_result = self.qdrant_client.query_points(
                collection_name="environment_events",
                query=placeholder_embedding,
                limit=limit
            )
            
            similar_events = []
            for hit in search_result.points:
                similar_events.append(hit.payload)
            
            logger.info(f"🔍 Found {len(similar_events)} similar environment events")
            return similar_events
            
        except Exception as e:
            logger.error(f"❌ Failed to search similar environment events: {e}")
            return []

def main():
    """
    Test the State Tracker
    测试状态追踪器
    """
    tracker = StateTracker()
    
    # Test environment event
    # 测试环境事件
    test_event = tracker.record_environment_event(
        event_type="file_modified",
        target="/Users/lst01/.openclaw/workspace/skills/capability-evolver/SKILL.md",
        change_summary="Updated SKILL.md with new capability evolution features",
        source_task="capability_evolution_v5_development",
        metadata={
            "file_size_before": 2048,
            "file_size_after": 3072,
            "lines_added": 15,
            "lines_removed": 3
        }
    )
    
    print(f"Test environment event recorded: {test_event['event_id']}")
    print(f"Event type: {test_event['event_type']}")
    print(f"Target: {test_event['target']}")
    print(f"Change summary: {test_event['change_summary']}")

if __name__ == "__main__":
    main()