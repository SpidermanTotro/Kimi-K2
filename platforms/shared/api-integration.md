# Cross-Platform API Integration Guide

## Overview

This guide provides comprehensive API integration patterns for Kimi-K2 across Linux, iOS, and Android platforms, focusing on hardware acceleration, performance optimization, and best practices.

## Platform-Specific Hardware Acceleration

### Linux - GPU and TPU Integration

#### NVIDIA GPU Acceleration

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Configure for optimal GPU usage
model = AutoModelForCausalLM.from_pretrained(
    "moonshotai/Kimi-K2-Instruct",
    device_map="auto",
    torch_dtype=torch.float16,
    attn_implementation="flash_attention_2"
)

# Multi-GPU deployment
if torch.cuda.device_count() > 1:
    model = torch.nn.DataParallel(model)

# Optimize CUDA settings
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True
```

#### AMD ROCm Acceleration

```python
import torch

# Set ROCm device
torch.cuda.set_device(0)  # ROCm appears as CUDA device

model = AutoModelForCausalLM.from_pretrained(
    "moonshotai/Kimi-K2-Instruct",
    device_map="auto",
    torch_dtype=torch.float16
)
```

#### Intel Optimization

```bash
# Install Intel Extension for PyTorch
pip install intel_extension_for_pytorch

# Use Intel optimizations
python -m intel_extension_for_pytorch.cpu.launch \
    --ncore_per_instance 8 \
    inference_script.py
```

### iOS - Apple Silicon Optimization

#### Metal Performance Shaders

```swift
import Metal
import MetalPerformanceShaders

class MetalAccelerator {
    let device: MTLDevice
    let commandQueue: MTLCommandQueue
    
    init?() {
        guard let device = MTLCreateSystemDefaultDevice(),
              let queue = device.makeCommandQueue() else {
            return nil
        }
        self.device = device
        self.commandQueue = queue
    }
    
    func matrixMultiply(
        a: MTLBuffer,
        b: MTLBuffer,
        rows: Int,
        cols: Int,
        inner: Int
    ) -> MTLBuffer? {
        guard let commandBuffer = commandQueue.makeCommandBuffer() else {
            return nil
        }
        
        let matmul = MPSMatrixMultiplication(
            device: device,
            transposeLeft: false,
            transposeRight: false,
            resultRows: rows,
            resultColumns: cols,
            interiorColumns: inner,
            alpha: 1.0,
            beta: 0.0
        )
        
        // Create result matrix descriptor
        let resultDescriptor = MPSMatrixDescriptor(
            rows: rows,
            columns: cols,
            rowBytes: cols * MemoryLayout<Float>.stride,
            dataType: .float32
        )
        
        guard let resultBuffer = device.makeBuffer(
            length: rows * cols * MemoryLayout<Float>.stride,
            options: .storageModeShared
        ) else {
            return nil
        }
        
        let resultMatrix = MPSMatrix(buffer: resultBuffer, descriptor: resultDescriptor)
        let matrixA = MPSMatrix(buffer: a, descriptor: MPSMatrixDescriptor(
            rows: rows,
            columns: inner,
            rowBytes: inner * MemoryLayout<Float>.stride,
            dataType: .float32
        ))
        let matrixB = MPSMatrix(buffer: b, descriptor: MPSMatrixDescriptor(
            rows: inner,
            columns: cols,
            rowBytes: cols * MemoryLayout<Float>.stride,
            dataType: .float32
        ))
        
        matmul.encode(
            commandBuffer: commandBuffer,
            leftMatrix: matrixA,
            rightMatrix: matrixB,
            resultMatrix: resultMatrix
        )
        
        commandBuffer.commit()
        commandBuffer.waitUntilCompleted()
        
        return resultBuffer
    }
}
```

#### Neural Engine via Core ML

```swift
import CoreML
import Accelerate

class NeuralEngineOptimizer {
    private var model: MLModel?
    
