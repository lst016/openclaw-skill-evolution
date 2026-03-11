#!/usr/bin/env python3
"""
Test Qdrant API calls to understand the correct usage
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

def test_qdrant():
    client = QdrantClient(host="localhost", port=6333)
    
    # Test query_points
    result = client.query_points(
        collection_name="skills",
        query=[0.1] * 1536,
        limit=3
    )
    
    print(f"Result type: {type(result)}")
    print(f"Points: {len(result.points)}")
    
    for point in result.points:
        print(f"Point ID: {point.id}")
        print(f"Score: {point.score}")
        print(f"Payload keys: {list(point.payload.keys()) if point.payload else 'None'}")
        break

if __name__ == "__main__":
    test_qdrant()