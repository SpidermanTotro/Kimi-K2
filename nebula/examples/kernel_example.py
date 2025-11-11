#!/usr/bin/env python3
"""
Example: Kernel and Process Management

This example demonstrates how to use the Nebula kernel to manage processes.
"""

import sys
import time
from pathlib import Path

# Add nebula to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kernel.kernel_module import NebulaKernel


def main():
    print("=" * 60)
    print("Nebula Kernel - Process Management Example")
    print("=" * 60)
    print()
    
    # Create and boot kernel
    kernel = NebulaKernel(total_memory=512 * 1024 * 1024)  # 512MB
    kernel.boot()
    
    print("\n" + "=" * 60)
    print("Creating processes...")
    print("=" * 60)
    
    # Create several processes
    processes = []
    for i in range(5):
        name = f"worker_{i+1}"
        memory = (i + 1) * 1024 * 1024  # 1MB, 2MB, 3MB, etc.
        pid = kernel.create_process(name, memory)
        
        if pid:
            processes.append(pid)
            print(f"✓ Created process '{name}' with PID {pid} ({memory // (1024*1024)}MB)")
        else:
            print(f"✗ Failed to create process '{name}'")
    
    print("\n" + "=" * 60)
    print("Current System State")
    print("=" * 60)
    
    # Display system info
    info = kernel.get_system_info()
    print(f"Kernel Version: {info['kernel_version']}")
    print(f"Uptime: {info['uptime']:.2f} seconds")
    print(f"Total Processes: {info['processes']}")
    print(f"Memory Usage: {info['memory']['allocated'] // (1024*1024)}MB / {info['memory']['total'] // (1024*1024)}MB")
    print(f"Free Memory: {info['memory']['free'] // (1024*1024)}MB")
    
    print("\n" + "=" * 60)
    print("Process List")
    print("=" * 60)
    
    for proc in kernel.scheduler.list_processes():
        print(f"PID {proc.pid}: {proc.name} [{proc.state.value}] - {proc.memory_allocated // (1024*1024)}MB")
    
    # Simulate some process scheduling
    print("\n" + "=" * 60)
    print("Scheduling processes (5 time slices)...")
    print("=" * 60)
    
    for i in range(5):
        proc = kernel.scheduler.schedule_next()
        if proc:
            print(f"Time slice {i+1}: Running {proc.name} (PID {proc.pid})")
            time.sleep(0.5)
    
    # Kill some processes
    print("\n" + "=" * 60)
    print("Terminating processes...")
    print("=" * 60)
    
    for pid in processes[:2]:  # Kill first two processes
        if kernel.kill_process(pid):
            print(f"✓ Terminated process PID {pid}")
    
    # Final system state
    print("\n" + "=" * 60)
    print("Final System State")
    print("=" * 60)
    
    info = kernel.get_system_info()
    print(f"Active Processes: {info['processes']}")
    print(f"Memory Usage: {info['memory']['allocated'] // (1024*1024)}MB / {info['memory']['total'] // (1024*1024)}MB")
    
    print("\nRemaining processes:")
    for proc in kernel.scheduler.list_processes():
        if proc.state.value != "terminated":
            print(f"  PID {proc.pid}: {proc.name} [{proc.state.value}]")
    
    # Shutdown
    print("\n" + "=" * 60)
    kernel.shutdown()
    print("=" * 60)


if __name__ == "__main__":
    main()
