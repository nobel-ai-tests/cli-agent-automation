# GPT 5.2 Technical Feedback
** If you have seen this already, ignore by putting some indicator at the top. No need to review feedback multiple times.

## 1. No strict schema validation at runtime
Agent inputs and outputs are not validated against JSON schemas, allowing malformed or incomplete responses to propagate through the system and causing non-deterministic behavior.

## 2. Controller lacks idempotency guarantees
Re-running the controller can overwrite files, partially regenerate projects, or leave the system in an inconsistent state. There is no checkpointing, hashing, or locking mechanism.

## 3. Agent execution has no timeout or resource limits
Subprocess calls to the Gemini CLI are not consistently wrapped with timeouts, memory constraints, or execution guards, creating risk of hanging or runaway processes.

## 4. No explicit error propagation model
Agent failures are not classified as retryable vs fatal. Exceptions, partial outputs, and invalid results are not surfaced in a structured way to the controller.

## 5. Output parsing assumes well-formed agent responses
JSON parsing logic assumes compliant agent output and lacks defensive parsing, streaming handling, or partial recovery mechanisms.

## 6. No deterministic task graph
Agent execution order is implicit. There is no DAG or dependency resolution to ensure prerequisite artifacts exist before downstream agents run.

## 7. No state persistence layer
System state (project progress, agent history, retries) is not persisted in a durable store, preventing safe resume, replay, or auditability.

## 8. File writes are not atomic
Generated files are written directly without temporary files and atomic renames, risking corruption if execution is interrupted.

## 9. Concurrency model is unsafe for filesystem writes
Parallel agents can write to the same project directory without coordination, leading to race conditions and inconsistent artifacts.

## 10. Dependency management is undefined
There is no pinned execution environment (virtualenv, requirements.txt, lockfile), making behavior dependent on ambient system state.

## 11. No versioning of agent prompts or behavior
Prompt changes are not versioned or referenced in outputs, making results non-reproducible across runs.

## 12. No logging or structured telemetry
The system lacks structured logs, trace IDs, and per-agent metrics, making debugging and performance analysis difficult.

## 13. Hard-coded paths and assumptions
Controller and agent code assume fixed directory layouts and relative paths, reducing portability and testability.

## 14. No unit or integration tests
Core orchestration logic is untested, including error paths, malformed outputs, and concurrency scenarios.

## 15. No sandboxing of agent execution
Agent-generated code and file operations are not sandboxed, allowing unintended filesystem modification or unsafe execution.
