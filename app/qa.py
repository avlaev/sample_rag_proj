from fastapi import APIRouter, UploadFile, File, Depends
from app.vector_store import collection
from openai import OpenAI
from app.config import OPENAI_API_KEY
from pydantic import BaseModel
from app.dependencies import verify_api_key
from app.logger import logger
import nltk
from nltk.corpus import stopwords
import re

nltk.download('stopwords')
stop_words = set(stopwords.words("english"))

router = APIRouter()
client = OpenAI(api_key=OPENAI_API_KEY)

class QuestionRequest(BaseModel):
    question: str

def keyword_filter(text):
    words = re.findall(r"\w+", text.lower())
    return [word for word in words if word not in stop_words]

@router.post("/ask", dependencies=[Depends(verify_api_key)])
async def ask_question(request: QuestionRequest):
    question = request.question
    logger.info("🔍 Received question: %s", question)

    # Step 1: Embed the question using OpenAI
    embedding_response = client.embeddings.create(
        input=question,
        model="text-embedding-ada-002"
    )
    embedded_query = embedding_response.data[0].embedding

    # Step 2: Perform vector similarity search
    results = collection.query(
        query_embeddings=[embedded_query],
        n_results=5  # Retrieve more candidates for hybrid filtering
    )
    logger.info("Retrieved context chunks")

    candidates = results["documents"][0]
    distances = results["distances"][0]

    # Step 3: Hybrid scoring (vector + keyword overlap)
    keywords = set(keyword_filter(question))
    logger.info("Extracted keywords: %s", keywords)

    def hybrid_score(text, distance):
        overlap = keywords.intersection(set(keyword_filter(text)))
        boost = len(overlap)
        return distance - (boost * 0.1)  # Lower is better

    sorted_chunks = sorted(
        zip(candidates, distances),
        key=lambda x: hybrid_score(x[0], x[1])
    )

    best_chunks = [chunk for chunk, _ in sorted_chunks[:3]]
    context = "\n".join(best_chunks)
    logger.info("🔎 Context sent to GPT:\n%s", context)

    # Step 4: Construct messages for GPT
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful and honest assistant. "
                "Use only the provided context below to answer the user's question. "
                "If the context does not contain the answer, respond with \"I don't know.\" "
                "Do not make up facts. Answer in a clear and concise way."
            )
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {question}"
        }
    ]
    logger.info("GPT prompt:\n%s", messages)

    # Step 5: Query OpenAI chat model
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    logger.info("Got response from GPT")

    answer = response.choices[0].message.content

    logger.info("Final Response Sent to User:")
    logger.info("Question: %s", question)
    logger.info("Answer: %s", answer)
    logger.info("Similarity Scores: %s", distances)
    logger.info("Chunks Used:\n%s", context)

    return {
        "answer": answer,
        "context_used": best_chunks
    }
