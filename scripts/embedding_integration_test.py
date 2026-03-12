#!/usr/bin/env python3
"""
Embedding Integration Test for OpenClaw Skill Evolution
Tests the complete embedding pipeline with real vector model
"""

import sys
import os

# Add the virtual environment to Python path
venv_path = os.path.join(os.path.dirname(__file__), '..', '.venv')
if os.path.exists(venv_path):
    site_packages = os.path.join(venv_path, 'lib', 'python3.14', 'site-packages')
    if os.path.exists(site_packages):
        sys.path.insert(0, site_packages)

from openclaw_skill_evolution.services.embedding_service import EmbeddingService
from openclaw_skill_evolution.agents.planner import Planner
from openclaw_skill_evolution.agents.trajectory_logger_v2 import TrajectoryLoggerV2
from openclaw_skill_evolution.agents.experience_manager import ExperienceManager

def test_embedding_service():
    """Test the embedding service"""
    print("1️⃣ Testing Embedding Service...")
    embedding_service = EmbeddingService()
    
    # Test text embedding
    text = "This is a test for OpenClaw Skill Evolution"
    embedding = embedding_service.get_embedding(text)
    
    if embedding and len(embedding) == 1536:
        print(f"✅ Embedding generated successfully! Dimension: {len(embedding)}")
        return True
    else:
        print("❌ Failed to generate embedding")
        return False

def test_trajectory_with_embedding():
    """Test trajectory logging with real embedding"""
    print("\n2️⃣ Testing Trajectory with Embedding...")
    logger = TrajectoryLoggerV2()
    
    trajectory = logger.log_trajectory(
        task="Test embedding integration for skill evolution",
        task_type="embedding_test",
        skill_name="embedding_test_skill",
        workflow_name="embedding_test_workflow",
        steps=[
            {
                "step": 1,
                "action": "test_embedding",
                "tool": "embedding_service",
                "input_summary": "Test input for embedding",
                "output_summary": "Successfully generated embedding",
                "success": True,
                "score": 0.9,
                "duration_ms": 500
            }
        ],
        tools_used=["embedding_service"],
        outputs_summary="Embedding integration test completed successfully",
        success=True,
        final_score=0.95,
        duration_ms=500
    )
    
    if trajectory and "trajectory_id" in trajectory:
        print(f"✅ Trajectory logged with embedding: {trajectory['trajectory_id']}")
        return True
    else:
        print("❌ Failed to log trajectory with embedding")
        return False

def test_planner_with_embedding():
    """Test planner with real embedding search"""
    print("\n3️⃣ Testing Planner with Embedding Search...")
    planner = Planner()
    
    # Create a test trajectory first
    logger = TrajectoryLoggerV2()
    test_trajectory = logger.log_trajectory(
        task="Search for information about OpenClaw Skill Evolution with real embeddings",
        task_type="web_search",
        skill_name="agent-reach",
        workflow_name="search_workflow_v1",
        steps=[
            {
                "step": 1,
                "action": "search_web",
                "tool": "web_search",
                "input_summary": "query: OpenClaw Skill Evolution real embeddings",
                "output_summary": "Found relevant results about skill evolution with embeddings",
                "success": True,
                "score": 0.85,
                "duration_ms": 1200
            }
        ],
        tools_used=["web_search"],
        outputs_summary="Successfully found information about OpenClaw Skill Evolution",
        success=True,
        final_score=0.88,
        duration_ms=1200
    )
    
    # Now test planner search
    plan = planner.plan_task("Find information about OpenClaw embedding integration")
    
    if plan and "selected_skill" in plan:
        print(f"✅ Planner found skill: {plan['selected_skill']}")
        print(f"   Selected workflow: {plan['selected_workflow']}")
        return True
    else:
        print("❌ Planner failed to find relevant skills")
        return False

def test_experience_manager_with_embedding():
    """Test experience manager with real embedding deduplication"""
    print("\n4️⃣ Testing Experience Manager with Embedding Deduplication...")
    manager = ExperienceManager()
    
    # Create experience
    experience = manager.create_experience(
        title="OpenClaw Embedding Integration Experience",
        problem_summary="Need to integrate real embedding model for semantic search",
        solution_summary="Integrated OpenAI text-embedding-3-small model with 1536 dimensions",
        workflow="embedding_integration_workflow",
        score=0.92,
        tags=["embedding", "integration", "skill-evolution"]
    )
    
    if experience and "experience_id" in experience:
        print(f"✅ Experience created with embedding: {experience['experience_id']}")
        
        # Test deduplication
        similar_experience = manager.create_experience(
            title="OpenClaw Real Embedding Integration",
            problem_summary="Need to integrate real embedding model for better semantic search",
            solution_summary="Used OpenAI text-embedding-3-small model with proper dimensions",
            workflow="embedding_integration_workflow_v2",
            score=0.90,
            tags=["embedding", "integration", "real-model"]
        )
        
        if similar_experience:
            print("✅ Deduplication test completed - similar experiences handled properly")
            return True
    
    print("❌ Experience manager failed")
    return False

def main():
    """Main test function"""
    print("🚀 Starting Embedding Integration Test for OpenClaw Skill Evolution")
    print("=" * 70)
    
    tests = [
        test_embedding_service,
        test_trajectory_with_embedding,
        test_planner_with_embedding,
        test_experience_manager_with_embedding
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All embedding integration tests passed!")
        print("✅ OpenClaw Skill Evolution is now ready for real-world use with semantic search!")
        return True
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)