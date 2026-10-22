# Context

What the model sees on a call is all it knows. Each call is built in this order, stable parts first so the provider can cache them:

1. Role and rules (docs/PROMPT_CONTRACT.md)
2. Examples
3. Knowledge: None
4. Memory: Full history
5. The request

## Sources
- None.

## Caching
- No caching.

## Budget per call (estimate)
| AI feature | Input tokens | Of which knowledge | Output tokens | Calls per use | Model window |
|---|---|---|---|---|---|
| Gap Analysis | 680 | 0 | 300 | 1 | ? |
| Title Suggestions | 680 | 0 | 300 | 1 | ? |
| Deep-Dive Search | 680 | 0 | 300 | 1 | ? |
| Objectives & Methodology | 680 | 0 | 300 | 1 | ? |
