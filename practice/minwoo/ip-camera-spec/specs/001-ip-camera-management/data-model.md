# Data Model: IP Camera Management

## Camera

Represents a managed IP camera.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `cameraId` | string | yes | Client-provided unique identifier; non-empty and format-validated |
| `cameraName` | string | yes | Non-empty and within the selected maximum length |
| `ipAddress` | string | yes | IPv4 only; four numeric octets, each from 0 through 255 |

A Camera is persisted across service restarts. `cameraId` is immutable after creation and is
used to identify the resource. TCP port is deliberately not a Camera field; it is supplied
per diagnostic request.

## Network Diagnostic Result

Represents one Ping or TCP Port check for an existing Camera.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `cameraId` | string | yes | Must identify an existing Camera |
| `diagnosticType` | enum | yes | `ping` or `tcp-port` |
| `status` | enum | yes | `success`, `failure`, or `timeout` |
| `port` | integer | TCP only | Integer from 1 through 65535 |
| `latencyMs` | integer | no | Non-negative when measured |
| `message` | string | no | Safe diagnostic detail without secrets or internal paths |

A diagnostic result is an API response, not a persisted entity. Each check uses a three-second
operation timeout.

## API Error

The common error representation for rejected requests and unavailable resources.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `code` | string | yes | Stable machine-readable error code |
| `message` | string | yes | Human-readable and safe |
| `fieldErrors` | object | no | Field-specific validation messages |

Expected error categories include invalid input, duplicate camera ID, camera not found, and
internal diagnostic failure. Exact HTTP status mapping is defined in [contracts/openapi.yaml](contracts/openapi.yaml).

## State and Integrity Rules

- Camera creation is atomic: a failed validation or duplicate ID cannot create a partial row.
- Camera update is atomic: invalid input leaves the previous row unchanged.
- Camera deletion affects only the selected `cameraId`.
- A diagnostic is performed only after the Camera exists and request inputs pass validation.
- Concurrent writes must not leave a partial Camera record; MVP conflict behavior is
  last-commit-wins.
