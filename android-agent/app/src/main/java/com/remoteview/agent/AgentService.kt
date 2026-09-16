package com.remoteview.agent

import android.app.Service
import android.content.Intent
import android.os.IBinder
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import org.json.JSONObject

class AgentService : Service() {
    private val scope = CoroutineScope(Dispatchers.IO)
    private var job: Job? = null

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent?.action == ACTION_START && intent.getBooleanExtra(EXTRA_AUTHORIZED, false)) {
            val token = intent.getStringExtra(EXTRA_SESSION_TOKEN)
            if (!token.isNullOrBlank()) startLoop(token)
        } else if (intent?.action == ACTION_STOP) {
            stopSelf()
        }
        return START_NOT_STICKY
    }

    private fun startLoop(sessionToken: String) {
        job?.cancel()
        job = scope.launch {
            val api = ApiClient(BuildConfig.CONTROL_PLANE_URL)
            val dispatcher = TaskDispatcher(applicationContext)
            val audit = AuditLogger(applicationContext)
            while (isActive) {
                runCatching {
                    val response = api.poll(sessionToken)
                    val task = response.optJSONObject("task")
                    if (task != null) {
                        val taskId = task.getString("task_id")
                        val operation = task.getString("operation")
                        audit.record("task_received", "$taskId:$operation")
                        val result = dispatcher.dispatch(operation, task.optJSONObject("parameters") ?: JSONObject())
                        val payload = if (result.isSuccess) {
                            JSONObject().put("status", "completed").put("data", result.getOrThrow())
                        } else {
                            JSONObject().put("status", "rejected").put("error", result.exceptionOrNull()?.message ?: "rejected")
                        }
                        api.submitResult(sessionToken, taskId, payload)
                        audit.record("task_result", "$taskId:${payload.getString("status")}")
                    }
                }.onFailure { audit.record("transport_error", it.message ?: "unknown") }
                delay(5000)
            }
        }
    }

    override fun onDestroy() {
        job?.cancel()
        scope.cancel()
        super.onDestroy()
    }

    companion object {
        const val ACTION_START = "com.remoteview.agent.START"
        const val ACTION_STOP = "com.remoteview.agent.STOP"
        const val EXTRA_AUTHORIZED = "authorized"
        const val EXTRA_SESSION_TOKEN = "session_token"
    }
}
