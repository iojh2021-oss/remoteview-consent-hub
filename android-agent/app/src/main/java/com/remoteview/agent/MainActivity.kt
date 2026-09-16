package com.remoteview.agent

import android.os.Bundle
import android.widget.TextView
import androidx.activity.ComponentActivity

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(TextView(this).apply {
            text = "RemoteView Lab Agent\n\nEnrollment and active-session authorization are required.\nNo hidden access or arbitrary shell is provided."
            textSize = 18f
            setPadding(32, 48, 32, 48)
        })
    }
}
