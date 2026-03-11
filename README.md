# OpenClaw Skill Evolution

## 中文 / Chinese

**目标**: 在现有 OpenClaw 运行时中集成一套"本地 Skill / Workflow 自进化层"

**核心原则**: 
- 模型不是资产，skill/workflow/policy/experience 才是资产
- 所有资产必须跨模型复用
- 所有新增知识必须先去重再写入
- 所有 policy 更新必须基于重复成功证据
- 系统优先追求稳定可解释，不追求复杂训练

---

## English / 英文

**Goal**: Integrate a local skill evolution layer into the existing OpenClaw runtime.

**Core Principles**:
- Models are not assets; skills, workflows, policies, and experiences are the real assets
- All assets must be reusable across model upgrades
- All new knowledge must be deduplicated before writing
- All policy updates must be based on repeated successful evidence
- The system prioritizes stability and explainability over complex training

---

## Architecture Evolution / 架构演进

### v1 - Memory Layer / 记忆层
- **Goal**: Accumulate experiences / 积累经验
- **Core**: Trajectory logging + Experience storage / 轨迹记录 + 经验存储

### v2 - Skill Evolution Layer / 技能进化层  
- **Goal**: Generate reusable skills and workflows / 生成可复用技能和工作流
- **Core**: Skill synthesis + Workflow comparison + Policy optimization / 技能合成 + 工作流比较 + 策略优化

### v3 - Policy Learning Layer / 策略学习层
- **Goal**: Automatically select optimal skill/workflow/tool order / 自动选择最优技能/工作流/工具顺序
- **Core**: Task classification + Policy routing + Stable policy learning / 任务分类 + 策略路由 + 稳定策略学习

---

## Key Features / 核心特性

### ✅ No Model Training / 无模型训练
- **Never train model weights** / 从不训练模型权重
- **Only learn Agent policies** / 只学习 Agent 策略
- **Safe and stable evolution** / 安全稳定的进化

### ✅ Explainable Decisions / 可解释决策  
- **Every decision has reasoning** / 每个决策都有原因说明
- **Confidence scores provided** / 提供置信度分数
- **Human-readable explanations** / 人类可读的解释

### ✅ Rollbackable Updates / 可回滚更新
- **Three-state policy management** / 三态策略管理 (active/candidate/archived)
- **Versioned assets** / 版本化资产
- **Safe promotion process** / 安全的升级流程

### ✅ Failure Learning / 失败学习
- **Learn from both success and failure** / 从成功和失败中学习
- **Fallback strategies** / 回退策略
- **Avoid repeated mistakes** / 避免重复错误

---

## System Architecture / 系统架构

```
User Task
    ↓
Task Classifier
    ↓  
Policy Router  
    ↓
Skill Selector
    ↓
Workflow Selector  
    ↓
Executor
    ↓
Trajectory Logger
    ↓
Critic / Evaluator
    ↓
Policy Updater
    ↓
Update Qdrant + Policy Files
```

---

## Directory Structure / 目录结构

```
.openclaw/
├── agents/
│   ├── main/                 # Main execution logic
│   ├── planner/              # Task planning and resource selection  
│   ├── reflector/            # Post-execution reflection
│   ├── synthesizer/          # Skill and workflow synthesis
│   ├── comparator/           # Workflow quality comparison
│   ├── optimizer/            # Policy optimization
│   ├── classifier/           # Task type classification (v3)
│   ├── critic/               # Policy quality evaluation (v3)
│   ├── policy_router/        # Policy-based routing (v3)
│   └── fallback_manager/     # Fallback strategy management (v3)
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
│   ├── task_policy.json      # Task type → default route mapping
│   ├── skill_policy.json     # Task type → preferred skill mapping  
│   ├── workflow_policy.json  # Task type → preferred workflow mapping
│   ├── tool_policy.json      # Task type → preferred tool order mapping
│   ├── fallback_policy.json  # Task type → fallback strategy mapping (v3)
│   └── history/              # Policy update history
├── logs/
│   ├── trajectories/         # Complete execution trajectories
│   ├── rewards/              # Reward and scoring logs
│   ├── reflections/          # Reflection results
│   ├── evaluations/          # Evaluation results
│   ├── daily_reports/        # Daily evolution reports
│   ├── policy_updates/       # Policy update logs (v3)
│   ├── critic/               # Critic evaluation logs (v3)
│   └── routing/              # Routing decision logs (v3)
├── reports/
│   └── evolution/            # Evolution analysis reports
├── scripts/
│   ├── evolve/               # Evolution-related scripts
│   ├── reflect/              # Reflection scripts
│   ├── evaluate/             # Evaluation scripts
│   ├── dedup/                # Deduplication scripts
│   ├── backup/               # Backup scripts
│   └── daily_evolution_loop.py # Daily evolution scheduler (v3)
└── config/
    ├── qdrant.json           # Qdrant configuration
    ├── thresholds.json       # Scoring and quality thresholds
    ├── models.json           # Model configuration
    └── evolution.json        # Evolution system configuration
```

---

## Qdrant Collections / Qdrant 集合

