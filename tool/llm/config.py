import os
import dotenv

dotenv.load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "You are assistant for PR code review. You are going to receive a diff of a PR and you are going to review the code and provide comments for each part of the code that needs to be improved.")
