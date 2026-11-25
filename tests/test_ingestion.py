import csv, json
from pathlib import Path

import pytest
from docx import Document

from src.rag.ingestion_service import IngestionService

MANIFEST_FIELDS = [
    "source_id",
    "title",
    "document_type",
    "version",
    "effective_date",
    "access_label",
    "status",
    "relative_path",
]

def create_docx(
    file_path: Path,
    heading: str = "complaints",
    text: str = "Complaints must be investigated."
) -> None:
    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    document = Document()
    document.add_heading(heading, level=1)
    document.add_paragraph(text)
    document.save(file_path)

def create_manifest(
    manifest_path: Path,
    rows: list[dict],
) -> None:
    manifest_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with manifest_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=MANIFEST_FIELDS,
        )

        writer.writeheader()
        writer.writerows(rows)

def valid_manifest_row(
    relative_path: str = "policies/KB-001.docx",
) -> dict:
    return {
        "source_id": "KB-001",
        "title": "Complaint Management Policy",
        "document_type": "Policy",
        "version": "3",
        "effective_date": "2026-01-01",
        "access_label": "Internal",
        "status": "Approved",
        "relative_path": relative_path,
    }

def test_valid_manifest_is_accepted(
    tmp_path: Path,
):
    source_dir = tmp_path / "Supporting Documents"
    manifest_path = source_dir / "manifest.csv"
    relative_path = "policies/KB-001.docx"

    create_docx(source_dir / relative_path)

    create_manifest(
        manifest_path,
        [valid_manifest_row(relative_path=relative_path)]
    )

    service = IngestionService(
        source_dir,
        manifest_path,
    )

    result = service.run()

    assert len(result["accepted"]) == 1
    assert len(result["normalised_documents"]) == 1
    assert result["rejected"] == []


def test_unlisted_file_is_rejected(
    tmp_path: Path,
) -> None:
    source_dir = tmp_path / "Supporting Documents"
    manifest_path = source_dir / "manifest.csv"

    listed_path = "policies/KB-001.docx"
    unlisted_path = "policies/unknown_policy.docx"

    create_docx(source_dir / listed_path)
    create_docx(source_dir / unlisted_path)

    create_manifest(
        manifest_path,
        [valid_manifest_row(relative_path=listed_path)],
    )

    service = IngestionService(
        source_dir,
        manifest_path,
    )

    result = service.run()

    assert any(
        item["reason"] == "unlisted_file"
        and item["file"] == unlisted_path
        for item in result["rejected"]
    )

def test_duplicate_source_id_is_rejected(
    tmp_path: Path,
) -> None:
    source_dir = tmp_path / "Supporting Documents"
    manifest_path = source_dir / "manifest.csv"

    first_path = "policies/KB-001.docx"
    second_path = "policies/KB-002.docx"

    create_docx(source_dir / first_path)
    create_docx(source_dir / second_path)

    first_row = valid_manifest_row(first_path)
    second_row = valid_manifest_row(second_path)

    create_manifest(
        manifest_path,
        [first_row, second_row],
    )

    service = IngestionService(
        source_dir,
        manifest_path,
    )

    result = service.run()

    duplicate_rejections = [
        item
        for item in result["rejected"]
        if item["reason"] == "duplicate_source_id"
    ]

    assert len(duplicate_rejections) == 2
    assert result["accepted"] == []
    assert result["normalised_documents"] == []

def test_missing_effective_date_is_rejected(
    tmp_path: Path,
) -> None:
    source_dir = tmp_path / "Supporting Documents"
    manifest_path = source_dir / "manifest.csv"
    relative_path = "policies/KB-001.docx"

    create_docx(source_dir / relative_path)

    row = valid_manifest_row(relative_path)
    row["effective_date"] = ""

    create_manifest(
        manifest_path,
        [row],
    )

    service = IngestionService(
        source_dir,
        manifest_path,
    )

    result = service.run()

    assert any(
        item["reason"] == "missing_required_fields"
        and "effective_date" in item["fields"]
        for item in result["rejected"]
    )

    assert result["accepted"] == []
    assert result["normalised_documents"] == []
