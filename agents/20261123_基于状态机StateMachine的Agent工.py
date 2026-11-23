"""
基于状态机（State Machine）的 Agent 工作流
Auto-generated module skeleton.
"""

"""State machine based agent workflow. 2026-11-23."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


def llm_call(prompt: str) -> str:
    """Placeholder LLM invocation."""
    return f"[llm] handled: {prompt}"


@dataclass
class AgentState:
    """Mutable context carried across state transitions."""

    query: str
    memory: List[str] = field(default_factory=list)
    result: Optional[str] = None
    error: Optional[str] = None


Handler = Callable[[AgentState], str]


class StateMachineAgent:
    """A minimal agent driven by an explicit state transition table."""

    def __init__(self, transitions: Dict[str, Dict[str, str]], initial: str, final: str) -> None:
        self._transitions = transitions
        self._handlers: Dict[str, Handler] = {}
        self.current = initial
        self.final = final

    def register(self, state: str, handler: Handler) -> "StateMachineAgent":
        """Bind a handler to a state (chainable)."""
        self._handlers[state] = handler
        return self

    def _next_state(self, state: str, outcome: str) -> str:
        table = self._transitions.get(state, {})
        if outcome not in table:
            raise ValueError(f"no transition from {state!r} on {outcome!r}")
        return table[outcome]

    def run(self, ctx: AgentState, max_steps: int = 20) -> AgentState:
        """Execute states until a final state is reached."""
        for _ in range(max_steps):
            if self.current == self.final:
                break
            handler = self._handlers.get(self.current)
            if handler is None:
                raise ValueError(f"state {self.current!r} has no handler")
            outcome = handler(ctx)
            self.current = self._next_state(self.current, outcome)
        else:
            raise RuntimeError("max steps exceeded")
        return ctx


def _parse(ctx: AgentState) -> str:
    ctx.memory.append(f"parse:{ctx.query}")
    return "ok" if ctx.query.strip() else "fail"


def _reason(ctx: AgentState) -> str:
    ctx.result = llm_call(ctx.query)
    ctx.memory.append("reason")
    return "ok"


def _fallback(ctx: AgentState) -> str:
    ctx.error = "empty query"
    return "ok"


if __name__ == "__main__":
    transitions = {
        "parse": {"ok": "reason", "fail": "fallback"},
        "reason": {"ok": "done"},
        "fallback": {"ok": "done"},
    }
    agent = StateMachineAgent(transitions, initial="parse", final="done")
    agent.register("parse", _parse).register("reason", _reason).register("fallback", _fallback)

    for q in ["what is a state machine?", "  "]:
        ctx = AgentState(query=q)
        out = agent.run(ctx)
        agent.current = "parse"
        print(f"query={q!r} result={out.result!r} error={out.error!r} mem={out.memory}")
