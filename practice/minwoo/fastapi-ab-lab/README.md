# FastAPI A/B/C 실습 프로젝트

로드맵 우선순위 1~3을 반영한 결과물입니다: FastAPI로 만든 독립 애플리케이션
A, B, C가 각각 엔드포인트를 가지며, A → B → C로 이어지는 REST 호출 체인까지
구성되어 있습니다.

## 구조

```
fastapi-ab-lab/
├── requirements.txt
├── app_a/
│   ├── __init__.py
│   └── main.py      # 서비스 A (기본 포트 8001)
├── app_b/
│   ├── __init__.py
│   └── main.py      # 서비스 B (기본 포트 8002)
└── app_c/
    ├── __init__.py
    └── main.py      # 서비스 C (기본 포트 8003, 저장소 역할)
```

## 설치

```bash
pip install -r requirements.txt
```

## 실행

세 서비스는 서로 다른 포트에서 독립적으로 뜹니다. 터미널 세 개(또는 백그라운드)로 각각 실행하세요.

```bash
# 터미널 1 - 서비스 A
uvicorn app_a.main:app --reload --port 8001

# 터미널 2 - 서비스 B
uvicorn app_b.main:app --reload --port 8002

# 터미널 3 - 서비스 C
uvicorn app_c.main:app --reload --port 8003
```

각 서비스는 자동 생성된 Swagger 문서를 제공합니다:
- A: http://127.0.0.1:8001/docs
- B: http://127.0.0.1:8002/docs
- C: http://127.0.0.1:8003/docs

## 엔드포인트

### 서비스 A (포트 8001)
| Method | Path | 설명 |
|---|---|---|
| GET | `/` | 서비스 상태 확인 |
| GET | `/health` | 헬스체크 |
| POST | `/items` | 아이템 생성 (`{"name": "...", "description": "..."}`) |
| GET | `/items/{item_id}` | 아이템 조회 |
| GET | `/items` | 전체 아이템 목록 |
| GET | `/b/health` | **[우선순위 2]** A가 B의 `/health`를 REST로 호출해 결과를 전달 |
| POST | `/b/process` | **[우선순위 2]** A가 B의 `/process`를 REST로 호출해 결과를 전달 (`{"text": "..."}`) |
| POST | `/pipeline` | **[우선순위 3]** A → B → C 전체 체인을 한 번에 트리거 (`{"text": "..."}`) |

### 서비스 B (포트 8002)
| Method | Path | 설명 |
|---|---|---|
| GET | `/` | 서비스 상태 확인 |
| GET | `/health` | 헬스체크 |
| POST | `/process` | 텍스트 처리 (`{"text": "..."}` → 대문자 변환 + 길이 반환) |
| POST | `/items` | 아이템 생성 |
| GET | `/items/{item_id}` | 아이템 조회 |
| GET | `/items` | 전체 아이템 목록 |
| POST | `/pipeline` | **[우선순위 3]** 텍스트 처리 후 C의 `/store`를 REST로 호출 (B → C) |

### 서비스 C (포트 8003, 저장소 역할)
| Method | Path | 설명 |
|---|---|---|
| GET | `/` | 서비스 상태 확인 |
| GET | `/health` | 헬스체크 |
| POST | `/store` | 텍스트를 최종 저장 (`{"text": "...", "path": [...]}`) |
| GET | `/store/{id}` | 저장된 레코드 조회 |
| GET | `/store` | 전체 저장 레코드 목록 |

## 동작 확인 (curl)

```bash
curl http://127.0.0.1:8001/health
curl -X POST http://127.0.0.1:8001/items -H "Content-Type: application/json" \
  -d '{"name":"apple","description":"a fruit"}'

curl http://127.0.0.1:8002/health
curl -X POST http://127.0.0.1:8002/process -H "Content-Type: application/json" \
  -d '{"text":"hello world"}'
```

두 서비스 모두 정상 기동 및 응답을 확인했습니다 (에이전트 검증 완료).

## 우선순위 2: A → B REST 통신 확인

서비스 A는 `httpx.AsyncClient`로 서비스 B를 호출합니다. B 주소는 환경 변수
`SERVICE_B_URL`로 바꿀 수 있고, 기본값은 `http://127.0.0.1:8002` 입니다.

