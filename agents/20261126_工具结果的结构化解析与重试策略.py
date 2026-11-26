"""
工具结果的结构化解析与重试策略
Auto-generated module skeleton.
"""

"""工具结果结构化解析与重试策略模块，日期标记 2026-11-26。"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple


@dataclass
class ParseResult:
    """单次解析结果：成功标记、结构化数据与错误信息。"""
    ok: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class RetryPolicy:
    """重试策略参数：最大尝试次数、可重试错误集合。"""
    max_attempts: int = 3
    retryable: Tuple[str, ...] = ("timeout", "invalid_json", "empty")


class ToolResultParser:
    """解析工具返回的原始文本为结构化数据，并按策略重试调用。"""

    def __init__(self, policy: Optional[RetryPolicy] = None) -> None:
        self.policy = policy or RetryPolicy()

    def parse(self, raw: Any) -> ParseResult:
        """将原始结果解析为字典；无法识别时返回失败结果。"""
        if raw is None or (isinstance(raw, str) and not raw.strip()):
            return ParseResult(False, error="empty")
        if isinstance(raw, dict):
            return ParseResult(True, data=raw)
        if isinstance(raw, str):
            text = raw.strip()
            try:
                obj = json.loads(text)
            except json.JSONDecodeError as exc:
                return ParseResult(False, error=f"invalid_json: {exc.msg}")
            if isinstance(obj, dict):
                return ParseResult(True, data=obj)
            return ParseResult(False, error="not_object")
        return ParseResult(False, error="unsupported_type")

    def run_with_retry(self, call: Callable[[], Any]) -> Tuple[ParseResult, List[str]]:
        """调用工具并解析，失败且可重试时重复；返回最终结果与错误日志。"""
        log: List[str] = []
        last = ParseResult(False, error="not_executed")
        for attempt in range(1, self.policy.max_attempts + 1):
            try:
                raw = call()
            except TimeoutError:
                last = ParseResult(False, error="timeout")
                log.append(f"attempt {attempt}: timeout")
            except Exception as exc:  # noqa: BLE001
                last = ParseResult(False, error=f"exception: {exc}")
                log.append(f"attempt {attempt}: exception {exc}")
            else:
                last = self.parse(raw)
                log.append(f"attempt {attempt}: {'ok' if last.ok else last.error}")
            if last.ok:
                return last, log
            reason = (last.error or "").split(":")[0]
            if reason not in self.policy.retryable:
                break
        return last, log


if __name__ == "__main__":
    samples: List[Any] = [
        '{"tool": "search", "hits": 3}',
        "not json",
        "",
        {"tool": "calc", "value": 42},
    ]
    parser = ToolResultParser(RetryPolicy(max_attempts=2))
    for item in samples:
        result = parser.parse(item)
        print(f"input={item!r} -> ok={result.ok} data={result.data} err={result.error}")

    queue = iter(["timeout-dummy", '{"ok": true}'])

    def flaky_call() -> Any:
        value = next(queue)
        if value == "timeout-dummy":
            raise TimeoutError("simulated")
        return value

    final, errors = parser.run_with_retry(flaky_call)
    print("final:", final)
    print("log:", errors)
