#!/usr/bin/env python3
"""
Local Embedding Service for OpenClaw Skill Evolution
Uses BAAI/bge-small-zh-v1.5 for Chinese-optimized embeddings
"""

import sys
import os
import json
from typing import List, Union
import logging

# Add the virtual environment to Python path
venv_path = os.path.join(os.path.dirname(__file__), '..', '.venv')
if os.path.exists(venv_path):
    site_packages = os.path.join(venv_path, 'lib', 'python3.14', 'site-packages')
    if os.path.exists(site_packages):
        sys.path.insert(0, site_packages)

from sentence_transformers import SentenceTransformer
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalEmbeddingService:
    """Local embedding service using BAAI/bge-small-zh-v1.5"""
    
    def __init__(self, model_name: str = "BAAI/bge-small-zh-v1.5"):
        """
        Initialize the local embedding service
        
        Args:
            model_name (str): Hugging Face model name
        """
        self.model_name = model_name
        self.model = None
        self.dimension = 384  # bge-small-zh-v1.5 outputs 384-dim vectors
        
        # Load model
        self._load_model()
        
    def _load_model(self):
        """Load the embedding model"""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"✅ Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            raise
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text (str): Input text
            
        Returns:
            List[float]: Embedding vector
        """
        if not isinstance(text, str):
            text = str(text)
            
        try:
            embedding = self.model.encode(text, normalize_embeddings=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"❌ Failed to generate embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * self.dimension
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts (List[str]): List of input texts
            
        Returns:
            List[List[float]]: List of embedding vectors
        """
        try:
            embeddings = self.model.encode(texts, normalize_embeddings=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"❌ Failed to generate embeddings: {e}")
            # Return zero vectors as fallback
            return [[0.0] * self.dimension for _ in texts]
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        return self.dimension

def main():
    """Test the embedding service"""
    # Test with Chinese text
    service = LocalEmbeddingService()
    
    test_texts = [
        "这是一个测试文本",
        "OpenClaw 技能进化系统",
        "多智能体协作学习"
    ]
    
    print("Testing local embedding service...")
    for text in test_texts:
        embedding = service.embed_text(text)
        print(f"Text: {text}")
        print(f"Embedding length: {len(embedding)}")
        print(f"First 5 dimensions: {embedding[:5]}")
        print("-" * 50)
    
    print("✅ Local embedding service test completed!")

if __name__ == "__main__":
    main()