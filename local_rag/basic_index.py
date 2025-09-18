#!/usr/bin/env python3
"""Basic in-memory RAG for Phase-0 (no Milvus complexity)."""

import os
import hashlib
import json
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import numpy as np


class BasicRAGIndexer:
    """Simple in-memory RAG indexer for Phase-0."""

    def __init__(self):
        self.embed_model = SentenceTransformer(os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2"))
        self.documents = {}
        self.cache_file = "data/rag_cache.json"

        # Load cached documents if they exist
        self._load_cache()

    def _load_cache(self):
        """Load cached documents from file."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    self.documents = json.load(f)
                print(f"Loaded {len(self.documents)} cached documents")
            except:
                pass

    def _save_cache(self):
        """Save documents to cache file."""
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        with open(self.cache_file, "w") as f:
            json.dump(self.documents, f)

    def _generate_id(self, text: str) -> str:
        """Generate deterministic ID for text."""
        return hashlib.sha256(text.encode()).hexdigest()[:16]

    def index_text(self, text: str, labels: List[str] = None, metadata: Dict = None) -> str:
        """Index a text document."""
        doc_id = self._generate_id(text)

        if doc_id in self.documents:
            print(f"Document already indexed: {doc_id}")
            return doc_id

        # Create embedding
        embedding = self.embed_model.encode(text).tolist()

        # Store document
        self.documents[doc_id] = {
            "text": text,
            "embedding": embedding,
            "labels": labels or [],
            "metadata": metadata or {}
        }

        self._save_cache()
        print(f"Indexed: {text[:50]}...")
        return doc_id

    def search(self, query: str, labels: List[str] = None, top_k: int = 5) -> List[Dict]:
        """Search for similar documents."""
        if not self.documents:
            return []

        # Create query embedding
        query_embedding = self.embed_model.encode(query)

        # Calculate similarities
        results = []
        for doc_id, doc in self.documents.items():
            # Cosine similarity
            doc_embedding = np.array(doc["embedding"])
            similarity = np.dot(query_embedding, doc_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
            )

            # Apply label filter if specified
            if labels:
                if not any(l in doc["labels"] for l in labels):
                    continue

            results.append({
                "id": doc_id,
                "text": doc["text"],
                "score": float(similarity),
                "labels": doc["labels"],
                "metadata": doc["metadata"]
            })

        # Sort by score and return top-k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]


if __name__ == "__main__":
    # Test the indexer
    indexer = BasicRAGIndexer()

    # Index sample documents
    indexer.index_text("PayReady unified BI dashboard for executives", ["product", "bi"])
    indexer.index_text("Slack analytics for business intelligence", ["bi", "slack"])
    indexer.index_text("Client health metrics and renewal tracking", ["client-health"])
    indexer.index_text("Apollo.io integration for sales data", ["sales", "apollo"])

    # Test search
    print("\nSearching for 'slack business'...")
    results = indexer.search("slack business", labels=["bi"])
    for r in results[:3]:
        print(f"  Score: {r['score']:.3f}, Text: {r['text'][:60]}...")

    print("\n✅ Basic RAG indexer ready")