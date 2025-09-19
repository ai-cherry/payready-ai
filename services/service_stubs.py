#!/usr/bin/env python3
"""
Service stubs for development - mock the expected services
Run this to start stub services on ports 8001, 8002, 8003, 8787
"""

import asyncio
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from typing import Dict, Any
import multiprocessing
import time


# Stub service for domain routing (8003)
app_domain = FastAPI(title="Domain Service Stub")

@app_domain.post("/{domain}/process")
async def process_domain(domain: str, request: Dict[str, Any]):
    """Mock domain processing endpoint."""
    return JSONResponse({
        "domain": domain,
        "status": "processed",
        "message": f"Mock response from {domain} domain",
        "input": request.get("message", ""),
        "timestamp": time.time()
    })


# Stub service for RAG (8787)
app_rag = FastAPI(title="RAG Service Stub")

@app_rag.post("/query")
async def query_rag(request: Dict[str, Any]):
    """Mock RAG query endpoint."""
    return JSONResponse({
        "results": [
            {
                "text": f"Mock result 1 for: {request.get('query', '')}",
                "score": 0.95,
                "metadata": {"source": "mock"}
            },
            {
                "text": f"Mock result 2 for: {request.get('query', '')}",
                "score": 0.85,
                "metadata": {"source": "mock"}
            }
        ],
        "query": request.get("query", ""),
        "labels": request.get("labels", [])
    })


# Stub service for Gateway (8001)
app_gateway = FastAPI(title="Gateway Service Stub")

@app_gateway.post("/chat")
async def chat(request: Dict[str, Any]):
    """Mock chat endpoint."""
    return JSONResponse({
        "response": f"Gateway mock response to: {request.get('message', '')}",
        "status": "success"
    })


# Stub service for additional services (8002)
app_services = FastAPI(title="Services Stub")

@app_services.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "mock"}


def run_service(app, port: int, name: str):
    """Run a FastAPI app on specified port."""
    print(f"Starting {name} on port {port}...")
    uvicorn.run(app, host="localhost", port=port, log_level="error")


def main():
    """Start all stub services."""
    services = [
        (app_gateway, 8001, "Gateway"),
        (app_services, 8002, "Services"),
        (app_domain, 8003, "Domain Router"),
        (app_rag, 8787, "RAG Service")
    ]

    processes = []

    print("Starting PayReady AI service stubs...")
    print("-" * 40)

    for app, port, name in services:
        p = multiprocessing.Process(target=run_service, args=(app, port, name))
        p.start()
        processes.append(p)
        print(f"✓ {name} started on http://localhost:{port}")

    print("-" * 40)
    print("All stubs running. Press Ctrl+C to stop.")

    try:
        # Keep main process alive
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("\nShutting down stubs...")
        for p in processes:
            p.terminate()
        print("Done.")


if __name__ == "__main__":
    main()