package benchmark

import (
	"fmt"
	"runtime"
	"strings"
	"time"

	"github.com/SpidermanTotro/Kimi-K2/pkg/config"
	"github.com/SpidermanTotro/Kimi-K2/pkg/model"
	"github.com/SpidermanTotro/Kimi-K2/pkg/tokenizer"
)

// BenchmarkResult holds the results of a benchmark run
type BenchmarkResult struct {
	Name               string
	TotalTime          time.Duration
	TokensPerSecond    float64
	MemoryUsedMB       float64
	PeakMemoryMB       float64
	NumTokensGenerated int
	Success            bool
	Error              error
}

// ModelBenchmark runs comprehensive benchmarks on the model
type ModelBenchmark struct {
	config *config.ModelConfig
	model  *model.GPTModel
	tok    *tokenizer.Tokenizer
}

// NewModelBenchmark creates a new benchmark instance
func NewModelBenchmark(cfg *config.ModelConfig) (*ModelBenchmark, error) {
	m, err := model.NewGPTModel(cfg)
	if err != nil {
		return nil, fmt.Errorf("failed to create model: %w", err)
	}
	
	tok := tokenizer.NewTokenizer(cfg.VocabSize)
	tok.BuildVocab([]string{
		"the quick brown fox jumps over the lazy dog",
		"hello world from the GPT model",
		"machine learning natural language processing",
	})
	
	return &ModelBenchmark{
		config: cfg,
		model:  m,
		tok:    tok,
	}, nil
}

// BenchmarkInference runs inference benchmark
func (mb *ModelBenchmark) BenchmarkInference(inputText string, maxTokens int) *BenchmarkResult {
	result := &BenchmarkResult{
		Name: "Inference",
	}
	
	// Encode input
	inputIDs := mb.tok.Encode(inputText, true)
	
	// Measure memory before
	var memBefore runtime.MemStats
	runtime.ReadMemStats(&memBefore)
	
	// Run inference
	startTime := time.Now()
	outputIDs, err := mb.model.Generate(inputIDs, maxTokens, 1.0)
	elapsed := time.Since(startTime)
	
	// Measure memory after
	var memAfter runtime.MemStats
	runtime.ReadMemStats(&memAfter)
	
	if err != nil {
		result.Error = err
		result.Success = false
		return result
	}
	
	result.Success = true
	result.TotalTime = elapsed
	result.NumTokensGenerated = len(outputIDs) - len(inputIDs)
	
	if elapsed.Seconds() > 0 {
		result.TokensPerSecond = float64(result.NumTokensGenerated) / elapsed.Seconds()
	}
	
	result.MemoryUsedMB = float64(memAfter.Alloc-memBefore.Alloc) / (1024 * 1024)
	result.PeakMemoryMB = float64(memAfter.Sys) / (1024 * 1024)
	
	return result
}

// BenchmarkForward runs forward pass benchmark
func (mb *ModelBenchmark) BenchmarkForward(seqLen int, iterations int) *BenchmarkResult {
	result := &BenchmarkResult{
		Name: "Forward Pass",
	}
	
	// Create dummy input
	inputIDs := make([]int, seqLen)
	for i := range inputIDs {
		inputIDs[i] = i % mb.config.VocabSize
	}
	
	// Warm up
	_, err := mb.model.Forward(inputIDs, false)
	if err != nil {
		result.Error = err
		result.Success = false
		return result
	}
	
	// Measure memory before
	var memBefore runtime.MemStats
	runtime.ReadMemStats(&memBefore)
	
	// Run benchmark
	startTime := time.Now()
	for i := 0; i < iterations; i++ {
		_, err = mb.model.Forward(inputIDs, false)
		if err != nil {
			result.Error = err
			result.Success = false
			return result
		}
	}
	elapsed := time.Since(startTime)
	
	// Measure memory after
	var memAfter runtime.MemStats
	runtime.ReadMemStats(&memAfter)
	
	result.Success = true
	result.TotalTime = elapsed
	result.NumTokensGenerated = seqLen * iterations
	
	if elapsed.Seconds() > 0 {
		result.TokensPerSecond = float64(result.NumTokensGenerated) / elapsed.Seconds()
	}
	
	result.MemoryUsedMB = float64(memAfter.Alloc-memBefore.Alloc) / (1024 * 1024)
	result.PeakMemoryMB = float64(memAfter.Sys) / (1024 * 1024)
	
	return result
}

