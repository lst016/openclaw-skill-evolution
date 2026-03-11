# OpenClaw Skill Evolution API Reference

## Table of Contents
- [Core Modules](#core-modules)
- [Data Structures](#data-structures)
- [Configuration Files](#configuration-files)
- [Qdrant Collections](#qdrant-collections)

## Core Modules

### Task Classifier
**Path**: `agents/classifier/task_classifier.py`

**Class**: `TaskClassifier`

**Methods**:
- `classify_task(task: str) -> Dict[str, Any]`
  - **Description**: Classifies a user task into a standardized task type
  - **Parameters**: 
    - `task` (str): User task description
  - **Returns**: 
    - `task_type` (str): Standardized task type
    - `confidence` (float): Classification confidence (0.0-1.0)
    - `reason` (str): Explanation for classification

### Policy Router
**Path**: `agents/policy_router/policy_router.py`

**Class**: `PolicyRouter`

**Methods**:
- `route_task(task_type: str, candidate_skills: List[Dict], candidate_workflows: List[Dict]) -> Dict[str, Any]`
  - **Description**: Routes a task to optimal skill, workflow, and tool order based on policies
  - **Parameters**:
    - `task_type` (str): Standardized task type
    - `candidate_skills` (List[Dict]): Available skills from Qdrant
    - `candidate_workflows` (List[Dict]): Available workflows from Qdrant
  - **Returns**:
    - `selected_skill` (str): Selected skill name
    - `selected_workflow` (str): Selected workflow ID
    - `selected_tool_order` (List[str]): Optimal tool execution order
    - `fallback_path` (Dict): Fallback strategy
    - `routing_reason` (str): Explanation for routing decision

### Critic
**Path**: `agents/critic/critic.py`

**Class**: `Critic`

**Methods**:
- `evaluate_policy_quality(trajectory: Dict, selected_skill: str, selected_workflow: str, selected_tool_order: List[str]) -> Dict[str, Any]`
  - **Description**: Evaluates the quality of policy decisions, not just task success
  - **Parameters**:
    - `trajectory` (Dict): Complete task execution trajectory
    - `selected_skill` (str): Skill used for execution
    - `selected_workflow` (str): Workflow used for execution  
    - `selected_tool_order` (List[str]): Tool order used for execution
  - **Returns**:
    - `skill_fit_score` (float): How well the skill matched the task (-1.0 to 1.0)
    - `workflow_fit_score` (float): How well the workflow matched the task (-1.0 to 1.0)
    - `tool_order_score` (float): How optimal the tool order was (-1.0 to 1.0)
    - `efficiency_score` (float): Execution efficiency score (-1.0 to 1.0)
    - `final_policy_reward` (float): Overall policy quality reward
    - `suggested_adjustment` (Dict): Recommendations for improvement

### Policy Updater
**Path**: `agents/policy_updater/policy_updater.py`

**Class**: `PolicyUpdater`

**Methods**:
- `update_policy(task_type: str, trajectories: List[Dict], critic_results: List[Dict]) -> bool`
  - **Description**: Updates policies based on trajectory and critic data using three-state mechanism
  - **Parameters**:
    - `task_type` (str): Task type to update policy for
    - `trajectories` (List[Dict]): Recent trajectories for this task type
    - `critic_results` (List[Dict]): Corresponding critic evaluations
  - **Returns**: 
    - `bool`: True if policy was updated, False otherwise

### Fallback Manager
**Path**: `agents/fallback_manager/fallback_manager.py`

**Class**: `FallbackManager`

**Methods**:
- `check_fallback_needed(task_type: str, recent_trajectories: List[Dict]) -> Dict[str, Any]`
  - **Description**: Determines if fallback strategy should be activated based on recent failures
  - **Parameters**:
    - `task_type` (str): Task type to check
    - `recent_trajectories` (List[Dict]): Recent trajectories for this task type
  - **Returns**:
    - `fallback_needed` (bool): Whether fallback is needed
    - `fallback_skill` (str): Recommended fallback skill
    - `fallback_workflow` (str): Recommended fallback workflow
    - `reason` (str): Explanation for fallback decision

## Data Structures

### Trajectory (v3 Enhanced)
```json
{
  "trajectory_id": "string",
  "task": "string",
  "task_type": "string",
  "skill_id": "string|null",
  "skill_name": "string|null", 
  "workflow_id": "string|null",
  "workflow_name": "string|null",
  "steps": [
    {
      "step": "integer",
      "action": "string",
      "tool": "string",
      "input_summary": "string",
      "output_summary": "string", 
      "success": "boolean",
      "score": "float",
      "duration_ms": "integer"
    }
  ],
  "tools_used": ["string"],
  "outputs_summary": "string",
  "success": "boolean",
  "final_score": "float",
  "duration_ms": "integer",
  "reflection_id": "string|null",
  "created_at": "ISO8601 datetime"
}
```

### Policy States
- **active**: Currently used policy
- **candidate**: Proposed policy awaiting validation
- **archived**: Historical policy (rollback available)

### Policy Reward Calculation
```
policy_reward = result_reward + efficiency_reward + strategy_reward - risk_penalty

result_reward:
  success: +1.0
  failure: -1.0

efficiency_reward:
  fewer_steps: +0.2
  shorter_duration: +0.2  
  unnecessary_steps: -0.2

strategy_reward:
  correct_skill: +0.2
  stable_workflow: +0.2
  reasonable_tool_order: +0.1

risk_penalty:
  wrong_tool: -0.2
  repeated_action: -0.1
  circular_attempts: -0.3
  no_validation: -0.2
```

## Configuration Files

### qdrant.json
```json
{
  "host": "localhost",
  "port": 6333,
  "collections": {
    "skills": {"vector_size": 1536, "distance": "Cosine"},
    "workflows": {"vector_size": 1536, "distance": "Cosine"},
    "experiences": {"vector_size": 1536, "distance": "Cosine"},
    "trajectories": {"vector_size": 1536, "distance": "Cosine"},
    "policies": {"vector_size": 1536, "distance": "Cosine"},
    "failures": {"vector_size": 1536, "distance": "Cosine"}
  }
}
```

### thresholds.json
```json
{
  "experience": {"min_final_score": 0.8, "similarity_threshold": 0.9},
  "skill": {"min_similar_tasks": 3, "min_avg_score": 0.7},
  "policy": {"min_evidence_count": 5, "confidence_threshold": 0.85},
  "scoring": {
    "task_success": 1.0,
    "task_failure": -1.0,
    "validation_passed": 0.3,
    "high_quality_result": 0.2,
    "unnecessary_steps": -0.2,
    "introduced_errors": -0.5,
    "no_validation": -0.2,
    "correct_context": 0.1,
    "correct_target": 0.1,
    "effective_tool_call": 0.1,
    "effective_modification": 0.2,
    "completed_verification": 0.2,
    "ineffective_search": -0.1,
    "repeated_action": -0.1,
    "wrong_tool": -0.2,
    "circular_attempts": -0.3
  }
}
```

## Qdrant Collections

### policies Collection
**Purpose**: Stores task-to-skill/workflow/tool-order policy mappings

**Payload Schema**:
- `policy_id` (keyword)
- `task_type` (keyword)  
- `preferred_skill` (keyword)
- `preferred_workflow` (keyword)
- `preferred_tool_order` (keyword array)
- `confidence` (float)
- `success_rate` (float)
- `avg_score` (float)
- `usage_count` (integer)
- `version` (integer)
- `status` (keyword: active|candidate|archived)
- `created_at` (datetime)
- `updated_at` (datetime)

**Embedding Fields**: `task_type + preferred_skill + preferred_workflow`

### failures Collection  
**Purpose**: Stores high-value failure samples for learning

**Payload Schema**:
- `failure_id` (keyword)
- `task_type` (keyword)
- `wrong_skill` (keyword)
- `wrong_workflow` (keyword) 
- `wrong_tool_order` (keyword array)
- `failure_reason` (text)
- `trajectory_id` (keyword)
- `score` (float)
- `created_at` (datetime)

**Embedding Fields**: `task_type + failure_reason`

## Usage Examples

### Basic v3 Workflow
```python
from agents.classifier.task_classifier import TaskClassifier
from agents.policy_router.policy_router import PolicyRouter
from agents.main.trajectory_logger_v2 import TrajectoryLoggerV2
from agents.critic.critic import Critic
from agents.policy_updater.policy_updater import PolicyUpdater

# 1. Classify task
classifier = TaskClassifier()
classification = classifier.classify_task("Debug Python application error")

# 2. Route to optimal policy
router = PolicyRouter()
routing_decision = router.route_task(
    classification['task_type'],
    candidate_skills=[],
    candidate_workflows=[]
)

# 3. Execute and log trajectory
logger = TrajectoryLoggerV2()
trajectory = logger.log_trajectory(
    task="Debug Python application error",
    task_type=classification['task_type'],
    skill_name=routing_decision['selected_skill'],
    workflow_name=routing_decision['selected_workflow'],
    steps=[...],
    success=True,
    final_score=1.5
)

# 4. Evaluate policy quality
critic = Critic()
policy_evaluation = critic.evaluate_policy_quality(
    trajectory,
    routing_decision['selected_skill'],
    routing_decision['selected_workflow'], 
    routing_decision['selected_tool_order']
)

# 5. Update policy (if validated)
updater = PolicyUpdater()
updater.update_policy(
    classification['task_type'],
    [trajectory],
    [policy_evaluation]
)
```