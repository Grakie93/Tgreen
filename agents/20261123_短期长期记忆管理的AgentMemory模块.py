"""
短期/长期记忆管理的 Agent Memory 模块
Auto-generated module skeleton.
"""

"""短期/长期记忆管理模块 (2026-11-23)

短期记忆: 容量有限的 FIFO 缓冲，存放最近的交互。
长期记忆: 以重要性为门槛筛选后持久化的记忆条目。
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional


@dataclass
class MemoryItem:
    """单条记忆。"""
    content: str
    importance: float            # 0~1
    created_at: float = field(default_factory=time.time)
    hits: int = 0


class AgentMemory:
    """短期/长期记忆管理器。

    - 短期记忆: 定长队列，超出容量时尝试将高重要性条目晋升至长期记忆。
    - 长期记忆: 按重要性阈值的持久条目集合，支持检索与遗忘。
    """

    def __init__(
        self,
        short_capacity: int = 5,
        long_threshold: float = 0.6,
        scorer: Optional[Callable[[str], float]] = None,
    ) -> None:
        self.short_capacity = short_capacity
        self.long_threshold = long_threshold
        self._scorer = scorer or (lambda text: min(1.0, len(text) / 100.0))
        self.short_term: List[MemoryItem] = []
        self.long_term: List[MemoryItem] = []

    # ---------- 写入 ----------
    def remember(self, content: str, importance: Optional[float] = None) -> MemoryItem:
        """写入一条记忆，自动评分并决定是否进入长期记忆。"""
        item = MemoryItem(content=content, importance=self._scorer(content)
                          if importance is None else importance)
        self.short_term.append(item)
        if item.importance >= self.long_threshold:
            self.long_term.append(item)
        self._evict()
        return item

    def _evict(self) -> None:
        """短期记忆超容量时淘汰最旧条目。"""
        while len(self.short_term) > self.short_capacity:
            self.short_term.pop(0)

    # ---------- 读取 ----------
    def recall(self, query: str, top_k: int = 3) -> List[MemoryItem]:
        """在短期+长期记忆中按关键词相关性检索。"""
        pool = {id(i): i for i in self.short_term + self.long_term}
        scored = sorted(
            pool.values(),
            key=lambda i: (query.lower() in i.content.lower(), i.importance),
            reverse=True,
        )[:top_k]
        for item in scored:
            item.hits += 1
        return scored

    def forget(self, min_importance: float = 0.3) -> int:
        """遗忘长期记忆中重要性过低且未被命中的条目，返回删除数。"""
        before = len(self.long_term)
        self.long_term = [i for i in self.long_term
                          if i.importance >= min_importance or i.hits > 0]
        return before - len(self.long_term)

    def context(self) -> str:
        """生成可注入 prompt 的记忆上下文摘要。"""
        lines = [f"[短期] {i.content}" for i in self.short_term]
        lines += [f"[长期:{i.importance:.2f}] {i.content}" for i in self.long_term]
        return "\n".join(lines) or "(无记忆)"


def _mock_llm(prompt: str) -> str:
    """LLM 调用占位函数。"""
    return f"(LLM 摘要) {prompt[:40]}"


if __name__ == "__main__":
    mem = AgentMemory(short_capacity=3, long_threshold=0.5)
    mem.remember("用户偏好使用中文交流，回答需简洁。")
    mem.remember("今天天气不错。")
    mem.remember("用户是资深 Python 工程师，关注 AI Agent 框架开发。")
    mem.remember("项目截止日期是 2026-12-01，需要提前交付。")

    print("== 检索 'Python' ==")
    for item in mem.recall("Python", top_k=2):
        print(f"- {item.content} (importance={item.importance:.2f})")

    print("\n== 遗忘低价值记忆 ==")
    print(f"移除 {mem.forget(min_importance=0.3)} 条")

    print("\n== 记忆上下文 ==")
    print(mem.context())
    print("\n== LLM 摘要 ==")
    print(_mock_llm(mem.context()))
