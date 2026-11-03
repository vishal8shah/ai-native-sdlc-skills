# Local helper reference

Python 3.10+, standard library only. No AI API or external service calls.

## init-run

`python scripts/sdlc.py init-run --output PATH --title TITLE --record-id ID --owner OWNER [--system-of-record TEXT] [--profile generic|servicenow]`

Create a new folder with six DRAFT Markdown templates and `run.json`. Refuse an existing output path. This does not create a real work item.

## snapshot

`python scripts/sdlc.py snapshot RUN --stage plan|design|build|test|deploy|maintain`

Store SHA-256 digests of the current stage artifact and all earlier stage artifacts. Do not change status, accept work or authenticate decisions. Clear any previous decision on the snapshotted stage; accepted records must first be reopened as draft. Snapshot again only after inspecting changed content; a new snapshot is not a substitute for impact review.

## check-run

`python scripts/sdlc.py check-run RUN [--through STAGE] [--require-accepted]`

Validate metadata, confined artifact paths and statuses. For ready-for-review or accepted records, require completed template placeholders, matching Markdown/manifest statuses, nonempty evidence references and matching snapshots. Require accepted records to contain an externally recorded decision owner, reference and timezone-aware timestamp. Require their earlier stages to be accepted and their digests to match.

`--require-accepted` rejects drafts/blocked/review-pending records through the chosen stage. A pass verifies only the supplied local record and its content lineage. It does not query approval systems, authenticate identities, prove application behavior or authorize deployment. Never use it as the sole production security gate.

Editing an upstream artifact after a downstream snapshot makes the check fail until the downstream impact has been reviewed and new evidence recorded. Unknown stages, malformed JSON, path traversal and invalid metadata return a nonzero exit status.

## measure

`python scripts/sdlc.py measure CSV --hour-rate AUD [--setup-hours HOURS] [--ai-cost AUD]`

Require nonempty complete paired observations. Elapsed hours must be positive. Staff minutes, rework and defect counts must be nonnegative; counts must be whole numbers. Reject blanks, non-finite values and incomplete rows. Compute the median of each pair's elapsed-time reduction, summed staff effort saved, rework/defect differences and net capacity value after setup and AI costs. Keep negative savings visible. Five pairs are exploratory, not causal proof; the helper never produces a statistical confidence claim or release decision.

## install

`python scripts/install.py --client claude|codex --project PATH [--only SKILL] [--apply]`

Default to a dry run. On apply, copy selected skills to the client's local project directory and refuse any existing skill destination. Do not install credentials, permissions, hooks or packages. The default includes a self-contained router plus six standalone stage skills. Re-run locally after reviewing updates rather than overwriting installed skills without review.
