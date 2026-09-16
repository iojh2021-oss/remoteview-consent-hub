# RemoteView Control Plane

Consent-based control plane for the authorized Android lab agent.

The control plane is the management layer; the Android component is an explicit, typed agent. The architecture keeps the Mythic-style separation between operator/control infrastructure and an agent, without introducing covert C2, arbitrary shell execution, persistence, or Android permission bypass.

## Architecture

```text
Operator / Lab Admin
        |
        v
   Control API
        |
   +----+----------------+
   |                     |
PostgreSQL          Task Queue
   |                     |
   +---------+-----------+
             |
             v
     Authorized Android Agent
             |
      typed allow-listed tasks
```

## Agent lifecycle

1. Device is explicitly enrolled with a short-lived/one-time enrollment code.
2. The control plane issues a device credential.
3. A session is explicitly started for the enrolled device.
4. Only while the session is active may the agent poll and execute typed tasks.
5. Tasks are allow-listed and audited.
6. Session expiry/revocation stops task processing.

## Initial operations

- `agent.ping`
- `device.info`
- `device.status`
- `network.info`
- `session.status`

The task protocol never interprets parameters as shell commands or executable code.

## Mythic relationship

Mythic remains the optional security-research/operator layer. This repository does not install a covert Android payload or a C2 profile. The Android agent is a purpose-built, consent-based lab component that follows the same conceptual separation of operator, tasking, agent, and results while respecting Android's application and permission model.

## Server

The API is FastAPI and PostgreSQL-backed and is packaged with Docker Compose. The compose file binds the API to localhost by default; place an authenticated TLS reverse proxy in front of it if remote access is required.

Create a local `.env` from `.env.example`, generate unique secrets, then start with:

```bash
cd control-plane
cp .env.example .env
chmod 600 .env
docker compose up -d --build
```

Do not commit `.env`.

## Security boundary

- No arbitrary shell.
- No hidden persistence.
- No credential extraction.
- No accessibility/device-admin/root/VPN/overlay bypass.
- No covert command channel.
- Only devices owned by the operator or explicitly authorized for testing.
