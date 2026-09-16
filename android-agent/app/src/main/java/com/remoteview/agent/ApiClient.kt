package com.remoteview.agent

import java.net.HttpURLConnection
import java.net.URI
import org.json.JSONObject

class ApiClient(private val baseUrl: String) {
    fun startSession(deviceToken: String): JSONObject = request("POST", "/v1/session/start", deviceToken)

    fun stopSession(deviceToken: String): JSONObject = request("POST", "/v1/session/stop", deviceToken)

    fun poll(deviceToken: String): JSONObject = request("GET", "/v1/tasks/poll", deviceToken)

    fun submitResult(deviceToken: String, taskId: String, result: JSONObject): JSONObject = request("POST", "/v1/tasks/$taskId/result", deviceToken, result)

    private fun request(method: String, path: String, token: String, body: JSONObject? = null): JSONObject {
        val connection = URI.create(baseUrl.trimEnd('/') + path).toURL().openConnection() as HttpURLConnection
        connection.requestMethod = method
        connection.setRequestProperty("Authorization", "Bearer $token")
        if (body != null) {
            connection.setRequestProperty("Content-Type", "application/json")
            connection.doOutput = true
            connection.outputStream.use { it.write(body.toString().toByteArray()) }
        }
        if (connection.responseCode !in 200..299) error("API request failed: ${connection.responseCode}")
        return JSONObject(connection.inputStream.bufferedReader().use { it.readText() })
    }
}
