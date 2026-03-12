#!/usr/bin/env python3
"""
Local Embedding Service for OpenClaw Skill Evolution
Uses BAAI/bge-small-zh-v1.5 model for Chinese-optimized embeddings
"""

import sys
import os
import logging
from typing import List, Union

# Add the virtual environment to Python path
venv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.venv')
if os.path.exists(venv_path):
    site_packages = os.path.join(venv_path, 'lib', 'python3.14', 'site-packages')
    if os.path.exists(site_packages):
        sys.path.insert(0, site_packages)

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    logging.error("sentence-transformers not installed. Please install with: pip install sentence-transformers")
    raise

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalEmbeddingService:
    """Local embedding service using BAAI/bge-small-zh-v1.5"""
    
    def __init__(self, model_name: str = "BAAI/bge-small-zh-v1.5"):
        """
        Initialize the local embedding service.
        
        Args:
            model_name (str): The model name to use. Default is "BAAI/bge-small-zh-v1.5"
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the embedding model."""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"✅ Embedding model loaded successfully: {self.model_name}")
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            raise
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text (str): Input text to embed
            
        Returns:
            List[float]: Embedding vector (384 dimensions for bge-small-zh-v1.5)
        """
        if not self.model:
            raise RuntimeError("Embedding model not loaded")
        
        try:
            embedding = self.model.encode(text, normalize_embeddings=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"❌ Failed to generate embedding: {e}")
            raise
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts (List[str]): List of input texts to embed
            
        Returns:
            List[List[float]]: List of embedding vectors
        """
        if not self.model:
            raise RuntimeError("Embedding model not loaded")
        
        try:
            embeddings = self.model.encode(texts, normalize_embeddings=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"❌ Failed to generate embeddings: {e}")
            raise

# Global embedding service instance
_embedding_service = None

def get_embedding_service() -> LocalEmbeddingService:
    """Get the global embedding service instance."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = LocalEmbeddingService()
    return _embedding_service

def embed_text(text: str) -> List[float]:
    """
    Generate embedding for a single text.
    
    Args:
        text (str): Input text to embed
        
    Returns:
        List[float]: Embedding vector
    """
    service = get_embedding_service()
    return service.embed_text(text)

def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts.
    
    Args:
        texts (List[str]): List of input texts to embed
        
    Returns:
        List[List[float]]: List of embedding vectors
    """
    service = get_embedding_service()
    return service.embed_texts(texts)

def main():
    """Test the embedding service."""
    # Test with Chinese text
    test_texts = [
        "这是一个测试文本",
        "OpenClaw 技能进化系统",
        "多智能体协作学习",
        "环境感知和长期任务"
    ]
    
    print("Testing local embedding service with Chinese text...")
    embeddings = embed_texts(test_texts)
    
    for i, (text, embedding) in enumerate(zip(test_texts, embeddings)):
        print(f"\nText {i+1}: {text}")
        print(f"Embedding dimensions: {len(embedding)}")
        print(f"First 5 dimensions: {embedding[:5]}")
    
    print("\n✅ Local embedding service test completed successfully!")

if __name__ == "__main__":
    main()