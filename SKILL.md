---
name: openclaw-skill-evolution
description: OpenClaw Skill Evolution - Local Skill/Workflow Self-Evolution Layer for OpenClaw Runtime
metadata: {"openclaw":{"requires":{"bins":["python3", "git"]}}}
---

# OpenClaw Skill Evolution

## 中文说明

**用途**：在现有 OpenClaw 运行时中集成一套"本地 Skill / Workflow 自进化层"，持续优化以下对象：

1. skill（技能）
2. workflow（工作流）  
3. tool usage order（工具使用顺序）
4. agent execution policy（Agent 执行策略）
5. experience memory（经验记忆）
6. reflection quality（反思质量）

**核心原则**：
- **不训练模型权重** - 只优化 skill/workflow/policy
- **资产跨模型复用** - 所有沉淀结果在模型升级后仍然可复用
- **版本化管理** - 所有 skill、workflow、policy 都可版本化、可回滚、可比较
- **去重优先** - 所有新增知识必须先去重再写入
- **证据驱动** - 所有 policy 更新必须基于重复成功证据

## English Description

**Purpose**: Integrate a local Skill/Workflow Self-Evolution Layer into the existing OpenClaw runtime to continuously optimize:

1. Skills
2. Workflows
3. Tool usage order
4. Agent execution policies
5. Experience memory
6. Reflection quality

**Core Principles**:
- **No Model Weight Training** - Only optimize skills/workflows/policies
- **Cross-Model Asset Reusability** - All accumulated assets remain reusable after model upgrades
- **Versioned Management** - All skills, workflows, and policies are versioned, rollbackable, and comparable
- **Deduplication First** - All new knowledge must be deduplicated before writing
- **Evidence-Driven** - All policy updates must be based on repeated successful evidence

## System Architecture

### v1 - Memory Layer
- **Goal**: Accumulate experiences
- **Focus**: Trajectory logging, reflection, experience storage

### v2 - Skill Evolution Layer  
- **Goal**: Generate reusable skills and workflows
- **Focus**: Skill synthesis from multiple trajectories, workflow comparison

### v3 - Policy Learning Layer
- **Goal**: Automatically select optimal skill/workflow/tool order
- **Focus**: Policy routing, policy quality evaluation, stable policy learning

## Directory Structure

```
.openclaw/
├── agents/
│   ├── main/                 # Main trajectory logger
│   ├── planner/              # Task planning and resource retrieval
│   ├── reflector/            # Post-task reflection and analysis
│   ├── synthesizer/          # Skill synthesis from patterns
│   ├── comparator/           # Workflow comparison and optimization
│   ├── optimizer/            # Policy optimization
│   ├── classifier/           # Task classification (v3)
│   ├── critic/               # Policy quality evaluation (v3)
│   ├── policy_router/        # Policy-based routing (v3)
│   └── fallback_manager/     # Fallback management (v3)
├── skills/
│   ├── generated/            # Auto-generated skills
│   ├── manual/               # Manually created skills
│   ├── archived/             # Archived skills
│   └── templates/            # Skill templates
├── workflows/
│   ├── generated/            # Auto-generated workflows
│   ├── preferred/            # Preferred workflows
│   ├── archived/             # Archived workflows
│   └── task_types/           # Task-type specific workflows
├── memory/
│   └── qdrant/               # Qdrant vector database storage
├── schemas/
│   └── collections/          # Qdrant collection schemas
├── snapshots/
├── embeddings/
├── cache/
├── policies/
│   ├── task_policy.json      # Task type routing policies
│   ├── skill_policy.json     # Skill selection policies
│   ├── workflow_policy.json  # Workflow selection policies
│   ├── tool_policy.json      # Tool order policies
│   ├── fallback_policy.json  # Fallback policies (v3)
│   └── history/              # Policy update history
├── logs/
│   ├── trajectories/         # Complete task execution trajectories
│   ├── rewards/              # Reward and scoring logs
│   ├── reflections/          # Reflection results
│   ├── evaluations/          # Evaluation results
│   ├── daily_reports/        # Daily evolution reports
│   ├── policy_updates/       # Policy update logs (v3)
│   ├── critic/               # Critic evaluation logs (v3)
│   └── routing/              # Routing decision logs (v3)
├── reports/
│   ├── evolution/            # Evolution reports
│   └── policy/               # Policy performance reports (v3)
├── scripts/
│   ├── evolve/               # Evolution scripts
│   ├── reflect/              # Reflection scripts
│   ├── evaluate/             # Evaluation scripts
│   ├── dedup/                # Deduplication scripts
│   ├── backup/               # Backup scripts
│   └── daily_evolution_loop.py # Daily evolution loop (v2/v3)
└── config/
    ├── qdrant.json           # Qdrant configuration
    ├── thresholds.json       # Scoring and threshold configuration
    ├── models.json           # Model configuration
    └── evolution.json        # Evolution system configuration
```

## Qdrant Collections

1. **skills** - Store reusable skills
2. **workflows** - Store task-type workflows
3. **experiences** - Store high-value experiences
4. **trajectories** - Store complete task trajectories
5. **policies** - Store policy mappings (v3)
6. **failures** - Store high-value failure samples (v3)

## Minimal Viable Loop

### v1 Loop:
```
task → execute → trajectory → reflection → experience
```

### v2 Loop:
```
task → planner → skill search → workflow execution → trajectory → 
reflection → workflow comparison → skill synthesis → policy optimization
```

### v3 Loop:
```
task → task classifier → policy router → skill selector → workflow selector → 
executor → trajectory logger → critic/evaluator → policy updater → 
update qdrant + policy files
```

## Prohibited Actions

- ❌ Train model weights
- ❌ Use PPO/GRPO/LoRA/Fine-tuning
- ❌ Embed skill evolution logic in single prompts
- ❌ Write experiences without deduplication
- ❌ Update policies based on single success
- ❌ Overwrite skills without versioning

## Repository

https://github.com/lst016/openclaw-skill-evolution.git

## Maintainer

🐮 牛牛 (Niu Niu)