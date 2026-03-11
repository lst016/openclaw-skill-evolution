---
name: openclaw-skill-evolution
description: OpenClaw Skill Evolution - 本地 Skill / Workflow 自进化层集成
metadata: {"openclaw":{"requires":{"bins":["python3", "git"]}}}
---

# OpenClaw Skill Evolution

**用途：** 在现有 OpenClaw 运行时中集成一套"本地 Skill / Workflow 自进化层"

## 核心功能

1. **skill memory** - 技能记忆存储与检索
2. **workflow memory** - 工作流记忆存储与检索  
3. **trajectory logging** - 任务轨迹记录
4. **reflection engine** - 任务反思引擎
5. **skill synthesizer** - 技能合成器
6. **policy updater** - 策略更新器
7. **qdrant vector memory backend** - 向量记忆后端

## 系统原则

- **不训练模型权重** - 只优化 skill/workflow/policy
- **资产跨模型复用** - 所有沉淀结果在模型升级后仍然可复用
- **版本化管理** - 所有 skill、workflow、policy 都可版本化、可回滚、可比较
- **去重优先** - 所有新增知识必须先去重再写入
- **证据驱动** - 所有 policy 更新必须基于重复成功证据

## 目录结构

按照方案要求创建完整的目录结构，包含 agents、skills、workflows、policies、logs、scripts、config 等模块。

## Qdrant 集成

使用 Qdrant 作为 vector memory backend，创建 skills、workflows、experiences、trajectories 四个 collections。

## 最小可用闭环

第一版实现核心闭环：
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

## 仓库地址

https://github.com/lst016/openclaw-skill-evolution.git

## 维护者

牛牛 🐮