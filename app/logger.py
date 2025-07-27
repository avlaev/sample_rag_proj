import logging

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),  # Save logs to file
        logging.StreamHandler()               # Also print to console
    ]
)

logger = logging.getLogger("secure-rag")
