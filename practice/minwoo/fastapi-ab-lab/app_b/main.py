"""
App B - FastAPI 서비스 B

우선순위 1 산출물: 독립적으로 실행되는 FastAPI 애플리케이션과
그에 딸린 엔드포인트들.

우선순위 3 산출물: B가 다시 서비스 C를 REST로 호출하는 /pipeline
엔드포인트. A -> B -> C 체인의 가운데 연결 고리 역할을 한다.

실행:
    uvicorn app_b.main:app --reload --port 8002

서비스 B는 "무언가를 처리해주는" 워커 역할을 맡습니다.
지금은 텍스트를 간단히 변환하는 /process 엔드포인트지만,
우선순위 4~5 단계에서 이 로직을 Ollama 로컬 LLM 호출로
교체할 수 있도록 설계했습니다.

서비스 C의 주소는 환경 변수 SERVICE_C_URL로 바꿀 수 있습니다
(기본값: http://127.0.0.1:8003).
"""
from __future__ import annotations

import os
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

SERVICE_C_URL = os.environ.get("SERVICE_C_URL", "http://127.0.0.1:8003")

# 우선순위 4: 로컬 Ollama 서버 연동
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")

app = FastAPI(
    title="Service B",
    description="FastAPI A/B/C 실습용 - 서비스 B",
    version="0.2.0",
)

_ITEMS: dict[int, "Item"] = {}
_NEXT_ID = 1


class Item(BaseModel):
    name: str
    description: Optional[str] = None


class ItemOut(Item):
    id: int
    created_by: str = "service-b"


class ProcessRequest(BaseModel):
    text: str


class ProcessResponse(BaseModel):
    original: str
    result: str
    length: int


@app.get("/")
def root():
    return {"service": "B", "status": "ok", "message": "Service B is running"}


@app.get("/health")
def health():
    return {"status": "healthy", "service": "B"}


@app.post("/process", response_model=ProcessResponse)
def process(req: ProcessRequest):
    """지금은 간단한 문자열 변환. 추후 Ollama /generate 호출로 교체 예정."""
    return ProcessResponse(
        original=req.text,
        result=req.text.upper(),
        length=len(req.text),
    )


@app.post("/items", response_model=ItemOut, status_code=201)
def create_item(item: Item):
    global _NEXT_ID
    item_id = _NEXT_ID
    _NEXT_ID += 1
    out = ItemOut(id=item_id, **item.model_dump())
    _ITEMS[item_id] = out
    return out


@app.get("/items/{item_id}", response_model=ItemOut)
def get_item(item_id: int):
    item = _ITEMS.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.get("/items", response_model=list[ItemOut])
def list_items():
    return list(_ITEMS.values())


# ---------------------------------------------------------------------------
# 우선순위 3: B -> C REST 호출 (A -> B -> C 체인의 중간 구간)
# ---------------------------------------------------------------------------

class PipelineRequest(BaseModel):
    text: str
    path: list[str] = []  # 지금까지 이 요청이 거쳐온 서비스 경로


@app.post("/pipeline")
async def pipeline(req: PipelineRequest):
    """텍스트를 처리한 뒤 서비스 C에 저장을 위임한다 (B -> C 호출)."""
    processed = req.text.upper()
    path = req.path + ["B"]

    url = f"{SERVICE_C_URL}/store"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(url, json={"text": processed, "path": path})
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502, detail=f"Service C 호출 실패 ({url}): {exc}"
        ) from exc

    return {
        "processed_by_b": processed,
        "called": url,
        "status_code": resp.status_code,
        "response_from_c": resp.json(),
    }


# ---------------------------------------------------------------------------
# 우선순위 4: 로컬 Ollama LLM 서버 연동 (/generate, /chat 호출)
# ---------------------------------------------------------------------------

class GenerateRequest(BaseModel):
    prompt: str
    model: Optional[str] = None


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    model: Optional[str] = None


@app.get("/llm/models")
async def llm_models():
    """Ollama에 로컬로 받아둔 모델 목록을 조회한다 (GET 통신 확인용)."""
    url = f"{OLLAMA_URL}/api/tags"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502, detail=f"Ollama 호출 실패 ({url}): {exc}"
        ) from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502, detail=f"Ollama 오류 응답: {exc.response.text}"
        ) from exc
    return resp.json()


@app.post("/llm/generate")
async def llm_generate(req: GenerateRequest):
    """Ollama의 POST /api/generate를 호출해 텍스트를 생성한다."""
    model = req.model or OLLAMA_MODEL
    url = f"{OLLAMA_URL}/api/generate"
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                url, json={"model": model, "prompt": req.prompt, "stream": False}
            )
            resp.raise_for_status()
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Ollama 호출 실패 ({url}). Ollama가 실행 중인지, 모델을 "
                   f"pull 했는지 확인하세요. ({exc})",
        ) from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502, detail=f"Ollama 오류 응답: {exc.response.text}"
        ) from exc
    data = resp.json()
    return {
        "model": model,
        "prompt": req.prompt,
        "response": data.get("response"),
        "raw": data,
    }


@app.post("/llm/chat")
async def llm_chat(req: ChatRequest):
    """Ollama의 POST /api/chat을 호출한다."""
    model = req.model or OLLAMA_MODEL
    url = f"{OLLAMA_URL}/api/chat"
    payload = {
        "model": model,
        "messages": [m.model_dump() for m in req.messages],
        "stream": False,
    }
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Ollama 호출 실패 ({url}). Ollama가 실행 중인지, 모델을 "
                   f"pull 했는지 확인하세요. ({exc})",
        ) from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502, detail=f"Ollama 오류 응답: {exc.response.text}"
        ) from exc
    data = resp.json()
    return {
        "model": model,
        "message": data.get("message"),
        "raw": data,
    }
