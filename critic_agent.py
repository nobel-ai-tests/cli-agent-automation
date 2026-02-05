import os
import re
import json
import subprocess
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "controller.log")
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")
LESSONS_FILE = os.path.join(BASE_DIR, "LESSONS_LEARNED.md")
INSTRUCTIONS_FILE = os.path.join(BASE_DIR, "subagent_instructions.txt")

def analyze_logs():
    if not os.path.exists(LOG_FILE):
        return {"errors": [], "loops": {}}
    
    errors = []
    steps_by_project = {}
    try:
        with open(LOG_FILE, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    proj = entry.get("project")
                    msg = entry.get("message")
                    
                    if entry.get("level") in ["ERROR", "WARNING", "CRITICAL"]:
                        errors.append(entry)
                    
                    if proj and msg:
                        if proj not in steps_by_project:
                            steps_by_project[proj] = []
                        steps_by_project[proj].append(msg)
                except json.JSONDecodeError:
                    pass
    except Exception as e:
        print(f"Error reading logs: {str(e)}")
        return {"errors": [], "loops": {}}
    
    # Detect loops (repetitive messages)
    loops = {}
    for proj, steps in steps_by_project.items():
        counts = {}
        for s in steps:
            counts[s] = counts.get(s, 0) + 1
        
        repeated = {k: v for k, v in counts.items() if v > 5}
        if repeated:
            loops[proj] = repeated

    return {"errors": errors, "loops": loops}

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
                "file_count": len(files),
                "is_done": ".done" in files
            }
            results[project] = integrity
            
            # PROACTIVE: If it's valid but not marked done, mark it now!
            if index_valid and not integrity["is_done"]:
                done_file = os.path.join(path, ".done")
                with open(done_file, "w") as f:
                    f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (Post-Mortem Repair)")
                print(f"Repaired .done status for {project}")
                integrity["is_done"] = True
                
    return results

def synthesize_lessons(log_analysis, integrity_results):
    current_instructions = ""
    if os.path.exists(INSTRUCTIONS_FILE):
        with open(INSTRUCTIONS_FILE, "r") as f:
            current_instructions = f.read()

    prompt = f"""
    Analyze the execution results of a parallel Gemini CLI orchestrator.
    
    Errors and Loop Detection:
    {json.dumps(log_analysis, indent=2)}
    
    Project Integrity Check (Did they finish?):
    {json.dumps(integrity_results, indent=2)}
    
    Current Sub-Agent Instructions:
    {current_instructions}
    
    Goal:
    1. Identify WHY projects failed or got stuck in loops.
    2. Synthesize 3-5 NEW actionable lessons.
    3. Produce a COMPLETE updated version of 'Sub-Agent Instructions' that incorporates both old and new lessons, avoiding redundancy.
    
    Format the output as a Markdown file with:
    ## Analysis
    (Your thoughts)
    
    ## Lessons for Controller
    (How to improve the python orchestrator)
    
    ## Updated Sub-Agent Instructions
    (The full block to be used in future prompts)
    """
    
    try:
        process = subprocess.run(
            ["gemini"],
            input=prompt,
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
    # Extract updated sub-agent lessons and update the file
    match = re.search(r"## Updated Sub-Agent Instructions\n(.*?)(?=\n##|$)", lessons, re.DOTALL)
    if match:
        sub_lessons = match.group(1).strip()
        with open(INSTRUCTIONS_FILE, "w") as f:
            f.write(sub_lessons)
        print(f"Updated {INSTRUCTIONS_FILE}")

def main():
    print("Starting post-mortem analysis...")
    log_data = analyze_logs()
    integrity = check_project_integrity()
    
    lessons = synthesize_lessons(log_data, integrity)
    
    with open(LESSONS_FILE, "w") as f:
        f.write(lessons)
    
    print(f"Analysis complete. Lessons saved to {LESSONS_FILE}")
    update_instructions(lessons)

if __name__ == "__main__":
    main()