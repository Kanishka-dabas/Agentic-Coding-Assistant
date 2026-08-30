"""
One-time (or re-run-on-demand) script: walks backend/app, chunks each
.py file, embeds the chunks, and stores them in Qdrant
"""

import os
import uuid

from sentence_transformers import SentenceTransformer
from qdrant_client.models import PointStruct

from app.rag.vectorstore import client,COLLECTION_NAME,ensure_collection

CODEBASE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CHUNK_SIZE = 1500

_model = SentenceTransformer("all-MiniLM-L6-v2")

def chunk_text(text : str , chunk_size : int = CHUNK_SIZE)->list[str]:
    return [text[i : i+chunk_size] for i in range(0 , len(text) , chunk_size)]

def ingest_codebase():
    ensure_collection()
    points =[]

    for root,_,files in os.walk(CODEBASE_ROOT):
        for filename in files:
            if not filename.endswith(".py"):
                continue
            filepath = os.path.join(root,filename)
            relative_path = os.path.relpath(CODEBASE_ROOT , filepath)

            with open(filepath , "r" , encoding = "utf-8") as f:
                content = f.read()

            for i , chunk in enumerate(chunk_text(content))  :
                if not chunk.strip():
                    continue
                embedding = _model.encode(chunk).tolist()
                points.append(
                    PointStruct(
                        id= str(uuid.uuid4()),
                        vector= embedding ,
                        payload = {"file":filepath , "chunk_idx":i , "text":chunk }
                    )
                )  

    if points:
        client.upsert(collection_name=COLLECTION_NAME , points=points)

    print(f"Ingested {len(points)} chunks from {CODEBASE_ROOT}")

if __name__ == "__main__":
    ingest_codebase()                    