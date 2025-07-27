import chromadb
from chromadb.config import Settings

chroma_client = chromadb.PersistentClient(path="vector_store")  # this creates the DB folder

collection = chroma_client.get_or_create_collection(name="my_collection")
