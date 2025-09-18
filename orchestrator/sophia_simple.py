#!/usr/bin/env python3
"""Simple orchestrator that routes messages to appropriate domains."""

import requests


def route(msg: str):
    """Route message to appropriate domain and action."""
    m = msg.lower()
    if "bi" in m or "slack" in m or "channel" in m or "activity" in m:
        return ("bi", "slack_insights")
    if "health" in m or "renewal" in m or "client" in m:
        return ("client-health", "summary")
    return ("ops", "lookup")


def handle(msg: str) -> dict:
    """Handle a message by routing to appropriate domain."""
    domain, action = route(msg)
    try:
        r = requests.post(f"http://localhost:8000/call/{domain}/{action}", json={"q": msg})
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e), "domain": domain, "action": action}


if __name__ == "__main__":
    # Test the orchestrator
    test_messages = [
        "show bi slack insights for last week",
        "get client health metrics",
        "lookup operational data",
    ]

    for msg in test_messages:
        print(f"\nQuery: {msg}")
        result = handle(msg)
        print(f"Result: {result}")