```bash
# A와 B를 각각 실행한 상태에서:

# GET 통신: A가 B의 /health를 대신 호출
curl http://127.0.0.1:8001/b/health

# POST 통신: A가 B의 /process를 대신 호출
curl -X POST http://127.0.0.1:8001/b/process -H "Content-Type: application/json" \
  -d '{"text":"hello from A"}'
```

실제 실행 결과 (검증 완료):

```
$ curl http://127.0.0.1:8001/b/health
{"called_by":"service-a","target":"http://127.0.0.1:8002/health","status_code":200,
 "response_from_b":{"status":"healthy","service":"B"}}

$ curl -X POST http://127.0.0.1:8001/b/process -d '{"text":"hello from A"}'
{"called_by":"service-a","target":"http://127.0.0.1:8002/process","status_code":200,
 "response_from_b":{"original":"hello from A","result":"HELLO FROM A","length":12}}
```

A가 B에게 GET/POST 요청을 보내고, B의 응답을 그대로 받아 반환하는 것까지 확인했습니다.
B가 꺼져 있으면 A는 502 에러(`Service B 호출 실패`)를 반환하도록 처리해 두었습니다.

## 우선순위 3: A → B → C 체인 확인

서비스 C(`app_c`)를 저장소 역할로 추가했습니다. B는 환경 변수 `SERVICE_C_URL`
(기본값 `http://127.0.0.1:8003`)로 C를 호출합니다. A의 `/pipeline` 하나만
호출하면 A → B → C 전체 체인이 연쇄적으로 실행됩니다. 각 서비스는 자신을
거쳐 갈 때마다 `path` 목록에 자기 이름을 추가하므로, 최종 응답의
`path`를 보면 실제로 세 서비스를 모두 거쳤는지 확인할 수 있습니다.

```bash
# A, B, C를 모두 실행한 상태에서, A의 엔드포인트 하나만 호출:
curl -X POST http://127.0.0.1:8001/pipeline -H "Content-Type: application/json" \
  -d '{"text":"hello chain"}'
```

실제 실행 결과 (검증 완료, `path` 값으로 A→B→C 경유를 확인):

```
$ curl -X POST http://127.0.0.1:8001/pipeline -d '{"text":"hello chain"}'
{
  "chain": "A -> B -> C",
  "called_by": "service-a",
  "target": "http://127.0.0.1:8002/pipeline",
  "status_code": 200,
  "response_from_b": {
    "processed_by_b": "HELLO CHAIN",
    "called": "http://127.0.0.1:8003/store",
    "status_code": 201,
    "response_from_c": {
      "id": 3,
      "text": "HELLO CHAIN",
      "path": ["A", "B", "C"]
    }
  }
}
```

C에 쌓인 전체 이력도 `GET http://127.0.0.1:8003/store`로 확인할 수 있으며,
직접 C를 호출한 요청(`path: ["C"]`)과 B를 거친 요청(`path: ["B","C"]`),
A→B→C 전체 체인을 거친 요청(`path: ["A","B","C"]`)이 모두 구분되어 저장됨을
확인했습니다. 이는 "A→B→C 또는 상호 호출" 산출물을 충족합니다.

## 우선순위 4: 로컬 Ollama 연동

`app_b`에 Ollama 호출용 엔드포인트 3개를 추가했습니다 (파일: `app_b/main.py`).
Ollama 주소와 모델은 환경 변수로 바꿀 수 있습니다.

- `OLLAMA_URL` (기본값 `http://localhost:11434`)
- `OLLAMA_MODEL` (기본값 `qwen2.5:7b-instruct-q4_K_M`)
- `OLLAMA_EMBED_MODEL` (기본값 `nomic-embed-text:latest`)

| Method | Path | 설명 |
|---|---|---|
| GET | `/llm/models` | Ollama에 받아둔 모델 목록 조회 (Ollama의 `/api/tags` 호출) |
| POST | `/llm/generate` | Ollama의 `/api/generate` 호출 (`{"prompt": "..."}`) |
| POST | `/llm/chat` | Ollama의 `/api/chat` 호출 (`{"messages": [{"role":"user","content":"..."}]}`) |

