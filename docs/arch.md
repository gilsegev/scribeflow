🏛️ ScribeFlow Architecture: The "Surgical" Model

We will build the app in three clear technical layers to ensure scalability and clean separation from the Visualization App.
Layer	Component	Responsibility
1. Discovery	MarkItDown + ScribeLLM	Converts .docx to Markdown. LLM identifies "High-Cognitive Load" sections and defines the Mood/Palette.
2. Orchestration	VisualManifestService	Generates a JSON manifest of all proposed visuals. Calls the Visualization App's API to generate PNGs sequentially (single-instance).
3. Integration	AnchorPointMerger	PoC: Generates the "Side-by-Side" HTML. Final: Uses python-docx to search for anchor sentences and insert the PNGs into the original doc.