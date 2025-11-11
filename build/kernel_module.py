#!/usr/bin/env python3
"""
Nebula Kernel Module Framework

This module provides the core kernel functionality for the Nebula Linux-like system.
It manages system resources, process scheduling, and inter-process communication.
"""

import os
import sys
import time
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class ProcessState(Enum):
    """Process states in the kernel"""
    READY = "ready"
    RUNNING = "running"
    WAITING = "waiting"
    TERMINATED = "terminated"


@dataclass
class Process:
    """Process control block representation"""
    pid: int
    name: str
    state: ProcessState = ProcessState.READY
    priority: int = 0
    memory_allocated: int = 0
    created_at: float = field(default_factory=time.time)
    
    def __str__(self):
        return f"Process(pid={self.pid}, name={self.name}, state={self.state.value})"


class MemoryManager:
    """Simple memory management system"""
    
    def __init__(self, total_memory: int = 1024 * 1024 * 1024):  # 1GB default
        self.total_memory = total_memory
        self.allocated_memory = 0
        self.allocations: Dict[int, int] = {}
    
    def allocate(self, pid: int, size: int) -> bool:
        """Allocate memory for a process"""
        if self.allocated_memory + size > self.total_memory:
            return False
        
        self.allocations[pid] = self.allocations.get(pid, 0) + size
        self.allocated_memory += size
        return True
    
    def deallocate(self, pid: int) -> None:
        """Deallocate all memory for a process"""
        if pid in self.allocations:
            self.allocated_memory -= self.allocations[pid]
            del self.allocations[pid]
    
    def get_free_memory(self) -> int:
        """Get available free memory"""
        return self.total_memory - self.allocated_memory
    
    def get_stats(self) -> Dict[str, int]:
        """Get memory statistics"""
        return {
            "total": self.total_memory,
            "allocated": self.allocated_memory,
            "free": self.get_free_memory()
        }


class ProcessScheduler:
    """Simple round-robin process scheduler"""
    
    def __init__(self):
        self.processes: Dict[int, Process] = {}
        self.ready_queue: List[int] = []
        self.next_pid = 1
        self.current_process: Optional[int] = None
        self.lock = threading.Lock()
    
    def create_process(self, name: str, priority: int = 0) -> int:
        """Create a new process"""
        with self.lock:
            pid = self.next_pid
            self.next_pid += 1
            
            process = Process(pid=pid, name=name, priority=priority)
            self.processes[pid] = process
            self.ready_queue.append(pid)
            
            return pid
    
    def terminate_process(self, pid: int) -> bool:
        """Terminate a process"""
        with self.lock:
            if pid not in self.processes:
                return False
            
            self.processes[pid].state = ProcessState.TERMINATED
            if pid in self.ready_queue:
                self.ready_queue.remove(pid)
            
            return True
    
    def schedule_next(self) -> Optional[Process]:
        """Schedule the next process to run"""
        with self.lock:
            if not self.ready_queue:
                return None
            
            # Simple round-robin scheduling
            next_pid = self.ready_queue.pop(0)
            self.current_process = next_pid
            
            if next_pid in self.processes:
                self.processes[next_pid].state = ProcessState.RUNNING
                self.ready_queue.append(next_pid)
                return self.processes[next_pid]
            
            return None
    
    def get_process(self, pid: int) -> Optional[Process]:
        """Get process by PID"""
        return self.processes.get(pid)
    
    def list_processes(self) -> List[Process]:
        """List all processes"""
        return list(self.processes.values())


class NebulaKernel:
    """Main kernel class for Nebula OS"""
    
    def __init__(self, total_memory: int = 1024 * 1024 * 1024):
        self.memory_manager = MemoryManager(total_memory)
        self.scheduler = ProcessScheduler()
        self.running = False
        self.kernel_version = "0.1.0"
        self.boot_time = None
    
    def boot(self) -> bool:
        """Boot the kernel"""
        print(f"Booting Nebula Kernel v{self.kernel_version}...")
        self.boot_time = time.time()
        self.running = True
        
        # Create init process
        init_pid = self.scheduler.create_process("init", priority=10)
        self.memory_manager.allocate(init_pid, 1024 * 1024)  # 1MB for init
        
        print(f"Kernel booted successfully at {time.ctime(self.boot_time)}")
        print(f"Total memory: {self.memory_manager.total_memory // (1024*1024)} MB")
        return True
    
    def shutdown(self) -> None:
        """Shutdown the kernel"""
        print("Shutting down Nebula Kernel...")
        
        # Terminate all processes
        for pid in list(self.scheduler.processes.keys()):
            self.scheduler.terminate_process(pid)
            self.memory_manager.deallocate(pid)
        
        self.running = False
        print("Kernel shutdown complete.")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        uptime = time.time() - self.boot_time if self.boot_time else 0
        
        return {
            "kernel_version": self.kernel_version,
            "uptime": uptime,
            "boot_time": self.boot_time,
            "memory": self.memory_manager.get_stats(),
            "processes": len(self.scheduler.processes),
            "running": self.running
        }
    
    def create_process(self, name: str, memory_size: int = 1024 * 1024) -> Optional[int]:
        """Create a new process with memory allocation"""
        pid = self.scheduler.create_process(name)
        
        if not self.memory_manager.allocate(pid, memory_size):
            self.scheduler.terminate_process(pid)
            return None
        
        process = self.scheduler.get_process(pid)
        if process:
            process.memory_allocated = memory_size
        
        return pid
    
    def kill_process(self, pid: int) -> bool:
        """Kill a process and free its memory"""
        if self.scheduler.terminate_process(pid):
            self.memory_manager.deallocate(pid)
            return True
        return False


def main():
    """Main kernel entry point"""
    kernel = NebulaKernel()
    
    # Boot the kernel
    kernel.boot()
    
    # Display system info
    print("\nSystem Information:")
    for key, value in kernel.get_system_info().items():
        print(f"  {key}: {value}")
    
    # Create some test processes
    print("\nCreating test processes...")
    pid1 = kernel.create_process("test_process_1", 2 * 1024 * 1024)
    pid2 = kernel.create_process("test_process_2", 3 * 1024 * 1024)
    
    print(f"Created processes: {pid1}, {pid2}")
    
    # List all processes
    print("\nActive processes:")
    for proc in kernel.scheduler.list_processes():
        print(f"  {proc}")
    
    # Memory stats
    print("\nMemory statistics:")
    for key, value in kernel.memory_manager.get_stats().items():
        print(f"  {key}: {value // (1024*1024)} MB")
    
    # Shutdown
    input("\nPress Enter to shutdown...")
    kernel.shutdown()


if __name__ == "__main__":
    main()
