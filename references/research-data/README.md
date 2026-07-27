# Research Data

This directory stores offline research assets for platform playbooks. These files are not Stage 1 or Stage 2 runtime inputs.

Runtime data allowed by the v3 platform coverage and trend intelligence rebuild remains in `data/`:

- `platform_registry.json` and `platform_registry_schema.json`
- `opportunity_evidence_brief_schema.json`
- `inputs_schema.json`, `launch_pack_schema.json`, `ga4_snapshot_schema.json`
- `trigger_signals.json`, `lifecycle_chips.json`

Research assets here may be used to periodically update `references/platform-playbooks/*.md`, but they must not be read by Stage 2 fit scoring, realtime probe adapters, or opportunity evidence brief generation.

## Layout

- `schemas/`: extraction schemas for offline case-study research.
- `instagram/`: industry URL pool, extracted case studies, and manual supplements for Instagram playbook research.
- `youtube/`: industry URL pool, extracted case studies, fetched video sample outputs, and manual supplements for YouTube playbook research.
- `tiktok/`: industry URL pool, extracted case studies, manual supplements, and a historical Creative Center snapshot sample.

## v3 Boundary

- Case studies and manual supplements are long-term structure research, not current-trend evidence.
- Creative Center outputs should be refreshed into `.cache/social_intel/manual/tiktok/{region}/{language}/{YYYY-Www}/creative-center.json` when used as L5 cache. The checked-in `tiktok/creative_center_snapshot_sample.json` is only a historical/example artifact.
- App-specific evidence must be produced as `opportunity_evidence_brief` and validated against `data/opportunity_evidence_brief_schema.json`.