from __future__ import annotations

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from .service import process_docx


def main() -> None:
    load_dotenv()
    if len(sys.argv) != 2:
        print("Usage: scribeflow <path-to-docx>")
        raise SystemExit(2)
    path = Path(sys.argv[1])
    if not path.exists() or path.suffix.lower() != ".docx":
        print("Input must be an existing .docx file.")
        raise SystemExit(2)
    result = process_docx(path)
    print(json.dumps(result["visual_manifest"], indent=2, ensure_ascii=False))
    print(json.dumps(result["style_guide"], indent=2, ensure_ascii=False))
    print(json.dumps(result["meta"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
