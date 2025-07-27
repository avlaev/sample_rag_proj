from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.embeddings import embed_and_store
import os
from app.dependencies import verify_api_key
from langchain.text_splitter import RecursiveCharacterTextSplitter
import fitz  # PyMuPDF
import pandas as pd

upload_file_router = APIRouter()

@upload_file_router.post("/upload", dependencies=[Depends(verify_api_key)])
async def upload_file(file: UploadFile = File(...)):
    content_type = file.content_type
    filename = file.filename

    if content_type == "text/plain":
        text = (await file.read()).decode("utf-8")

    elif content_type == "application/pdf":
        contents = await file.read()
        doc = fitz.open(stream=contents, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()

    elif content_type in ["text/csv", "application/vnd.ms-excel"]:
        df = pd.read_csv(file.file)
        text = df.to_string()

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {content_type}")


    chunks = split_text(text)
    embed_and_store(chunks)

    return {"status": "uploaded and embedded", "chunks": len(chunks)}


def split_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", "!", "?", " ", ""]
    )
    return splitter.split_text(text)
