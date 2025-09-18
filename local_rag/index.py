#!/usr/bin/env python3
"""Milvus Lite RAG indexer for PayReady AI."""

import os
import hashlib
from pathlib import Path
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from pymilvus import MilvusClient
import json


class RAGIndexer:
    """RAG indexer using Milvus Lite."""

    def __init__(self):
        self.db_path = os.getenv("MILVUS_URI", "milvus.db")
        self.collection_name = os.getenv("COLLECTION_NAME", "payready_docs")
        self.embed_model = SentenceTransformer(os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2"))
        self.dim = int(os.getenv("MILVUS_DIM", "384"))
        self.client = MilvusClient(self.db_path)
        self._init_collection()

    def _init_collection(self):
        """Initialize Milvus collection."""
        collections = self.client.list_collections()
        if self.collection_name not in collections:
            schema = {
                "fields": [
                    {"name": "id", "type": "VARCHAR", "max_length": 64, "is_primary": True},
                    {"name": "text", "type": "VARCHAR", "max_length": 65535},
                    {"name": "embedding", "type": "FLOAT_VECTOR", "dim": self.dim},
                    {"name": "labels", "type": "JSON"},
                    {"name": "metadata", "type": "JSON"}
                ]
            }
            self.client.create_collection(
                collection_name=self.collection_name,
                schema=schema
            )
            print(f"Created collection: {self.collection_name}")
        else:
            print(f"Collection exists: {self.collection_name}")

    def _generate_id(self, text: str) -> str:
        """Generate deterministic ID for text (idempotency)."""
        return hashlib.sha256(text.encode()).hexdigest()[:32]

    def index_text(self, text: str, labels: List[str] = None, metadata: Dict = None) -> str:
        """Index a text document."""
        doc_id = self._generate_id(text)

        existing = self.client.query(
            collection_name=self.collection_name,
            filter=f'id == "{doc_id}"',
            output_fields=["id"]
        )

        if existing:
            print(f"Document already indexed: {doc_id}")
            return doc_id

        embedding = self.embed_model.encode(text).tolist()

        data = {
            "id": doc_id,
            "text": text,
            "embedding": embedding,
            "labels": labels or [],
            "metadata": metadata or {}
        }

        self.client.insert(
            collection_name=self.collection_name,
            data=[data]
        )

        print(f"Indexed document: {doc_id}")
        return doc_id

    def index_batch(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Index multiple documents."""
        ids = []
        for doc in documents:
            doc_id = self.index_text(
                text=doc["text"],
                labels=doc.get("labels"),
                metadata=doc.get("metadata")
            )
            ids.append(doc_id)
        return ids

    def search(self, query: str, labels: List[str] = None, top_k: int = 5) -> List[Dict]:
        """Search for similar documents."""
        query_embedding = self.embed_model.encode(query).tolist()

        filter_expr = None
        if labels:
            label_conditions = [f'JSON_CONTAINS(labels, "{label}")' for label in labels]
            filter_expr = " OR ".join(label_conditions)

        results = self.client.search(
            collection_name=self.collection_name,
            data=[query_embedding],
            limit=top_k,
            filter=filter_expr,
            output_fields=["text", "labels", "metadata"]
        )

        formatted_results = []
        for hit in results[0]:
            formatted_results.append({
                "id": hit["id"],
                "text": hit["text"],
                "score": hit["distance"],
                "labels": hit["labels"],
                "metadata": hit["metadata"]
            })

        return formatted_results

    def delete_by_id(self, doc_id: str) -> bool:
        """Delete document by ID."""
        self.client.delete(
            collection_name=self.collection_name,
            filter=f'id == "{doc_id}"'
        )
        print(f"Deleted document: {doc_id}")
        return True

    def get_stats(self) -> Dict:
        """Get collection statistics."""
        stats = self.client.get_collection_stats(self.collection_name)
        return {
            "collection": self.collection_name,
            "document_count": stats.get("row_count", 0),
            "index_size": stats.get("data_size", 0),
            "embedding_dim": self.dim
        }


def main():
    """Test RAG indexer."""
    indexer = RAGIndexer()

    # Sample documents
    docs = [
        {
            "text": "PayReady AI provides unified BI dashboard for CEO insights.",
            "labels": ["product", "dashboard"],
            "metadata": {"source": "product_docs", "version": "0.1.0"}
        },
        {
            "text": "Apollo.io connector enables sales team to track client health metrics.",
            "labels": ["sales", "apollo", "client-health"],
            "metadata": {"source": "feature_docs", "connector": "apollo"}
        },
        {
            "text": "RBAC system ensures secure access control based on user roles.",
            "labels": ["security", "rbac"],
            "metadata": {"source": "security_docs", "priority": "high"}
        }
    ]

    # Index documents
    print("\nIndexing documents...")
    ids = indexer.index_batch(docs)
    print(f"Indexed {len(ids)} documents")

    # Test search
    print("\nSearching for 'client health'...")
    results = indexer.search("client health", labels=["sales"])
    for r in results:
        print(f"  - Score: {r['score']:.3f}, Text: {r['text'][:100]}")

    # Get stats
    print("\nCollection stats:")
    stats = indexer.get_stats()
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()