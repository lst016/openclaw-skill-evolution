#!/usr/bin/env python3
"""
Debug Qdrant API calls
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

def test_qdrant_calls():
    client = QdrantClient(host="localhost", port=6333)
    
    # Test skills collection
    print("Testing skills collection...")
    result = client.query_points(
        collection_name="skills",
        query=[0.1] * 1536,
        limit=1
    )
    print(f"Skills result type: {type(result)}")
    print(f"Has points attribute: {hasattr(result, 'points')}")
    if hasattr(result, 'points'):
        print(f"Number of points: {len(result.points)}")
        if result.points:
            print(f"First point payload: {result.points[0].payload}")
    
    # Test workflows collection  
    print("\nTesting workflows collection...")
    result = client.query_points(
        collection_name="workflows",
        query=[0.1] * 1536,
        limit=1
    )
    print(f"Workflows result type: {type(result)}")
    print(f"Has points attribute: {hasattr(result, 'points')}")
    if hasattr(result, 'points'):
        print(f"Number of points: {len(result.points)}")

if __name__ == "__main__":
    test_qdrant_calls()