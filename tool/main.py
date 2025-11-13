from utils import parse_args, read_diff
from llm import generate_response

def main():
    args = parse_args()
    diff_file = args.diff_file
    diff = read_diff(diff_file)
    response = generate_response(diff)
    print(response)

if __name__ == "__main__":
    main()
