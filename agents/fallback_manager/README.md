# Fallback Manager Agent

## Overview / 概述

The Fallback Manager handles policy underperformance by providing **automatic fallback strategies** when current policies fail repeatedly.

## Functionality / 功能特性

### Core Responsibilities / 核心职责
- **Failure Detection**: Monitor policy performance and detect degradation
- **Fallback Triggering**: Automatically activate backup strategies when needed
- **Second-Best Solutions**: Identify and route to historically successful alternatives
- **Failure Learning**: Record high-value failures to avoid repeating mistakes
- **Tool Order Adjustment**: Optimize tool sequences based on failure patterns

### Fallback Criteria / 回退条件
- **Consecutive Failures**: 2 consecutive failures on current policy
- **High Failure Rate**: More than 50% failure rate in recent executions
- **Low Performance**: Critic scores consistently below threshold
- **Tool Issues**: Specific tools repeatedly causing failures

## Input / 输入

```python
# Fallback check request
{
    "task_type": "debugging",
    "recent_trajectories": [...],
    "current_policy_performance": 0.45
}
```

## Output / 输出

```python
# Fallback decision
{
    "fallback_needed": true,
    "fallback_skill": "basic_debugging.v1",
    "fallback_workflow": "safe_debug_workflow.v1",
    "reason": "Current policy has 3 consecutive failures"
}
```

## Usage / 使用方法

```python
from agents.fallback_manager.fallback_manager import FallbackManager

fallback_manager = FallbackManager()

# Check if fallback is needed
if fallback_manager.should_trigger_fallback(task_type, failure_count, consecutive_failures):
    fallback_strategy = fallback_manager.get_fallback_strategy(task_type)
    # Execute with fallback strategy
```

## Failure Analysis / 失败分析

The system analyzes failure patterns to:

1. **Identify Problematic Tools**: Tools that consistently fail
2. **Sequence Issues**: Tool order problems causing failures
3. **Skill Mismatches**: Skills that don't match task types
4. **Workflow Inefficiencies**: Unnecessary steps or redundant actions

## Integration / 集成

The Fallback Manager works with:
- **Policy Router**: To execute alternative routing strategies
- **Critic**: To evaluate why fallback was triggered
- **Policy Updater**: To deprioritize underperforming strategies

## Design Principles / 设计原则

1. **Safe Fallback**: Always provide a working alternative, never leave tasks hanging
2. **Learning from Failure**: Record and analyze failures to prevent recurrence
3. **History-Based**: Use historical second-best solutions as fallbacks
4. **Automatic Recovery**: Self-correcting when current policy underperforms
5. **Explainable**: Every fallback decision includes clear reasoning