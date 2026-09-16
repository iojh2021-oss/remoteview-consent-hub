package com.remoteview.agent

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import androidx.activity.ComponentActivity

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val status = TextView(this).apply {
            text = "RemoteView Lab Agent\n\nNot running.\nEnrollment and an active authorized session are required."
            textSize = 18f
            setPadding(32, 48, 32, 32)
        }
        val start = Button(this).apply {
            text = "Start authorized session"
            setOnClickListener {
                // The session token must be supplied by the authenticated enrollment/session flow.
                status.text = "No session token configured. Enroll the device and start a session through the control plane."
            }
        }
        val stop = Button(this).apply {
            text = "Stop agent"
            setOnClickListener { stopService(Intent(this@MainActivity, AgentService::class.java)); status.text = "Stopped." }
        }
        setContentView(LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            addView(status)
            addView(start)
            addView(stop)
        })
    }
}
