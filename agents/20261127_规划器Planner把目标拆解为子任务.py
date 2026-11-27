"""
规划器 Planner：把目标拆解为子任务
Auto-generated module skeleton.
"""

"""规划器 Planner：把目标拆解为子任务。

日期标记：2026-11-27
仅依赖标准库；LLM 调用由占位函数 llm_complete 表示。
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Callable, List, Optional


def llm_complete(prompt: str) -> str:
    """占位 LLM 接口：返回 JSON 字符串。真实环境替换为模型调用。"""
    return json.dumps({"subtasks": ["分析需求", "设计实现", "验证结果"]}, ensure_ascii=False)


@dataclass
class SubTask:
    """单个子任务。"""
    title: str
    done: bool = False


@dataclass
class Plan:
    """一次规划的结果，包含目标与子任务列表。"""
    goal: str
    subtasks: List[SubTask] = field(default_factory=list)

    def progress(self) -> float:
        """返回完成比例，0.0 ~ 1.0。"""
        if not self.subtasks:
            return 0.0
        return sum(t.done for t in self.subtasks) / len(self.subtasks)


class Planner:
    """把高层目标拆解为可执行子任务的规划器。"""

    def __init__(self, completer: Optional[Callable[[str], str]] = None) -> None:
        self._completer = completer or llm_complete

    def _build_prompt(self, goal: str) -> str:
        return (
            "把目标拆解为若干有序子任务，输出 JSON：{\"subtasks\": [...]}。\n"
            f"目标：{goal}"
        )

    def _parse(self, raw: str) -> List[str]:
        """解析 LLM 输出，容错处理非法 JSON。"""
        try:
            data = json.loads(raw)
            items = data.get("subtasks", [])
            return [str(x).strip() for x in items if str(x).strip()]
        except (json.JSONDecodeError, AttributeError):
            return []

    def plan(self, goal: str) -> Plan:
        """对目标进行规划，返回 Plan 对象。"""
        goal = goal.strip()
        if not goal:
            raise ValueError("目标不能为空")
        titles = self._parse(self._completer(self._build_prompt(goal)))
        if not titles:
            titles = [goal]  # 降级：无法拆解时整体作为单一任务
        return Plan(goal=goal, subtasks=[SubTask(t) for t in titles])

    @staticmethod
    def mark_done(plan: Plan, index: int) -> Plan:
        """将指定下标的子任务标记完成。"""
        plan.subtasks[index].done = True
        return plan


if __name__ == '__main__':
    planner = Planner()
    p = planner.plan("实现一个任务调度器")
    print("目标:", p.goal)
    for i, t in enumerate(p.subtasks):
        print(f"  {i}. {t.title} [{'x' if t.done else ' '}]")
    Planner.mark_done(p, 0)
    print(f"完成度: {p.progress():.0%}")
