---

description: "Executable task list for IP Camera Management"
---

# Tasks: IP Camera Management

**Input**: Design documents from `/specs/001-ip-camera-management/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md

**Tests**: Included because the specification requires automated coverage of core behavior and edge cases.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently after the foundational phase.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel when files and dependencies do not overlap
- **[Story]**: Maps a task to US1, US2, or US3 from spec.md
- Every task includes the exact target file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the single TypeScript REST service and its development checks.

- [x] T001 Create the Node.js project manifest and scripts in `package.json` for build, start, test, lint, and format commands
- [x] T002 [P] Configure TypeScript compiler settings in `tsconfig.json` for the `src/` and `tests/` trees
- [x] T003 [P] Configure lint and formatting rules in `eslint.config.js` and `.prettierrc.json`
- [x] T004 [P] Create the planned source and test directories with placeholder-preserving `.gitkeep` files in `src/`, `src/api/`, `src/domain/`, `src/storage/`, `src/diagnostics/`, `tests/contract/`, `tests/unit/`, and `tests/integration/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement shared boundaries required by every user story.

**Critical**: No user story implementation starts until this phase is complete.

- [x] T005 Implement environment and database path configuration in `src/config.ts`
- [x] T006 Implement SQLite connection setup, schema creation, WAL mode, and transaction helpers in `src/storage/database.ts`
- [x] T007 [P] Define Camera, NetworkDiagnosticResult, and ApiError types in `src/domain/camera.ts`
- [x] T008 [P] Define shared request, response, IPv4, and TCP port schemas in `src/api/schemas.ts`
- [x] T009 Implement stable error codes and common HTTP error mapping in `src/api/errors.ts`
- [x] T010 Implement the Fastify application factory and shared error handling in `src/app.ts`
- [x] T011 Implement the process entry point and graceful shutdown in `src/server.ts`
- [x] T012 [P] Create isolated database and application fixtures for deterministic tests in `tests/helpers/test-app.ts`
- [x] T013 [P] Add the standard test setup and test environment configuration in `tests/setup.ts`

**Checkpoint**: Shared configuration, validation schemas, error representation, application factory, and SQLite foundation are ready.

---

## Phase 3: User Story 1 - 카메라 등록 및 관리 (Priority: P1) 🎯 MVP

**Goal**: 관리자가 카메라를 등록하고 목록·상세 조회, 수정, 삭제를 수행하며 정보가 재시작 후에도 유지된다.

**Independent Test**: 계약 테스트로 유효한 카메라를 생성하고, 조회·수정·삭제한 뒤 isolated SQLite database를 다시 열어 persistence를 확인한다.

### Tests for User Story 1

- [x] T014 [P] [US1] Add CRUD contract tests for `POST /cameras`, `GET /cameras`, and `GET /cameras/{cameraId}` in `tests/contract/cameras-crud.test.ts`
- [x] T015 [P] [US1] Add update and delete contract tests for `PUT /cameras/{cameraId}` and `DELETE /cameras/{cameraId}` in `tests/contract/cameras-lifecycle.test.ts`
- [x] T016 [P] [US1] Add restart persistence integration tests in `tests/integration/camera-persistence.test.ts`

### Implementation for User Story 1

- [x] T017 [P] [US1] Implement transactional Camera CRUD queries in `src/storage/camera-repository.ts`
- [x] T018 [US1] Implement Camera management use cases and repository error translation in `src/domain/camera-service.ts` after T017
- [x] T019 [US1] Implement camera CRUD route handlers and bind them to the application in `src/api/camera-routes.ts` after T008, T009, and T018
- [x] T020 [US1] Register CRUD routes and verify response schemas against the contract in `src/app.ts` after T019
- [x] T021 [US1] Add Camera CRUD request and response examples to `contracts/openapi.yaml` after T019

**Checkpoint**: US1 independently provides the MVP camera registration and management flow.

---

## Phase 4: User Story 3 - 예외 상황 처리 (Priority: P1)

**Goal**: 잘못된 입력, 중복 ID, 존재하지 않는 카메라 요청을 저장 변경 없이 일관된 오류로 처리한다.

**Independent Test**: 오류 계약 테스트만 실행해 malformed IPv4, missing fields, invalid ports, duplicate IDs, and unknown camera IDs를 검증한다.

### Tests for User Story 3

- [ ] T022 [P] [US3] Add request schema unit tests for identifiers, names, IPv4 values, required fields, unknown fields, and TCP port range in `tests/unit/request-validation.test.ts`
- [ ] T023 [P] [US3] Add error contract tests for 400, 404, and 409 JSON responses in `tests/contract/error-responses.test.ts`
- [ ] T024 [P] [US3] Add atomicity tests proving rejected create and update requests leave SQLite data unchanged in `tests/integration/error-atomicity.test.ts`

### Implementation for User Story 3

- [ ] T025 [US3] Enforce identifier and Camera Name constraints, including the selected maximum name length, in `src/api/schemas.ts`
- [ ] T026 [US3] Map validation, duplicate, and not-found failures to the common ApiError response in `src/api/errors.ts`
- [ ] T027 [US3] Add route-level handling for unknown cameras, duplicate IDs, empty bodies, and malformed payloads in `src/api/camera-routes.ts`
- [ ] T028 [US3] Verify failed writes are rejected before persistence and preserve prior state in `src/domain/camera-service.ts`

**Checkpoint**: US1 and US3 independently satisfy the management and exception-handling requirements.

---

## Phase 5: User Story 2 - 네트워크 연결 진단 (Priority: P2)

**Goal**: 관리자가 등록된 카메라에 Ping 또는 사용자가 제공한 TCP 포트 확인을 수행하고 3초 이내에 분류된 결과를 받는다.

