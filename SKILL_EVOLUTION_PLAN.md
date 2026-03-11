# OpenClaw Skill Evolution 完整集成方案

目标

在现有 OpenClaw 运行时中集成一套“本地 Skill / Workflow 自进化层”。

该系统的目标不是训练模型参数，而是持续优化以下对象：

1. skill
2. workflow
3. tool usage order
4. agent execution policy
5. experience memory
6. reflection quality

系统必须做到：

1. 不训练模型权重
2. 不使用 PPO / GRPO / LoRA / Fine-tuning
3. 仅通过任务执行轨迹、反思、经验沉淀和策略更新实现自进化
4. 所有沉淀结果在模型升级后仍然可复用
5. 所有 skill、workflow、policy 都可版本化、可回滚、可比较

一、系统定位

这是一个集成在 OpenClaw 内部的 Skill Evolution Layer。

OpenClaw 仍然是主运行时与主 agent。
新增的只是：

1. skill memory
2. workflow memory
3. trajectory logging
4. reflection engine
5. skill synthesizer
6. policy updater
7. qdrant vector memory backend

系统不替换 OpenClaw，不独立构建新的 agent 平台，只扩展 OpenClaw 的能力。

二、核心原则

1. 模型不是资产
2. skill 是资产
3. workflow 是资产
4. policy 是资产
5. experience 是资产
6. 所有资产必须跨模型复用
7. 所有新增知识必须先去重再写入
8. 所有 policy 更新必须基于重复成功证据
9. 系统优先追求稳定可解释，不追求复杂训练

三、OpenClaw 扩展后的总体流程

用户任务
↓
OpenClaw main agent
↓
planner
↓
search skills from qdrant
↓
search workflows from qdrant
↓
search experiences from qdrant
↓
select best skill / workflow
↓
execute tools
↓
record trajectory
↓
run reflection
↓
evaluate result
↓
generate / update experience
↓
generate / update skill
↓
update policies
↓
save all outputs

四、目录结构要求

请在现有 OpenClaw workspace 中新增以下目录结构：

.openclaw/
agents/
main/
planner/
reflector/
synthesizer/
skills/
generated/
manual/
archived/
templates/
workflows/
generated/
preferred/
archived/
task_types/
memory/
qdrant/
schemas/
collections/
snapshots/
embeddings/
cache/
policies/
task_policy.json
skill_policy.json
tool_policy.json
routing_policy.json
logs/
trajectories/
rewards/
reflections/
evaluations/
daily_reports/
reports/
evolution/
scripts/
evolve/
reflect/
evaluate/
dedup/
backup/
config/
qdrant.json
thresholds.json
models.json
evolution.json

五、Qdrant 集成要求

必须使用 Qdrant 作为 vector memory backend。

请创建以下 collections：

1. skills
2. workflows
3. experiences
4. trajectories

所有与 skill、workflow、experience 的检索、去重、候选匹配、相似推荐，都必须通过 Qdrant 完成。

Qdrant 的职责：

1. skill 检索
2. workflow 检索
3. experience 检索
4. 去重候选检索
5. 相似任务轨迹检索
6. 为 planner 提供历史成功模式

六、Collection 设计

1. skills collection

作用：
存放可复用 skill。

payload 字段要求：

skill_id
skill_name
description
applicable_when
steps
required_tools
success_rate
avg_score
usage_count
version
status
source
tags
created_at
updated_at

embedding 内容要求：

skill_name + description + applicable_when + tags

用途：
根据任务语义检索最匹配 skill。

2. workflows collection

作用：
存放 task type 对应 workflow。

payload 字段要求：

workflow_id
task_type
description
steps
tool_order
success_rate
avg_score
usage_count
version
status
source_skill_id
created_at
updated_at

embedding 内容要求：

task_type + description + steps + tool_order

用途：
为 planner 提供默认执行路径，为 skill updater 提供比较对象。

3. experiences collection

作用：
存放高价值经验。

payload 字段要求：

experience_id
title
problem_summary
solution_summary
workflow
score
success_count
fail_count
last_used_at
source_trajectory_id
tags
status
created_at
updated_at

embedding 内容要求：

title + problem_summary + solution_summary + tags

用途：
给 planner、reflector、synthesizer 提供历史经验参考，并用于去重合并。

4. trajectories collection

作用：
存放完整任务轨迹。

payload 字段要求：

trajectory_id
task
task_type
selected_skill
selected_workflow
steps
tools_used
outputs_summary
success
final_score
duration_ms
reflection_id
created_at

embedding 内容建议：

task + task_type + outputs_summary

用途：
支持相似任务检索、workflow 提炼、skill 生成与统计分析。

七、Skill 文件格式要求

每个 skill 必须同时：

1. 存本地 yaml 文件
2. 写入 Qdrant skills collection

skill yaml 结构要求：

skill_name:
description:
applicable_when:
steps:
required_tools:
success_rate:
avg_score:
usage_count:
version:
status:
tags:
created_at:
updated_at:

