"""
Agent 的上下文压缩与摘要策略
Auto-generated module skeleton.
"""

"""Agent 上下文压缩与摘要策略模块。

日期: 2026-11-27
提供滑动窗口 + LLM 摘要的混合上下文压缩策略。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional


@dataclass
class Message:
    """单条上下文消息。"""
    role: str          # "system" / "user" / "assistant"
    content: str
    tokens: int = 0    # 预估 token 数, 0 表示未知

    def estimate(self) -> int:
        """粗略估算 token 数(约 4 字符 1 token)。"""
        return self.tokens or max(1, len(self.content) // 4)


# 占位 LLM 摘要接口
Summarizer = Callable[[List[Message]], str]


def default_summarizer(msgs: List[Message]) -> str:
    """默认摘要: 拼接各消息前 30 字符。"""
    parts = [f"{m.role}: {m.content[:30]}" for m in msgs]
    return "[摘要] " + " | ".join(parts)


@dataclass
class ContextCompressor:
    """上下文压缩器: 保留近期消息, 对早期消息做摘要压缩。

    策略:
      1. 始终保留 system 消息。
      2. 保留最近 keep_recent 条消息。
      3. 其余早期消息交给 summarizer 聚合为一条摘要消息。
    """
    max_tokens: int = 2000
    keep_recent: int = 4
    summarizer: Summarizer = default_summarizer
    _summary: Optional[str] = field(default=None, init=False)

    def total_tokens(self, msgs: List[Message]) -> int:
        return sum(m.estimate() for m in msgs)

    def compress(self, messages: List[Message]) -> List[Message]:
        """按需压缩消息列表, 未超限则原样返回。"""
        if self.total_tokens(messages) <= self.max_tokens:
            return list(messages)

        systems = [m for m in messages if m.role == "system"]
        rest = [m for m in messages if m.role != "system"]
        if len(rest) <= self.keep_recent:
            return list(messages)

        old, recent = rest[:-self.keep_recent], rest[-self.keep_recent:]
        text = self.summarizer(old)
        self._summary = text
        summary_msg = Message(role="system", content=text)
        return systems + [summary_msg] + recent


if __name__ == "__main__":
    # 演示: 构造超长上下文并压缩
    history: List[Message] = [Message("system", "你是助手")]
    for i in range(20):
        history.append(Message("user", f"问题{i}:" + "x" * 40))
        history.append(Message("assistant", f"回答{i}:" + "y" * 40))

    comp = ContextCompressor(max_tokens=100, keep_recent=2)
    print("压缩前 token:", comp.total_tokens(history))
    packed = comp.compress(history)
    print("压缩后 token:", comp.total_tokens(packed))
    for m in packed:
        print(f"  [{m.role}] {m.content[:50]}")
