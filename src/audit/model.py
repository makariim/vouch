"""The three model calls, behind one small interface.

Why an interface at all: decision 0002 allows exactly one outbound call, the
model call. Putting all three behind `Model` means there is a single place to
audit for network access, and it lets the tests drive the whole graph with a
scripted stand-in -- no key, no network, no cost.

Structured outputs (`output_format=<pydantic model>`) is used instead of asking
for JSON in the prompt and parsing it. The API constrains the response to the
schema, so a malformed reply is not a failure mode we have to handle.

Two providers sit behind `Model`: `AnthropicModel`, which the code was written
against, and `GroqModel`, which is the one with a key. `build_model()` picks
between them from the environment. The prompts are module-level and shared, so
the two differ in transport and in nothing else.
"""

from __future__ import annotations

import json
import os
from typing import Literal, Protocol

from pydantic import BaseModel, Field

from .index import Line

PROVIDER = os.environ.get("AUDIT_PROVIDER", "groq")
MODEL_ID = os.environ.get("AUDIT_MODEL", "claude-opus-5")
GROQ_MODEL_ID = os.environ.get("AUDIT_GROQ_MODEL", "openai/gpt-oss-120b")


class Extraction(BaseModel):
    """What extract asks the model for."""

    requirements: list[str] = Field(
        description="Each discrete requirement, copied character for character from the post."
    )


class Query(BaseModel):
    """The agent choosing how to look. Decision 0001 calls this out as the
    decision nobody told it to make, so it is its own call with its own event."""

    query: str = Field(description="Keywords to search the resume with.")
    reason: str = Field(description="One short clause on why these terms.")


class Judgement(BaseModel):
    # A Literal, not a str: it becomes an enum in the JSON schema the API is
    # constrained to, so a fourth verdict cannot come back. Structural, not a
    # rule we ask the prompt to keep.
    verdict: Literal["evidenced", "partly_evidenced", "not_evidenced"] = Field(
        description="evidenced, partly_evidenced, or not_evidenced."
    )
    line_number: int | None = Field(
        default=None,
        description="Line number of the single best supporting line, or null if none.",
    )
    line: str | None = Field(
        default=None, description="That line's text, copied exactly, or null."
    )
    reason: str = Field(description="One sentence.")
    evidence_weak: bool = Field(
        default=False,
        description="True if a different search might turn up better evidence.",
    )


class Model(Protocol):
    def extract(self, post: str) -> Extraction: ...

    def choose_query(
        self, requirement: str, tried: list[str], seen: list[Line]
    ) -> Query: ...

    def judge(self, requirement: str, lines: list[Line]) -> Judgement: ...


_EXTRACT_SYSTEM = """You read job posts and list the discrete requirements.

Rules:
- Copy each requirement from the post CHARACTER FOR CHARACTER. Do not paraphrase,
  summarise, tidy up punctuation, or expand abbreviations.
- Split a sentence that asks for two separate things into two requirements.
- Do not merge two requirements into one.
- Skip company blurb, benefits, equal-opportunity text and application
  instructions. Only what the candidate is being asked to have or do.
- Invent nothing. If it is not in the post, it is not a requirement."""

_QUERY_SYSTEM = """You search a resume for evidence of one job requirement.

Return the keywords you want to search with. You are searching a plain keyword
index over resume lines, so give concrete terms likely to appear in a resume
(tools, languages, job titles, actions) rather than a question or a sentence.

If earlier searches were already tried, choose DIFFERENT terms -- a synonym, the
underlying skill, or a tool someone would name instead."""

_JUDGE_SYSTEM = """You decide whether a resume evidences one job requirement,
using only the resume lines you are given.

Exactly one of three verdicts:
- evidenced: a line clearly shows the requirement is met.
- partly_evidenced: a line shows part of it -- the skill but not the years, the
  tool but not the scale, adjacent but not the same thing.
- not_evidenced: nothing among these lines supports it.

Rules:
- Quote at most ONE line, and copy it exactly as given, with its line number.
- not_evidenced with no line is a correct answer. Do not stretch a weak line to
  avoid it.
- Never quote a line you were not given.
- Set evidence_weak when you suspect the resume says something relevant that
  these particular search terms missed."""


def _query_prompt(requirement: str, tried: list[str], seen: list[Line]) -> str:
    parts = [f"Requirement: {requirement}"]
    if tried:
        parts.append("Search terms already tried: " + "; ".join(tried))
    if seen:
        parts.append(
            "What those turned up (judged too weak):\n"
            + "\n".join(f"  line {ln.number}: {ln.text}" for ln in seen)
        )
    parts.append("Give the search terms to try now.")
    return "\n\n".join(parts)


def _judge_prompt(requirement: str, lines: list[Line]) -> str:
    if lines:
        body = "\n".join(f"line {ln.number}: {ln.text}" for ln in lines)
    else:
        body = "(the search returned no lines)"
    return (
        f"Requirement: {requirement}\n\nResume lines retrieved:\n{body}\n\n"
        "Give your verdict."
    )


