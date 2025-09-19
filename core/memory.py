#!/usr/bin/env python3
"""
PayReady AI - Unified Memory System
Integrates Redis (cache), Mem0 (persistent), and simple file storage
"""

import os
import json
import time
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from mem0 import Memory
    MEM0_AVAILABLE = True
except ImportError:
    MEM0_AVAILABLE = False


class UnifiedMemory:
    """Simple unified memory system for PayReady AI"""

    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.getcwd()
        self.memory_dir = os.path.expanduser("~/.payready/memory")
        os.makedirs(self.memory_dir, exist_ok=True)

        # Initialize Redis if available
        self.redis_client = None
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
                self.redis_client.ping()  # Test connection
            except:
                self.redis_client = None

        # Initialize Mem0 if available and configured
        self.mem0_client = None
        if MEM0_AVAILABLE and os.getenv('MEM0_API_KEY'):
            try:
                self.mem0_client = Memory(api_key=os.getenv('MEM0_API_KEY'))
            except:
                self.mem0_client = None

        # File-based storage as fallback
        self.conversation_file = os.path.join(self.memory_dir, "conversations.jsonl")
        self.context_file = os.path.join(self.memory_dir, "context.json")

    def remember(self, key: str, value: Any, category: str = "general") -> bool:
        """Store a key-value pair in memory"""
        timestamp = datetime.now().isoformat()

        # Try Redis first (fast cache)
        if self.redis_client:
            try:
                cache_key = f"payready:{category}:{key}"
                self.redis_client.setex(cache_key, 3600, json.dumps(value))  # 1 hour TTL
            except:
                pass

        # Try Mem0 for long-term memory
        if self.mem0_client:
            try:
                self.mem0_client.add(f"{key}: {value}", metadata={
                    "category": category,
                    "timestamp": timestamp,
                    "project": os.path.basename(self.project_root)
                })
            except:
                pass

        # File storage as fallback
        try:
            entry = {
                "timestamp": timestamp,
                "key": key,
                "value": value,
                "category": category,
                "project": os.path.basename(self.project_root)
            }

            with open(self.conversation_file, "a") as f:
                f.write(json.dumps(entry) + "\n")

            return True
        except:
            return False

    def recall(self, query: str, category: str = None) -> List[Dict]:
        """Search memory for relevant information"""
        results = []

        # Try Redis cache first
        if self.redis_client and category:
            try:
                cache_key = f"payready:{category}:{query}"
                cached = self.redis_client.get(cache_key)
                if cached:
                    results.append({
                        "source": "cache",
                        "content": json.loads(cached),
                        "relevance": 1.0
                    })
            except:
                pass

        # Try Mem0 semantic search
        if self.mem0_client:
            try:
                mem0_results = self.mem0_client.search(query, limit=5)
                for result in mem0_results:
                    results.append({
                        "source": "mem0",
                        "content": result.get("memory", ""),
                        "relevance": result.get("score", 0.5)
                    })
            except:
                pass

        # File-based search as fallback
        try:
            if os.path.exists(self.conversation_file):
                with open(self.conversation_file, "r") as f:
                    for line in f:
                        entry = json.loads(line.strip())

                        # Simple keyword matching
                        content = f"{entry['key']} {entry['value']}".lower()
                        if query.lower() in content:
                            if not category or entry.get("category") == category:
                                results.append({
                                    "source": "file",
                                    "content": entry,
                                    "relevance": 0.7
                                })
        except:
            pass

        # Sort by relevance
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results[:10]  # Top 10 results

    def get_context(self) -> Dict:
        """Get current session context"""
        context = {
            "project": os.path.basename(self.project_root),
            "timestamp": datetime.now().isoformat(),
            "redis_available": self.redis_client is not None,
            "mem0_available": self.mem0_client is not None
        }

        # Load persistent context
        if os.path.exists(self.context_file):
            try:
                with open(self.context_file, "r") as f:
                    persistent_context = json.load(f)
                    context.update(persistent_context)
            except:
                pass

        return context

    def save_context(self, context: Dict) -> bool:
        """Save current session context"""
        try:
            context["last_updated"] = datetime.now().isoformat()
            with open(self.context_file, "w") as f:
                json.dump(context, f, indent=2)
            return True
        except:
            return False

    def log_conversation(self, user_input: str, ai_response: str, model: str = None) -> bool:
        """Log a conversation exchange"""
        return self.remember(
            key=f"conversation_{int(time.time())}",
            value={
                "user": user_input,
                "ai": ai_response,
                "model": model,
                "timestamp": datetime.now().isoformat()
            },
            category="conversation"
        )


def main():
    """CLI interface for memory system"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python memory.py <command> [args...]")
        print("Commands:")
        print("  remember <key> <value> [category]")
        print("  recall <query> [category]")
        print("  context")
        sys.exit(1)

    memory = UnifiedMemory()
    command = sys.argv[1]

    if command == "remember" and len(sys.argv) >= 4:
        key = sys.argv[2]
        value = sys.argv[3]
        category = sys.argv[4] if len(sys.argv) > 4 else "general"

        if memory.remember(key, value, category):
            print(f"✓ Remembered: {key} = {value} ({category})")
        else:
            print(f"✗ Failed to remember: {key}")

    elif command == "recall" and len(sys.argv) >= 3:
        query = sys.argv[2]
        category = sys.argv[3] if len(sys.argv) > 3 else None

        results = memory.recall(query, category)
        if results:
            print(f"Found {len(results)} result(s) for '{query}':")
            for i, result in enumerate(results, 1):
                print(f"{i}. [{result['source']}] {result['content']}")
        else:
            print(f"No results found for '{query}'")

    elif command == "context":
        context = memory.get_context()
        print("Current context:")
        for key, value in context.items():
            print(f"  {key}: {value}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()