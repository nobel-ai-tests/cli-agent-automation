I will start by reading the `controller.log` and the current `subagent_instructions.txt` to understand the execution context and existing guidance.
I will now read the `projects.json` file to see how the tasks are structured and defined.
## Analysis

1.  **Rate Limit Saturation:** The dominant cause of failure was the `429 Too Many Requests` error. Even as the controller scaled concurrency down from 6 to 1, agents continued to hit quotas. This suggests that the agents' internal retry logic and the controller's task-level retries were not sufficiently backed off to allow the quota to reset properly.
2.  **`replace` Tool Fragility:** Many projects (e.g., `pong_game`, `whack_a_mole`) suffered from `replace` failures. Agents often attempted to replace large blocks of code without verifying the current state of the file on disk. In a parallel/retrying environment, the file content might have been modified by a previous partially successful attempt, leading to "0 occurrences found" or "Expected X occurrences but found Y" errors.
3.  **Inefficient Context Usage:** Agents frequently tried to "implement the entire game in a single file" in one turn. This creates massive output tokens, which consumes quota rapidly and makes the agent more vulnerable to context window limits and formatting errors during large-scale `replace` or `write_file` operations.
4.  **Resume Inefficiency:** When agents resumed a project, they often spent multiple turns re-discovering the state (listing directories, reading files sequentially) before making a move. This repetitive overhead under rate-limited conditions often led to hitting the quota before any productive work was done.

## Technical Debt & Solutions

| Failure | Root Cause | Solution |
| :--- | :--- | :--- |
| **False Failures** | Agents finished work but hit 429/Timeout during final summary, causing non-zero exit code. | **Integrity Verification**: Added `verify_integrity()` to check for valid `index.html` regardless of process exit status. |
| **Arg List Too Long** | Passing massive logs as a shell argument (`gemini -p "..."`) hit OS limits. | **Stdin Stream**: Updated `critic_agent.py` to pipe prompts via `stdin`, bypassing shell argument limits. |
| **Silent Completion** | Agents finished but didn't create a `.done` marker before crashing. | **Post-Mortem Repair**: Updated Critic Agent to proactively create `.done` files if integrity checks pass. |
| **Replace Mismatches** | Parallel runs caused files to change, making cached `replace` strings invalid. | **Read-Before-Replace**: Updated sub-agent instructions to force a `read_file` immediately before any `replace` call. |

## Lessons for Controller

1.  **Global Backoff Strategy:** The python orchestrator should implement a global "Cool Down" period. If any agent hits a 429, *all* agents should be paused for 5-10 seconds to allow the shared quota to reset completely, rather than letting them individually beat against the limit.
2.  **Jittered Task Start:** Instead of starting all workers simultaneously, the controller should stagger agent starts by 2-3 seconds to prevent a synchronized burst of initial `list_directory` and `read_file` calls that often triggers early rate limits.
3.  **Error-Specific Retries:** Distinguish between "Agent Crashed" (Retryable) and "Tool Failed" (Logic Error). If an agent fails a `replace` call multiple times, the controller should inject a "Warning: Previous replace failed, please read the file again" hint into the next attempt.

## Updated Sub-Agent Instructions

```text
- **Atomic Incrementalism**: Build projects in small, verifiable steps. Create the README first, then the HTML skeleton, then CSS, then core JS logic, and finally refinements. Avoid writing massive blocks of code in a single turn.
- **Read-Before-Replace**: Never call 'replace' based on memory. Always 'read_file' immediately before a 'replace' call to ensure you have the exact string, including whitespace and indentation.
- **Robust 'replace' Recovery**: If a 'replace' call fails, do not retry the same string. Re-read the file to see if a previous attempt partially succeeded or if the context changed. If 'replace' fails twice on the same block, use 'write_file' to overwrite the file with the full corrected content.
- **Rate Limit Grace**: If you see "exhausted capacity" or 429 errors in your logs, stop your current turn immediately after summarizing your progress. The controller will resume you when the quota resets.
- **README as a Save Point**: Treat the README.md as your persistent memory. Every time you finish a feature or hit an error, update the README with "Progress:" and "Pending Tasks:". This ensures the next agent (or retry) picks up exactly where you left off.
- **Self-Contained & Vanilla**: Ensure all assets (CSS/JS) are either inline or in dedicated local files created by you. Avoid external dependencies (CDNs) unless explicitly requested. Use vanilla JS/CSS for game logic and layout (centering, responsiveness).
- **Mandatory Reset**: Every game/interactive app MUST have a visible 'Reset' or 'Restart' button that resets the game state without a full page reload.
```
