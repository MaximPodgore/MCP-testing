import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

# environment variables populated from .env file
# api_key, endpoint, etcs
load_dotenv()

model = AzureChatOpenAI(
    model="o3-mini",
    api_version= os.getenv("AZURE_OPENAI_VERSION"),
)