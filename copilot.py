from dotenv import load_dotenv
load_dotenv()
import os
from langchain_groq import ChatGroq
from tools import retrieve_history
print("Groq Key:", os.getenv("GROQ_API_KEY"))
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)


def ask_factory_copilot(question, context):
    history = retrieve_history()

    prompt = (
        f"You are EcoLoop Factory Copilot.\n\n"
        f"Historical Machine Knowledge:\n{history}\n\n"
        f"Recent Factory Context:\n{context}\n\n"
        f"Manager Question:\n{question}\n\n"
        "Answer professionally.\n\n"
        "Include:\n"
        "1. Summary\n"
        "2. Root Cause\n"
        "3. Historical Similarity\n"
        "4. Recommended Action\n"
        "5. Estimated Impact\n"
    )

    response = llm.invoke(prompt)
    return response.content