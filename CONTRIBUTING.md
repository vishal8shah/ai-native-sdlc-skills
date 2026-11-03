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
```

The validator deliberately supports this repository's simple, one-line skill frontmatter and three-field quoted UI metadata schema. It is not a general YAML parser or a universal Agent Skills validator. Keep metadata in that format or extend the schema and tests together.

For pilot reports, use [the report template](docs/PILOT_REPORT_TEMPLATE.md). Include the client/model and skill version, sample size, baseline, costs, quality and confounders. Do not claim independent assurance from a second AI verdict alone.

Use synthetic or approved redacted data. Keep credentials and internal records out of commits and issues. Original contributions are covered by the repository's MIT license.
