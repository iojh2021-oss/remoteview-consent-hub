# Android Agent Task Contract

## Envelope

```json
{
  "task_id": "uuid",
  "session_id": "uuid",
  "operation": "device.info",
  "created_at": "2026-01-01T00:00:00Z",
  "expires_at": "2026-01-01T00:01:00Z",
  "parameters": {}
}
```

## Result

```json
{
  "task_id": "uuid",
  "status": "completed",
  "completed_at": "2026-01-01T00:00:01Z",
  "data": {}
}
```

## Required validation

- Verify the authenticated device identity.
- Verify the session is active and authorized.
- Reject expired tasks.
- Validate the operation against the compiled allow-list.
- Validate operation parameters against a strict schema.
- Record accepted, rejected, and completed tasks in the audit trail.
- Never interpret operation parameters as shell commands or executable code.

## Extending the operation set

New operations should be typed, documented, permission-scoped, and independently auditable. Operations that access sensitive Android data require an explicit product requirement, Android permission, visible user authorization where applicable, and a documented retention policy.
