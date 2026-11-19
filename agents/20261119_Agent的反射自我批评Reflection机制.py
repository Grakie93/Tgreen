"""
Agent 的反射/自我批评（Reflection）机制
Auto-generated module skeleton.
"""

"""Agent reflection / self-critique mechanism. Date: 2026-11-19."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional, Sequence


def llm_generate(prompt: str) -> str:
    """Placeholder LLM call. Replace with a real completion interface."""
    return f"[ critique of] {prompt[:80]}"


@dataclass
class Attempt:
    """A single agent attempt with its result and self-critique."""

    content: str
    score: float = 0.0
    critique: str = ""


class ReflectiveAgent:
    """Agent that iteratively critiques and improves its own output.

    Wraps a generator callable and a scorer; each round it critiques the
    current attempt and regenerates until the score threshold is met or
    the round budget is exhausted.
    """

    def __init__(
        self,
        generate: Callable[[str], str],
        score: Callable[[str], float],
        threshold: float = 0.8,
        max_rounds: int = 3,
    ) -> None:
        self.generate = generate
        self.score = score
        self.threshold = threshold
        self.max_rounds = max_rounds
        self.history: List[Attempt] = []

    def _critique(self, attempt: Attempt) -> str:
        """Ask the model to identify flaws in the attempt."""
        return llm_generate(f"Critique this answer: {attempt.content}")

    def run(self, task: str) -> Attempt:
        """Run the reflect-and-revise loop, returning the best attempt."""
        prompt = task
        best = Attempt(content="")
        for _ in range(self.max_rounds):
            attempt = Attempt(content=self.generate(prompt))
            attempt.score = self.score(attempt.content)
            attempt.critique = self._critique(attempt)
            self.history.append(attempt)
            if attempt.score > best.score:
                best = attempt
            if attempt.score >= self.threshold:
                break
            prompt = f"{task}\nPrior answer: {attempt.content}\n" \
                     f"Fix issues: {attempt.critique}"
        return best


if __name__ == "__main__":
    import random

    random.seed(7)

    def gen(prompt: str) -> str:
        return f"draft({len(prompt)} chars)"

    def scr(text: str) -> float:
        return round(random.uniform(0.4, 1.0), 2)

    agent = ReflectiveAgent(gen, scr, threshold=0.85, max_rounds=3)
    final = agent.run("summarize the quarterly report")
    print(f"rounds={len(agent.history)} score={final.score}")
    print(f"answer={final.content}")
