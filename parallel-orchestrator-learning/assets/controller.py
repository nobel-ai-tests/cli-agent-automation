import os
import json
import subprocess
import sys
import argparse
import re
import time
import random
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from rich.live import Live
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

# Configuration
PROJECTS_FILE = "projects.json"
PROJECTS_DIR = "projects"
LOG_FILE = "controller.log"

# Shared state for UI and concurrency
project_status = {}
concurrency_semaphore = None
current_max_workers = 2
concurrency_lock = threading.Lock()

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

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

INSTRUCTIONS_FILE = "subagent_instructions.txt"

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
    
    project_status[name] = {"status": "Starting", "step": "Initializing...", "progress": 0}
    update_ui_cb()

    # Load custom instructions for the sub-agent
    extra_instructions = get_subagent_instructions()
    instruction_block = f"\n\nIMPORTANT GUIDELINES:\n{extra_instructions}" if extra_instructions else ""

    # We add a preamble to the prompt to encourage planning
    full_prompt = f"First, create a simple README.md outlining your plan. Then: {task}{instruction_block}"
    command = ["gemini", "--yolo", "-p", full_prompt]
    
    retries = 0
    while retries <= max_retries:
        with concurrency_semaphore:
            log(f"Starting agent for project: {name} (Attempt {retries + 1})")
            project_status[name]["status"] = "Running"
            project_status[name]["step"] = f"Attempt {retries + 1}..."
            update_ui_cb()

            try:
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
                
                # Stream stdout to find steps and rate limits
                for line in process.stdout:
                    line_stripped = line.strip()
                    log(f"[{name}] STDOUT: {line_stripped}")
                    
                    if check_rate_limit(line_stripped):
                        is_rate_limited = True
                        log(f"[{name}] Rate limit detected in STDOUT.")

                    step = extract_step(line_stripped)
                    if step:
                        project_status[name]["step"] = step[:100] + "..." if len(step) > 100 else step
                        project_status[name]["progress"] = min(95, project_status[name]["progress"] + 10)
                        update_ui_cb()

                process.wait()
                
                # Read stderr for logs and rate limits
                stderr_output = process.stderr.read()
                if stderr_output:
                    log(f"[{name}] STDERR: {stderr_output.strip()}")
                    if check_rate_limit(stderr_output):
                        is_rate_limited = True
                        log(f"[{name}] Rate limit detected in STDERR.")

                if is_rate_limited or process.returncode != 0:
                    if is_rate_limited:
                        adjust_concurrency(-1) # Reduce concurrency on rate limit
                        retries += 1
                        if retries <= max_retries:
                            wait_time = min(max_backoff, (2 ** retries) + random.random() * 5)
                            log(f"[{name}] Rate limited. Retrying in {wait_time:.2f}s...")
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
                    # Optionally increase concurrency slowly after success
                    # adjust_concurrency(1) 
                    break # Success
                    
                update_ui_cb()
                break # If not retrying, break loop
                    
            except Exception as e:
                log(f"Error running agent for {name}: {str(e)}")
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
