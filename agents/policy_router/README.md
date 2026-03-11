# Policy Router

## 中文
策略路由器根据任务类型和候选资源，选择最优的技能、工作流和工具顺序。

## English  
The Policy Router selects the optimal skill, workflow, and tool order based on task type and candidate resources.

## Key Features
- Routes tasks to preferred policies
- Supports fallback strategies
- Provides explainable routing decisions
- Integrates with Qdrant for policy retrieval

## Usage
```python
from agents.policy_router.policy_router import PolicyRouter

router = PolicyRouter()
decision = router.route_task(
    task_type="debugging",
    candidate_skills=[...],
    candidate_workflows=[...]
)
```