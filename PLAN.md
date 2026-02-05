# Plan: Controller Evolution, Self-Learning Loop, and Robustness

## Overview
Enhance the existing Python controller to handle API rate limits gracefully, analyze its own performance post-execution, synthesize lessons learned, and address critical architectural feedback regarding hanging, idempotency, and reliability.

## Phase 1: Robustness & Adaptive Throttling
- **Detection Logic:** Update `extract_step` or add a new parser to detect "quota exhausted" or "rate limit" messages in `stdout`/`stderr`.
- **Dynamic Backoff:** Implement a retry mechanism with exponential backoff specifically for quota errors.
- **Concurrency Control:** Add logic to dynamically reduce `max_workers` if multiple concurrent agents report rate limits.
- **Timeout Implementation:** Add a global execution timeout per agent to prevent hanging (Address Feedback #3).
- **Idempotency:** Implement a check to skip already completed projects (Address Feedback #2).

## Phase 2: Post-Mortem & Self-Learning Loop
- **Log Analysis:** Create a `critic_agent.py` or a function within `controller.py` that reads `controller.log` after a run.
- **Outcome Assessment:** Verify the integrity of `projects/` (e.g., do `index.html` and `README.md` exist and contain valid code?).
- **Lesson Synthesis:** Use a Gemini agent to analyze failures and successes, producing a `LESSONS_LEARNED.md`.
- **Instruction Injection:** Implement a mechanism to update a global `subagent_instructions.txt` that `controller.py` automatically appends to every project prompt.

## Phase 3: Skill Integration
- **Skill Creation:** Use `activate_skill("skill-creator")` to formalize the "Parallel Orchestration and Learning" workflow into a reusable Gemini CLI skill.
- **Documentation:** Ensure the skill includes documentation on how to maintain the learning loop.

## Phase 4: Verification
- **Stress Test:** Run the 10 games in `projects.json` with a low `--max-workers` and verify the self-learning loop captures any issues.
- **Audit:** Confirm `GEMINI.md` and `LESSONS_LEARNED.md` are accurately reflecting the system's state.
- **Feedback Audit:** Verify that issues in `feedback.md` (Timeouts, Idempotency, etc.) are addressed.
