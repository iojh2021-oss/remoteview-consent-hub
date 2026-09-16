package com.remoteview.agent

import android.content.Context
import java.net.HttpURLConnection
import java.net.URI
import org.json.JSONObject

class EnrollmentClient(private val context: Context) {
    fun enroll(baseUrl: String, deviceName: String, owner: String, enrollmentCode: String, deviceId: String, capabilities: JSONObject): JSONObject {
        val connection = URI.create(baseUrl.trimEnd('/') + "/v1/enroll").toURL().openConnection() as HttpURLConnection
        connection.requestMethod = "POST"
        connection.setRequestProperty("Content-Type", "application/json")
        connection.doOutput = true
        val body = JSONObject()
            .put("device_id", deviceId)
            .put("device_name", deviceName)
            .put("owner", owner)
            .put("enrollment_code", enrollmentCode)
            .put("capabilities", capabilities)
            .toString()
        connection.outputStream.use { it.write(body.toByteArray()) }
        if (connection.responseCode !in 200..299) error("Enrollment failed: ${connection.responseCode}")
        return JSONObject(connection.inputStream.bufferedReader().use { it.readText() })
    }
}
