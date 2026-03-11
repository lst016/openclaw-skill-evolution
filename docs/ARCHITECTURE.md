# OpenClaw Skill Evolution Architecture

## System Overview

OpenClaw Skill Evolution is a **policy learning layer** integrated into the existing OpenClaw runtime. It enables the system to automatically learn and optimize agent decision-making without training model weights.

The system evolves through three distinct phases:

- **v1 (Memory Layer)**: Accumulates experiences from task execution
- **v2 (Skill Evolution Layer)**: Generates reusable skills and workflows from patterns
- **v3 (Policy Learning Layer)**: Learns optimal policy for skill/workflow/tool selection

## Core Principles

### 1. Policy Learning, Not Model Training
- **DO**: Learn agent policies, routing strategies, and execution patterns
- **DON'T**: Train model weights, use RLHF/PPO/LoRA, or modify model parameters

### 2. Explainable Decisions
Every decision must be explainable with clear reasoning:
- Historical success rate is higher
- Recent 5 executions have better average scores  
- Workflow steps are shorter
- Failure rate is lower

### 3. Stable Policy Updates
Policy updates follow strict validation rules:
- Minimum 3 successful executions to generate candidate policy
- Minimum 5 successful executions to promote to active policy
- New policy must consistently outperform current policy

### 4. Full Rollback Capability
All assets maintain version history:
- Skills: `skills/generated/{name}.v{version}.yaml`
- Workflows: `workflows/task_types/{type}.v{version}.yaml`  
- Policies: Three-state management (active/candidate/archived)

### 5. Learn from Both Success and Failure
The system learns from all execution outcomes:
- **Success**: Identify optimal patterns and reinforce them
- **Failure**: Record high-value failure samples to avoid repeating mistakes

## v3 Architecture Components

### Core Modules

| Module | Responsibility | Key Features |
|--------|----------------|--------------|
| **Task Classifier** | Maps user tasks to standardized task types | Confidence scoring, keyword matching, taxonomy enforcement |
| **Policy Router** | Routes tasks to optimal skill/workflow/tool order | Multi-criteria decision making, fallback path generation |
| **Critic** | Evaluates policy quality beyond task success | Strategy reward calculation, efficiency analysis, risk assessment |
| **Policy Updater** | Manages policy lifecycle and updates | Three-state workflow, validation requirements, version control |
| **Fallback Manager** | Handles policy underperformance | Automatic fallback triggering, second-best solution selection |

### Data Flow

```
User Task
    ↓
Task Classifier → Standardized task_type
    ↓  
Policy Router → Optimal skill/workflow/tool_order + fallback_path  
    ↓
Executor → Task execution using selected resources
    ↓
Trajectory Logger → Complete execution record with metadata
    ↓
Critic → Policy quality evaluation (not just task success)
    ↓
Policy Updater → Candidate policy generation/validation
    ↓
Qdrant + Policy Files → Persistent storage and retrieval
```

## Qdrant Collections

The system uses Qdrant as the vector memory backend with six collections:

| Collection | Purpose | Key Fields |
|------------|---------|------------|
| **skills** | Reusable skill storage | skill_name, success_rate, avg_score, version |
| **workflows** | Task-type specific workflows | task_type, tool_order, success_rate, version |
| **experiences** | High-value execution experiences | problem_summary, solution_summary, score |
| **trajectories** | Complete task execution records | task, task_type, skill_id, workflow_id, final_score |
| **policies** | Task-to-resource mapping policies | task_type, preferred_skill, confidence, status |
| **failures** | High-value failure samples | task_type, failure_reason, wrong_skill, trajectory_id |

## Policy Structure

The system maintains five policy files with standardized structure:

### Task Policy (`task_policy.json`)
```json
{
  "debugging": {
    "route": "debug-policy-v3"
  }
}
```

### Skill Policy (`skill_policy.json`)  
```json
{
  "debugging": {
    "preferred_skill": "structured_debugging.v2",
    "confidence": 0.86
  }
}
```

### Workflow Policy (`workflow_policy.json`)
```json
{
  "debugging": {
    "preferred_workflow": "debug-workflow.v3"
  }
}
```

### Tool Policy (`tool_policy.json`)
```json
{
  "debugging": {
    "tool_order": ["search_context", "inspect_target", "execute_change", "validate_result"]
  }
}
```

### Fallback Policy (`fallback_policy.json`)
```json
{
  "debugging": {
    "fallback_skill": "generic_problem_solving.v1",
    "fallback_workflow": "safe-debug-workflow.v1"
  }
}
```

## Policy States

