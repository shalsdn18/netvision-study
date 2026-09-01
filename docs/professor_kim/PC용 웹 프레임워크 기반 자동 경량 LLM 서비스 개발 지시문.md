# PC용 웹 프레임워크 기반 자동 경량 LLM 서비스 개발 지시문  
## Transformers 직접 실행 방식 v2.0

---

## 1. 개발 목적

Python과 Flask를 사용하여 PC에서 직접 실행되는 경량 LLM 웹서비스를 구현한다.

프로그램은 실행되는 PC의 운영체제, CPU, 메모리, NVIDIA GPU, GPU 메모리 및 저장 공간을 자동으로 확인하고, 현재 환경에서 안정적으로 실행할 수 있는 경량 언어모델을 자동으로 선택·다운로드·검증·로드한다.

사용자는 웹브라우저에서 질문을 입력하고 답변을 받을 수 있어야 한다.

사용자가 다음 항목을 직접 설정하지 않아도 자동으로 동작해야 한다.

- 모델 종류
- 모델 크기
- 모델 저장 형식
- CPU 또는 GPU 사용 여부
- 메모리 사용량
- 연산 정밀도
- 최대 문맥 길이
- 생성 토큰 수
- 모델 저장 위치

LLM 실행에는 다음 도구를 사용하지 않는다.

- `llama-cpp-python`
- `llama-server`
- 별도의 LLM 실행 서버
- GGUF 모델

LLM은 Python 프로그램 내부에서 다음 라이브러리를 통해 직접 실행한다.

- PyTorch
- Hugging Face Transformers
- Safetensors
- Hugging Face Hub

---

## 2. 단일 파일 구현 원칙

전체 프로그램은 반드시 다음 한 파일로 작성한다.

```text
app.py
```

다음 파일은 별도로 만들지 않는다.

- 별도 Python 모듈
- HTML 파일
- CSS 파일
- JavaScript 파일
- 설정 파일
- `requirements.txt`
- 별도 모델 실행 서버
- 별도 API 서버

다음 내용을 모두 `app.py` 안에 포함한다.

- Flask 웹서버
- PC 환경 탐지
- 승인 모델 목록
- 모델 자동 선택
- 모델 다운로드
- 모델 파일 검증
- 모델 로드
- CPU·GPU 자동 전환
- 질문과 답변 처리
- HTML 화면
- CSS 디자인
- JavaScript 기능
- 상태 API
- 모델 재선택 API
- 오류 처리
- 로그 처리
- 프로그램 실행 코드

모델과 실행 중 생성되는 데이터는 다음 폴더에 저장할 수 있다.

```text
data/
├─ models/
├─ cache/
└─ manifests/

logs/
└─ app.log
```

이 폴더들은 프로그램 실행 시 자동으로 생성한다.

---

## 3. 전체 실행 구조

```text
웹브라우저
    ↓
Flask 웹 프레임워크
    ↓
PC 환경 자동 확인
    ↓
승인된 경량 LLM 자동 선택
    ↓
Hugging Face 모델 자동 다운로드
    ↓
Safetensors 파일 검증
    ↓
Transformers와 PyTorch로 모델 직접 로드
    ↓
질문 처리
    ↓
웹브라우저에 답변 표시
```

LLM은 Flask와 같은 Python 프로세스 안에서 직접 실행한다.

별도의 실행 파일이나 하위 서버 프로세스를 사용하지 않는다.

---

## 4. 기본 개발 환경

다음 환경을 기본으로 한다.

- Python 3.10 이상
- Flask
- psutil
- requests
- PyTorch
- Transformers
- Accelerate
- Safetensors
- huggingface-hub
- Waitress
- Windows 지원
- Linux 지원
- CPU 전용 PC 지원
- NVIDIA GPU 자동 지원
- 인터넷이 없으면 기존 로컬 모델 사용

필요한 패키지는 다음 명령으로 설치한다.

```bash
pip install flask psutil requests waitress torch transformers accelerate safetensors huggingface_hub
```

별도의 `requirements.txt` 파일은 만들지 않는다.

프로그램 시작 시 필요한 패키지가 설치되어 있는지 확인한다.

누락된 패키지가 있으면 서버 전체를 강제 종료하지 말고 웹 화면과 콘솔에 설치 명령을 안내한다.

