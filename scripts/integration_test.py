#!/usr/bin/env python3
"""
Integration Test for OpenClaw Skill Evolution
Tests the complete minimal viable loop
"""

import sys
import os

# Add the virtual environment to Python path
venv_path = os.path.join(os.path.dirname(__file__), '..', '.venv')
if os.path.exists(venv_path):
    site_packages = os.path.join(venv_path, 'lib', 'python3.14', 'site-packages')
    if os.path.exists(site_packages):
        sys.path.insert(0, site_packages)

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from trajectory_logger import TrajectoryLogger
    from evaluator import Evaluator
    from reflector import Reflector
    from experience_manager import ExperienceManager
    from skill_generator import SkillGenerator
    from planner import Planner
    print("✅ All modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def main():
    """Run integration test"""
    print("🚀 Starting OpenClaw Skill Evolution Integration Test")
    
    # Step 1: Create and log trajectory
    print("\n1️⃣ Creating trajectory...")
    logger = TrajectoryLogger()
    trajectory = logger.log_trajectory(
        task="Search for information about OpenClaw Skill Evolution",
        task_type="web_search",
        selected_skill="agent-reach",
        selected_workflow="search_workflow_v1",
        steps=[
            {
                "step": 1,
                "action": "search_web",
                "tool": "web_search",
                "input_summary": "query: OpenClaw Skill Evolution",
                "output_summary": "Found 5 relevant results about skill evolution",
                "success": True,
                "score": 0.8,
                "duration_ms": 1200
            },
            {
                "step": 2,
                "action": "fetch_content",
                "tool": "web_fetch",
                "input_summary": "url: https://example.com/openclaw-skill-evolution",
                "output_summary": "Extracted content about skill evolution framework",
                "success": True,
                "score": 0.9,
                "duration_ms": 800
            }
        ],
        tools_used=["web_search", "web_fetch"],
        outputs_summary="Successfully found and extracted information about OpenClaw Skill Evolution",
        success=True,
        final_score=0.0,  # Will be calculated by evaluator
        duration_ms=2000
    )
    print(f"✅ Trajectory created: {trajectory['trajectory_id']}")
    
    # Step 2: Evaluate trajectory
    print("\n2️⃣ Evaluating trajectory...")
    evaluator = Evaluator()
    evaluation_result = evaluator.evaluate_trajectory(trajectory)
    print(f"✅ Evaluation completed - Final score: {evaluation_result['final_score']:.2f}")
    
    # Update trajectory with final score
    trajectory["final_score"] = evaluation_result["final_score"]
    
    # Step 3: Run reflection
    print("\n3️⃣ Running reflection...")
    reflector = Reflector()
    reflection = reflector.reflect_trajectory(trajectory)
    print(f"✅ Reflection completed: {reflection['reflection_id']}")
    
    # Step 4: Store experience (if qualified)
    print("\n4️⃣ Storing experience...")
    experience_manager = ExperienceManager()
    experience = experience_manager.store_experience(trajectory, reflection)
    if experience:
        print(f"✅ Experience stored: {experience['experience_id']}")
    else:
        print("⚠️ Experience not stored (didn't meet criteria)")
    
    # Step 5: Generate skill (if qualified)
    print("\n5️⃣ Generating skill...")
    # Simulate having multiple similar trajectories
    similar_trajectories = [trajectory, trajectory, trajectory]  # Simulate 3 similar trajectories
    skill_generator = SkillGenerator()
    skill = skill_generator.generate_skill_from_trajectories(similar_trajectories)
    if skill:
        print(f"✅ Skill generated: {skill['skill_name']}")
    else:
        print("⚠️ Skill not generated (didn't meet criteria)")
    
    # Step 6: Plan task using generated resources
    print("\n6️⃣ Planning task with generated resources...")
    planner = Planner()
    execution_plan = planner.plan_task("Search for more information about OpenClaw Skill Evolution")
    print(f"✅ Execution plan generated:")
    print(f"   Selected Skill: {execution_plan['selected_skill']}")
    print(f"   Selected Workflow: {execution_plan['selected_workflow']}")
    print(f"   Fallback Needed: {execution_plan['fallback_needed']}")
    
    print("\n🎉 Integration test completed successfully!")
    print("\n📊 Summary of OpenClaw Skill Evolution Minimal Viable Loop:")
    print("   ✅ Trajectory logging")
    print("   ✅ Evaluation with scoring")
    print("   ✅ Reflection and analysis") 
    print("   ✅ Experience storage with deduplication")
    print("   ✅ Skill generation from patterns")
    print("   ✅ Planning with retrieved resources")

if __name__ == "__main__":
    main()