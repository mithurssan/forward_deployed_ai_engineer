import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai

BATCH_SIZE = 10
MAX_RETRIES = 3

def load_jsonl(path):
    records = []

    if not path.exists():
        return records

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))

    return records


def write_jsonl(records, path):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                    sort_keys=True,
                )
                + "\n"
            )

def create_embedding(client, model, text):
    result = client.models.embed_content(
        model=model,
        contents=text,
    )

    return result.embeddings[0].values

def create_embedding_with_retry(
    client,
    model,
    text,
    max_retries=MAX_RETRIES,
):
    for attempt in range(1, max_retries + 1):
        try:
            return create_embedding(
                client=client,
                model=model,
                text=text,
            )
        
        except Exception as error:
            if attempt == max_retries:
                raise error

        wait_seconds = attempt * 2

        print(
            f"Request failed. Retrying in "
            f"{wait_seconds} seconds..."
        )

        time.sleep(wait_seconds)

def main():
    project_root = Path(__file__).resolve().parents[2]

    load_dotenv(project_root / ".env")

    api_key = os.getenv("AI_API_KEY")
    model = os.getenv("AI_EMBEDDING_MODEL")

    if not api_key:
        raise ValueError(
            "AI_API_KEY is missing from .env"
        )

    if not model:
        raise ValueError(
            "AI_EMBEDDING_MODEL is missing from .env"
        )

    input_path = (
        project_root
        / "data"
        / "processed"
        / "chunks_selected.jsonl"
    )

    output_path = (
        project_root
        / "data"
        / "processed"
        / "embeddings.jsonl"
    )

    run_log_path = (
        project_root
        / "embedding_run_log.json"
    )

    chunks = load_jsonl(input_path)
    existing_records = load_jsonl(output_path)

    #Store existing records by chunk_id to prevent duplicate output
    records_by_id = {
        record["chunk_id"]: record
        for record in existing_records
    }

    client = genai.Client(api_key=api_key)

    processed = 0
    skipped = 0
    failures = []

    print(f"Loaded {len(chunks)} chunks")

    for batch_start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[
            batch_start:batch_start + BATCH_SIZE
        ]

        batch_number = (
            batch_start // BATCH_SIZE
        ) + 1

        for chunk in batch:
            chunk_id = chunk["chunk_id"]

            if chunk_id in records_by_id:
                skipped += 1
                continue
            
            try:
                vector = create_embedding_with_retry(
                    client=client,
                    model=model,
                    text=chunk["text"],
                )

                records_by_id[chunk_id] = {
                    **chunk,
                    "embedding_model": model,
                    "embedding": vector,
                }

                processed += 1

            except Exception as error:
                failures.append(
                    {
                        "chunk_id": chunk_id,
                        "error": str(error),
                    }
                )

            #save after every batch
            write_jsonl(
                list(records_by_id.values()),
                output_path,
            )

            print(f"Batch {batch_number} processed")
        
        run_log = {
            "model": model,
            "batch_size": BATCH_SIZE,
            "chunks_loaded": len(chunks),
            "embedding_generated": processed,
            "existing_records_skipped": skipped,
            "total_embeddings_saved": len(records_by_id),
            "failure_count": len(failures),
            "failures": failures,
        }

        with run_log_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                run_log,
                file,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        
        print(f"New embeddings generated: {processed}")
        print(f"Existing records skipped: {skipped}")
        print(f"Total embeddings saved: {len(records_by_id)}")
        print(f"Failures: {len(failures)}")
        print(f"Output: {output_path}")
        print(f"Run log: {run_log_path}")

if __name__ == "__main__":
    main()