---

## 5. 모델 형식

모델은 Hugging Face Transformers에서 직접 실행할 수 있는 형식을 사용한다.

기본 형식은 다음과 같다.

```text
config.json
tokenizer.json
tokenizer_config.json
generation_config.json
*.safetensors
*.safetensors.index.json
special_tokens_map.json
```

모델 가중치는 가능한 경우 반드시 Safetensors 형식을 사용한다.

다음 형식은 자동 실행 대상으로 사용하지 않는다.

- 임의 Pickle 모델
- 출처가 불분명한 `.bin`
- 임의 Python 코드가 포함된 모델
- 원격 사용자 코드 실행이 필요한 모델
- GGUF
- GPTQ 전용 모델
- AWQ 전용 모델
- EXL2 모델

기본적으로 다음 설정을 사용한다.

```python
trust_remote_code=False
use_safetensors=True
```

---

## 6. 승인된 모델 목록

인터넷에서 임의의 모델을 검색하거나 자동 실행하지 않는다.

검증된 승인 모델 목록을 `app.py` 안의 Python 리스트 또는 딕셔너리로 작성한다.

예:

```python
MODEL_REGISTRY = [
    {
        "id": "qwen25-05b",
        "name": "Qwen2.5 0.5B Instruct",
        "repository": "Qwen/Qwen2.5-0.5B-Instruct",
        "revision": "고정된 커밋 해시",
        "parameters": "0.5B",
        "format": "Safetensors",
        "minimum_ram_gb": 4,
        "recommended_ram_gb": 6,
        "minimum_vram_gb": 0,
        "estimated_ram_gb": 2.5,
        "estimated_vram_gb": 2.0,
        "context_length": 2048,
        "maximum_context_length": 8192,
        "korean_support": True,
        "quality_score": 1,
        "license": "Apache-2.0",
        "allow_cpu": True,
        "allow_gpu": True
    }
]
```

각 모델 정보에는 다음 항목을 포함한다.

- 내부 모델 ID
- 모델 이름
- Hugging Face 저장소
- 고정된 리비전 또는 커밋 해시
- 매개변수 규모
- 모델 형식
- 최소 메모리
- 권장 메모리
- 예상 CPU 메모리 사용량
- 예상 GPU 메모리 사용량
- 최소 GPU 메모리
- 기본 문맥 길이
- 최대 문맥 길이
- 한국어 지원 여부
- 품질 우선순위
- 라이선스
- CPU 실행 허용 여부
- GPU 실행 허용 여부

모델 목록은 최소 다음 규모를 포함한다.

```text
0.5B
1.5B
3B
```

7B 이상 모델은 기본 자동 선택 대상에서 제외하거나, 메모리가 충분한 PC에서만 선택하게 한다.

항상 가장 큰 모델을 선택하지 않는다.

---

## 7. 모델 보안 기준

모델은 반드시 다음 조건을 만족해야 한다.

- 승인된 Hugging Face 저장소
- 승인된 고정 리비전
- Safetensors 형식
- 라이선스 확인
- `trust_remote_code=False`
- 임의 Python 코드 실행 없음
- 다운로드 파일 목록 제한
- 모델 폴더 외부 경로 접근 금지
- 불필요한 파일 다운로드 금지

모델 저장소의 최신 버전을 자동으로 따라가지 않는다.

반드시 승인된 리비전 또는 커밋 해시를 고정한다.

예:

```python
revision="승인된 커밋 해시"
```

---

## 8. PC 환경 자동 탐지

프로그램 시작 시 다음 정보를 자동 확인한다.

- 운영체제
- 운영체제 버전
- CPU 이름
- CPU 논리 코어 수
- CPU 물리 코어 수
- 전체 메모리
- 사용 가능한 메모리
- Python 버전
- PyTorch 버전
- CUDA 사용 가능 여부
- NVIDIA GPU 유무
- GPU 이름
- GPU 메모리
- GPU 사용 가능한 메모리
- 저장 공간
- 기존 다운로드 모델
- 인터넷 연결 여부

NVIDIA GPU 정보는 다음 순서로 확인한다.

