#!/usr/bin/env python3
"""Simple Orchestrator for Sophia persona - routes to BI domain."""

import os
from datetime import datetime
import requests
import httpx
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END


class SophiaState:
    """State for Sophia orchestrator."""

    def __init__(self):
        self.message: str = ""
        self.context: Dict[str, Any] = {}
        self.labels: List[str] = []
        self.user_flags: List[str] = []
        self.user_role: str = "Default"
        self.response: str = ""
        self.metadata: Dict[str, Any] = {}


class SophiaOrchestrator:
    """Main orchestrator for Sophia."""

    def __init__(self):
        self.graph = self._build_graph()
        self.rag_url = "http://localhost:8787"
        self.portkey_api_key = os.getenv("PORTKEY_API_KEY")
        self.portkey_url = "https://api.portkey.ai/v1"

    def _build_graph(self):
        """Build the LangGraph workflow."""
        workflow = StateGraph(SophiaState)

        workflow.add_node("analyze_request", self.analyze_request)
        workflow.add_node("retrieve_context", self.retrieve_context)
        workflow.add_node("route_to_domain", self.route_to_domain)
        workflow.add_node("generate_response", self.generate_response)

        workflow.set_entry_point("analyze_request")

        workflow.add_edge("analyze_request", "retrieve_context")
        workflow.add_conditional_edges(
            "retrieve_context",
            self.should_route_to_domain,
            {
                "route": "route_to_domain",
                "generate": "generate_response"
            }
        )
        workflow.add_edge("route_to_domain", "generate_response")
        workflow.add_edge("generate_response", END)

        return workflow.compile()

    def analyze_request(self, state: SophiaState) -> SophiaState:
        """Analyze the incoming request."""
        state.metadata["analyzed_at"] = datetime.utcnow().isoformat()

        if "apollo" in state.message.lower() or "sales" in state.message.lower():
            state.labels.append("sales")

        if "financial" in state.message.lower() or "revenue" in state.message.lower():
            state.labels.append("finance")

        if "technical" in state.message.lower() or "code" in state.message.lower():
            state.labels.append("engineering")

        return state

    async def retrieve_context(self, state: SophiaState) -> SophiaState:
        """Retrieve relevant context from RAG."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.rag_url}/query",
                    json={
                        "query": state.message,
                        "labels": state.labels,
                        "top_k": 5
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    state.context["rag_results"] = data.get("results", [])
                    state.metadata["rag_retrieved"] = True
        except Exception as e:
            state.metadata["rag_error"] = str(e)
            state.metadata["rag_retrieved"] = False

        return state

    def should_route_to_domain(self, state: SophiaState) -> str:
        """Decide if request should be routed to a specific domain."""
        if "client-health" in state.labels and "ai_factory" in state.user_flags:
            return "route"

        if len(state.labels) > 0 and state.user_role in ["CEO", "Leadership"]:
            return "route"

        return "generate"

    async def route_to_domain(self, state: SophiaState) -> SophiaState:
        """Route to appropriate domain service."""
        domain = state.labels[0] if state.labels else "general"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"http://localhost:8003/{domain}/process",
                    json={
                        "message": state.message,
                        "context": state.context,
                        "user_role": state.user_role
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    state.context["domain_response"] = data
                    state.metadata["domain_routed"] = domain
        except Exception as e:
            state.metadata["domain_error"] = str(e)
            state.metadata["domain_routed"] = None

        return state

    async def generate_response(self, state: SophiaState) -> SophiaState:
        """Generate final response using LLM."""
        context_str = ""
        if state.context.get("rag_results"):
            context_str = "\n".join([
                f"- {r.get('text', '')}"
                for r in state.context["rag_results"][:3]
            ])

        prompt = f"""You are Sophia, an AI assistant for PayReady.
User Role: {state.user_role}
User Message: {state.message}
Context: {context_str}

Provide a helpful, concise response."""

        try:
            response = await self._call_llm(prompt)
            state.response = response
        except Exception as e:
            state.response = f"I'm having trouble processing your request. Please try again later."
            state.metadata["llm_error"] = str(e)

        return state

    async def _call_llm(self, prompt: str) -> str:
        """Call LLM via Portkey."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.portkey_url}/chat/completions",
                headers={
                    "x-portkey-api-key": self.portkey_api_key,
                    "x-portkey-virtual-key": "anthropic-vk-b42804"
                },
                json={
                    "model": "claude-3-5-sonnet-latest",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            )
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                raise Exception(f"LLM call failed: {response.status_code}")

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a chat request."""
        state = SophiaState()
        state.message = request.get("message", "")
        state.context = request.get("context", {})
        state.labels = request.get("labels", [])
        state.user_flags = request.get("user_flags", [])
        state.user_role = request.get("user_role", "Default")

        result = await self.graph.ainvoke(state)

        return {
            "response": result.response,
            "metadata": result.metadata,
            "timestamp": datetime.utcnow().isoformat()
        }


orchestrator = SophiaOrchestrator()


async def main():
    """Test the orchestrator."""
    request = {
        "message": "Show me the latest client health metrics",
        "user_role": "CEO",
        "user_flags": ["all", "ai_factory"]
    }
    response = await orchestrator.process(request)
    print(response)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())