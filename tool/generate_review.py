"""
Script to generate both PR comment and structured smells JSON.
This script is called by the GitHub Actions workflow.
"""
import json
import sys
from pathlib import Path

from utils import read_diff
from llm import generate_response


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_review.py <diff_file>", file=sys.stderr)
        sys.exit(1)
    
    diff_file = sys.argv[1]
    diff_content = read_diff(diff_file)
    
    # Generate structured response with code smells
    response = generate_response(diff_content)
    
    # Save PR comment to review.md (for GitHub comment)
    Path("review.md").write_text(response.pr_comment)
    
    # Save structured smells to JSON (for dataset)
    smells_data = [smell.model_dump() for smell in response.smells]
    Path("llm_smells.json").write_text(
        json.dumps(smells_data, indent=2)
    )
    
    print(f"✓ Generated review with {len(response.smells)} code smell(s)")
    print(f"✓ Saved PR comment to review.md")
    print(f"✓ Saved structured smells to llm_smells.json")


if __name__ == "__main__":
    main()
