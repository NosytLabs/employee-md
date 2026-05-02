"""Tests for monitoring and metrics collection."""

import pytest
import time
from tooling.monitoring import (
    MetricsCollector,
    get_metrics,
    reset_metrics,
    format_prometheus_metrics,
    format_statsd_metrics,
)


class TestMetricsCollector:
    """Tests for MetricsCollector class."""

    def test_initial_state(self):
        """Test initial state of metrics collector."""
        collector = MetricsCollector()

        assert collector.total_validations == 0
        assert collector.successful_validations == 0
        assert collector.failed_validations == 0
        assert collector.total_validation_time == 0.0
        assert len(collector.individual_validator_times) == 0
        assert collector.cache_hits == 0
        assert collector.cache_misses == 0

    def test_record_validation_start(self):
        """Test recording validation start time."""
        collector = MetricsCollector()
        start_time = collector.record_validation_start()

        assert isinstance(start_time, float)
        assert start_time > 0

    def test_record_validation_end_success(self):
        """Test recording successful validation."""
        collector = MetricsCollector()
        start_time = time.time()
        time.sleep(0.01)

        duration = collector.record_validation_end(start_time, success=True)

        assert duration >= 0.01
        assert collector.total_validations == 1
        assert collector.successful_validations == 1
        assert collector.failed_validations == 0
        assert collector.total_validation_time == duration

    def test_record_validation_end_failure(self):
        """Test recording failed validation."""
        collector = MetricsCollector()
        start_time = time.time()
        time.sleep(0.01)

        duration = collector.record_validation_end(start_time, success=False)

        assert duration >= 0.01
        assert collector.total_validations == 1
        assert collector.successful_validations == 0
        assert collector.failed_validations == 1

    def test_record_cache_hit(self):
        """Test recording cache hit."""
        collector = MetricsCollector()
        collector.record_cache_hit()

        assert collector.cache_hits == 1
        assert collector.cache_misses == 0

    def test_record_cache_miss(self):
        """Test recording cache miss."""
        collector = MetricsCollector()
        collector.record_cache_miss()

        assert collector.cache_misses == 1
        assert collector.cache_hits == 0

    def test_record_validator_time(self):
        """Test recording validator time."""
        collector = MetricsCollector()
        collector.record_validator_time("TestValidator", 0.5)

        assert "TestValidator" in collector.individual_validator_times
        assert collector.individual_validator_times["TestValidator"] == 0.5

    def test_record_validator_time_accumulates(self):
        """Test that validator times accumulate."""
        collector = MetricsCollector()
        collector.record_validator_time("TypeValidator", 0.1)
        collector.record_validator_time("TypeValidator", 0.2)

        assert collector.individual_validator_times["TypeValidator"] == pytest.approx(
            0.3
        )

    def test_record_error(self):
        """Test recording validation error."""
        collector = MetricsCollector()
        collector.record_error("spec.name")

        assert "spec.name" in collector.error_counts
        assert collector.error_counts["spec.name"] == 1

    def test_record_error_accumulates(self):
        """Test that error counts accumulate."""
        collector = MetricsCollector()
        collector.record_error("spec.version")
        collector.record_error("spec.version")
        collector.record_error("spec.version")

        assert collector.error_counts["spec.version"] == 3

    def test_get_summary(self):
        """Test getting metrics summary."""
        collector = MetricsCollector()

        start_time = time.time()
        time.sleep(0.01)
        collector.record_validation_end(start_time, success=True)
        collector.record_cache_hit()
        collector.record_validator_time("TestValidator", 0.5)

        summary = collector.get_summary()

        assert summary["total_validations"] == 1
        assert summary["successful_validations"] == 1
        assert summary["failed_validations"] == 0
        assert summary["avg_validation_time_seconds"] > 0
        assert summary["cache_hit_rate"] == 1.0
        assert summary["cache_hits"] == 1
        assert summary["cache_misses"] == 0
        assert summary["individual_validator_times"]["TestValidator"] == 0.5

    def test_get_summary_multiple_validations(self):
        """Test summary with multiple validations."""
        collector = MetricsCollector()

        for i in range(3):
            start_time = time.time()
            time.sleep(0.01)
            collector.record_validation_end(start_time, success=(i < 2))

        summary = collector.get_summary()

        assert summary["total_validations"] == 3
        assert summary["successful_validations"] == 2
        assert summary["failed_validations"] == 1

    def test_get_summary_avg_validation_time(self):
        """Test average validation time calculation."""
        collector = MetricsCollector()

        collector.record_validation_end(time.time() - 0.1, success=True)
        collector.record_validation_end(time.time() - 0.2, success=True)

        summary = collector.get_summary()

        avg_time = summary["avg_validation_time_seconds"]
        assert 0.15 <= avg_time <= 0.25

    def test_get_summary_cache_hit_rate(self):
        """Test cache hit rate calculation."""
        collector = MetricsCollector()

        collector.record_cache_hit()
        collector.record_cache_hit()
        collector.record_cache_miss()

        summary = collector.get_summary()

        assert summary["cache_hit_rate"] == 2.0 / 3.0

    def test_get_summary_zero_validations(self):
        """Test summary with zero validations."""
        collector = MetricsCollector()
        summary = collector.get_summary()

        assert summary["total_validations"] == 0
        assert summary["avg_validation_time_seconds"] == 0.0
        assert summary["cache_hit_rate"] == 0.0

    def test_reset(self):
        """Test resetting metrics collector."""
        collector = MetricsCollector()

        collector.record_validation_end(time.time() - 0.1, success=True)
        collector.record_cache_hit()
        collector.record_error("test")
        collector.record_validator_time("Test", 0.5)

        collector.reset()

        assert collector.total_validations == 0
        assert collector.successful_validations == 0
        assert collector.failed_validations == 0
        assert collector.total_validation_time == 0.0
        assert len(collector.individual_validator_times) == 0
        assert collector.cache_hits == 0
        assert collector.cache_misses == 0
        assert len(collector.error_counts) == 0


