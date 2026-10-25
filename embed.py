import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.environ["AZURE_OPENAI_BASE_URL"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
)

response = client.embeddings.create(
    model="text-embedding-3-small",
    input="Hello Azure"
)

print("Embedding SUCCESS!")
print("Dimensions:", len(response.data[0].embedding))