#!/usr/bin/env node

const fs = require('fs').promises;
const path = require('path');

/**
 * Reflection Engine for OpenClaw Skill Evolution
 * Analyzes task trajectories and generates insights for skill/workflow improvement
 */

class Reflector {
  constructor() {
    this.thresholds = {
      minScoreForExperience: 0.8,
      minSuccessCountForSkill: 3,
      workflowConsistency: 0.8
    };
  }

  /**
   * Run reflection on a completed task trajectory
   * @param {Object} trajectory - The completed task trajectory
   * @returns {Object} Reflection results
   */
  async reflect(trajectory) {
    console.log(`Running reflection on trajectory: ${trajectory.trajectory_id}`);
    
    const reflection = {
      trajectory_id: trajectory.trajectory_id,
      timestamp: new Date().toISOString(),
      success_reason: '',
      failure_risk: '',
      best_steps: [],
      redundant_steps: [],
      missing_steps: [],
      optimized_workflow: [],
      should_store_experience: false,
      should_generate_skill: false,
      improvement_notes: []
    };

    // Analyze success/failure
    if (trajectory.success) {
      reflection.success_reason = this.analyzeSuccess(trajectory);
      reflection.should_store_experience = this.shouldStoreExperience(trajectory);
    } else {
      reflection.failure_risk = this.analyzeFailure(trajectory);
    }

    // Analyze steps
    const stepAnalysis = this.analyzeSteps(trajectory.steps);
    reflection.best_steps = stepAnalysis.best_steps;
    reflection.redundant_steps = stepAnalysis.redundant_steps;
    reflection.missing_steps = stepAnalysis.missing_steps;
    reflection.optimized_workflow = stepAnalysis.optimized_workflow;

    // Determine if skill generation is warranted
    reflection.should_generate_skill = await this.shouldGenerateSkill(trajectory);

    // Generate improvement notes
    reflection.improvement_notes = this.generateImprovementNotes(reflection);

    return reflection;
  }

  /**
   * Analyze why a task succeeded
   * @param {Object} trajectory
   * @returns {string}
   */
  analyzeSuccess(trajectory) {
    const reasons = [];
    
    if (trajectory.final_score >= 0.9) {
      reasons.push('High quality result with excellent execution');
    }
    
    if (trajectory.steps.some(step => step.score >= 0.3)) {
      reasons.push('Effective tool usage and step execution');
    }
    
    if (trajectory.tools_used.length <= 5) {
      reasons.push('Efficient tool usage without unnecessary calls');
    }
    
    return reasons.join(', ') || 'Task completed successfully';
  }

  /**
   * Analyze why a task failed
   * @param {Object} trajectory
   * @returns {string}
   */
  analyzeFailure(trajectory) {
    const risks = [];
    
    if (trajectory.final_score <= -0.5) {
      risks.push('Significant errors or wrong tool usage');
    }
    
    const failedSteps = trajectory.steps.filter(step => !step.success);
    if (failedSteps.length > 0) {
      risks.push(`${failedSteps.length} steps failed during execution`);
    }
    
    if (trajectory.tools_used.length > 10) {
      risks.push('Excessive tool usage indicating poor planning');
    }
    
    return risks.join(', ') || 'Task failed to complete successfully';
  }

  /**
   * Determine if experience should be stored
   * @param {Object} trajectory
   * @returns {boolean}
   */
  shouldStoreExperience(trajectory) {
    return trajectory.success && 
           trajectory.final_score >= this.thresholds.minScoreForExperience &&
           trajectory.steps.length > 0;
  }

  /**
   * Analyze individual steps for optimization opportunities
   * @param {Array} steps
   * @returns {Object}
   */
  analyzeSteps(steps) {
    const analysis = {
      best_steps: [],
      redundant_steps: [],
      missing_steps: [],
      optimized_workflow: []
    };

    steps.forEach((step, index) => {
      if (step.score >= 0.2) {
        analysis.best_steps.push(index);
        analysis.optimized_workflow.push(step);
      }
      
      if (step.score <= -0.1) {
        analysis.redundant_steps.push(index);
        // Don't include low-scoring steps in optimized workflow
      }
    });

    // Check for missing validation steps
    const hasValidation = steps.some(step => 
      step.action.toLowerCase().includes('validate') || 
      step.action.toLowerCase().includes('verify')
    );
    
    if (!hasValidation && steps.length > 2) {
      analysis.missing_steps.push('validation_step');
    }

    return analysis;
  }

  /**
   * Determine if a new skill should be generated
   * This would typically check historical data, but for now we'll use a simple heuristic
   * @param {Object} trajectory
   * @returns {Promise<boolean>}
   */
  async shouldGenerateSkill(trajectory) {
    // In a real implementation, this would query the trajectories collection
    // to see if similar successful trajectories exist
    
    // For now, we'll use a simple heuristic based on task type frequency
    // This would be enhanced with actual historical data lookup
    const taskType = trajectory.task_type;
    
    // Simulate checking if this task type has been successful before
    // In reality, this would query Qdrant for similar trajectories
    const simulatedSuccessCount = Math.floor(Math.random() * 5); // Random for demo
    
    return simulatedSuccessCount >= this.thresholds.minSuccessCountForSkill &&
           trajectory.final_score >= 0.85;
  }

  /**
   * Generate improvement notes based on reflection results
   * @param {Object} reflection
   * @returns {Array}
   */
  generateImprovementNotes(reflection) {
    const notes = [];
    
    if (reflection.redundant_steps.length > 0) {
      notes.push('Consider removing redundant steps to improve efficiency');
    }
    
    if (reflection.missing_steps.length > 0) {
      notes.push('Add validation steps to ensure result quality');
    }
    
    if (reflection.should_generate_skill) {
      notes.push('This workflow pattern appears stable enough to generate a reusable skill');
    }
    
    if (reflection.should_store_experience) {
      notes.push('High-value experience worth storing for future reference');
    }
    
    return notes;
  }

  /**
   * Save reflection results to log file
   * @param {Object} reflection
   */
  async saveReflection(reflection) {
    const dateStr = new Date().toISOString().split('T')[0];
    const logDir = path.join(process.cwd(), 'logs', 'reflections', dateStr);
    
    try {
      await fs.mkdir(logDir, { recursive: true });
      const filePath = path.join(logDir, `${reflection.trajectory_id}.json`);
      await fs.writeFile(filePath, JSON.stringify(reflection, null, 2));
      console.log(`Reflection saved to: ${filePath}`);
    } catch (error) {
      console.error('Failed to save reflection:', error);
    }
  }
}

// CLI interface
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('Usage: node reflect_task.js <trajectory-file-path>');
    process.exit(1);
  }
  
  const trajectoryPath = args[0];
  
  fs.readFile(trajectoryPath, 'utf8')
    .then(data => {
      const trajectory = JSON.parse(data);
      const reflector = new Reflector();
      
      return reflector.reflect(trajectory);
    })
    .then(async (reflection) => {
      console.log('Reflection Results:');
      console.log(JSON.stringify(reflection, null, 2));
      
      // Save reflection
      const reflector = new Reflector();
      await reflector.saveReflection(reflection);
    })
    .catch(error => {
      console.error('Error running reflection:', error);
      process.exit(1);
    });
}

module.exports = Reflector;