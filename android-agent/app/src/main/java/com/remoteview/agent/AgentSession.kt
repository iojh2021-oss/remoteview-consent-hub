package com.remoteview.agent

import java.time.Instant

class AgentSession {
    var sessionId: String? = null
        private set
    private var expiresAt: Instant? = null

    fun activate(id: String, expires: Instant) {
        sessionId = id
        expiresAt = expires
    }

    fun revoke() {
        sessionId = null
        expiresAt = null
    }

    fun isActive(now: Instant = Instant.now()): Boolean = sessionId != null && expiresAt?.isAfter(now) == true
}
