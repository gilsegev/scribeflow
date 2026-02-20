from __future__ import annotations

import json
import urllib.request

from dotenv import load_dotenv

from .openrouter import config


def main() -> None:
    load_dotenv()
    key, base_url, _, _ = config()
    if not key:
        raise SystemExit("OPENROUTER_API_KEY is missing in .env")
    req = urllib.request.Request(f"{base_url.rstrip('/')}/key", headers={"Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            print(json.dumps(json.loads(r.read().decode("utf-8")), indent=2))
    except Exception as e:
        detail = e.read().decode("utf-8") if hasattr(e, "read") else str(e)
        raise SystemExit(f"OpenRouter key check failed: {detail}") from e


if __name__ == "__main__":
    main()
