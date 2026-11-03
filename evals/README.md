# Behavior evaluations

Run each case in a fresh assistant context with only its named skill and the stated inputs. Capture the exact client/model version, prompt, supplied evidence, actual output and date. A reviewer scores each rubric item pass, fail or insufficient evidence. Do not tell the assistant the rubric or expected conclusion during the run.

Cases are original synthetic scenarios. Do not let an evaluation touch real services. Report deterministic helper tests separately from model behavior evaluation. An artifact should be assessed for correctness and useful next actions, not just whether it contains the right words.

The [initial two authoring trials](results.md) are retained as history. The [seven captured task packets](recorded/README.md) add original inputs, complete final responses, inspected-source hashes, provenance and author observations for every shipped skill, including a successful authorized build. These are selected task trials, not a statistical benchmark or certification of native clients.

Run `python scripts/trials.py verify --require-current` to check the captures and source correspondence. Use `python scripts/trials.py prompt DEMO-301 --client codex` to print one input for manual replay without the response. The command does not run a model or score an output.
