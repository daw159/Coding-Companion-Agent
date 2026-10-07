import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

GEMINI = "google_genai:gemini-3.1-flash-lite"
GROQ = "groq:openai/gpt-oss-120b"

MODEL = GEMINI

if MODEL == GEMINI:
    api_key = os.getenv("GEMINI_KEY")
else:
    api_key = os.getenv("GROQ_API_KEY")

llm = init_chat_model(
    MODEL,
    api_key=api_key,
)