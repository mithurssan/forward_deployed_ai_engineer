# Policy RAG Clarification Log

## CL-01 - Approved Documents

**Question:** Which documents are approved?

**Status:** Open

**Decision:** Awaiting business decision.

**Impact:** The service cannot finalise which document sources are permitted for retrieval until this is confirmed.

## CL-02 - Mandatory Metadata

**Question:** Which metadata is mandatory?

**Status:** Open

**Decision:** Awaiting business decision.

**Impact:** The required metadata returned with retrieved policy information cannot be finalised.

## CL-03 - Valid Citation

**Question:** What forms a valid citation?

**Status:** Open

**Decision:** Awaiting business decision.

**Impact:** The exact citation fields required in an answer cannot be finalised.

## CL-04 - Insufficient Evidence

**Question:** What should happen when evidence is insufficient?

**Status:** Resolved

**Decision:** The service must safely abstain rather than generate an unsupported answer. The response should explain to the user that sufficient information could not be found in the approved policy documents.

**Impact:** The specification must require safe abstention when an answer cannot be supported by retrieved evidence.

## CL-05 - Access Labels

**Question:** Which access labels may each role retrieve?

**Status:** Open

**Decision:** Awaiting business decision.

**Impact:** Role-based retrieval boundaries cannot be finalised until the permitted access labels are defined.

## CL-06 - Superseded Versions

**Question:** How are superseded versions handled?

**Status:** Open

**Decision:** Awaiting business decision.

**Impact:** The retrieval rules for old and replaced policy versions cannot be finalised.