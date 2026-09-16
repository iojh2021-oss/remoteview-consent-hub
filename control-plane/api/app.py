from datetime import datetime, timezone
from typing import Dict
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI(title="RemoteView Control Plane", version="0.1.0")

DEVICES: Dict[str, dict] = {}
SESSIONS: Dict[str, dict] = {}
AUDIT_LOG = []

class Device(BaseModel):
    name: str
    owner: str

class SessionRequest(BaseModel):
    device_id: str
    operator: str


def audit(action: str, actor: str, target: str):
    AUDIT_LOG.append({
        "id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "actor": actor,
        "target": target,
    })

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/devices")
def register_device(device: Device, x_operator: str = Header(default="local-admin")):
    device_id = str(uuid4())
    DEVICES[device_id] = {
        "id": device_id,
        "name": device.name,
        "owner": device.owner,
        "online": False,
        "consent_required": True,
    }
    audit("device_registered", x_operator, device_id)
    return DEVICES[device_id]

@app.get("/devices")
def list_devices():
    return list(DEVICES.values())

@app.post("/sessions")
def create_session(req: SessionRequest):
    device = DEVICES.get(req.device_id)
    if not device:
        raise HTTPException(404, "device not found")
    if not device["consent_required"]:
        raise HTTPException(403, "explicit device consent is required")
    session_id = str(uuid4())
    SESSIONS[session_id] = {
        "id": session_id,
        "device_id": req.device_id,
        "operator": req.operator,
        "status": "awaiting_device_consent",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    audit("session_requested", req.operator, req.device_id)
    return SESSIONS[session_id]

@app.get("/sessions")
def list_sessions():
    return list(SESSIONS.values())

@app.get("/audit")
def audit_log():
    return AUDIT_LOG
