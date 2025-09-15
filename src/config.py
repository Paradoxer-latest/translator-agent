from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model="gpt-5",
    temperature=0,
    api_key=OPENAI_API_KEY
)
