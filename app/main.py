from fastapi import FastAPI
from app.ingestion import upload_file_router
from app.qa import router as qa_router
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.limiter import limiter

app = FastAPI()

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(upload_file_router)
app.include_router(qa_router)

# CORS settings
origins = [
    "http://localhost:3000",  # React dev frontend
    "http://127.0.0.1:3000",
    "http://localhost",
    "https://your-production-domain.com",  # Add your actual domain here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,             # domains allowed
    allow_credentials=True,
    allow_methods=["*"],               # allow all HTTP methods
    allow_headers=["*"],               # allow all headers
)

@app.get("/")
def read_root():
    return {"status": "Secure RAG API running"}