# RustDesk Server Deployment

This folder contains a self-hosted RustDesk Server setup for authorized remote support.

## Server requirements

- Linux VPS (Ubuntu/Debian recommended)
- Docker and Docker Compose installed
- Public IP address or DNS name
- Firewall access for RustDesk ports

## Start

```bash
cd deploy/rustdesk
docker compose up -d
```

## Firewall

Open the RustDesk server ports required by your deployment:

- TCP 21115-21119
- UDP 21116

## Client configuration

After the server starts, configure RustDesk clients with:

- ID Server: your server hostname/IP
- Relay Server: your server hostname/IP
- Key: the generated public key from the server data directory

## Production recommendations

- Use a domain name and TLS where applicable
- Keep server keys private
- Use authentication and device authorization
- Do not expose unnecessary ports
