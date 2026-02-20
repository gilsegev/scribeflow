from __future__ import annotations

import os

from openai import OpenAI


def config() -> tuple[str, str, str, str]:
    return (
        os.getenv("OPENROUTER_API_KEY", ""),
        os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        os.getenv("OPENROUTER_SITE_URL", "https://visualization-project.local"),
        os.getenv("OPENROUTER_APP_NAME", "Visualization Project"),
    )


def client() -> OpenAI | None:
    key, base_url, site_url, app_name = config()
    if not key:
        return None
    return OpenAI(
        api_key=key,
        base_url=base_url,
        default_headers={
            "HTTP-Referer": site_url,
            "X-Title": app_name,
        },
    )
