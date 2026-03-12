#!/usr/bin/env python3
"""
Embedding Service for OpenClaw Skill Evolution
Provides real embedding generation instead of placeholder vectors
"""

import sys
import os
import json
from typing import List, Union, Optional
import logging

# Add the virtual environment to Python path
venv_path = os.path.join(os.path.dirname(__file__), '..', '.venv')
if os.path.exists(venv_path):
    site_packages = os.path.join(venv_path, 'lib', 'python3.14', 'site-packages')
    if os.path.exists(site_packages):
        sys.path.insert(0, site_packages)

# Try to import OpenAI first
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI not available, falling back to sentence-transformers")

# Try to import sentence-transformers as fallback
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingService:
    """Generates embeddings for text content"""
    
    def __init__(self, model_name: str = "text-embedding-3-small"):
        self.model_name = model_name
        self.client = None
        self.local_model = None
        self._initialize_embedding_service()
    
    def _initialize_embedding_service(self):
        """Initialize the embedding service based on available libraries"""
        # First try OpenAI
        if OPENAI_AVAILABLE:
            try:
                # Try to get API key from environment or config
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    # Try to load from OpenClaw config
                    config_path = os.path.expanduser("~/.openclaw/config.json")
                    if os.path.exists(config_path):
                        with open(config_path, 'r') as f:
                            config = json.load(f)
                            api_key = config.get("openai", {}).get("apiKey")
                
                if api_key:
                    self.client = OpenAI(api_key=api_key)
                    logger.info(f"✅ Initialized OpenAI embedding service with model: {self.model_name}")
                    return
                else:
                    logger.warning("OpenAI API key not found, trying local models")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI: {e}")
        
        # Fallback to local sentence-transformers
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                # Use a lightweight local model
                local_model_name = "all-MiniLM-L6-v2"  # 384 dimensions, fast and good
                self.local_model = SentenceTransformer(local_model_name)
                logger.info(f"✅ Initialized local embedding service with model: {local_model_name}")
                return
            except Exception as e:
                logger.warning(f"Failed to initialize local model: {e}")
        
        # If nothing works, use placeholder
        logger.error("❌ No embedding service available, using placeholder vectors")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for given text"""
        if not text.strip():
            text = "empty"
        
        # Use OpenAI if available
        if self.client:
            try:
                response = self.client.embeddings.create(
                    input=text,
                    model=self.model_name
                )
                return response.data[0].embedding
            except Exception as e:
                logger.error(f"OpenAI embedding failed: {e}")
        
        # Use local model if available
        if self.local_model:
            try:
                embedding = self.local_model.encode(text).tolist()
                # Pad to 1536 dimensions if needed (for compatibility with existing Qdrant schema)
                if len(embedding) < 1536:
                    embedding.extend([0.0] * (1536 - len(embedding)))
                elif len(embedding) > 1536:
                    embedding = embedding[:1536]
                return embedding
            except Exception as e:
                logger.error(f"Local embedding failed: {e}")
        
        # Fallback to placeholder
        logger.warning("Using placeholder embedding")
        return [0.1] * 1536
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        return [self.generate_embedding(text) for text in texts]

# Global embedding service instance
_embedding_service = None

def get_embedding_service() -> EmbeddingService:
    """Get singleton embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service

def generate_embedding(text: str) -> List[float]:
    """Convenience function to generate embedding"""
    return get_embedding_service().generate_embedding(text)

def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Convenience function to generate multiple embeddings"""
    return get_embedding_service().generate_embeddings(texts)

def main():
    """Test the embedding service"""
    service = EmbeddingService()
    
    # Test embedding generation
    test_text = "This is a test sentence for embedding generation"
    embedding = service.generate_embedding(test_text)
    
    print(f"✅ Generated embedding with {len(embedding)} dimensions")
    print(f"Sample values: {embedding[:5]}...")

if __name__ == "__main__":
    main()