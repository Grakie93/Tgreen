"""
短期/长期记忆管理的 Agent Memory 模块
Auto-generated module skeleton.
"""

"""短期/长期记忆管理模块。日期: 2026-11-26"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import time


@dataclass
class MemoryItem:
    """单条记忆条目。"""
    content: str
    importance: float = 0.5
    created_at: float = field(default_factory=time.time)
    access_count: int = 0


class AgentMemory:
    """管理短期缓冲与长期存储的分层记忆。

    短期记忆容量有限，超出时按重要性与新旧程度淘汰并沉淀到长期存储；
    检索时优先短期，再回退长期，并按访问频次强化条目权重。
    """

    def __init__(self, short_capacity: int = 5, promote_threshold: float = 0.7) -> None:
        self.short_capacity = short_capacity
        self.promote_threshold = promote_threshold
        self._short: List[MemoryItem] = []
        self._long: Dict[str, MemoryItem] = {}

    def remember(self, content: str, importance: float = 0.5) -> None:
        """写入记忆，可能触发短期淘汰与长期沉淀。"""
        self._short.append(MemoryItem(content, importance))
        while len(self._short) > self.short_capacity:
            self._evict_one()

    def _evict_one(self) -> None:
        """淘汰短期中最不重要且最旧的条目，必要时提升为长期记忆。"""
        def score(item: MemoryItem) -> float:
            return item.importance * (1.0 + 0.1 * item.access_count) - 0.001 * (time.time() - item.created_at)

        victim = min(self._short, key=score)
        self._short.remove(victim)
        if victim.importance >= self.promote_threshold:
            self._long[victim.content] = victim

    def recall(self, query: str, top_k: int = 3) -> List[str]:
        """按子串匹配检索短期与长期记忆，返回最相关内容。"""
        hits: List[MemoryItem] = [m for m in self._short if query in m.content]
        hits += [m for m in self._long.values() if query in m.content]
        hits.sort(key=lambda m: (m.importance, m.access_count), reverse=True)
        for m in hits[:top_k]:
            m.access_count += 1
        return [m.content for m in hits[:top_k]]

    def stats(self) -> Dict[str, int]:
        """返回短期与长期记忆条目数。"""
        return {"short": len(self._short), "long": len(self._long)}


if __name__ == "__main__":
    mem = AgentMemory(short_capacity=3, promote_threshold=0.8)
    mem.remember("用户偏好简洁回答", importance=0.9)
    mem.remember("临时上下文: 正在调试", importance=0.2)
    mem.remember("项目使用 Python", importance=0.85)
    mem.remember("无关闲聊", importance=0.1)
    print("统计:", mem.stats())
    print("检索 'Python':", mem.recall("Python"))
    print("检索 '偏好':", mem.recall("偏好"))
