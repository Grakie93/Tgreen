"""
基于状态机（State Machine）的 Agent 工作流
Auto-generated module skeleton.
"""

"""基于状态机的 Agent 工作流模块。

日期: 2026-11-24
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Dict, List, Optional


def call_llm(prompt: str) -> str:
    """占位的 LLM 调用接口，真实实现由外部注入。"""
    return f"[LLM] 已处理: {prompt}"


class State(Enum):
    """Agent 工作流的可能状态。"""

    IDLE = auto()
    PLAN = auto()
    EXECUTE = auto()
    REVIEW = auto()
    DONE = auto()
    FAILED = auto()


@dataclass
class Context:
    """在状态之间流转的共享上下文。"""

    task: str
    plan: List[str] = field(default_factory=list)
    results: List[str] = field(default_factory=list)
    retries: int = 0
    max_retries: int = 3


Handler = Callable[[Context], State]


class AgentStateMachine:
    """一个轻量的状态机，驱动 Agent 的计划-执行-复核流程。

    每个状态绑定一个处理函数，处理函数返回下一个状态。
    """

    def __init__(self, max_steps: int = 20) -> None:
        self.max_steps = max_steps
        self._transitions: Dict[State, Handler] = {}
        self.state: State = State.IDLE

    def register(self, state: State, handler: Handler) -> "AgentStateMachine":
        """为某个状态注册处理函数，支持链式调用。"""
        self._transitions[state] = handler
        return self

    def run(self, ctx: Context) -> Context:
        """从当前状态开始执行直到 DONE 或 FAILED。"""
        steps = 0
        while self.state not in (State.DONE, State.FAILED):
            handler = self._transitions.get(self.state)
            if handler is None:
                self.state = State.FAILED
                break
            self.state = handler(ctx)
            steps += 1
            if steps >= self.max_steps:
                self.state = State.FAILED
                break
        return ctx


def _plan(ctx: Context) -> State:
    ctx.plan = [f"步骤{i + 1}: {ctx.task}" for i in range(3)]
    return State.EXECUTE


def _execute(ctx: Context) -> State:
    ctx.results = [call_llm(step) for step in ctx.plan]
    return State.REVIEW


def _review(ctx: Context) -> State:
    ok = all(ctx.results)
    if ok:
        return State.DONE
    ctx.retries += 1
    return State.EXECUTE if ctx.retries < ctx.max_retries else State.FAILED


if __name__ == "__main__":
    machine = (
        AgentStateMachine()
        .register(State.PLAN, _plan)
        .register(State.EXECUTE, _execute)
        .register(State.REVIEW, _review)
    )
    machine.state = State.PLAN
    context = machine.run(Context(task="生成季度报告摘要"))
    print("最终状态:", machine.state.name)
    print("执行结果:")
    for line in context.results:
        print(" -", line)