**Independent Test**: 등록된 카메라에 fake diagnostic adapters and a local TCP listener를 사용해 success, failure, and timeout 결과를 검증한다.

### Tests for User Story 2

- [ ] T029 [P] [US2] Add Ping and TCP diagnostic contract tests for success, failure, timeout, and unknown camera responses in `tests/contract/diagnostics.test.ts`
- [ ] T030 [P] [US2] Add TCP adapter tests for reachable, refused, invalid, and 3-second timeout connections in `tests/unit/tcp-checker.test.ts`
- [ ] T031 [P] [US2] Add Ping adapter tests with a fake process runner for success, failure, cancellation, and timeout in `tests/unit/ping-checker.test.ts`
- [ ] T032 [P] [US2] Add diagnostic integration tests using a local TCP listener in `tests/integration/network-diagnostics.test.ts`

### Implementation for User Story 2

- [ ] T033 [P] [US2] Implement the TCP diagnostic adapter with port validation, socket cleanup, and a 3-second timeout in `src/diagnostics/tcp-checker.ts`
- [ ] T034 [P] [US2] Implement the platform-aware Ping adapter with process cancellation and a 3-second timeout in `src/diagnostics/ping-checker.ts`
- [ ] T035 [US2] Implement diagnostic use cases and normalized success, failure, and timeout results in `src/domain/camera-service.ts`
- [ ] T036 [US2] Add Ping and TCP diagnostic route handlers using the request-supplied port in `src/api/camera-routes.ts`
- [ ] T037 [US2] Register diagnostic dependencies and verify diagnostic response schemas in `src/app.ts`
- [ ] T038 [US2] Update diagnostic request and response examples in `contracts/openapi.yaml`

**Checkpoint**: All three result states are deterministic in tests and available through the documented REST API.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the complete feature and keep documentation and quality gates aligned.

- [ ] T039 [P] Update endpoint behavior, persistence assumptions, and test commands in `quickstart.md`
- [ ] T040 [P] Add a safe local configuration example and database runtime guidance in `.env.example` and `README.md`
- [ ] T041 Run lint, formatting check, typecheck, and the full automated test suite using scripts in `package.json`
- [ ] T042 Run every scenario in `quickstart.md` against an isolated database and record any contract mismatch in `quickstart.md`
- [ ] T043 [P] Validate `contracts/openapi.yaml` against the implemented route schemas in `tests/contract/openapi-conformance.test.ts`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001-T004 can start immediately; T001 must precede dependency installation and test execution.
- **Foundational (Phase 2)**: T005-T013 depend on setup and block all user stories.
- **User Story 1 (Phase 3)**: T014-T021 depend on the foundational phase; this is the MVP slice.
- **User Story 3 (Phase 4)**: T022-T028 depend on the foundational phase and the shared CRUD boundaries from US1.
- **User Story 2 (Phase 5)**: T029-T038 depend on the foundational phase and an existing Camera lookup from US1.
- **Polish (Phase 6)**: T039-T043 depend on all desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: No dependency on another user story after Phase 2; delivers the recommended MVP.
- **US3 (P1)**: Uses US1 repository and routes, but its error tests can be authored in parallel with US1 implementation.
- **US2 (P2)**: Requires Camera lookup from US1; diagnostic adapter tests and implementations can be developed in parallel after Phase 2, then integrated through US1 routes.

### Parallel Opportunities

- Setup: T002-T004 can run in parallel after T001 establishes the project manifest.
- Foundation: T007-T009 and T012-T013 can run in parallel while T006 establishes storage.
- US1: T014-T016 are parallel test authoring tasks; T017 can proceed independently of contract test files.
- US3: T022-T024 are parallel test authoring tasks; T025-T26 can be coordinated by file ownership.
- US2: T029-T032 and T033-T034 are parallel by test/adapter file; T035-T037 are integration tasks afterward.
- Polish: T039-T040 and T043 can run in parallel before T041-T042.

## Parallel Example: User Story 1

```text
Task T014: CRUD contract tests in tests/contract/cameras-crud.test.ts
Task T015: Lifecycle contract tests in tests/contract/cameras-lifecycle.test.ts
Task T016: Persistence integration tests in tests/integration/camera-persistence.test.ts
Task T017: Camera repository in src/storage/camera-repository.ts
```

## Parallel Example: User Story 2

```text
Task T029: Diagnostic contract tests in tests/contract/diagnostics.test.ts
Task T030: TCP adapter tests in tests/unit/tcp-checker.test.ts
Task T031: Ping adapter tests in tests/unit/ping-checker.test.ts
Task T033: TCP adapter in src/diagnostics/tcp-checker.ts
Task T034: Ping adapter in src/diagnostics/ping-checker.ts
```

## Implementation Strategy

### MVP First (US1)

1. Complete Phase 1 and Phase 2.
2. Write and run the US1 contract and persistence tests.
3. Implement Camera repository, service, and CRUD routes.
4. Validate registration, list/detail retrieval, update, delete, and restart persistence.
5. Stop for an MVP review before adding diagnostics.

### Incremental Delivery

1. Add US3 validation and error guarantees without changing successful CRUD behavior.
2. Add US2 with deterministic adapters and 3-second timeout handling.
3. Run the complete quickstart and conformance suite.

## Notes

- Every task uses the required checkbox, sequential ID, optional `[P]`, story label where applicable, and exact file path format.
- Tests are included because FR-015 and the constitution require automated coverage of core behavior and boundary cases.
- No task adds authentication, video streaming, alerts, bulk import, search, sorting, or other out-of-scope features.