Policies follow a three-state lifecycle:

1. **Active**: Currently used for task execution
2. **Candidate**: Under validation, requires repeated success to promote  
3. **Archived**: Previous versions, available for rollback

## Reward Design

The system uses a four-component reward structure:

### Result Reward
- Success: +1.0
- Failure: -1.0

### Efficiency Reward  
- Fewer steps: +0.2
- Shorter duration: +0.2
- Obvious detour: -0.2

### Strategy Reward
- Correct skill selection: +0.2
- Stable workflow: +0.2  
- Reasonable tool order: +0.1

### Risk Penalty
- Wrong tool: -0.2
- Repetitive actions: -0.1
- Circular attempts: -0.3
- No validation: -0.2

**Final Policy Reward** = result_reward + efficiency_reward + strategy_reward - risk_penalty

## Daily Evolution Loop

The system runs daily policy evolution:

1. Load today's trajectories
2. Group by task_type
3. Analyze active policy performance  
4. Validate candidate policies
5. Compare skill success rates
6. Compare workflow average scores
7. Compare tool order stability
8. Update candidate policies
9. Promote/keep/archive decisions
10. Generate daily evolution report

## Success Indicators

The v3 system is working correctly when you observe:

1. Similar tasks consistently select the same skill
2. Similar tasks follow stable workflow patterns  
3. Tool order becomes increasingly consistent
4. Underperforming skills are automatically deprioritized
5. Fallback paths are automatically activated when needed
6. Policy files show continuous, stable evolution

## What v3 Does NOT Do

To maintain stability, v3 explicitly avoids:

1. Multi-agent free-for-all competition
2. Models modifying their own prompts randomly
3. Single-success policy updates
4. Direct replacement of active policies without candidate phase
5. Ignoring failure samples
6. Operating without fallback mechanisms

---

## 系统架构概述 (中文)

OpenClaw Skill Evolution 是一个集成到现有 OpenClaw 运行时中的**策略学习层**。它使系统能够自动学习和优化 Agent 决策，而无需训练模型权重。

系统通过三个不同阶段演进：

- **v1 (记忆层)**: 从任务执行中积累经验
- **v2 (技能进化层)**: 从模式中生成可重用的技能和工作流  
- **v3 (策略学习层)**: 学习技能/工作流/工具选择的最优策略

## 核心原则

### 1. 策略学习，而非模型训练
- **做**: 学习 Agent 策略、路由策略和执行模式
- **不做**: 训练模型权重、使用 RLHF/PPO/LoRA 或修改模型参数

### 2. 可解释的决策
每个决策都必须有清晰的解释：
- 历史成功率更高
- 最近 5 次执行平均分更好
- 工作流步骤更短  
- 失败率更低

### 3. 稳定的策略更新
策略更新遵循严格的验证规则：
- 至少 3 次成功执行才能生成候选策略
- 至少 5 次成功执行才能提升为活跃策略
- 新策略必须持续优于当前策略

### 4. 完整的回滚能力
所有资产都维护版本历史：
- 技能: `skills/generated/{name}.v{version}.yaml`
- 工作流: `workflows/task_types/{type}.v{version}.yaml`
- 策略: 三态管理 (active/candidate/archived)

### 5. 从成功和失败中学习
系统从所有执行结果中学习：
- **成功**: 识别最优模式并强化它们
- **失败**: 记录高价值失败样本以避免重复错误

## v3 架构组件

### 核心模块

| 模块 | 职责 | 关键特性 |
|------|------|----------|
| **任务分类器** | 将用户任务映射到标准化任务类型 | 置信度评分、关键词匹配、分类法强制执行 |
| **策略路由器** | 将任务路由到最优技能/工作流/工具顺序 | 多标准决策、回退路径生成 |
| **批评家** | 评估策略质量（不仅仅是任务成功） | 策略奖励计算、效率分析、风险评估 |
| **策略更新器** | 管理策略生命周期和更新 | 三态工作流、验证要求、版本控制 |
| **回退管理器** | 处理策略表现不佳的情况 | 自动回退触发、次优解决方案选择 |

### 数据流

```
用户任务
    ↓
任务分类器 → 标准化 task_type
    ↓  
策略路由器 → 最优技能/工作流/工具顺序 + 回退路径  
    ↓
执行器 → 使用选定资源执行任务
    ↓
轨迹记录器 → 带元数据的完整执行记录
    ↓
批评家 → 策略质量评估（不仅仅是任务成功）
    ↓
策略更新器 → 候选策略生成/验证
    ↓
Qdrant + 策略文件 → 持久化存储和检索
```