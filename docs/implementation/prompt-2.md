# Prompt 2 Implementation (Broker & Integration Layer)

## What was implemented
- Added `BrokerService` to compile Prompt-1 outputs into Visualization Engine payloads.
- Added ID management (`lesson-1-viz-N`) for each artifact.
- Added template type mapping and payload sanitization per template.
- Injected `globalStyleGuide` into every compiled payload.
- Added sequential async POST queue with retry/backoff for handshake resilience.
- Added Companion HTML generator (`review.html`) that aligns markdown paragraphs with visual anchors.
- Aligned compiled JSON layout with `assets/test docs/fishing_course.json`:
  - top-level keys: `course`, `lessons`, `production`
  - lesson shape includes `visualizations[]` entries expected by the visualization engine.

## New files
- `src/scribeflow/broker.py`
- `src/scribeflow/broker_cli.py`

## CLI
```bash
scribeflow-broker \
  --markdown generated_artifacts/the_american_angler.extracted.md \
  --manifest generated_artifacts/the_american_angler.visual_manifest.json \
  --style generated_artifacts/the_american_angler.style_guide.json \
  --endpoint http://localhost:3000/api/visualizations \
  --review-html generated_artifacts/review.html \
  --compiled-out generated_artifacts/compiled_payloads.json
```

## Dry-run mode
Use `--dry-run` to validate compile + review HTML generation without calling the Visualization Engine.