    init(modelURL: URL) {
        let config = MLModelConfiguration()
        
        // Force Neural Engine usage
        config.computeUnits = .cpuAndNeuralEngine
        config.allowLowPrecisionAccumulationOnGPU = true
        
        model = try? MLModel(contentsOf: modelURL, configuration: config)
    }
    
    func predict(input: MLFeatureProvider) -> MLFeatureProvider? {
        return try? model?.prediction(from: input)
    }
    
    // Batch prediction for efficiency
    func batchPredict(inputs: [MLFeatureProvider]) async -> [MLFeatureProvider]? {
        return try? await model?.predictions(from: inputs)
    }
}
```

#### Accelerate Framework Integration

```swift
import Accelerate

class AccelerateOptimizer {
    // SIMD-optimized vector operations
    func vectorMultiply(_ a: [Float], _ b: [Float]) -> [Float] {
        var result = [Float](repeating: 0, count: a.count)
        vDSP_vmul(a, 1, b, 1, &result, 1, vDSP_Length(a.count))
        return result
    }
    
    // Fast Fourier Transform
    func fft(_ input: [Float]) -> [Float] {
        let log2n = vDSP_Length(log2(Float(input.count)))
        guard let fftSetup = vDSP_create_fftsetup(log2n, FFTRadix(kFFTRadix2)) else {
            return input
        }
        
        defer { vDSP_destroy_fftsetup(fftSetup) }
        
        var realp = [Float](repeating: 0, count: input.count / 2)
        var imagp = [Float](repeating: 0, count: input.count / 2)
        var splitComplex = DSPSplitComplex(realp: &realp, imagp: &imagp)
        
        input.withUnsafeBytes { ptr in
            ptr.withMemoryRebound(to: DSPComplex.self) { complexPtr in
                vDSP_ctoz(complexPtr.baseAddress!, 2, &splitComplex, 1, vDSP_Length(input.count / 2))
            }
        }
        
        vDSP_fft_zrip(fftSetup, &splitComplex, 1, log2n, FFTDirection(FFT_FORWARD))
        
        return realp
    }
}
```

### Android - NPU and GPU Optimization

#### NNAPI (Neural Networks API)

```kotlin
import android.content.Context
import android.os.Build
import org.tensorflow.lite.Interpreter
import org.tensorflow.lite.nnapi.NnApiDelegate
import java.nio.ByteBuffer

class NNAPIOptimizer(context: Context, modelPath: String) {
    private val interpreter: Interpreter
    
    init {
        val options = Interpreter.Options()
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            // Use NNAPI for hardware acceleration
            val nnApiDelegate = NnApiDelegate()
            options.addDelegate(nnApiDelegate)
            
            // Additional optimizations
            options.setNumThreads(Runtime.getRuntime().availableProcessors())
            options.setUseXNNPACK(true)
        }
        
        val modelBuffer = loadModelFile(context, modelPath)
        interpreter = Interpreter(modelBuffer, options)
    }
    
    fun runInference(input: FloatArray): FloatArray {
        val output = FloatArray(1024) // Adjust size as needed
        interpreter.run(input, output)
        return output
    }
    
    private fun loadModelFile(context: Context, modelPath: String): ByteBuffer {
        val fileDescriptor = context.assets.openFd(modelPath)
        val inputStream = java.io.FileInputStream(fileDescriptor.fileDescriptor)
        val fileChannel = inputStream.channel
        val startOffset = fileDescriptor.startOffset
        val declaredLength = fileDescriptor.declaredLength
        return fileChannel.map(
            java.nio.channels.FileChannel.MapMode.READ_ONLY,
            startOffset,
            declaredLength
        )
    }
    
    fun close() {
        interpreter.close()
    }
}
```

#### GPU Delegate for TensorFlow Lite

```kotlin
import org.tensorflow.lite.gpu.GpuDelegate
import org.tensorflow.lite.gpu.CompatibilityList

class GPUOptimizer(context: Context, modelPath: String) {
    private var interpreter: Interpreter? = null
    private var gpuDelegate: GpuDelegate? = null
    
