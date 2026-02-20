from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any

import httpx

SUPPORTED_TYPES = {"bento_grid", "versus_split", "step_journey", "story_image"}


def _map_type(t: str) -> str:
    if t in SUPPORTED_TYPES:
        return t
    if t == "steps":
        return "step_journey"
    return "story_image"


def _sanitize_payload(t: str, payload: dict[str, Any]) -> dict[str, Any]:
    if t == "versus_split":
        return {
            "title": payload.get("title", "Comparison"),
            "panels": [
                {"side": "left", "label": payload.get("left_column_title", "Left"), "characteristics": [payload.get("left_column_text", "")]},
                {"side": "right", "label": payload.get("right_column_title", "Right"), "characteristics": [payload.get("right_column_text", "")]},
            ],
            "bridgeElement": payload.get("comparison_point", "Key Difference"),
        }
    if t == "bento_grid":
        items = payload.get("items", [])
        return {"title": payload.get("title", "Grid Reference"), "distortions": items if isinstance(items, list) else []}
    if t == "step_journey":
        steps = payload.get("steps", [])
        return {"title": payload.get("title", "Step Journey"), "structure": {"milestones": steps if isinstance(steps, list) else []}}
    return {
        "title": payload.get("title", "Story Image"),
        "imageSpecs": {
            "brief": payload.get("image_description") or payload.get("description") or payload.get("title", "Context image"),
            "points_of_interest": payload.get("points_of_interest", []),
        },
    }


def _style_injection(style_guide: dict[str, Any]) -> dict[str, Any]:
    palette = style_guide.get("palette", [])
    return {
        "colorPalette": {
            "riverBlue": palette[0] if len(palette) > 0 else "#2B6CB0",
            "forestGreen": palette[1] if len(palette) > 1 else "#2F855A",
            "sunriseGold": palette[2] if len(palette) > 2 else "#D69E2E",
            "stoneGrey": palette[3] if len(palette) > 3 else "#4A5568",
            "foamWhite": palette[4] if len(palette) > 4 else "#F7FAFC",
            "deepNavy": palette[5] if len(palette) > 5 else "#1A365D",
            "warningOrange": palette[3] if len(palette) > 3 else "#DD6B20",
        },
        "typography": {"fontFamily": ["Inter", "Source Sans Pro"], "heading": "18-22pt bold", "body": "12-14pt regular", "decorativeFontsAllowed": False},
        "layout": {"whitespace": "Generous", "clutter": "None", "principle": "Every element must earn its place"},
        "illustrationStyle": {
            "design": "Clean vector infographics + realistic photo-based story images",
            "shapes": "Simple icons and panels for diagrams; natural scenes for photos",
            "humanFigures": "Real people in photos; no identifiable faces required (prefer turned-away or out-of-focus)",
        },
        "mood": style_guide.get("mood", "Informative, Adventurous, Natural"),
    }


class BrokerService:
    def compile_payloads(self, visual_manifest: list[dict[str, Any]], style_guide: dict[str, Any], lesson_id: str = "lesson-1") -> list[dict[str, Any]]:
        style = _style_injection(style_guide)
        compiled = []
        for i, item in enumerate(visual_manifest, start=1):
            mapped = _map_type(item.get("template_type", "story_image"))
            body = _sanitize_payload(mapped, item.get("data_payload", {}))
            dimensions = {"width": 1400, "height": 900, "orientation": "landscape"} if mapped == "story_image" else {"width": 1200, "height": 1200, "orientation": "landscape"}
            compiled.append(
                {
                    "visualizationId": f"1.{i}",
                    "title": body.get("title", f"Visualization {i}"),
                    "type": mapped,
                    "dimensions": dimensions,
                    "placement": "Inline near anchor sentence",
                    "purpose": item.get("rationale", ""),
                    "anchorSentence": item.get("anchor_sentence", ""),
                    "globalStyleGuide": style,
                    **({k: v for k, v in body.items() if k != "title"}),
                }
            )
        return compiled

    def compile_course_payload(self, visual_manifest: list[dict[str, Any]], style_guide: dict[str, Any], lesson_id: str = "lesson-1", course_title: str = "ScribeFlow Course") -> dict[str, Any]:
        visualizations = self.compile_payloads(visual_manifest, style_guide, lesson_id=lesson_id)
        return {
            "course": {
                "title": course_title,
                "targetAudience": "Curriculum learners requiring visual reinforcement",
                "designPhilosophy": "Pedagogical clarity with calm, scannable visuals.",
                "learningScienceRationale": [
                    {"principle": "Dual Coding Theory", "theorist": "Paivio", "description": "Pair text with visuals to improve retention."},
                    {"principle": "Signaling Principle", "theorist": "Mayer", "description": "Highlight key contrasts and structure to reduce search effort."},
                ],
                "globalStyleGuide": _style_injection(style_guide),
            },
            "lessons": [{"lessonId": lesson_id, "title": "Auto-generated lesson", "description": "Generated from Prompt-1 visual manifest.", "visualizations": visualizations}],
            "production": {
                "recommendedWorkflow": [
                    "Generate visual elements first",
                    "Export at 2x resolution",
                    "Overlay text manually in design tool",
                    "Verify color consistency across all visuals",
                ],
                "placementGuidelines": [
                    "Precede each visual with one setup sentence",
                    "Follow with one reference sentence",
                    "Avoid orphan visuals without anchor context",
                ],
            },
        }

    async def post_sequential(self, payloads: list[dict[str, Any]], endpoint: str, timeout_s: float = 10.0) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            for p in payloads:
                for attempt in range(3):
                    try:
                        r = await client.post(endpoint, json=p)
                        r.raise_for_status()
                        results.append({"visualizationId": p["visualizationId"], "ok": True, "response": r.json() if r.text else {}})
                        break
                    except Exception as e:
                        if attempt == 2:
                            results.append({"visualizationId": p["visualizationId"], "ok": False, "error": str(e)})
                        else:
                            await asyncio.sleep(0.3 * (attempt + 1))
        return results


