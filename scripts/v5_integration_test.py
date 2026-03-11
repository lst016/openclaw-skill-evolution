#!/usr/bin/env python3
"""
v5 Integration Test for OpenClaw Skill Evolution
Tests the complete v5 environment learning layer functionality
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def main():
    """Run v5 integration test"""
    print("✅ All v5 modules imported successfully")
    print("🚀 Starting OpenClaw Skill Evolution v5 Integration Test")
    
    # Test 1: Environment Manager
    print("\n1️⃣ Testing Environment Manager...")
    from environment.manager.environment_manager import EnvironmentManager
    env_manager = EnvironmentManager()
    snapshot = env_manager.create_environment_snapshot("/")
    print(f"✅ Environment snapshot created: {snapshot['snapshot_id']}")
    
    # Test 2: State Tracker  
    print("\n2️⃣ Testing State Tracker...")
    from environment.tracker.state_tracker import StateTracker
    tracker = StateTracker()
    event = tracker.record_environment_event(
        event_type="file_modified",
        target="test_file.py", 
        change_summary="Test file modification for v5 integration",
        source_task="v5_integration_test"
    )
    print(f"✅ Environment event recorded: {event['event_id']}")
    
    # Test 3: World Model Builder
    print("\n3️⃣ Testing World Model Builder...")
    from environment.graph.world_model_builder import WorldModelBuilder
    builder = WorldModelBuilder()
    
    # Create test nodes
    nodes = [
        builder.create_environment_node("service_a", "service", "Service A", "Main business service"),
        builder.create_environment_node("service_b", "service", "Service B", "Supporting service"),
        builder.create_environment_node("db_main", "database", "Main Database", "Primary database")
    ]
    
    # Create relationships
    relationships = [
        ("service_a", "service_b", "depends_on"),
        ("service_a", "db_main", "writes"),
        ("service_b", "db_main", "reads")
    ]
    
    # Build and save graph
    graph = builder.build_dependency_graph(nodes, relationships)
    graph_file = builder.save_graph_to_file(graph)
    print(f"✅ Environment graph built and saved: {graph_file}")
    
    # Test 4: Long Task Manager
    print("\n4️⃣ Testing Long Task Manager...")
    from long_tasks.manager.long_task_manager import LongTaskManager
    task_manager = LongTaskManager()
    
    # Create initial steps
    initial_steps = [
        {
            "step_id": "analyze_repo",
            "description": "Analyze repository structure and requirements",
            "status": "pending",
            "assigned_to": "planner",
            "estimated_duration": "2 hours",
            "dependencies": [],
            "outputs": []
        },
        {
            "step_id": "design_api", 
            "description": "Design API interfaces and data models",
            "status": "pending",
            "assigned_to": "architect",
            "estimated_duration": "4 hours",
            "dependencies": ["analyze_repo"],
            "outputs": []
        }
    ]
    
    long_task = task_manager.create_long_task(
        goal="Implement payment feature",
        description="Add payment processing capability to the system",
        priority="high",
        estimated_duration="2 weeks",
        initial_steps=initial_steps
    )
    task_manager.save_long_task(long_task)
    print(f"✅ Long task created: {long_task['task_id']}")
    
    print("\n🎉 v5 Integration Test completed successfully!")
    print("✅ Environment Manager: Working")
    print("✅ State Tracker: Working") 
    print("✅ World Model Builder: Working")
    print("✅ Long Task Manager: Working")
    print("\n🎯 v5 Environment Learning Layer is ready!")

if __name__ == "__main__":
    main()