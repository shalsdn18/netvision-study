"""Small in-memory RAG service backed by the local Ollama API."""

from __future__ import annotations

import asyncio
import math
from dataclasses import dataclass
from pathlib import Path

import httpx


class RagServiceError(RuntimeError):
    """Raised when local documents or Ollama cannot satisfy a RAG request."""


@dataclass(frozen=True)
class IndexedChunk:
    source: str
    chunk_id: int
    text: str
    embedding: list[float]


class LocalRagService:
    def __init__(
        self,
        documents_dir: Path,
        ollama_url: str,
        generation_model: str,
        embedding_model: str,
    ) -> None:
        self.documents_dir = documents_dir
        self.ollama_url = ollama_url.rstrip("/")
        self.generation_model = generation_model
        self.embedding_model = embedding_model
        self._chunks: list[IndexedChunk] = []
        self._index_lock = asyncio.Lock()

    @property
    def indexed(self) -> bool:
        return bool(self._chunks)

    async def rebuild_index(self) -> dict[str, object]:
        async with self._index_lock:
            document_chunks: list[tuple[str, int, str]] = []
            files = sorted(
                path
                for path in self.documents_dir.glob("**/*")
                if path.is_file() and path.suffix.lower() in {".md", ".txt"}
            )

            for path in files:
                text = path.read_text(encoding="utf-8-sig")
                relative_source = path.relative_to(self.documents_dir).as_posix()
                for chunk_id, chunk in enumerate(_split_text(text), start=1):
                    document_chunks.append((relative_source, chunk_id, chunk))

            if not document_chunks:
                raise RagServiceError(
                    f"색인할 .md 또는 .txt 문서가 없습니다: {self.documents_dir}"
                )

            embeddings = await self._embed([item[2] for item in document_chunks])
            if len(embeddings) != len(document_chunks):
                raise RagServiceError("Ollama가 문서 조각 수와 다른 임베딩 수를 반환했습니다.")

            self._chunks = [
                IndexedChunk(source, chunk_id, text, embedding)
                for (source, chunk_id, text), embedding in zip(
                    document_chunks, embeddings, strict=True
                )
            ]

            return {
                "indexed_files": len(files),
                "indexed_chunks": len(self._chunks),
                "embedding_model": self.embedding_model,
                "documents_dir": str(self.documents_dir),
            }

    async def ask(self, question: str, top_k: int) -> dict[str, object]:
        if not self.indexed:
            await self.rebuild_index()

        question_embedding = (await self._embed([question]))[0]
        ranked = sorted(
            (
                (_cosine_similarity(question_embedding, chunk.embedding), chunk)
                for chunk in self._chunks
            ),
            key=lambda item: item[0],
            reverse=True,
        )[: min(top_k, len(self._chunks))]

        context_parts = []
        sources = []
        for rank, (score, chunk) in enumerate(ranked, start=1):
            label = f"{chunk.source}#chunk-{chunk.chunk_id}"
            context_parts.append(f"[자료 {rank}: {label}]\n{chunk.text}")
            sources.append(
                {
                    "source": chunk.source,
                    "chunk_id": chunk.chunk_id,
                    "score": round(score, 4),
                    "excerpt": chunk.text[:200],
                }
            )

        prompt = (
            "아래 참고자료만 근거로 질문에 한국어로 답하세요. "
            "참고자료에 답이 없으면 '자료에서 확인할 수 없습니다'라고 답하세요. "
            "답변 마지막에는 사용한 파일명을 [출처: 파일명] 형식으로 표시하세요.\n\n"
            + "\n\n".join(context_parts)
            + f"\n\n[질문]\n{question}"
        )
        answer, metrics = await self._generate(prompt)
        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "generation_model": self.generation_model,
            "embedding_model": self.embedding_model,
            "metrics": metrics,
        }

    async def _embed(self, texts: list[str]) -> list[list[float]]:
        url = f"{self.ollama_url}/api/embed"
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    url,
                    json={"model": self.embedding_model, "input": texts},
                )
                response.raise_for_status()
        except httpx.RequestError as exc:
            raise RagServiceError(f"Ollama 임베딩 호출 실패 ({url}): {exc}") from exc
        except httpx.HTTPStatusError as exc:
            raise RagServiceError(
                f"Ollama 임베딩 오류 응답: {exc.response.text}"
            ) from exc

        embeddings = response.json().get("embeddings")
        if not isinstance(embeddings, list) or not embeddings:
            raise RagServiceError("Ollama 임베딩 응답에 embeddings가 없습니다.")
        return embeddings

    async def _generate(self, prompt: str) -> tuple[str, dict[str, object]]:
        url = f"{self.ollama_url}/api/generate"
        try:
            async with httpx.AsyncClient(timeout=180.0) as client:
                response = await client.post(
                    url,
                    json={
                        "model": self.generation_model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0, "num_ctx": 4096},
                    },
                )
                response.raise_for_status()
        except httpx.RequestError as exc:
            raise RagServiceError(f"Ollama 생성 호출 실패 ({url}): {exc}") from exc
        except httpx.HTTPStatusError as exc:
            raise RagServiceError(
                f"Ollama 생성 오류 응답: {exc.response.text}"
            ) from exc

        data = response.json()
        answer = data.get("response")
        if not isinstance(answer, str) or not answer.strip():
            raise RagServiceError("Ollama 생성 응답에 response가 없습니다.")

        eval_count = data.get("eval_count") or 0
        eval_duration = data.get("eval_duration") or 0
        tokens_per_second = (
            round(eval_count / (eval_duration / 1_000_000_000), 2)
            if eval_count and eval_duration
            else None
        )
        return answer.strip(), {
            "total_seconds": round((data.get("total_duration") or 0) / 1_000_000_000, 2),
            "output_tokens": eval_count,
            "tokens_per_second": tokens_per_second,
        }


def _split_text(text: str, max_chars: int = 700, overlap: int = 100) -> list[str]:
    normalized = "\n".join(line.rstrip() for line in text.splitlines()).strip()
    if not normalized:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = min(start + max_chars, len(normalized))
        if end < len(normalized):
            boundary = max(
                normalized.rfind("\n", start + max_chars // 2, end),
                normalized.rfind(" ", start + max_chars // 2, end),
            )
            if boundary > start:
                end = boundary

        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(normalized):
            break
        start = max(end - overlap, start + 1)

    return chunks


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise RagServiceError("질문과 문서 임베딩의 차원이 다릅니다.")
    dot_product = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot_product / (left_norm * right_norm)
