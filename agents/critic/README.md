# Critic Agent

## Overview
The Critic agent evaluates the **policy quality** of task executions, not just final success. It provides multi-dimensional feedback to guide policy learning.

## Key Features
- **Skill Fit Scoring**: Evaluates if the selected skill was appropriate for the task
- **Workflow Fit Scoring**: Assesses workflow efficiency and redundancy  
- **Tool Order Scoring**: Analyzes tool sequence effectiveness
- **Policy Reward Calculation**: Combines multiple dimensions into a final policy reward
- **Improvement Suggestions**: Provides actionable recommendations for policy optimization

## Input
- Trajectory data with execution details
- Selected skill/workflow/tool order
- Task classification results

## Output
- `skill_fit_score`: [-1.0, 1.0] - Skill appropriateness rating
- `workflow_fit_score`: [-1.0, 1.0] - Workflow efficiency rating  
- `tool_order_score`: [-1.0, 1.0] - Tool sequence effectiveness rating
- `final_policy_reward`: Combined policy quality score
- `suggested_adjustments`: Specific improvement recommendations

## Integration
The Critic works with Policy Updater to determine when candidate policies should be promoted to active status based on consistent high-quality performance.