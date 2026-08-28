# Minwoo 실습 공간

Minwoo의 FastAPI 학습 코드, 실험 및 프로토타입을 저장합니다.

## FastAPI 프로젝트 구성

| 프로젝트 | 학습 목적 | 데이터 저장 | 주요 기능 |
| --- | --- | --- | --- |
| [`fastapi_test`](./fastapi_test/) | FastAPI 기본 문법 입문 | 코드에 정의된 딕셔너리 | `GET /items/{item_id}` 단일 조회 API |
| [`fastapi-study`](./fastapi-study/) | 카메라 관리 REST API | SQLite + SQLAlchemy | 카메라 CRUD, Ping, 포트 연결 확인 |
| [`fastapi-ab-lab`](./fastapi-ab-lab/) | 여러 서비스 사이의 REST 통신 및 LLM 연동 | 서비스별 인메모리 저장소 | A → B → C 호출 체인, Ollama generate/chat 연동 |

세 프로젝트는 일부 FastAPI 사용법이 겹치지만 학습 목적과 구조가 서로 다르므로 하나로 병합하지 않고 각각 유지합니다.

## 프로젝트별 설명

### `fastapi_test`

FastAPI의 애플리케이션 생성, 경로 매개변수, JSON 응답을 확인하는 가장 간단한 입문 예제입니다.

```powershell
cd practice/minwoo/fastapi_test
python -m uvicorn app_a:app --reload --port 8000
```

### `fastapi-study`

카메라 정보를 SQLite에 저장하는 단일 서비스 프로젝트입니다. Pydantic 스키마와 SQLAlchemy 모델을 분리했으며 다음 기능을 제공합니다.

- 카메라 목록 및 단건 조회
- 카메라 생성, 수정, 삭제
- 카메라 IP Ping 확인
- 지정 포트 연결 확인

애플리케이션을 시작하면 필요한 SQLite 테이블을 자동으로 생성합니다. 데이터베이스 경로는 실행 위치와 관계없이 프로젝트 폴더의 `cameras.db`를 사용하며, 테스트나 별도 환경에서는 `CAMERA_DATABASE_URL` 환경 변수로 변경할 수 있습니다. 샘플 카메라 데이터를 공유하기 위해 현재 `cameras.db`는 저장소에 유지합니다.

전용 가상환경을 사용할 경우 프로젝트 폴더에서 다음과 같이 실행합니다.

```powershell
cd practice/minwoo/fastapi-study
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
```

### `fastapi-ab-lab`

독립적인 FastAPI 서비스 A, B, C가 REST API로 통신하는 실습입니다.

- 서비스 A: 아이템 API와 서비스 B 호출 진입점
- 서비스 B: 텍스트 처리, 서비스 C 호출, Ollama 연동
- 서비스 C: 처리 결과 저장
- 전체 호출 흐름: A → B → C
- 로컬 RAG: 문서 임베딩, 유사도 검색, Qwen 근거 기반 답변과 출처 반환

자세한 실행 방법과 엔드포인트는 [`fastapi-ab-lab/README.md`](./fastapi-ab-lab/README.md)를 참고합니다.

## 관리 원칙

- 기초 예제, 카메라 CRUD, 멀티서비스 실습을 서로 다른 프로젝트로 유지합니다.
- 프로젝트마다 의존성과 실행 방법을 자체 README 또는 `requirements.txt`에 기록합니다.
- `.venv`, `__pycache__` 등 로컬 생성 파일은 Git에 포함하지 않습니다.
- SQLite DB는 샘플 데이터 공유가 필요한 경우에만 저장소에 포함합니다.
