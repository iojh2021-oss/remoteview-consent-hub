# Dedicated Server Deployment

This guide prepares a dedicated Linux host for an authorized Mythic lab. The repository does not configure firewall rules or network segmentation, per project requirements.

## 1. Host prerequisites

Recommended baseline:

- Ubuntu/Debian Linux on a dedicated VM or server
- Docker Engine and Docker Compose plugin
- Git
- Persistent SSD storage
- Accurate system time (NTP)
- A DNS name if the web UI will be exposed through TLS

Keep the server dedicated to the lab and do not store production credentials on it.

## 2. Deploy Mythic core

From this repository:

```bash
cd mythic
chmod +x install-server.sh
./install-server.sh
```

The helper clones the upstream Mythic repository and builds the Mythic CLI. It does not install payload types or covert agents.

## 3. Secrets

Create the real environment configuration on the server. Do not commit it.

```bash
cp .env.example .env
chmod 600 .env
```

Replace every `CHANGE_ME` value with a long, unique secret. Keep backups of secrets encrypted and separate from Git.

## 4. Start and verify

Run the commands from the upstream Mythic directory created by the installer:

```bash
cd "$HOME/Mythic"
sudo ./mythic-cli start
sudo ./mythic-cli health
sudo ./mythic-cli status
```

Use the upstream Mythic documentation for version-specific service names and UI access because those details can change between releases.

## 5. Lab devices

Only phones explicitly registered in the project's control plane should be treated as lab devices. A device should have:

- a stable device identifier
- an owner/authorization record
- an active consent/session state
- an audit trail for actions
- a revocation path

Do not deploy an agent to a device merely because its address is reachable.

## 6. Operations

- Rotate secrets periodically and after any suspected exposure.
- Keep application and database backups encrypted.
- Retain audit logs long enough to investigate sessions.
- Test restore procedures before relying on backups.
- Keep Mythic and Docker images updated according to the upstream release process.

## Scope

The repository intentionally excludes hidden persistence, credential theft, arbitrary remote shell, unauthorized device access, and evasion features.
