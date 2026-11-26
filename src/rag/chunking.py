import json
from pathlib import Path

CHUNK_SIZE = 500
OVERLAP = 50

def fixed_chunk(text, source_id, section, metadata, chunk_size=500, overlap=50):

    chunks = []
    start = 0
    chunk_number = 1

    while start < len(text):
        end = start + chunk_size
        chunk_text = text[start:end].strip()

        if chunk_text:
            chunks.append(
                {
                    "chunk_id": (
                        f"{source_id}_"
                        f"{section['sequence']}_"
                        f"{chunk_number:03d}"
                    ),
                    "source_id": source_id,
                    "section_title": section["section_title"],
                    "section_sequence": section["sequence"],
                    "chunk_sequence": chunk_number,
                    "text": chunk_text,
                    **metadata,
                }
            )

            chunk_number += 1
        
        start += chunk_size - overlap
    
    return chunks

def structure_aware_chunk(
    document,
    target_size = 500,
):
    chunks = []
    current_text = ""
    current_heading = ""
    chunk_number = 1

    source_id = document["source_id"]

    metadata = {
        key: value
        for key, value in document.items()
        if key != "sections"
    }

    for section in document["sections"]:
        heading = section["section_title"]
        paragraphs = section["text"].split("\n")

        section_text = heading + "\n"

        for paragraph in paragraphs:
            paragraph = paragraph.strip()

            if not paragraph:
                continue
            
            proposed_text = section_text + paragraph + "\n"
        
            if (
                len(current_text) + len(proposed_text)
                <= target_size
            ):
                if not current_heading:
                    current_heading = heading

                current_text += proposed_text
                section_text = ""

            else:
                if current_text.strip():
                    chunks.append(
                        {
                            **metadata,
                            "chunk_id": (
                                f"{source_id}_structure_"
                                f"{chunk_number:03d}"
                            ),
                            "heading": current_heading,
                            "chunk_sequence": chunk_number,
                            "strategy": "structure_aware",
                            "text": current_text.strip(),
                        }
                    )

                    chunk_number += 1
                
                current_heading = heading
                current_text = proposed_text
                section_text = ""
    
    if current_text.strip():
        chunks.append(
            {
                **metadata,
                "chunk_id": (
                    f"{source_id}_structure_"
                    f"{chunk_number:03d}"
                ),
                "heading": current_heading,
                "chunk_sequence": chunk_number,
                "strategy": "structure_aware",
                "text": current_text.strip(),
            }
        )
    
    return connect_exception_chunks(chunks)

def connect_exception_chunks(chunks, max_size=750):

    connected_chunks = []

    for chunk in chunks:
        heading = chunk["heading"].lower()

        is_exception = (
            "exception" in heading
            or "exemption" in heading
        )

        if is_exception and connected_chunks:
            previous_chunk = connected_chunks[-1]

            combined_text = (
                previous_chunk["text"]
                + "\n\n"
                + chunk["text"]
            )
        
            if len(combined_text) <= max_size:
                previous_chunk["text"] = combined_text
                continue

        connected_chunks.append(chunk)
    
    return connected_chunks


def main():
    project_root = Path(__file__).resolve().parents[2]

    input_path = (
        project_root
        / "data"
        / "processed"
        / "documents.jsonl"
    )

    output_path = (
        project_root
        / "data"
        / "processed"
        / "chunks_baseline.jsonl"
    )

    structure_output_path = (
        project_root
        / "data"
        / "processed"
        / "chunks_structure_aware.jsonl"
    )

    all_chunks = []
    documents = []

    with input_path.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
        
            document = json.loads(line)
            documents.append(document)

            source_id = document["source_id"]

            metadata = {
                key: value
                for key, value in document.items()
                if key != "sections"
            }

            for section in document["sections"]:
                section_chunks = fixed_chunk(
                    text=section["text"],
                    source_id=source_id,
                    section=section,
                    metadata=metadata,
                    chunk_size=CHUNK_SIZE,
                    overlap=OVERLAP,
                )

                all_chunks.extend(section_chunks)
        
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open("w", encoding="utf-8") as file:
        for chunk in all_chunks:
            file.write(
                json.dumps(
                    chunk,
                    ensure_ascii=False,
                    sort_keys=True,
                )
                + "\n"
            )
    
    structure_chunks = []

    for document in documents:
        document_chunks = structure_aware_chunk(
            document=document,
            target_size=500,
        )

        structure_chunks.extend(document_chunks)
    
    with structure_output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        for chunk in structure_chunks:
            file.write(
                json.dumps(
                    chunk,
                    ensure_ascii=False,
                    sort_keys=True,
                )
                + "\n"
            )

    print("Baseline chunking completed.")
    print(f"Chunks created: {len(all_chunks)}")
    print(f"Chunk size: {CHUNK_SIZE} characters")
    print(f"Overlap: {OVERLAP} characters")
    print(f"Output: {output_path}")

    print("Structure-aware chunking completed.")
    print(
        f"Alternative chunks created: "
        f"{len(structure_chunks)}"
    )
    print(f"Alternative output: {structure_output_path}")

if __name__ == "__main__":
    main()