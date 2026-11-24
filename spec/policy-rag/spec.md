# Policy RAG Knowledge Service Specification

## 1. Overview
The Policy RAG Knowledge Service provides grounded answers to policy questions related to complaints using approved company policy documents.

The service retrieves relevant policy information, generates an answer based on that information and provides citations showing where exactly the answers came from.

If sufficient evidence cannot be found, the service must not guess and must instead inform the user that there is not enough information to answer the question.

## 2. Scope and Non-Goals

### Scope

The Policy RAG Knowledge Service will:
- Accept complaint-related policy questions from authorised users.
- Search approved policy documents for relevant information.
- Retrieve relevant policy documents for the question.
- Generate answers grounded in the retrieved policy evidence.
- Return relevant source information with citations.
- Respect document access restrictions when retrieving information.
- Abstain when sufficient supporting evidence is not found.

### Non-goals

The Policy RAG Knowledge Service will not:
- Provide legal advice.
- Create or change company policies.
- Use unapproved documents as policy evidence.
- Answer questions using information the user is not permitted to access.
- Guess answers when sufficient policy evidence cannot be found.

## 3. Actors

The users of the service may include:
- Complaint Analysts
- Team Leads
- Support Agents

Users may have different levels of access to policy documents.

## 4. Preconditions

Before the service can answer a question:

- The user must be authorised to use the service.
- Approved policy documents must be available for retrieval.
- The user must have permission to access the retrieved information.
- Required document information must be available for citations.

## 5. Flows

### Successful Answer

1. The user submits a complaint-related policy question.
2. The service searches approved policy documents.
3. Relevant policy information is retrieved.
4. The service generates an answer using the retrieved evidence.
5. The answer is returned with citations.

### Insufficient Evidence

1. The user submits a question.
2. The service searches approved policy documents.
3. Sufficient supporting evidence cannot be found.
4. The service does not generate an unsupported answer.
5. The service informs the user that there is not enough evidence to answer the question.

## 6. Rules

- Answers must be based on approved policy documents.
- Answers must be supported by retrieved evidence.
- Answers must include citations to their supporting evidence.
- Users must only receive information they are authorised to access.
- The service must not invent policy information.
- The service must abstain when supporting evidence is insufficient.

The exact approved documents, required metadata, citation format, access labels, evidence requirements and handling of older documents require clarification.

## 7. Errors

The service must safely handle:

- No relevant policy information being found.
- Insufficient evidence to answer a question.
- Policy documents being unavailable.
- Users not having access to relevant information.
- Invalid requests.
- Internal service failures.

Errors must not cause the service to generate unsupported policy information or expose information the user is not authorised to access.

## 8. Non-Functional Requirements

### Security

The service must repect user permissions and document access restrictions.

### Reliability

The service must fail safely and must not generate unsupported policy answers when required evidence is unavailable.

### Traceability

Answers must be traceable to their supporting policy sources through citations.

### Performance
The service should return answers within an acceptable response time. The measurable response-time requirement needs to be confirmed.

## 9. API Expectations

The API must accept a policy question and return either:

- A grounded answer with supporting citations, or
- A safe abstention or error response when an answer cannot be supported.

The API must support the information required to identify the answer, citations and relevant source information.

## 10. Acceptance Criteria

### AC1 - Retrieval

- The service must retrieve information only from approved policy sources.
- Retrieved information must respect the user's access permissions.
- Information the user is not permitted to access must not be used in the answer.

### AC2 - Citations

- Every supported policy answer must include at least one citation.
- Citations must identify the policy document used to support the answer.

### AC3 - Metadata

- Retrieved evidence must include the mandatory source metadata.
- The exact fields will follow the agreed metadata requirements

### AC4 - Abstention

- If sufficient supporting evidence cannot be found, the service must abstain.
- The service must not invent or assume policy information
- The abstention response must clearly state that sufficient evidence could not be found in the approved policy sources.

### AC5 - Unsupported Questions

- Questions that cannot be answered from approved policy sources must not receive a generated policy answer.
- The service must return a safe abstention response instead.

### AC6 - Access Control

- The service must only use evidence the requesting user is authorised to access.
- Restricted information must not appear in the generated answer or citations.

### AC7 - Retrieval or Source Failure

- If required policy information cannot be retrieved, the service must not generate an unsupported answer.
- The service must return a safe error or abstention response.