```text
① torch.cuda.is_available()
② torch.cuda.get_device_name()
③ torch.cuda.mem_get_info()
④ 필요하면 nvidia-smi 보조 확인
```

`nvidia-smi`가 없더라도 PyTorch CUDA가 정상 동작하면 GPU를 사용할 수 있어야 한다.

환경 결과는 다음처럼 표시한다.

```text
운영체제: Windows
CPU: Intel Core i7
CPU 코어: 8
전체 메모리: 16GB
사용 가능 메모리: 10GB
GPU: NVIDIA RTX 3060
GPU 메모리: 12GB
PyTorch CUDA: 사용 가능
선택 모델: Qwen2.5 1.5B Instruct
실행 방식: GPU
연산 정밀도: float16
```

이 정보는 웹 화면과 로그에 기록한다.

---

## 9. 모델 자동 선택

현재 PC 환경과 승인 모델 목록을 비교하여 안정적으로 실행 가능한 모델을 선택한다.

기본 메모리 기준은 다음과 같다.

```text
사용 가능 메모리 4GB 미만
→ 모델 실행 불가 안내

사용 가능 메모리 4~8GB
→ 0.5B 모델

사용 가능 메모리 8~16GB
→ 0.5B 또는 1.5B 모델

사용 가능 메모리 16~32GB
→ 1.5B 또는 3B 모델

사용 가능 메모리 32GB 이상
→ 3B 이상 모델 검토
```

GPU 기준은 다음과 같다.

```text
CUDA 사용 불가
→ CPU 모드

GPU 사용 가능 메모리 3GB 미만
→ CPU 모드 또는 0.5B 모델

GPU 사용 가능 메모리 3~6GB
→ 0.5B 또는 1.5B 모델

GPU 사용 가능 메모리 6~10GB
→ 1.5B 또는 3B 모델

GPU 사용 가능 메모리 10GB 이상
→ 3B 이상 모델 검토
```

안정성 기준은 다음과 같다.

```text
예상 모델 메모리 사용량
≤ 현재 사용 가능한 메모리의 65%
```

운영체제와 다른 프로그램을 위해 충분한 메모리를 남긴다.

적합한 모델이 여러 개이면 다음 순서로 선택한다.

1. 한국어 지원
2. 안정적 메모리 사용
3. 현재 장치에서 실행 가능
4. 모델 품질
5. 작은 다운로드 용량
6. 라이선스 조건
7. 빠른 응답 속도

---

## 10. 실행 장치 자동 선택

모델 실행 장치는 자동 결정한다.

가능한 실행 방식:

```text
CUDA GPU
CPU
```

Apple MPS는 선택적으로 지원할 수 있으나 필수는 아니다.

NVIDIA GPU가 정상 동작하면 우선 GPU를 사용한다.

예:

```python
device = "cuda"
torch_dtype = torch.float16
```

CPU에서는 다음을 사용한다.

```python
device = "cpu"
torch_dtype = torch.float32
```

CPU에서 `float16`을 강제로 사용하지 않는다.

GPU가 있어도 메모리가 부족하면 CPU로 자동 전환한다.

---

## 11. 모델 자동 다운로드

선택된 모델이 로컬에 없으면 자동 다운로드한다.

저장 위치:

```text
data/models/<모델ID>/
```

동작 순서:

```text
① 모델 폴더 생성
② 로컬 모델 존재 여부 확인
③ 승인된 리비전 확인
④ 필요한 파일 목록 확인
⑤ 다운로드 시작
⑥ 다운로드 진행 상태 저장
⑦ 모든 파일 다운로드
⑧ Safetensors 파일 검증
⑨ 매니페스트 생성
⑩ 검증 성공 시 사용 가능 상태로 변경
```

다운로드는 `huggingface_hub`를 사용한다.

예:

```python
snapshot_download(
    repo_id=model_info["repository"],
    revision=model_info["revision"],
    local_dir=model_path,
    local_dir_use_symlinks=False,
    allow_patterns=[
        "*.json",
        "*.safetensors",
        "*.model",
        "*.txt"
    ]
)
```

심볼릭 링크에 의존하지 않는다.

다운로드 중에는 웹 화면에서 다음 상태를 표시한다.

```text
모델 다운로드 준비 중
모델 파일 다운로드 중
다운로드 완료
모델 파일 검증 중
```

