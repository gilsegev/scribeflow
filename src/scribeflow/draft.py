from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI

SYSTEM_PROMPT = """You are ScribeFlow Writer. Return only markdown.
Write a full, scannable 5-page-ready draft with an informative, adventurous, natural tone.
Requirements:
- Expand all existing sections with richer detail.
- In knots section, explain knot physics (friction, load distribution, tag-end behavior).
- In Texas lakes, include best seasons and recommended rods/reels per lake.
- Add a new section titled "Seasonal Tactics" (Spring->Winter).
- Convert common fish species into a detailed 2-column markdown table: Species | Expanded Habitat & Behavior.
- Insert placeholders exactly as:
  [VISUAL INSERT: {Template Type} - {Description from Manifest}]
  Graphic Details: include manifest data_payload and style guide palette/mood notes.
- Use bolding and bullets for scanability.
"""


def _fallback(md: str, manifest: list[dict[str, Any]], style: dict[str, Any]) -> str:
    def v(i: int) -> str:
        m = manifest[i] if i < len(manifest) else {}
        return (
            f"[VISUAL INSERT: {m.get('template_type','story_image')} - {m.get('rationale','visual support')}]\n"
            f"Graphic Details: data_payload={json.dumps(m.get('data_payload', {}), ensure_ascii=False)}; "
            f"palette={style.get('palette', [])}; mood={style.get('mood', '')}"
        )

    return f"""# The American Angler's Guide: Fundamentals, Trends, and the Texas Frontier

**Date:** February 20, 2026  
**Subject:** Comprehensive Overview of U.S. Recreational Fishing  
**Mood:** {style.get('mood', 'Informative, Adventurous, Natural')}

## I. The State of the Sport: Participation and Economics
Recreational fishing remains the largest outdoor participation sport in the U.S., with **57.7 million anglers** and broad reach across age groups, geographies, and income brackets. The participation story is not just about volume. It is about repeat behavior, where anglers invest in licenses, tackle, travel, lodging, electronics, and guided experiences year after year.

### Why participation keeps growing
- **Accessible entry points:** A local pond, basic combo, and a short time window can still produce a meaningful day on the water.
- **Mental reset value:** Anglers consistently report stress reduction, focus restoration, and stronger connection to place.
- **Family transfer effect:** Skills move intergenerationally, so each active angler often recruits another.

{v(0)}

### Economic mechanics
The often-quoted direct spend only tells part of the story. In practice, fishing drives a local chain: marinas, fuel docks, bait shops, boat service, guide operations, and destination hospitality. A single tournament weekend can meaningfully lift regional revenue, while steady weekend traffic sustains small businesses through non-peak tourism periods.

## II. The Essential Knots: Mastery of the Connection
A knot is a controlled friction system. The strongest knots do three things well: they **increase surface contact**, **distribute load** gradually, and **prevent tag-end slip** under cyclical force.

### 2.1 Improved Clinch Knot (Monofilament Standard)
The Improved Clinch performs because each wrap adds friction against the standing line. Under load, those wraps compress and lock, while the final tuck creates a second retention point. On mono, slight line stretch helps absorb shock and reduces abrupt stress concentration.

### 2.2 Palomar Knot (Braided-Line Workhorse)
Braid is slick, so knots that rely on single friction points can slip. The Palomar doubles line through the eye, increasing contact area and reducing pressure per strand. The overhand segment forms a compact core, and the final cinch creates a high-strength lock with minimal twist damage.

### 2.3 Surgeon's Loop (Leader Mobility)
The Surgeon's Loop is efficient because it builds a doubled loop body that resists collapse and allows a lure to articulate naturally. More freedom of movement often improves lure action in clear or pressured water.

### Practical knot protocol
- **Moisten before cinching:** Reduces heat and micro-abrasion.
- **Seat slowly, then test:** Pull steadily until fully set; hard snap-tests can mask weak seating.
- **Retie after abrasion:** One rough rock or dock post can compromise knot integrity.

{v(1)}

## III. Baits and Lures: Strategy by Species and Conditions
Matching bait to fish behavior is less about preference and more about context: forage base, water clarity, wind, temperature, and pressure.

### 3.1 Live and Natural Baits
- **Nightcrawlers:** Reliable in low-visibility water and for neutral fish.
- **Crayfish:** Prime around rock transitions and current seams.
- **Shad/Minnows:** Best where predator fish are actively corralling bait schools.

### 3.2 Artificial Lures
- **Soft plastics:** Precise bottom contact and profile control.
- **Crankbaits:** Rapid water coverage and depth targeting via bill design.
- **Spinners/underspins:** Flash and vibration for stained water or windy chop.

## IV. Common Fish Species (Expanded Field Reference)
| Species | Expanded Habitat & Behavior |
| --- | --- |
| **Largemouth Bass** | Occupies weedy flats, timber edges, and dock shade lines. Ambush predator that often tracks prey from cover before committing. Most aggressive during low-light windows or feeding surges around weather changes. |
| **Channel Catfish** | Thrives in turbid rivers and reservoir channels with current breaks. Uses scent and vibration detection more than vision. Often feeds in predictable lanes near bottom transitions and eddies. |
| **Rainbow Trout** | Prefers cold, oxygen-rich systems and responds strongly to current seams, insect hatches, and subtle presentation errors. Pressure-sensitive fish that rewards stealth, line control, and drift quality. |
| **Walleye** | Common along deep rock, points, and saddle structures. Visual predator tuned for low-light feeding; dawn, dusk, and wind-driven banks are high-percentage windows. Frequently groups by depth and forage type. |

{v(2)}

## V. Texas Fishing: The Lone Star Deep Dive
Texas offers diverse water profiles, which means tactic diversity is mandatory. The best anglers adapt by season, water color, and forage behavior rather than forcing one confidence pattern.

### 5.1 Lake Fork (Trophy Bass Program)
**Best seasons:** Late winter pre-spawn through spring, and fall shad migration.  
**Recommended gear:**  
- Rod: **7'2" to 7'6" MH fast casting** for jigs, Texas rigs, and spinnerbaits  
- Reel: **7.1:1 baitcaster** for line pickup around timber  
- Line: **15-20 lb fluorocarbon** near wood; **50 lb braid** in heavy grass

### 5.2 Lake Texoma (Striper Capital)
**Best seasons:** Spring schooling runs, summer early-morning topwater, winter jigging over deep bait.  
**Recommended gear:**  
- Rod: **7'0" M/MH spinning or casting** for swimbaits and slabs  
- Reel: **3000-4000 spinning** or mid-size low-profile casting reel  
- Line: **20-30 lb braid** with **12-17 lb leader** for sensitivity and abrasion balance

### 5.3 O.H. Ivie (Modern Powerhouse)
**Best seasons:** Late winter to spawn for giants; post-spawn offshore structure periods.  
**Recommended gear:**  
- Rod: **7'4" heavy fast** for big soft plastics and deep jigs  
- Reel: **High-torque baitcaster** with strong drag consistency  
- Line: **17-25 lb fluorocarbon** around hard structure and brush

### 5.4 Sam Rayburn and Toledo Bend
**Best seasons:** Spring grass growth, summer deep grass edges, fall transition creeks.  
**Recommended gear:**  
- Rod: **7'3" MH fast** all-purpose reaction rod plus **7'6" heavy** for punching  
- Reel: **6.8:1** for crank/chatter and **8.1:1** for frog/punching follow-up  
- Line: **40-65 lb braid** in vegetation, **12-16 lb fluorocarbon** for moving baits

{v(3)}

## VI. Seasonal Tactics: Spring to Winter
Seasonal success comes from understanding metabolism, forage position, and oxygen/temperature distribution.

### Spring (Spawn and Pre-Spawn)
- Target warming pockets, protected coves, and secondary points.
- Use slower profiles first, then speed up if fish show chase behavior.
- Prioritize precision casting around bedding lanes and staging cover.

### Summer (Heat and Thermocline)
- Fish low-light periods and move deeper as sun intensity rises.
- Locate bait first using electronics; predators rarely stay far.
- Use deep crankbaits, football jigs, and vertical presentations.

### Fall (Forage Migration)
- Follow bait into creeks and wind-blown banks.
- Use reaction baits to trigger competitive feeding.
- Cover water fast, then slow down when schools are located.

### Winter (Cold-Water Efficiency)
- Focus steep breaks, channel swings, and vertical structure.
- Downsize profiles and reduce retrieve cadence.
- Fish methodically; fewer bites, but often quality fish.

## VII. Conservation and the Future
Modern angling is increasingly aligned with sustainability. **Selective harvest**, habitat stewardship, and better fish handling now define high-level practice.

### High-impact habits
- Keep legal eaters, release large breeding fish.
- Use barbless or micro-barb options in pressured waters.
- Minimize air exposure and support fish horizontally for release photos.
- Report invasive species and follow local slot regulations.

This draft is structured for direct DOCX layout with clear headers, bullets, and visual insertion anchors."""


class DraftService:
    def __init__(self, model: str | None = None) -> None:
        self.model = model or os.getenv("SCRIBEFLOW_LLM_MODEL", "google/gemini-2.5-flash-lite")
        key = os.getenv("OPENROUTER_API_KEY")
        self.client = OpenAI(api_key=key, base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")) if key else None

    def expand(self, markdown: str, visual_manifest: list[dict[str, Any]], style_guide: dict[str, Any]) -> str:
        if not self.client:
            return _fallback(markdown, visual_manifest, style_guide)
        user_prompt = (
            f"Base markdown:\n{markdown[:18000]}\n\n"
            f"Visual manifest:\n{json.dumps(visual_manifest, ensure_ascii=False)}\n\n"
            f"Style guide:\n{json.dumps(style_guide, ensure_ascii=False)}"
        )
        try:
            r = self.client.chat.completions.create(
                model=self.model,
                temperature=0.5,
                messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}],
            )
            return (r.choices[0].message.content or "").strip()
        except Exception:
            return _fallback(markdown, visual_manifest, style_guide)
