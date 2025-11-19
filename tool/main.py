from utils import parse_args, read_diff
from llm import generate_response

def main():
    args = parse_args()
    diff_file = args.diff_file
    diff = read_diff(diff_file)
    
    # Generate structured response with code smells
    response = generate_response(diff)
    
    # Print the PR comment (will be saved to review.md by the workflow)
    print(response.pr_comment)

if __name__ == "__main__":
    main()
