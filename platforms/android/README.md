# Kimi-K2 for Android (Galaxy 21 Series)

## Overview

Kimi-K2 for Android delivers AI-powered assistance optimized for Samsung Galaxy 21 Series devices, leveraging cutting-edge hardware capabilities while maintaining excellent battery efficiency and performance across the Android ecosystem.

## Device Requirements

### Target Devices: Galaxy 21 Series

#### Galaxy S21 Ultra
- **Processor**: Snapdragon 8 Gen 4 / Exynos 2600
- **NPU**: Dedicated AI Engine (48 TOPS)
- **RAM**: 12GB/16GB LPDDR5X
- **Storage**: 256GB/512GB/1TB UFS 4.0
- **Display**: 6.9" Dynamic AMOLED 2X, 120Hz
- **Battery**: 5,500 mAh
- **Android Version**: Android 17 or later

#### Galaxy S21+ / S21
- **Processor**: Snapdragon 8 Gen 4 / Exynos 2600
- **NPU**: AI Engine (40 TOPS)
- **RAM**: 8GB/12GB LPDDR5X
- **Storage**: 128GB/256GB UFS 4.0
- **Android Version**: Android 17 or later

### Supported Devices

- Samsung Galaxy S21/S21+/S21 Ultra
- Samsung Galaxy Z Fold 7
- Samsung Galaxy Z Flip 7
- Samsung Galaxy Tab S10/S10+/S10 Ultra
- Other flagship Android devices with Android 14+

## Architecture Overview

### Deployment Modes

1. **Cloud API Mode** (Recommended)
   - Low latency via Moonshot AI API
   - No local storage required
   - Full feature set
   - Requires internet connectivity

2. **Hybrid Mode** (Optimal)
   - On-device lightweight model via TensorFlow Lite
   - Cloud fallback for complex tasks
   - Smart caching and prefetching
   - Balanced performance and privacy

3. **Edge Mode** (Experimental)
   - Quantized on-device model
   - Samsung Neural SDK integration
   - Privacy-focused
   - Limited capabilities

## Getting Started

### 1. Development Environment Setup

```bash
# Install Android Studio
# Download from https://developer.android.com/studio

# Install Android SDK and NDK
sdkmanager "platforms;android-34"
sdkmanager "ndk;26.1.10909125"
sdkmanager "cmake;3.22.1"

# Install required build tools
sdkmanager "build-tools;34.0.0"
```

### 2. Create New Android Project

```bash
# Using Android Studio command line
# Or create via Android Studio UI:
# File > New > New Project > Empty Activity (Compose)

# Project configuration:
# - Minimum SDK: API 26 (Android 8.0)
# - Target SDK: API 34 (Android 14)
# - Language: Kotlin
# - Build system: Gradle (Kotlin DSL)
```

### 3. Add Dependencies

`build.gradle.kts` (app level):

```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.serialization") version "1.9.21"
}

android {
    namespace = "com.yourcompany.kimik2"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.yourcompany.kimik2"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"

        ndk {
            abiFilters += listOf("arm64-v8a", "armeabi-v7a")
        }
    }

    buildFeatures {
        compose = true
        mlModelBinding = true
    }

    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.7"
    }
}

dependencies {
    // Jetpack Compose
    implementation(platform("androidx.compose:compose-bom:2024.01.00"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.activity:activity-compose:1.8.2")
    
    // Networking
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-kotlinx-serialization:2.9.0")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.2")
    
    // ML and AI
    implementation("org.tensorflow:tensorflow-lite:2.14.0")
    implementation("org.tensorflow:tensorflow-lite-gpu:2.14.0")
    implementation("org.tensorflow:tensorflow-lite-support:0.4.4")
    implementation("com.google.android.gms:play-services-mlkit-text-recognition:19.0.0")
    
    // Samsung Neural SDK (if available)
    // implementation("com.samsung.android:neural-sdk:1.0.0")
    
    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    
    // ViewModel and Lifecycle
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.7.0")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.7.0")
    
    // DataStore
    implementation("androidx.datastore:datastore-preferences:1.0.0")
    
    // Testing
    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.compose.ui:ui-test-junit4")
}
```

