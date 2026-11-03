# Contribute a result someone else can reproduce

Start with a focused change: one skill behavior, a helper bug, a clearer example, or a redacted/synthetic pilot write-up. Report failures as well as successes.

1. Describe the concrete task and current behavior. For a skill, give the prompt, supplied inputs and the output that matters.
2. Make the smallest useful change. Keep SKILL.md concise and link stage resources directly. Preserve existing authorization and real decision boundaries.
3. Add a meaningful deterministic regression for a helper bug, or a scenario and reviewer rubric for changed skill behavior. Do not leak the desired answer into a blind task trial.
4. Run repository validation, tests and the demo. Explain verification limits in the pull request.

```shell
python scripts/validate_repo.py
python -m unittest discover -s tests -v
python scripts/demo.py --json
python scripts/worked_example.py
python scripts/trials.py verify --require-current
```

The validator deliberately supports this repository's simple, one-line skill frontmatter and three-field quoted UI metadata schema. Descriptions must be nonblank double-quoted strings with JSON-compatible escaping. It is not a general YAML parser or a universal Agent Skills validator. Keep metadata in that format or extend the schema and tests together.

When a trial's inspected skill/template changes, retain the original packet as history and capture a new fresh-context trial against the new source. Do not silently rewrite historical source hashes to make a check pass. Review the new input/output and update the current-source coverage check deliberately. [The trial method](evals/recorded/README.md) explains the current seven-packet starter set; it is not a statistical evaluation framework.

For local delivery evidence, use `attach-evidence` so the file's bytes are checked. Keep links to external records but describe them as unverified by the local helper. Synthetic records must identify their simulated decisions; never present the example's accepted statuses as real approvals.

For pilot reports, use [the report template](docs/PILOT_REPORT_TEMPLATE.md). Include the client/model and skill version, sample size, baseline, costs, quality and confounders. Do not claim independent assurance from a second AI verdict alone.

Use synthetic or approved redacted data. Keep credentials and internal records out of commits and issues. Original contributions are covered by the repository's MIT license.
