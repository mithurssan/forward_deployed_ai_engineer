import csv, json, hashlib
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from docx import Document

REQUIRED_FIELDS = {
    "source_id",
    "title",
    "document_type",
    "version",
    "effective_date",
    "access_label",
    "status",
    "relative_path",
}

class IngestionService:
    def __init__(
        self,
        supporting_documents_dir: Path,
        manifest_path: Path,
    ):

        self.supporting_documents_dir = supporting_documents_dir
        self.manifest_path = manifest_path

    def _load_manifest(self):
        with self.manifest_path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            headers = set(reader.fieldnames or [])
            missing_headers = REQUIRED_FIELDS - headers

            if missing_headers:
                raise ValueError(
                    "Missing manifest headers: "
                    + ", ".join(sorted(missing_headers))
                )
            
            return list(reader)

    
    def run(self):
        manifest_rows = self._load_manifest()

        accepted = []
        rejected = []
        warnings = []

        manifest_paths = [
            row["relative_path"]
            for row in manifest_rows
        ]

        path_counts = Counter(manifest_paths)
        source_id_counts = Counter(
            row["source_id"]
            for row in manifest_rows
        )

        for row in manifest_rows:
            source_id = row["source_id"]
            relative_path = row["relative_path"]

            missing_fields = [
                field
                for field in sorted(REQUIRED_FIELDS)
                if not (row.get(field) or "").strip()
            ]

            if missing_fields:
                rejected.append(
                    {
                        "file": relative_path or None,
                        "source_id": source_id or None,
                        "reason": "missing_required_fields",
                        "fields": missing_fields, 
                    }
                )
                continue
            
            if not (row.get("category") or "").strip():
                warnings.append(
                    {
                        "file": relative_path,
                        "source_id": source_id,
                        "reason": "missing_category",
                        "message": (
                            f"Category is missing for source_id "
                            f"'{source_id}'."
                        ),
                    }
                )
            if source_id_counts[source_id] > 1:
                rejected.append(
                    {
                        "file": relative_path,
                        "source_id": source_id,
                        "reason": "duplicate_source_id",
                        "message": (
                            f"source_id '{source_id}' appears more than once "
                            "in the manifest."
                        ),
                    }
                )
                continue
                
            if path_counts[relative_path] > 1:
                rejected.append(
                    {
                        "file": relative_path,
                        "source_id": source_id,
                        "reason": "duplicate_file",
                    }
                )
                continue

            file_path = (
                self.supporting_documents_dir
                / relative_path
            )

            if not file_path.exists():
                rejected.append(
                    {
                        "file": relative_path,
                        "reason": "missing_file",
                    }
                )
                continue
            
            accepted.append(row)
            

        manifest_path_set = set(manifest_paths)

        #Finding files that aren't listed in manifest
        for file_path in self.supporting_documents_dir.rglob("*.docx"):
            relative_path = file_path.relative_to(
                self.supporting_documents_dir
            ).as_posix()

            if relative_path not in manifest_path_set:
                rejected.append(
                    {
                        "file": relative_path,
                        "reason": "unlisted_file",
                    }
                )
        
        validated_sources = sorted(
            accepted,
            key=lambda row: row["source_id"],
        )
        accepted_documents = []
        normalised_documents = []

        for row in validated_sources:
            source_id = row["source_id"]
            relative_path = row["relative_path"]

            file_path = (
                self.supporting_documents_dir
                / relative_path
            )

            try:
                sections = self._extract_docx_sections(file_path)
            except Exception as error:
                rejected.append(
                    {
                        "file": relative_path,
                        "source_id": source_id,
                        "reason": "extraction_failed",
                        "message": str(error),
                    }
                )
                continue
            
            if not sections:
                rejected.append(
                    {
                        "file": relative_path,
                        "source_id": source_id,
                        "reason": "no_content",
                        "message": (
                            "No extractable sections or paragraphs "
                            "were found."
                        ),
                    }
                )
                continue
            
            accepted_documents.append(row)

            checksum = self._calculate_checksum(file_path)

            pre_chunks = []

            for section in sections:
                sequence = section["sequence"]

                pre_chunks.append(
                    {
                        "chunk_id": (
                            f"{source_id}-CHUNK-{sequence:03d}"
                        ),
                        "source_id": source_id,
                        "heading_section": section["section_title"],
                        "sequence": sequence,
                        "access_label": row["access_label"].strip(),
                        "text": section["text"],
                    }
                )       


            normalised_documents.append(
                {
                    "source_id": source_id,
                    "title": row["title"].strip(),
                    "document_type": row["document_type"].strip(),
                    "category": (
                        (row.get("category") or "").strip() or None
                    ),
                    "version": row["version"].strip(),
                    "effective_date": row["effective_date"].strip(),
                    "access_label": row["access_label"].strip(),
                    "checksum": checksum,
                    "status": row["status"].strip(),
                    "relative_path": relative_path,
                    "pre_chunks": pre_chunks,
                }
            )

        return {
            "accepted": accepted_documents,
            "normalised_documents": normalised_documents,
            "rejected": rejected,
            "warnings": warnings,
        }
    
    def _normalise_whitespace(self, text: str) -> str:
        return " ".join(text.split())
    
    def _is_heading(self, paragraph) -> bool:
        style_name = paragraph.style.name or ""

        return style_name.lower().startswith("heading")
    
    def _extract_docx_sections(self, file_path: Path):
        document = Document(file_path)

        sections = []
        current_title = "Document Introduction"
        current_paragraphs = []
        sequence = 1

        for paragraph in document.paragraphs:
            text = self._normalise_whitespace(paragraph.text)

            if not text:
                continue
            
            if self._is_heading(paragraph):
                if current_paragraphs:
                    sections.append(
                        {
                            "section_title": current_title,
                            "sequence": sequence,
                            "text": "\n".join(current_paragraphs),
                        }
                    )

                    sequence += 1
                    current_paragraphs = []
                
                current_title = text
            else:
                current_paragraphs.append(text)

        #Save section after loop finishes
        if current_paragraphs:
            sections.append(
                {
                    "section_title": current_title,
                    "sequence": sequence,
                    "text": "\n".join(current_paragraphs),
                }
            )

        return sections

    def write_normalised_documents(
        self,
        documents: list[dict],
        output_path: Path,
    ) -> None:
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with output_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            for document in documents:
                file.write(
                    json.dumps(
                        document,
                        ensure_ascii=False,
                        sort_keys=True,
                    )
                    + "\n"
                )

    def _calculate_checksum(self, file_path: Path) -> str:
        sha256 = hashlib.sha256()

        with file_path.open("rb") as file:
            for block in iter(lambda: file.read(8192), b""):
                sha256.update(block)

        return sha256.hexdigest()

    def write_run_log(
        self,
        result: dict,
        output_path: Path,
    ) -> None:
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        accepted_files = [
            {
                "source_id": document["source_id"],
                "file": document["relative_path"],
                "status": document["status"],
            }
            for document in result["normalised_documents"]
        ]

        run_log = {
            "run_time": datetime.now(
                timezone.utc
            ).isoformat(),
            "accepted_count": len(accepted_files),
            "rejected_count": len(result["rejected"]),
            "warning_count": len(result["warnings"]),
            "accepted_files": accepted_files,
            "rejected_files": result["rejected"],
            "warnings": result["warnings"],
        }

        with output_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                run_log,
                file,
                ensure_ascii = False,
                indent = 2,
                sort_keys = True,
            )

def main():
    project_root = Path(__file__).resolve().parents[2]

    supporting_documents_dir = (
        project_root / "Supporting Documents"
        )

    manifest_path = (
        supporting_documents_dir
        / "05_Manifests_and_Guides"
        / "knowledge_base_manifest.csv"
    )

    output_path = (
        project_root
        / "data"
        / "processed"
        / "documents.jsonl"
    )

    run_log_output_path = (
        project_root
        / "ingestion_run_log.json"
    )

    service = IngestionService(
        supporting_documents_dir,
        manifest_path,
    )

    result = service.run()

    service.write_normalised_documents(
        result["normalised_documents"],
        output_path,
    )

    service.write_run_log(
        result,
        run_log_output_path,
    )

    print("Ingestion completed.")
    print(
        f"Accepted: "
        f"{len(result['normalised_documents'])}"
    )
    print(
        f"Rejected: "
        f"{len(result['rejected'])}"
    )
    print(
        f"Warnings: "
        f"{len(result['warnings'])}"
    )
    print(
        f"Run log: {run_log_output_path}"
    )

if __name__ == "__main__":
    main()