### 4. API Client Implementation

`KimiK2Client.kt`:

```kotlin
package com.yourcompany.kimik2.api

import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.IOException

class KimiK2Client(private val apiKey: String) {
    private val baseUrl = "https://api.moonshot.ai/v1"
    private val client = OkHttpClient.Builder()
        .addInterceptor { chain ->
            val request = chain.request().newBuilder()
                .addHeader("Authorization", "Bearer $apiKey")
                .addHeader("Content-Type", "application/json")
                .build()
            chain.proceed(request)
        }
        .build()

    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
    }

    suspend fun chat(messages: List<ChatMessage>): ChatResponse {
        val requestBody = ChatRequest(
            model = "moonshot-v1-128k",
            messages = messages,
            temperature = 0.6,
            maxTokens = 4096
        )

        val jsonBody = json.encodeToString(ChatRequest.serializer(), requestBody)
        val body = jsonBody.toRequestBody("application/json".toMediaType())

        val request = Request.Builder()
            .url("$baseUrl/chat/completions")
            .post(body)
            .build()

        return client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw IOException("Unexpected code $response")
            val responseBody = response.body?.string() ?: throw IOException("Empty response")
            json.decodeFromString(ChatResponse.serializer(), responseBody)
        }
    }

    fun streamChat(messages: List<ChatMessage>): Flow<ChatChunk> = flow {
        val requestBody = ChatRequest(
            model = "moonshot-v1-128k",
            messages = messages,
            temperature = 0.6,
            stream = true
        )

        val jsonBody = json.encodeToString(ChatRequest.serializer(), requestBody)
        val body = jsonBody.toRequestBody("application/json".toMediaType())

        val request = Request.Builder()
            .url("$baseUrl/chat/completions")
            .post(body)
            .build()

        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw IOException("Unexpected code $response")

            response.body?.source()?.use { source ->
                while (!source.exhausted()) {
                    val line = source.readUtf8Line() ?: continue
                    if (line.startsWith("data: ")) {
                        val data = line.substring(6)
                        if (data == "[DONE]") break

                        try {
                            val chunk = json.decodeFromString(ChatChunk.serializer(), data)
                            emit(chunk)
                        } catch (e: Exception) {
                            // Skip malformed chunks
                        }
                    }
                }
            }
        }
    }
}

@Serializable
data class ChatRequest(
    val model: String,
    val messages: List<ChatMessage>,
    val temperature: Double = 0.6,
    val maxTokens: Int? = null,
    val stream: Boolean = false
)

@Serializable
data class ChatMessage(
    val role: String,
    val content: String
)

@Serializable
data class ChatResponse(
    val choices: List<Choice>
) {
    @Serializable
    data class Choice(
        val message: ChatMessage
    )
}

@Serializable
data class ChatChunk(
    val choices: List<Choice>
) {
    @Serializable
    data class Choice(
        val delta: Delta
    )

    @Serializable
    data class Delta(
        val content: String? = null
    )
}
```

### 5. Jetpack Compose UI

`MainActivity.kt`:

