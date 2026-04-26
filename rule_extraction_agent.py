"""Rule extraction agent built with Strands Agents."""

from __future__ import annotations

import re
from typing import List, Literal, Optional

from pydantic import BaseModel, Field
from strands import Agent
from strands.models import BedrockModel
from strands.tools.decorator import tool


# ── Schema ─────────────────────────────────────────────────────────────────────

class Rule(BaseModel):
    rule_id: str = Field(description="Short stable id, e.g. RULE_001")
    source_span: str = Field(
        description="Exact verbatim quote from the document — copy-paste only, no paraphrase"
    )
    actor: str = Field(description="Who the rule applies to (person/system/role)")
    condition: str = Field(
        description="Preconditions/trigger, including thresholds and timing"
    )
    action: str = Field(description="Required or forbidden action")
    modality: Literal["must", "must_not", "may", "should"] = Field(
        description="Obligation strength"
    )
    exception: Optional[str] = Field(
        default=None,
        description="Documented exceptions or overrides if any",
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "Model certainty that this rule is correctly extracted "
            "(extraction accuracy, not business importance)"
        ),
    )
    section_id: Optional[str] = Field(
        default=None,
        description="Logical section or heading where the rule was found",
    )
    rule_type: Optional[str] = Field(
        default=None,
        description=(
            "Functional topic for downstream filtering, e.g. availability, "
            "security, data_handling, incident_response, support, "
            "access_control, compliance"
        ),
    )


class RuleList(BaseModel):
    """Structured output container for a single chunk's extracted rules."""
    rules: List[Rule]


# ── Extraction sub-agent ───────────────────────────────────────────────────────
# Separate from the orchestrator so its prompt stays focused and temperature
# can be tuned independently. structured_output_model=RuleList means Strands
# forces the model to call a generated tool that validates against the schema,
# eliminating manual JSON parsing and schema repair.

_CHUNK_SYSTEM_PROMPT = """\
You are a rule extraction specialist. Extract every explicit normative statement
from the document chunk — obligations, prohibitions, permissions, and
recommendations.

Rules for extraction:
- Extract only explicit statements; do not infer unstated actors or obligations.
- source_span must be a verbatim copy-paste from the input text, kept short
  (the triggering sentence or clause only).
- actor: the specific role, system, or party the rule applies to.
- condition: the trigger, threshold, or precondition that activates the rule.
- action: what must or must not happen (use positive phrasing even for must_not).
- modality: "must" for obligations, "must_not" for prohibitions, "may" for
  permissions, "should" for recommendations.
- exception: any documented override or carve-out stated in the same sentence
  or clause; null otherwise.
- confidence: your certainty that the extraction is correct (0.0–1.0). Lower it
  when the text is ambiguous, not when the rule seems unimportant.
- rule_type: assign a short topic label (availability, security, data_handling,
  incident_response, support, access_control, compliance, or other).
- If the chunk contains no normative statements, return an empty rules list.
"""

_chunk_model = BedrockModel(
    model_id="us.amazon.nova-pro-v1:0",
    temperature=0.1,
    max_tokens=5120,
)


def _make_chunk_agent() -> Agent:
    # Fresh agent per call — Agent instances accumulate conversation history,
    # so reusing a global causes context bleed between chunks.
    return Agent(
        model=_chunk_model,
        system_prompt=_CHUNK_SYSTEM_PROMPT,
        structured_output_model=RuleList,
    )


# ── Normalization helpers ──────────────────────────────────────────────────────

_PUNCT_RE = re.compile(r"[^\w\s]")
_WS_RE = re.compile(r"\s+")