要求：

1. steps 必须是可执行步骤序列
2. required_tools 必须列出常用工具
3. applicable_when 必须描述适用场景
4. status 至少支持 active / archived
5. version 必须递增

文件命名规则：

skills/generated/{skill-name}.v{version}.yaml

八、Workflow 文件格式要求

每个 workflow 必须同时：

1. 存本地 yaml 文件
2. 写入 Qdrant workflows collection

workflow yaml 结构要求：

task_type:
description:
steps:
tool_order:
success_rate:
avg_score:
usage_count:
version:
status:
source_skill_id:
created_at:
updated_at:

要求：

1. workflow 只表达执行顺序，不表达大段解释
2. tool_order 必须单独维护
3. version 必须递增
4. 可以独立于 skill 存在

文件命名规则：

workflows/task_types/{task-type}.v{version}.yaml

九、Trajectory 日志要求

每次任务执行结束后，必须生成一条 trajectory 日志。

日志必须保存到：

.openclaw/logs/trajectories/{date}/{trajectory_id}.json

trajectory 结构要求：

trajectory_id
task
task_type
selected_skill
selected_workflow
steps
tools_used
success
final_score
duration_ms
created_at

每个 step 必须包含：

step
action
tool
input_summary
output_summary
success
score
duration_ms

要求：

1. 每个工具调用都要映射到 step
2. 每个 step 都要有局部分
3. 所有 trajectory 都要保留，不允许只保留成功案例

十、评分机制要求

系统必须实现双层评分：

1. 任务总分

2. 步骤局部分

3. 任务总分建议规则

任务成功：+1.0
任务失败：-1.0
验证通过：+0.3
结果质量高：+0.2
明显绕路：-0.2
引入错误：-0.5
未验证：-0.2

2. 步骤分建议规则

命中正确上下文：+0.1
识别正确目标：+0.1
有效工具调用：+0.1
有效修改：+0.2
完成验证：+0.2
无效搜索：-0.1
重复动作：-0.1
错误工具：-0.2
循环尝试：-0.3

最终分数公式：

final_score = task_score + sum(step_scores) + quality_adjustment

要求：

1. final_score 必须写入 trajectory
2. 每个 step 的 score 必须保留
3. evaluator 必须可配置阈值

十一、Planner 集成要求

OpenClaw 在执行任务前必须先经过 planner。

planner 的职责：

1. 识别 task_type
2. 检索相似 skill
3. 检索相似 workflow
4. 检索相似 experience
5. 生成候选执行计划
6. 选择最优 skill / workflow 组合

planner 输出至少包含：

task_type
candidate_skills
candidate_workflows
selected_skill
selected_workflow
planned_steps
planned_tool_order

要求：

1. planner 优先复用高成功率 skill
2. planner 必须支持 fallback
3. 如果无合适 skill，则生成基础 workflow

十二、Reflection 集成要求

每次任务完成后，必须运行 reflection。

reflector 的职责：

1. 判断哪些步骤有效
2. 判断哪些步骤无效
3. 判断是否存在冗余步骤
4. 判断 workflow 是否需要优化
5. 判断是否值得生成 experience
6. 判断是否值得生成 skill

reflection 输出至少包含：

success_reason
failure_risk
best_steps
redundant_steps
missing_steps
optimized_workflow
should_store_experience
should_generate_skill
improvement_notes

保存路径：

.openclaw/logs/reflections/{date}/{trajectory_id}.json

十三、Experience 写入规则

不是所有任务都写入 experience。

只有同时满足以下条件才允许写入：

1. success = true
2. final_score >= 0.8
3. reflection 判断 should_store_experience = true
4. workflow 清晰可复用
5. 不是低价值琐碎结果

写入前必须先去重。

流程要求：

生成 experience summary
↓
embedding
↓
在 experiences collection 检索 top candidates
↓
判断 similarity 是否超过阈值
↓
若超过阈值则 merge
↓
否则 insert

相似度阈值建议：

0.88 ~ 0.92

merge 时必须：

1. success_count +1
2. 更新 score
3. 更新 solution_summary
4. 更新 workflow
5. 更新 last_used_at
6. 保留历史版本信息

十四、Skill 生成规则

skill 不是每个任务都生成。

只有当某类任务在多次执行中呈现稳定高分 workflow 时，才允许生成新 skill。

建议条件：

1. 同类任务成功次数 >= 3
2. workflow 基本一致
3. 平均分高于阈值
4. 工具顺序稳定
5. reflection 判断 should_generate_skill = true

生成流程要求：

读取一组相似高分 trajectories
↓
抽取共同步骤
↓
去掉偶然步骤
↓
总结 applicable_when
↓
生成 skill yaml
↓
写本地 skill 文件
↓
写入 skills collection
↓
更新 skill policy

十五、Skill 更新规则

若已存在相关 skill，新 workflow 不应直接覆盖旧 skill。

必须比较以下维度：