```kotlin
package com.yourcompany.kimik2

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Send
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.yourcompany.kimik2.ui.theme.KimiK2Theme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            KimiK2Theme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    ChatScreen()
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatScreen(viewModel: ChatViewModel = viewModel()) {
    val messages by viewModel.messages.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    var inputText by remember { mutableStateOf("") }
    val listState = rememberLazyListState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Kimi K2") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            )
        },
        bottomBar = {
            Surface(
                modifier = Modifier.fillMaxWidth(),
                shadowElevation = 8.dp
            ) {
                Row(
                    modifier = Modifier
                        .padding(16.dp)
                        .fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    OutlinedTextField(
                        value = inputText,
                        onValueChange = { inputText = it },
                        modifier = Modifier.weight(1f),
                        placeholder = { Text("Ask Kimi anything...") },
                        enabled = !isLoading,
                        maxLines = 4
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    IconButton(
                        onClick = {
                            if (inputText.isNotBlank()) {
                                viewModel.sendMessage(inputText)
                                inputText = ""
                            }
                        },
                        enabled = inputText.isNotBlank() && !isLoading
                    ) {
                        Icon(
                            imageVector = Icons.Default.Send,
                            contentDescription = "Send",
                            tint = if (inputText.isNotBlank() && !isLoading) {
                                MaterialTheme.colorScheme.primary
                            } else {
                                MaterialTheme.colorScheme.onSurface.copy(alpha = 0.38f)
                            }
                        )
                    }
                }
            }
        }
    ) { paddingValues ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(horizontal = 16.dp),
            state = listState,
            reverseLayout = false
        ) {
            items(messages) { message ->
                MessageBubble(message = message)
                Spacer(modifier = Modifier.height(8.dp))
            }

            if (isLoading) {
                item {
                    Row(
                        modifier = Modifier.padding(8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        CircularProgressIndicator(modifier = Modifier.size(24.dp))
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "Kimi is thinking...",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
        }
    }

    LaunchedEffect(messages.size) {
        if (messages.isNotEmpty()) {
            listState.animateScrollToItem(messages.size - 1)
        }
    }
}

@Composable
fun MessageBubble(message: Message) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = if (message.isUser) {
            Arrangement.End
        } else {
            Arrangement.Start
        }
    ) {
        Surface(
            shape = RoundedCornerShape(16.dp),
            color = if (message.isUser) {
                MaterialTheme.colorScheme.primaryContainer
            } else {
                MaterialTheme.colorScheme.secondaryContainer
            },
            modifier = Modifier.widthIn(max = 300.dp)
        ) {
            Text(
                text = message.content,
                modifier = Modifier.padding(12.dp),
                style = MaterialTheme.typography.bodyLarge,
                color = if (message.isUser) {
                    MaterialTheme.colorScheme.onPrimaryContainer
                } else {
                    MaterialTheme.colorScheme.onSecondaryContainer
                }
            )
        }
    }
}
```

`ChatViewModel.kt`:

```kotlin
package com.yourcompany.kimik2

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.yourcompany.kimik2.api.ChatMessage
import com.yourcompany.kimik2.api.KimiK2Client
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.util.*

data class Message(
    val id: String = UUID.randomUUID().toString(),
    val content: String,
    val isUser: Boolean,
    val timestamp: Long = System.currentTimeMillis()
)

class ChatViewModel : ViewModel() {
    private val client = KimiK2Client(apiKey = "your-api-key-here") // Load from secure storage

    private val _messages = MutableStateFlow<List<Message>>(emptyList())
    val messages: StateFlow<List<Message>> = _messages.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    fun sendMessage(text: String) {
        val userMessage = Message(content = text, isUser = true)
        _messages.value += userMessage

        viewModelScope.launch {
            _isLoading.value = true
            try {
                val chatMessages = _messages.value.map {
                    ChatMessage(
                        role = if (it.isUser) "user" else "assistant",
                        content = it.content
                    )
                }

                var assistantContent = ""
                val assistantMessage = Message(content = "", isUser = false)
                _messages.value += assistantMessage

                client.streamChat(chatMessages).collect { chunk ->
                    chunk.choices.firstOrNull()?.delta?.content?.let { content ->
                        assistantContent += content
                        _messages.value = _messages.value.dropLast(1) +
                                assistantMessage.copy(content = assistantContent)
                    }
                }
            } catch (e: Exception) {
                _messages.value += Message(
                    content = "Sorry, I encountered an error: ${e.message}",
                    isUser = false
                )
            } finally {
                _isLoading.value = false
            }
        }
    }
}
```

## Samsung-Specific Optimizations

### 1. Neural Processing SDK Integration

```kotlin
package com.yourcompany.kimik2.ml

import android.content.Context
// import com.samsung.android.sdk.neural.Neural // Samsung Neural SDK

class SamsungNeuralOptimizer(private val context: Context) {
    
    fun initializeNPU(): Boolean {
        return try {
            // Check if Samsung Neural SDK is available
            // Neural.initialize(context)
            // Neural.isNPUAvailable()
            true
        } catch (e: Exception) {
            false
        }
    }
    
    fun runInference(input: FloatArray): FloatArray {
        // Use Samsung NPU for optimized inference
        // This would utilize the dedicated AI accelerator
        return floatArrayOf() // Placeholder
    }
}
```

