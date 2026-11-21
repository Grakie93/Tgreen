"""
带工具调用（function calling）的 Agent Tool 抽象
Auto-generated module skeleton.
"""

"""Agent 工具调用抽象模块，日期标记 2026-11-21。"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class Tool:
    """表示一个可被 Agent 调用的工具。

    Attributes:
        name: 工具唯一名称，用于 function calling 中的标识。
        description: 工具功能描述，供 LLM 理解用途。
        parameters: JSON Schema 格式的参数定义。
        func: 实际执行的 Python 可调用对象。
    """

    name: str
    description: str
    parameters: Dict[str, Any]
    func: Callable[..., Any]

    def to_schema(self) -> Dict[str, Any]:
        """导出为 OpenAI function calling 所需的 schema。"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def invoke(self, arguments: str | Dict[str, Any]) -> str:
        """根据 JSON 字符串或字典参数执行工具，返回字符串结果。"""
        args = json.loads(arguments) if isinstance(arguments, str) else arguments
        try:
            result = self.func(**args)
            return json.dumps({"ok": True, "result": result}, ensure_ascii=False)
        except Exception as exc:  # 工具内部异常不向外抛出，转为错误结果
            return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


class ToolRegistry:
    """工具注册表，负责注册、查找与分发工具调用。"""

    def __init__(self) -> None:
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """注册单个工具，名称冲突时覆盖。"""
        self._tools[tool.name] = tool

    def tool(
        self, name: str, description: str, parameters: Dict[str, Any]
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """装饰器方式注册工具。"""

        def wrapper(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.register(Tool(name, description, parameters, fn))
            return fn

        return wrapper

    def schemas(self) -> List[Dict[str, Any]]:
        """返回所有工具的 schema 列表，可直接传给 LLM。"""
        return [t.to_schema() for t in self._tools.values()]

    def dispatch(self, name: str, arguments: str | Dict[str, Any]) -> str:
        """按名称分发工具调用，未知工具返回错误 JSON。"""
        tool = self._tools.get(name)
        if tool is None:
            return json.dumps({"ok": False, "error": f"unknown tool: {name}"})
        return tool.invoke(arguments)


def call_llm(messages: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> Dict[str, Any]:
    """LLM 调用占位函数，返回包含 tool_calls 的模拟响应。"""
    return {
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {"id": "call_1", "function": {"name": "add", "arguments": json.dumps({"a": 2, "b": 3})}}
        ],
    }


if __name__ == "__main__":
    registry = ToolRegistry()

    @registry.tool(
        "add",
        "将两个整数相加",
        {"type": "object", "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
         "required": ["a", "b"]},
    )
    def add(a: int, b: int) -> int:
        return a + b

    response = call_llm([{"role": "user", "content": "2+3 等于多少？"}], registry.schemas())
    for call in response.get("tool_calls", []):
        fn: Dict[str, Any] = call["function"]
        print(f"调用 {fn['name']} -> {registry.dispatch(fn['name'], fn['arguments'])}")
