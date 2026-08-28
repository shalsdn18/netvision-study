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
7. 변경 전에 `main`을 최신 상태로 맞추고, 실행을 검증한 뒤 커밋·푸시합니다.
8. 다른 팀원의 개인 폴더를 변경할 때는 사전에 공유합니다.

## Git 운영

- 저장소는 `main` 단일 브랜치로 운영합니다.
- 작업을 시작하기 전에 `git pull --ff-only origin main`으로 최신 변경을 받습니다.
- 한 커밋에는 하나의 목적에 해당하는 변경만 포함합니다.
- 실행 및 문서 확인을 마친 뒤 `main`에 직접 푸시합니다.

여러 사람이 동시에 같은 파일을 수정해야 할 때는 작업 범위를 먼저 공유합니다.
