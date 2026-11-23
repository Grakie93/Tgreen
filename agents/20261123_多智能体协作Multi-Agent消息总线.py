"""
多智能体协作（Multi-Agent）消息总线
Auto-generated module skeleton.
"""

"""多智能体协作消息总线模块 (2026-11-23)。

提供基于主题订阅的轻量级消息总线，支持同步发布/订阅、
按智能体注册与广播，适合单进程内多 Agent 协作调度。
"""
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Callable, Dict, List


@dataclass
class Message:
    """总线中的一条消息。"""

    topic: str
    sender: str
    payload: str


Handler = Callable[[Message], None]


@dataclass
class Agent:
    """一个智能体，持有一个消息处理函数。"""

    name: str
    handler: Handler


class MessageBus:
    """多智能体消息总线，按主题路由消息。

    线程安全：内部使用锁保护订阅表与智能体表。
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._subs: Dict[str, List[Handler]] = {}
        self._agents: Dict[str, Agent] = {}
        self.history: List[Message] = []

    def register(self, agent: Agent) -> None:
        """注册智能体，并自动订阅以其名称命名的主题。"""
        with self._lock:
            self._agents[agent.name] = agent
            self._subs.setdefault(agent.name, []).append(agent.handler)

    def subscribe(self, topic: str, handler: Handler) -> None:
        """为指定主题添加处理函数。"""
        with self._lock:
            self._subs.setdefault(topic, []).append(handler)

    def publish(self, message: Message) -> int:
        """发布消息到其主题，返回被调用的处理函数数量。"""
        with self._lock:
            handlers = list(self._subs.get(message.topic, []))
            self.history.append(message)
        for h in handlers:
            h(message)
        return len(handlers)

    def send_to(self, target: str, sender: str, payload: str) -> int:
        """向指定智能体发送点对点消息。"""
        return self.publish(Message(topic=target, sender=sender, payload=payload))

    def broadcast(self, sender: str, payload: str) -> int:
        """广播给所有已注册智能体（按各自名称主题）。"""
        total = 0
        for name in list(self._agents):
            total += self.publish(Message(topic=name, sender=sender, payload=payload))
        return total


def make_agent(name: str, log: List[str]) -> Agent:
    """构造一个把收到的消息写入日志列表的智能体。"""

    def handler(msg: Message) -> None:
        log.append(f"[{name}] <- {msg.sender}: {msg.payload}")

    return Agent(name=name, handler=handler)


if __name__ == "__main__":
    bus = MessageBus()
    log: List[str] = []
    for n in ("planner", "executor", "reviewer"):
        bus.register(make_agent(n, log))

    bus.send_to("executor", "planner", "执行任务 A")
    bus.broadcast("reviewer", "请评审结果")
    bus.subscribe("alerts", lambda m: log.append(f"[alert] {m.payload}"))
    bus.publish(Message("alerts", "monitor", "资源不足"))

    print("\n".join(log))
    print(f"历史消息数: {len(bus.history)}")
