# Local helper reference

Python 3.10+, standard library only. No AI API or external service calls. Paths below are relative to the cloned repository unless stated otherwise.

## init-run

`python scripts/sdlc.py init-run --output PATH --title TITLE --record-id ID --owner OWNER [--system-of-record TEXT] [--profile generic|servicenow] [--synthetic]`

Create a new folder with six DRAFT Markdown templates and `run.json`. Refuse an existing output path. This does not create a real work item. Identity values must be nonblank single-line strings; edge whitespace is trimmed and control characters are rejected. Supply the matching values when filling the templates.

`--synthetic` records `record_mode: synthetic` and makes checks warn that acceptance metadata is simulated. Omit it for working records. A working-mode label does not authenticate the record either. Existing manifests without this field are treated as working records.

## attach-evidence

`python scripts/sdlc.py attach-evidence RUN --stage STAGE --file RELATIVE_FILE`

Register an existing file **inside the run folder** by relative path and SHA-256. For example, after putting your actual source and result files in that folder:

```shell
python scripts/sdlc.py attach-evidence ../delivery-demo --stage test --file implementation/request_validation.py
python scripts/sdlc.py attach-evidence ../delivery-demo --stage test --file evidence/unittest.txt
```

The command adds an object of this shape to the stage's evidence list:

```json
{
  "kind": "local_file",
  "path": "implementation/request_validation.py",
  "sha256": "<64 lowercase hexadecimal characters computed from the file>"
}
```

Reattaching the same path replaces its digest after your review. It clears that stage's prior decision. Accepted stages must first be reopened. Absolute/escaping paths, symlink files or ancestors, missing files and mutable `run.json` metadata are refused.

Plain nonblank reference strings remain supported for external records or historical references. They are **not fetched, authenticated or checked for freshness**. A filename supplied as a plain string is also unverified; use the typed attachment command for local byte verification.

## snapshot

`python scripts/sdlc.py snapshot RUN --stage plan|design|build|test|deploy|maintain`

Store SHA-256 digests of the current stage's Markdown artifact and all earlier stage artifacts. Do not change status, accept work or authenticate decisions. Clear any previous decision on the snapshotted stage; accepted records must first be reopened as draft.

Snapshotting does **not** update registered evidence-file digests. If source or results changed, inspect the impact and reattach the appropriate files separately. A new digest records new bytes; it never proves that a new test was run or a new decision occurred.

## check-run

`python scripts/sdlc.py check-run RUN [--through STAGE] [--require-accepted]`

Validate metadata, confined artifact paths and statuses. For ready-for-review or accepted stages, check:

- Matching identity/status fields and nonempty expected stage sections; no remaining required markers.
- Current artifact and upstream Markdown snapshots; all earlier stages locally accepted.
- At least one evidence reference. Typed local files must exist and match their registered digests.
- Accepted stages have a supplied decision owner, reference and timezone-aware timestamp.

The supported Markdown format uses plain identity fields and `##` section headings. Content hidden in comments cannot satisfy those checks. Metadata or headings inside fenced code do not count as record structure; actual nonempty code can count as a section body. Inline code is supported. Raw HTML outside code is unsupported. This is a constrained structural parser, not full CommonMark rendering or a semantic/security assessment.

The JSON result separates these counts:

|Field|Meaning|
|---|---|
|`local_files_verified`|Unique local file paths successfully checked|
|`local_file_references_verified`|Successfully checked attachments across stages; one file can be referenced several times|
|`external_references_unverified`|Plain reference strings recorded without contacting their destination|

Counts cover review-ready/accepted stages through the requested stage. Draft/blocked stage evidence is not assessed. A valid draft can still contain unfinished work; use `--require-accepted` to reject draft, blocked or review-pending stages. Check `warnings` and `record_mode` alongside `valid`.

A pass verifies local structure and recorded bytes. It does not query approval systems, authenticate identities, prove application behavior or authorize deployment. A person able to alter the files and manifests can replace the hashes too. Never use this helper as the sole production security gate.

Editing an upstream artifact after a downstream snapshot makes the check fail. Changed/missing registered attachments also fail. Review the downstream impact and update applicable evidence and decisions. Unknown stages, malformed JSON, unsafe paths and invalid metadata return a nonzero exit status.

## measure

`python scripts/sdlc.py measure CSV --hour-rate AUD [--setup-hours HOURS] [--ai-cost AUD]`

Require nonempty complete paired observations. Elapsed hours must be positive. Staff minutes, rework and defect counts must be nonnegative; counts must be whole numbers. Reject blanks, non-finite values and incomplete rows. Compute the median of each pair's elapsed-time reduction, summed staff effort saved, rework/defect differences and net capacity value after setup and AI costs. Keep negative savings visible. Five pairs are exploratory, not causal proof; the helper never produces a statistical confidence claim or release decision.

## install

`python scripts/install.py --client claude|codex --project PATH [--only SKILL] [--apply]`

Default to a dry run. On apply, copy selected skills to the client's local project directory and refuse any existing skill destination. Do not install credentials, permissions, hooks or packages. The default includes a self-contained router plus six standalone stage skills. Review updates locally rather than overwriting installed skills without inspection.

The installed router carries `sdlc.py`, `install.py`, stage resources and this reference. Repository-only validation, demo, trial and worked-example tools are intentionally omitted.

## Repository experiments

|Command|Purpose|
|---|---|
|`python scripts/demo.py [--json]`|Show wrong expected behavior, correction and stale/missing evidence detection|
|`python scripts/worked_example.py [--output NEW_DIRECTORY]`|Run actual local unit tests and generate a complete synthetic six-stage packet; no output argument uses a temporary folder and cleans it up|
|`python scripts/trials.py verify [--require-current]`|Check preserved task/response bytes, provenance fields and inspected-source hashes; strict mode also requires those sources still match|
|`python scripts/trials.py prompt DEMO-301 --client codex`|Print only the captured task with a client invocation for manual replay; also supports `--client claude`|

For the full lifecycle, use [the repository walkthrough](https://github.com/vishal8shah/ai-native-sdlc-skills/blob/main/docs/WALKTHROUGH.md). For trial limitations and replay instructions, see [the recorded trials](https://github.com/vishal8shah/ai-native-sdlc-skills/blob/main/evals/recorded/README.md).
