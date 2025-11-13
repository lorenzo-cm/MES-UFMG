import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Process git diff file')
    parser.add_argument('diff_file', help='Path to the diff file')
    
    args = parser.parse_args()

    return args
