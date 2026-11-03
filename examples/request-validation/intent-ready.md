# Intent: synthetic request-form validation
Status: READY_FOR_REVIEW
Record ID: DEMO-001
Source of truth: Existing work item and change records
Accountable owner: Pilot owner
Source versions: synthetic-fixture:DEMO-001

## Problem and evidence
The synthetic request fixture accepts a whitespace-only justification. This is a demonstration input, not a report of an actual ServiceNow instance.

## Desired outcome
Reject an empty or whitespace-only justification while preserving successful requests with nonblank string values.

## Scope and exclusions
One development-only request item. Exclude production, integrations, approval-policy changes, access changes and bulk updates.

## Acceptance examples
|ID|Input / situation|Expected result|Independent reviewer|
|---|---|---|---|
|AC-01|Empty string|Reject with a useful message|Pilot owner|
|AC-02|Spaces or tabs/newlines|Reject with a useful message|Pilot owner|
|AC-03|Nonblank justification|Preserve the valid path|Pilot owner|
|AC-04|Alternative submission path|Same required behavior|Platform reviewer|

## Constraints and unknowns
The actual platform release, item, variable names, current validation and transport mechanism are unknown. Inspect them before design. Use synthetic data and non-production tests only.

## Decision and next step
No organizational acceptance is recorded. Ask the accountable owner to review the problem, scope and expected results before progressing under the actual project policy.