가능하면 파일 수 또는 다운로드된 바이트를 기준으로 진행률을 표시한다.

정확한 진행률을 계산할 수 없으면 단계별 상태를 표시한다.

---

## 12. 모델 파일 검증

다운로드가 완료되면 모델 파일을 검증한다.

검증 항목:

- 필수 설정 파일 존재
- 토크나이저 파일 존재
- Safetensors 파일 존재
- 파일 크기 정상 여부
- 승인 리비전 일치 여부
- 다운로드 완료 여부
- 임시 파일 잔존 여부
- 파일 경로가 모델 폴더 내부인지 확인
- Safetensors 헤더 읽기 가능 여부

가능한 경우 승인된 SHA-256 매니페스트를 사용한다.

매니페스트 예:

```python
MODEL_FILE_HASHES = {
    "model-00001-of-00002.safetensors": "실제 SHA-256 값",
    "model-00002-of-00002.safetensors": "실제 SHA-256 값"
}
```

SHA-256 값이 등록된 파일은 반드시 검증한다.

검증값이 다르면 다음과 같이 처리한다.

- 손상 파일 삭제
- 모델 로드 금지
- 사용자에게 간단한 오류 표시
- 상세 오류 로그 기록
- 재다운로드 가능 상태로 전환

SHA-256 목록이 없는 경우에도 다음 조건은 반드시 검사한다.

- 고정된 승인 리비전에서 다운로드되었는지
- Safetensors 형식인지
- 필수 파일이 모두 존재하는지
- 임시 파일이 아닌지

---

## 13. 인터넷 연결이 없는 경우

인터넷 연결이 없을 때 다음처럼 처리한다.

```text
검증된 로컬 모델 있음
→ 로컬 모델 실행

검증되지 않은 로컬 모델만 있음
→ 실행 금지

저장된 모델 없음
→ 인터넷 연결 필요 안내
```

인터넷 연결 여부만으로 프로그램을 종료하지 않는다.

웹 UI와 상태 API는 계속 동작해야 한다.

---

## 14. 모델 자동 로드

모델은 Transformers와 PyTorch를 사용하여 직접 로드한다.

예:

```python
tokenizer = AutoTokenizer.from_pretrained(
    model_path,
    local_files_only=True,
    trust_remote_code=False
)

model = AutoModelForCausalLM.from_pretrained(
    model_path,
    local_files_only=True,
    trust_remote_code=False,
    use_safetensors=True,
    torch_dtype=torch_dtype,
    low_cpu_mem_usage=True
)
```

GPU 사용 시:

```python
model.to("cuda")
```

CPU 사용 시:

```python
model.to("cpu")
```

모델 로드 후 반드시 평가 모드로 전환한다.

```python
model.eval()
```

추론 시 다음을 사용한다.

```python
with torch.inference_mode():
    ...
```

모델은 프로그램 실행 중 한 번만 로드한다.

질문을 받을 때마다 다시 로드하지 않는다.

---

## 15. 모델 로드 자동 설정

PC 환경에 따라 다음 값을 자동 결정한다.

- 실행 장치
- 연산 정밀도
- 문맥 길이
- 최대 입력 길이
- 최대 출력 토큰
- 샘플링 온도
- `top_p`
- `top_k`
- 반복 억제값
- CPU 스레드 수

CPU 스레드는 전체 코어를 모두 사용하지 않는다.

예:

```text
4코어 CPU → 3개 사용
8코어 CPU → 6개 사용
16코어 CPU → 12개 사용
```

PyTorch CPU 스레드는 다음과 같이 설정할 수 있다.

```python
torch.set_num_threads(thread_count)
```

기본 생성값 예:

```python
GENERATION_CONFIG = {
    "max_new_tokens": 384,
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "repetition_penalty": 1.1,
    "do_sample": True
}
```

낮은 메모리 환경에서는 다음 값을 축소한다.

- 문맥 길이
- 최대 입력 토큰
- 최대 출력 토큰

---

## 16. 채팅 프롬프트 처리

가능하면 토크나이저의 채팅 템플릿을 사용한다.

예:

```python
messages = [
    {
        "role": "system",
        "content": "당신은 정확하고 친절하게 한국어로 답변하는 AI입니다."
    },
    {
        "role": "user",
        "content": question
    }
]

prompt = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)
```

