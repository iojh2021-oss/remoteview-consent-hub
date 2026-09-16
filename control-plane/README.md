# RemoteView Control Plane

This is a consent-based management layer for the RustDesk deployment.

It is intended for devices owned by the operator or devices where the operator has explicit authorization.

## Features

- Device registration and inventory
- User authentication
- Session approval workflow
- Online/offline device status
- Audit logs
- Role-based access control
- Session history
- Integration point for RustDesk ID/Relay infrastructure

## Architecture

```
Web Admin
   |
   v
Control API
   |
   +-- Database (devices, users, sessions, logs)
   |
   +-- RustDesk Server
   |
   +-- Notification service
```

## Security requirements

- TLS everywhere
- Strong authentication
- Short-lived session tokens
- Device authorization
- No hidden access or bypass of Android permissions

## Planned stack

- API: FastAPI or Node.js
- Database: PostgreSQL
- Web UI: React
- Deployment: Docker Compose
