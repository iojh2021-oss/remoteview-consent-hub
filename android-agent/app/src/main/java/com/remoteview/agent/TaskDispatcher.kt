package com.remoteview.agent

class TaskDispatcher {
    private val allowed = setOf(
        "agent.ping",
        "device.info",
        "device.status",
        "network.info",
        "session.status"
    )

    fun dispatch(operation: String): Result<String> {
        if (operation !in allowed) return Result.failure(IllegalArgumentException("Operation not allowed"))
        return Result.success(operation)
    }
}
