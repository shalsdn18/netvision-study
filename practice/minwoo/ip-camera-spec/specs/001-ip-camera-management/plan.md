# Implementation Plan: IP Camera Management

**Branch**: `001-ip-camera-management` | **Date**: 2026-08-31 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-ip-camera-management/spec.md`

## Summary

관리자가 카메라를 영구적으로 등록, 조회, 수정, 삭제하고, 등록된 IPv4 주소에 Ping 및
사용자 지정 TCP 포트 진단을 수행하는 단일 REST API를 제공한다. Node.js 22 LTS와
TypeScript, Fastify, SQLite를 사용하며, HTTP 계약은 OpenAPI 문서와 결정적 주입 테스트로
검증한다. 실제 네트워크 동작은 진단 어댑터로 분리해 자동화 테스트에서 대체한다.

## Technical Context

**Language/Version**: TypeScript on Node.js 22 LTS

**Primary Dependencies**: Fastify, SQLite driver, JSON Schema validation, OpenAPI tooling

**Storage**: SQLite database file with explicit transactions and WAL mode

**Testing**: Fastify in-process contract tests, unit tests for validation and adapters, local TCP test server

**Target Platform**: Linux or Windows server with access to the managed camera network

**Project Type**: Single-process web service

**Performance Goals**: 95% of valid management requests complete within 1 second under normal network conditions; diagnostics end within 3 seconds

**Constraints**: IPv4 only; TCP ports 1-65535; diagnostic results are success, failure, or timeout; no authentication, streaming, alerts, or bulk operations in MVP

**Scale/Scope**: Small MVP for one service and a manageable camera inventory; no horizontal scaling target is specified

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Minimal Implementation**: PASS. The plan contains only specified CRUD and network diagnostic
  behavior; authentication, streaming, alerts, and bulk features remain out of scope.
- **RESTful API Conventions**: PASS. Resource paths, HTTP methods, status codes, JSON
  representations, and endpoint contracts are defined in `contracts/openapi.yaml`.
- **Testable Requirements**: PASS. Each functional requirement maps to an acceptance scenario,
  contract test, unit test, or deterministic diagnostic test.
- **External Input Validation**: PASS. Request schemas validate identifiers, names, IPv4 values,
  required fields, unknown fields, and TCP port range before persistence or diagnostics.
- **Consistent HTTP Errors**: PASS. Invalid input, duplicate IDs, and missing cameras use the
  common `ApiError` JSON shape and documented status mappings.
- **Maintainable Simplicity**: PASS. The design uses a single service, direct SQLite access, and
  two small diagnostic adapters; no ORM, queue, cache, or microservice split is introduced.
- **Core Behavior Test Coverage**: PASS. CRUD, validation, errors, empty lists, persistence,
  and deterministic diagnostic outcomes are listed in `quickstart.md`.
- **Explicit Scope Control**: PASS. All planned endpoints trace to FR-001 through FR-018;
  unrequested capabilities are explicitly excluded.

## Project Structure

### Documentation (this feature)

```text
specs/001-ip-camera-management/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── openapi.yaml
└── tasks.md                 # Created by /speckit-tasks, not this command
```

### Source Code (repository root)

```text
src/
├── app.ts                 # Fastify application composition
├── server.ts              # Process entry point
├── config.ts              # Environment and database configuration
├── api/
│   ├── camera-routes.ts   # CRUD and diagnostic route definitions
│   ├── schemas.ts         # Request and response schemas
│   └── errors.ts          # Common ApiError mapping
├── domain/
│   ├── camera.ts          # Camera and diagnostic types
│   └── camera-service.ts  # Use cases and validation boundary
├── storage/
│   ├── database.ts        # SQLite connection and schema setup
│   └── camera-repository.ts
└── diagnostics/
    ├── ping-checker.ts    # OS Ping adapter with cancellation
    └── tcp-checker.ts     # TCP socket adapter with timeout

tests/
├── contract/              # HTTP routes, status codes, JSON contracts
├── unit/                  # Validation, service, repository, adapter behavior
└── integration/           # SQLite restart persistence and local TCP checks
```

**Structure Decision**: Use a single TypeScript web-service project. Keep HTTP concerns,
domain use cases, SQLite persistence, and network diagnostics in separate small modules so
each boundary is independently testable without introducing a multi-project architecture.

## Complexity Tracking

No violations. Complexity tracking is not required.

## Phase 0: Research

Research decisions are recorded in [research.md](research.md). They resolve the technology,
persistence, diagnostic adapter, timeout, and deterministic testing choices without adding
unrequested features.

## Phase 1: Design and Contracts

- [data-model.md](data-model.md) defines Camera, Network Diagnostic Result, and API Error.
- [contracts/openapi.yaml](contracts/openapi.yaml) defines the REST endpoints, schemas, and
  success/error status mappings.
- [quickstart.md](quickstart.md) defines automated and manual validation scenarios.

## Post-Design Constitution Check

- All eight principles remain PASS after design.
- The design adds no unrequested product capability and keeps diagnostics behind testable
  boundaries.
- Persistent storage, input validation, error consistency, and core behavior tests are
  explicitly represented in the model, contract, and quickstart.
