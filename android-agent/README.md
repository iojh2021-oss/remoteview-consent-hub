# Android Lab Agent

A professional Android device agent for devices owned by the operator or explicitly authorized for testing.

This component is intentionally **not** a covert RAT. It requires an explicit enrollment and active session authorization before accepting tasks.

## Responsibilities

- Device enrollment with a unique device identity
- Mutual application authentication using short-lived enrollment/session credentials
- Heartbeat and connection state
- Capability discovery
- Allow-listed information collection
- Explicit task queue with typed operations
- Structured task results
- Session expiration and revocation
- Local audit events

## Initial task contract

The agent exposes typed operations rather than an arbitrary shell:

- `device.info` — Android version, model, manufacturer, app version, and agent capabilities
- `device.status` — battery/charging and connectivity state
- `network.info` — connection type and non-secret connection metadata
- `session.status` — current authorization/session state
- `agent.ping` — health check

Every task carries a task ID, session ID, timestamp, and expiration. Unknown operations are rejected.

## Session model

1. The device is enrolled by an authorized operator.
2. The control plane issues a short-lived session authorization.
3. The agent verifies the session before processing tasks.
4. Each task is written to the local audit stream.
5. Results are returned with the same task ID.
6. Revocation or expiry immediately stops task processing.

## Android implementation

The production implementation should use Kotlin, Android's normal application/service lifecycle, HTTPS with certificate validation, Android Keystore-backed credentials, and WorkManager for resilient non-interactive housekeeping. Do not request accessibility, notification-listener, device-admin, VPN, root, or overlay privileges unless a separately documented product requirement genuinely needs them.

## Boundary

The agent must not provide arbitrary shell execution, hidden persistence, credential extraction, stealth, security-control bypass, or covert command-and-control behavior.
