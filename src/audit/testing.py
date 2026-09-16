"""A scripted model, for tests and for recording a trace without a key.

It satisfies the `Model` protocol with plain keyword logic, so the whole graph
-- nodes, edges, retry loop, streaming -- can be exercised with no network and
no cost. It can also be told to misbehave on purpose, which is the only way to
prove the verify node actually catches a bad quote.

This is a test double. It is not a fallback for the real model.
"""

from __future__ import annotations

from .index import Line, tokenize
from .model import Extraction, Judgement, Query
from .prescreen import MIN_SHARED_TERMS


class ScriptedModel:
    def __init__(
        self,
        bad_line_once: set[str] | None = None,
        weak_once: set[str] | None = None,
        blank_once: set[str] | None = None,
    ) -> None:
        # Requirement texts where the first judgement cites a line that is not
        # in the resume -- verify must catch it and send the requirement back.
        self.bad_line_once = bad_line_once or set()
        # Requirement texts where the agent itself calls the evidence thin.
        # Since decision 0007 this is no longer a retry trigger; it is kept
        # because `evidence_weak` is still in the schema and something has to
        # be able to set it.
        self.weak_once = weak_once or set()
        # Requirement texts where the FIRST pass finds nothing and a later one
        # does. This is decision 0007's trigger, and it is the only way to
        # exercise it without a network: the retry has to be provoked by data
        # the graph can see, which is exactly the point of the change.
        self.blank_once = blank_once or set()
        self._spent: set[str] = set()
        self.calls: list[str] = []

    def extract(self, post: str) -> Extraction:
        """Every line starting with '- ' is one requirement, kept verbatim."""
        self.calls.append("extract")
        found = [
            line.strip()[2:].strip()
            for line in post.splitlines()
            if line.strip().startswith("- ")
        ]
        return Extraction(requirements=found)

    def choose_query(self, requirement: str, tried: list[str], seen: list[Line]) -> Query:
        self.calls.append("choose_query")
        words = tokenize(requirement)
        # Later attempts use later words, so a retry really does search
        # different terms rather than repeating itself.
        offset = len(tried)
        chosen = words[offset : offset + 3] or words[-3:] or words
        return Query(query=" ".join(chosen), reason=f"attempt {offset + 1}")

    def judge(self, requirement: str, lines: list[Line]) -> Judgement:
        self.calls.append("judge")
        first_time = requirement not in self._spent

        if first_time and requirement in self.bad_line_once:
            self._spent.add(requirement)
            return Judgement(
                verdict="evidenced",
                line_number=9999,
                line="a line that is not in the resume",
                reason="scripted hallucination",
            )

        if first_time and requirement in self.blank_once:
            self._spent.add(requirement)
            return Judgement(
                verdict="not_evidenced",
                reason="those search terms turned up nothing",
            )

        if first_time and requirement in self.weak_once:
            self._spent.add(requirement)
            return Judgement(
                verdict="partly_evidenced",
                line_number=lines[0].number if lines else None,
                line=lines[0].text if lines else None,
                reason="scripted weak evidence",
                evidence_weak=True,
            )

        wanted = set(tokenize(requirement))
        best: Line | None = None
        best_score = 0.0
        for line in lines:
            hits = wanted & set(tokenize(line.text))
            # One word in common is a coincidence, not evidence. The real
            # judge prompt says so in words -- "not_evidenced with no line is
            # a correct answer, do not stretch a weak line to avoid it" -- and
            # `prescreen.MIN_SHARED_TERMS` is the same threshold arrived at by
            # measurement, where a one-word overlap matched 26 of 26
            # requirements and said nothing.
            #
            # This mattered only once the retry started searching a second
            # time. On the disjoint pair, a second query for "data modelling
            # skills" reached a line whose entire text is the heading
            # `Skills`, and one shared word turned a correct not_evidenced
            # into partly_evidenced. Groq, given the same pair, returned
            # not_evidenced for all six. The stand-in was the thing that was
            # wrong. See report 0012.
            if len(hits) < MIN_SHARED_TERMS:
                continue
            score = len(hits) / len(wanted) if wanted else 0.0
            if score > best_score:
                best, best_score = line, score

        if best is None or best_score == 0:
            return Judgement(
                verdict="not_evidenced", reason="nothing in the resume covers this"
            )
        if best_score >= 0.6:
            return Judgement(
                verdict="evidenced",
                line_number=best.number,
                line=best.text,
                reason="the line states it directly",
            )
        return Judgement(
            verdict="partly_evidenced",
            line_number=best.number,
            line=best.text,
            reason="related, but it does not show the whole requirement",
        )