채팅 템플릿이 없는 모델은 안전한 기본 프롬프트를 사용한다.

질문과 시스템 메시지가 출력 답변에 그대로 반복되지 않도록 생성된 새 토큰 부분만 디코딩한다.

---

## 17. 모델 로드 실패 처리

모델 로드에 실패하면 자동으로 다음 순서로 재시도한다.

```text
① GPU 캐시 해제
② GPU에서 같은 모델 다시 시도
③ CPU 모드로 전환
④ 문맥 길이 축소
⑤ 출력 토큰 수 축소
⑥ 현재 모델 해제
⑦ 더 작은 모델 선택
⑧ 로컬 모델 재검증
⑨ 모두 실패하면 오류 상태 유지
```

GPU 메모리 정리는 다음과 같이 수행한다.

```python
torch.cuda.empty_cache()
```

모델 해제 시:

```python
del model
del tokenizer
gc.collect()
```

오류가 발생해도 Flask 서버가 즉시 종료되지 않게 한다.

웹 화면과 상태 API는 계속 동작해야 한다.

---

## 18. 의존성 오류 처리

필수 라이브러리가 설치되지 않은 경우 다음 원칙을 적용한다.

```text
Flask 없음
→ 실행 불가 안내

PyTorch 또는 Transformers 없음
→ 웹 UI는 가능하면 실행
→ 모델 상태를 dependency_missing으로 표시
→ 설치 명령 제공

CUDA 지원 PyTorch 아님
→ CPU 모드로 실행
```

화면에 다음 설치 명령을 표시한다.

```bash
pip install flask psutil requests waitress torch transformers accelerate safetensors huggingface_hub
```

프로그램은 누락된 라이브러리를 사용자 승인 없이 자동 설치하지 않는다.

---

## 19. Flask 웹서비스

다음 주소를 구현한다.

### 메인 화면

```text
GET /
```

표시 내용:

- 서비스 상태
- 운영체제
- CPU 정보
- CPU 코어
- 전체 메모리
- 사용 가능 메모리
- GPU 정보
- GPU 메모리
- PyTorch 상태
- CUDA 상태
- 선택된 모델
- 모델 크기
- 모델 형식
- 라이선스
- 다운로드 상태
- 파일 검증 상태
- 모델 로드 상태
- 실행 장치
- 질문 입력창
- 질문 전송 버튼
- 답변 출력창
- 오류 메시지
- 모델 다시 선택 버튼
- 상태 새로고침 버튼
- 답변 지우기 버튼

HTML, CSS, JavaScript는 별도 파일로 만들지 않는다.

`render_template_string`을 사용한다.

```python
HTML_PAGE = """
<!doctype html>
<html lang="ko">
...
</html>
"""
```

---

## 20. UI 상태 원칙

모델이 준비되지 않았더라도 모든 버튼이 무반응 상태가 되어서는 안 된다.

각 버튼은 항상 사용자에게 결과를 알려야 한다.

예:

```text
질문 전송
→ 모델 준비 중이면 준비 상태 안내

모델 다시 선택
→ 재선택 시작 또는 처리 중 안내

상태 새로고침
→ 현재 상태 즉시 표시

답변 지우기
→ 화면 내용 초기화
```

버튼을 비활성화하는 경우 비활성화 이유를 화면에 표시한다.

UI는 다음 상태를 구분한다.

```text
starting
checking_environment
dependency_missing
selecting_model
downloading
verifying
loading
ready
generating
reloading
offline
error
```

---

## 21. 상태 API

다음 API를 구현한다.

```text
GET /api/status
```

응답 예:

```json
{
  "ok": true,
  "service": "running",
  "model_status": "ready",
  "model_name": "Qwen2.5 1.5B Instruct",
  "parameters": "1.5B",
  "format": "Safetensors",
  "device": "CUDA",
  "torch_dtype": "float16",
  "memory_available_gb": 10.2,
  "gpu_memory_available_gb": 6.4,
  "download_progress": 100,
  "verification_status": "verified",
  "message": "질문할 수 있습니다."
}
```

API는 내부 시스템 경로와 상세 예외 메시지를 노출하지 않는다.

