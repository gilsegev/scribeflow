from __future__ import annotations

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

from .draft import DraftService


def main() -> None:
    load_dotenv()
    p = argparse.ArgumentParser(description="Expand markdown into a 5-page-ready draft with visual placeholders.")
    p.add_argument("--markdown", required=True)
    p.add_argument("--manifest", required=True)
    p.add_argument("--style", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    md = Path(a.markdown).read_text(encoding="utf-8")
    manifest = json.loads(Path(a.manifest).read_text(encoding="utf-8"))
    style = json.loads(Path(a.style).read_text(encoding="utf-8"))
    out = DraftService().expand(md, manifest, style)
    out_path = Path(a.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(out, encoding="utf-8")
    print(f"Wrote expanded draft to {out_path}")


if __name__ == "__main__":
    main()
