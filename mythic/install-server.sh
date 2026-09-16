#!/usr/bin/env bash
set -euo pipefail

# Authorized-lab deployment helper for a dedicated Linux server.
# This installs Mythic core only. No payload type or C2 profile is installed here.

MYTHIC_DIR="${MYTHIC_DIR:-$HOME/Mythic}"
MYTHIC_REPO="https://github.com/its-a-feature/Mythic.git"

command -v git >/dev/null || { echo "git is required"; exit 1; }
command -v docker >/dev/null || { echo "Docker is required"; exit 1; }
docker compose version >/dev/null 2>&1 || { echo "Docker Compose plugin is required"; exit 1; }

if [[ ! -d "$MYTHIC_DIR/.git" ]]; then
  git clone --depth 1 "$MYTHIC_REPO" "$MYTHIC_DIR"
fi

cd "$MYTHIC_DIR"

# Build the current mythic-cli from the checked-out source.
make

# Generate/validate the local Mythic environment without starting services yet.
./mythic-cli status || true

cat <<'EOF'

Mythic core is prepared.

Next steps:
  1. Review Mythic/.env on this server and set unique secrets/passwords.
  2. Keep the real .env outside Git and protect it with filesystem permissions.
  3. Start with: sudo ./mythic-cli start
  4. Check health with: sudo ./mythic-cli health
  5. Do not install payloads or C2 profiles until the corresponding phone/device
     is explicitly registered as an authorized lab device.

This repository intentionally does not install an agent, payload, persistence,
credential collection, or covert command channel.
EOF
