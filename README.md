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
7. 작업은 개인 브랜치에서 진행하고, 실행을 검증한 뒤 Pull Request로 `main`에 반영합니다.
8. 다른 팀원의 개인 폴더를 변경할 때는 사전에 공유합니다.

## Git 운영

- `main`: 검토와 실행 확인이 끝난 결과만 유지하며 직접 작업하거나 강제 푸시하지 않습니다.
- 개인 브랜치: 각자 이름의 브랜치에서 작업합니다. 현재 Minwoo는 `minwoo`를 사용합니다.
- 한 커밋에는 하나의 목적에 해당하는 변경만 포함합니다.
- 병합 전 GitHub Pull Request의 `Files changed`에서 삭제되거나 덮어써지는 내용을 확인합니다.
- 충돌이 발생하면 한쪽 파일을 통째로 선택하지 말고 충돌 구간별로 필요한 내용을 합칩니다.

### 개인 브랜치 작업 순서

작업을 시작하기 전에 최신 `main`을 개인 브랜치에 반영합니다.

```powershell
git switch main
git pull --ff-only origin main
git switch minwoo
git merge main
```

작업과 검증을 마치면 개인 브랜치에만 푸시합니다.

```powershell
git add <변경한 파일>
git commit -m "변경 목적을 설명하는 메시지"
git push origin minwoo
```

병합 전에는 `git diff main...minwoo`와 Pull Request의 `Files changed`를 확인합니다.
여러 사람이 동시에 같은 파일을 수정해야 할 때는 작업 범위를 먼저 공유합니다.
