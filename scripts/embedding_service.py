#!/usr/bin/env python3
"""
Local Embedding Service for OpenClaw Skill Evolution
Uses BAAI/bge-small-zh-v1.5 for Chinese-optimized embeddings
"""

import sys
import os
import numpy as np
from typing import List, Union

# Add the virtual environment to Python path
venv_path = os.path.join(os.path.dirname(__file__), '..', '.venv')
if os.path.exists(venv_path):
    site_packages = os.path.join(venv_path, 'lib', 'python3.14', 'site-packages')
    if os.path.exists(site_packages):
        sys.path.insert(0, site_packages)

from sentence_transformers import SentenceTransformer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalEmbeddingService:
    """Local embedding service using BAAI/bge-small-zh-v1.5"""
    
    def __init__(self, model_name: str = "BAAI/bge-small-zh-v1.5"):
        """
        Initialize the local embedding service
        
        Args:
            model_name (str): HuggingFace model name
        """
        self.model_name = model_name
        self.model = None
        self.dimension = 384  # bge-small-zh-v1.5 dimension
        self._load_model()
    
    def _load_model(self):
        """Load the embedding model"""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"✅ Embedding model loaded successfully. Dimension: {self.dimension}")
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            raise
    
    def encode(self, texts: Union[str, List[str]], normalize_embeddings: bool = True) -> np.ndarray:
        """
        Generate embeddings for text(s)
        
        Args:
            texts: Single text or list of texts
            normalize_embeddings: Whether to normalize embeddings (recommended for cosine similarity)
            
        Returns:
            numpy array of embeddings
        """
        if self.model is None:
            raise ValueError("Model not loaded")
        
        try:
            embeddings = self.model.encode(
                texts, 
                normalize_embeddings=normalize_embeddings,
                show_progress_bar=False
            )
            return embeddings
        except Exception as e:
            logger.error(f"❌ Failed to generate embeddings: {e}")
            raise
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a single text
        
        Args:
            text: Input text
            
        Returns:
            List of floats representing the embedding
        """
        embedding = self.encode(text)
        return embedding.tolist()
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for multiple texts
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embeddings
        """
        embeddings = self.encode(texts)
        return embeddings.tolist()

# Global embedding service instance
_embedding_service = None

def get_embedding_service() -> LocalEmbeddingService:
    """Get the global embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = LocalEmbeddingService()
    return _embedding_service

def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for text using local model
    
    Args:
        text: Input text
        
    Returns:
        Embedding as list of floats
    """
    service = get_embedding_service()
    return service.get_embedding(text)

def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts
    
    Args:
        texts: List of input texts
        
    Returns:
        List of embeddings
    """
    service = get_embedding_service()
    return service.get_embeddings(texts)

def main():
    """Test the embedding service"""
    # Test with Chinese text
    test_texts = [
        "这是一个测试文本",
        "OpenClaw 技能进化系统",
        "多智能体协作框架"
    ]
    
    print("Testing local embedding service with Chinese text...")
    for text in test_texts:
        embedding = generate_embedding(text)
        print(f"Text: {text}")
        print(f"Embedding dimension: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")
        print("-" * 50)
    
    # Test batch processing
    print("\nTesting batch processing...")
    embeddings = generate_embeddings(test_texts)
    print(f"Generated {len(embeddings)} embeddings")
    print(f"Each embedding has {len(embeddings[0])} dimensions")

if __name__ == "__main__":
    main()