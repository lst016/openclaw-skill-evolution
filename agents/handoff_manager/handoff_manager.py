#!/usr/bin/env python3
"""
Handoff Manager for OpenClaw Skill Evolution v4
Manages handoffs between different roles in the collaboration workflow
"""

import sys
import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
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

class HandoffManager:
    """Manages handoffs between roles in the collaboration workflow"""
    
    def __init__(self, workspace_path: str = "/Users/lst01/.openclaw/workspace"):
        self.workspace_path = workspace_path
        self.handoffs_log_dir = os.path.join(workspace_path, "logs", "handoffs")
        self.qdrant_client = QdrantClient(host="localhost", port=6333)
        
        # Ensure log directory exists
        os.makedirs(self.handoffs_log_dir, exist_ok=True)
    
    def create_handoff_id(self) -> str:
        """Generate a unique handoff ID"""
        return str(uuid.uuid4())
    
    def get_current_date_str(self) -> str:
        """Get current date in YYYY-MM-DD format"""
        return datetime.now().strftime("%Y-%m-%d")
    
    def get_date_log_dir(self) -> str:
        """Get the log directory for current date"""
        date_str = self.get_current_date_str()
        date_log_dir = os.path.join(self.handoffs_log_dir, date_str)
        os.makedirs(date_log_dir, exist_ok=True)
        return date_log_dir
    
    def create_handoff_record(
        self,
        from_role: str,
        to_role: str,
        input_summary: str,
        output_summary: str,
        success: bool = True,
        delay_ms: int = 0,
        quality_score: float = 0.0,
        trajectory_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a handoff record"""
        handoff_id = self.create_handoff_id()
        created_at = datetime.now().isoformat()
        
        handoff = {
            "handoff_id": handoff_id,
            "from_role": from_role,
            "to_role": to_role,
            "input_summary": input_summary,
            "output_summary": output_summary,
            "success": success,
            "delay_ms": delay_ms,
            "quality_score": quality_score,
            "trajectory_id": trajectory_id,
            "created_at": created_at
        }
        
        return handoff
    
    def validate_handoff_structure(self, handoff_data: Dict) -> bool:
        """Validate that handoff data has required structure"""
        required_fields = ["from_role", "to_role", "input_summary", "output_summary"]
        return all(field in handoff_data for field in required_fields)
    
    def execute_handoff(
        self,
        from_role: str,
        to_role: str,
        handoff_data: Dict,
        trajectory_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a handoff between roles"""
        logger.info(f"🔄 Executing handoff from {from_role} to {to_role}")
        
        # Validate handoff structure
        if not self.validate_handoff_structure(handoff_data):
            raise ValueError("Invalid handoff data structure")
        
        # Create handoff record
        handoff = self.create_handoff_record(
            from_role=from_role,
            to_role=to_role,
            input_summary=handoff_data.get("input_summary", ""),
            output_summary=handoff_data.get("output_summary", ""),
            success=handoff_data.get("success", True),
            delay_ms=handoff_data.get("delay_ms", 0),
            quality_score=handoff_data.get("quality_score", 0.0),
            trajectory_id=trajectory_id
        )
        
        # Save to file
        self.save_handoff_to_file(handoff)
        
        # Save to Qdrant
        self.save_handoff_to_qdrant(handoff)
        
        logger.info(f"✅ Handoff completed: {handoff['handoff_id']}")
        return handoff
    
    def save_handoff_to_file(self, handoff: Dict) -> str:
        """Save handoff to local file"""
        date_log_dir = self.get_date_log_dir()
        handoff_file = os.path.join(date_log_dir, f"{handoff['handoff_id']}.json")
        
        with open(handoff_file, 'w', encoding='utf-8') as f:
            json.dump(handoff, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Saved handoff to file: {handoff_file}")
        return handoff_file
    
    def save_handoff_to_qdrant(self, handoff: Dict) -> bool:
        """Save handoff to Qdrant vector database"""
        try:
            # Create embedding content (from_role + to_role + input_summary)
            embedding_content = f"{handoff['from_role']} {handoff['to_role']} {handoff['input_summary']}"
            
            # For now, use placeholder embedding
            placeholder_embedding = [0.1] * 1536
            
            # Create point for Qdrant
            point = PointStruct(
                id=handoff["handoff_id"],
                vector=placeholder_embedding,
                payload={
                    "handoff_id": handoff["handoff_id"],
                    "from_role": handoff["from_role"],
                    "to_role": handoff["to_role"],
                    "input_summary": handoff["input_summary"],
                    "output_summary": handoff["output_summary"],
                    "success": handoff["success"],
                    "delay_ms": handoff["delay_ms"],
                    "quality_score": handoff["quality_score"],
                    "trajectory_id": handoff["trajectory_id"],
                    "created_at": handoff["created_at"]
                }
            )
            
            # Upsert to Qdrant
            self.qdrant_client.upsert(
                collection_name="handoffs",
                points=[point]
            )
            
            logger.info(f"✅ Saved handoff to Qdrant: {handoff['handoff_id']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save handoff to Qdrant: {e}")
            return False
    
    def analyze_handoff_quality(self, from_role: str, to_role: str) -> Dict[str, Any]:
        """Analyze handoff quality between two roles"""
        try:
            # Search for handoffs between these roles
            search_result = self.qdrant_client.query_points(
                collection_name="handoffs",
                query=[0.1] * 1536,  # placeholder embedding
                limit=100,
                query_filter={
                    "must": [
                        {"key": "from_role", "match": {"value": from_role}},
                        {"key": "to_role", "match": {"value": to_role}}
                    ]
                }
            )
            
            if not search_result.points:
                return {"success_rate": 0.0, "avg_quality": 0.0, "count": 0}
            
            handoffs = [hit.payload for hit in search_result.points]
            success_count = sum(1 for h in handoffs if h.get("success", False))
            total_quality = sum(h.get("quality_score", 0) for h in handoffs)
            
            success_rate = success_count / len(handoffs)
            avg_quality = total_quality / len(handoffs)
            
            return {
                "success_rate": success_rate,
                "avg_quality": avg_quality,
                "count": len(handoffs),
                "recent_handoffs": handoffs[-5:]  # Last 5 handoffs
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze handoff quality: {e}")
            return {"success_rate": 0.0, "avg_quality": 0.0, "count": 0}
    
    def get_problematic_handoffs(self, threshold: float = 0.5) -> List[Dict]:
        """Get handoffs with quality below threshold"""
        try:
            # This would require more complex querying, but for now we'll simulate
            # In production, you'd implement proper filtering and aggregation
            return []
            
        except Exception as e:
            logger.error(f"❌ Failed to get problematic handoffs: {e}")
            return []

def main():
    """Test the handoff manager"""
    manager = HandoffManager()
    
    # Test handoff
    test_handoff = manager.execute_handoff(
        from_role="planner",
        to_role="executor",
        handoff_data={
            "input_summary": "Generated execution plan for debugging task",
            "output_summary": "Plan received and ready for execution",
            "success": True,
            "delay_ms": 150,
            "quality_score": 0.85
        },
        trajectory_id="test-trajectory-123"
    )
    
    print(f"Test handoff created: {test_handoff['handoff_id']}")
    print(f"From: {test_handoff['from_role']} → To: {test_handoff['to_role']}")
    print(f"Quality score: {test_handoff['quality_score']}")

if __name__ == "__main__":
    main()