from openai import OpenAI
from app.config import OPENAI_API_KEY
from app.vector_store import collection

client = OpenAI(api_key=OPENAI_API_KEY)

def embed_and_store(chunks):
    for i, chunk in enumerate(chunks):
        response = client.embeddings.create(
            input=chunk,
            model="text-embedding-ada-002"
        )
        embedding = response.data[0].embedding
        collection.add(
            documents=[chunk],
            embeddings=[embedding],
            ids=[f"chunk_{i}"]
        )