### Core Collections / 核心集合
- **skills**: Reusable skill definitions / 可复用技能定义
- **workflows**: Task-type specific workflows / 任务类型特定工作流  
- **experiences**: High-value experience records / 高价值经验记录
- **trajectories**: Complete execution trajectories / 完整执行轨迹

### v3 Additional Collections / v3 新增集合
- **policies**: Task → skill/workflow/tool order mappings / 任务到技能/工作流/工具顺序的映射
- **failures**: High-value failure samples for learning / 用于学习的高价值失败样本

---

## Usage / 使用方法

### Minimal Viable Loop / 最小可用闭环

#### v1 Workflow:
```python
# Execute task → Log trajectory → Store experience
trajectory = logger.log_trajectory(task, steps, success, score)
experience = experience_manager.store_experience(trajectory, reflection)
```

#### v2 Workflow:  
```python
# Execute task → Compare workflows → Synthesize skill → Optimize policy
trajectories = [trajectory1, trajectory2, trajectory3]
best_workflow = comparator.compare_workflows(trajectories)
skill = synthesizer.synthesize_skill(trajectories, task_type)
policy_optimizer.optimize_policy(task_type, trajectories, skill)
```

#### v3 Workflow:
```python
# Classify task → Route policy → Execute → Evaluate policy → Update policy
task_type = classifier.classify_task(task)
routing_decision = router.route_task(task_type)
trajectory = execute_and_log(task, routing_decision)
policy_evaluation = critic.evaluate_policy_quality(trajectory, routing_decision)  
policy_updater.update_policy(task_type, policy_evaluation, trajectory)
```

---

## Configuration / 配置

### Scoring Thresholds / 评分阈值
- **Experience Storage**: `final_score >= 0.8`
- **Skill Generation**: `min_similar_tasks >= 3` and `avg_score >= 0.7`
- **Policy Promotion**: `min_evidence_count >= 5` and `confidence_threshold >= 0.85`

### Policy Update Rules / 策略更新规则
- **Candidate Creation**: At least 3 successful executions
- **Active Promotion**: At least 5 successful executions with continuous improvement
- **Fallback Trigger**: 2 consecutive failures on current policy

---

## Stability Guarantees / 稳定性保证

### What v3 Does / v3 做什么
✅ Learn from repeated successful patterns / 从重复成功模式中学习  
✅ Maintain explainable decision logs / 维护可解释的决策日志
✅ Support safe rollback to previous versions / 支持安全回滚到先前版本
✅ Handle failures gracefully with fallbacks / 优雅处理失败并提供回退
✅ Evolve policies slowly and safely / 缓慢而安全地进化策略

### What v3 Never Does / v3 从不做什么  
❌ Train model weights / 训练模型权重
❌ Replace active policies after single success / 单次成功后替换活跃策略
❌ Make decisions without explanations / 无解释的决策
❌ Lose historical policy versions / 丢失历史策略版本
❌ Ignore failure patterns / 忽略失败模式

---

## Success Metrics / 成功指标

When v3 is working correctly, you'll observe:

### v3 正常工作时的表现：

1. **Consistent Skill Selection** / 一致的技能选择
   - Similar tasks consistently select the same skill
   - 相似任务始终选择相同的技能

2. **Stable Workflow Execution** / 稳定的工作流执行  
   - Tasks follow consistent execution patterns
   - 任务遵循一致的执行模式

3. **Optimized Tool Order** / 优化的工具顺序
   - Tool sequences become more efficient over time
   - 工具序列随时间变得更加高效

4. **Automatic Policy Evolution** / 自动策略进化
   - Policy files continuously improve without manual intervention
   - 策略文件在无人工干预的情况下持续改进

5. **Intelligent Fallback Usage** / 智能回退使用
   - System automatically switches to fallback paths when needed
   - 系统在需要时自动切换到回退路径

---

## Repository Structure / 仓库结构

This repository follows a clear versioned evolution:

### 仓库遵循清晰的版本演进：

- **v1.0**: Memory Layer implementation / 记忆层实现
- **v2.0**: Skill Evolution Layer implementation / 技能进化层实现  
- **v3.0**: Policy Learning Layer implementation / 策略学习层实现

Each version builds upon the previous one while maintaining backward compatibility.

每个版本都在前一个版本的基础上构建，同时保持向后兼容性。

---

## Getting Started / 快速开始

1. **Clone the repository** / 克隆仓库
   ```bash
   git clone https://github.com/lst016/openclaw-skill-evolution.git
   ```

2. **Install dependencies** / 安装依赖
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install qdrant-client pyyaml
   ```

3. **Start Qdrant** / 启动 Qdrant
   ```bash
   docker run -d --name openclaw-skill-evolution-qdrant -p 6333:6333 qdrant/qdrant:latest
   ```

4. **Initialize collections** / 初始化集合
   ```bash
   python scripts/qdrant_setup.py
   ```

5. **Run integration tests** / 运行集成测试
   ```bash
   python scripts/v3_integration_test.py
   ```

---

## License / 许可证

MIT License - See LICENSE file for details.

MIT 许可证 - 详情见 LICENSE 文件。