---

## 22. 질문 API

다음 API를 구현한다.

```text
POST /api/ask
```

입력:

```json
{
  "question": "웹 프레임워크란 무엇인가?"
}
```

출력:

```json
{
  "ok": true,
  "answer": "웹 프레임워크는...",
  "model": "Qwen2.5 1.5B Instruct",
  "device": "CUDA",
  "elapsed_seconds": 2.4
}
```

적용 기준:

- 질문이 비어 있으면 실행하지 않는다.
- 질문은 문자열만 허용한다.
- 최대 4,000자로 제한한다.
- 앞뒤 공백을 제거한다.
- 모델이 준비되지 않았으면 생성하지 않는다.
- 요청 처리 시간을 기록한다.
- 생성 결과가 비어 있으면 오류로 처리한다.

모델 준비 전 응답 예:

```json
{
  "ok": false,
  "error": "모델을 준비하고 있습니다.",
  "model_status": "loading"
}
```

---

## 23. 모델 다시 선택 API

다음 API를 구현한다.

```text
POST /api/model/reload
```

동작:

```text
① 질문 처리 중인지 확인
② 현재 모델 안전하게 해제
③ GPU 캐시 정리
④ PC 환경 다시 확인
⑤ 로컬 모델 상태 확인
⑥ 적합한 모델 다시 선택
⑦ 필요하면 다운로드
⑧ 모델 파일 검증
⑨ 모델 다시 로드
```

질문 처리 중에는 즉시 재로드하지 않는다.

응답 예:

```json
{
  "ok": true,
  "message": "모델 재선택을 시작했습니다."
}
```

---

## 24. 의존성 상태 API

다음 API를 추가할 수 있다.

```text
GET /api/dependencies
```

표시 항목:

- Flask
- psutil
- requests
- torch
- transformers
- accelerate
- safetensors
- huggingface_hub
- waitress
- CUDA 지원 여부

설치되지 않은 패키지가 있으면 설치 명령을 함께 반환한다.

---

## 25. 동시 실행 방지

LLM 질문 처리, 모델 다운로드, 모델 로드는 동시에 충돌하지 않도록 잠금을 적용한다.

예:

```python
MODEL_LOCK = threading.Lock()
DOWNLOAD_LOCK = threading.Lock()
LOAD_LOCK = threading.Lock()
STATE_LOCK = threading.RLock()
```

질문 처리:

```python
with MODEL_LOCK:
    answer = run_model(question)
```

모델 재선택 중에는 질문 생성을 막는다.

질문 처리 중에는 모델을 해제하지 않는다.

다운로드 중 동일 모델을 중복 다운로드하지 않는다.

---

## 26. 백그라운드 초기화

Flask 웹 화면이 먼저 열릴 수 있도록 모델 준비 작업은 별도 스레드에서 실행할 수 있다.

예:

```text
Flask 서버 시작
→ UI 즉시 사용 가능
→ 백그라운드에서 환경 확인
→ 모델 선택
→ 모델 다운로드
→ 모델 검증
→ 모델 로드
→ ready 상태 전환
```

백그라운드 스레드에서 오류가 발생해도 Flask 서버는 계속 실행되어야 한다.

단, Flask 개발 서버의 자동 재로더는 사용하지 않는다.

---

## 27. 웹 화면 구성

화면은 단순하고 이해하기 쉽게 작성한다.

필수 영역:

```text
서비스 상태
PC 환경
PyTorch·CUDA 상태
현재 모델
모델 다운로드 상태
모델 검증 상태
모델 로드 상태
질문 입력
질문 전송
답변 출력
오류 안내
모델 다시 선택
상태 새로고침
답변 지우기
```

PC와 스마트폰에서 모두 사용할 수 있는 반응형 화면으로 작성한다.

CSS는 HTML 안의 `<style>`에 포함한다.

JavaScript는 HTML 안의 `<script>`에 포함한다.

브라우저는 일정 간격으로 `/api/status`를 호출하여 상태를 자동 갱신한다.

권장 간격:

```text
1~2초
```

---

## 28. 질문 화면 동작

질문 전송 방식:

- 질문 전송 버튼 클릭
- `Ctrl + Enter`
- 모바일에서는 전송 버튼 사용

