package com.remoteview.agent

import android.content.Context
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class AuditLogger(context: Context) {
    private val file = java.io.File(context.filesDir, "agent-audit.log")
    private val format = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSXXX", Locale.US)

    @Synchronized
    fun record(action: String, detail: String) {
        file.appendText("${format.format(Date())}\t$action\t$detail\n")
    }
}
