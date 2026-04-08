import os
from dotenv import load_dotenv

load_dotenv()

LLM_MODE = os.getenv("LLM_MODE", "no_llm")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
