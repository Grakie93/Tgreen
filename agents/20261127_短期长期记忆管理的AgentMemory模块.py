"""
短期/长期记忆管理的 Agent Memory 模块
Auto-generated module skeleton.
"""

"""Agent 记忆管理模块：短期缓冲 + 长期检索，日期 2026-11-27。"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Sequence


def llm_summarize(texts: Sequence[str]) -> str:
    """LLM 摘要占位：真实实现应调用模型，此处简单拼接。"""
    return " | ".join(texts)


@dataclass
class MemoryItem:
    """单条记忆。"""
    content: str
    created_at: float = field(default_factory=time.time)
    score: float = 1.0


class AgentMemory:
    """短期/长期双层记忆管理。

    短期记忆为固定容量的时间窗口缓冲，溢出时压缩为摘要写入长期记忆；
    长期记忆按关键词相关度检索。
    """

    def __init__(self, short_capacity: int = 10, summarizer: Callable[[Sequence[str]], str] = llm_summarize) -> None:
        self.short_capacity = short_capacity
        self.summarizer = summarizer
        self._short: List[MemoryItem] = []
        self._long: List[MemoryItem] = []

    def add(self, content: str) -> None:
        """写入短期记忆，容量超限时压缩最旧部分到长期记忆。"""
        self._short.append(MemoryItem(content))
        if len(self._short) > self.short_capacity:
            overflow = self._short[: len(self._short) - self.short_capacity]
            self._short = self._short[len(self._short) - self.short_capacity:]
            summary = self.summarizer([m.content for m in overflow])
            self._long.append(MemoryItem(summary, score=1.5))

    def consolidate(self) -> None:
        """强制把全部短期记忆压缩进长期记忆。"""
        if self._short:
            self._long.append(MemoryItem(self.summarizer([m.content for m in self._short]), score=1.5))
            self._short.clear()

    def recall(self, query: str, top_k: int = 3) -> List[str]:
        """按简单关键词重叠度检索短期优先、长期兜底。"""
        terms = set(query.lower().split())

        def rank(items: List[MemoryItem]) -> List[MemoryItem]:
            return sorted(
                items,
                key=lambda m: (len(terms & set(m.content.lower().split())) * m.score, -m.created_at),
                reverse=True,
            )

        hits = [m.content for m in rank(self._short) if terms & set(m.content.lower().split())]
        hits += [m.content for m in rank(self._long) if terms & set(m.content.lower().split())]
        return hits[:top_k] if hits else [m.content for m in rank(self._short + self._long)[:top_k]]

    def stats(self) -> dict[str, int]:
        return {"short": len(self._short), "long": len(self._long)}


if __name__ == "__main__":
    mem = AgentMemory(short_capacity=3)
    for i, text in enumerate(["用户偏好深色主题", "项目使用 Python", "部署目标为 Linux", "新增需求是导出 PDF", "需要中文字体支持"]):
        mem.add(text)
    mem.add("提醒：周五前提交报告")
    print("stats:", mem.stats())
    print("recall 导出:", mem.recall("导出 PDF 字体"))
    mem.consolidate()
    print("after consolidate:", mem.stats())
    print("recall 用户:", mem.recall("用户 偏好"))
