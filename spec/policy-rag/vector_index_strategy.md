# Vector Index Strategy

## 1. Vector Index

The vector index supports semantic retrieval of policy content.

The purpose of the vector index is to find chunks whose content is relevant to the user's question, even when the wording of the question does not exactly match the document.

Each indexed chunk must remain linked to its metadata so that retrieved content can be traced back to its source document and section.

## 2. Text Index

The text index supports keyword and exact-text retrieval.

Text search should support fields such as:

- title
- heading_section
- chunk content

This allows retrieval where exact terminology, policy names or section names are important.

## 3. Metadata Index

Metadata fields must be indexed where required for retrieval filtering.

Required filterable fields include:

- source_id
- document_type
- version
- effective_date
- access_label
- status

The field names must remain consistent with the metadata model.

## 4. Filtering Rules

### Document Type

Retrieval must support filtering using:

'document_type'

The same 'document_type' field defined in the document metadata model must be used by the retrieval contract.

### Effective Version

Retrieval must support selecting the applicable document version using:

- 'version'
- 'effective_date'
- 'status'

Superseded documents must be identifiable through 'status' so that retrieval can apply the approved effective-version rules.

### Access Control

Retrieval must support filtering using:

'access_label'

Only content that the requesting user is authorised to access may be returned.

The access labels currently present in the knowledge-base inventory are:

- Internal
- Restricted

## 5. Citation Support

Every retrieved chunk must retain the metadata required to trace it back to its source.

At minimum, retrieval must preserve:

- chunk_id
- source_id
- heading_section
- sequence
- access_label

The source_id must map to the corresponding document metadata so that citation information such as the document title, version and effective data can be obtained.

This provides the traceability required to produce citatations for generated answers.

## 6. Index Consistency

The index strategy must use the same metadata field names defined in document_metadata_model.md.

Fields must not be renamed between the metadata model and retrieval contract.

This ensures that document type, effective version and access-control filters can be applied consistently.