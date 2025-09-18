#!/usr/bin/env python3
"""FastAPI Gateway with RBAC for PayReady AI."""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import yaml
import os
from pathlib import Path
import httpx
from datetime import datetime


app = FastAPI(title="PayReady AI Gateway", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CallRequest(BaseModel):
    service: str
    method: str
    params: Dict[str, Any]
    labels: Optional[List[str]] = None


class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None
    labels: Optional[List[str]] = None


class RBACManager:
    """Simple RBAC manager for Phase 0."""

    def __init__(self):
        rbac_file = Path(__file__).parent.parent / "policies" / "rbac" / "roles.yaml"
        with open(rbac_file) as f:
            self.config = yaml.safe_load(f)
        self.roles = self.config["roles"]

    def check_permission(self, role: str, resource: str, action: str) -> bool:
        """Check if role has permission for resource:action."""
        if role not in self.roles:
            return False

        role_config = self.roles[role]
        grants = role_config.get("grants", [])

        for grant in grants:
            if self._match_grant(grant, resource, action):
                return True

        return False

    def _match_grant(self, grant: str, resource: str, action: str) -> bool:
        """Check if grant matches resource:action."""
        if grant == "*:*":
            return True

        grant_parts = grant.split(":")
        if len(grant_parts) != 2:
            return False

        grant_resource, grant_action = grant_parts

        if grant_resource == "*" or grant_resource == resource:
            if grant_action == "*" or grant_action == action:
                return True

        if grant_resource.endswith("*"):
            prefix = grant_resource[:-1]
            if resource.startswith(prefix):
                if grant_action == "*" or grant_action == action:
                    return True

        return False

    def get_role_flags(self, role: str) -> List[str]:
        """Get flags for a role."""
        if role not in self.roles:
            return []
        return self.roles[role].get("flags", [])


rbac = RBACManager()


def get_current_user(x_user_role: Optional[str] = Header(None)) -> str:
    """Get current user role from header. Phase 0: default to CEO."""
    return x_user_role or "CEO"


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "PayReady AI Gateway",
        "version": "0.1.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/call")
async def service_call(
    request: CallRequest,
    user_role: str = Depends(get_current_user)
):
    """Generic service call with RBAC."""
    resource = f"{request.service}:{request.method}"
    action = "execute"

    if not rbac.check_permission(user_role, request.service, action):
        raise HTTPException(
            status_code=403,
            detail=f"Role {user_role} lacks permission for {resource}"
        )

    flags = rbac.get_role_flags(user_role)

    try:
        if request.service == "orchestrator":
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:8001/orchestrate",
                    json={
                        "method": request.method,
                        "params": request.params,
                        "labels": request.labels,
                        "user_flags": flags
                    }
                )
                return response.json()

        elif request.service.startswith("connectors"):
            connector_name = request.service.split(":")[1]
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://localhost:8002/{connector_name}/{request.method}",
                    json=request.params
                )
                return response.json()

        elif request.service.startswith("domains"):
            domain_name = request.service.split(":")[1]
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://localhost:8003/{domain_name}/{request.method}",
                    json={
                        "params": request.params,
                        "labels": request.labels
                    }
                )
                return response.json()

        else:
            raise HTTPException(
                status_code=404,
                detail=f"Unknown service: {request.service}"
            )

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )


@app.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    user_role: str = Depends(get_current_user)
):
    """Chat endpoint for Sophia orchestrator."""
    if not rbac.check_permission(user_role, "orchestrator", "sophia"):
        raise HTTPException(
            status_code=403,
            detail=f"Role {user_role} lacks permission for Sophia chat"
        )

    flags = rbac.get_role_flags(user_role)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:8001/sophia/chat",
                json={
                    "message": request.message,
                    "context": request.context,
                    "labels": request.labels,
                    "user_flags": flags,
                    "user_role": user_role
                }
            )
            return response.json()

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Sophia unavailable: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    services = {
        "gateway": "healthy",
        "orchestrator": "unknown",
        "connectors": "unknown",
        "rag": "unknown"
    }

    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get("http://localhost:8001/health")
            if response.status_code == 200:
                services["orchestrator"] = "healthy"
    except:
        pass

    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get("http://localhost:8787/health")
            if response.status_code == 200:
                services["rag"] = "healthy"
    except:
        pass

    all_healthy = all(status == "healthy" for status in services.values())

    return {
        "status": "healthy" if all_healthy else "degraded",
        "services": services,
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)