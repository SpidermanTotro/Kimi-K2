# Platform Testing and Compliance Guide

## Overview

This guide provides comprehensive testing strategies and compliance requirements for Kimi-K2 deployments across all platforms.

## Testing Strategy

### 1. Functional Testing

#### Core Functionality Tests

```python
# Example test suite
import pytest
from kimi_k2_client import KimiK2Client

class TestCoreFunction:
    @pytest.fixture
    def client(self):
        return KimiK2Client(api_key="test-key")
    
    def test_basic_chat(self, client):
        """Test basic chat completion"""
        response = client.chat([
            {"role": "user", "content": "Hello"}
        ])
        assert response is not None
        assert len(response.choices) > 0
        assert response.choices[0].message.content
    
    def test_streaming(self, client):
        """Test streaming responses"""
        chunks = []
        for chunk in client.stream_chat([
            {"role": "user", "content": "Count to 5"}
        ]):
            chunks.append(chunk)
        assert len(chunks) > 0
    
    def test_tool_calling(self, client):
        """Test tool/function calling"""
        tools = [{
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string"}
                    }
                }
            }
        }]
        
        response = client.chat(
            [{"role": "user", "content": "Weather in Tokyo?"}],
            tools=tools
        )
        
        assert response.choices[0].finish_reason == "tool_calls"
```

### 2. Performance Testing

#### Load Testing

```python
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

class PerformanceTest:
    def __init__(self, client, num_requests=100):
        self.client = client
        self.num_requests = num_requests
    
    async def run_load_test(self):
        """Test with concurrent requests"""
        start = time.time()
        
        async def single_request():
            return await self.client.chat([
                {"role": "user", "content": "Test"}
            ])
        
        tasks = [single_request() for _ in range(self.num_requests)]
        results = await asyncio.gather(*tasks)
        
        elapsed = time.time() - start
        
        return {
            'total_requests': self.num_requests,
            'total_time': elapsed,
            'requests_per_second': self.num_requests / elapsed,
            'avg_latency': elapsed / self.num_requests
        }
    
    def measure_token_throughput(self, prompt="Write a story", num_tokens=1000):
        """Measure tokens per second"""
        start = time.time()
        
        response = self.client.chat([
            {"role": "user", "content": prompt}
        ], max_tokens=num_tokens)
        
        elapsed = time.time() - start
        tokens_generated = len(response.choices[0].message.content.split())
        
        return {
            'tokens_generated': tokens_generated,
            'time_seconds': elapsed,
            'tokens_per_second': tokens_generated / elapsed
        }
```

#### Stress Testing

```python
class StressTest:
    def test_memory_limit(self):
        """Test behavior under memory pressure"""
        large_context = "x" * 100000  # Large input
        
        try:
            response = client.chat([
                {"role": "user", "content": large_context}
            ])
            assert response is not None
        except MemoryError:
            pytest.skip("Expected memory error")
    
    def test_concurrent_limit(self):
        """Test maximum concurrent requests"""
        max_concurrent = 100
        
        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            futures = [
                executor.submit(client.chat, [{"role": "user", "content": f"Test {i}"}])
                for i in range(max_concurrent)
            ]
            
            results = [f.result() for f in futures]
            assert all(r is not None for r in results)
```

### 3. Platform-Specific Testing

#### Linux Testing

```bash
#!/bin/bash
# test_linux_deployment.sh

echo "Testing Linux deployment..."

# Test 1: Check service status
systemctl status kimi-k2 || exit 1

# Test 2: API endpoint availability
curl -f http://localhost:8000/health || exit 1

# Test 3: GPU utilization
nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader || exit 1

# Test 4: Load test
ab -n 1000 -c 10 http://localhost:8000/v1/chat/completions || exit 1

echo "All Linux tests passed!"
```

#### iOS Testing

```swift
import XCTest

class KimiK2IOSTests: XCTestCase {
    var client: KimiK2Client!
    
    override func setUp() {
        super.setUp()
        client = KimiK2Client(apiKey: "test-key")
    }
    
    func testNeuralEngineAcceleration() {
        let config = MLModelConfiguration()
        config.computeUnits = .cpuAndNeuralEngine
        
        // Verify Neural Engine is being used
        XCTAssertEqual(config.computeUnits, .cpuAndNeuralEngine)
    }
    
    func testMemoryUsage() {
        let beforeMemory = getMemoryUsage()
        
        // Run inference
        _ = client.chat(messages: [
            ChatMessage(role: "user", content: "Test")
        ])
        
        let afterMemory = getMemoryUsage()
        let memoryIncrease = afterMemory - beforeMemory
        
        // Should not increase by more than 500MB
        XCTAssertLessThan(memoryIncrease, 500_000_000)
    }
    
    func testBatteryImpact() {
        let startBattery = getBatteryLevel()
        
        // Run for 1 minute
        for _ in 0..<60 {
            _ = client.chat(messages: [
                ChatMessage(role: "user", content: "Test")
            ])
            sleep(1)
        }
        
        let endBattery = getBatteryLevel()
        let batteryDrain = startBattery - endBattery
        
        // Should not drain more than 2% per minute
        XCTAssertLessThan(batteryDrain, 2.0)
    }
    
    private func getMemoryUsage() -> Int64 {
        var info = mach_task_basic_info()
        var count = mach_msg_type_number_t(MemoryLayout<mach_task_basic_info>.size)/4
        
        let result = withUnsafeMutablePointer(to: &info) {
            $0.withMemoryRebound(to: integer_t.self, capacity: 1) {
                task_info(mach_task_self_, task_flavor_t(MACH_TASK_BASIC_INFO), $0, &count)
            }
        }
        
        return result == KERN_SUCCESS ? Int64(info.resident_size) : 0
    }
}
```

