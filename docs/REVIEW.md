# Review: useful evidence before promotion

Date: 03-Nov-2026. Scope: this starter repository, local helper behavior, installation-to-first-use documentation and synthetic examples. This is an authoring review, not an independent security audit or production certification.

## What the first review found

A fresh-context reviewer followed the original README in temporary directories. It reproduced working helper commands and passing baseline tests, then identified five concrete gaps.

|Finding|Change made|Verification|
|---|---|---|
|Example path existed in the clone but not the destination project|Quickstart launches the client in the destination and supplies the full input inline|Documentation walkthrough and review; actual client execution remains unverified|
|Draft-to-accepted transition was underspecified|Add the full record lifecycle, status/snapshot order and decision object|Worked record instructions; six-stage helper regression coverage|
|Validator accepted malformed UI metadata and incomplete evaluation cases|Validate the documented supported schemas and required fields|Negative regression cases for malformed/duplicate metadata, missing prompts/rubrics/inputs and missing catalog|
|Installed router included a validator without its evaluation catalog|Ship only the two runtime helper scripts|Installer regression checks installed contents and runtime resources|
|An accepted document could omit the actual template structure|Require matching identity fields and nonempty stage sections as well as freshness|Minimal-document and identity/section regression checks|

The installer also stages all copies before publication and removes only the new skill directories it created if a later step fails. Regression cases simulate staging and publication failures. The helper still does not protect against an adversary who can alter all local records and tooling.

## v0.2 follow-up review

A fresh-context reviewer re-ran the earlier failures against the revision, followed the walkthrough in temporary Claude/Codex project layouts, and exercised installed runtime commands. The review reported no remaining material first-use failures. It confirmed 44 passing local tests, the documented demo, readiness/recorded-acceptance/staleness/reopening behavior, malformed metadata rejection, and failure cleanup that preserved a pre-existing user skill. No real AI client process, genuine approval or external service was exercised. A minor missing repository link in the installed CLI reference was corrected.

The first expanded GitHub matrix run also completed successfully on Ubuntu/Python 3.10 and 3.13, Windows/Python 3.13 and macOS/Python 3.13. [Inspect that exact run](https://github.com/vishal8shah/ai-native-sdlc-skills/actions/runs/41615301412); the workflow link below shows the current status after later changes.

## v0.3 deeper audit: false passes still existed

The earlier 44 passing tests and first-use review did not establish the absence of bugs. A separate read-only audit reproduced additional cases against the helper and validator. The following changes address the observed failures:

|Finding|Change made|Regression or reproduction|
|---|---|---|
|Frontmatter accepted YAML scalars as descriptions, blank quoted descriptions, and a wrong skill invocation with a matching prefix|Require nonblank quoted string descriptions and an exact invocation boundary|Reject `null`, `false`, numeric and unquoted values; whitespace-only descriptions; suffixed skill names|
|A whole document inside a comment or code fence could satisfy readiness checks|Parse supported visible record structure; ignore commented content and fenced metadata/headings|Commented/fenced complete records fail; genuine fenced section evidence and inline code still work|
|Edge whitespace or control characters could make initialized identities unusable|Normalize edge whitespace and require single-line control-free identity text|Round-trip normalization and control-character rejection|
|Source/results could change while only Markdown snapshots remained current|Add typed local evidence attachments with SHA-256 verification; distinguish external reference strings|Edited/deleted attachments fail; Markdown snapshotting does not bless changed attachments|
|A directory symlink could alias mutable run metadata as evidence|Reject symlink files and ancestors; reject metadata self-reference after canonicalization|`alias/run.json` through `alias -> .` fails without modifying the manifest|
|A successful process exit alone could conceal skipped application tests|Require a structured result with all four named methods executed and no skipped/failing/expected-failure tests|All-skipped and missing-method reproductions refuse packet completion; normal worked example succeeds|

The final targeted follow-up reproduced these cases after the fixes. It observed no unresolved failure in those exact cases and **77 passing local regression tests**. The unmodified worked example executed all four application methods with no failures, errors or skips and verified six unique evidence files. Other test cases, platforms, actual clients and services are separate evidence requirements.

Seven fresh-context task trials were also preserved, one for every shipped skill. They include a successful build under existing development authority, ordinary planning, a policy conflict, diagnosis with competing hypotheses, untrusted ticket instructions, wrong test expectations and a release-version gap. Complete original tasks/responses, inspected-source hashes and author observations are available in [the recorded packets](../evals/recorded/README.md). The exact model deployment identifier was unavailable. These are selected author-reviewed examples, not a benchmark or independent assurance.

The worked example reruns the captured build's actual source/tests and constructs all six records in explicitly synthetic mode. Every decision is simulated; deployment is not executed. It is a teaching fixture for inspection and mutation experiments, not a claim of real organizational delivery.

## Verification layers

|Layer|Evidence and limit|
|---|---|
|Repository validation|Supported metadata schemas, relative file paths, evaluation catalog and Python syntax. Deliberately constrained; not a general YAML/specification validator.|
|Deterministic tests|Covered installation, measurement, record structure, lineage, typed attachments, trial integrity and worked-example behavior. See the current test output in Actions.|
|Synthetic demo|The misleading test passes; independent checks expose four misses; the corrected function passes seven cases; edited artifacts/source and missing results are detected.|
|Worked change|Real local execution plus six completed teaching records and six unique local evidence files. All decisions are explicitly simulated; no deployment occurs.|
|Skill task trials|Seven captured fresh-context synthetic tasks, complete inputs/outputs and author observations. Exact model deployment identifier unavailable. See [the captures](../evals/recorded/README.md); [two initial excerpt-based trials](../evals/results.md) remain as history.|
|CI portability|Configured Ubuntu/Python 3.10 and 3.13, Windows/Python 3.13 and macOS/Python 3.13. Use the [actual workflow result](https://github.com/vishal8shah/ai-native-sdlc-skills/actions/workflows/validate.yml) as evidence of execution.|

## Remaining limits

- Real Claude Code and Codex discovery/invocation have not been tested here. The installation paths follow their official documentation; enterprise policies and client versions can differ.
- No live ServiceNow instance, production change, genuine approval or operational recovery was exercised.
- Section presence and nonempty text are structural checks, not a judgment that the content satisfies the business requirement.
- Decision fields are supplied metadata. No external approval system or identity is queried.
- Seven selected task trials are not a benchmark. Broader tasks, repeated runs with target clients/models and independent assessment remain outstanding.
- Plain external references are not fetched or verified. Local hashes cannot defend against someone able to rewrite the records and tooling.
- Demo and sample measurement figures are synthetic. No real productivity, cost saving, adoption, reach or virality is claimed.

## Reproduce the local checks

```shell
python scripts/validate_repo.py
python -m unittest discover -s tests -v
python scripts/demo.py --json
python scripts/worked_example.py
python scripts/trials.py verify --require-current
python scripts/render_assets.py
```

The asset generator runs the synthetic demo before rendering the result diagram. A successful README illustration should stay tied to its runnable source.

See the [quality bar](QUALITY_BAR.md) for the claims each layer supports and the next evidence targets. The current GitHub workflow runs validation, tests, demo, trial integrity and the worked example in all four configurations; its actual commit-specific result is the portability evidence.
