# Task Classifier

## Overview
The Task Classifier maps user tasks to standardized task types for consistent policy routing.

## Functionality
- **Input**: Raw user task description
- **Output**: Standardized task_type with confidence score and reasoning
- **Purpose**: Enable consistent policy application across similar tasks

## Usage
```python
from agents.classifier.task_classifier import TaskClassifier

classifier = TaskClassifier()
result = classifier.classify_task("Debug a Python application error")
# Returns: {"task_type": "debugging", "confidence": 0.85, "reason": "Contains debug keywords"}
```

## Configuration
Task taxonomy is maintained in `config/task_taxonomy.json` to prevent unlimited task type proliferation.

## Design Principles
- **Standardization**: Only predefined task types are allowed
- **Explainability**: Every classification includes reasoning
- **Stability**: Prevents random task type generation