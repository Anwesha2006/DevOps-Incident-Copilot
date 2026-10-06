from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_retries=0,
    timeout=30
)

print("Sending request...")

response = llm.invoke("Say hello in one sentence.")

print("Response:")
print(response.content)