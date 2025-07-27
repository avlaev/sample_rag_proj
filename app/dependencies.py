from fastapi import Header, HTTPException, Depends, Request

from app.config import API_KEY
from app.config import OPENAI_API_KEY
import datetime
from app.logger import logger

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")
    logger.info(f"API Key Used: {x_api_key}")
    logger.info(f"Timestamp: {datetime.datetime.now()}")
