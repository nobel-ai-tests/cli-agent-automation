---
name: parallel-orchestrator-learning
description: Orchestrates multiple sub-agents in parallel with a self-learning loop. Use when you need to run many tasks simultaneously while automatically learning from failures and successes to improve future agent instructions.
---

# Parallel Orchestrator Learning

## Overview
This skill enables the orchestration of multiple Gemini CLI instances in parallel using a Python-based controller. It includes a built-in "Self-Learning Loop" that analyzes execution logs and project outputs to synthesize lessons learned and inject them into future prompts.

## Workflow

1. **Setup**: Define tasks in a `projects.json` file.
2. **Execution**: Run the controller with a specified concurrency limit.
   ```bash
   python3 controller.py --max-workers 4
   ```
3. **Adaptive Throttling**: The controller automatically detects rate limits and reduces concurrency while retrying with exponential backoff.
4. **Post-Mortem**: After all tasks finish, the `critic_agent.py` script runs to analyze logs and project integrity.
5. **Instruction Injection**: Synthesized lessons are saved to `subagent_instructions.txt` and automatically included in subsequent agent prompts.

## Core Components

### Controller (`assets/controller.py`)
A Python orchestrator using `ThreadPoolExecutor` and a `rich` dashboard for real-time tracking.

### Critic Agent (`scripts/critic_agent.py`)
A script that uses Gemini to analyze `controller.log` and project directories to generate `LESSONS_LEARNED.md`.

### Learning Loop
The loop is closed by the `subagent_instructions.txt` file, which acts as a persistent memory for "best practices" discovered during execution.

## Guidelines for Sub-Agents
When running as a sub-agent under this orchestrator:
- Always start by creating a `README.md` with your plan.
- Be concise and focus on high-quality file generation.
- If you encounter errors, document them clearly in your output so the Critic Agent can learn from them.