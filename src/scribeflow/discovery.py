from __future__ import annotations

from pathlib import Path

from markitdown import MarkItDown


class DiscoveryService:
    def __init__(self) -> None:
        self._converter = MarkItDown()

    def extract_markdown(self, docx_path: str | Path) -> str:
        result = self._converter.convert(str(docx_path))
        return (
            getattr(result, "text_content", None)
            or getattr(result, "markdown", None)
            or str(result)
        ).strip()
