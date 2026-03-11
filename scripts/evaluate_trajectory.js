#!/usr/bin/env node

const fs = require('fs').promises;
const path = require('path');

// Load scoring thresholds from config
const THRESHOLDS_PATH = path.join(__dirname, '..', 'config', 'thresholds.json');
let thresholds = {};

async function loadThresholds() {
  try {
    const thresholdsData = await fs.readFile(THRESHOLDS_PATH, 'utf8');
    thresholds = JSON.parse(thresholdsData).scoring;
  } catch (error) {
    console.warn('Could not load thresholds, using defaults:', error.message);
    // Default scoring rules as per the specification
    thresholds = {
      task_success: 1.0,
      task_failure: -1.0,
      validation_passed: 0.3,
      high_quality_result: 0.2,
      obvious_detour: -0.2,
      introduced_error: -0.5,
      no_validation: -0.2,
      correct_context: 0.1,
      correct_target: 0.1,
      effective_tool_call: 0.1,
      effective_modification: 0.2,
      completed_verification: 0.2,
      ineffective_search: -0.1,
      repeated_action: -0.1,
      wrong_tool: -0.2,
      circular_attempt: -0.3
    };
  }
}

/**
 * Evaluate a single step in a trajectory
 * @param {Object} step - Step object with action, tool, success, etc.
 * @returns {number} - Step score
 */
function evaluateStep(step) {
  let score = 0;
  
  // Base success/failure
  if (step.success) {
    score += 0.1; // Small base reward for successful step
  } else {
    score -= 0.2; // Penalty for failed step
  }
  
  // Tool-specific evaluations
  if (step.tool) {
    if (step.effective_tool_call) {
      score += thresholds.effective_tool_call || 0.1;
    }
    if (step.wrong_tool) {
      score += thresholds.wrong_tool || -0.2;
    }
  }
  
  // Action-specific evaluations
  if (step.action) {
    if (step.correct_context) {
      score += thresholds.correct_context || 0.1;
    }
    if (step.correct_target) {
      score += thresholds.correct_target || 0.1;
    }
    if (step.effective_modification) {
      score += thresholds.effective_modification || 0.2;
    }
    if (step.completed_verification) {
      score += thresholds.completed_verification || 0.2;
    }
    if (step.ineffective_search) {
      score += thresholds.ineffective_search || -0.1;
    }
    if (step.repeated_action) {
      score += thresholds.repeated_action || -0.1;
    }
    if (step.circular_attempt) {
      score += thresholds.circular_attempt || -0.3;
    }
  }
  
  return parseFloat(score.toFixed(2));
}

/**
 * Evaluate entire trajectory
 * @param {Object} trajectory - Complete trajectory object
 * @returns {Object} - Evaluation result with scores
 */
function evaluateTrajectory(trajectory) {
  // Task-level evaluation
  let taskScore = 0;
  
  if (trajectory.success) {
    taskScore += thresholds.task_success || 1.0;
    
    // Additional quality bonuses
    if (trajectory.validation_passed) {
      taskScore += thresholds.validation_passed || 0.3;
    }
    if (trajectory.high_quality_result) {
      taskScore += thresholds.high_quality_result || 0.2;
    }
    if (trajectory.obvious_detour) {
      taskScore += thresholds.obvious_detour || -0.2;
    }
  } else {
    taskScore += thresholds.task_failure || -1.0;
    
    if (trajectory.introduced_error) {
      taskScore += thresholds.introduced_error || -0.5;
    }
    if (!trajectory.validation_passed) {
      taskScore += thresholds.no_validation || -0.2;
    }
  }
  
  // Step-level evaluation
  let stepScores = [];
  let totalStepScore = 0;
  
  if (trajectory.steps && Array.isArray(trajectory.steps)) {
    for (const step of trajectory.steps) {
      const stepScore = evaluateStep(step);
      stepScores.push(stepScore);
      totalStepScore += stepScore;
    }
  }
  
  // Final score calculation
  const finalScore = parseFloat((taskScore + totalStepScore).toFixed(2));
  
  return {
    task_score: parseFloat(taskScore.toFixed(2)),
    step_scores: stepScores,
    total_step_score: parseFloat(totalStepScore.toFixed(2)),
    final_score: finalScore,
    evaluation_timestamp: new Date().toISOString()
  };
}

/**
 * Save evaluation result to file
 * @param {string} trajectoryId - Trajectory ID
 * @param {Object} evaluation - Evaluation result
 */
async function saveEvaluation(trajectoryId, evaluation) {
  const date = new Date().toISOString().split('T')[0];
  const evalDir = path.join(__dirname, '..', 'logs', 'evaluations', date);
  
  try {
    await fs.mkdir(evalDir, { recursive: true });
    const evalPath = path.join(evalDir, `${trajectoryId}.json`);
    await fs.writeFile(evalPath, JSON.stringify(evaluation, null, 2));
    console.log(`Evaluation saved to ${evalPath}`);
  } catch (error) {
    console.error('Failed to save evaluation:', error.message);
  }
}

// Main execution
async function main() {
  await loadThresholds();
  
  // If called directly with trajectory file
  if (process.argv.length > 2) {
    const trajectoryPath = process.argv[2];
    try {
      const trajectoryData = await fs.readFile(trajectoryPath, 'utf8');
      const trajectory = JSON.parse(trajectoryData);
      
      const evaluation = evaluateTrajectory(trajectory);
      console.log('Trajectory Evaluation Result:');
      console.log(JSON.stringify(evaluation, null, 2));
      
      // Save evaluation
      const trajectoryId = trajectory.trajectory_id || path.basename(trajectoryPath, '.json');
      await saveEvaluation(trajectoryId, evaluation);
      
    } catch (error) {
      console.error('Error evaluating trajectory:', error.message);
    }
  }
}

// Export for use as module
module.exports = {
  evaluateTrajectory,
  evaluateStep,
  saveEvaluation
};

// Run if called directly
if (require.main === module) {
  main().catch(console.error);
}