# Architecture

```text
Android device A
  | MediaProjection + WebRTC
  | explicit user approval
  v
Signaling service <---- authenticated session ----> Web viewer/device B
```

## Session flow

1. The operator creates or joins an authenticated session.
2. Android requests the system MediaProjection permission dialog.
3. Only after approval does the client capture the display.
4. WebRTC transports the media between authorized participants.
5. Signaling exchanges SDP/ICE information; it should not carry screen pixels.
6. Sessions use short-lived identifiers/tokens and expire automatically.

## Control permissions

If remote input/control is added, Android Accessibility permission must be explicitly enabled by the device owner. The application should clearly show when remote control is active and provide a local stop/disconnect action.

## Deployment requirements

- HTTPS/WSS with a valid TLS certificate
- Authentication and short-lived session tokens
- No secrets embedded in the APK or browser bundle
- Restrictive CORS/origin policy
- Rate limiting and basic audit logs
- Firewall rules exposing only required ports