질문 처리 중에는 중복 요청을 방지한다.

질문 처리 상태를 표시한다.

```text
답변 생성 중...
```

응답이 완료되면 다음 정보를 표시한다.

- 답변
- 사용 모델
- 실행 장치
- 처리 시간

HTML 삽입 공격을 방지하기 위해 답변은 기본적으로 텍스트로 표시한다.

---

## 29. 프로그램 실행

`app.py` 마지막 부분에 다음 실행 코드를 포함한다.

```python
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )
```

각 설정 의미:

```text
host="0.0.0.0"
→ 같은 네트워크의 다른 PC와 스마트폰에서도 접속 가능

port=5000
→ 5000번 포트 사용

debug=False
→ 디버그 기능 비활성화

use_reloader=False
→ 모델이 두 번 로드되는 문제 방지
```

현재 PC 접속 주소:

```text
http://127.0.0.1:5000/
```

같은 네트워크 기기 접속 주소:

```text
http://서버PC의내부IP:5000/
```

예:

```text
http://192.168.0.20:5000/
```

---

## 30. Waitress 운영 서버 지원

기본 실행은 Flask 방식으로 제공한다.

다음 옵션을 사용하면 Waitress로 실행한다.

```bash
python app.py --waitress
```

예:

```python
if "--waitress" in sys.argv:
    from waitress import serve

    serve(
        app,
        host="0.0.0.0",
        port=5000,
        threads=4
    )
else:
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )
```

별도의 `server.py` 파일은 만들지 않는다.

Waitress 스레드가 여러 개여도 LLM 생성은 잠금으로 한 번에 하나씩 처리한다.

---

## 31. 로그 처리

Python `logging` 모듈과 회전 로그를 사용한다.

로그 파일:

```text
logs/app.log
```

다음 내용을 기록한다.

- 프로그램 시작
- Python 버전
- 운영체제
- CPU 정보
- 메모리 정보
- GPU 정보
- PyTorch 버전
- CUDA 상태
- 선택된 모델
- 선택 이유
- 모델 다운로드 시작과 완료
- 모델 파일 검증 결과
- 모델 로드 결과
- CPU 또는 GPU 전환
- 더 작은 모델 선택
- 질문 처리 시간
- 생성 실패
- 메모리 부족 오류
- 모델 재선택
- 프로그램 종료

회전 로그 예:

```python
RotatingFileHandler(
    "logs/app.log",
    maxBytes=5 * 1024 * 1024,
    backupCount=3,
    encoding="utf-8"
)
```

사용자의 질문과 전체 답변은 기본적으로 로그에 저장하지 않는다.

필요하면 질문 길이와 처리 시간만 기록한다.

---

## 32. 보안 기준

다음 원칙을 적용한다.

- 승인된 모델만 다운로드
- 고정된 모델 리비전 사용
- Safetensors 우선 사용
- `trust_remote_code=False`
- 임의 Python 코드 실행 금지
- 사용자가 모델 주소를 입력하지 못하게 함
- 업로드 파일 실행 금지
- 시스템 명령 실행 금지
- 시스템 내부 경로 화면 노출 금지
- 상세 오류는 로그에만 기록
- 사용자 화면에는 간단한 오류만 표시
- 디버그 모드 항상 비활성화
- Flask 자동 재로더 비활성화
- 질문 길이 제한
- JSON 입력 형식 검증
- 모델 다운로드 경로 고정
- 경로 이동 공격 차단
- 외부 공개 시 인증과 HTTPS 필요 안내
- 기본 서비스는 내부 네트워크 사용을 전제로 함

---

## 33. 종료 처리

프로그램 종료 시 다음 작업을 수행한다.

```text
① 현재 요청 종료 대기
② 모델 참조 해제
③ 토크나이저 참조 해제
④ GPU 캐시 정리
⑤ 가비지 컬렉션 실행
⑥ 로그 기록
```

가능하면 `atexit` 또는 종료 신호 처리를 적용한다.

---

## 34. 실행 순서

사용자는 다음 명령만 실행하면 된다.

```bash
pip install flask psutil requests waitress torch transformers accelerate safetensors huggingface_hub
python app.py
```

프로그램은 자동으로 다음 작업을 수행한다.

