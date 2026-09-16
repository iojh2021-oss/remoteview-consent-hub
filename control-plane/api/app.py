import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import psycopg
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="RemoteView Control Plane", version="0.2.0")
DB = os.environ["DATABASE_URL"]
ENROLLMENT_CODE = os.environ["ENROLLMENT_CODE"]
ADMIN_API_KEY = os.environ["ADMIN_API_KEY"]
SESSION_MINUTES = int(os.getenv("SESSION_MINUTES", "30"))
ALLOWED = {"agent.ping", "device.info", "device.status", "network.info", "session.status"}


def db():
    return psycopg.connect(DB)


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def audit(conn, action: str, actor: str, device_id: str | None, details: dict[str, Any] | None = None):
    conn.execute(
        "INSERT INTO audit_events(action, actor, device_id, details) VALUES (%s,%s,%s,%s)",
        (action, actor, device_id, psycopg.types.json.Json(details or {})),
    )


@app.on_event("startup")
def init_db():
    with db() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS devices(
          id UUID PRIMARY KEY, device_name TEXT NOT NULL, owner TEXT NOT NULL,
          token_hash TEXT NOT NULL UNIQUE, enrolled_at TIMESTAMPTZ NOT NULL DEFAULT now(),
          last_seen TIMESTAMPTZ, capabilities JSONB NOT NULL DEFAULT '{}'::jsonb
        );
        CREATE TABLE IF NOT EXISTS sessions(
          id UUID PRIMARY KEY, device_id UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
          status TEXT NOT NULL, token_hash TEXT NOT NULL UNIQUE,
          created_at TIMESTAMPTZ NOT NULL DEFAULT now(), expires_at TIMESTAMPTZ NOT NULL
        );
        CREATE TABLE IF NOT EXISTS tasks(
          id UUID PRIMARY KEY, device_id UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
          session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
          operation TEXT NOT NULL, parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
          status TEXT NOT NULL DEFAULT 'queued', result JSONB,
          created_at TIMESTAMPTZ NOT NULL DEFAULT now(), claimed_at TIMESTAMPTZ
        );
        CREATE TABLE IF NOT EXISTS audit_events(
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(), created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
          action TEXT NOT NULL, actor TEXT NOT NULL, device_id UUID, details JSONB NOT NULL DEFAULT '{}'::jsonb
        );
        """)
        conn.commit()


class Enrollment(BaseModel):
    device_id: str
    device_name: str = Field(min_length=1, max_length=120)
    owner: str = Field(min_length=1, max_length=120)
    enrollment_code: str
    capabilities: dict[str, Any] = {}


class TaskRequest(BaseModel):
    device_id: str
    operation: str
    parameters: dict[str, Any] = {}


class TaskResult(BaseModel):
    status: str
    data: dict[str, Any] = {}
    error: str | None = None


def require_admin(value: str | None):
    if not value or not secrets.compare_digest(value, ADMIN_API_KEY):
        raise HTTPException(401, "admin authentication required")


def auth_device(authorization: str | None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "device authentication required")
    token_hash = digest(authorization[7:])
    with db() as conn:
        row = conn.execute("SELECT id FROM devices WHERE token_hash=%s", (token_hash,)).fetchone()
    if not row:
        raise HTTPException(401, "invalid device credential")
    return str(row[0])


def auth_session(device_id: str, authorization: str | None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "session authentication required")
    with db() as conn:
        row = conn.execute(
            "SELECT id, expires_at FROM sessions WHERE device_id=%s AND token_hash=%s AND status='active'",
            (device_id, digest(authorization[7:])),
        ).fetchone()
    if not row or row[1] <= datetime.now(timezone.utc):
        raise HTTPException(401, "session expired or revoked")
    return str(row[0])


@app.get("/health")
def health():
    return {"status": "ok", "service": "remoteview-control-plane", "version": "0.2.0"}


@app.post("/v1/enroll")
def enroll(req: Enrollment):
    if not secrets.compare_digest(req.enrollment_code, ENROLLMENT_CODE):
        raise HTTPException(403, "invalid enrollment code")
    token = secrets.token_urlsafe(32)
    with db() as conn:
        conn.execute(
            "INSERT INTO devices(id,device_name,owner,token_hash,capabilities) VALUES (%s,%s,%s,%s,%s) "
            "ON CONFLICT(id) DO UPDATE SET device_name=EXCLUDED.device_name, owner=EXCLUDED.owner, capabilities=EXCLUDED.capabilities",
            (req.device_id, req.device_name, req.owner, digest(token), psycopg.types.json.Json(req.capabilities)),
        )
        audit(conn, "device_enrolled", req.owner, req.device_id, {"capabilities": req.capabilities})
        conn.commit()
    return {"device_id": req.device_id, "device_token": token}


@app.post("/v1/session/start")
def start_session(authorization: str | None = Header(default=None)):
    device_id = auth_device(authorization)
    session_token = secrets.token_urlsafe(32)
    session_id = secrets.token_hex(16)
    expires = datetime.now(timezone.utc) + timedelta(minutes=SESSION_MINUTES)
    with db() as conn:
        conn.execute("UPDATE sessions SET status='revoked' WHERE device_id=%s AND status='active'", (device_id,))
        conn.execute(
            "INSERT INTO sessions(id,device_id,status,token_hash,expires_at) VALUES (%s,%s,'active',%s,%s)",
            (session_id, device_id, digest(session_token), expires),
        )
        conn.execute("UPDATE devices SET last_seen=now() WHERE id=%s", (device_id,))
        audit(conn, "session_started", device_id, device_id, {"expires_at": expires.isoformat()})
        conn.commit()
    return {"session_id": session_id, "session_token": session_token, "expires_at": expires}


@app.post("/v1/session/stop")
def stop_session(authorization: str | None = Header(default=None)):
    device_id = auth_device(authorization)
    with db() as conn:
        conn.execute("UPDATE sessions SET status='revoked' WHERE device_id=%s AND status='active'", (device_id,))
        audit(conn, "session_stopped", device_id, device_id)
        conn.commit()
    return {"status": "revoked"}


@app.get("/v1/session/status")
def session_status(authorization: str | None = Header(default=None)):
    device_id = auth_device(authorization)
    with db() as conn:
        row = conn.execute("SELECT id, status, expires_at FROM sessions WHERE device_id=%s ORDER BY created_at DESC LIMIT 1", (device_id,)).fetchone()
    return {"device_id": device_id, "session_id": str(row[0]) if row else None, "status": row[1] if row else "none", "expires_at": row[2] if row else None}


@app.post("/v1/admin/tasks")
def create_task(req: TaskRequest, x_admin_key: str | None = Header(default=None)):
    require_admin(x_admin_key)
    if req.operation not in ALLOWED:
        raise HTTPException(400, "operation is not allow-listed")
    with db() as conn:
        row = conn.execute("SELECT id FROM sessions WHERE device_id=%s AND status='active' AND expires_at>now() ORDER BY created_at DESC LIMIT 1", (req.device_id,)).fetchone()
        if not row:
            raise HTTPException(409, "device has no active authorized session")
        task_id = str(secrets.token_hex(16))
        conn.execute("INSERT INTO tasks(id,device_id,session_id,operation,parameters) VALUES (%s,%s,%s,%s,%s)", (task_id, req.device_id, str(row[0]), req.operation, psycopg.types.json.Json(req.parameters)))
        audit(conn, "task_queued", "admin", req.device_id, {"operation": req.operation, "task_id": task_id})
        conn.commit()
    return {"task_id": task_id, "operation": req.operation, "status": "queued"}


@app.get("/v1/tasks/poll")
def poll(authorization: str | None = Header(default=None)):
    device_id = auth_device(authorization)
    session_id = auth_session(device_id, authorization)
    with db() as conn:
        row = conn.execute("SELECT id,operation,parameters FROM tasks WHERE device_id=%s AND session_id=%s AND status='queued' ORDER BY created_at FOR UPDATE SKIP LOCKED LIMIT 1", (device_id, session_id)).fetchone()
        if not row:
            return {"task": None}
        conn.execute("UPDATE tasks SET status='claimed', claimed_at=now() WHERE id=%s", (str(row[0]),))
        conn.commit()
    return {"task": {"task_id": str(row[0]), "session_id": session_id, "operation": row[1], "parameters": row[2]}}


@app.post("/v1/tasks/{task_id}/result")
def result(task_id: str, req: TaskResult, authorization: str | None = Header(default=None)):
    device_id = auth_device(authorization)
    session_id = auth_session(device_id, authorization)
    if req.status not in {"completed", "rejected", "failed"}:
        raise HTTPException(400, "invalid result status")
    with db() as conn:
        updated = conn.execute("UPDATE tasks SET status=%s,result=%s WHERE id=%s AND device_id=%s AND session_id=%s AND status='claimed' RETURNING id", (req.status, psycopg.types.json.Json(req.model_dump()), task_id, device_id, session_id)).fetchone()
        if not updated:
            raise HTTPException(404, "task not found or not claimed by this session")
        audit(conn, "task_result", device_id, device_id, {"task_id": task_id, "status": req.status})
        conn.execute("UPDATE devices SET last_seen=now() WHERE id=%s", (device_id,))
        conn.commit()
    return {"task_id": task_id, "status": req.status}


@app.get("/v1/admin/devices")
def admin_devices(x_admin_key: str | None = Header(default=None)):
    require_admin(x_admin_key)
    with db() as conn:
        rows = conn.execute("SELECT id,device_name,owner,enrolled_at,last_seen,capabilities FROM devices ORDER BY enrolled_at DESC").fetchall()
    return [{"device_id": str(r[0]), "device_name": r[1], "owner": r[2], "enrolled_at": r[3], "last_seen": r[4], "capabilities": r[5]} for r in rows]


@app.get("/v1/admin/audit")
def admin_audit(x_admin_key: str | None = Header(default=None)):
    require_admin(x_admin_key)
    with db() as conn:
        rows = conn.execute("SELECT id,created_at,action,actor,device_id,details FROM audit_events ORDER BY created_at DESC LIMIT 500").fetchall()
    return [{"id": str(r[0]), "created_at": r[1], "action": r[2], "actor": r[3], "device_id": str(r[4]) if r[4] else None, "details": r[5]} for r in rows]
