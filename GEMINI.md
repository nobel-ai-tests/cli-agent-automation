# Gemini CLI Controller Technical Documentation

## Architecture Overview
The controller is a Python-based orchestrator designed for high-concurrency, long-running agent tasks. It prioritizes robustness, idempotency, and automated recovery.

### Concurrency & Throttling
- **Dynamic Semaphore:** Uses a `threading.Semaphore` combined with a `concurrency_lock` to adjust `max_workers` in real-time.
- **Adaptive Backoff:** When a `RateLimit` (429) is detected in STDOUT or STDERR, the controller:
    1. Reduces the current concurrency limit by 1.
    2. Implements an exponential backoff (2^n + jitter) for the affected project.
- **Global Timeout:** Enforces `EXECUTION_TIMEOUT` (default 300s) per agent to prevent hanging sub-processes.

### Execution Engine (`run_agent`)
- **Prompts:** Injects a standard `system_guidelines` block (loop prevention, resumption context) and `subagent_instructions.txt` (learned lessons) into every prompt.
- **Resumption Context:** Automatically detects existing files and provides the first 1000 characters of `README.md` to the agent as context for resuming work.
- **Telemetry:** Logs every line of output to `controller.log` as a JSON object:
  ```json
  {"timestamp": "...", "level": "INFO", "project": "name", "message": "..."}
  ```

### Completion & Integrity
The controller employs a "Defense in Depth" approach to marking tasks complete:
1. **Exit Code:** Standard completion on `returncode == 0`.
2. **Post-Process Verification:** If a process fails or times out, `verify_integrity()` checks if `index.html` exists and contains valid `<body>` content > 100 bytes.
3. **Idempotency:** Checks for a `.done` file in the project directory to skip completed work on subsequent runs.

### Self-Learning Loop (`critic_agent.py`)
Triggered automatically after the `ThreadPoolExecutor` finishes.
1. **Integrity Audit:** Re-runs validation on all projects.
2. **Proactive Repair:** If a project is valid but lacks a `.done` marker (due to a crash or rate limit at the very end), the critic creates it.
3. **Prompt Synthesis:** Sends the entire log analysis and integrity report to Gemini via `stdin` to generate new `subagent_instructions.txt`.

### Skill: `parallel-orchestrator-learning`
A formalized Gemini CLI skill that bundles these scripts and logic.
- **Location:** `.gemini/skills/parallel-orchestrator-learning/`
- **Assets:** Includes `controller.py` and `critic_agent.py` as internal resources.

### Usage
```bash
# Run with 2 workers (default)
python3 controller.py

# Run with increased concurrency
python3 controller.py --max-workers 5
```

### Manifest Generation
`generate_manifest.py` recursively scans the `projects/` directory to create a `projects_manifest.json` for the web dashboard, ensuring that only valid project assets are displayed.