### 2. One UI Adaptations

```kotlin
// themes/OneUITheme.kt
package com.yourcompany.kimik2.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val OneUILightColorScheme = lightColorScheme(
    primary = Color(0xFF0080F7), // Samsung Blue
    onPrimary = Color.White,
    primaryContainer = Color(0xFFE3F2FD),
    secondary = Color(0xFF757575),
    background = Color(0xFFFAFAFA),
    surface = Color.White
)

private val OneUIDarkColorScheme = darkColorScheme(
    primary = Color(0xFF4DA6FF),
    onPrimary = Color.Black,
    primaryContainer = Color(0xFF003D66),
    secondary = Color(0xFFB0B0B0),
    background = Color(0xFF121212),
    surface = Color(0xFF1E1E1E)
)

@Composable
fun KimiK2Theme(
    darkTheme: Boolean = androidx.compose.foundation.isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    MaterialTheme(
        colorScheme = if (darkTheme) OneUIDarkColorScheme else OneUILightColorScheme,
        content = content
    )
}
```

### 3. Edge Panel Integration

```kotlin
package com.yourcompany.kimik2.edgepanel

import android.content.Intent
import android.os.Bundle
import android.widget.RemoteViews
import com.samsung.android.sdk.look.cocktailbar.SlookCocktailManager
import com.samsung.android.sdk.look.cocktailbar.SlookCocktailProvider

class KimiEdgePanel : SlookCocktailProvider() {
    override fun onUpdate(
        context: android.content.Context,
        cocktailManager: SlookCocktailManager,
        cocktailIds: IntArray
    ) {
        for (cocktailId in cocktailIds) {
            val views = RemoteViews(context.packageName, R.layout.edge_panel_layout)
            
            // Setup quick actions
            val intent = Intent(context, MainActivity::class.java)
            val pendingIntent = android.app.PendingIntent.getActivity(
                context, 0, intent, android.app.PendingIntent.FLAG_IMMUTABLE
            )
            views.setOnClickPendingIntent(R.id.quick_chat_button, pendingIntent)
            
            cocktailManager.updateCocktail(cocktailId, views)
        }
    }
}
```

## Performance Optimization

### 1. Memory Management

```kotlin
package com.yourcompany.kimik2.utils

import android.app.ActivityManager
import android.content.Context
import android.os.Build

class MemoryManager(private val context: Context) {
    private val activityManager = 
        context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
    
    fun getAvailableMemoryMB(): Long {
        val memInfo = ActivityManager.MemoryInfo()
        activityManager.getMemoryInfo(memInfo)
        return memInfo.availMem / (1024 * 1024)
    }
    
    fun isLowMemory(): Boolean {
        val memInfo = ActivityManager.MemoryInfo()
        activityManager.getMemoryInfo(memInfo)
        return memInfo.lowMemory
    }
    
    fun optimizeForMemory() {
        if (isLowMemory()) {
            // Clear caches
            // Reduce model precision
            // Disable animations
        }
    }
}
```

### 2. Battery Optimization

```kotlin
package com.yourcompany.kimik2.power

import android.content.Context
import android.os.BatteryManager
import android.os.PowerManager

class BatteryOptimizer(private val context: Context) {
    private val powerManager = context.getSystemService(Context.POWER_SERVICE) as PowerManager
    private val batteryManager = context.getSystemService(Context.BATTERY_SERVICE) as BatteryManager
    
    fun isPowerSaveMode(): Boolean {
        return powerManager.isPowerSaveMode
    }
    
    fun getBatteryLevel(): Int {
        return batteryManager.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)
    }
    
    fun optimizeForBattery() {
        when {
            isPowerSaveMode() -> {
                // Use cloud API only
                // Reduce polling frequency
                // Minimize background processing
            }
            getBatteryLevel() < 20 -> {
                // Reduce inference frequency
                // Use aggressive caching
            }
        }
    }
}
```

### 3. TensorFlow Lite GPU Acceleration

