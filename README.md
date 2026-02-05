# Gemini CLI Agent Automation

An advanced orchestrator for running multiple Gemini CLI agents in parallel with real-time tracking, automated post-mortems, and a web-based dashboard.

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Components](#components)
    - [The Controller](#the-controller)
    - [The Critic Agent](#the-critic-agent)
    - [Project Dashboard](#project-dashboard)
4. [Installation](#installation)
5. [Usage](#usage)
    - [Adding Projects](#adding-projects)
    - [Running the Controller](#running-the-controller)
    - [Web Dashboard](#web-dashboard)
6. [Self-Learning Loop](#self-learning-loop)
7. [Skill Integration](#skill-integration)

---

## Overview
This project provides a robust framework for automating complex software engineering tasks using the Gemini CLI. It allows users to define multiple tasks, execute them in isolated environments, and automatically learn from the outcomes to improve future performance.

## Architecture
The system is built around a parallel execution model:
- **Isolation:** Each project runs in its own subdirectory under `projects/`.
- **Parallelism:** Utilizes Python's `ThreadPoolExecutor` for concurrent agent execution.
- **Monitoring:** Real-time feedback via a CLI dashboard powered by the `rich` library.
- **Feedback:** A "Critic" agent analyzes logs to synthesize lessons learned.

## Components

### The Controller (`controller.py`)
The main entry point. It reads `projects.json`, manages the execution pool, and provides a live UI. It handles retries and captures agent output to extract progress steps.

### The Critic Agent (`critic_agent.py`)
A post-execution analyzer. It reviews the `controller.log` and the state of the `projects/` directory to identify what worked and what didn't.

### Project Dashboard
A web-based interface (`index.html`) that allows you to browse the results of your projects and their subdirectories.

## Installation

### Prerequisites
- Python 3.8+
- [Gemini CLI](https://github.com/google/gemini-cli)
- GitHub CLI (for repository management)

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/nobel-ai-tests/cli-agent-automation.git
   cd cli-agent-automation
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Adding Projects
Define your tasks in `projects.json`:
```json
[
  {
    "name": "refactor-api",
    "prompt": "Refactor the authentication module in the current directory."
  }
]
```

### Running the Controller
Execute all pending projects:
```bash
python3 controller.py --max-workers 2
```
Options:
- `--max-workers`: Number of agents to run in parallel (default: 2).

### Web Dashboard
To update the web dashboard with the latest project results:
1. Generate the manifest:
   ```bash
   python3 generate_manifest.py
   ```
2. View the dashboard locally by opening `index.html` or visit the [GitHub Pages site](https://nobel-ai-tests.github.io/cli-agent-automation/).

## Self-Learning Loop
After the controller finishes, the Critic Agent is automatically triggered. It:
1. Analyzes logs for errors (e.g., rate limits, syntax errors).
2. Summarizes successes.
3. Updates `subagent_instructions.txt` with actionable lessons.
These lessons are injected into the prompts of subsequent agent runs, creating a continuous improvement cycle.

## Skill Integration
This workflow is also available as a Gemini CLI skill: `parallel-orchestrator-learning`.
Activate it within a Gemini CLI session for specialized guidance:
```bash
activate_skill("parallel-orchestrator-learning")
```

---
*Created by Gemini CLI*
