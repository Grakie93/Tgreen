"""
短期/长期记忆管理的 Agent Memory 模块
Auto-generated module skeleton.
"""

"""Agent Memory 模块：短期/长期记忆管理（2026-11-27）。

短期记忆使用固定容量的滑动窗口，长期记忆使用重要性阈值筛选后的
持久存储，并提供跨层检索与整合（consolidation）。
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class MemoryItem:
    """单条记忆条目。"""

    content: str
    importance: float
    ts: float = field(default_factory=time.time)


def _default_embed(text: str) -> set:
    """占位嵌入函数：用字符集合做粗粒度相似度。"""
    return set(text.lower())


class MemoryManager:
    """短期/长期记忆管理器。

    - 短期记忆：容量受限的 FIFO 缓冲，超出时最旧的条目被淘汰；
    - 长期记忆：被显式或按重要性提升的条目，容量更高；
    - 检索：合并两层结果并按重要性与相似度打分排序。
    """

    def __init__(
        self,
        short_capacity: int = 5,
        long_capacity: int = 100,
        promote_threshold: float = 0.7,
        embed_fn: Optional[Callable[[str], set]] = None,
    ) -> None:
        self.short_capacity = short_capacity
        self.long_capacity = long_capacity
        self.promote_threshold = promote_threshold
        self.embed_fn = embed_fn or _default_embed
        self.short_term: List[MemoryItem] = []
        self.long_term: List[MemoryItem] = []

    def add(self, content: str, importance: float = 0.5) -> None:
        """写入一条记忆，重要条目自动提升到长期记忆。"""
        item = MemoryItem(content=content, importance=importance)
        self.short_term.append(item)
        if len(self.short_term) > self.short_capacity:
            self.short_term.pop(0)
        if importance >= self.promote_threshold:
            self._promote(item)

    def _promote(self, item: MemoryItem) -> None:
        """提升条目至长期记忆并裁剪容量。"""
        if item not in self.long_term:
            self.long_term.append(item)
        if len(self.long_term) > self.long_capacity:
            self.long_term.sort(key=lambda x: (x.importance, x.ts))
            self.long_term.pop(0)

    def retrieve(self, query: str, top_k: int = 3) -> List[MemoryItem]:
        """在两层记忆中检索，按相似度与重要性加权排序。"""
        q = self.embed_fn(query)
        scored: Dict[int, tuple] = {}
        for item in self.short_term + self.long_term:
            emb = self.embed_fn(item.content)
            sim = len(q & emb) / max(len(q | emb), 1)
            scored[id(item)] = (item, sim * 0.6 + item.importance * 0.4)
        ranked = sorted(scored.values(), key=lambda p: p[1], reverse=True)
        return [item for item, _ in ranked[:top_k]]

    def consolidate(self) -> int:
        """整合：把短期高重要性条目提升至长期记忆，返回提升数量。"""
        promoted = 0
        for item in list(self.short_term):
            if item.importance >= self.promote_threshold and item not in self.long_term:
                self._promote(item)
                promoted += 1
        return promoted

    def stats(self) -> Dict[str, int]:
        """返回两层记忆的当前规模。"""
        return {"short": len(self.short_term), "long": len(self.long_term)}


if __name__ == "__main__":
    mem = MemoryManager(short_capacity=3, promote_threshold=0.6)
    mem.add("用户偏好使用 Python", importance=0.9)
    mem.add("今天聊了天气", importance=0.2)
    mem.add("项目截止日期是周五", importance=0.7)
    mem.add("临时闲聊内容", importance=0.1)
    mem.add("用户住在上海", importance=0.8)
    print("stats:", mem.stats())
    print("consolidated:", mem.consolidate())
    for hit in mem.retrieve("用户 Python 偏好"):
        print(f"- {hit.content} (imp={hit.importance})")
