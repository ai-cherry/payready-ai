#!/usr/bin/env python3
"""Slack analytics for BI domain with CSV cache and Neon Postgres sink."""

from fastapi import FastAPI, HTTPException
import pandas as pd
from pathlib import Path
import os
import psycopg
from datetime import datetime
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from services.connectors import slack

app = FastAPI(title="PayReady BI - Slack Analytics")
CACHE = Path("data/foundations/slack_metrics.csv")
NEON_URL = os.getenv("NEON_DATABASE_URL")

# Database schema
DDL = """
CREATE SCHEMA IF NOT EXISTS bi;
CREATE TABLE IF NOT EXISTS bi.slack_channel_activity (
  id SERIAL PRIMARY KEY,
  channel TEXT NOT NULL,
  messages INT NOT NULL,
  period TEXT NOT NULL,
  num_members INT DEFAULT 0,
  is_archived BOOLEAN DEFAULT false,
  is_private BOOLEAN DEFAULT false,
  collected_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_channel_collected ON bi.slack_channel_activity(channel, collected_at DESC);
"""

UPSERT = """
INSERT INTO bi.slack_channel_activity (channel, messages, period, num_members, is_archived, is_private)
VALUES (%s, %s, %s, %s, %s, %s);
"""


@app.post("/slack_insights")
async def slack_insights(period: str = "7d"):
    """Fetch Slack channel activity metrics and persist to CSV + Neon."""
    try:
        # 1) Fetch channels from Slack (read-only)
        channels = slack.list_conversations(limit=200)
        active_channels = [ch for ch in channels if not ch.get("is_archived", False)][:50]  # Cap for Phase-0

        rows = []
        for ch in active_channels:
            try:
                msg_data = slack.read_message_counts(ch["id"])
                rows.append({
                    "channel": ch.get("name") or ch["id"],
                    "messages": msg_data["count"],
                    "num_members": ch.get("num_members", 0),
                    "is_archived": ch.get("is_archived", False),
                    "is_private": ch.get("is_private", False),
                })
            except Exception as e:
                print(f"Error fetching channel {ch.get('name', ch['id'])}: {e}")
                continue

        if not rows:
            return {
                "_labels": ["internal"],
                "period": period,
                "top_channels": [],
                "neon_sink": False,
                "error": "No channel data available"
            }

        df = pd.DataFrame(rows).sort_values("messages", ascending=False)

        # 2) Cache to CSV for quick BI
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        df_with_meta = df.assign(period=period, collected_at=datetime.now().isoformat())
        df_with_meta.to_csv(CACHE, index=False)

        # 3) Write to Neon (if configured)
        neon_success = False
        if NEON_URL:
            try:
                with psycopg.connect(NEON_URL, autocommit=True) as conn:
                    with conn.cursor() as cur:
                        cur.execute(DDL)
                        for rec in df.itertuples(index=False):
                            cur.execute(
                                UPSERT,
                                (
                                    rec.channel,
                                    int(rec.messages),
                                    period,
                                    int(rec.num_members),
                                    bool(rec.is_archived),
                                    bool(rec.is_private),
                                ),
                            )
                neon_success = True
            except Exception as e:
                print(f"Neon write error: {e}")

        top = df.head(10).to_dict(orient="records")
        return {
            "_labels": ["internal"],
            "period": period,
            "total_channels": len(df),
            "top_channels": top,
            "neon_sink": neon_success,
            "csv_cache": str(CACHE),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "bi.slack_analytics"}


@app.get("/stats")
async def stats():
    """Get statistics from cached data."""
    if CACHE.exists():
        df = pd.read_csv(CACHE)
        return {
            "total_records": len(df),
            "unique_channels": df["channel"].nunique() if "channel" in df.columns else 0,
            "cache_file": str(CACHE),
            "last_modified": datetime.fromtimestamp(CACHE.stat().st_mtime).isoformat(),
        }
    return {"error": "No cached data available"}