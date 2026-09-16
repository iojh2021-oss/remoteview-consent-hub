package com.remoteview.agent

import android.app.Service
import android.content.Intent
import android.os.IBinder

class AgentService : Service() {
    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Production transport/session handling will run only after explicit enrollment.
        return START_NOT_STICKY
    }
}