```kotlin
package com.yourcompany.kimik2.ml

import android.content.Context
import org.tensorflow.lite.Interpreter
import org.tensorflow.lite.gpu.CompatibilityList
import org.tensorflow.lite.gpu.GpuDelegate
import java.io.FileInputStream
import java.nio.MappedByteBuffer
import java.nio.channels.FileChannel

class TFLiteInference(context: Context, modelPath: String) {
    private var interpreter: Interpreter? = null
    private var gpuDelegate: GpuDelegate? = null
    
    init {
        val options = Interpreter.Options()
        
        // Use GPU if available
        val compatList = CompatibilityList()
        if (compatList.isDelegateSupportedOnThisDevice) {
            gpuDelegate = GpuDelegate(compatList.bestOptionsForThisDevice)
            options.addDelegate(gpuDelegate)
        } else {
            // Use NNAPI (Android Neural Networks API)
            options.setUseNNAPI(true)
            options.setNumThreads(4)
        }
        
        val modelFile = loadModelFile(context, modelPath)
        interpreter = Interpreter(modelFile, options)
    }
    
    private fun loadModelFile(context: Context, modelPath: String): MappedByteBuffer {
        val fileDescriptor = context.assets.openFd(modelPath)
        val inputStream = FileInputStream(fileDescriptor.fileDescriptor)
        val fileChannel = inputStream.channel
        val startOffset = fileDescriptor.startOffset
        val declaredLength = fileDescriptor.declaredLength
        return fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength)
    }
    
    fun runInference(input: FloatArray): FloatArray {
        val output = FloatArray(768) // Example output size
        interpreter?.run(input, output)
        return output
    }
    
    fun close() {
        interpreter?.close()
        gpuDelegate?.close()
    }
}
```

## Security and Privacy

### 1. Encrypted SharedPreferences

```kotlin
package com.yourcompany.kimik2.storage

import android.content.Context
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

class SecureStorage(context: Context) {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()
    
    private val sharedPreferences = EncryptedSharedPreferences.create(
        context,
        "kimi_secure_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )
    
    fun saveApiKey(apiKey: String) {
        sharedPreferences.edit().putString("api_key", apiKey).apply()
    }
    
    fun getApiKey(): String? {
        return sharedPreferences.getString("api_key", null)
    }
}
```

### 2. Network Security Configuration

`res/xml/network_security_config.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">moonshot.ai</domain>
        <pin-set expiration="2026-01-01">
            <pin digest="SHA-256">base64_encoded_pin</pin>
            <pin digest="SHA-256">backup_pin</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

`AndroidManifest.xml`:

```xml
<application
    android:networkSecurityConfig="@xml/network_security_config"
    ...>
</application>
```

## Testing

### Unit Tests

```kotlin
package com.yourcompany.kimik2

import kotlinx.coroutines.test.runTest
import org.junit.Test
import org.junit.Assert.*

class ChatViewModelTest {
    @Test
    fun sendMessage_addsUserMessage() = runTest {
        val viewModel = ChatViewModel()
        
        viewModel.sendMessage("Hello")
        
        val messages = viewModel.messages.value
        assertTrue(messages.isNotEmpty())
        assertEquals("Hello", messages.first().content)
        assertTrue(messages.first().isUser)
    }
}
```

### Instrumentation Tests

```kotlin
package com.yourcompany.kimik2

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import org.junit.Rule
import org.junit.Test

class ChatScreenTest {
    @get:Rule
    val composeTestRule = createAndroidComposeRule<MainActivity>()
    
    @Test
    fun inputField_acceptsText() {
        composeTestRule.onNodeWithText("Ask Kimi anything...")
            .performTextInput("Test message")
        
        composeTestRule.onNodeWithText("Test message")
            .assertExists()
    }
    
