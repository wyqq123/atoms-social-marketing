# Atoms Social Marketing - Test Results

**Date:** 2026-07-28  
**Scope:** Conversation Clarifier positioning-intake path, existing realtime-probe regression coverage, and JSON handoff contract.

## Implemented Coverage

- Automatic routing to `quick_confirm` only for explicit, high-confidence candidates.
- Mandatory user confirmation before a session emits a pipeline handoff.
- Clarification priority: `target_audience`, then `promo_goal`, then `key_selling_point`.
- Builder identity candidates do not qualify for automatic confirmation.
- Custom values, one/two-option audience selection, HIL form fallback, form prefill, and two-invalid-answer fallback.
- Stateless CLI protocol: `start -> answer -> ready handoff`.
- JSON Schema validation for a ready intake session.

## Commands And Results

| Check | Command | Result |
|---|---|---|
| Full automated suite | `python -B -m unittest discover -s tests -p 'test_*.py'` | PASS: 16 tests, 0 failures, 0 errors |
| Ready handoff schema | Python smoke validation with `jsonschema.validate` against `data/positioning_intake_schema.json` | PASS: `ready-handoff-schema-valid` |
| Intake script syntax | Python AST parse of `intake_models.py`, `state_machine.py`, `run_positioning_intake.py` | PASS |
| Diff whitespace | `git diff --check` | PASS: no whitespace errors |
| Existing realtime probe regression | Included in full suite | PASS: 8 existing tests |

## Verification Notes

- Tests run with `PYTHONDONTWRITEBYTECODE=1` to avoid modifying tracked Python cache artifacts.
- No live YouTube, Reddit, or Google CSE request was made because this change does not require API credentials; realtime adapters remain covered by their existing mock/no-network tests.
- The new state machine is intentionally stateless. The Atoms host must persist the returned session JSON and restrict Stage 1/Stage 2b tools until `route` is `ready` and `handoff` is present.