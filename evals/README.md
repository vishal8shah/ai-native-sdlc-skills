# Behavior evaluations

Run each case in a fresh assistant context with only its named skill and the stated inputs. Capture the exact client/model version, prompt, supplied evidence, actual output and date. A reviewer scores each rubric item pass, fail or insufficient evidence. Do not tell the assistant the rubric or expected conclusion during the run.

Cases are original synthetic scenarios. Do not let an evaluation touch real services. Report deterministic helper tests separately from model behavior evaluation. An artifact should be assessed for correctness and useful next actions, not just whether it contains the right words.

Forward tests performed during initial authoring are recorded in `results.md`; they cover only the listed scenarios, not all clients or models.
