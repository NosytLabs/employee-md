"""Monitoring and metrics collection for validation operations."""

import threading
import time
from typing import Dict, Optional
from dataclasses import dataclass, field


@dataclass
class MetricsCollector:
    """Collects and tracks validation metrics."""

    total_validations: int = 0
    successful_validations: int = 0
    failed_validations: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    total_validation_time: float = 0.0
    individual_validator_times: Dict[str, float] = field(default_factory=dict)
    error_counts: Dict[str, int] = field(default_factory=dict)
    cache_size: int = 0
    cache_max_size: int = 100
    cache_evictions: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def record_validation_start(self) -> float:
        """Record start of validation and return timestamp."""
        return time.time()

    def record_validation_end(self, start_time: float, success: bool) -> float:
        """Record end of validation and return duration."""
        duration = time.time() - start_time
        with self._lock:
            self.total_validations += 1
            self.total_validation_time += duration

            if success:
                self.successful_validations += 1
            else:
                self.failed_validations += 1

        return duration

    def record_cache_hit(self) -> None:
        """Record a cache hit."""
        with self._lock:
            self.cache_hits += 1

    def record_cache_miss(self) -> None:
        """Record a cache miss."""
        with self._lock:
            self.cache_misses += 1

    def record_validator_time(self, validator_name: str, duration: float) -> None:
        """Record time for individual validator."""
        with self._lock:
            if validator_name not in self.individual_validator_times:
                self.individual_validator_times[validator_name] = 0.0
            self.individual_validator_times[validator_name] += duration

    def record_error(self, error_type: str) -> None:
        """Record an error type."""
        with self._lock:
            if error_type not in self.error_counts:
                self.error_counts[error_type] = 0
            self.error_counts[error_type] += 1

    def record_cache_size(self, current_size: int, max_size: int) -> None:
        """Record cache size metrics."""
        with self._lock:
            self.cache_size = current_size
            self.cache_max_size = max_size

    def record_cache_eviction(self) -> None:
        """Record a cache eviction event."""
        with self._lock:
            self.cache_evictions += 1

    def get_summary(self) -> Dict:
        """Get metrics summary."""
        with self._lock:
            cache_hit_rate = 0.0
            if self.cache_hits + self.cache_misses > 0:
                cache_hit_rate = self.cache_hits / (self.cache_hits + self.cache_misses)

            avg_validation_time = 0.0
            if self.total_validations > 0:
                avg_validation_time = (
                    self.total_validation_time / self.total_validations
                )

            cache_utilization = 0.0
            if self.cache_max_size > 0:
                cache_utilization = self.cache_size / self.cache_max_size

            return {
                "total_validations": self.total_validations,
                "successful_validations": self.successful_validations,
                "failed_validations": self.failed_validations,
                "cache_hit_rate": cache_hit_rate,
                "cache_hits": self.cache_hits,
                "cache_misses": self.cache_misses,
                "cache_size": self.cache_size,
                "cache_max_size": self.cache_max_size,
                "cache_utilization": cache_utilization,
                "cache_evictions": self.cache_evictions,
                "avg_validation_time_seconds": avg_validation_time,
                "total_validation_time_seconds": self.total_validation_time,
                "individual_validator_times": dict(self.individual_validator_times),
                "error_counts": dict(self.error_counts),
            }

    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self.total_validations = 0
            self.successful_validations = 0
            self.failed_validations = 0
            self.cache_hits = 0
            self.cache_misses = 0
            self.total_validation_time = 0.0
            self.individual_validator_times.clear()
            self.error_counts.clear()
            self.cache_size = 0
            self.cache_evictions = 0


# Global metrics collector
_global_metrics: Optional[MetricsCollector] = None
_global_metrics_lock = threading.Lock()


def get_metrics() -> MetricsCollector:
    """Get global metrics collector instance."""
    global _global_metrics
    with _global_metrics_lock:
        if _global_metrics is None:
            _global_metrics = MetricsCollector()
        return _global_metrics


def reset_metrics() -> None:
    """Reset global metrics collector."""
    global _global_metrics
    with _global_metrics_lock:
        if _global_metrics is not None:
            _global_metrics.reset()


def format_prometheus_metrics(metrics: MetricsCollector) -> str:
    """Format metrics for Prometheus.

    Args:
        metrics: MetricsCollector instance

    Returns:
        Prometheus-formatted metrics string
    """
    summary = metrics.get_summary()
    lines = []

    lines.append(f"employee_validator_total_validations {summary['total_validations']}")
    lines.append(
        f"employee_validator_successful_validations {summary['successful_validations']}"
    )
    lines.append(
        f"employee_validator_failed_validations {summary['failed_validations']}"
    )
    lines.append(f"employee_validator_cache_hit_rate {summary['cache_hit_rate']}")
    lines.append(f"employee_validator_cache_hits {summary['cache_hits']}")
    lines.append(f"employee_validator_cache_misses {summary['cache_misses']}")
    lines.append(f"employee_validator_cache_size {summary['cache_size']}")
    lines.append(f"employee_validator_cache_max_size {summary['cache_max_size']}")
    lines.append(f"employee_validator_cache_utilization {summary['cache_utilization']}")
    lines.append(f"employee_validator_cache_evictions {summary['cache_evictions']}")
    lines.append(
        f"employee_validator_avg_validation_time_seconds {summary['avg_validation_time_seconds']}"
    )
    lines.append(
        f"employee_validator_total_validation_time_seconds {summary['total_validation_time_seconds']}"
    )

    for validator_name, total_time in summary["individual_validator_times"].items():
        lines.append(
            f'employee_validator_validator_time_seconds{{validator="{validator_name}"}} {total_time}'
        )

    return "\n".join(lines)


def format_statsd_metrics(metrics: MetricsCollector) -> str:
    """Format metrics for StatsD.

    Args:
        metrics: MetricsCollector instance

    Returns:
        StatsD-formatted metrics string
    """
    summary = metrics.get_summary()
    lines = []

    lines.append(
        f"employee_validator.total_validations:{summary['total_validations']}|c"
    )
    lines.append(
        f"employee_validator.successful_validations:{summary['successful_validations']}|c"
    )
    lines.append(
        f"employee_validator.failed_validations:{summary['failed_validations']}|c"
    )
    lines.append(f"employee_validator.cache_hit_rate:{summary['cache_hit_rate']}|c")
    lines.append(f"employee_validator.cache_hits:{summary['cache_hits']}|c")
    lines.append(f"employee_validator.cache_misses:{summary['cache_misses']}|c")
    lines.append(f"employee_validator.cache_size:{summary['cache_size']}|g")
    lines.append(f"employee_validator.cache_max_size:{summary['cache_max_size']}|g")
    lines.append(
        f"employee_validator.cache_utilization:{summary['cache_utilization']}|g"
    )
    lines.append(f"employee_validator.cache_evictions:{summary['cache_evictions']}|c")
    lines.append(
        f"employee_validator.avg_validation_time_seconds:{summary['avg_validation_time_seconds']}|c"
    )
    lines.append(
        f"employee_validator.total_validation_time_seconds:{summary['total_validation_time_seconds']}|c"
    )

    for validator_name, total_time in summary["individual_validator_times"].items():
        lines.append(
            f"employee_validator.validator_time_seconds[{validator_name}]:{total_time}|ms"
        )

    return "\n".join(lines)
