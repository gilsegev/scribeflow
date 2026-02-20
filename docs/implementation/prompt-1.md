# Prompt 1 Implementation

## What was implemented
- Standalone Python service under `src/scribeflow`.
- Discovery layer using `MarkItDown` for `.docx -> markdown`.
- `ScribeLLM` module with a pedagogy-focused system prompt and tasteful artifact limits.
- JSON outputs for `visual_manifest` and `style_guide` for each processed document.
- CLI entrypoint: `scribeflow <path-to-docx>`.

## Directory layout
- `src/scribeflow/discovery.py`: document extraction.
- `src/scribeflow/llm.py`: LLM analysis + heuristic fallback.
- `src/scribeflow/service.py`: orchestration and timing metadata.
- `src/scribeflow/cli.py`: script interface printing JSON outputs.
- `pyproject.toml`: dependencies and script registration.

## Run
```bash
pip install -e .
scribeflow path/to/file.docx
```

## Notes
- `.env` now includes OpenRouter settings and defaults the model to `google/gemini-2.5-flash-lite`.
- If `OPENROUTER_API_KEY` is present, the service calls OpenRouter.
- Without an API key, the service falls back to deterministic local heuristics so development can continue.