class TestGlobalMetricsFunctions:
    """Tests for global metrics functions."""

    def test_get_metrics_singleton(self):
        """Test that get_metrics returns same instance."""
        reset_metrics()
        metrics1 = get_metrics()
        metrics2 = get_metrics()

        assert metrics1 is metrics2

    def test_reset_metrics(self):
        """Test resetting global metrics."""
        reset_metrics()
        metrics = get_metrics()

        metrics.record_validation_end(time.time() - 0.1, success=True)
        assert metrics.total_validations == 1

        reset_metrics()
        assert metrics.total_validations == 0


class TestPrometheusMetrics:
    """Tests for Prometheus metrics formatting."""

    def test_format_prometheus_metrics(self):
        """Test Prometheus metrics format."""
        reset_metrics()
        metrics = get_metrics()

        metrics.record_validation_end(time.time() - 0.1, success=True)
        metrics.record_cache_hit()
        metrics.record_validator_time("TestValidator", 0.5)

        output = format_prometheus_metrics(metrics)

        assert isinstance(output, str)
        assert "employee_validator_total_validations 1" in output
        assert "employee_validator_successful_validations 1" in output
        assert "employee_validator_cache_hit_rate" in output
        assert (
            'employee_validator_validator_time_seconds{validator="TestValidator"} 0.5'
            in output
        )

    def test_format_prometheus_metrics_empty(self):
        """Test Prometheus format with empty metrics."""
        reset_metrics()
        metrics = get_metrics()

        output = format_prometheus_metrics(metrics)

        assert "employee_validator_total_validations 0" in output
        assert "employee_validator_successful_validations 0" in output


class TestStatsdMetrics:
    """Tests for StatsD metrics formatting."""

    def test_format_statsd_metrics(self):
        """Test StatsD metrics format."""
        reset_metrics()
        metrics = get_metrics()

        metrics.record_validation_end(time.time() - 0.1, success=True)
        metrics.record_cache_hit()
        metrics.record_validator_time("TestValidator", 0.5)

        output = format_statsd_metrics(metrics)

        assert isinstance(output, str)
        assert "employee_validator.total_validations:1|c" in output
        assert "employee_validator.successful_validations:1|c" in output
        assert "employee_validator.cache_hit_rate" in output
        assert (
            "employee_validator.validator_time_seconds[TestValidator]:0.5|ms" in output
        )

    def test_format_statsd_metrics_empty(self):
        """Test StatsD format with empty metrics."""
        reset_metrics()
        metrics = get_metrics()

        output = format_statsd_metrics(metrics)

        assert "employee_validator.total_validations:0|c" in output
        assert "employee_validator.successful_validations:0|c" in output
