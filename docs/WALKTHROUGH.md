# From draft to a reviewable record

This walkthrough uses a synthetic request and a local working copy. It does not create an organizational approval. Keep your existing work/change system authoritative according to your team's rules.

## 1. Initialize a new run

From the cloned repository:

```shell
python scripts/sdlc.py init-run --output ../delivery-demo --title "Request validation" --record-id DEMO-001 --owner "Pilot owner" --profile servicenow
```

The new folder contains six draft documents and `run.json`. Existing output folders are refused. The metadata records `record_id`, `owner`, `system_of_record` and the six stages. The template still requires actual content.

## 2. Complete the intent

Open `../delivery-demo/intent.md`. Replace required markers with the actual problem, evidence, expected behavior, exclusions, unknowns and next decision. Supply all template sections with nonempty content. Keep these fields consistent with `run.json`:

```text
Status: READY_FOR_REVIEW
Record ID: DEMO-001
Source of truth: Existing work item and change records
Accountable owner: Pilot owner
```

The [synthetic ready-for-review intent](../examples/request-validation/intent-ready.md) shows the complete document shape. Copy it into the run only for this example, not as evidence of a real change.

## 3. Record readiness and snapshot the bytes

In `run.json`, update only `stages.plan.status` to `ready_for_review` and supply `stages.plan.evidence` as a list of actual evidence references. For the synthetic example, an honest reference is `synthetic-fixture:DEMO-001`.

```json
{
  "status": "ready_for_review",
  "evidence": ["synthetic-fixture:DEMO-001"],
  "decision": null
}
```

This is a fragment to edit within `stages.plan`; do not replace the entire manifest. Preserve its artifact and other fields. Then run:

```shell
python scripts/sdlc.py snapshot ../delivery-demo --stage plan
python scripts/sdlc.py check-run ../delivery-demo --through plan
```

A pass establishes only the checked local structure and current snapshots. The skill still needs a human to judge whether the outcome and acceptance examples are right.

## 4. Record an acceptance that actually happened

After the accountable person makes the required decision in the authoritative system:

1. Change the intent's status to `ACCEPTED`.
2. Keep the manifest status `ready_for_review` while taking a new snapshot; the status line changed the bytes.
3. Run `snapshot` again. It clears any old decision on this stage.
4. Change the manifest status to `accepted` and populate `decision` from the real external record.

The decision object has this shape. Values below are placeholders, not approval evidence:

```json
{
  "owner": "<actual decision maker>",
  "reference": "<actual external decision record>",
  "timestamp": "<actual ISO 8601 timestamp with timezone>"
}
```

Then check the accepted local record:

```shell
python scripts/sdlc.py check-run ../delivery-demo --through plan --require-accepted
```

The checker validates these supplied fields; it cannot authenticate them or contact the approval system. Never use the local status as the sole release gate. Copying a placeholder into a field does not make it evidence.

## 5. Continue to design

Supply the accepted intent, its version and actual platform context to `sdlc-design`. Complete `spec.md`, preserve the acceptance IDs and record the source versions. The design snapshot captures the current intent digest. Follow the same review/recording pattern for the next stage.

A later accepted stage requires all its earlier stages to be accepted in the local manifest. This is this starter's linear record convention; it does not replace your organization's actual workflow.

## 6. Reopen when the evidence changes

Editing an upstream document invalidates the snapshots that reference its old bytes. Reopen the affected records, inspect the impact, update the downstream output and gather the new decisions that your process requires. Snapshot only after that review. The script refuses to re-snapshot a record whose manifest still says `accepted`.

Hash freshness says that bytes match a recorded snapshot. It does not say the content is complete in meaning, correct or authorized.