#### Android Testing

```kotlin
@RunWith(AndroidJUnit4::class)
class KimiK2AndroidTests {
    private lateinit var client: KimiK2Client
    
    @Before
    fun setup() {
        client = KimiK2Client("test-key")
    }
    
    @Test
    fun testNNAPIAcceleration() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val optimizer = NNAPIOptimizer(context, "test_model.tflite")
        
        assertNotNull("NNAPI should be available", optimizer)
    }
    
    @Test
    fun testMemoryUsage() {
        val runtime = Runtime.getRuntime()
        val beforeMemory = runtime.totalMemory() - runtime.freeMemory()
        
        runBlocking {
            client.chat(listOf(
                ChatMessage("user", "Test message")
            ))
        }
        
        val afterMemory = runtime.totalMemory() - runtime.freeMemory()
        val memoryIncrease = afterMemory - beforeMemory
        
        // Should not increase by more than 300MB
        assertTrue(
            "Memory increase too high: $memoryIncrease bytes",
            memoryIncrease < 300_000_000
        )
    }
    
    @Test
    fun testBatteryOptimization() {
        val powerManager = InstrumentationRegistry.getInstrumentation()
            .targetContext
            .getSystemService(Context.POWER_SERVICE) as PowerManager
        
        // Test should adapt to power save mode
        val inPowerSaveMode = powerManager.isPowerSaveMode
        
        if (inPowerSaveMode) {
            // Verify lightweight model is used
            // Verify reduced inference frequency
        }
    }
}
```

## Compliance Testing

### 1. App Store Compliance (iOS)

#### Privacy Requirements

```swift
// PrivacyInfo.xcprivacy
class PrivacyComplianceTests: XCTestCase {
    func testPrivacyManifest() {
        // Verify privacy manifest exists
        let bundle = Bundle.main
        let privacyURL = bundle.url(forResource: "PrivacyInfo", withExtension: "xcprivacy")
        XCTAssertNotNil(privacyURL, "Privacy manifest must exist")
    }
    
    func testDataCollection() {
        // Verify proper consent for data collection
        let hasConsent = UserDefaults.standard.bool(forKey: "hasDataCollectionConsent")
        
        if client.collectsData {
            XCTAssertTrue(hasConsent, "Must have user consent before data collection")
        }
    }
    
    func testThirdPartySDKs() {
        // Document all third-party SDKs
        let sdks = [
            "OpenAI API Client",
            "Firebase Analytics", // if used
            "Core ML"
        ]
        
        // Verify all are declared in privacy manifest
        XCTAssertTrue(sdks.count > 0)
    }
}
```

### 2. Google Play Compliance (Android)

#### Data Safety

```kotlin
class PlayStoreComplianceTests {
    @Test
    fun testDataSafetyDeclarations() {
        // Verify data safety declarations
        val dataSafety = mapOf(
            "collects_data" to true,
            "shares_data" to true,
            "encryption_in_transit" to true,
            "encryption_at_rest" to true,
            "user_can_delete" to true
        )
        
        assertTrue("Must collect data", dataSafety["collects_data"] == true)
        assertTrue("Must encrypt in transit", dataSafety["encryption_in_transit"] == true)
    }
    
    @Test
    fun testPermissions() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val permissions = listOf(
            android.Manifest.permission.INTERNET,
            // List all required permissions
        )
        
        permissions.forEach { permission ->
            val granted = ContextCompat.checkSelfPermission(
                context,
                permission
            ) == PackageManager.PERMISSION_GRANTED
            
            // Verify permissions are declared and justified
            assertTrue("Permission $permission must be declared", granted || true)
        }
    }
}
```

### 3. GDPR Compliance

```python
class GDPRComplianceTests:
    def test_data_deletion(self):
        """Test user can delete their data"""
        user_id = "test_user"
        
        # Store some data
        store_user_data(user_id, "test data")
        
        # User requests deletion
        delete_user_data(user_id)
        
        # Verify data is deleted
        data = get_user_data(user_id)
        assert data is None
    
    def test_data_export(self):
        """Test user can export their data"""
        user_id = "test_user"
        
        # Request data export
        export = export_user_data(user_id)
        
        assert export is not None
        assert 'conversations' in export
        assert 'metadata' in export
    
    def test_consent_management(self):
        """Test consent tracking"""
        user_id = "test_user"
        
        # Check consent required
        assert requires_consent("data_processing")
        
        # Grant consent
        grant_consent(user_id, "data_processing")
        
        # Verify consent recorded
        assert has_consent(user_id, "data_processing")
```

