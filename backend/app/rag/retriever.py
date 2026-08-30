"""
Given a query (the user's task), returns the most relevant code chunks
from Qdrant - this is what makes the coder node "codebase-aware".
"""

from sentence_transformers import SentenceTransformer
from app.rag.vectorstore import client , COLLECTION_NAME

_model = SentenceTransformer("all-MiniLM-L6-v2")

def retrieve_context(query:str , top_k:int=3)-> list[dict]:
    query_embedding = _model.encode(query).tolist()

    results = client.search(
        collection_name=COLLECTION_NAME , 
        query_vector=query_embedding ,
        limit=top_k
    )
    return [
        {"file" : r.payload['file'] , "text" : r.payload['text'] , "score" : r.score}
            for r in results]