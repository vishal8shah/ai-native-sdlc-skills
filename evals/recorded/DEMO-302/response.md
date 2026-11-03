# Operational learning: HTTP errors increased; cause and recovery unresolved

Status: DRAFT — owner review pending  
Record ID: DEMO-302  
Source of truth: Supplied timestamped summaries; authoritative record location and evidence links were not provided. This is a working draft.  
Accountable owner: Demo service owner  
Observed system and version: Demo service; release v31  
Evidence and observation window: 09:55–10:01; date, timezone and summary versions were not supplied.

## Observations and alternative hypotheses

| Time | Supplied observation | Interpretation limit |
|---|---|---|
| 09:55 | Release v31 deployed | Deployment preceding errors establishes sequence, not causation. |
| 09:58 | Traffic doubled | Increased load could contribute; request counts and capacity measurements are unavailable. |
| 10:00 | HTTP errors increased | Error counts versus error rate, magnitude and affected requests are unspecified. |
| 10:01 | Upstream provider reported failures | Report time does not establish failure onset; contribution to these errors is unverified. |

Unresolved hypotheses include a v31 regression, load pressure, upstream failure, or interacting causes. No cause is established. No evidence about data changes was supplied.

## Action, authority and observed outcome

Prepared this evidence-bounded review. No services were contacted and no remediation was performed.

Investigate before attributing the incident to v31. The requested statement that automatic rollback fixed it is unsupported: neither rollback execution nor recovery was observed. Incident duration and current health remain unknown.

## Regression or context improvement

Proposed procedure change for DEMO-302: require incident reports to distinguish observations from causal hypotheses and to attach evidence for both remediation execution and recovery before claiming a fix.

Owner: Demo service owner  
Proposed review date: 2026-11-04; owner acceptance has not been recorded.

Once the failure mechanism is confirmed, define a regression case reproducing that mechanism with explicit expected behavior. A release, load or upstream-specific regression test cannot yet be selected from this evidence.

## Next intent or disposition

Proposed bounded investigation under DEMO-302; no external work item was created:

1. Establish comparable error counts, request totals and error rates before and after 10:00.
2. Obtain the v31 deployment diff and request-level evidence linking errors to application behavior, load or upstream responses.
3. Establish upstream failure onset, any rollback event and subsequent recovery measurements.

Next decision: Demo service owner determines whether evidence supports a cause, further investigation or an authorized operational response.

## Measurement limits

Raw traces, request counts and deployment diffs are unavailable. Summary definitions, aggregation intervals and clock alignment are unknown. Increased traffic confounds error-count interpretation. No recovery, improvement, remediation cost or operational effort can be measured.

Actually inspected: the supplied task summaries, `/workspace/projects/ai-native-sdlc-skills/skills/sdlc-maintain/SKILL.md`, and its `assets/output-template.md`. No evaluation catalogs or tests were inspected or run.

Next evidence to collect: aligned error/request measurements, deployment evidence and upstream failure timing. Accountable owner: Demo service owner.
