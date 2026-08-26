# Extraction pipeline

The compile plane is deliberately separate from runtime evaluation. It turns public statutory text into reviewable candidate rules; it never decides a real-world request.

Implemented stages are deterministic snapshot normalization and hashing, offset-preserving segmentation, definition extraction, dual-proposal structural comparison, pre-review mechanical gates, review prioritization, and reproducible L3 metric calculation.

Provider calls are injected into the proposal interface rather than embedded in the library. This makes every request/response capture and model version an explicit artifact, prevents an API key from becoming a runtime dependency, and keeps the evaluator offline.

No live extraction accuracy or held-out results have been published. Those require two configured model providers, a sealed held-out corpus opened exactly once, and independent human review. Until then, this repository makes no performance claim for model-assisted extraction.
