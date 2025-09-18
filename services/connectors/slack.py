#!/usr/bin/env python3
"""Slack connector for BI ONLY (read-only) - NO MCP, NO coding agent hooks."""

import os
import httpx

BASE = "https://slack.com/api"
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

# IMPORTANT: This connector is ONLY used from the BI domain via the gateway.
# It is NOT connected to any MCP servers or coding tools.


def _client():
    """Create authenticated Slack client."""
    if not SLACK_BOT_TOKEN:
        raise RuntimeError("SLACK_BOT_TOKEN not set")
    return httpx.Client(headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}, timeout=20)


def list_conversations(limit: int = 200):
    """List Slack channels/conversations."""
    with _client() as c:
        r = c.get(f"{BASE}/conversations.list", params={"limit": limit})
        r.raise_for_status()
        data = r.json()
        if not data.get("ok"):
            raise RuntimeError(f"Slack error: {data}")
        return [
            {
                "id": ch["id"],
                "name": ch.get("name"),
                "is_archived": ch.get("is_archived", False),
                "is_channel": ch.get("is_channel", False),
                "is_group": ch.get("is_group", False),
                "is_im": ch.get("is_im", False),
                "is_mpim": ch.get("is_mpim", False),
                "is_private": ch.get("is_private", False),
                "num_members": ch.get("num_members", 0),
            }
            for ch in data.get("channels", [])
        ]


def read_message_counts(channel_id: str, oldest: float | None = None, latest: float | None = None):
    """Get message counts for a channel."""
    params = {"channel": channel_id, "limit": 1000}
    if oldest:
        params["oldest"] = oldest
    if latest:
        params["latest"] = latest

    with _client() as c:
        r = c.get(f"{BASE}/conversations.history", params=params)
        r.raise_for_status()
        data = r.json()
        if not data.get("ok"):
            raise RuntimeError(f"Slack error: {data}")

        msgs = data.get("messages", [])
        return {
            "count": len(msgs),
            "has_more": data.get("has_more", False),
            "oldest": oldest,
            "latest": latest,
        }


def get_channel_info(channel_id: str):
    """Get detailed channel information."""
    with _client() as c:
        r = c.get(f"{BASE}/conversations.info", params={"channel": channel_id})
        r.raise_for_status()
        data = r.json()
        if not data.get("ok"):
            raise RuntimeError(f"Slack error: {data}")
        return data.get("channel", {})


def get_users_list(limit: int = 200):
    """Get list of workspace users."""
    with _client() as c:
        r = c.get(f"{BASE}/users.list", params={"limit": limit})
        r.raise_for_status()
        data = r.json()
        if not data.get("ok"):
            raise RuntimeError(f"Slack error: {data}")
        return [
            {
                "id": u["id"],
                "name": u.get("name"),
                "real_name": u.get("real_name"),
                "is_bot": u.get("is_bot", False),
                "is_admin": u.get("is_admin", False),
                "is_owner": u.get("is_owner", False),
                "deleted": u.get("deleted", False),
            }
            for u in data.get("members", [])
        ]