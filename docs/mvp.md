Project Overview: ScribeFlow

ScribeFlow is a "Visual Instruction Engine" designed to bridge the gap between complex written curriculum and visual comprehension. Unlike generic design tools, ScribeFlow uses deep pedagogical reasoning to transform raw text into a structured, visual-first learning experience.
1. Core Functionality

The app automates the end-to-end workflow of document-to-visual conversion:

    Deep Extraction: Ingests complex documents (starting with .docx) and converts them into structured Markdown to preserve pedagogical hierarchy.

    Pedagogical Analysis: An LLM-based "Visual Architect" analyzes the text to identify high-cognitive-load sections that require visualization.

    Dual-Path Generation: * Infographics: Generates structured data visualizations (Bento grids, Versus splits, Step journeys) using verified HTML/CSS templates.

        Narrative Heroes: Generates high-fidelity "Story Images" (1400×900px) that set the mood and semantic context of the lesson.

    Surgical Insertion: Re-integrates the generated art back into the original document at the exact semantic "anchor points" where the learning occurs.

2. The MVP (Minimum Viable Product)

The current focus is on building a robust, observable pipeline that demonstrates the "Intelligence" of the system before scaling to full document automation.

    Input: User uploads a .docx file.

    The Blueprint: The system generates a Visual Manifest (JSON) detailing what will be visualized and why, alongside an auto-generated Style Guide derived from the document's "spirit."

    The PoC Output: A "Companion HTML" view showing the original text on the left and generated artifacts on the right, pinned to their respective paragraphs.

    Final Output: A new version of the .docx file with the high-res PNGs surgically inserted.

    Metric: 10 pages of content processed into a visual curriculum in under one minute.

3. High-Level Architecture & Layer Model

The app is built as a separate service from the core Visualization Engine, communicating via a structured JSON payload to maintain loose coupling.
Layer	Component	Responsibility
I. Discovery	MarkItDown + ScribeLLM	Locally converts .docx → Markdown. LLM extracts pedagogical triggers and "Mood."
II. Orchestration	VisualManifestService	Creates the JSON blueprint. Manages the generation queue (Parallel/Sequential) for the Visualization API.
III. Generation Gate	CLIP + Vision LLM	Local CLIP ranks search candidates; GPT-4o performs the final "Aesthetic Pass" for style-locking.
IV. Integration	AnchorPointMerger	Uses python-docx to search for anchor sentences and insert images into the source stream.
V. Observability	PerformanceDashboard	Logs extraction status, queue wait times (p-limit), generation latency, and quality scores.
4. Design Principles for the Agent

    Determinism over Randomness: Use templates and strict style-locking (hex codes) to ensure a "Wellness Book" aesthetic—calm, non-corporate, and grounded.

    Pedagogical Soundness: Every visual must serve a learning principle (e.g., Dual Coding or Signaling). If a visual doesn't add clarity, it is refused.

    Fail-Fast Resilience: Implement strict schema validation and exponential backoff for external API calls (SiliconFlow, OpenRouter).

    Local-First: Prioritize local processing for document extraction and final .docx assembly to minimize latency and costs.