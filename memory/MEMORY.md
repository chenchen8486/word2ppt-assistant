# Claude Code Memory for word2ppt-assistant Project

## Project Overview
- Project Name: word2ppt-assistant
- Purpose: Converting Word documents to PowerPoint presentations using AI agents
- Key Feature: Structure document validation and optimized PPT layout

## Development Standards
The project follows Agent development engineering standards based on Anthropic and OpenAI research on harness engineering.

### Core Principles
1. **Harness/Testing Framework**:
   - Implement context bridging mechanisms for long-running agents
   - Use initializer agent pattern for environment setup
   - Ensure agent readability in code design

2. **Environment Feedback Loops**:
   - Maintain agent identity across sessions
   - Externalize state beyond single context windows
   - Implement closed human-AI feedback loops

3. **Engineering Quality Control**:
   - Build incremental progress mechanisms
   - Use repository as system of record
   - Implement verification mechanisms for agent-generated code

### Specific Development Directives
- Establish test cases before implementing parsing logic
- Include self-check functionality in code
- Implement state persistence mechanisms
- Design for testability and error recovery
- Create standardized logging for agent operations