    init {
        val compatList = CompatibilityList()
        
        val options = Interpreter.Options().apply {
            if (compatList.isDelegateSupportedOnThisDevice) {
                // GPU is supported
                val delegateOptions = compatList.bestOptionsForThisDevice
                gpuDelegate = GpuDelegate(delegateOptions)
                addDelegate(gpuDelegate)
            } else {
                // Fallback to CPU with optimizations
                setUseNNAPI(true)
                setNumThreads(4)
            }
        }
        
        val modelBuffer = loadModelFile(context, modelPath)
        interpreter = Interpreter(modelBuffer, options)
    }
    
    fun inference(input: FloatArray): FloatArray {
        val output = FloatArray(vocab_size)
        interpreter?.run(input, output)
        return output
    }
    
    fun cleanup() {
        interpreter?.close()
        gpuDelegate?.close()
    }
}
```

#### Qualcomm Hexagon DSP

```kotlin
import org.tensorflow.lite.HexagonDelegate

class HexagonOptimizer(context: Context, modelPath: String) {
    private val interpreter: Interpreter
    private val hexagonDelegate: HexagonDelegate
    
    init {
        val options = Interpreter.Options()
        
        // Use Hexagon DSP if available (Qualcomm Snapdragon)
        hexagonDelegate = HexagonDelegate(context)
        options.addDelegate(hexagonDelegate)
        
        val modelBuffer = loadModelFile(context, modelPath)
        interpreter = Interpreter(modelBuffer, options)
    }
    
    fun process(input: ByteArray): ByteArray {
        val output = ByteArray(output_size)
        interpreter.run(input, output)
        return output
    }
}
```

## Unified API Client Pattern

### Cross-Platform Abstract Interface

```kotlin
// Kotlin Multiplatform
interface KimiK2API {
    suspend fun chat(messages: List<Message>): Response
    fun streamChat(messages: List<Message>): Flow<ChunkResponse>
    suspend fun embeddings(text: String): List<Float>
}

expect class KimiK2Client(apiKey: String) : KimiK2API

// Platform-specific implementations
// Android
actual class KimiK2Client actual constructor(private val apiKey: String) : KimiK2API {
    private val client = OkHttpClient()
    
    actual override suspend fun chat(messages: List<Message>): Response {
        // Android-specific implementation with NNAPI optimization
        return withContext(Dispatchers.IO) {
            // Implementation
        }
    }
}

// iOS
actual class KimiK2Client actual constructor(private val apiKey: String) : KimiK2API {
    actual override suspend fun chat(messages: List<Message>): Response {
        // iOS-specific implementation with Neural Engine
        return withContext(Dispatchers.Default) {
            // Implementation
        }
    }
}
```

### React Native Bridge

```typescript
// JavaScript/TypeScript API
import { NativeModules } from 'react-native';

interface KimiK2Module {
  chat(messages: Message[]): Promise<Response>;
  streamChat(messages: Message[], callback: (chunk: string) => void): void;
  enableHardwareAcceleration(enabled: boolean): void;
}

const { KimiK2 } = NativeModules as { KimiK2: KimiK2Module };

export class KimiK2Client {
  constructor(private apiKey: string) {}
  
  async chat(messages: Message[]): Promise<Response> {
    return KimiK2.chat(messages);
  }
  
  streamChat(
    messages: Message[],
    onChunk: (chunk: string) => void
  ): void {
    KimiK2.streamChat(messages, onChunk);
  }
}

// Native module implementation (Android)
// KimiK2Module.kt
class KimiK2Module(reactContext: ReactApplicationContext) :
    ReactContextBaseJavaModule(reactContext) {
    
    override fun getName() = "KimiK2"
    
    @ReactMethod
    fun chat(messages: ReadableArray, promise: Promise) {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val result = kimiClient.chat(messages.toMessageList())
                promise.resolve(result.toWritableMap())
            } catch (e: Exception) {
                promise.reject("CHAT_ERROR", e.message, e)
            }
        }
    }
}
```

## Performance Optimization Patterns

### Request Batching

```python
import asyncio
from typing import List

