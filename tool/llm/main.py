from openai import OpenAI

from .config import OPENAI_API_KEY, OPENAI_MODEL, SYSTEM_PROMPT

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_response(prompt: str) -> str:
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content or ""
