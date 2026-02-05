import os
import re
import json
import subprocess
from datetime import datetime

LOG_FILE = "controller.log"
PROJECTS_DIR = "projects"
LESSONS_FILE = "LESSONS_LEARNED.md"
INSTRUCTIONS_FILE = "subagent_instructions.txt"

def analyze_logs():
    if not os.path.exists(LOG_FILE):
        return "No log file found."
    
    with open(LOG_FILE, "r") as f:
        logs = f.read()
    
    # Extract errors and rate limits
    errors = re.findall(r"\[.*?\] (Error running agent for .*?|.*?Rate limit detected.*?)", logs)
    return errors

def check_project_integrity():
    results = {}
    if not os.path.exists(PROJECTS_DIR):
        return results
    
    for project in os.listdir(PROJECTS_DIR):
        path = os.path.join(PROJECTS_DIR, project)
        if os.path.isdir(path):
            files = os.listdir(path)
            
            # Basic validity checks
            index_valid = False
            if "index.html" in files:
                try:
                    with open(os.path.join(path, "index.html"), "r") as f:
                        content = f.read()
                        if "<body>" in content.lower() and len(content) > 50:
                            index_valid = True
                except:
                    pass

            integrity = {
                "has_readme": "README.md" in files,
                "has_index": "index.html" in files,
                "index_valid": index_valid,
                "file_count": len(files)
            }
            results[project] = integrity
    return results

def synthesize_lessons(log_analysis, integrity_results):
    prompt = f"""
    Analyze the following execution results from a parallel Gemini CLI orchestrator and provide 3-5 actionable lessons for future sub-agents and the controller.
    
    Errors found in logs:
    {json.dumps(log_analysis, indent=2)}
    
    Project Integrity Check:
    {json.dumps(integrity_results, indent=2)}
    
    Format the output as a Markdown file with 'Lessons for Controller' and 'Lessons for Sub-Agents' sections.
    """
    
    # Run gemini to synthesize lessons
    try:
        process = subprocess.run(
            ["gemini", "-p", prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if process.returncode == 0:
            return process.stdout
        else:
            return f"Error synthesizing lessons: {process.stderr}"
    except Exception as e:
        return f"Exception during synthesis: {str(e)}"

def update_instructions(lessons):
    # Extract sub-agent lessons and append to subagent_instructions.txt
    match = re.search(r"## Lessons for Sub-Agents\n(.*?)(?=\n##|$)", lessons, re.DOTALL)
    if match:
        sub_lessons = match.group(1).strip()
        with open(INSTRUCTIONS_FILE, "w") as f:
            f.write(sub_lessons)
        print(f"Updated {INSTRUCTIONS_FILE}")

def main():
    print("Starting post-mortem analysis...")
    log_errs = analyze_logs()
    integrity = check_project_integrity()
    
    lessons = synthesize_lessons(log_errs, integrity)
    
    with open(LESSONS_FILE, "w") as f:
        f.write(lessons)
    
    print(f"Analysis complete. Lessons saved to {LESSONS_FILE}")
    update_instructions(lessons)

if __name__ == "__main__":
    main()
