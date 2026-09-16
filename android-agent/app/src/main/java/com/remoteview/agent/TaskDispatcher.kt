package com.remoteview.agent

import android.content.Context
import android.net.ConnectivityManager
import android.os.BatteryManager
import android.os.Build
import org.json.JSONObject

class TaskDispatcher(private val context: Context) {
    private val allowed = setOf("agent.ping", "device.info", "device.status", "network.info", "session.status")

    fun dispatch(operation: String, parameters: JSONObject = JSONObject()): Result<JSONObject> {
        if (operation !in allowed) return Result.failure(IllegalArgumentException("Operation not allowed"))
        return runCatching {
            when (operation) {
                "agent.ping" -> JSONObject().put("status", "ok")
                "device.info" -> JSONObject()
                    .put("manufacturer", Build.MANUFACTURER)
                    .put("model", Build.MODEL)
                    .put("android_release", Build.VERSION.RELEASE)
                    .put("sdk", Build.VERSION.SDK_INT)
                    .put("agent_package", context.packageName)
                    .put("agent_version", context.packageManager.getPackageInfo(context.packageName, 0).versionName)
                "device.status" -> {
                    val battery = context.getSystemService(BatteryManager::class.java)
                    val cm = context.getSystemService(ConnectivityManager::class.java)
                    JSONObject()
                        .put("battery_percent", battery.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY))
                        .put("charging", battery.isCharging)
                        .put("network_available", cm.activeNetwork != null)
                }
                "network.info" -> {
                    val cm = context.getSystemService(ConnectivityManager::class.java)
                    val network = cm.activeNetwork
                    val caps = network?.let { cm.getNetworkCapabilities(it) }
                    JSONObject()
                        .put("connected", network != null)
                        .put("validated", caps?.hasCapability(android.net.NetworkCapabilities.NET_CAPABILITY_VALIDATED) == true)
                        .put("transport_wifi", caps?.hasTransport(android.net.NetworkCapabilities.TRANSPORT_WIFI) == true)
                        .put("transport_cellular", caps?.hasTransport(android.net.NetworkCapabilities.TRANSPORT_CELLULAR) == true)
                }
                "session.status" -> JSONObject().put("status", "active-session-required")
                else -> error("unreachable")
            }
        }
    }
}
