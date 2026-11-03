# From draft to a reviewable record

This walkthrough uses a synthetic request and a local working copy. It does not create an organizational approval. Keep your existing work/change system authoritative according to your team's rules.

For a complete packet you can generate and deliberately break, start with [the worked example](../examples/worked-change/README.md). It runs real local tests while marking all owner decisions as simulated. This walkthrough shows how to manage the record lifecycle yourself.

## 1. Initialize a new run

From the cloned repository:

```shell
python scripts/sdlc.py init-run --output ../delivery-demo --title "Request validation" --record-id DEMO-001 --owner "Pilot owner" --profile servicenow --synthetic
```

The new folder contains six draft documents and `run.json`. Existing output folders are refused. The metadata records `record_id`, `owner`, `system_of_record`, synthetic mode and the six stages. The template still requires actual content. For actual work, omit `--synthetic` and use real identities/records; that label alone does not authenticate anything.

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

In `run.json`, update only `stages.plan.status` to `ready_for_review`. Evidence can include plain external reference strings and typed local files. For the synthetic example, an honest plain reference is `synthetic-fixture:DEMO-001`:

```json
{
  "status": "ready_for_review",
  "evidence": ["synthetic-fixture:DEMO-001"],
  "decision": null
}
```

This is a fragment to edit within `stages.plan`; do not replace the entire manifest. Preserve its artifact and other fields. The string is recorded but not verified. To register actual local bytes, copy the supplied synthetic request into the run:

```shell
python -c "from pathlib import Path; import shutil; shutil.copyfile('examples/request-validation/request.md', Path('../delivery-demo/request.md'))"
python scripts/sdlc.py attach-evidence ../delivery-demo --stage plan --file request.md
```

`attach-evidence` adds a `local_file` object with a SHA-256 digest. Its path is relative to the run folder. The checker now detects changes or deletion of this file; it still cannot verify that the expected behavior is right. Then run:

```shell
python scripts/sdlc.py snapshot ../delivery-demo --stage plan
python scripts/sdlc.py check-run ../delivery-demo --through plan
```

A pass establishes only the checked local structure and current snapshots. Inspect the counts and warnings: the local request is hash-checked; the plain synthetic reference remains unverified. The skill still needs an appropriate reviewer to judge whether the outcome and acceptance examples are right.

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

This walkthrough is in synthetic mode. If you continue for practice without a real external decision, explicitly use a `SIMULATED` owner and a `synthetic://` reference, as the worked example does. That can demonstrate the local record shape; it is never a genuine acceptance. Start a separate working run for real work and real decisions.

## 5. Continue to design

Supply the accepted intent, its version and actual platform context to `sdlc-design`. Complete `spec.md`, preserve the acceptance IDs and record the source versions. The design snapshot captures the current intent digest. Follow the same review/recording pattern for the next stage.

A later accepted stage requires all its earlier stages to be accepted in the local manifest. This is this starter's linear record convention; it does not replace your organization's actual workflow.

## 6. Reopen when the evidence changes

Editing an upstream document invalidates the snapshots that reference its old bytes. Changing or deleting a registered local file also fails its evidence check. Reopen the affected records, inspect the impact, run the applicable checks, reattach changed evidence and update downstream output. Gather new decisions where your process requires them. Snapshot only after that review. The script refuses to re-snapshot or attach files to a record whose manifest still says `accepted`.

A new Markdown snapshot does not silently refresh an attached file's digest. A plain external link is not queried. Review every stage that relies on changed source/results even if the local structural check does not require further edits.

Hash freshness says that bytes match a recorded snapshot. It does not say the content is complete in meaning, correct or authorized.
