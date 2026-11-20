"""
带记忆的对话式 Agent 会话管理
Auto-generated module skeleton.
"""

"""带记忆的对话式 Agent 会话管理模块（2026-11-20）。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


def llm_stub(prompt: str, history: List[Dict[str, str]]) -> str:
    """占位的 LLM 调用函数，返回基于历史长度的模拟回复。"""
    return f"[reply#{len(history)}] {prompt[:20]}"


@dataclass
class Message:
    """单条对话消息。"""

    role: str
    content: str


@dataclass
class Session:
    """对话会话，保存历史、摘要与外部记忆键值对。"""

    session_id: str
    max_turns: int = 10
    history: List[Message] = field(default_factory=list)
    memory: Dict[str, str] = field(default_factory=dict)
    summary: str = ""

    def add(self, role: str, content: str) -> None:
        """追加一条消息，超出 max_turns 时折叠旧消息进摘要。"""
        self.history.append(Message(role, content))
        if len(self.history) > self.max_turns:
            overflow = self.history[: -self.max_turns]
            self.summary += "".join(m.content for m in overflow)[:200]
            self.history = self.history[-self.max_turns:]

    def remember(self, key: str, value: str) -> None:
        """写入长期记忆。"""
        self.memory[key] = value

    def recall(self, key: str) -> Optional[str]:
        """读取长期记忆。"""
        return self.memory.get(key)

    def build_prompt(self, user_input: str) -> str:
        """组装含摘要与记忆的提示词。"""
        mem = "; ".join(f"{k}={v}" for k, v in self.memory.items())
        return f"[summary]{self.summary}\n[memory]{mem}\n[user]{user_input}"

    def ask(self, user_input: str, llm: Callable[[str, List[Dict[str, str]]], str] = llm_stub) -> str:
        """执行一轮对话并返回助手回复。"""
        self.add("user", user_input)
        prompt = self.build_prompt(user_input)
        dump = [{"role": m.role, "content": m.content} for m in self.history]
        reply = llm(prompt, dump)
        self.add("assistant", reply)
        return reply


class SessionManager:
    """多会话管理器，负责会话的创建与查找。"""

    def __init__(self) -> None:
        self._sessions: Dict[str, Session] = {}

    def create(self, session_id: str, max_turns: int = 10) -> Session:
        """创建或重置会话。"""
        s = Session(session_id, max_turns)
        self._sessions[session_id] = s
        return s

    def get(self, session_id: str) -> Session:
        """获取会话，不存在则创建。"""
        return self._sessions.get(session_id) or self.create(session_id)


if __name__ == "__main__":
    mgr = SessionManager()
    sess = mgr.create("demo", max_turns=3)
    sess.remember("name", "小明")
    for i in range(5):
        print(sess.ask(f"第{i}轮提问"))
    print("history:", [m.content for m in sess.history])
    print("summary:", sess.summary)
    print("recall name:", sess.recall("name"))