// BenchmarkMemoryUsage measures peak memory usage
func (mb *ModelBenchmark) BenchmarkMemoryUsage() *BenchmarkResult {
	result := &BenchmarkResult{
		Name: "Memory Usage",
	}
	
	// Force garbage collection
	runtime.GC()
	
	var mem runtime.MemStats
	runtime.ReadMemStats(&mem)
	
	result.Success = true
	result.MemoryUsedMB = float64(mem.Alloc) / (1024 * 1024)
	result.PeakMemoryMB = float64(mem.Sys) / (1024 * 1024)
	
	return result
}

// RunAll runs all benchmarks and returns results
func (mb *ModelBenchmark) RunAll() []*BenchmarkResult {
	results := []*BenchmarkResult{}
	
	// Memory benchmark
	results = append(results, mb.BenchmarkMemoryUsage())
	
	// Forward pass benchmark with different sequence lengths
	for _, seqLen := range []int{32, 64, 128, 256} {
		if seqLen <= mb.config.MaxSeqLen {
			result := mb.BenchmarkForward(seqLen, 10)
			result.Name = fmt.Sprintf("Forward Pass (seq_len=%d)", seqLen)
			results = append(results, result)
		}
	}
	
	// Inference benchmark
	inferenceResult := mb.BenchmarkInference("hello world", 10)
	results = append(results, inferenceResult)
	
	return results
}

// PrintResults prints benchmark results in a formatted way
func PrintResults(results []*BenchmarkResult) {
	separator := strings.Repeat("=", 80)
	divider := strings.Repeat("-", 80)
	
	fmt.Println("\n" + separator)
	fmt.Println("BENCHMARK RESULTS")
	fmt.Println(separator)
	
	for i, result := range results {
		fmt.Printf("\n[%d] %s\n", i+1, result.Name)
		fmt.Println(divider)
		
		if !result.Success {
			fmt.Printf("  Status: FAILED\n")
			if result.Error != nil {
				fmt.Printf("  Error: %v\n", result.Error)
			}
			continue
		}
		
		fmt.Printf("  Status: SUCCESS\n")
		
		if result.TotalTime > 0 {
			fmt.Printf("  Total Time: %v\n", result.TotalTime)
		}
		
		if result.NumTokensGenerated > 0 {
			fmt.Printf("  Tokens Generated: %d\n", result.NumTokensGenerated)
		}
		
		if result.TokensPerSecond > 0 {
			fmt.Printf("  Tokens/Second: %.2f\n", result.TokensPerSecond)
		}
		
		if result.MemoryUsedMB > 0 {
			fmt.Printf("  Memory Used: %.2f MB\n", result.MemoryUsedMB)
		}
		
		if result.PeakMemoryMB > 0 {
			fmt.Printf("  Peak Memory: %.2f MB (%.2f GB)\n", 
				result.PeakMemoryMB, result.PeakMemoryMB/1024)
		}
	}
	
	fmt.Println("\n" + separator)
}

// GetSystemInfo returns information about the system
func GetSystemInfo() map[string]interface{} {
	var mem runtime.MemStats
	runtime.ReadMemStats(&mem)
	
	return map[string]interface{}{
		"NumCPU":        runtime.NumCPU(),
		"GOMAXPROCS":    runtime.GOMAXPROCS(0),
		"GoVersion":     runtime.Version(),
		"NumGoroutine":  runtime.NumGoroutine(),
		"AllocMB":       float64(mem.Alloc) / (1024 * 1024),
		"TotalAllocMB":  float64(mem.TotalAlloc) / (1024 * 1024),
		"SysMB":         float64(mem.Sys) / (1024 * 1024),
		"NumGC":         mem.NumGC,
	}
}

// PrintSystemInfo prints system information
func PrintSystemInfo() {
	info := GetSystemInfo()
	separator := strings.Repeat("=", 80)
	
	fmt.Println("\nSYSTEM INFORMATION")
	fmt.Println(separator)
	fmt.Printf("Go Version: %v\n", info["GoVersion"])
	fmt.Printf("CPU Cores: %v\n", info["NumCPU"])
	fmt.Printf("GOMAXPROCS: %v\n", info["GOMAXPROCS"])
	fmt.Printf("Goroutines: %v\n", info["NumGoroutine"])
	fmt.Printf("Allocated Memory: %.2f MB\n", info["AllocMB"])
	fmt.Printf("Total Allocated: %.2f MB\n", info["TotalAllocMB"])
	fmt.Printf("System Memory: %.2f MB (%.2f GB)\n", info["SysMB"], info["SysMB"].(float64)/1024)
	fmt.Printf("GC Runs: %v\n", info["NumGC"])
	fmt.Println(separator)
}
