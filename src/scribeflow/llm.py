from __future__ import annotations

import json
import os
import re
from typing import Any

from openai import AuthenticationError

from .openrouter import client as openrouter_client

SYSTEM_PROMPT = """You are ScribeLLM, a Senior Visual Pedagogy Expert.
Analyze markdown curriculum and identify high-cognitive-load or abstract sections
that benefit from visuals using Dual Coding Theory and the Signaling Principle.
Keep recommendations tasteful: limit to 1-2 high-impact artifacts per page.
Critical image-generation constraint:
- Flux-style image generation is weak at text rendering. Never ask the image model to render words, numbers, labels, equations, or logos inside imagery.
- Always describe scenes/symbols/composition only; text will be overlaid later by templates.
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

NO_TEXT_TERMS = ["text", "numbers", "letters", "labels", "captions", "equations", "logos", "watermarks"]


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
    return _enforce_visual_constraints({"visual_manifest": manifest, "style_guide": _heuristic_style(markdown)})


def _strip_text_generation_phrases(text: str) -> str:
    t = text.strip()
    t = re.sub(r"\b(with|include|show|add)\s+(visible\s+)?(text|numbers?|letters?|labels?|captions?|equations?)\b", "with visual symbols only", t, flags=re.I)
    t = re.sub(r"\b(labeled|labelled)\b", "symbol-marked", t, flags=re.I)
    return t


def _enforce_visual_constraints(analysis: dict[str, Any]) -> dict[str, Any]:
    manifest = analysis.get("visual_manifest") if isinstance(analysis, dict) else None
    if not isinstance(manifest, list):
        return analysis
    for item in manifest:
        if not isinstance(item, dict):
            continue
        payload = item.get("data_payload")
        if not isinstance(payload, dict):
            payload = {}
        t = str(item.get("template_type", "")).lower()
        if isinstance(payload.get("image_description"), str):
            payload["image_description"] = _strip_text_generation_phrases(payload["image_description"])
        if isinstance(payload.get("description"), str):
            payload["description"] = _strip_text_generation_phrases(payload["description"])
        if t in {"story_image", "bento_grid", "step_journey"}:
            payload["rendering_constraints"] = {
                "no_baked_text": True,
                "no_numbers_or_equations": True,
                "do_not_include": NO_TEXT_TERMS,
            }
            neg = payload.get("negative_prompt_terms", [])
            payload["negative_prompt_terms"] = list(dict.fromkeys(([*(neg if isinstance(neg, list) else []), *NO_TEXT_TERMS])))
        for key in ("items", "steps", "points_of_interest"):
            seq = payload.get(key)
            if isinstance(seq, list):
                for obj in seq:
                    if isinstance(obj, dict):
                        if isinstance(obj.get("image_description"), str):
                            obj["image_description"] = _strip_text_generation_phrases(obj["image_description"])
                        obj["no_baked_text"] = True
        item["data_payload"] = payload
    analysis["visual_manifest"] = manifest
    return analysis


class ScribeLLM:
    def __init__(self, model: str | None = None) -> None:
        self.model = model or os.getenv("OPENROUTER_MODEL") or os.getenv("SCRIBEFLOW_LLM_MODEL", "google/gemini-2.5-flash-lite")
        self.client = openrouter_client()

    def analyze(self, markdown: str, page_estimate: int) -> dict[str, Any]:
        if not self.client:
            return _heuristic(markdown, page_estimate)
        user_prompt = (
            f"Estimated pages: {page_estimate}\n"
            "Produce tasteful recommendations only.\n\n"
            f"Markdown:\n{markdown[:12000]}"
        )
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                temperature=0.2,
                response_format={"type": "json_object"},
                messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}],
            )
        except AuthenticationError as e:
            raise RuntimeError(
                "OpenRouter authentication failed (401). Update OPENROUTER_API_KEY in .env (current key is invalid/revoked)."
            ) from e
        return _enforce_visual_constraints(json.loads(resp.choices[0].message.content or "{}"))
