# Subagent Evolution Framework

A framework for enabling continuous evolution and improvement of OpenClaw subagents through self-assessment, experience extraction, and configuration optimization.

## Features

- **Self-Assessment**: Automatically evaluate subagent performance across multiple dimensions
- **Experience Extraction**: Extract reusable patterns from completed tasks
- **Configuration Optimization**: Optimize skill configurations based on performance data
- **Standardized Interfaces**: Consistent CLI interface for all evolution operations

## Getting Started

```bash
# Clone the repository
git clone <repository-url>
cd subagent-evolution

# Install dependencies
npm install

# Run self-assessment
node index.js self-assess --days=7

# Extract experiences
node index.js extract-experience --days=7

# Optimize configurations
node index.js optimize-config
```

## API Reference

### Self-Assessment

Evaluates subagent performance across key dimensions:

- Code Generation (0-100)
- Error Handling (0-100) 
- Performance Optimization (0-100)
- Learning Capability (0-100)
- Browser Automation (0-100)
- Memory Management (0-100)

### Experience Extraction

Extracts reusable patterns from task completion logs and stores them in standardized format.

### Configuration Optimization

Analyzes skill usage patterns and suggests configuration improvements.

## Contributing

This project is designed to be integrated into the OpenClaw ecosystem. Contributions welcome!

## License

MIT