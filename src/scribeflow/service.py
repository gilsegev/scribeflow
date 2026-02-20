from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from .discovery import DiscoveryService
from .llm import ScribeLLM


def _estimate_pages(markdown: str) -> int:
    return max(1, round(len(markdown.split()) / 450))


def process_docx(docx_path: str | Path) -> dict[str, Any]:
    started = time.perf_counter()
    markdown = DiscoveryService().extract_markdown(docx_path)
    page_estimate = _estimate_pages(markdown)
    analysis = ScribeLLM().analyze(markdown, page_estimate)
    return {
        "visual_manifest": analysis.get("visual_manifest", []),
        "style_guide": analysis.get("style_guide", {}),
        "meta": {
            "docx_path": str(docx_path),
            "page_estimate": page_estimate,
            "extraction_seconds": round(time.perf_counter() - started, 3),
        },
    }