class AnthropicModel:
    """The real model. The only thing in this project that touches the network."""

    def __init__(self, client=None, model_id: str = MODEL_ID) -> None:
        import anthropic

        self.client = client or anthropic.Anthropic()
        self.model_id = model_id

    def _parse(self, system: str, prompt: str, schema: type[BaseModel]):
        response = self.client.messages.parse(
            model=self.model_id,
            max_tokens=16000,
            system=system,
            messages=[{"role": "user", "content": prompt}],
            output_format=schema,
        )
        return response.parsed_output

    def extract(self, post: str) -> Extraction:
        return self._parse(
            _EXTRACT_SYSTEM,
            f"Job post:\n\n{post}\n\nList the requirements, each copied verbatim.",
            Extraction,
        )

    def choose_query(self, requirement: str, tried: list[str], seen: list[Line]) -> Query:
        return self._parse(_QUERY_SYSTEM, _query_prompt(requirement, tried, seen), Query)

    def judge(self, requirement: str, lines: list[Line]) -> Judgement:
        return self._parse(_JUDGE_SYSTEM, _judge_prompt(requirement, lines), Judgement)


# The two Groq models that offer constrained decoding. Groq offers it for these
# and nothing else today, so the list is short and it is ours: langchain-groq
# keeps the same set privately and silently ignores strict=True off it, which
# would turn a real weakening into a thing nobody noticed. Named here so the
# downgrade is a branch we take on purpose.
_SCHEMA_CONSTRAINED = frozenset({"openai/gpt-oss-120b", "openai/gpt-oss-20b"})


def _json_mode_tail(schema: type[BaseModel]) -> str:
    """What JSON mode needs and constrained decoding does not: the schema, in
    the prompt, because nothing is holding the reply to it."""
    return (
        "Reply with one JSON object and nothing else -- no prose, no code fence.\n"
        "It must match this JSON schema exactly:\n"
        + json.dumps(schema.model_json_schema(), indent=2)
    )


class GroqModel:
    """The same three calls, against Groq. The only key we have (standing brief).

    Why `langchain-groq` and not the `groq` SDK: LangChain core is already in
    the tree underneath LangGraph, so this costs two packages rather than a
    second ecosystem, and `with_structured_output` gives the same
    schema-in, model-out shape `AnthropicModel` gets from `messages.parse`.

    Why the model id matters more than usual here. Groq offers constrained
    decoding (`method="json_schema"`, `strict=True`) on the two gpt-oss models
    only. On those, `Judgement.verdict` is an `enum` in the schema the API is
    held to, so a fourth verdict cannot come back -- structurally, the same
    guarantee `AnthropicModel` has. On any other model that drops to JSON mode
    plus Pydantic validation after the fact, which is a weaker thing: the
    reply is checked rather than constrained. `self.constrained` records which
    of the two is in force so it can be reported rather than assumed.
    """

    def __init__(self, client=None, model_id: str = GROQ_MODEL_ID) -> None:
        from langchain_groq import ChatGroq

        self.model_id = model_id
        self.constrained = model_id in _SCHEMA_CONSTRAINED
        # Counts replies that failed validation and were asked again. Zero on
        # the constrained path by construction. Distinct from the graph's
        # retry, which is about weak evidence, not malformed JSON.
        self.validation_retries = 0
        self.client = client or ChatGroq(
            model=model_id, temperature=0, max_tokens=16000
        )

    def _parse(self, system: str, prompt: str, schema: type[BaseModel]):
        if self.constrained:
            runnable = self.client.with_structured_output(
                schema, method="json_schema", strict=True
            )
        else:
            runnable = self.client.with_structured_output(schema, method="json_mode")
            system = f"{system}\n\n{_json_mode_tail(schema)}"

        messages = [("system", system), ("human", prompt)]
        try:
            return runnable.invoke(messages)
        except Exception as exc:
            # A constrained reply that does not validate is a broken promise,
            # not a bad draft. Asking again would hide it.
            if self.constrained:
                raise
            self.validation_retries += 1
            return runnable.invoke(
                messages
                + [
                    (
                        "human",
                        f"That reply did not fit the schema ({exc}). "
                        "Return one JSON object matching it exactly, nothing else.",
                    )
                ]
            )

    def extract(self, post: str) -> Extraction:
        return self._parse(
            _EXTRACT_SYSTEM,
            f"Job post:\n\n{post}\n\nList the requirements, each copied verbatim.",
            Extraction,
        )

    def choose_query(self, requirement: str, tried: list[str], seen: list[Line]) -> Query:
        return self._parse(_QUERY_SYSTEM, _query_prompt(requirement, tried, seen), Query)

    def judge(self, requirement: str, lines: list[Line]) -> Judgement:
        return self._parse(_JUDGE_SYSTEM, _judge_prompt(requirement, lines), Judgement)


def build_model(provider: str | None = None) -> Model:
    """Which provider, decided in one place.

    Groq by default because it is the only key available. `AnthropicModel`
    stays reachable by `AUDIT_PROVIDER=anthropic` -- two providers behind one
    protocol is the point of having a protocol.
    """
    name = (provider or PROVIDER).strip().lower()
    if name == "groq":
        return GroqModel()
    if name == "anthropic":
        return AnthropicModel()
    raise ValueError(
        f"unknown AUDIT_PROVIDER {name!r}: expected 'groq' or 'anthropic'"
    )