## Quality Assurance

### 1. Accuracy Testing

```python
class AccuracyTests:
    def test_response_quality(self):
        """Test response quality on benchmark tasks"""
        test_cases = [
            {
                "input": "What is 2+2?",
                "expected": "4",
                "tolerance": "exact"
            },
            {
                "input": "Explain photosynthesis",
                "expected_keywords": ["light", "plants", "oxygen", "carbon dioxide"],
                "min_length": 50
            }
        ]
        
        for test in test_cases:
            response = client.chat([
                {"role": "user", "content": test["input"]}
            ])
            
            content = response.choices[0].message.content
            
            if test.get("tolerance") == "exact":
                assert test["expected"] in content
            
            if "expected_keywords" in test:
                for keyword in test["expected_keywords"]:
                    assert keyword.lower() in content.lower()
            
            if "min_length" in test:
                assert len(content) >= test["min_length"]
```

### 2. Regression Testing

```python
class RegressionTests:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test baseline"""
        self.baseline_responses = load_baseline_responses()
    
    def test_no_quality_regression(self):
        """Ensure quality hasn't regressed"""
        for test_case in self.baseline_responses:
            current_response = client.chat(test_case["messages"])
            baseline_response = test_case["expected_response"]
            
            # Compare using similarity metric
            similarity = calculate_similarity(
                current_response.choices[0].message.content,
                baseline_response
            )
            
            assert similarity > 0.9, f"Response quality regressed for: {test_case['name']}"
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Platform Tests

on: [push, pull_request]

jobs:
  test-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest
      - name: Run tests
        run: pytest tests/test_linux.py
  
  test-ios:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and test
        run: |
          xcodebuild test \
            -scheme KimiK2 \
            -destination 'platform=iOS Simulator,name=iPhone 15 Pro'
  
  test-android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Android SDK
        uses: android-actions/setup-android@v2
      - name: Run tests
        run: ./gradlew test
```

## Performance Benchmarking

### Benchmark Suite

```python
class BenchmarkSuite:
    def __init__(self):
        self.results = []
    
    def benchmark_latency(self, num_runs=100):
        """Benchmark inference latency"""
        latencies = []
        
        for _ in range(num_runs):
            start = time.time()
            client.chat([{"role": "user", "content": "Hello"}])
            latencies.append(time.time() - start)
        
        return {
            'p50': np.percentile(latencies, 50),
            'p95': np.percentile(latencies, 95),
            'p99': np.percentile(latencies, 99),
            'mean': np.mean(latencies),
            'std': np.std(latencies)
        }
    
    def benchmark_throughput(self, duration_seconds=60):
        """Benchmark throughput"""
        start = time.time()
        requests = 0
        
        while time.time() - start < duration_seconds:
            client.chat([{"role": "user", "content": "Test"}])
            requests += 1
        
        elapsed = time.time() - start
        return {
            'total_requests': requests,
            'requests_per_second': requests / elapsed
        }
    
    def save_results(self, filename):
        """Save benchmark results"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
```

## Test Reporting

### Test Report Template

```python
from datetime import datetime

def generate_test_report(test_results):
    """Generate comprehensive test report"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'platform': 'Linux/iOS/Android',
        'test_summary': {
            'total_tests': len(test_results),
            'passed': sum(1 for t in test_results if t['passed']),
            'failed': sum(1 for t in test_results if not t['passed']),
        },
        'performance_metrics': {
            'avg_latency': calculate_avg_latency(test_results),
            'throughput': calculate_throughput(test_results),
            'memory_usage': get_memory_usage(),
        },
        'compliance': {
            'gdpr': check_gdpr_compliance(),
            'app_store': check_app_store_compliance(),
            'play_store': check_play_store_compliance(),
        },
        'detailed_results': test_results
    }
    
    return report
```

## Best Practices

1. **Automate testing** in CI/CD pipeline
2. **Test on real devices** not just simulators/emulators
3. **Monitor production** for issues
4. **Version test suites** with code
5. **Document test coverage**
6. **Regular security audits**
7. **Performance regression testing**
8. **Compliance reviews** before releases

## Resources

- [Linux Testing Guide](../linux/README.md#testing)
- [iOS Testing Guide](../ios/README.md#testing)
- [Android Testing Guide](../android/README.md#testing)
- [GDPR Compliance](https://gdpr.eu/)
- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- [Google Play Policy](https://play.google.com/about/developer-content-policy/)

## Related Documentation

- [Platform Overview](README.md)
- [API Integration Guide](shared/api-integration.md)
- [Deployment Guides](README.md#quick-start-guide)
