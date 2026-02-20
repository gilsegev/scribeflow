from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from dotenv import load_dotenv

from .broker import run_broker


def main() -> None:
    load_dotenv()
    p = argparse.ArgumentParser(description="Compile manifest/style into visualization payloads, post sequentially, and generate companion review.html.")
    p.add_argument("--markdown", required=True)
    p.add_argument("--manifest", required=True)
    p.add_argument("--style", required=True)
    p.add_argument("--endpoint", default="http://localhost:3000/api/visualizations")
    p.add_argument("--review-html", default="generated_artifacts/review.html")
    p.add_argument("--lesson-id", default="lesson-1")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--compiled-out", default="generated_artifacts/compiled_payloads.json")
    a = p.parse_args()

    md = Path(a.markdown).read_text(encoding="utf-8")
    manifest = json.loads(Path(a.manifest).read_text(encoding="utf-8"))
    style = json.loads(Path(a.style).read_text(encoding="utf-8"))

    result = asyncio.run(
        run_broker(
            markdown=md,
            visual_manifest=manifest,
            style_guide=style,
            endpoint=a.endpoint,
            review_html_path=a.review_html,
            lesson_id=a.lesson_id,
            dry_run=a.dry_run,
        )
    )

    Path(a.compiled_out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.compiled_out).write_text(json.dumps(result.compiled_payloads, indent=2, ensure_ascii=False), encoding="utf-8")
    ok_count = sum(1 for h in result.handshakes if h.get("ok"))
    print(f"Broker done in {result.elapsed_seconds}s")
    print(f"Handshake success: {ok_count}/{len(result.handshakes)}")
    for h in result.handshakes[:3]:
        print(json.dumps(h, ensure_ascii=False))
    print(f"review.html: {a.review_html}")
    print(f"compiled payloads: {a.compiled_out}")


if __name__ == "__main__":
    main()