def _normalize(text: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace for dedup comparison."""
    text = _PUNCT_RE.sub(" ", text.lower())
    return _WS_RE.sub(" ", text).strip()


# ── Tools ──────────────────────────────────────────────────────────────────────

@tool
def chunk_document(text: str, max_chars: int = 2000, overlap_lines: int = 2) -> List[str]:
    """
    Split a long document into overlapping line-boundary chunks.

    Each chunk ends on a line boundary. The first `overlap_lines` lines of
    each previous chunk are prepended to the next one so rules that straddle
    a boundary are visible to both extraction calls.

    Args:
        text: Full document text.
        max_chars: Maximum characters per chunk (default 2000).
        overlap_lines: Lines carried over from the previous chunk (default 2).
    """
    chunks: List[str] = []
    buf: List[str] = []
    current_len = 0

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if current_len + len(line) + 1 > max_chars and buf:
            chunks.append("\n".join(buf))
            buf = buf[-overlap_lines:] if overlap_lines else []
            current_len = sum(len(l) + 1 for l in buf)
        buf.append(line)
        current_len += len(line) + 1

    if buf:
        chunks.append("\n".join(buf))

    return chunks


@tool
def extract_rules_from_chunk(chunk: str) -> List[Rule]:
    """
    Extract structured rules from a single document chunk.

    Uses a focused sub-agent with structured_output_model=RuleList so the
    model is forced to populate a validated Pydantic schema rather than
    returning free text. Rules cover obligations (must), prohibitions
    (must_not), permissions (may), and recommendations (should).

    Args:
        chunk: A section of the document text.

    Returns:
        A list of Rule objects found in this chunk.
    """
    result = _make_chunk_agent()(
        f"Extract all normative rules from this document chunk:\n\n{chunk}"
    )
    if result.structured_output:
        return result.structured_output.rules
    return []


@tool
def merge_and_deduplicate_rules(rules_per_chunk: List[List[Rule]]) -> List[Rule]:
    """
    Merge rule lists from multiple chunks, deduplicate, and re-number IDs.

    Deduplication key: normalized (actor, condition, action, modality).
    Including modality prevents collapsing rules that share text but differ in
    obligation strength. Normalization (lowercase, strip punctuation, collapse
    whitespace) catches near-duplicates caused by superficial wording changes
    in overlapping chunk regions. When two entries share a key, the one with
    higher confidence is kept. IDs are reassigned as RULE_001, RULE_002, …
    after merging so they are always stable and sequential.

    Args:
        rules_per_chunk: One sub-list of rules per document chunk.
    """
    flat: List[Rule] = [r for sub in rules_per_chunk for r in sub]

    deduped: dict[tuple[str, str, str, str], Rule] = {}
    for r in flat:
        key = (
            _normalize(r.actor),
            _normalize(r.condition),
            _normalize(r.action),
            r.modality,
        )
        if key not in deduped or r.confidence > deduped[key].confidence:
            deduped[key] = r

    merged = list(deduped.values())
    for i, rule in enumerate(merged, 1):
        rule.rule_id = f"RULE_{i:03d}"

    return merged


# ── Orchestrator agent ─────────────────────────────────────────────────────────

_RULE_SYSTEM_PROMPT = """\
You are a rule extraction assistant. Your job is to read policy or technical
documents and return a clean, structured list of rules.

Workflow — follow these steps in order every time:
1. Call chunk_document to split the input into manageable pieces.
2. Call extract_rules_from_chunk once for EACH chunk (do not skip any).
3. Call merge_and_deduplicate_rules once with ALL per-chunk results combined.
4. Return the final merged rule list as a JSON array.

Rule quality standards:
- Prefer many small, precise rules over a few vague ones.
- source_span must be copied verbatim from the original text.
- Never invent rules not supported by the source text.
- For ambiguous phrasing, lower confidence and note the ambiguity in condition.
- modality: "must" (obligation), "must_not" (prohibition),
  "may" (permission), "should" (recommendation).
"""

rule_agent = Agent(
    model=BedrockModel(model_id="us.amazon.nova-pro-v1:0", temperature=0.1),
    system_prompt=_RULE_SYSTEM_PROMPT,
    tools=[chunk_document, extract_rules_from_chunk, merge_and_deduplicate_rules],
)


# ── Public API ─────────────────────────────────────────────────────────────────

def extract_rules_from_document(doc_text: str) -> List[Rule]:
    """
    Run the full extraction pipeline on raw document text.

    Orchestrates the three tools directly in Python. The LLM is only invoked
    inside extract_rules_from_chunk (via _make_chunk_agent), where it adds
    value; chunking and merging are deterministic and need no LLM.

    Returns a deduplicated, sequentially numbered list of Rule objects.
    """
    chunks = chunk_document._tool_func(doc_text)
    rules_per_chunk = [extract_rules_from_chunk._tool_func(c) for c in chunks]
    return merge_and_deduplicate_rules._tool_func(rules_per_chunk)


# ── Smoke test ─────────────────────────────────────────────────────────────────

_SAMPLE_DOC = """\
Data Retention Policy v2.3
Section 3 – Storage and Deletion

3.1  All user data must be encrypted at rest using AES-256 or stronger.

3.2  The data controller must delete personal data within 30 days of a verified
deletion request, except where retention is required by applicable law.

3.3  Employees may access customer records only when responding to an active
support ticket. Browsing records without a linked ticket is prohibited.

3.4  Automated backups should be performed daily and retained for 90 days.
Backups older than 90 days must be permanently destroyed.

3.5  In the event of a confirmed data breach, the security team must notify
affected users within 72 hours of discovery.
"""

if __name__ == "__main__":
    rules = extract_rules_from_document(_SAMPLE_DOC)
    print(f"Extracted {len(rules)} rules\n")
    for r in rules:
        print(r.model_dump_json(indent=2))
        print()
