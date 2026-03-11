# Policy Updater Agent

## Overview / 概述

The Policy Updater manages the **three-state policy lifecycle** (active/candidate/archived) and handles stable policy updates based on repeated validation evidence.

## Functionality / 功能特性

### Core Responsibilities / 核心职责
- **Candidate Policy Creation**: Generate candidate policies from successful trajectories
- **Validation Management**: Ensure candidates meet strict quality thresholds before promotion
- **Active Policy Promotion**: Promote validated candidates to active status
- **Policy Archival**: Archive historical policies for rollback capability
- **Version Control**: Maintain version history for all policy types

### Stability Mechanisms / 稳定性机制
- **Minimum Evidence Requirement**: At least 3 successful executions for candidate generation
- **Promotion Threshold**: At least 5 successful executions with consistent improvement
- **Continuous Improvement Requirement**: New policy must outperform current policy across multiple metrics
- **Rollback Support**: All policy versions are archived and can be restored

## Input / 输入

```python
# Policy update request
{
    "task_type": "debugging",
    "trajectories": [...],  # List of successful trajectories
    "critic_results": [...]  # Corresponding critic evaluations
}
```

## Output / 输出

```python
# Policy update result
{
    "updated": true,
    "new_status": "candidate|active|archived",
    "version": 2,
    "reason": "Candidate meets all promotion criteria"
}
```

## Configuration / 配置

### Promotion Thresholds / 晋升阈值

Located in `config/thresholds.json`:

```json
{
  "policy": {
    "min_evidence_count": 5,
    "confidence_threshold": 0.85,
    "success_rate_improvement": 0.1,
    "avg_score_improvement": 0.1
  }
}
```

## Usage / 使用方法

```python
from agents.policy_updater.policy_updater import PolicyUpdater

updater = PolicyUpdater()

# Update policy for a task type
success = updater.update_policy_from_trajectories(
    task_type="debugging",
    trajectories=recent_trajectories
)

# Promote candidate to active
if success:
    updater.promote_candidate_to_active(candidate, "skill_policy")
```

## Policy Lifecycle / 策略生命周期

```
candidate (under validation)
    ↓
meets all promotion criteria
    ↓
active (currently used)
    ↓
new candidate generated
    ↓
archived (historical version)
```

## Design Principles / 设计原则

1. **Evidence-Based**: Only update policies based on repeated successful evidence
2. **Stable Updates**: Avoid single-success policy changes
3. **Explainable**: Every policy update includes clear reasoning
4. **Rollbackable**: All historical versions are preserved
5. **Versioned**: Every policy change increments version number