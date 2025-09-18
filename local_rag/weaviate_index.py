"""Weaviate vector database integration for advanced RAG."""

import os
import weaviate
from weaviate.classes.config import Property, DataType
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class WeaviateIndex:
    """Weaviate cloud vector database for PayReady RAG."""

    def __init__(self):
        # Get credentials from environment
        rest_endpoint = os.getenv("WEAVIATE_REST_ENDPOINT", "")
        api_key = os.getenv("WEAVIATE_ADMIN_API_KEY", "")

        if not rest_endpoint or not api_key:
            raise ValueError("Weaviate credentials not configured in env.rag")

        # Connect to Weaviate cloud
        self.client = weaviate.connect_to_weaviate_cloud(
            cluster_url=f"https://{rest_endpoint}",
            auth_credentials=weaviate.auth.AuthApiKey(api_key)
        )

        self.collection_name = "PayReadyDocs"
        self._ensure_collection()

    def _ensure_collection(self):
        """Create collection if it doesn't exist."""
        try:
            # Check if collection exists
            if not self.client.collections.exists(self.collection_name):
                self.client.collections.create(
                    name=self.collection_name,
                    properties=[
                        Property(name="content", data_type=DataType.TEXT),
                        Property(name="labels", data_type=DataType.TEXT_ARRAY),
                        Property(name="source", data_type=DataType.TEXT),
                        Property(name="domain", data_type=DataType.TEXT),
                    ],
                    vectorizer_config=weaviate.classes.config.Configure.Vectorizer.text2vec_openai(),
                )
                logger.info(f"Created Weaviate collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error ensuring collection: {e}")

    def add_documents(self, documents: List[Dict[str, Any]]) -> int:
        """Add documents to Weaviate."""
        collection = self.client.collections.get(self.collection_name)

        with collection.batch.dynamic() as batch:
            for doc in documents:
                batch.add_object(properties={
                    "content": doc.get("content", ""),
                    "labels": doc.get("labels", []),
                    "source": doc.get("source", "unknown"),
                    "domain": doc.get("domain", "general"),
                })

        return len(documents)

    def search(self, query: str, labels: List[str] = None, k: int = 5) -> List[Dict[str, Any]]:
        """Search Weaviate with optional label filtering."""
        collection = self.client.collections.get(self.collection_name)

        # Build query
        query_builder = collection.query.near_text(query=query, limit=k)

        # Add label filter if provided
        if labels:
            where_filter = weaviate.classes.query.Filter.by_property("labels").contains_any(labels)
            query_builder = query_builder.where(where_filter)

        # Execute search
        response = query_builder.do()

        # Format results
        results = []
        for item in response.objects:
            results.append({
                "content": item.properties.get("content", ""),
                "labels": item.properties.get("labels", []),
                "source": item.properties.get("source", ""),
                "score": item.metadata.certainty if hasattr(item.metadata, 'certainty') else 0.0
            })

        return results

    def close(self):
        """Close Weaviate connection."""
        if self.client:
            self.client.close()