@dataclass
class BrokerRunResult:
    compiled_payloads: dict[str, Any]
    handshakes: list[dict[str, Any]]
    elapsed_seconds: float


def generate_review_html(markdown: str, compiled_payloads: dict[str, Any], handshakes: list[dict[str, Any]], out_path: str | Path) -> None:
    url_by_id = {}
    for h in handshakes:
        if h.get("ok"):
            body = h.get("response", {})
            url_by_id[h["visualizationId"]] = body.get("url") or body.get("imageUrl") or body.get("posterUrl") or ""

    visualizations = ((compiled_payloads.get("lessons") or [{}])[0].get("visualizations") or [])
    paras = [p.strip() for p in markdown.split("\n\n") if p.strip()]
    anchors: dict[int, list[dict[str, Any]]] = {i: [] for i in range(len(paras))}
    for p in visualizations:
        anchor = p.get("anchorSentence", "")
        idx = next((i for i, para in enumerate(paras) if anchor and anchor in para), len(paras) - 1 if paras else 0)
        anchors.setdefault(idx, []).append(p)

    rows = []
    for i, para in enumerate(paras):
        cards = []
        for viz in anchors.get(i, []):
            vid = viz["visualizationId"]
            url = url_by_id.get(vid, "")
            media = f'<img src="{escape(url)}" alt="{escape(vid)}"/>' if url else '<div class="ph">PNG Placeholder</div>'
            cards.append(
                f'<div class="card"><div><b>{escape(viz["visualizationId"])}</b> · {escape(viz["type"])}</div>'
                f'<div class="small">{escape(viz["anchorSentence"][:180])}</div>{media}</div>'
            )
        right = "".join(cards) if cards else '<div class="small muted">No visual mapped</div>'
        rows.append(f'<div class="row"><pre class="left">{escape(para)}</pre><div class="right">{right}</div></div>')

    html = f"""<!doctype html><html><head><meta charset="utf-8"/><title>ScribeFlow Review</title>
<style>body{{font-family:Segoe UI,Arial,sans-serif;margin:16px}}.row{{display:grid;grid-template-columns:1.2fr 1fr;gap:14px;border-bottom:1px solid #ddd;padding:10px 0}}
.left{{white-space:pre-wrap;margin:0;background:#f8fafc;padding:10px;border-radius:8px}}.card{{border:1px solid #ccd;padding:8px;border-radius:8px;margin-bottom:8px;background:#fff}}
img{{width:100%;border-radius:6px;margin-top:6px}}.ph{{height:140px;display:flex;align-items:center;justify-content:center;background:#eef2f7;border-radius:6px;margin-top:6px}}
.small{{font-size:12px}}.muted{{color:#6b7280}}</style></head><body>
<h2>Companion HTML Review</h2><p>Left: full markdown paragraphs. Right: generated PNGs/placeholders aligned to anchor_sentence.</p>
{''.join(rows)}</body></html>"""
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(html, encoding="utf-8")


async def run_broker(markdown: str, visual_manifest: list[dict[str, Any]], style_guide: dict[str, Any], endpoint: str, review_html_path: str | Path, lesson_id: str = "lesson-1", dry_run: bool = False) -> BrokerRunResult:
    start = time.perf_counter()
    svc = BrokerService()
    compiled = svc.compile_course_payload(visual_manifest, style_guide, lesson_id=lesson_id)
    visualizations = ((compiled.get("lessons") or [{}])[0].get("visualizations") or [])
    handshakes = (
        [{"visualizationId": p["visualizationId"], "ok": True, "response": {"url": ""}} for p in visualizations]
        if dry_run
        else await svc.post_sequential(visualizations, endpoint)
    )
    generate_review_html(markdown, compiled, handshakes, review_html_path)
    return BrokerRunResult(compiled_payloads=compiled, handshakes=handshakes, elapsed_seconds=round(time.perf_counter() - start, 3))
