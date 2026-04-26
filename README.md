# Rule Extraction Agent

Extracts structured, typed rules from business documents (policies, SLAs, contracts) using a two-level [Strands Agents](https://strandsagents.com) pipeline backed by Amazon Bedrock.

Each rule is returned as a typed object with actor, condition, action, obligation strength (must / must_not / may / should), exceptions, a verbatim source quote, a confidence score, and a functional topic label for filtering.

## Prerequisites

- Python 3.10+
- AWS credentials with Bedrock access (model: `us.amazon.nova-pro-v1:0`, region `us-east-1`)

Verify your credentials:

```bash
aws sts get-caller-identity
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install strands-agents strands-agents-tools
```

## Run the built-in demo

`example.py` runs the agent against a sample Cloud Service SLA document that covers availability, incident response, data handling, security, and support rules.

```bash
source .venv/bin/activate
python example.py
```

Expected output (abbreviated):

```
Extracted 22 rules

ID         Modality   Actor                     Action
------------------------------------------------------------------------------------------
RULE_001   must       provider                  maintain a monthly uptime of 99.9% for all product
RULE_002   must_not   provider                  not exceed 4 hours per month and be announced at l
RULE_003   must       provider                  notify the customer within 15 minutes
RULE_006   must       on-call engineer          post a status update every 30 minutes until resolu
RULE_009   must_not   provider                  not store customer data outside the geographic reg
RULE_019   may        customer                  submit support requests via the ticketing portal o
...

── Full detail for first 3 rules ──

{
  "rule_id": "RULE_001",
  "source_span": "The provider must maintain a monthly uptime of 99.9% for all production services...",
  "actor": "provider",
  "condition": "monthly",
  "action": "maintain a monthly uptime of 99.9% for all production services",
  "modality": "must",
  "exception": null,
  "confidence": 1.0,
  "section_id": null,
  "rule_type": "availability"
}
```

## Use on your own document

```python
from rule_extraction_agent import extract_rules_from_document

text = open("your_policy.txt").read()
rules = extract_rules_from_document(text)

for r in rules:
    print(r.model_dump_json(indent=2))
```

The returned `Rule` objects are Pydantic models — you can filter, sort, or serialize them however you like:

```python
# Only hard obligations
must_rules = [r for r in rules if r.modality == "must"]

# Filter by topic
security_rules = [r for r in rules if r.rule_type == "security"]

# Export to JSON file
import json
with open("rules.json", "w") as f:
    json.dump([r.model_dump() for r in rules], f, indent=2)
```

## Rule schema

| Field | Type | Description |
|---|---|---|
| `rule_id` | `str` | Sequential ID: `RULE_001`, `RULE_002`, … |
| `source_span` | `str` | Verbatim quote from the source document |
| `actor` | `str` | Who the rule applies to |
| `condition` | `str` | Trigger or precondition |
| `action` | `str` | What must / must not happen |
| `modality` | `must` \| `must_not` \| `may` \| `should` | Obligation strength |
| `exception` | `str \| None` | Documented override or carve-out |
| `confidence` | `float` 0–1 | Certainty that the extraction is correct (not business importance) |
| `section_id` | `str \| None` | Section heading where the rule was found |
| `rule_type` | `str \| None` | Functional topic: availability, security, data_handling, incident_response, support, access_control, compliance |

## How it works

```
extract_rules_from_document(text)
         │
         ├─ chunk_document()              split into ≤2000-char chunks with 2-line overlap
         │
         ├─ extract_rules_from_chunk()    fresh sub-agent per chunk, structured_output_model=RuleList
         │   (once per chunk)             → validated List[Rule] with no JSON parsing
         │
         └─ merge_and_deduplicate_rules() normalize + dedup on (actor, condition, action, modality)
                                          re-number IDs sequentially
```

The LLM is only invoked inside `extract_rules_from_chunk`. Each call creates a fresh agent (no conversation history bleed) with `structured_output_model=RuleList`, which forces the model to populate a validated Pydantic schema via a generated tool call rather than returning free text. Chunking and merging are pure Python.

Chunk overlap (2 lines by default) ensures rules at chunk boundaries appear in both extraction calls and are caught even when a condition and its verb land in different chunks. Dedup normalization (lowercase, strip punctuation, collapse whitespace) collapses near-duplicates introduced by the overlap before the key comparison.

## Files

| File | Purpose |
|---|---|
| `rule_extraction_agent.py` | Agent, tools, `Rule` schema, public API |
| `example.py` | Runnable demo with a sample SLA document |
| `skeleton_reference.py` | Original design skeleton for reference |

## Background & theory

**Deontic modalities.** The `modality` field is a direct engineering encoding of the classical operators of *deontic logic* — the branch of modal logic that formalises normative language. Von Wright's foundational paper introduced obligation (O), permission (P), and prohibition (¬P) as primitive operators \[1\]. The four-value vocabulary used here (`must`, `must_not`, `may`, `should`) corresponds to those operators and is also the vocabulary standardised in IETF RFC 2119 for technical specifications \[2\].

**Normative language extraction.** Identifying deontic statements in natural-language documents is an active sub-field of information extraction. Key benchmarks include CUAD (expert-labelled legal contract clauses) \[3\] and ContractNLI (document-level NLI for contracts) \[4\]. These datasets highlight the same challenge this agent faces: normative force is often implicit (passive constructions, nominalisations) and clause boundaries are blurry — which is why confidence scoring and verbatim `source_span` anchoring matter.

**Structured output from LLMs.** Rather than parsing free-form text from the model, the extraction sub-agent uses constrained generation (`structured_output_model=RuleList`). This approach follows Willard & Louf's efficient guided generation \[5\], which steers token sampling to stay within a schema-defined grammar, eliminating ad-hoc JSON repair and validation loops.

**Map-reduce chunking.** Long documents exceed a single LLM context window, so the pipeline follows a *map-reduce* pattern: split into overlapping chunks (map), extract per chunk (map), merge and deduplicate (reduce). The two-line overlap at chunk boundaries is a sliding-window heuristic that prevents rules straddling a boundary from being missed — a technique discussed in the context of retrieval-augmented generation \[6\].

**Agentic tool use.** The orchestrator–subagent architecture follows the ReAct paradigm \[7\], in which an LLM interleaves reasoning steps with tool calls. Here the orchestrator is explicitly constrained to a fixed three-step workflow (chunk → extract → merge), trading open-ended planning flexibility for reliability and auditability.

**Strands Agents.** The pipeline is implemented with [Strands Agents](https://strandsagents.com), an open-source Python SDK from AWS that handles tool registration, schema generation, and model dispatch. Tool specs (name, description, JSON schema) are derived automatically from `@tool`-decorated functions' type hints and docstrings, so there is no hand-written glue between the Python functions and the LLM's tool-call interface.

### References

1. Von Wright, G. H. (1951). Deontic Logic. *Mind*, 60(237), 1–15.
2. Bradner, S. (1997). Key words for use in RFCs to Indicate Requirement Levels. *IETF RFC 2119*.
3. Hendrycks, D., et al. (2021). CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review. *NeurIPS 2021 Datasets and Benchmarks Track*. arXiv:2103.06268.
4. Koreeda, Y., & Manning, C. D. (2021). ContractNLI: A Dataset for Document-level Natural Language Inference for Contracts. *Findings of EMNLP 2021*. arXiv:2110.01799.
5. Willard, B. T., & Louf, R. (2023). Efficient Guided Generation for Large Language Models. arXiv:2307.09702.
6. Lewis, P., et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. *NeurIPS 2020*. arXiv:2005.11401.
7. Yao, S., et al. (2022). ReAct: Synergizing Reasoning and Acting in Language Models. *ICLR 2023*. arXiv:2210.03629.
