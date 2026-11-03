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

## Follow-up review

A fresh-context reviewer re-ran the earlier failures against the revision, followed the walkthrough in temporary Claude/Codex project layouts, and exercised installed runtime commands. The review reported no remaining material first-use failures. It confirmed 44 passing local tests, the documented demo, readiness/recorded-acceptance/staleness/reopening behavior, malformed metadata rejection, and failure cleanup that preserved a pre-existing user skill. No real AI client process, genuine approval or external service was exercised. A minor missing repository link in the installed CLI reference was corrected.

The first expanded GitHub matrix run also completed successfully on Ubuntu/Python 3.10 and 3.13, Windows/Python 3.13 and macOS/Python 3.13. [Inspect that exact run](https://github.com/vishal8shah/ai-native-sdlc-skills/actions/runs/41615301412); the workflow link below shows the current status after later changes.

## Verification layers

|Layer|Evidence and limit|
|---|---|
|Repository validation|Supported metadata schemas, relative file paths, evaluation catalog and Python syntax. Deliberately constrained; not a general YAML/specification validator.|
|Deterministic tests|Covered installation, measurement, record structure, lineage and demo behavior. See the current test output in Actions.|
|Synthetic demo|The misleading test passes; independent checks expose four misses; the corrected function passes seven cases; an edited artifact invalidates its snapshot.|
|Initial skill task trials|Two fresh-context synthetic tasks; review caught a wrong expected result and a release version/approval gap. Exact model deployment identifier was unavailable. See [the trial record](../evals/results.md).|
|CI portability|Configured Ubuntu/Python 3.10 and 3.13, Windows/Python 3.13 and macOS/Python 3.13. Use the [actual workflow result](https://github.com/vishal8shah/ai-native-sdlc-skills/actions/workflows/validate.yml) as evidence of execution.|

## Remaining limits

- Real Claude Code and Codex discovery/invocation have not been tested here. The installation paths follow their official documentation; enterprise policies and client versions can differ.
- No live ServiceNow instance, production change, genuine approval or operational recovery was exercised.
- Section presence and nonempty text are structural checks, not a judgment that the content satisfies the business requirement.
- Decision fields are supplied metadata. No external approval system or identity is queried.
- Two synthetic task trials are not a benchmark. All seven evaluation cases still need repeated runs with target clients/models and retained outputs.
- Demo and sample measurement figures are synthetic. No real productivity, cost saving, adoption, reach or virality is claimed.

## Reproduce the local checks

```shell
python scripts/validate_repo.py
python -m unittest discover -s tests -v
python scripts/demo.py --json
python scripts/render_assets.py
```

The asset generator runs the synthetic demo before rendering the result diagram. A successful README illustration should stay tied to its runnable source.
