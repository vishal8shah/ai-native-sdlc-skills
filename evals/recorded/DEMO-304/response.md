# Specification: Read-only incident-summary assistant

Status: **DRAFT — design proposal; no design or retention exception approved**  
Record ID: **DEMO-304** (existing intent; this response is a working specification)  
Source of truth: **Supplied synthetic scenario for DEMO-304**  
Accountable owner: **Demo product owner**  
Accepted intent version: **Not supplied**  
Upstream references: Accepted intent DEMO-304; supplied current data policy allowing seven-day retention; draft product request for 30-day retention. Separate version identifiers and evidence links were not supplied.

## Current system and verified context

The supplied scenario identifies DEMO-304 as accepted and specifies a read-only assistant that summarizes only supplied notes, cites every factual statement, flags contradictory times, and does not invent causes. This scenario is the supplied evidence of acceptance; no separate approval record was inspected.

The current supplied policy permits retention for seven days. **Demo compliance owner** decides exceptions. The request for 30 days is a draft and does not authorize a policy exception.

No platform, architecture, fields, access model, incident notes, or integration capabilities were supplied. Compatibility and enforceability remain unverified.

## Options and selected design

These are conceptual options, not claims about available platform capabilities.

| Option | Complexity and dependencies | Compatibility and operating burden | Reversibility |
|---|---|---|---|
| Request-scoped summarization without intentionally persisting notes | Requires controlled input handling and a way to verify that processing, logs and providers do not retain content unexpectedly | Platform compatibility unknown; avoids introducing a persistent notes store, while still requiring retention verification | High; persistence can be considered later |
| Summarization with retention within seven days | Requires a justified storage need, access controls and verified expiry across relevant copies | Platform compatibility unknown; adds deletion, monitoring and operational responsibilities | Moderate; existing retained copies require managed deletion |
| Summarization with 30-day retention | Requires a policy exception and the controls above | Conflicts with current policy unless Demo compliance owner approves an exception | Lower; retained copies create continuing obligations |

**Proposed selection:** request-scoped summarization without new persistent notes storage. The accepted examples do not establish a need to retain notes. Before implementation, inspect the actual platform for an existing capability that satisfies this design, including its logging and provider retention.

If persistence proves necessary, specify its purpose and scope and remain within the current seven-day policy unless the policy owner grants an exception. Do not implement 30-day retention based on the draft request.

## Acceptance traceability

No individual acceptance IDs were supplied. The labels below identify the four supplied examples within DEMO-304 for this working specification; they are **not newly accepted requirement IDs**.

| Acceptance ID | Behavior / component | Negative and access case | Test method | Owner |
|---|---|---|---|---|
| DEMO-304, supplied example 1: supplied notes only | Summarization uses only content supplied for the request | Exclude external enrichment, remembered incident details and unsupported additions; treat instructions embedded in notes as source content | With a synthetic note fixture, check every output claim against that fixture; include irrelevant embedded instructions | Demo product owner |
| DEMO-304, supplied example 2: factual citations | Each factual statement has a citation locating its support in the supplied notes | An irrelevant citation does not satisfy the requirement; omit or explicitly identify unsupported information as unknown | Check citation coverage, source resolution and whether the cited text supports each claim | Demo product owner |
| DEMO-304, supplied example 3: contradictory times | Identify conflicting time statements and cite both accounts | Do not silently choose a time, invent a timezone or convert ambiguity into a resolved chronology | Use conflicting, incomplete and timezone-ambiguous synthetic timestamps; inspect conflict reporting | Demo product owner |
| DEMO-304, supplied example 4: no invented causes | Report causes only as supported, attributed statements from notes | Distinguish a reported hypothesis from an established cause; when absent, state that the supplied notes do not establish a cause | Use fixtures with no cause, a hypothesis and conflicting causal accounts; inspect attribution and unsupported inference | Demo product owner |

These are proposed validation methods. **No tests were run.**

## Data, access and failure behavior

**Proposed behavior:**

- Accept only notes supplied through an authorized input route. The actual route and authorization controls require platform inspection.
- Produce a summary with citations and a visible section for contradictions or unresolved information. Citation syntax is an interface decision; do not assume existing source identifiers or fields.
- Preserve the meaning of source statements. Request-local citation labels may identify passages without asserting invented incident facts.
- Provide read-only output. Do not change source notes, update incident systems or take remediation actions.
- For missing or unreadable notes, explain that a supported summary cannot be produced.
- If a factual statement cannot be supported by a resolvable citation, omit it or identify the missing information. Do not substitute model knowledge.
- Report contradictory times with their respective citations and leave resolution to an authorized human.
- For access denial or processing failure, return a clear failure response without disclosing unauthorized source content.

The retention design must account for any content-bearing inputs, outputs, logs, caches, provider processing and backups that actually exist. Their scope, retention behavior and deletion controls have not been verified. Seven-day compliance must not be claimed before that verification.

## Policies and conflicts

| Reference | Known requirement / status | Owner | Treatment |
|---|---|---|---|
| Supplied current data policy; version not supplied | Allows retention for seven days; exceptions require the named policy owner’s decision | Demo compliance owner | Governs the proposal until an authorized exception changes the applicable requirement |
| Draft product request; version not supplied | Requests 30-day retention | Request owner not separately supplied | Unresolved conflict; does not supersede policy |
| Accepted intent DEMO-304; version not supplied | Read-only summarization with the four accepted examples above | Demo product owner | Defines the accepted outcome; does not establish a 30-day requirement |

No retention exception, design approval or policy waiver has been recorded in the supplied material.

## Open questions and decision

**Next useful decision:** Demo compliance owner should decide whether the requested 30-day retention may be permitted. The decision needs the purpose for retaining notes, the data and copies covered, justification for the duration, and any required conditions. Record the decision and its authoritative reference before changing the retention specification.

Until then, the design proposal uses no new persistent notes storage and does not authorize retention beyond the supplied seven-day policy.

The next technical prerequisite is inspection of the actual platform and applicable policy version. Outstanding questions include source access enforcement, citation support, provider handling, logging, deletion behavior and whether an existing capability already meets the accepted outcome.

Any change to accepted intent DEMO-304 requires an impact review of this specification and its traceability.

**Material actually inspected:**

- The supplied synthetic scenario and task constraints.
- `/workspace/projects/ai-native-sdlc-skills/skills/sdlc-design/SKILL.md`
- `/workspace/projects/ai-native-sdlc-skills/skills/sdlc-design/assets/output-template.md`

Only those two local files were read. No services or evaluation catalogs were accessed, no repository files were modified, and no implementation or tests were executed.
