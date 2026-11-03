---
name: ai-native-sdlc-skills
description: "Run an evidence-based software delivery workflow from intent through design, implementation, verification, release preparation and operational learning. Use for AI-native SDLC adoption, stage handovers, delivery pilots or choosing the right bundled SDLC skill; do not load the whole bundle for an unrelated task."
---
# Run the appropriate delivery stage

1. Identify the actual work item, source of truth, current stage, authorized scope and desired output. Inspect available evidence before asking for information already supplied.
2. Read only the relevant stage skill below. For a complete request, proceed through the stages within the existing authorization, preserving linked evidence and actual required decisions.
3. Use [the delivery contract](references/delivery-contract.md) for record lineage, acceptance and working status. For ServiceNow work, also read [the platform adaptation](references/servicenow.md).
4. Treat the scripts as local helpers. They neither call AI nor authenticate approvals, enforce access or connect to any external service. Read [the CLI reference](references/cli.md) before first use.
5. Finish with the produced output, inspected evidence, checks actually run, verification limits and next decision owner. Never claim an operational benefit without measurements.

## Stage selection

|Work requested|Read this skill|Primary output|
|---|---|---|
|Clarify the problem and outcome|[sdlc-plan](skills/sdlc-plan/SKILL.md)|intent.md|
|Specify behavior and constraints|[sdlc-design](skills/sdlc-design/SKILL.md)|spec.md|
|Plan and implement a bounded change|[sdlc-build](skills/sdlc-build/SKILL.md)|plan.md plus actual change|
|Verify accepted behavior|[sdlc-test](skills/sdlc-test/SKILL.md)|test-evidence.md|
|Review and prepare a release decision|[sdlc-deploy](skills/sdlc-deploy/SKILL.md)|release.md|
|Investigate outcomes and improve the process|[sdlc-maintain](skills/sdlc-maintain/SKILL.md)|lessons.md or new intent|

## Start small

Start with one low-impact change whose outcome can be checked. Agree expected results before implementation. Keep a named independent reviewer and use the existing authoritative work/change records. Measure waiting separately from active work and elapsed time separately from staff effort. Expand only on observed evidence and approved controls.
