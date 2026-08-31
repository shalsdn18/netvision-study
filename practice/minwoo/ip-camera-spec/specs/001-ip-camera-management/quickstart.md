# Quickstart: IP Camera Management

This guide validates the feature through the REST API contract. It assumes Node.js 22 LTS,
SQLite support, and the project dependencies have been installed.

## Prerequisites

- Start the service using the repository's standard development command.
- Set the test database path to an isolated temporary file.
- Ensure the service can access the local network for optional diagnostic smoke checks.

## Automated validation

Run the repository's standard test command. The suite must cover:

1. Create a camera with a valid ID, name, and IPv4 address.
2. List cameras and verify the created camera is present.
3. Retrieve the camera by ID, update its name or address, then delete it.
4. Reject malformed IPv4 addresses, missing fields, invalid ports, and duplicate IDs.
5. Return a not-found error for lookup, update, delete, Ping, and TCP checks on an unknown ID.
6. Return an empty list when no cameras exist.
7. Return deterministic success, failure, and timeout diagnostic results using test doubles.
8. Restart the service against the same database file and verify camera data remains.

## Manual request flow

Use the endpoint and payload definitions in [contracts/openapi.yaml](contracts/openapi.yaml):

1. Create a camera with `POST /cameras`.
2. Confirm it with `GET /cameras` and `GET /cameras/{cameraId}`.
3. Run `POST /cameras/{cameraId}/diagnostics/ping`.
4. Run `POST /cameras/{cameraId}/diagnostics/tcp` with a port in the request body.
5. Update with `PUT /cameras/{cameraId}` and remove with `DELETE /cameras/{cameraId}`.

Expected outcomes include `201` for creation, `200` for successful reads, updates, and
checks, `204` for deletion, `400` for invalid input, `404` for an unknown camera, and `409`
for a duplicate camera ID. Diagnostic reachability failures are successful diagnostic
responses with a classified result; they are not API validation errors.

## Optional network smoke check

Run against a controlled local or test network target only. Do not make the automated suite
depend on external cameras or Internet hosts. Confirm that a check which cannot finish within
3 seconds returns `timeout` and that the request does not remain pending.
