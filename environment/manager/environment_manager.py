#!/usr/bin/env python3
"""
Environment Manager for OpenClaw Skill Evolution v5
环境管理器 - 维护系统当前环境的快照和状态

Purpose:
- Capture and maintain environment snapshots
- Track system structure (files, services, databases, APIs, tools)
- Provide environment context for task execution
- Update environment state after task execution

目标：
- 捕获和维护环境快照
- 跟踪系统结构（文件、服务、数据库、API、工具）
- 为任务执行提供环境上下文
- 任务执行后更新环境状态
"""

import sys
import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Add the virtual environment to Python path
venv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.venv')
if os.path.exists(venv_path):
    site_packages = os.path.join(venv_path, 'lib', 'python3.14', 'site-packages')
    if os.path.exists(site_packages):
        sys.path.insert(0, site_packages)

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnvironmentManager:
    """
    Environment Manager class for v5 Environment Learning Layer
    v5 环境学习层的环境管理器类
    """
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        """
        Initialize Environment Manager
        初始化环境管理器
        
        Args:
            workspace_path (str): Path to OpenClaw workspace
                                OpenClaw 工作区路径
        """
        self.workspace_path = workspace_path
        self.environment_dir = os.path.join(workspace_path, "environment")
        self.qdrant_client = QdrantClient(host="localhost", port=6333)
        
        # Ensure environment directory exists
        # 确保环境目录存在
        os.makedirs(self.environment_dir, exist_ok=True)
    
    def create_environment_snapshot_id(self) -> str:
        """
        Generate a unique environment snapshot ID
        生成唯一的环境快照 ID
        
        Returns:
            str: Unique snapshot ID
                 唯一快照 ID
        """
        timestamp = datetime.now().isoformat()
        hash_input = f"env_snapshot_{timestamp}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]
    
    def scan_project_structure(self, project_path: str) -> Dict[str, Any]:
        """
        Scan and analyze project structure
        扫描和分析项目结构
        
        Args:
            project_path (str): Path to project directory
                              项目目录路径
                              
        Returns:
            Dict[str, Any]: Project structure information
                           项目结构信息
        """
        logger.info(f"🔍 Scanning project structure: {project_path}")
        
        if not os.path.exists(project_path):
            logger.warning(f"⚠️ Project path does not exist: {project_path}")
            return {}
        
        structure = {
            "project_path": project_path,
            "files": [],
            "directories": [],
            "config_files": [],
            "source_files": [],
            "database_files": [],
            "api_files": []
        }
        
        try:
            for root, dirs, files in os.walk(project_path):
                # Skip hidden directories and node_modules
                # 跳过隐藏目录和 node_modules
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
                
                for file in files:
                    if file.startswith('.'):
                        continue
                    
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, project_path)
                    
                    structure["files"].append(relative_path)
                    
                    # Categorize files
                    # 文件分类
                    if file.endswith(('.json', '.yaml', '.yml', '.toml', '.ini')):
                        structure["config_files"].append(relative_path)
                    elif file.endswith(('.py', '.js', '.ts', '.java', '.go', '.rs')):
                        structure["source_files"].append(relative_path)
                    elif file.endswith(('.db', '.sqlite', '.sql')):
                        structure["database_files"].append(relative_path)
                    elif 'api' in file.lower() or 'route' in file.lower():
                        structure["api_files"].append(relative_path)
            
            # Get directories
            # 获取目录
            for root, dirs, _ in os.walk(project_path):
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    relative_path = os.path.relpath(dir_path, project_path)
                    structure["directories"].append(relative_path)
            
            logger.info(f"✅ Project structure scanned: {len(structure['files'])} files, {len(structure['directories'])} directories")
            
        except Exception as e:
            logger.error(f"❌ Failed to scan project structure: {e}")
        
        return structure
    
    def analyze_system_services(self) -> List[Dict[str, Any]]:
        """
        Analyze running system services
        分析运行中的系统服务
        
        Returns:
            List[Dict[str, Any]]: List of service information
                                 服务信息列表
        """
        logger.info("🔍 Analyzing system services")
        
        services = []
        
        # This is a placeholder - in production, you would use system-specific commands
        # 这是一个占位符 - 在生产环境中，你会使用系统特定的命令
        try:
            # Example: Check for common services
            # 示例：检查常见服务
            common_services = ["qdrant", "docker", "redis", "postgresql", "nginx"]
            
            for service in common_services:
                # In real implementation, check if service is running
                # 在实际实现中，检查服务是否正在运行
                services.append({
                    "service_name": service,
                    "status": "running",  # Placeholder
                    "port": None,         # Placeholder  
                    "version": None       # Placeholder
                })
            
            logger.info(f"✅ System services analyzed: {len(services)} services")
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze system services: {e}")
        
        return services
    
    def create_environment_snapshot(self, project_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a complete environment snapshot
        创建完整的环境快照
        
        Args:
            project_paths (Optional[List[str]]): List of project paths to include
                                               要包含的项目路径列表
                                               
        Returns:
            Dict[str, Any]: Complete environment snapshot
                           完整的环境快照
        """
        logger.info("📸 Creating environment snapshot")
        
        snapshot_id = self.create_environment_snapshot_id()
        created_at = datetime.now().isoformat()
        
        # Default project paths
        # 默认项目路径
        if project_paths is None:
            project_paths = ["/Users/lst01/.openclaw/workspace"]
        
        # Analyze projects
        # 分析项目
        projects = []
        for project_path in project_paths:
            project_structure = self.scan_project_structure(project_path)
            if project_structure:
                projects.append(project_structure)
        
        # Analyze system services
        # 分析系统服务
        services = self.analyze_system_services()
        
        # Create environment snapshot
        # 创建环境快照
        environment_snapshot = {
            "snapshot_id": snapshot_id,
            "created_at": created_at,
            "projects": projects,
            "services": services,
            "workspace_path": self.workspace_path,
            "version": "v5.0"
        }
        
        logger.info(f"✅ Environment snapshot created: {snapshot_id}")
        return environment_snapshot
    
    def save_environment_snapshot_to_file(self, snapshot: Dict[str, Any]) -> str:
        """
        Save environment snapshot to local file
        将环境快照保存到本地文件
        
        Args:
            snapshot (Dict[str, Any]): Environment snapshot to save
                                     要保存的环境快照
                                     
        Returns:
            str: Path to saved snapshot file
                 保存的快照文件路径
        """
        snapshot_file = os.path.join(self.environment_dir, f"snapshot_{snapshot['snapshot_id']}.json")
        
        with open(snapshot_file, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Saved environment snapshot to file: {snapshot_file}")
        return snapshot_file
    
    def save_environment_snapshot_to_qdrant(self, snapshot: Dict[str, Any]) -> bool:
        """
        Save environment snapshot to Qdrant vector database
        将环境快照保存到 Qdrant 向量数据库
        
        Args:
            snapshot (Dict[str, Any]): Environment snapshot to save
                                     要保存的环境快照
                                     
        Returns:
            bool: True if successful, False otherwise
                  成功返回 True，否则返回 False
        """
        try:
            # Create embedding content from snapshot
            # 从快照创建嵌入内容
            embedding_content = f"environment snapshot {snapshot['snapshot_id']} created at {snapshot['created_at']}"
            
            # For now, use placeholder embedding
            # 目前使用占位符嵌入
            placeholder_embedding = [0.1] * 1536
            
            # Create point for Qdrant
            # 为 Qdrant 创建点
            point = PointStruct(
                id=snapshot["snapshot_id"],
                vector=placeholder_embedding,
                payload={
                    "snapshot_id": snapshot["snapshot_id"],
                    "created_at": snapshot["created_at"],
                    "project_count": len(snapshot.get("projects", [])),
                    "service_count": len(snapshot.get("services", [])),
                    "workspace_path": snapshot["workspace_path"],
                    "version": snapshot["version"]
                }
            )
            
            # Upsert to Qdrant
            # 插入到 Qdrant
            self.qdrant_client.upsert(
                collection_name="environment_nodes",
                points=[point]
            )
            
            logger.info(f"✅ Saved environment snapshot to Qdrant: {snapshot['snapshot_id']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save environment snapshot to Qdrant: {e}")
            return False
    
    def load_latest_environment_snapshot(self) -> Optional[Dict[str, Any]]:
        """
        Load the latest environment snapshot
        加载最新的环境快照
        
        Returns:
            Optional[Dict[str, Any]]: Latest environment snapshot or None
                                    最新的环境快照或 None
        """
        try:
            # Search for latest snapshot in Qdrant
            # 在 Qdrant 中搜索最新快照
            search_result = self.qdrant_client.query_points(
                collection_name="environment_nodes",
                query=[0.1] * 1536,  # placeholder
                limit=1
            )
            
            if search_result.points:
                snapshot_id = search_result.points[0].id
                snapshot_file = os.path.join(self.environment_dir, f"snapshot_{snapshot_id}.json")
                
                if os.path.exists(snapshot_file):
                    with open(snapshot_file, 'r', encoding='utf-8') as f:
                        snapshot = json.load(f)
                    logger.info(f"✅ Loaded latest environment snapshot: {snapshot_id}")
                    return snapshot
                else:
                    logger.warning(f"⚠️ Snapshot file not found: {snapshot_file}")
                    return None
            else:
                logger.info("ℹ️ No environment snapshots found")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to load latest environment snapshot: {e}")
            return None
    
    def update_environment_after_task(self, task_result: Dict[str, Any], previous_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update environment after task execution
        任务执行后更新环境
        
        Args:
            task_result (Dict[str, Any]): Result of task execution
                                        任务执行结果
            previous_snapshot (Dict[str, Any]): Previous environment snapshot
                                              之前的环境快照
                                              
        Returns:
            Dict[str, Any]: Updated environment snapshot
                           更新后的环境快照
        """
        logger.info("🔄 Updating environment after task execution")
        
        # In a real implementation, this would analyze what changed
        # 在实际实现中，这会分析发生了什么变化
        # For now, we'll create a new snapshot
        # 目前，我们会创建一个新的快照
        
        updated_snapshot = self.create_environment_snapshot()
        updated_snapshot["previous_snapshot_id"] = previous_snapshot.get("snapshot_id")
        updated_snapshot["task_that_changed_environment"] = task_result.get("task_id")
        
        logger.info("✅ Environment updated after task execution")
        return updated_snapshot

def main():
    """Test the environment manager"""
    manager = EnvironmentManager()
    
    # Create environment snapshot
    snapshot = manager.create_environment_snapshot()
    
    # Save to file and Qdrant
    manager.save_environment_snapshot_to_file(snapshot)
    manager.save_environment_snapshot_to_qdrant(snapshot)
    
    # Load latest snapshot
    latest_snapshot = manager.load_latest_environment_snapshot()
    
    if latest_snapshot:
        print(f"Latest snapshot ID: {latest_snapshot['snapshot_id']}")
        print(f"Projects: {len(latest_snapshot.get('projects', []))}")
        print(f"Services: {len(latest_snapshot.get('services', []))}")

if __name__ == "__main__":
    main()