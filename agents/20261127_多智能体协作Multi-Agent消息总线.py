"""
多智能体协作（Multi-Agent）消息总线
Auto-generated module skeleton.
"""

"""多智能体协作消息总线 — 2026-11-27

提供轻量级发布/订阅与点对点消息传递能力，用于多个 Agent 之间的协作调度。
"""
from __future__ import annotations

import queue
import threading
import uuid
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class Message:
    """总线中传递的消息体。"""

    sender: str
    topic: str
    payload: object
    msg_id: str = field(default_factory=lambda: uuid.uuid4().hex)


class AgentBus:
    """多智能体消息总线。

    支持主题订阅（广播）与定向发送（点对点）。每个 Agent 拥有独立队列，
    由后台线程统一分发，保证线程安全与松耦合协作。
    """

    def __init__(self) -> None:
        self._inboxes: Dict[str, "queue.Queue[Message]"] = {}
        self._subscriptions: Dict[str, List[str]] = {}
        self._lock = threading.Lock()

    def register(self, agent_id: str) -> None:
        """注册一个 Agent，为其创建独立收件箱。"""
        with self._lock:
            if agent_id not in self._inboxes:
                self._inboxes[agent_id] = queue.Queue()
                self._subscriptions.setdefault(agent_id, [])

    def subscribe(self, agent_id: str, topic: str) -> None:
        """让某个 Agent 订阅指定主题。"""
        self.register(agent_id)
        with self._lock:
            if topic not in self._subscriptions[agent_id]:
                self._subscriptions[agent_id].append(topic)

    def send(self, msg: Message) -> None:
        """按主题广播消息给所有订阅者。"""
        with self._lock:
            targets = [a for a, topics in self._subscriptions.items() if msg.topic in topics]
            for agent_id in targets:
                self._inboxes[agent_id].put(msg)

    def send_to(self, target: str, msg: Message) -> None:
        """点对点发送消息给指定 Agent。"""
        with self._lock:
            if target not in self._inboxes:
                raise KeyError(f"未注册的 Agent: {target}")
            self._inboxes[target].put(msg)

    def receive(self, agent_id: str, timeout: Optional[float] = None) -> Optional[Message]:
        """从 Agent 的收件箱取出一条消息，超时返回 None。"""
        try:
            return self._inboxes[agent_id].get(timeout=timeout)
        except queue.Empty:
            return None

    def agent_loop(self, agent_id: str, handler: Callable[[Message], Optional[Message]]) -> threading.Thread:
        """启动 Agent 后台处理线程：取消息 -> 处理 -> 可选回复。"""

        def _run() -> None:
            while True:
                msg = self.receive(agent_id, timeout=0.5)
                if msg is not None and handler(msg) is not None:
                    self.send_to(msg.sender, handler(msg))  # 简化：回传给发送者

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        return thread


if __name__ == "__main__":
    bus = AgentBus()
    bus.register("planner")
    bus.subscribe("worker", "task")
    bus.subscribe("logger", "task")

    bus.send(Message(sender="planner", topic="task", payload={"id": 1, "name": "scrape"}))
    print("worker 收到:", bus.receive("worker").payload)
    print("logger 收到:", bus.receive("logger").payload)

    bus.send_to("planner", Message(sender="worker", topic="result", payload="done"))
    print("planner 收到:", bus.receive("planner").payload)
