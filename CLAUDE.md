# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment

Python 3.12 with a local virtual environment at `.venv/`. Always activate before running anything:

```bash
source .venv/bin/activate
```

Install / sync dependencies:

```bash
pip install strands-agents strands-agents-tools
```

## Running the agent

```bash
python rule_extraction_agent.py          # runs the built-in smoke test against _SAMPLE_DOC
```

The agent requires AWS credentials in the environment (used by `BedrockModel` via boto3). The model is `us.amazon.nova-pro-v1:0` in us-east-1 by default.

## Architecture

The file `rule_extraction_agent.py` is the entire codebase. It implements a two-level Strands agent pipeline:

```
extract_rules_from_document(doc_text)
        │
        ▼
   rule_agent  (orchestrator)
   ├── chunk_document          → splits text into ≤4000-char line-boundary chunks
   ├── extract_rules_from_chunk → calls _chunk_agent (sub-agent) per chunk → List[Rule]
   └── merge_and_deduplicate_rules → deduplicates by (actor, condition, action), re-numbers IDs
```

**Two agents, one concern each:**

- `rule_agent` — the orchestrator. Receives the full document and is prompted to call the three tools in a fixed order: chunk → extract (once per chunk) → merge.
- `_chunk_agent` — a focused sub-agent called inside `extract_rules_from_chunk`. Its system prompt instructs it to return *only* a bare JSON array with no prose. Temperature 0.1 for both.

**Tool discovery:** Strands generates tool specs (name, description, JSON schema) from the `@tool`-decorated functions' docstrings and type hints. The orchestrator LLM sees these specs and decides when to call each tool.

**Structured output contract:** `Rule` is a Pydantic `BaseModel`. The sub-agent returns raw JSON; `_parse_rules_from_response` extracts the first `[…]` array from the response string and constructs `Rule` objects, skipping any malformed entries rather than raising.

**Deduplication key:** `(actor.lower(), condition.lower(), action.lower())`. When two rules share a key, the higher-confidence one is kept. Rule IDs (`RULE_001`, `RULE_002`, …) are reassigned sequentially after merging, so they are always stable and gapless in the final output.

## Calling the tools directly (without AWS)

The `@tool` decorator wraps functions as `DecoratedFunctionTool`. To call the underlying Python function in tests or scripts, use `._tool_func(...)`:

```python
from rule_extraction_agent import chunk_document, merge_and_deduplicate_rules

chunks = chunk_document._tool_func("some long text...", max_chars=500)
merged = merge_and_deduplicate_rules._tool_func([[rule1, rule2], [rule3]])
```

## Sample documents

`sample_docs.py` contains ready-to-use test documents:

| Constant | Domain | Notes |
|---|---|---|
| `SLA_DOCUMENT` | Cloud service SLA | Original dev/smoke-test document |
| `GENERIC_LIFE_UNDERWRITING_DOCUMENT` | Life insurance underwriting | Out-of-domain benchmark document (29 clauses, 6 sections) |
| `LIFE_INSURANCE_UNDERWRITING_DOCUMENT` | Detailed life insurance underwriting | Longer synthetic document (~100 rules) |

Example runners: `example.py`, `example_generic_underwriting.py`, `example_life_insurance.py`.

## Benchmarking

A silver-labeled dataset and scorer exist for `GENERIC_LIFE_UNDERWRITING_DOCUMENT`:

```bash
python score.py                                       # run agent + score
python score.py --dry-run benchmarks/last_run.json   # rescore without re-running
python score.py --threshold 0.20                      # tune match threshold
```

Silver labels: `benchmarks/generic_life_underwriting_silver.json` (29 hand-labeled rules).

The scorer uses greedy bipartite matching on Jaccard word-overlap of the `action` field (default threshold 0.30) and reports precision, recall, F1, and per-modality accuracy. Each live run saves output to `benchmarks/last_run.json`.

Latest results: **F1 = 0.90, modality accuracy = 1.00**. See `BENCHMARK_RESULTS.md` for full analysis.

## Key design constraints

- `source_span` must always be a verbatim copy from the input text — the sub-agent prompt enforces this.
- `modality` is a closed enum: `"must"`, `"must_not"`, `"may"`, `"should"`. Pydantic validates this at parse time.
- The orchestrator system prompt explicitly names the three-step workflow so the model reliably follows `chunk → extract → merge` rather than attempting to extract rules inline.
