"""
GPU monitoring and performance tracking
Provides VRAM usage monitoring, performance metrics, and memory leak detection
"""

import logging
import time
from typing import Dict, List, Optional

import torch

logger = logging.getLogger(__name__)


class GPUMonitor:
    """
    GPU monitoring and performance tracking
    """

    def __init__(self):
        self._performance_history: List[Dict] = []
        self._max_history_size = 100
        self._vram_threshold_percent = 90.0
        self._baseline_memory: Optional[float] = None

    def get_gpu_memory(self) -> Dict[str, float]:
        """
        Get current GPU memory usage
        Returns dict with total, used, free memory in MB and utilization percentage
        """
        if not torch.cuda.is_available():
            return {
                "total_mb": 0.0,
                "used_mb": 0.0,
                "free_mb": 0.0,
                "utilization_percent": 0.0,
            }

        try:
            # Get memory info for device 0
            total = torch.cuda.get_device_properties(0).total_memory / (1024**2)  # Convert to MB
            allocated = torch.cuda.memory_allocated(0) / (1024**2)
            reserved = torch.cuda.memory_reserved(0) / (1024**2)
            free = total - reserved

            utilization = (reserved / total * 100) if total > 0 else 0.0

            # Check threshold warning
            if utilization > self._vram_threshold_percent:
                logger.warning(
                    f"VRAM usage ({utilization:.1f}%) exceeds threshold "
                    f"({self._vram_threshold_percent}%)"
                )

            return {
                "total_mb": round(total, 2),
                "used_mb": round(allocated, 2),
                "reserved_mb": round(reserved, 2),
                "free_mb": round(free, 2),
                "utilization_percent": round(utilization, 2),
            }

        except Exception as e:
            logger.error(f"Failed to get GPU memory info: {e}")
            return {
                "total_mb": 0.0,
                "used_mb": 0.0,
                "free_mb": 0.0,
                "utilization_percent": 0.0,
            }

    def get_gpu_info(self) -> Dict[str, any]:
        """
        Get GPU device information
        Returns device name, CUDA version, compute capability
        """
        if not torch.cuda.is_available():
            return {
                "available": False,
                "device_name": "No CUDA device",
                "cuda_version": None,
                "compute_capability": None,
                "device_count": 0,
            }

        try:
            device_props = torch.cuda.get_device_properties(0)
            return {
                "available": True,
                "device_name": device_props.name,
                "cuda_version": torch.version.cuda,
                "compute_capability": f"{device_props.major}.{device_props.minor}",
                "device_count": torch.cuda.device_count(),
                "current_device": torch.cuda.current_device(),
            }

        except Exception as e:
            logger.error(f"Failed to get GPU info: {e}")
            return {
                "available": False,
                "device_name": "Error",
                "cuda_version": None,
                "compute_capability": None,
                "device_count": 0,
            }

    def track_model_switch(
        self,
        model_type: str,
        operation: str,
        duration: float,
        memory_before: Optional[Dict] = None,
        memory_after: Optional[Dict] = None,
    ) -> None:
        """
        Track model switch performance
        Records timing and memory usage for model loading/unloading operations

        Args:
            model_type: Type of model (stt/tts)
            operation: Operation type (load/unload)
            duration: Operation duration in seconds
            memory_before: Memory state before operation
            memory_after: Memory state after operation
        """
        record = {
            "timestamp": time.time(),
            "model_type": model_type,
            "operation": operation,
            "duration_seconds": round(duration, 3),
            "memory_before": memory_before,
            "memory_after": memory_after,
        }

        self._performance_history.append(record)

        # Trim history if too large
        if len(self._performance_history) > self._max_history_size:
            self._performance_history = self._performance_history[-self._max_history_size :]

        logger.info(
            f"Model switch tracked: {model_type} {operation} "
            f"took {duration:.2f}s, "
            f"VRAM: {memory_after.get('used_mb', 0):.1f}MB"
            if memory_after
            else ""
        )

    def get_performance_stats(self) -> Dict:
        """
        Get performance statistics
        Returns aggregated statistics from performance history
        """
        if not self._performance_history:
            return {
                "total_switches": 0,
                "avg_load_time_seconds": 0.0,
                "avg_unload_time_seconds": 0.0,
                "recent_switches": [],
            }

        load_times = [
            r["duration_seconds"] for r in self._performance_history if r["operation"] == "load"
        ]
        unload_times = [
            r["duration_seconds"] for r in self._performance_history if r["operation"] == "unload"
        ]

        avg_load = sum(load_times) / len(load_times) if load_times else 0.0
        avg_unload = sum(unload_times) / len(unload_times) if unload_times else 0.0

        # Get last 10 switches
        recent = self._performance_history[-10:]

        return {
            "total_switches": len(self._performance_history),
            "total_loads": len(load_times),
            "total_unloads": len(unload_times),
            "avg_load_time_seconds": round(avg_load, 3),
            "avg_unload_time_seconds": round(avg_unload, 3),
            "recent_switches": recent,
        }

    def detect_memory_leak(self) -> Dict[str, any]:
        """
        Detect potential memory leaks
        Compares current memory usage with baseline

        Returns:
            Dict with leak detection results
        """
        current_memory = self.get_gpu_memory()

        if self._baseline_memory is None:
            self._baseline_memory = current_memory["used_mb"]
            return {
                "leak_detected": False,
                "baseline_mb": self._baseline_memory,
                "current_mb": current_memory["used_mb"],
                "delta_mb": 0.0,
            }

        delta = current_memory["used_mb"] - self._baseline_memory
        leak_threshold_mb = 100.0  # Consider 100MB+ increase as potential leak

        leak_detected = delta > leak_threshold_mb

        if leak_detected:
            logger.warning(
                f"Potential memory leak detected: "
                f"baseline={self._baseline_memory:.1f}MB, "
                f"current={current_memory['used_mb']:.1f}MB, "
                f"delta={delta:.1f}MB"
            )

        return {
            "leak_detected": leak_detected,
            "baseline_mb": round(self._baseline_memory, 2),
            "current_mb": round(current_memory["used_mb"], 2),
            "delta_mb": round(delta, 2),
        }

    def reset_baseline(self) -> None:
        """
        Reset memory baseline
        Should be called after model unloading
        """
        current_memory = self.get_gpu_memory()
        self._baseline_memory = current_memory["used_mb"]
        logger.info(f"Memory baseline reset to {self._baseline_memory:.1f}MB")

    def set_vram_threshold(self, threshold_percent: float) -> None:
        """
        Set VRAM usage threshold for warnings

        Args:
            threshold_percent: Threshold percentage (0-100)
        """
        if 0 <= threshold_percent <= 100:
            self._vram_threshold_percent = threshold_percent
            logger.info(f"VRAM threshold set to {threshold_percent}%")
        else:
            logger.error(f"Invalid threshold: {threshold_percent}. Must be 0-100")


# Convenience functions for direct access
def get_gpu_memory() -> Dict[str, float]:
    """Get current GPU memory usage"""
    monitor = GPUMonitor()
    return monitor.get_gpu_memory()


def get_gpu_info() -> Dict[str, any]:
    """Get GPU device information"""
    monitor = GPUMonitor()
    return monitor.get_gpu_info()


def track_model_switch(
    model_type: str,
    operation: str,
    duration: float,
    memory_before: Optional[Dict] = None,
    memory_after: Optional[Dict] = None,
) -> None:
    """Track model switch performance"""
    monitor = GPUMonitor()
    monitor.track_model_switch(model_type, operation, duration, memory_before, memory_after)


def get_performance_stats() -> Dict:
    """Get performance statistics"""
    monitor = GPUMonitor()
    return monitor.get_performance_stats()


# Global GPU monitor instance
gpu_monitor = GPUMonitor()
