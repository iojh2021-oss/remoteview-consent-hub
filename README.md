# RemoteView Consent Hub

A consent-based remote screen viewing/control project for devices the operator owns or is explicitly authorized to administer.

## Goals

- Android screen capture through the platform MediaProjection consent flow
- WebRTC-based media transport
- Signaling service for authorized sessions
- Web viewer for an authenticated session
- Explicit user consent for screen capture and accessibility/control permissions
- TLS, short-lived session tokens, and basic audit logging for deployment

## Safety

This project is intended for legitimate remote support and device administration. It does not implement covert persistence, hidden control, credential theft, malware propagation, or unauthorized access.

## Planned structure

- `android/` — Android client
- `signaling/` — WebSocket signaling service
- `web/` — browser viewer
- `deploy/` — deployment configuration
- `docs/` — architecture and setup documentation
