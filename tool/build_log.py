import json
import sys
from pathlib import Path

def load_sonar(pr_number):
    path = Path(f"sonar_pr_{pr_number}.json")
    return json.loads(path.read_text()) if path.exists() else {}

def load_llm():
    path = Path("review.md")
    return path.read_text() if path.exists() else ""

def extract_ground_truth(pr_body, labels):
    smells = []

    # Option 1: Body tag "SMELLS: smell1, smell2"
    if "SMELLS:" in pr_body:
        line = pr_body.split("SMELLS:")[1].split("\n")[0].strip()
        smells += [s.strip().upper() for s in line.split(",")]

    # Option 2: Labels of type "smell:XXX"
    for label in labels:
        if label.lower().startswith("smell:"):
            smells.append(label.split(":", 1)[1].strip().upper())

    return list(set(smells))

def main():
    event = json.loads(Path(sys.argv[1]).read_text())
    pr = event["pull_request"]
    pr_number = pr["number"]

    ground_truth = extract_ground_truth(
        pr["body"] or "",
        [l["name"] for l in pr["labels"]]
    )

    log = {
        "pr_number": pr_number,
        "pr_author": pr["user"]["login"],
        "created_at": pr["created_at"],
        "ground_truth_smells": ground_truth,
        "llm_output": load_llm(),
        "sonar_issues": load_sonar(pr_number).get("issues", [])
    }

    Path(f"dataset/pr_{pr_number}.json").write_text(
        json.dumps(log, indent=2)
    )

if __name__ == "__main__":
    main()
