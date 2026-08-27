"""
App A - FastAPI 서비스 A

우선순위 1 산출물: 독립적으로 실행되는 FastAPI 애플리케이션과
그에 딸린 엔드포인트들.

우선순위 2 산출물: httpx를 이용해 서비스 B(app_b)를 REST로 호출하는
GET/POST 엔드포인트 (/b/health, /b/process).

실행:
    uvicorn app_a.main:app --reload --port 8001

서비스 B의 주소는 환경 변수 SERVICE_B_URL로 바꿀 수 있습니다
(기본값: http://127.0.0.1:8002).
"""
from __future__ import annotations

import os
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

SERVICE_B_URL = os.environ.get("SERVICE_B_URL", "http://127.0.0.1:8002")

app = FastAPI(
    title="Service A",
    description="FastAPI A/B 실습용 - 서비스 A",
    version="0.2.0",
)

# 아주 단순한 인메모리 저장소 (재시작하면 초기화됨)
_ITEMS: dict[int, "Item"] = {}
_NEXT_ID = 1


class Item(BaseModel):
    name: str
    description: Optional[str] = None


class ItemOut(Item):
    id: int
    created_by: str = "service-a"


@app.get("/")
def root():
    return {"service": "A", "status": "ok", "message": "Service A is running"}


@app.get("/health")
def health():
    return {"status": "healthy", "service": "A"}


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
# 우선순위 2: A -> B REST 호출
# ---------------------------------------------------------------------------

class CallBRequest(BaseModel):
    text: str


@app.get("/b/health")
async def call_b_health():
    """A가 B의 GET /health를 REST로 호출해 그대로 전달한다."""
    url = f"{SERVICE_B_URL}/health"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502, detail=f"Service B 호출 실패 ({url}): {exc}"
        ) from exc
    return {
        "called_by": "service-a",
        "target": url,
        "status_code": resp.status_code,
        "response_from_b": resp.json(),
    }


@app.post("/b/process")
async def call_b_process(req: CallBRequest):
    """A가 B의 POST /process를 REST로 호출해 그대로 전달한다."""
    url = f"{SERVICE_B_URL}/process"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(url, json={"text": req.text})
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502, detail=f"Service B 호출 실패 ({url}): {exc}"
        ) from exc
    return {
        "called_by": "service-a",
        "target": url,
        "status_code": resp.status_code,
        "response_from_b": resp.json(),
    }


# ---------------------------------------------------------------------------
# 우선순위 3: A -> B -> C 체인
# ---------------------------------------------------------------------------

class PipelineRequest(BaseModel):
    text: str


@app.post("/pipeline")
async def pipeline(req: PipelineRequest):
    """A가 B의 /pipeline을 호출하면, B는 다시 C의 /store를 호출한다.
    한 번의 호출로 A -> B -> C 전체 체인이 실행된다."""
    url = f"{SERVICE_B_URL}/pipeline"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(url, json={"text": req.text, "path": ["A"]})
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502, detail=f"Service B 호출 실패 ({url}): {exc}"
        ) from exc
    return {
        "chain": "A -> B -> C",
        "called_by": "service-a",
        "target": url,
        "status_code": resp.status_code,
        "response_from_b": resp.json(),
    }
