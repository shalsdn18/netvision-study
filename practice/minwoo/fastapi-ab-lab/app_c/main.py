"""
App C - FastAPI 서비스 C

우선순위 3 산출물: 세 번째 서비스를 추가해 A -> B -> C 체인(또는 상호 호출)을
구성한다. 서비스 C는 "저장소" 역할을 맡아, B가 처리한 결과를 최종적으로
저장하는 엔드포인트를 제공한다.

실행:
    uvicorn app_c.main:app --reload --port 8003
"""
from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="Service C",
    description="FastAPI A/B/C 실습용 - 서비스 C (저장소 역할)",
    version="0.1.0",
)

_STORE: dict[int, "StoreRecord"] = {}
_NEXT_ID = 1


class StoreRequest(BaseModel):
    text: str
    path: list[str] = []  # 지금까지 이 요청이 거쳐온 서비스 경로 (예: ["A", "B"])


class StoreRecord(BaseModel):
    id: int
    text: str
    path: list[str]


@app.get("/")
def root():
    return {"service": "C", "status": "ok", "message": "Service C is running"}


@app.get("/health")
def health():
    return {"status": "healthy", "service": "C"}


@app.post("/store", response_model=StoreRecord, status_code=201)
def store(req: StoreRequest):
    """B(혹은 다른 서비스)로부터 전달받은 텍스트를 최종 저장한다."""
    global _NEXT_ID
    record = StoreRecord(
        id=_NEXT_ID,
        text=req.text,
        path=req.path + ["C"],
    )
    _STORE[_NEXT_ID] = record
    _NEXT_ID += 1
    return record


@app.get("/store/{record_id}", response_model=StoreRecord)
def get_record(record_id: int):
    record = _STORE.get(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@app.get("/store", response_model=list[StoreRecord])
def list_records():
    return list(_STORE.values())
