# Main Agent - Trajectory Logger

## Overview / 概述

The Main Agent's Trajectory Logger is the foundational component that records **complete task execution trajectories** with enhanced v3 metadata (skill_id, workflow_id, task_type).

## Functionality / 功能特性

### Core Responsibilities / 核心职责
- **Trajectory Recording**: Capture every execution with step-level details
- **Enhanced Metadata**: Store v3 metadata (skill_id, workflow_id, task_type)
- **Dual Storage**: Save trajectories to both local files and Qdrant
- **Validation**: Ensure trajectory data integrity and completeness
- **Quality Control**: Maintain high-quality trajectory data for learning

### v3 Enhanced Fields / v3 增强字段
- `skill_id`: Unique identifier for the skill used
- `skill_name`: Human-readable skill name
- `workflow_id`: Unique identifier for the workflow used  
- `workflow_name`: Human-readable workflow name
- `task_type`: Standardized task classification
- `reflection_id`: Reference to reflection analysis

## Trajectory Structure / 轨迹结构

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

## Usage / 使用方法

```python
from agents.main.trajectory_logger_v2 import TrajectoryLoggerV2

logger = TrajectoryLoggerV2()

trajectory = logger.log_trajectory(
    task="Debug Python application error",
    task_type="debugging",
    skill_name="structured_debugging",
    workflow_name="debug_workflow_v1",
    steps=[...],
    tools_used=["read", "edit", "exec"],
    outputs_summary="Successfully debugged and fixed the error",
    success=True,
    final_score=1.8
)
```

## Storage / 存储位置

### Local Storage / 本地存储
- Files: `~/.openclaw/workspace/logs/trajectories/YYYY-MM-DD/{trajectory_id}.json`
- Date-based organization for easy querying

### Qdrant Storage / Qdrant 存储
- Collection: `trajectories`
- Embedding: `task + task_type + outputs_summary`
- Payload: Complete trajectory data with v3 metadata

## Data Integrity / 数据完整性

- **Validation**: Every step must have required fields before storage
- **Timestamping**: All trajectories include created_at timestamp
- **Version Compatibility**: Supports both v1 (basic) and v2/v3 (enhanced) formats
- **Deduplication**: Prevents duplicate trajectory storage using trajectory_id