class BatchedAPI:
    def __init__(self, max_batch_size=8, max_wait_ms=100):
        self.max_batch_size = max_batch_size
        self.max_wait_ms = max_wait_ms
        self.pending_requests = []
        self.batch_task = None
    
    async def chat(self, messages: List[dict]) -> dict:
        future = asyncio.Future()
        self.pending_requests.append((messages, future))
        
        if len(self.pending_requests) >= self.max_batch_size:
            await self._process_batch()
        elif self.batch_task is None:
            self.batch_task = asyncio.create_task(self._wait_and_process())
        
        return await future
    
    async def _wait_and_process(self):
        await asyncio.sleep(self.max_wait_ms / 1000)
        await self._process_batch()
    
    async def _process_batch(self):
        if not self.pending_requests:
            return
        
        batch = self.pending_requests[:self.max_batch_size]
        self.pending_requests = self.pending_requests[self.max_batch_size:]
        self.batch_task = None
        
        # Process batch in parallel
        results = await self._batch_inference([req[0] for req in batch])
        
        for (_, future), result in zip(batch, results):
            future.set_result(result)
```

### Connection Pooling

```swift
import Foundation

class ConnectionPool {
    private let maxConnections = 10
    private var availableConnections: [URLSession] = []
    private var activeConnections: Set<URLSession> = []
    private let queue = DispatchQueue(label: "connection.pool")
    
    func getConnection() async -> URLSession {
        return await withCheckedContinuation { continuation in
            queue.async {
                if let connection = self.availableConnections.popLast() {
                    self.activeConnections.insert(connection)
                    continuation.resume(returning: connection)
                } else if self.activeConnections.count < self.maxConnections {
                    let newSession = URLSession(configuration: .default)
                    self.activeConnections.insert(newSession)
                    continuation.resume(returning: newSession)
                } else {
                    // Wait for available connection
                    // Implementation for waiting
                }
            }
        }
    }
    
    func releaseConnection(_ session: URLSession) {
        queue.async {
            self.activeConnections.remove(session)
            self.availableConnections.append(session)
        }
    }
}
```

### Retry with Exponential Backoff

```kotlin
class RetryStrategy {
    suspend fun <T> executeWithRetry(
        maxAttempts: Int = 3,
        initialDelayMs: Long = 1000,
        maxDelayMs: Long = 10000,
        factor: Double = 2.0,
        block: suspend () -> T
    ): T {
        var currentDelay = initialDelayMs
        repeat(maxAttempts - 1) { attempt ->
            try {
                return block()
            } catch (e: Exception) {
                Log.w("RetryStrategy", "Attempt ${attempt + 1} failed", e)
                delay(currentDelay)
                currentDelay = (currentDelay * factor).toLong().coerceAtMost(maxDelayMs)
            }
        }
        return block() // Last attempt without catch
    }
}

// Usage
val result = retryStrategy.executeWithRetry {
    kimiClient.chat(messages)
}
```

## Testing Hardware Acceleration

### iOS Metal Testing

```swift
import XCTest
import Metal

class MetalPerformanceTests: XCTestCase {
    func testMetalAvailability() {
        let device = MTLCreateSystemDefaultDevice()
        XCTAssertNotNil(device, "Metal is not available on this device")
    }
    
    func testNeuralEnginePerformance() async {
        let config = MLModelConfiguration()
        config.computeUnits = .cpuAndNeuralEngine
        
        // Load test model
        guard let modelURL = Bundle.main.url(forResource: "TestModel", withExtension: "mlmodelc"),
              let model = try? MLModel(contentsOf: modelURL, configuration: config) else {
            XCTFail("Failed to load model")
            return
        }
        
        let startTime = CFAbsoluteTimeGetCurrent()
        
        // Run inference
        // ... test code ...
        
        let elapsed = CFAbsoluteTimeGetCurrent() - startTime
        XCTAssertLessThan(elapsed, 0.1, "Neural Engine inference too slow")
    }
}
```

### Android GPU Testing

```kotlin
class GPUAccelerationTest {
    @Test
    fun testGPUAvailability() {
        val compatList = CompatibilityList()
        assertTrue(
            "GPU acceleration not available",
            compatList.isDelegateSupportedOnThisDevice
        )
    }
    
