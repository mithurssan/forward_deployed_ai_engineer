# Metadata Model

## Document Fields

|Field|Description|
|---|---|
|source_id|stable identifier for the source document.
|document_type|document classification used by the retrieval filter; use this exact field name in the retrieval contract.
|category|subject or business category, distinct from document type.
|version|document version
|effective_date| date document becomes applicable
|access_label| access-control value used by retrieval filtering.
|checksum| content-integrity value for the source document.
|status| Indicates whether the document is approved or superseded.
|relative_path| Location of the source document within the knowledge base

## Validation Rules

### source_id
- Required.
- Must not be empty.
- Must uniquely identify one source document.
- Must remain stable for the source document.

### title
- Required.
- Must not be empty.

### document_type
- Required.
- Must use an approved document type.
- Values present in the current inventory are:
    - Policy
    - Guide
    - FAQ
    - Casebook
    - Bulletin

### category
- Required.
- Must represent the subject or business category of the document.
- Must remain separate from 'document_type'.
- Category values must be confirmed because they are not provided in the current manifest.

### version
- Required.
- Must identify the version of the source document.

### effective_date
- Required.
- Must contain a valid date.
- Stored using a consistent date format.

### access_label
- Required.
- Must contain an approved access-control value.
- Values present in the current inventory are:
    - Internal
    - Restricted

### checksum
- Required.
- Must contain a content-integrity value for the source document.
- A change to document content must result in a different checksum.

### status
- Required.
- Values present in the current inventory are:
    - Approved
    - Superseded

### relative_path
- Required.
- Must identify the location of the source document in the knowledge base.

## Consistency Rules

- Each 'source_id' must uniquely identify its source.
- Metadata must correspond to the correct source document.
- 'document_type' must use the same field name throughout the metadata and retrieval contracts.
- 'access_label' must use the same field name throughout the metadata and retrieval contracts.
- Retrieval must take document version and 'effective_date' into account when selecting the effective version.
- Superseded documents must be identifiable through 'status'.
- 'checksum' must correspond to the content of the associated source document.

## Chunk Fields

| Field | Description |
|---|---|
| chunk_id | Unique identifier for the chunk
| source_id | Identifier of the source document the chunk came from.
| heading_section | Heading or section of the source document containing the chunk.
| sequence | Position of the chunk within the source document.
| access_label | Access-control value applied to the chunk during retrieval.

## Chunk Validation Rules

### chunk_id
- Required.
- Must not be empty.
- Must uniquely identify one chunk.

### source_id
- Required.
- Must match a valid 'source_id' in the document metadata.
- Every chunk must trace back to one source document.

### heading_section
- Required.
- Must identify the heading or section of the source document from which the chunk was created.

### sequence
- Required.
- Must identify the position of the chunk within its source document.
- Must use a consistent sequence format.

### access_label
- Required.
- Must match the access requirements associated with the source.
- Must use an approved access-label value.
- Values currently present in the source inventory are:
    - Internal
    - Restricted


## Access Filtering

Retrieval must support filtering using the metadata fields:

- 'document_type'
- 'version' and 'effective_date' for effective-version selection
- 'access_label'

The same field names must be used in the document metadata, chunk metadata where applicable, and retrieval contract.

Content that does not meet the user's permitted 'access_label' must not be returned for use in an answer.

Superseded versions must be identifiable so that retrieval can apply the agreed effective-version rules.

## Citation Mapping

Every retrieved chunk must be traceable to its original source document and section.

The mapping is:

'chunk_id' -> 'source_id' -> source document

The 'heading_section' identifies where within the source document the retrieved content originated.

This mapping allows a generated answer to identify the supporting source document and section when producing a citation.

A chunk must not be used as cited evidence if it cannot be traced back to its source document and section.