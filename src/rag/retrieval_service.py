import argparse
import json
import os
import time
import re
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from google import genai

COLLECTION_NAME = "policy_chunks"
MAX_RETRIES = 3

class RetrievalService:
    def __init__(self):
        self.project_root = Path(__file__).resolve().parents[2]

        load_dotenv(self.project_root / ".env")

        api_key = os.getenv("AI_API_KEY")
        self.model = os.getenv("AI_EMBEDDING_MODEL")

        if not api_key:
            raise ValueError(
                "AI_API_KEY is missing from .env"
            )

        if not self.model:
            raise ValueError(
                "AI_EMBEDDING_MODEL is missing from .env"
            )

        vector_index_path = (
            self.project_root
            / "data"
            / "vector_index"
        )

        if not vector_index_path.exists():
            raise FileNotFoundError(
                "Vector index was not found. "
                "Run vector_index.py --rebuild first."
            )

        self.embedding_client = genai.Client(
            api_key=api_key
        )

        self.chroma_client = chromadb.PersistentClient(
            path=str(vector_index_path)
        )

        self.collection = self.chroma_client.get_collection(
            name=COLLECTION_NAME
        )

    def embed_query(self, query):
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                result = (
                    self.embedding_client
                    .models
                    .embed_content(
                        model=self.model,
                        contents=query,
                    )
                )
                
                return result.embeddings[0].values
            
            except Exception:
                if attempt == MAX_RETRIES:
                    raise

                wait_seconds = attempt * 5

                print(
                    "Embedding request failed. "
                    f"Retrying in {wait_seconds} seconds..."
                )

                time.sleep(wait_seconds)

    def build_filters(
        self,
        document_type=None,
        version=None,
        access_label=None,
    ):
        filters = []

        if document_type:
            filters.append(
                {"document_type": document_type}
            )
        
        if version:
            filters.append(
                {"version": version}
            )
        
        if access_label:
            filters.append(
                {"access_label": access_label}
            )
        
        if not filters:
            return None
        
        if len(filters) == 1:
            return filters[0]
        
        return {
            "$and": filters
        }

    def rerank(self, query, results):
        query_words = set(
            re.findall(r"\b\w+b", query.lower())
        )

        reranked_results = []

        for result in results:
            searchable_text = (
                result["metada"].get("heading", "")
                + " "
                + result["metadata"].get("title", "")
                + " "
                + result["text"]
            )

            text_words = set(
                re.findall(
                    r"\b\w+\b",
                    searchable_text.lower(),
                )
            )

            overlap = query_words & text_words

            reranked_result = result.copy()

            reranked_result["original_score"] = result["score"]
            reranked_result["rerank_score"] = len(overlap)
            reranked_result["matched_terms"] = sorted(overlap)

            reranked_results.append(reranked_result)

        return sorted(
            reranked_results,
            key=lambda result: (
                result["rerank_score"],
                result["original_score"],
            ),
            reverse=True,
        )

    def retrieve(
        self,
        query, 
        top_k=3, 
        document_type=None, 
        version=None,
        access_label=None,
        rerank=False,
    ):
        if not query or not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        if top_k < 1:
            raise ValueError(
                "top_k must be at least 1."
            )

        available_records = self.collection.count()

        if available_records == 0:
            raise ValueError(
                "The vector index is empty."
            )
        
        top_k = min(top_k, available_records)

        candidate_count = top_k

        if rerank:
            candidate_count = min(
                top_k * 3,
                available_records,
            )

        query_embedding = self.embed_query(
            query.strip()
        )

        where_filter = self.build_filters(
            document_type=document_type,
            version=version,
            access_label=access_label,
        )

        query_parameters = {
            "query_embeddings": [query_embedding],
            "n_results": candidate_count,
            "include": [
                "documents",
                "metadatas",
                "distances",
            ],
        }

        if where_filter:
            query_parameters["where"] = where_filter
        
        results = self.collection.query(
            **query_parameters
        )

        retrieved_chunks = []

        for chunk_id, text, metadata, distance in zip(
            results["ids"][0],
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            score = 1 - distance

            retrieved_chunks.append(
                {
                    "chunk_id": chunk_id,
                    "text": text,
                    "score": round(score, 4),
                    "distance": round(distance, 4),
                    "metadata": metadata,
                }
            )
        
        if rerank:
            retrieved_chunks = self.rerank(
                query=query,
                results=retrieved_chunks,
            )
        
        return retrieved_chunks[:top_k]

def main():
    parser = argparse.ArgumentParser(
        description="Search the policy vector index."
    )

    parser.add_argument(
        "--query",
        required=True,
        help="Question to search for."
    )

    parser.add_argument(
        "--document-type",
        help="Filter by document_type.",
    )

    parser.add_argument(
        "--version",
        help="Filter by version.",
    )

    parser.add_argument(
        "--access-label",
        help="Filter by access_label.",
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of chunks to return.",
    )

    parser.add_argument(
        "--rerank",
        action="store_true",
        help="Apply deterministic keyword reranking."
    )

    arguments = parser.parse_args()

    service = RetrievalService()

    results = service.retrieve(
        query=arguments.query,
        top_k=arguments.top_k,
        document_type=arguments.document_type,
        version=arguments.version,
        access_label=arguments.access_label,
        rerank=arguments.rerank,
    )

    evidence = {
        "query": arguments.query,
        "top_k": arguments.top_k,
        "reranking_enabled": arguments.rerank,
        "filters": {
            "document_type": arguments.document_type,
            "version": arguments.version,
            "access_label": arguments.access_label,
        },
        "results": results,
    }

    evidence_path = (
        service.project_root
        / "retrieval_filtered_results.json"
    )

    with evidence_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            evidence,
            file,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )

    print(
        json.dumps(
            evidence,
            ensure_ascii=False,
            indent=2,
        )
    )

    print(f"\nEvidence saved to: {evidence_path}")

if __name__ == "__main__":
    main()