    @Test
    fun testInferencePerformance() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val optimizer = GPUOptimizer(context, "test_model.tflite")
        
        val input = FloatArray(1024) { Random.nextFloat() }
        
        val startTime = System.nanoTime()
        val result = optimizer.inference(input)
        val elapsed = (System.nanoTime() - startTime) / 1_000_000 // ms
        
        assertTrue("Inference too slow: ${elapsed}ms", elapsed < 100)
        optimizer.cleanup()
    }
}
```

## Monitoring and Telemetry

### Performance Metrics Collection

```python
import time
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class PerformanceMetrics:
    request_id: str
    platform: str
    hardware_type: str
    latency_ms: float
    tokens_generated: int
    memory_used_mb: float
    gpu_utilization: float
    timestamp: float

class MetricsCollector:
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
    
    def record_inference(
        self,
        platform: str,
        hardware: str,
        latency: float,
        tokens: int,
        memory: float,
        gpu_util: float
    ):
        metric = PerformanceMetrics(
            request_id=str(uuid.uuid4()),
            platform=platform,
            hardware_type=hardware,
            latency_ms=latency,
            tokens_generated=tokens,
            memory_used_mb=memory,
            gpu_utilization=gpu_util,
            timestamp=time.time()
        )
        self.metrics.append(metric)
    
    def get_average_latency(self, platform: str = None) -> float:
        filtered = self.metrics
        if platform:
            filtered = [m for m in filtered if m.platform == platform]
        
        if not filtered:
            return 0.0
        
        return sum(m.latency_ms for m in filtered) / len(filtered)
    
    def export_metrics(self) -> Dict:
        return {
            'total_requests': len(self.metrics),
            'average_latency': self.get_average_latency(),
            'by_platform': {
                platform: self.get_average_latency(platform)
                for platform in set(m.platform for m in self.metrics)
            }
        }
```

## Best Practices Summary

### Platform Selection Matrix

| Requirement | Linux | iOS | Android |
|-------------|-------|-----|---------|
| **High Throughput** | ✅ Best | ⚠️ Limited | ⚠️ Limited |
| **Low Latency** | ✅ GPU | ✅ Neural Engine | ✅ NPU/GPU |
| **Battery Efficiency** | N/A | ✅ Best | ✅ Good |
| **Scalability** | ✅ Best | ❌ Single device | ❌ Single device |
| **Cost** | 💰💰💰 High | 💰 Low | 💰 Low |

### Optimization Checklist

- [ ] Enable platform-specific hardware acceleration
- [ ] Implement connection pooling
- [ ] Add request batching where applicable
- [ ] Use appropriate quantization for target hardware
- [ ] Implement retry logic with exponential backoff
- [ ] Monitor performance metrics
- [ ] Cache responses intelligently
- [ ] Handle errors gracefully
- [ ] Test on real devices
- [ ] Profile memory usage
- [ ] Optimize for battery life (mobile)
- [ ] Document platform-specific configurations

## Resources

- [NVIDIA CUDA Documentation](https://docs.nvidia.com/cuda/)
- [Apple Metal Performance Shaders](https://developer.apple.com/documentation/metalperformanceshaders)
- [Android NNAPI Guide](https://developer.android.com/ndk/guides/neuralnetworks)
- [TensorFlow Lite GPU Delegate](https://www.tensorflow.org/lite/performance/gpu)
- [Core ML Performance Guide](https://developer.apple.com/documentation/coreml/core_ml_api/improving_model_performance)

## Related Documentation

- [Linux Platform Guide](../linux/README.md)
- [iOS Platform Guide](../ios/README.md)
- [Android Platform Guide](../android/README.md)
- [Lightweight Deployment](./lightweight-deployment.md)
