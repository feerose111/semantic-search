from fastapi import FastAPI, Query
from backend.search.query_milvus import search_documents

app = FastAPI()

@app.get("/search")
def search(q: str = Query(..., description="Search query")):
    results = search_documents(q)
    return {"results": results}
