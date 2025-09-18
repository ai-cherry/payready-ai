#!/usr/bin/env python3
"""FastAPI service for RAG."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from .basic_index import BasicRAGIndexer as RAGIndexer

app = FastAPI(title="PayReady RAG Service", version="0.1.0")
indexer = RAGIndexer()


class IndexRequest(BaseModel):
    text: str
    labels: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class BatchIndexRequest(BaseModel):
    documents: List[Dict[str, Any]]


class QueryRequest(BaseModel):
    query: str
    labels: Optional[List[str]] = None
    top_k: int = 5


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "PayReady RAG Service",
        "version": "0.1.0",
        "status": "operational"
    }


@app.post("/index")
async def index_document(request: IndexRequest):
    """Index a single document."""
    try:
        doc_id = indexer.index_text(
            text=request.text,
            labels=request.labels,
            metadata=request.metadata
        )
        return {"id": doc_id, "status": "indexed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/index_batch")
async def index_batch(request: BatchIndexRequest):
    """Index multiple documents."""
    try:
        ids = indexer.index_batch(request.documents)
        return {"ids": ids, "count": len(ids), "status": "indexed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
async def query_documents(request: QueryRequest):
    """Query similar documents."""
    try:
        results = indexer.search(
            query=request.query,
            labels=request.labels,
            top_k=request.top_k
        )
        return {"results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/document/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document by ID."""
    try:
        success = indexer.delete_by_id(doc_id)
        return {"id": doc_id, "deleted": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get RAG statistics."""
    try:
        stats = indexer.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        stats = indexer.get_stats()
        return {
            "status": "healthy",
            "collection": stats["collection"],
            "documents": stats["document_count"]
        }
    except:
        return {"status": "unhealthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8787)