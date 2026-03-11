# OpenClaw Skill Evolution Usage Guide

## Table of Contents
- [Quick Start](#quick-start)
- [v1 Memory Layer](#v1-memory-layer)
- [v2 Skill Evolution Layer](#v2-skill-evolution-layer)
- [v3 Policy Learning Layer](#v3-policy-learning-layer)
- [Configuration](#configuration)
- [API Reference](#api-reference)

## Quick Start

### Installation
```bash
# Clone the repository
git clone https://github.com/lst016/openclaw-skill-evolution.git
cd openclaw-skill-evolution

# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Initialize Qdrant
```bash
# Start Qdrant container
docker run -d --name openclaw-skill-evolution-qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest

# Setup collections
python scripts/qdrant_setup.py
```

### Run Integration Tests
```bash
# Test v1 functionality
python scripts/integration_test.py

# Test v2 functionality  
python scripts/v2_integration_test.py

# Test v3 functionality
python scripts/v3_integration_test.py
```

## v1 Memory Layer

The v1 layer focuses on **experience accumulation**. It records task execution trajectories and stores high-value experiences.

### Key Components
- **Trajectory Logger**: Records complete task execution with step-level details
- **Evaluator**: Implements dual-layer scoring (task + step level)
- **Reflector**: Analyzes execution quality and generates improvement suggestions
- **Experience Manager**: Stores and deduplicates high-value experiences

### Data Flow
```
Task Execution → Trajectory Logging → Evaluation → Reflection → Experience Storage
```

### Configuration
- `config/thresholds.json`: Scoring thresholds and experience storage criteria
- `logs/trajectories/`: Local trajectory storage
- `logs/reflections/`: Reflection results storage

## v2 Skill Evolution Layer

The v2 layer adds **automatic skill generation** from repeated successful patterns.

### Key Components
- **Workflow Comparator**: Compares different workflows to find optimal execution strategies
- **Skill Synthesizer**: Generates reusable skills from multiple successful trajectories
- **Policy Optimizer**: Automatically updates policies based on performance metrics
- **Daily Evolution Loop**: Scheduled optimization and reporting

### Data Flow
```
Multiple Trajectories → Workflow Comparison → Skill Synthesis → Policy Optimization → Daily Reporting
```

### Requirements for Skill Generation
- Minimum 3 similar trajectories
- Success rate ≥ 80%
- Average score ≥ 0.7
- Consistent tool order

### Generated Assets
- `skills/generated/*.yaml`: Auto-generated skill files
- `workflows/generated/*.yaml`: Optimized workflow files
- `logs/daily_reports/`: Daily evolution reports

## v3 Policy Learning Layer

The v3 layer provides **stable policy learning** without model training. It focuses on optimal decision-making.

### Key Components
- **Task Classifier**: Maps user tasks to standardized task types
- **Policy Router**: Routes tasks to optimal skill/workflow/tool combinations
- **Critic**: Evaluates policy quality beyond just task success
- **Policy Updater**: Manages three-state policy lifecycle (active/candidate/archived)
- **Fallback Manager**: Handles failures with backup strategies

### Data Flow
```
User Task → Task Classification → Policy Routing → Execution → 
Trajectory Logging → Critic Evaluation → Policy Update → Fallback Management
```

### Policy States
- **Active**: Currently used policies
- **Candidate**: New policies awaiting validation
- **Archived**: Historical policies for rollback

### Stability Principles
1. **No Model Training**: Only learns agent policies, never trains model weights
2. **Explainable Decisions**: Every routing decision includes reasoning
3. **Slow Updates**: Requires repeated validation before policy promotion
4. **Rollback Support**: All policies are versioned and reversible
5. **Failure Learning**: Records and learns from high-value failures

## Configuration

### Core Configuration Files
- `config/qdrant.json`: Qdrant connection and collection settings
- `config/thresholds.json`: Scoring and policy update thresholds
- `config/evolution.json`: System-wide evolution settings

### Policy Files
- `policies/task_policy.json`: Task type to route mapping
- `policies/skill_policy.json`: Task type to preferred skill mapping
- `policies/workflow_policy.json`: Task type to preferred workflow mapping
- `policies/tool_policy.json`: Task type to preferred tool order mapping
- `policies/fallback_policy.json`: Failure handling strategies

### Directory Structure
```
.openclaw/
├── agents/                 # Core modules
│   ├── classifier/         # Task classification
│   ├── critic/            # Policy quality evaluation
│   ├── fallback_manager/  # Failure handling
│   ├── main/              # Main trajectory logger
│   ├── optimizer/         # v2 policy optimization
│   ├── planner/           # v2 planning
│   ├── policy_router/     # v3 policy routing
│   ├── policy_updater/    # v3 policy lifecycle management
│   ├── reflector/         # Execution reflection
│   ├── synthesizer/       # v2 skill synthesis
│   └── comparator/        # v2 workflow comparison
├── skills/                # Generated and manual skills
│   ├── generated/         # Auto-generated skills
│   ├── manual/            # Hand-crafted skills
│   ├── archived/          # Archived skills
│   └── templates/         # Skill templates
├── workflows/             # Generated and preferred workflows
│   ├── generated/         # Auto-generated workflows
│   ├── preferred/         # High-performing workflows
│   └── archived/          # Archived workflows
├── policies/              # Policy configuration
│   ├── history/           # Policy change history
├── logs/                  # System logs
│   ├── trajectories/      # Execution trajectories
│   ├── reflections/       # Reflection results
│   ├── critic/            # v3 policy evaluations
│   ├── policy_updates/    # Policy update logs
│   └── daily_reports/     # Daily evolution reports
├── reports/               # Analysis reports
│   ├── evolution/         # v2 evolution reports
│   └── policy/            # v3 policy reports
└── config/                # Configuration files
```

## API Reference

### Core Classes

#### TrajectoryLoggerV2
```python
logger = TrajectoryLoggerV2()
trajectory = logger.log_trajectory(
    task="Debug application error",
    task_type="debugging",
    skill_name="structured_debugging",
    workflow_name="debug_workflow_v1",
    steps=[...],
    tools_used=["read", "edit", "exec"],
    success=True,
    final_score=1.8
)
```

#### TaskClassifier
```python
classifier = TaskClassifier()
classification = classifier.classify_task("How do I fix this Python bug?")
# Returns: {"task_type": "debugging", "confidence": 0.85, "reason": "..."}
```

#### PolicyRouter
```python
router = PolicyRouter()
routing_decision = router.route_task(
    task_type="debugging",
    candidate_skills=[...],
    candidate_workflows=[...]
)
```

#### Critic
```python
critic = Critic()
policy_evaluation = critic.evaluate_policy_quality(
    trajectory,
    selected_skill,
    selected_workflow,
    selected_tool_order
)
```

### Policy Management
```python
# Update policy (creates candidate)
updater = PolicyUpdater()
updater.update_policy("debugging", trajectories)

# Promote candidate to active (after validation)
updater.promote_candidate_policy("debugging")

# Handle fallback
fallback_manager = FallbackManager()
if fallback_manager.should_fallback("debugging"):
    fallback_path = fallback_manager.get_fallback_path("debugging")
```

## Best Practices

### For Stable Operation
1. **Start with v1**: Ensure trajectory logging works correctly
2. **Monitor v2**: Watch skill generation quality and adjust thresholds
3. **Validate v3**: Manually review policy candidates before promotion
4. **Regular backups**: Archive important policies and skills
5. **Performance monitoring**: Track success rates and scores over time

### For Development
1. **Use integration tests**: Always test changes with full integration tests
2. **Check Qdrant health**: Monitor Qdrant collections and vector quality
3. **Review daily reports**: Analyze daily evolution reports for insights
4. **Update documentation**: Keep README and usage guides current
5. **Version control**: Use Git tags for major releases (v1.0, v2.0, v3.0)

## Troubleshooting

### Common Issues
- **Qdrant connection errors**: Verify Docker container is running
- **Missing trajectories**: Check file permissions in logs directory
- **Policy not updating**: Ensure sufficient trajectory volume for validation
- **Skill generation failures**: Verify trajectory quality meets thresholds
- **Routing inconsistencies**: Review task classification accuracy

### Debugging Commands
```bash
# Check Qdrant status
curl http://localhost:6333

# View recent trajectories
ls -la ~/.openclaw/workspace/logs/trajectories/

# Check policy files
cat ~/.openclaw/workspace/policies/*.json

# Run specific tests
python scripts/v3_integration_test.py
```

---
*OpenClaw Skill Evolution v3.0 - Stable Policy Learning Layer*