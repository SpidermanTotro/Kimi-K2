"""
Nebula OS - Linux-like system for Kimi-K2

A comprehensive operating system with kernel, shell, and package manager.
"""

__version__ = "0.1.0"
__author__ = "Nebula Project"

from .kernel.kernel_module import NebulaKernel, ProcessScheduler, MemoryManager
from .cli.shell import NebulaShell
from .package_manager.npm import PackageManager, Package

__all__ = [
    'NebulaKernel',
    'ProcessScheduler',
    'MemoryManager',
    'NebulaShell',
    'PackageManager',
    'Package',
]
