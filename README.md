# netvision-study

NetVision Telecom 개발·학습 공동 프로젝트 저장소입니다.

## 폴더 구조

```text
netvision-study/
├─ src/                         # 팀 공통 코드
├─ practice/                    # 팀원별 개인 실습 코드
│  ├─ minwoo/
│  ├─ changuk/
│  ├─ jihun/
│  └─ sehyeon/
├─ docs/                        # 문서와 연구 기록
│  ├─ minwoo/
│  ├─ changuk/
│  ├─ jihun/
│  ├─ sehyeon/
│  └─ professor_kim/            # 김완석 박사님 자료 및 검토 기록
├─ presentation/                # 팀 발표자료
├─ references/                  # 교육자료, 논문 및 외부 참고자료
├─ .gitignore
└─ README.md
```

## 작업 규칙

1. 팀이 함께 사용하는 구현은 `src/`에 작성합니다.
2. 개인별 실험과 학습 코드는 `practice/<이름>/`에 작성합니다.
3. 개인 문서와 연구 기록은 `docs/<이름>/`에 작성합니다.
4. 김완석 박사님 제공 자료와 검토 기록은 `docs/professor_kim/`에서 관리합니다.
5. 팀 발표자료는 `presentation/`, 교육자료와 외부 참고자료는 `references/`에서 관리합니다.
6. 비밀번호, API 키, `.env` 등 민감정보는 커밋하지 않습니다.
7. 공통 코드 변경은 담당 브랜치에서 작업하고 검토 후 `main`에 반영합니다.
8. 다른 팀원의 개인 폴더를 변경할 때는 사전에 공유합니다.

## 브랜치 운영

- `main`: 검토가 완료된 공통 결과물을 유지하는 기준 브랜치
- `minwoo`: Minwoo의 현재 작업 브랜치

새 브랜치가 필요하면 최신 `main`을 기준으로 생성하고, 작업 내용을 검토한 뒤 `main`에 병합합니다.
