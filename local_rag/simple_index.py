#!/usr/bin/env python3
"""Simplified RAG indexer using pymilvus."""

import os
import hashlib
from sentence_transformers import SentenceTransformer
from pymilvus import MilvusClient


class SimpleRAGIndexer:
    """Simple RAG indexer using pymilvus."""

    def __init__(self):
        self.db_path = os.getenv("MILVUS_URI", "./milvus.db")
        self.collection_name = os.getenv("COLLECTION_NAME", "payready_docs")
        self.embed_model = SentenceTransformer(os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2"))
        self.dim = int(os.getenv("MILVUS_DIM", "384"))

        # Initialize client
        self.client = MilvusClient(uri=self.db_path)

        # Create collection if it doesn't exist
        if self.collection_name not in self.client.list_collections():
            self.client.create_collection(
                collection_name=self.collection_name,
                dimension=self.dim,
                metric_type="L2",  # Euclidean distance
                auto_id=False
            )
            print(f"Created collection: {self.collection_name}")

    def _generate_id(self, text: str) -> str:
        """Generate deterministic ID for text."""
        return hashlib.sha256(text.encode()).hexdigest()[:32]

    def index_text(self, text: str, labels=None, metadata=None) -> str:
        """Index a text document."""
        doc_id = self._generate_id(text)

        # Check if already exists
        results = self.client.query(
            collection_name=self.collection_name,
            filter=f'id == "{doc_id}"',
            limit=1
        )

        if results:
            print(f"Document already indexed: {doc_id[:8]}...")
            return doc_id

        # Create embedding
        embedding = self.embed_model.encode(text).tolist()

        # Insert document
        data = {
            "id": doc_id,
            "vector": embedding,
            "text": text,
            "labels": str(labels or []),
            "metadata": str(metadata or {})
        }

        self.client.insert(
            collection_name=self.collection_name,
            data=[data]
        )

        print(f"Indexed document: {doc_id[:8]}...")
        return doc_id

    def search(self, query: str, labels=None, top_k: int = 5):
        """Search for similar documents."""
        query_embedding = self.embed_model.encode(query).tolist()

        results = self.client.search(
            collection_name=self.collection_name,
            data=[query_embedding],
            limit=top_k,
            output_fields=["text", "labels", "metadata"]
        )

        formatted_results = []
        for hits in results:
            for hit in hits:
                formatted_results.append({
                    "id": hit.get("id"),
                    "text": hit.get("text", ""),
                    "score": hit.get("distance", 0),
                    "labels": hit.get("labels", "[]"),
                    "metadata": hit.get("metadata", "{}")
                })

        # Client-side label filtering if specified
        if labels:
            filtered = []
            for r in formatted_results:
                try:
                    doc_labels = eval(r["labels"]) if isinstance(r["labels"], str) else r["labels"]
                    if any(l in doc_labels for l in labels):
                        filtered.append(r)
                except:
                    pass
            return filtered

        return formatted_results


if __name__ == "__main__":
    # Test the indexer
    indexer = SimpleRAGIndexer()

    # Index sample documents
    indexer.index_text("PayReady unified BI dashboard", ["product", "bi"])
    indexer.index_text("Slack analytics for business intelligence", ["bi", "slack"])
    indexer.index_text("Client health metrics and renewals", ["client-health"])

    # Test search
    print("\nSearching for 'slack analytics'...")
    results = indexer.search("slack analytics", labels=["bi"])
    for r in results[:3]:
        print(f"  Score: {r['score']:.3f}, Text: {r['text'][:60]}...")

    print("\n✅ RAG indexer test complete")