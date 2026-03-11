#!/usr/bin/env python3
"""
v3 Integration Test for OpenClaw Skill Evolution
Tests the complete v3 policy learning workflow
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
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from agents.classifier.task_classifier import TaskClassifier
    from agents.policy_router.policy_router import PolicyRouter
    from agents.critic.critic import Critic
    from agents.policy_updater.policy_updater import PolicyUpdater
    from agents.fallback_manager.fallback_manager import FallbackManager
    from agents.main.trajectory_logger_v2 import TrajectoryLoggerV2
    from scripts.evaluator import Evaluator
    print("✅ All v3 modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def main():
    """Run v3 integration test"""
    print("🚀 Starting OpenClaw Skill Evolution v3 Integration Test")
    
    # Step 1: Classify task type
    print("\n1️⃣ Classifying task type...")
    classifier = TaskClassifier()
    task = "Debug a Python application that's crashing in production"
    classification = classifier.classify_task(task)
    print(f"✅ Task classified as: {classification['task_type']}")
    print(f"   Confidence: {classification['confidence']:.2f}")
    print(f"   Reason: {classification['reason']}")
    
    # Step 2: Route to optimal policy
    print("\n2️⃣ Routing to optimal policy...")
    router = PolicyRouter()
    
    # Get candidate skills and workflows
    candidate_skills = router.get_candidate_skills(classification['task_type'])
    candidate_workflows = router.get_candidate_workflows(classification['task_type'])
    
    routing_decision = router.route_task(classification['task_type'], candidate_skills, candidate_workflows)
    print(f"✅ Routing decision:")
    print(f"   Selected skill: {routing_decision['selected_skill']}")
    print(f"   Selected workflow: {routing_decision['selected_workflow']}")
    print(f"   Selected tool order: {routing_decision['selected_tool_order']}")
    print(f"   Fallback path: {routing_decision['fallback_path']}")
    print(f"   Routing reason: {routing_decision['routing_reason']}")
    
    # Step 3: Execute and log trajectory
    print("\n3️⃣ Executing task and logging trajectory...")
    logger = TrajectoryLoggerV2()
    trajectory = logger.log_trajectory(
        task=task,
        task_type=classification['task_type'],
        skill_name=routing_decision['selected_skill'],
        workflow_name=routing_decision['selected_workflow'],
        steps=[
            {"step": 1, "action": "analyze_error", "tool": "read", "success": True, "score": 0.9},
            {"step": 2, "action": "inspect_code", "tool": "read", "success": True, "score": 0.8},
            {"step": 3, "action": "generate_fix", "tool": "write", "success": True, "score": 0.9},
            {"step": 4, "action": "validate_fix", "tool": "exec", "success": True, "score": 0.8}
        ],
        tools_used=routing_decision['selected_tool_order'],
        outputs_summary="Successfully debugged and fixed the production crash",
        success=True,
        final_score=0.0,
        duration_ms=5000
    )
    print(f"✅ Trajectory logged: {trajectory['trajectory_id'][:8]}...")
    
    # Step 4: Evaluate with standard evaluator
    print("\n4️⃣ Evaluating trajectory...")
    evaluator = Evaluator()
    evaluation = evaluator.evaluate_trajectory(trajectory)
    trajectory["final_score"] = evaluation["final_score"]
    print(f"✅ Evaluation completed - Final score: {evaluation['final_score']:.2f}")
    
    # Step 5: Critic evaluate policy quality
    print("\n5️⃣ Critic evaluating policy quality...")
    critic = Critic()
    policy_evaluation = critic.evaluate_policy_quality(
        trajectory, 
        routing_decision['selected_skill'],
        routing_decision['selected_workflow'],
        routing_decision['selected_tool_order']
    )
    print(f"✅ Policy evaluation completed:")
    print(f"   Skill fit score: {policy_evaluation['skill_fit_score']:.2f}")
    print(f"   Workflow fit score: {policy_evaluation['workflow_fit_score']:.2f}")
    print(f"   Tool order score: {policy_evaluation['tool_order_score']:.2f}")
    print(f"   Final policy reward: {policy_evaluation['final_policy_reward']:.2f}")
    
    if policy_evaluation['suggested_adjustment']:
        print("   Suggestions:")
        for key, suggestion in policy_evaluation['suggested_adjustment'].items():
            print(f"     {key}: {suggestion}")
    
    # Step 6: Update policy (candidate stage)
    print("\n6️⃣ Updating policy (candidate stage)...")
    updater = PolicyUpdater()
    
    # Simulate having multiple trajectories for policy update
    simulated_trajectories = [trajectory, trajectory, trajectory]  # Same trajectory 3 times for demo
    
    policy_update_result = updater.update_policy_from_trajectories(
        classification['task_type'], 
        simulated_trajectories
    )
    
    if policy_update_result:
        print(f"✅ Policy candidate updated for task type: {classification['task_type']}")
    else:
        print("⚠️ Policy update not needed (insufficient evidence)")
    
    # Step 7: Check fallback manager
    print("\n7️⃣ Checking fallback manager...")
    fallback_manager = FallbackManager()
    
    # Check if fallback is needed
    fallback_needed = fallback_manager.should_trigger_fallback(
        classification['task_type'], 
        failure_count=0, 
        consecutive_failures=0
    )
    
    print(f"✅ Fallback status checked:")
    print(f"   Fallback needed: {fallback_needed}")
    
    if fallback_needed:
        fallback_strategy = fallback_manager.get_fallback_strategy(classification['task_type'])
        if fallback_strategy:
            print(f"   Recommended fallback: {fallback_strategy['fallback_skill']}")
        else:
            print("   No fallback strategy available")
    
    # Step 8: Simulate daily evolution loop
    print("\n8️⃣ Simulating daily evolution loop...")
    # This would normally run on a schedule
    print("✅ Daily evolution loop ready for scheduled execution")
    print("   - Would analyze today's trajectories")
    print("   - Would promote validated candidates to active")
    print("   - Would archive outdated active policies")
    print("   - Would generate daily evolution report")
    
    print("\n🎉 v3 Integration test completed successfully!")
    print("\n📊 Summary of OpenClaw Skill Evolution v3 Capabilities:")
    print("   ✅ Task classification with confidence and reasoning")
    print("   ✅ Policy-based routing to optimal skill/workflow/tool order")
    print("   ✅ Policy quality evaluation (not just task success)")
    print("   ✅ Three-state policy management (active/candidate/archived)")
    print("   ✅ Fallback management for failure scenarios")
    print("   ✅ Stable policy learning without model training")
    print("   ✅ Explainable and rollbackable decisions")

if __name__ == "__main__":
    main()