1. success_rate
2. avg_score
3. workflow 长度
4. 错误率
5. 验证完整性

只有满足以下条件时才允许升级：

1. new_success_rate > old_success_rate
2. new_avg_score > old_avg_score
3. new workflow 不显著更长
4. 新 workflow 更稳定

升级流程要求：

1. version + 1
2. 旧版本移入 archived
3. 新版本写入 generated
4. 更新 qdrant skills collection
5. 更新 skill_policy.json

十六、Policy 系统要求

必须维护四类 policy：

1. task_policy

2. skill_policy

3. tool_policy

4. routing_policy

5. task_policy

作用：
task_type -> preferred_workflow

2. skill_policy

作用：
task_type -> preferred_skill

3. tool_policy

作用：
task_type -> preferred_tool_order

4. routing_policy

作用：
task_type -> planner / executor / fallback strategy

要求：

1. policy 更新必须基于重复成功证据
2. policy 文件必须支持回滚
3. policy 更新必须有日志记录
4. policy 不能基于单次偶然成功直接替换

十七、每日进化循环要求

系统必须支持每日或定期批处理进化。

每日循环流程：

1. 读取当天 trajectories
2. 按 task_type 分组
3. 统计 success_rate
4. 找出高分 workflow
5. 找出低分 workflow
6. 提炼新 experience
7. 合并或新增 experience
8. 生成 skill 候选
9. 比较并升级 skill
10. 更新 policy
11. 生成 daily report

daily report 必须包含：

新增 experience 数量
合并 experience 数量
新增 skill 数量
升级 skill 数量
淘汰 workflow 数量
最稳定 workflow
最差 workflow
建议优化项

保存路径：

.openclaw/logs/daily_reports/{date}.md

十八、Tool 扩展要求

请为 OpenClaw 增加以下内部工具或模块接口：

1. search_skill
2. search_workflow
3. search_experience
4. save_trajectory
5. reflect_task
6. generate_skill
7. update_skill
8. update_policy
9. merge_experience
10. snapshot_qdrant

这些工具不必都暴露给最终用户，但必须能被内部 agent / scheduler 调用。

十九、本地模型职责要求

本地模型只做以下事情：

1. planner reasoning
2. reflection
3. trajectory summarization
4. experience merge judgment
5. skill synthesis
6. workflow comparison
7. policy recommendation

本地模型不做：

1. 权重训练
2. 强化学习参数更新
3. 长周期训练任务

二十、最小可用闭环要求

第一版只需要实现以下闭环：

1. 执行任务并记录 trajectory
2. 任务结束后做 reflection
3. 高分任务提炼 experience 并写入 qdrant
4. 当 3 个以上相近高分 trajectories 出现时生成 skill
5. skill 稳定后更新 policy

只要这个闭环跑通，就算完成第一版 Skill Evolution 系统。

二十一、脚本与模块建议

请优先实现以下脚本或模块：

evaluate_trajectory
reflect_task
merge_experience
generate_skill
update_policy
snapshot_qdrant
daily_evolution_runner

二十二、实现顺序要求

建议按以下顺序落地：

1. 接入 Qdrant
2. 建 collection schema
3. 记录 trajectory
4. 实现 evaluator
5. 实现 reflector
6. 实现 experience 去重写入
7. 实现 planner 检索 skill / workflow / experience
8. 实现 skill 生成
9. 实现 policy 更新
10. 实现 daily evolution loop

二十三、最终产物要求

该系统最终必须沉淀以下资产：

1. skills
2. workflows
3. experiences
4. policies
5. reflections
6. evolution reports

这些资产必须满足：

1. 可版本化
2. 可回滚
3. 可比较
4. 可跨模型复用
5. 可跨机器迁移

二十四、禁止事项

禁止：

1. 训练模型权重
2. 引入 LoRA / PPO / GRPO / SFT
3. 把 skill 进化逻辑写死在单个 prompt 中
4. 不做去重就无限写入经验
5. 基于一次成功立即改 policy
6. 不保存历史版本直接覆盖 skill

二十五、执行目标

Goal:
Integrate a local skill evolution layer into the existing OpenClaw runtime.

Requirements:

1. Use Qdrant as the vector memory backend
2. Create collections for skills, workflows, experiences, and trajectories
3. Record every task trajectory with step-level details
4. Implement task-level and step-level scoring
5. Run reflection after each task
6. Store only high-value experiences after deduplication
7. Generate reusable skills from repeated successful workflows
8. Version skills and workflows
9. Maintain task_policy, skill_policy, tool_policy, and routing_policy
10. Run a daily evolution loop to update skills and policies
11. Keep all generated assets reusable across model upgrades
12. Do not train model weights

二十六、补充要求

请基于我现有的 OpenClaw 工程方式落地，不要新起一套完全独立的 agent 框架。
优先做“与现有 OpenClaw 兼容的最小侵入式集成”。
所有新增模块都应围绕 OpenClaw 当前运行时扩展，而不是替换它。