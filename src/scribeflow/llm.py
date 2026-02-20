from __future__ import annotations

import json
import os
import re
from typing import Any

from openai import OpenAI

SYSTEM_PROMPT = """You are ScribeLLM, a Senior Visual Pedagogy Expert.
Analyze markdown curriculum and identify high-cognitive-load or abstract sections
that benefit from visuals using Dual Coding Theory and the Signaling Principle.
Keep recommendations tasteful: limit to 1-2 high-impact artifacts per page.
Return only JSON with:
{
  "visual_manifest": [
    {
      "anchor_sentence": "... exact sentence from the source ...",
      "rationale": "... pedagogical reason ...",
      "template_type": "versus_split|bento_grid|step_journey|story_image",
      "data_payload": { ... template-ready structured data ... }
    }
  ],
  "style_guide": {
    "palette": ["#......", "#......", "#......", "#......", "#......", "#......"],
    "mood": "..."
  }
}
"""


def _sentences(markdown: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", markdown) if len(s.strip()) > 25]


def _template_for(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["versus", "vs", "compared", "difference", "tradeoff"]):
        return "versus_split"
    if re.search(r"(^|\s)(first|second|third|step|process|workflow)\b", t):
        return "step_journey"
    if any(k in t for k in ["framework", "components", "dimensions", "pillars"]):
        return "bento_grid"
    return "story_image"


def _heuristic_style(markdown: str) -> dict[str, Any]:
    m = markdown.lower()
    if any(k in m for k in ["health", "wellness", "mindful", "care"]):
        return {"palette": ["#E6F4EA", "#B7DCC8", "#7DB69E", "#3E7C67", "#2F5144", "#F6FBF8"], "mood": "Serene Wellness"}
    if any(k in m for k in ["architecture", "system", "api", "technical"]):
        return {"palette": ["#0B1F3A", "#1F4B99", "#3E7CB1", "#A7C6ED", "#EAF2FF", "#5B6B7A"], "mood": "Modern Technical"}
    return {"palette": ["#1F2937", "#3B82F6", "#60A5FA", "#D1E5FF", "#F8FAFC", "#0F766E"], "mood": "Focused Professional"}


def _heuristic(markdown: str, page_estimate: int) -> dict[str, Any]:
    sents = _sentences(markdown)
    limit = max(1, min(2 * max(1, page_estimate), len(sents)))
    ranked = sorted(sents, key=lambda s: (len(s), sum(k in s.lower() for k in ["because", "therefore", "however", "process", "system"])), reverse=True)[:limit]
    manifest = [{
        "anchor_sentence": s,
        "rationale": "High information density; a visual can reduce cognitive load and improve signaling.",
        "template_type": _template_for(s),
        "data_payload": {"source_excerpt": s, "key_points": [p.strip() for p in re.split(r"[,:;]", s)[:4] if p.strip()]},
    } for s in ranked]
    return {"visual_manifest": manifest, "style_guide": _heuristic_style(markdown)}


class ScribeLLM:
    def __init__(self, model: str | None = None) -> None:
        self.model = model or os.getenv("SCRIBEFLOW_LLM_MODEL", "google/gemini-3-flash")
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        self.client = (
            OpenAI(
                api_key=openrouter_key,
                base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            )
            if openrouter_key
            else None
        )

    def analyze(self, markdown: str, page_estimate: int) -> dict[str, Any]:
        if not self.client:
            return _heuristic(markdown, page_estimate)
        user_prompt = (
            f"Estimated pages: {page_estimate}\n"
            "Produce tasteful recommendations only.\n\n"
            f"Markdown:\n{markdown[:12000]}"
        )
        resp = self.client.chat.completions.create(
            model=self.model,
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}],
        )
        return json.loads(resp.choices[0].message.content or "{}")
