# Research: IP Camera Management

## Decision: Node.js 22 LTS, TypeScript, Fastify, and SQLite

- **Rationale**: The project has no existing source or stack. This combination keeps a small
  REST service in one process, provides schema-based request validation, and supports
  in-process HTTP contract tests without opening a real port.
- **Alternatives considered**: Node's built-in HTTP module would reduce dependencies but
  require hand-built routing and validation. Express is viable but offers less integrated
  schema validation. PostgreSQL adds operational cost beyond this MVP. A JSON file is not
  sufficient because concurrent writes and partial writes need stronger atomicity.

## Decision: SQLite with explicit transactions

- **Rationale**: A single database file provides persistence across restarts with minimal
  operational setup. Explicit transactions preserve atomic create, update, and delete
  operations. The MVP accepts last-commit-wins behavior for concurrent edits because
  version conflict detection is not specified.
- **Alternatives considered**: A hosted relational database is more scalable but unnecessary
  for the stated scope. An ORM adds abstraction without enough model complexity to justify it.

## Decision: Separate network diagnostic adapters

- **Rationale**: TCP checks can use a direct socket connection, while Ping is an operating
  system capability with platform-specific invocation details. Separate adapters normalize
  both to `success`, `failure`, or `timeout` and allow deterministic test doubles.
- **Alternatives considered**: Direct network calls in route handlers would make tests
  environment-dependent. A single combined adapter would obscure the different failure and
  timeout semantics of Ping and TCP.

## Decision: Three-second diagnostic timeout

- **Rationale**: The clarified specification requires both Ping and TCP checks to return a
  timeout result after 3 seconds. Timeout handling must cancel or destroy the underlying
  process or socket so the request cannot continue in the background.
- **Alternatives considered**: One, five, and ten seconds were considered; one second can
  classify transient local delay too aggressively, while five or ten seconds makes operator
  feedback slower for an MVP.

## Decision: Contract tests with deterministic diagnostics

- **Rationale**: CRUD, validation, status codes, JSON errors, and empty lists can be tested
  through Fastify's in-process request injection. Network diagnostics use fake adapters for
  success and timeout cases plus a local TCP listener for connection behavior. Real OS Ping
  is reserved for an optional environment smoke check.
- **Alternatives considered**: Calling real cameras and external hosts in every test would
  create flaky results and violate deterministic test expectations.

## Decision: MVP scope remains a single REST service

- **Rationale**: Authentication, authorization, streaming, alerts, bulk import, search,
  sorting, audit logs, caching, queues, and microservices are not specified. Excluding them
  preserves the constitution's minimal implementation and explicit scope principles.
- **Alternatives considered**: Adding these capabilities now would increase deployment,
  security, and test surface without supporting an approved requirement.
