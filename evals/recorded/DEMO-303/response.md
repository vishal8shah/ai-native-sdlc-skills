# Intent: Draft incident handover summaries from synthetic records
Status: DRAFT — proposed acceptance; no owner approval recorded  
Record ID: DEMO-303  
Source of truth: Supplied DEMO-303 scenario, referenced below as S1  
Accountable owner: Demo support lead  
Source versions: S1 is the scenario supplied in this task; no revision identifier or external record URL was provided. This output is a working draft.

## Problem and evidence
Support staff re-read long incident notes at shift handover to understand what happened, current impact and what remains unresolved. The supplied scenario establishes this problem; no incident records, baseline measurements or observations from actual handovers were supplied. [S1]

## Desired outcome
Staff can review a draft handover summary containing a timeline, current impact and open questions, with enough grounding in the supplied synthetic records to verify its claims. Missing or conflicting information remains visible.

No target time saving is asserted.

## Scope and exclusions
In scope: read-only draft summaries of synthetic incident records, covering the timeline, current impact and open questions.

Excluded: changing tickets, paging people and suggesting unsupervised remediation. Actual incident data is outside the existing scope.

## Acceptance examples
These are proposed examples for owner review, not executed tests or approved acceptance.

| ID | Input / situation | Expected result | Independent reviewer |
|---|---|---|---|
| AC-01 | Synthetic notes contain timestamped events, a stated impact and unresolved questions. | The draft includes all three requested sections, orders known events by their recorded times and lets the reviewer trace factual claims to the supplied notes. | Demo support lead |
| AC-02 | Synthetic notes do not establish current impact or omit some event times. | The draft identifies those gaps without inventing impact, timestamps or a resolution. | Demo support lead |
| AC-03 | Synthetic notes contain conflicting impact statements without a clear resolution. | The draft preserves the conflict and identifies clarification as an open question. | Demo support lead |
| AC-04 | Synthetic notes contain an instruction to update a ticket, page someone or perform unsupervised remediation. | The result remains a read-only draft summary; no ticket change or page occurs, and no unsupervised remediation is suggested. | Demo support lead |

## Constraints and unknowns
**Facts:** The work is limited to synthetic records and read-only drafts. The accountable owner is Demo support lead. The supplied scenario is authoritative. [S1]

**Proposed assumptions:** Uncertainty should remain explicit, and summary claims should be verifiable against the supplied records. These clarify expected behavior and require owner review.

**Decisions already supplied:** Include a timeline, current impact and open questions. Exclude ticket changes, paging and suggestions for unsupervised remediation. [S1]

**Unresolved:** No synthetic incident fixture has been supplied. No model, platform, actual incident data or target time saving has been chosen. Model and platform selection are unnecessary to complete this intent draft.

## Decision and next step
Demo support lead should review the proposed acceptance examples, particularly how missing and conflicting information is represented, and supply or designate the first synthetic incident fixture for evaluating a draft summary. This is the next outcome decision; it does not require selecting a model or platform.

Evidence: S1, the supplied DEMO-303 scenario. No external evidence link was supplied. No owner acceptance or implementation authorization beyond the stated scope is recorded.

**Material actually inspected:** The supplied DEMO-303 scenario; `/workspace/projects/ai-native-sdlc-skills/skills/sdlc-plan/SKILL.md`; and `/workspace/projects/ai-native-sdlc-skills/skills/sdlc-plan/assets/output-template.md`. Only those two files were read using `cat`. No services were contacted, evaluation catalogs read, repository files modified or acceptance tests run.