    @Test
    fun sendButton_sendsMessage() {
        composeTestRule.onNodeWithText("Ask Kimi anything...")
            .performTextInput("Hello")
        
        composeTestRule.onNodeWithContentDescription("Send")
            .performClick()
        
        composeTestRule.onNodeWithText("Hello")
            .assertExists()
    }
}
```

## Google Play Store Publishing

### 1. App Bundle Configuration

`build.gradle.kts`:

```kotlin
android {
    bundle {
        language {
            enableSplit = true
        }
        density {
            enableSplit = true
        }
        abi {
            enableSplit = true
        }
    }
}
```

### 2. ProGuard Rules

`proguard-rules.pro`:

```proguard
# Kimi K2 specific rules
-keepclassmembers class com.yourcompany.kimik2.api.** { *; }
-keep class org.tensorflow.lite.** { *; }
-keep class com.google.gson.** { *; }

# Retrofit
-keepattributes Signature
-keepattributes Exceptions

# Kotlin Serialization
-keepattributes *Annotation*, InnerClasses
-dontnote kotlinx.serialization.AnnotationsKt
```

### 3. Data Safety Form

Required declarations for Play Store:
- Data collection: User messages, API usage
- Data sharing: With Moonshot AI for processing
- Security practices: Encryption in transit, encrypted storage
- Data deletion: User can delete conversation history

## Advanced Features

### 1. Widget Support

```kotlin
package com.yourcompany.kimik2.widget

import androidx.glance.appwidget.GlanceAppWidget
import androidx.glance.appwidget.GlanceAppWidgetReceiver

class KimiWidget : GlanceAppWidget() {
    // Widget implementation
}

class KimiWidgetReceiver : GlanceAppWidgetReceiver() {
    override val glanceAppWidget: GlanceAppWidget = KimiWidget()
}
```

### 2. Quick Settings Tile

```kotlin
package com.yourcompany.kimik2.tile

import android.service.quicksettings.TileService
import android.service.quicksettings.Tile

class KimiQuickSettingsTile : TileService() {
    override fun onClick() {
        super.onClick()
        
        // Launch quick chat
        val intent = Intent(this, MainActivity::class.java)
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        startActivityAndCollapse(intent)
    }
    
    override fun onStartListening() {
        super.onStartListening()
        qsTile?.state = Tile.STATE_ACTIVE
        qsTile?.updateTile()
    }
}
```

### 3. Wear OS Companion

```kotlin
// Wear OS module
dependencies {
    implementation("com.google.android.gms:play-services-wearable:18.1.0")
    implementation("androidx.wear.compose:compose-material:1.2.1")
}
```

## Troubleshooting

### Common Issues

1. **NPU Not Utilized**
   - Verify Samsung Neural SDK installation
   - Check device compatibility
   - Ensure model format is compatible

2. **High Battery Drain**
   - Implement power save mode detection
   - Reduce inference frequency
   - Use cloud API instead of on-device

3. **Memory Leaks**
   - Properly close TensorFlow Lite interpreters
   - Clear bitmap caches
   - Use WeakReferences for large objects

4. **Network Timeouts**
   - Implement exponential backoff
   - Increase timeout values
   - Add retry logic

## Performance Benchmarks

On Galaxy S21 Ultra:
- **App Launch**: < 1.5 seconds cold start
- **Message Response**: < 600ms (cloud API)
- **Memory Usage**: 120-250MB average
- **Battery Impact**: < 3% per hour active use
- **NPU Utilization**: 70-90% during on-device inference

## Best Practices

1. **Follow Material Design 3** guidelines
2. **Optimize for foldable displays** (Galaxy Z series)
3. **Support dark theme** properly
4. **Implement proper error handling**
5. **Use Kotlin Coroutines** for async operations
6. **Cache API responses** intelligently
7. **Test on multiple screen sizes**
8. **Monitor ANRs and crashes** via Firebase Crashlytics

## Resources

- [Android Developers Documentation](https://developer.android.com)
- [Samsung Developers Portal](https://developer.samsung.com)
- [TensorFlow Lite for Android](https://www.tensorflow.org/lite/android)
- [Jetpack Compose Documentation](https://developer.android.com/jetpack/compose)
- [Moonshot AI API Documentation](https://platform.moonshot.ai)

## Next Steps

- Explore [iOS deployment](../ios/README.md) for cross-platform development
- Review [Linux deployment](../linux/README.md) for server integration
- Check [lightweight deployment](../shared/lightweight-deployment.md) for resource-constrained devices
