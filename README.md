# OpenClaw Skill Evolution

本地 Skill / Workflow 自进化层集成方案

## 目标

在现有 OpenClaw 运行时中集成一套"本地 Skill / Workflow 自进化层"，持续优化以下对象：

1. skill
2. workflow  
3. tool usage order
4. agent execution policy
5. experience memory
6. reflection quality

## 核心原则

- **模型不是资产，skill/workflow/policy/experience 才是资产**
- **所有资产必须跨模型复用**
- **所有新增知识必须先去重再写入**
- **所有 policy 更新必须基于重复成功证据**
- **系统优先追求稳定可解释，不追求复杂训练**

## 系统定位

这是集成在 OpenClaw 内部的 Skill Evolution Layer，不替换 OpenClaw，只扩展其能力。

## 目录结构

```
.openclaw/
├── agents/
│   ├── main/
│   ├── planner/
│   ├── reflector/
│   └── synthesizer/
├── skills/
│   ├── generated/
│   ├── manual/
│   ├── archived/
│   └── templates/
├── workflows/
│   ├── generated/
│   ├── preferred/
│   └── archived/
├── task_types/
├── memory/
│   └── qdrant/
├── schemas/
│   └── collections/
├── snapshots/
├── embeddings/
├── cache/
├── policies/
│   ├── task_policy.json
│   ├── skill_policy.json
│   ├── tool_policy.json
│   └── routing_policy.json
├── logs/
│   ├── trajectories/
│   ├── rewards/
│   ├── reflections/
│   ├── evaluations/
│   └── daily_reports/
├── reports/
│   └── evolution/
├── scripts/
│   ├── evolve/
│   ├── reflect/
│   ├── evaluate/
│   ├── dedup/
│   └── backup/
└── config/
    ├── qdrant.json
    ├── thresholds.json
    ├── models.json
    └── evolution.json
```

## Qdrant Collections

1. **skills** - 存放可复用 skill
2. **workflows** - 存放 task type 对应 workflow  
3. **experiences** - 存放高价值经验
4. **trajectories** - 存放完整任务轨迹

## 最小可用闭环

第一版只需要实现以下闭环：
1. 执行任务并记录 trajectory
2. 任务结束后做 reflection  
3. 高分任务提炼 experience 并写入 qdrant
4. 当 3 个以上相近高分 trajectories 出现时生成 skill
5. skill 稳定后更新 policy

## 禁止事项

- ❌ 训练模型权重
- ❌ 引入 LoRA / PPO / GRPO / SFT  
- ❌ 把 skill 进化逻辑写死在单个 prompt 中
- ❌ 不做去重就无限写入经验
- ❌ 基于一次成功立即改 policy
- ❌ 不保存历史版本直接覆盖 skill

## 仓库

https://github.com/lst016/openclaw-skill-evolution.git