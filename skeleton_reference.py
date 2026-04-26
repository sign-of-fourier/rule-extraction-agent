@ 1. Setup and imports
# install:
# pip install strands-agents strands-agents-tools

from typing import List, Literal, Optional
from pydantic import BaseModel, Field

from strands import Agent
from strands.models import BedrockModel  # or OpenAIModel, etc.
from strands.tools.decorator import tool
This uses the Strands Agent plus the @tool decorator to turn plain Python functions into tools.

2. Define a rule schema
python
class Rule(BaseModel):
    rule_id: str = Field(description="Short stable id, e.g. RULE_001")
    source_span: str = Field(
        description="Exact text span from the document that expresses this rule"
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
        description="Model confidence that this rule is correctly extracted",
    )
    section_id: Optional[str] = Field(
        default=None,
        description="Logical section or heading where the rule was found",
    )
Using a Pydantic model gives you typed, validated structured output and matches Strands’ structured-output pattern.

3. Chunking / preprocessing tool
python
@tool
def chunk_document(text: str, max_chars: int = 4000) -> List[str]:
    """
    Split a long document into smaller chunks for rule extraction.

    Args:
        text: Full document text.
        max_chars: Maximum characters per chunk.
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
            buf = []
            current_len = 0
        buf.append(line)
        current_len += len(line) + 1

    if buf:
        chunks.append("\n".join(buf))

    return chunks
This is a basic text chunker exposed as a tool; the Strands runtime can decide when to call it.

4. Rule extraction tool (LLM-facing)
python
@tool
def extract_rules_from_chunk(chunk: str) -> List[Rule]:
    """
    Extract structured rules from a single document chunk.

    Args:
        chunk: A section of the document text.

    Returns:
        A list of Rule objects representing obligations, prohibitions,
        permissions, and recommendations found in this chunk.
    """
    # NOTE: This function body is just a placeholder. In practice you will
    # call an LLM with a strong system prompt and JSON schema instructions.
    #
    # In Strands, the agent itself typically calls tools; the LLM reasons
    # about when/how to use this tool based on the docstring + type hints.
    #
    # For a first skeleton, we leave implementation to the agent prompt.
    return []
By decorating this function, Strands generates a tool spec (name, description, parameter schema) that the model can use for tool calls.

In a real implementation you would either:

Have the agent call an LLM directly and then parse JSON into Rule, or

Use Strands’ structured-output / tool-calling behavior so the model calls this tool and returns properly typed Rule objects.

5. Aggregation / post-processing tool
python
@tool
def merge_and_deduplicate_rules(rules_per_chunk: List[List[Rule]]) -> List[Rule]:
    """
    Merge rule lists from multiple chunks and deduplicate them.

    Args:
        rules_per_chunk: A list where each element is the list of rules
            extracted from a single chunk.
    """
    flat: List[Rule] = [r for sub in rules_per_chunk for r in sub]

    deduped: dict[tuple[str, str, str], Rule] = {}
    for r in flat:
        key = (r.actor.strip().lower(), r.condition.strip().lower(), r.action.strip().lower())
        if key not in deduped:
            deduped[key] = r
        else:
            # keep the higher confidence rule
            if r.confidence > deduped[key].confidence:
                deduped[key] = r

    return list(deduped.values())
This lets the model call a tool to clean up its own extraction across chunks instead of you hand-wiring everything.

6. Define the rule extraction agent
python
RULE_SYSTEM_PROMPT = """
You are a rule extraction assistant.

Goal:
- Read technical or policy documents and extract explicit, text-grounded rules.
- Focus on obligations, prohibitions, permissions, and recommendations.
- For each rule, always include:
  - actor (who the rule applies to)
  - condition (trigger, including thresholds and durations)
  - action (what must or must not be done)
  - modality (must, must_not, may, should)
  - exception (if any)
  - exact source_span copied from the text
  - a confidence score in [0, 1].

Guidelines:
- Prefer many small, precise rules over a few vague ones.
- Never invent rules not supported by the source text.
- If the text is ambiguous, include that explicitly in the rule or lower confidence.
"""

bedrock_model = BedrockModel(
    model_id="us.amazon.nova-pro-v1:0",
    temperature=0.1,
)

rule_agent = Agent(
    model=bedrock_model,
    system_prompt=RULE_SYSTEM_PROMPT,
    tools=[
        chunk_document,
        extract_rules_from_chunk,
        merge_and_deduplicate_rules,
    ],
)
This mirrors the Strands quickstart pattern: define a model, a system prompt, and a list of tools the agent can call.

7. Simple usage wrapper
python
def extract_rules_from_document(doc_text: str) -> List[Rule]:
    """
    High-level convenience function that runs the rule agent on raw text.
    """
    # You can either:
    # - Let the agent decide when to call chunking/extraction/merge tools, or
    # - Guide it with a more explicit input instruction.
    response = rule_agent(
        "Extract all rules from the following document and return them as a JSON array "
        "of Rule objects.\n\nDOCUMENT:\n" + doc_text
    )

    # Depending on how you configure structured output, you may get back
    # already-parsed Rule instances or JSON you parse into Rule.
    #
    # For a skeleton, we just return the raw response and refine later.
    return response
The final step is to tighten the prompt so the model reliably uses chunk_document → extract_rules_from_chunk → merge_and_deduplicate_rules, which fits Strands’ “agent + tools” flow.