```text
① 필요한 폴더 생성
② 로그 설정
③ 웹서비스 시작
④ 필수 패키지 확인
⑤ PC 환경 확인
⑥ 로컬 모델 확인
⑦ 적합한 승인 모델 선택
⑧ 모델이 없으면 다운로드
⑨ 모델 파일 검증
⑩ PyTorch로 모델 로드
⑪ CPU 또는 GPU 실행
⑫ 웹브라우저에서 질문과 답변 사용
```

---

## 35. 완료 조건

다음 조건을 모두 만족해야 한다.

1. 전체 소스는 `app.py` 한 파일이다.
2. 별도의 Python 모듈을 만들지 않는다.
3. HTML, CSS, JavaScript를 `app.py` 안에 포함한다.
4. 승인 모델 목록을 `app.py` 안에 포함한다.
5. `llama-cpp-python`을 사용하지 않는다.
6. `llama-server`를 사용하지 않는다.
7. GGUF 모델을 사용하지 않는다.
8. Transformers와 PyTorch로 모델을 직접 실행한다.
9. Safetensors 모델을 사용한다.
10. CPU만 있는 PC에서도 실행된다.
11. NVIDIA GPU가 있으면 자동 활용한다.
12. GPU 오류가 발생하면 CPU로 자동 전환한다.
13. PC 환경을 자동으로 확인한다.
14. 실행 가능한 경량 모델을 자동으로 선택한다.
15. 모델이 없으면 자동 다운로드한다.
16. 승인된 고정 모델 리비전만 사용한다.
17. 모델 파일을 검증한다.
18. 인터넷이 없어도 검증된 로컬 모델이 있으면 실행된다.
19. 모델은 한 번만 로드한다.
20. 질문마다 모델을 다시 로드하지 않는다.
21. 메모리가 부족하면 더 작은 모델을 선택한다.
22. 웹브라우저에서 질문과 답변이 가능하다.
23. 현재 모델과 실행 환경을 화면에 표시한다.
24. 다운로드·검증·로드 상태를 표시한다.
25. 모든 버튼이 정상적으로 응답한다.
26. 모델이 준비되지 않았을 때도 UI가 멈추지 않는다.
27. 동시에 여러 요청이 들어와도 모델 충돌이 발생하지 않는다.
28. 모델 재선택 중 질문 요청을 안전하게 차단한다.
29. 오류가 발생해도 웹서버 전체가 종료되지 않는다.
30. Windows와 Linux에서 실행된다.
31. `python app.py` 명령으로 실행된다.
32. `python app.py --waitress` 실행을 지원한다.
33. 로그 회전 기능을 포함한다.
34. 상세 오류를 사용자 화면에 그대로 노출하지 않는다.
35. 외부 모델 실행 서버가 없어도 LLM이 정상 작동한다.

---

## 36. 최종 구현 원칙

- 부분 코드가 아니라 완성된 `app.py` 전체 코드를 제공한다.
- 코드를 여러 파일로 나누지 않는다.
- 외부 HTML, CSS, JavaScript 파일을 만들지 않는다.
- 외부 LLM 서버를 실행하지 않는다.
- 별도의 실행 파일을 다운로드하지 않는다.
- 승인된 Hugging Face 모델만 사용한다.
- 모델 리비전을 반드시 고정한다.
- `trust_remote_code=False`를 유지한다.
- 가장 큰 모델보다 안정적으로 실행되는 모델을 선택한다.
- 운영체제와 다른 프로그램을 위한 메모리를 충분히 남긴다.
- CPU 환경에서는 무리한 모델을 선택하지 않는다.
- GPU가 있어도 메모리가 부족하면 CPU 또는 작은 모델을 사용한다.
- 각 주요 함수에 이해하기 쉬운 한글 주석을 작성한다.
- 함수 이름은 역할을 알 수 있게 작성한다.
- 중복 코드를 제거한다.
- 전역 상태는 잠금으로 보호한다.
- 오류 처리와 로그 기능을 포함한다.
- 실행 방법과 접속 주소를 `app.py` 상단 주석에 작성한다.
- 최종 출력은 설명 조각이 아니라 바로 저장하여 실행할 수 있는 단일 `app.py` 전체 코드여야 한다.