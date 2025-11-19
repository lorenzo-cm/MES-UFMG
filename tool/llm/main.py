from openai import OpenAI

from .config import OPENAI_API_KEY, OPENAI_MODEL, SYSTEM_PROMPT
from .models import CodeReviewResponse

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_response(diff_content: str) -> CodeReviewResponse:
    """
    Generate a structured code review response using OpenAI's Structured Outputs.
    
    Args:
        diff_content: The git diff content to analyze
        
    Returns:
        CodeReviewResponse with detected code smells and PR comment
    """
    completion = client.beta.chat.completions.parse(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user", 
                "content": f"Please analyze the following code diff and identify any code smells:\n\n{diff_content}"
            },
        ],
        response_format=CodeReviewResponse,
    )
    
    return completion.choices[0].message.parsed

