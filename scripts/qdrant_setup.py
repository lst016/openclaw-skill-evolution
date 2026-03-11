#!/usr/bin/env python3
"""
Qdrant Setup Script for OpenClaw Skill Evolution
Creates the required collections with proper schema
"""

import sys
import os

# Add the virtual environment to Python path
venv_path = os.path.join(os.path.dirname(__file__), '..', '.venv')
if os.path.exists(venv_path):
    site_packages = os.path.join(venv_path, 'lib', 'python3.14', 'site-packages')
    if os.path.exists(site_packages):
        sys.path.insert(0, site_packages)

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PayloadSchemaType
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_collection_schema(schema_file):
    """Load collection schema from JSON file"""
    with open(schema_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_collection(client, collection_name, schema_file):
    """Create a collection in Qdrant"""
    try:
        # Load schema
        schema = load_collection_schema(schema_file)
        
        # Create vector configuration - fix Distance enum
        distance_str = schema['vector_config']['distance']
        if distance_str == "Cosine":
            distance_enum = Distance.COSINE
        elif distance_str == "Dot":
            distance_enum = Distance.DOT
        elif distance_str == "Euclid":
            distance_enum = Distance.EUCLID
        else:
            distance_enum = Distance.COSINE
        
        vector_config = VectorParams(
            size=schema['vector_config']['size'],
            distance=distance_enum
        )
        
        # Create collection
        client.create_collection(
            collection_name=collection_name,
            vectors_config=vector_config
        )
        
        logger.info(f"✅ Created collection: {collection_name}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create collection {collection_name}: {e}")
        return False

def main():
    """Main function to setup Qdrant collections"""
    # Initialize Qdrant client
    client = QdrantClient(host="localhost", port=6333)
    
    # Verify connection
    try:
        info = client.get_collections()
        logger.info("✅ Connected to Qdrant successfully")
    except Exception as e:
        logger.error(f"❌ Failed to connect to Qdrant: {e}")
        return False
    
    # Collection definitions
    collections = [
        ("skills", "schemas/collections/skills.json"),
        ("workflows", "schemas/collections/workflows.json"), 
        ("experiences", "schemas/collections/experiences.json"),
        ("trajectories", "schemas/collections/trajectories.json")
    ]
    
    # Create collections
    success_count = 0
    for collection_name, schema_file in collections:
        schema_path = os.path.join(os.path.dirname(__file__), '..', schema_file)
        if create_collection(client, collection_name, schema_path):
            success_count += 1
    
    logger.info(f"🎯 Created {success_count}/{len(collections)} collections")
    
    # Verify collections exist
    collections_info = client.get_collections()
    existing_collections = [col.name for col in collections_info.collections]
    logger.info(f"📊 Existing collections: {existing_collections}")
    
    return success_count == len(collections)

if __name__ == "__main__":
    success = main()
    if success:
        print("🎉 Qdrant setup completed successfully!")
        sys.exit(0)
    else:
        print("💥 Qdrant setup failed!")
        sys.exit(1)