from pathlib import Path

def read_diff(diff_file: str) -> str:
    diff_file_path = Path(diff_file)
    with open(diff_file_path, 'r') as f:
        return f.read()
