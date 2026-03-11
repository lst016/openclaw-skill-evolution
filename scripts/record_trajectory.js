#!/usr/bin/env node

const fs = require('fs-extra');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

class TrajectoryLogger {
  constructor() {
    this.logsDir = path.join(process.cwd(), 'logs', 'trajectories');
    this.ensureLogsDirectory();
  }

  ensureLogsDirectory() {
    const today = new Date().toISOString().split('T')[0];
    const todayDir = path.join(this.logsDir, today);
    fs.ensureDirSync(todayDir);
  }

  createTrajectory(task, taskType, selectedSkill = null, selectedWorkflow = null) {
    const trajectoryId = uuidv4();
    const trajectory = {
      trajectory_id: trajectoryId,
      task: task,
      task_type: taskType,
      selected_skill: selectedSkill,
      selected_workflow: selectedWorkflow,
      steps: [],
      tools_used: [],
      outputs_summary: '',
      success: false,
      final_score: 0.0,
      duration_ms: 0,
      reflection_id: null,
      created_at: new Date().toISOString()
    };

    return trajectory;
  }

  addStep(trajectory, stepData) {
    // Validate step data structure
    const requiredFields = ['step', 'action', 'tool', 'input_summary', 'output_summary', 'success', 'score', 'duration_ms'];
    for (const field of requiredFields) {
      if (!(field in stepData)) {
        throw new Error(`Missing required field in step data: ${field}`);
      }
    }

    trajectory.steps.push(stepData);
    
    // Track tools used
    if (!trajectory.tools_used.includes(stepData.tool)) {
      trajectory.tools_used.push(stepData.tool);
    }

    return trajectory;
  }

  finalizeTrajectory(trajectory, success, finalScore, durationMs, outputsSummary) {
    trajectory.success = success;
    trajectory.final_score = finalScore;
    trajectory.duration_ms = durationMs;
    trajectory.outputs_summary = outputsSummary;

    // Save to file
    const today = new Date().toISOString().split('T')[0];
    const filePath = path.join(this.logsDir, today, `${trajectory.trajectory_id}.json`);
    fs.writeJsonSync(filePath, trajectory, { spaces: 2 });

    console.log(`Trajectory saved: ${filePath}`);
    return trajectory;
  }

  loadTrajectory(trajectoryId) {
    // Search through all date directories
    const dates = fs.readdirSync(this.logsDir);
    for (const date of dates) {
      const datePath = path.join(this.logsDir, date);
      const trajectoryPath = path.join(datePath, `${trajectoryId}.json`);
      if (fs.existsSync(trajectoryPath)) {
        return fs.readJsonSync(trajectoryPath);
      }
    }
    throw new Error(`Trajectory not found: ${trajectoryId}`);
  }
}

module.exports = TrajectoryLogger;