### 실행 전 준비

1. Ollama가 이미 설치되어 있는지 확인 (홈 폴더에 `.ollama`가 있는 것으로 보아 설치되어 있을 가능성이 높습니다):
   ```
   ollama --version
   ```
2. 생성 모델과 임베딩 모델을 받습니다:
   ```
   ollama pull qwen2.5:7b-instruct-q4_K_M
   ollama pull nomic-embed-text
   ```
3. Ollama 서버 실행 확인 (보통 설치 시 자동으로 백그라운드 실행됨):
   ```
   curl http://localhost:11434/api/tags
   ```
4. PowerShell에서 프로젝트 가상환경과 의존성을 준비합니다:
   ```powershell
   cd fastapi-ab-lab
   py -3.13 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```
5. 서비스 B 실행:
   ```powershell
   $env:OLLAMA_URL="http://127.0.0.1:11434"
   $env:OLLAMA_MODEL="qwen2.5:7b-instruct-q4_K_M"
   .\.venv\Scripts\python.exe -m uvicorn app_b.main:app --port 8002
   ```

### 테스트

```bash
# 받아둔 모델 목록 확인 (GET)
curl http://127.0.0.1:8002/llm/models

# 텍스트 생성 (POST)
curl -X POST http://127.0.0.1:8002/llm/generate -H "Content-Type: application/json" ^
  -d "{\"prompt\":\"한국어로 짧게 자기소개 해줘\"}"

# 채팅 형식 (POST)
curl -X POST http://127.0.0.1:8002/llm/chat -H "Content-Type: application/json" ^
  -d "{\"messages\":[{\"role\":\"user\",\"content\":\"안녕?\"}]}"
```

(Windows `cmd`에서 여러 줄 명령은 줄 끝에 `^`를 붙이거나, PowerShell에서는
`curl.exe`로 한 줄에 붙여서 실행하세요.)

실제 `/llm/generate` 호출에서 Qwen 모델의 한국어 응답과 `200 OK`를 확인했습니다.

## 우선순위 5: 7B 양자화 모델 확인

`qwen2.5:7b-instruct-q4_K_M`은 7.6B 매개변수의 Q4_K_M 양자화 모델입니다.
CPU 실행으로 한국어 49토큰을 생성했으며 실제 생성 속도는 약 5.8 tokens/s였습니다.

## 우선순위 6: 로컬 문서 기반 RAG

서비스 B는 `data/documents` 아래의 `.md`, `.txt` 문서를 검색합니다.
`nomic-embed-text`로 문서와 질문을 임베딩하고 코사인 유사도가 높은 문서 조각을
Qwen에 전달합니다. 별도 벡터 DB 없이 메모리에 색인을 보관하며, 서버를 다시
시작한 뒤 첫 질문에서는 문서를 자동으로 다시 색인합니다.

| Method | Path | 설명 |
|---|---|---|
| POST | `/rag/index` | 로컬 문서를 읽고 검색 색인을 다시 생성 |
| POST | `/rag/ask` | 관련 문서를 검색하고 근거 기반 답변과 출처 반환 |

Swagger(`http://127.0.0.1:8002/docs`)에서 먼저 `POST /rag/index`를 실행한 뒤
다음 요청으로 질의할 수 있습니다.

```json
{
  "question": "카메라 영상이 나오지 않으면 어떤 순서로 확인해야 하나요?",
  "top_k": 3
}
```

응답의 `sources`에는 답변에 사용한 파일명, 문서 조각 번호, 유사도 점수와
내용 일부가 포함됩니다. `data/documents`의 기본 자료는 기능 검증용 예시이며
실제 회사 규정이 아닙니다.

실제 검증에서는 문서 2개를 2개 조각으로 색인한 뒤 "카메라 영상이 나오지
않으면 어떤 순서로 확인해야 하나요?"라고 질문했습니다. 응답은 학습용 문서의
전원 표시등, 랜 케이블, Ping, 554번 포트, 재시작 순서를 답하고
`camera_troubleshooting.md`를 출처로 표시했습니다. 첫 질의는 모델 전환과
로딩을 포함해 약 84.9초가 걸렸고 생성 속도는 약 4.62 tokens/s였습니다.
