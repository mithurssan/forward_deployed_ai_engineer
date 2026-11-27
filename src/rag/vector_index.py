import argparse
import json
from pathlib import Path

import chromadb

COLLECTION_NAME = "policy_chunks"
BATCH_SIZE = 50

def load_jsonl(path):
    records = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))

    return records

def build_metdata(record):
    #metadata for filtering and traceability

    approved_fields = [
        "source_id",
        "title",
        "document_type",
        "category",
        "version",
        "effective_date",
        "access_label",
        "status",
        "relative_path",
        "checksum",
        "heading",
        "section_title",
        "section_sequence",
        "chunk_sequence",
        "strategy",
        "embedding_model",
    ]

    metadata = {}

    for field in approved_fields:
        value = record.get(field)

        #no null in chroma metada
        if value is not None:
            metadata[field] = value

    return metadata

def create_vector_index(rebuild=False):
    project_root = Path(__file__).resolve().parents[2]

    embeddings_path = (
        project_root
        / "data"
        / "processed"
        / "embeddings.jsonl"
    )

    vector_index_path = (
        project_root
        / "data"
        / "vector_index"
    )

    if not embeddings_path.exists():
        raise FileNotFoundError(
            f"Embedding file not found: {embeddings_path}"
        )
    
    records = load_jsonl(embeddings_path)

    if not records:
        raise ValueError("No embedding records were found.")

    client = chromadb.PersistentClient(
        path=str(vector_index_path)
    )

    existing_collections = [
        collection.name
        for collection in client.list_collections()
    ]

    if rebuild and COLLECTION_NAME in existing_collections:
        client.delete_collection(
            name=COLLECTION_NAME
        )
    
        print("Existing vector index deleted.")
    
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=None,
        configuration={
            "hnsw": {
                "space": "cosine"
            }
        },
    )

    for batch_start in range(0, len(records), BATCH_SIZE):
        batch = records[
            batch_start:batch_start + BATCH_SIZE
        ]

        ids = [
            record["chunk_id"]
            for record in batch
        ]

        documents = [
            record["text"]
            for record in batch
        ]

        embeddings = [
            record["embedding"]
            for record in batch
        ]

        metadatas = [
            build_metdata(record)
            for record in batch
        ]

        collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        batch_number = (
            batch_start // BATCH_SIZE
        ) + 1

        print(f"Index batch {batch_number} stored")

    print("Vector index completed.")
    print(f"Input records: {len(records)}")
    print(f"Records in index: {collection.count()}")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Index location: {vector_index_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Build the persistent vector index."
    )

    parser.add_argument(
        "--rebuild",
        action="store_true",
        help = "Delete and fully rebuild the collection.",
    )

    arguments = parser.parse_args()

    create_vector_index(
        rebuild=arguments.rebuild
    )

if __name__ == "__main__":
    main()

