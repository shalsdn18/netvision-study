# PrivAI 로컬 PoC

## 실행

이 폴더에서 다음 명령을 실행합니다.

```powershell
python -m http.server 8080 --bind 127.0.0.1
```

브라우저에서 `http://localhost:8080/PrivAI_v050_clean.html`을 엽니다.

## 검증 순서

1. `test-data`의 비민감 Markdown 파일을 등록합니다.
2. Hybrid 검색으로 카메라·네트워크 장애 질의를 실행합니다.
3. WebLLM을 사용할 수 없으면 추출형 답변으로 전환되는지 확인합니다.
4. Network 탭에서 WALT, 프록시, 텔레메트리 요청이 없는지 확인합니다.

현재 CDN 기반 PDF.js, Mammoth, WebLLM 모듈·모델 다운로드는 외부 정적 에셋 예외입니다. 완전 폐쇄망은 해당 에셋을 로컬 번들한 후 별도 검증합니다.
