"""
RAG 检索增强的 Agent 知识检索器
Auto-generated module skeleton.
"""

"""RAG 检索增强的 Agent 知识检索器 (2026-11-24)。"""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Callable, Iterable, List, Sequence


@dataclass
class Document:
    """知识库中的一条文档。"""
    doc_id: str
    text: str


def _tokens(text: str) -> List[str]:
    return re.findall(r"\w+", text.lower())


class TfIdfIndex:
    """轻量 TF-IDF 索引，用于文档召回。"""

    def __init__(self, docs: Sequence[Document]) -> None:
        self.docs = list(docs)
        self._tf: List[Counter[str]] = [Counter(_tokens(d.text)) for d in self.docs]
        df: Counter[str] = Counter()
        for tf in self._tf:
            df.update(tf.keys())
        n = max(len(self.docs), 1)
        self._idf = {t: math.log((n + 1) / (c + 1)) + 1.0 for t, c in df.items()}

    def _score(self, query: str, idx: int) -> float:
        q = Counter(_tokens(query))
        tf = self._tf[idx]
        return sum(q[t] * tf[t] * self._idf.get(t, 1.0) ** 2 for t in q if t in tf)

    def search(self, query: str, top_k: int = 3) -> List[Document]:
        """返回与查询最相关的 top_k 文档。"""
        ranked = sorted(range(len(self.docs)), key=lambda i: self._score(query, i), reverse=True)
        return [self.docs[i] for i in ranked[:top_k] if self._score(query, i) > 0]


def llm(prompt: str) -> str:
    """LLM 调用的占位函数。"""
    return f"[LLM 回答] 基于以下上下文：{prompt[:120]}"


class RAGRetriever:
    """RAG 检索增强的 Agent 知识检索器：召回文档并拼接上下文交给 LLM。"""

    def __init__(self, docs: Iterable[Document], top_k: int = 3, max_chars: int = 800) -> None:
        self.index = TfIdfIndex(list(docs))
        self.top_k = top_k
        self.max_chars = max_chars

    def retrieve(self, query: str) -> List[Document]:
        """检索与查询相关的文档。"""
        return self.index.search(query, self.top_k)

    def build_context(self, query: str) -> str:
        """将召回文档拼接为受长度限制的上下文字符串。"""
        parts: List[str] = []
        total = 0
        for doc in self.retrieve(query):
            chunk = f"[{doc.doc_id}] {doc.text}"
            if total + len(chunk) > self.max_chars:
                break
            parts.append(chunk)
            total += len(chunk)
        return "\n".join(parts)

    def answer(self, query: str, generator: Callable[[str], str] = llm) -> str:
        """检索增强后调用生成器回答问题。"""
        context = self.build_context(query)
        prompt = f"问题：{query}\n上下文：\n{context}\n请作答。"
        return generator(prompt)


if __name__ == "__main__":
    knowledge = [
        Document("d1", "RAG 通过检索外部知识增强大模型的回答准确性。"),
        Document("d2", "Agent 可以调用工具并规划多步任务。"),
        Document("d3", "TF-IDF 是一种经典的文本相关性排序方法。"),
        Document("d4", "向量数据库常用于语义检索。"),
    ]
    rag = RAGRetriever(knowledge)
    q = "RAG 如何增强回答？"
    print("召回：", [d.doc_id for d in rag.retrieve(q)])
    print(rag.answer(q))
