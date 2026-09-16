package com.remoteview.agent

import org.json.JSONObject

data class TaskEnvelope(
    val taskId: String,
    val sessionId: String,
    val operation: String,
    val parameters: JSONObject
)

data class TaskResult(
    val taskId: String,
    val status: String,
    val data: JSONObject = JSONObject(),
    val error: String? = null
)
