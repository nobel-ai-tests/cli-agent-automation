import os
import json
import subprocess
import sys
import argparse
import re
import time
import random
import threading
import tempfile
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from rich.live import Live
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

# Dynamic path resolution
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECTS_FILE = os.path.join(BASE_DIR, "projects.json")
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")
LOG_FILE = os.path.join(BASE_DIR, "controller.log")
INSTRUCTIONS_FILE = os.path.join(BASE_DIR, "subagent_instructions.txt")

# Configuration
EXECUTION_TIMEOUT = 300  # 5 minutes per agent
MAX_BACKOFF = 60

# Shared state for UI and concurrency
project_status = {}
concurrency_semaphore = None
current_max_workers = 2
concurrency_lock = threading.Lock()

def atomic_write(file_path, content):
    """Write content to a file atomically using a temporary file."""
    dir_name = os.path.dirname(file_path)
    fd, temp_path = tempfile.mkstemp(dir=dir_name, text=True)
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        os.replace(temp_path, file_path)
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e

def log(message, level="INFO", project=None):
    """Structured logging."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "project": project,
        "message": message
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def is_project_complete(project_dir):
    """Check if the project has already been completed successfully."""
    if os.path.exists(os.path.join(project_dir, ".done")):
        return True
    return verify_integrity(project_dir)

def verify_integrity(project_dir):
    """Check if the project looks complete (has index.html with a body)."""
    index_path = os.path.join(project_dir, "index.html")
    if os.path.exists(index_path):
        try:
            with open(index_path, "r") as f:
                content = f.read().lower()
                if "<body>" in content and len(content) > 100:
                    return True
        except:
            pass
    return False

def mark_project_done(project_dir):
    """Mark the project as completed successfully."""
    done_file = os.path.join(project_dir, ".done")
    atomic_write(done_file, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def extract_step(line):
    """Try to extract a concise 'current step' from the agent's output."""
    line = line.strip()
    # Patterns common in Gemini CLI output when planning/acting
    # Updated to handle potential dots in filenames better
    patterns = [
        r"(I will\s+.*?\.($|\s))",
        r"(I'll\s+.*?\.($|\s))",
        r"(Creating\s+.*)",
        r"(Reading\s+.*)",
        r"(Writing\s+.*)",
        r"(Running\s+.*)",
        r"(Executing\s+.*)",
        r"(Analyzing\s+.*)",
        r"(Searching\s+.*)"
    ]
    for p in patterns:
        match = re.search(p, line, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None

def check_rate_limit(line):
    """Check if the line indicates a rate limit or quota exhaustion."""
    rate_limit_patterns = [
        r"exhausted your capacity",
        r"rate limit reached",
        r"quota exceeded",
        r"429 Too Many Requests",
        r"Resource exhausted"
    ]
    for p in rate_limit_patterns:
        if re.search(p, line, re.IGNORECASE):
            return True
    return False

def adjust_concurrency(delta):
    """Adjust the number of concurrent agents."""
    global current_max_workers, concurrency_semaphore
    with concurrency_lock:
        new_val = max(1, current_max_workers + delta)
        if new_val != current_max_workers:
            log(f"Adjusting concurrency: {current_max_workers} -> {new_val}")
            if delta > 0:
                for _ in range(new_val - current_max_workers):
                    concurrency_semaphore.release()
            else:
                for _ in range(current_max_workers - new_val):
                    # We don't block here, just try to acquire to reduce future capacity
                    concurrency_semaphore.acquire(blocking=False)
            current_max_workers = new_val

def get_subagent_instructions():
    if os.path.exists(INSTRUCTIONS_FILE):
        with open(INSTRUCTIONS_FILE, "r") as f:
            return f.read().strip()
    return ""

def run_agent(project, update_ui_cb, max_retries=5):
    name = project["name"]
    task = project["task"]
    project_dir = os.path.join(PROJECTS_DIR, name)
    os.makedirs(project_dir, exist_ok=True)
    
    if is_project_complete(project_dir):
        log(f"Project already complete. Skipping.", project=name)
        project_status[name] = {"status": "Done", "step": "Skipped (Already Complete)", "progress": 100}
        update_ui_cb()
        return

    project_status[name] = {"status": "Starting", "step": "Initializing...", "progress": 0}
    update_ui_cb()

    # Load custom instructions for the sub-agent
    extra_instructions = get_subagent_instructions()
    
    # Loop prevention and resumption instructions
    system_guidelines = """
- DO NOT get stuck in an infinite loop. If you are repeating the same action or hitting the same error, stop, analyze why, and try a different approach.
- If files already exist, ANALYZE them first and CONTINUE the work. Do not overwrite everything unless necessary.
- ALWAYS check for a README.md or PLAN.md to understand the previous state.
"""
    instruction_block = f"\n\nIMPORTANT GUIDELINES:\n{system_guidelines}\n{extra_instructions}"

    # Check for existing files to determine if we are resuming
    existing_files = [f for f in os.listdir(project_dir) if f not in [".done", ".gemini", "__pycache__", ".git"]]
    is_resume = len(existing_files) > 0
    
    if is_resume:
        log(f"Resuming project. Existing files: {existing_files}", project=name)
        resumption_context = f"Current directory contains: {', '.join(existing_files)}. "
        # Try to read README.md for context
        if "README.md" in existing_files:
            try:
                with open(os.path.join(project_dir, "README.md"), "r") as f:
                    readme_content = f.read(1000) # Get first 1000 chars
                    resumption_context += f"\nLast known plan (README.md excerpt):\n{readme_content}\n"
            except:
                pass
        
        full_prompt = f"RESUME WORK: You were working on: {task}. {resumption_context}\n\nContinue from where you left off. Identify what is missing or broken and fix it. {instruction_block}"
    else:
        # We add a preamble to the prompt to encourage planning
        full_prompt = f"START NEW PROJECT: {task}. First, create a simple README.md outlining your plan. Then implement the task. {instruction_block}"

    command = ["gemini", "--yolo", "-p", full_prompt]
    
    retries = 0
    while retries <= max_retries:
        with concurrency_semaphore:
            log(f"Starting agent (Attempt {retries + 1})", project=name)
            project_status[name]["status"] = "Running"
            project_status[name]["step"] = f"Attempt {retries + 1}..."
            update_ui_cb()

            try:
                start_time = time.time()
                process = subprocess.Popen(
                    command,
                    cwd=project_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                is_rate_limited = False
                
                for line in process.stdout:
                    if time.time() - start_time > EXECUTION_TIMEOUT:
                        process.kill()
                        log(f"Timed out after {EXECUTION_TIMEOUT}s", level="WARNING", project=name)
                        project_status[name]["status"] = "Timed Out"
                        update_ui_cb()
                        break

                    line_stripped = line.strip()
                    if line_stripped:
                        log(line_stripped, project=name)
                    
                    if check_rate_limit(line_stripped):
                        is_rate_limited = True
                        log("Rate limit detected in STDOUT.", level="WARNING", project=name)

                    step = extract_step(line_stripped)
                    if step:
                        project_status[name]["step"] = step[:100] + "..." if len(step) > 100 else step
                        project_status[name]["progress"] = min(95, project_status[name]["progress"] + 10)
                        update_ui_cb()

                process.wait(timeout=10) # Small grace period for final cleanup
                
                # Read stderr for logs and rate limits
                stderr_output = process.stderr.read()
                if stderr_output:
                    log(stderr_output.strip(), level="ERROR", project=name)
                    if check_rate_limit(stderr_output):
                        is_rate_limited = True
                        log("Rate limit detected in STDERR.", level="WARNING", project=name)

                if project_status[name]["status"] == "Timed Out":
                    # Even on timeout, check if it's actually done
                    if verify_integrity(project_dir):
                        project_status[name]["status"] = "Done"
                        project_status[name]["step"] = "Task Completed (Detected after Timeout)"
                        project_status[name]["progress"] = 100
                        mark_project_done(project_dir)
                        log("Task completed (detected after timeout).", project=name)
                        break
                elif is_rate_limited or process.returncode != 0:
                    # Check if it's actually done despite the error/rate limit
                    if verify_integrity(project_dir):
                        project_status[name]["status"] = "Done"
                        project_status[name]["step"] = "Task Completed (Detected after Error)"
                        project_status[name]["progress"] = 100
                        mark_project_done(project_dir)
                        log("Task completed (detected after error).", project=name)
                        break

                    error_type = "RateLimit" if is_rate_limited else "FatalError"
                    log(f"Agent failed. Type: {error_type}, Code: {process.returncode}", level="ERROR", project=name)
                    
                    if is_rate_limited:
                        adjust_concurrency(-1) # Reduce concurrency on rate limit
                        retries += 1
                        if retries <= max_retries:
                            wait_time = min(MAX_BACKOFF, (2 ** retries) + random.random() * 5)
                            log(f"Retrying in {wait_time:.2f}s...", project=name)
                            project_status[name]["status"] = "Retrying"
                            project_status[name]["step"] = f"Rate limited. Waiting {wait_time:.2f}s"
                            update_ui_cb()
                            time.sleep(wait_time)
                            continue
                    
                    project_status[name]["status"] = "Failed"
                    project_status[name]["step"] = f"Exit Code: {process.returncode}"
                else:
                    project_status[name]["status"] = "Done"
                    project_status[name]["step"] = "Task Completed Successfully"
                    project_status[name]["progress"] = 100
                    mark_project_done(project_dir)
                    log("Task completed successfully.", project=name)
                    break # Success
                    
                update_ui_cb()
                break # If not retrying, break loop
                    
            except subprocess.TimeoutExpired:
                process.kill()
                log(f"Subprocess timed out.", level="ERROR", project=name)
                project_status[name]["status"] = "Timed Out"
                update_ui_cb()
                break
            except Exception as e:
                log(f"Exception: {str(e)}", level="CRITICAL", project=name)
                project_status[name]["status"] = "Error"
                project_status[name]["step"] = str(e)[:50]
                update_ui_cb()
                break

def generate_table():
    table = Table(title="[bold blue]Gemini CLI Sub-Agent Dashboard[/bold blue]", expand=True)
    table.add_column("Project", style="cyan", width=20, no_wrap=True, overflow="ellipsis")
    table.add_column("Status", style="magenta", width=12, no_wrap=True, overflow="ellipsis")
    table.add_column("Current Step", style="green", width=50, no_wrap=True, overflow="ellipsis")
    table.add_column("Progress", style="yellow", width=20, no_wrap=True)
    table.add_column("Limit", style="red", width=6, no_wrap=True)

    for name, info in project_status.items():
        prog = info["progress"]
        table.add_row(
            name, 
            info["status"], 
            info["step"], 
            f"[{'#' * (prog // 10)}{'.' * (10 - prog // 10)}] {prog}%",
            str(current_max_workers)
        )
    return table

def main():
    global current_max_workers, concurrency_semaphore
    parser = argparse.ArgumentParser(description="Parallel Gemini CLI Controller")
    parser.add_argument("--max-workers", type=int, default=2, help="Maximum number of simultaneous agents")
    args = parser.parse_args()

    current_max_workers = args.max_workers
    concurrency_semaphore = threading.Semaphore(current_max_workers)

    if not os.path.exists(PROJECTS_FILE):
        print(f"Error: {PROJECTS_FILE} not found.")
        sys.exit(1)
        
    with open(PROJECTS_FILE, "r") as f:
        projects = json.load(f)
        
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    
    # Initialize statuses
    for p in projects:
        project_status[p["name"]] = {"status": "Pending", "step": "Waiting in queue...", "progress": 0}

    with Live(generate_table(), refresh_per_second=4) as live:
        def update_ui():
            live.update(generate_table())

        # ThreadPool size doesn't strictly matter as much now because of the semaphore
        with ThreadPoolExecutor(max_workers=max(10, args.max_workers)) as executor:
            futures = [executor.submit(run_agent, p, update_ui) for p in projects]
            for future in futures:
                future.result()

    # After all projects are done, run the critic agent
    print("\nExecuting Post-Mortem Analysis...")
    subprocess.run(["python3", "critic_agent.py"])

if __name__ == "__main__":
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    main()
