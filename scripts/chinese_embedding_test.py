#!/usr/bin/env python3
"""
Chinese Embedding Integration Test for OpenClaw Skill Evolution
Tests the BAAI/bge-small-zh-v1.5 model with Chinese text
"""

import sys
import os

# Add the virtual environment to Python path
venv_path = os.path.join(os.path.dirname(__file__), '..', '.venv')
if os.path.exists(venv_path):
    site_packages = os.path.join(venv_path, 'lib', 'python3.14', 'site-packages')
    if os.path.exists(site_packages):
        sys.path.insert(0, site_packages)

from openclaw_skill_evolution.utils.embedding_service import EmbeddingService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Test Chinese embedding integration"""
    logger.info("🚀 Starting Chinese Embedding Integration Test")
    
    # Initialize embedding service
    embedding_service = EmbeddingService()
    
    # Test Chinese texts
    test_texts = [
        "实现一个支付功能",
        "优化客服系统性能", 
        "分析股票交易数据",
        "调试复杂的代码问题",
        "部署新的机器学习模型"
    ]
    
    logger.info("📝 Testing Chinese text embeddings...")
    
    # Generate embeddings
    embeddings = []
    for text in test_texts:
        embedding = embedding_service.get_embedding(text)
        embeddings.append(embedding)
        logger.info(f"✅ Generated embedding for: '{text}' (dimension: {len(embedding)})")
    
    # Test similarity
    logger.info("🔍 Testing semantic similarity...")
    
    # Similar texts should have high similarity
    text1 = "实现支付功能"
    text2 = "开发支付系统"
    text3 = "优化数据库查询"
    
    emb1 = embedding_service.get_embedding(text1)
    emb2 = embedding_service.get_embedding(text2) 
    emb3 = embedding_service.get_embedding(text3)
    
    # Calculate cosine similarity
    def cosine_similarity(a, b):
        import numpy as np
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    sim_1_2 = cosine_similarity(emb1, emb2)
    sim_1_3 = cosine_similarity(emb1, emb3)
    
    logger.info(f"📊 Similarity between '{text1}' and '{text2}': {sim_1_2:.4f}")
    logger.info(f"📊 Similarity between '{text1}' and '{text3}': {sim_1_3:.4f}")
    
    # Verify that similar texts have higher similarity
    if sim_1_2 > sim_1_3:
        logger.info("✅ Semantic similarity test PASSED!")
    else:
        logger.error("❌ Semantic similarity test FAILED!")
        return False
    
    # Test Qdrant integration
    logger.info("📦 Testing Qdrant integration...")
    
    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct
    
    client = QdrantClient(host="localhost", port=6333)
    
    # Create test point
    test_point = PointStruct(
        id="chinese_test_1",
        vector=embeddings[0],
        payload={
            "text": test_texts[0],
            "language": "zh",
            "test": True
        }
    )
    
    # Upsert to Qdrant
    client.upsert(
        collection_name="trajectories",
        points=[test_point]
    )
    
    # Search similar
    search_results = client.query_points(
        collection_name="trajectories",
        query=embeddings[0],
        limit=1
    )
    
    if len(search_results.points) > 0:
        logger.info("✅ Qdrant integration test PASSED!")
    else:
        logger.error("❌ Qdrant integration test FAILED!")
        return False
    
    logger.info("🎉 Chinese Embedding Integration Test COMPLETED SUCCESSFULLY!")
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)