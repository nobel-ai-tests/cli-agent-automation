# Gemini CLI Controller Documentation

## Architecture Overview
The controller is a Python-based orchestrator designed to run multiple Gemini CLI agents in parallel. It handles project isolation, real-time progress tracking, and centralized logging.

### Core Components:
- **Parallelism:** Uses `concurrent.futures.ThreadPoolExecutor` to manage a pool of sub-agents.
- **Agent Execution:** Each sub-agent is invoked via `subprocess.Popen` running `gemini --yolo`.
- **UI Dashboard:** Utilizes the `rich` library (`Live` and `Table`) to display a real-time status of all active and pending projects.
- **Step Extraction:** Employs regex patterns to parse the agent's "thought process" and update the "Current Step" column in the dashboard.
- **Isolation:** Each project is executed within its own subdirectory under `projects/`.

### Execution Flow:
1. Reads `projects.json` for task definitions.
2. Initializes the `rich` dashboard.
3. Submits tasks to the thread pool (default `max_workers=2`).
4. Streams `stdout` to detect progress steps and logs all activity to `controller.log`.
5. Updates project status to "Done" or "Failed" based on the exit code.

### Self-Learning Loop
The controller includes an automated post-mortem process:
1. **Critic Agent:** After execution, `critic_agent.py` analyzes the `controller.log` and the contents of the `projects/` directory.
2. **Lesson Synthesis:** It uses Gemini to identify failures (like rate limits or missing files) and successes.
3. **Instruction Injection:** Actionable lessons for sub-agents are saved to `subagent_instructions.txt`, which the controller automatically injects into the prompt of every future agent run.

### Parallel Orchestrator Learning Skill
The orchestration workflow has been formalized into a Gemini CLI skill: `parallel-orchestrator-learning`.
- **Installation:** Already installed in the workspace scope.
- **Activation:** Use `activate_skill("parallel-orchestrator-learning")` to get guidance on running parallel tasks with a learning loop.
- **Maintenance:** To update the skill, modify the files in `parallel-orchestrator-learning/` and re-package/re-install.

### Usage:
```bash
python3 controller.py --max-workers <count>
```
This will run all projects in `projects.json`, handle retries, and trigger the learning loop at the end.
