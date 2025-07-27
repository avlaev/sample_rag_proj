from fastapi import FastAPI
from app.ingestion import upload_file_router
from app.qa import router as qa_router

app = FastAPI()

app.include_router(upload_file_router)
app.include_router(qa_router)

@app.get("/")
def read_root():
    return {"status": "Secure RAG API running"}