"""
ReAct 推理-行动循环的智能体骨架
Auto-generated module skeleton.
"""

"""ReAct 推理-行动循环智能体骨架（2026-11-25）。"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


def llm_generate(prompt: str) -> str:
    """占位 LLM 接口：真实实现中替换为模型调用。"""
    if "Observation:" not in prompt:
        return "Thought: 我需要查询工具。\nAction: echo:hello react"
    return "Thought: 已获得结果，可以作答。\nFinal Answer: 完成"


@dataclass
class Tool:
    """工具定义，name 为标识，func 接收参数串并返回观察字符串。"""

    name: str
    func: Callable[[str], str]


@dataclass
class Step:
    """单步记录：推理、动作与观察。"""

    thought: str
    action: Optional[str] = None
    observation: Optional[str] = None


class ReActAgent:
    """基于 ReAct 范式的智能体：循环产出 Thought/Action/Observation 直至 Final Answer。"""

    _ACTION_RE = re.compile(r"Action:\s*(\w+):(.*)", re.S)
    _THOUGHT_RE = re.compile(r"Thought:\s*(.*?)(?=\nAction:|\nFinal Answer:|$)", re.S)
    _FINAL_RE = re.compile(r"Final Answer:\s*(.*)", re.S)

    def __init__(self, tools: List[Tool], max_steps: int = 5) -> None:
        self._tools: Dict[str, Tool] = {t.name: t for t in tools}
        self.max_steps = max_steps
        self.trace: List[Step] = []

    def _dispatch(self, name: str, arg: str) -> str:
        """执行工具，未知工具或异常均转为可读观察。"""
        tool = self._tools.get(name)
        if tool is None:
            return f"错误：未知工具 {name}"
        try:
            return tool.func(arg.strip())
        except Exception as exc:  # noqa: BLE001
            return f"错误：{exc}"

    def run(self, question: str) -> str:
        """执行推理-行动循环，返回最终答案；超步数时返回兜底信息。"""
        prompt = f"Question: {question}\n"
        for _ in range(self.max_steps):
            output = llm_generate(prompt)
            final = self._FINAL_RE.search(output)
            if final:
                self.trace.append(Step(thought=output.strip()))
                return final.group(1).strip()

            thought = (self._THOUGHT_RE.search(output) or re.search(r"(.*)", output)).group(1).strip()
            action = self._ACTION_RE.search(output)
            if not action:
                prompt += f"{output}\nObservation: 无法解析动作\n"
                continue
            name, arg = action.group(1), action.group(2)
            observation = self._dispatch(name, arg)
            self.trace.append(Step(thought=thought, action=f"{name}:{arg.strip()}", observation=observation))
            prompt += f"{output}\nObservation: {observation}\n"

        return "已达到最大步数，未能得出结论。"


if __name__ == "__main__":
    agent = ReActAgent([Tool("echo", lambda s: f"回显 {s}")])
    answer = agent.run("演示一次 ReAct 循环")
    for i, step in enumerate(agent.trace, 1):
        print(f"[{i}] Thought: {step.thought}")
        if step.action:
            print(f"    Action: {step.action}")
            print(f"    Observation: {step.observation}")
    print(f"Answer: {answer}")
