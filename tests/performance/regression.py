"""Performance regression tests for employee.md validator."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tooling.employee_validator import EmployeeValidationOrchestrator
from tooling.constants import (
    REGRESSION_THRESHOLD,
    REGRESSION_THRESHOLD_PER_FILE,
    REGRESSION_THRESHOLD_PER_VALIDATION,
    REGRESSION_THRESHOLD_THROUGHPUT,
)


class PerformanceRegressionTests:
    """Performance regression tests."""

    def __init__(self):
        self.orchestrator = EmployeeValidationOrchestrator(
            use_cache=False, parallel_validation=False
        )
        self.examples_dir = Path(__file__).parent.parent.parent / "examples"

    def test_single_file_validation_performance(self):
        """Test single file validation performance."""
        test_file = self.examples_dir / "minimal.md"

        start_time = time.perf_counter()
        result = self.orchestrator.validate_file(str(test_file))
        end_time = time.perf_counter()

        duration_ms = (end_time - start_time) * 1000

        print(f"Single file validation: {duration_ms:.2f}ms")

        assert (
            duration_ms < REGRESSION_THRESHOLD
        ), f"Single file validation too slow: {duration_ms:.2f}ms > {REGRESSION_THRESHOLD}ms threshold"

    def test_batch_validation_performance(self):
        """Test batch validation performance."""
        test_files = [
            self.examples_dir / "minimal.md",
            self.examples_dir / "ai-assistant.md",
            self.examples_dir / "senior-dev.md",
        ]

        start_time = time.perf_counter()
        results = self.orchestrator.validate_batch([str(f) for f in test_files])
        end_time = time.perf_counter()

        duration_ms = (end_time - start_time) * 1000
        duration_per_file = duration_ms / len(test_files)

        print(
            f"Batch validation ({len(test_files)} files): {duration_ms:.2f}ms ({duration_per_file:.2f}ms per file)"
        )

        assert (
            duration_per_file < REGRESSION_THRESHOLD_PER_FILE
        ), f"Batch validation too slow: {duration_per_file:.2f}ms/file > {REGRESSION_THRESHOLD_PER_FILE}ms/file threshold"

    def test_parallel_validation_performance(self):
        """Test parallel validation performance."""
        orchestrator_parallel = EmployeeValidationOrchestrator(
            use_cache=False, parallel_validation=True
        )

        test_files = [
            self.examples_dir / "minimal.md",
            self.examples_dir / "ai-assistant.md",
            self.examples_dir / "senior-dev.md",
        ]

        start_time = time.perf_counter()
        results = orchestrator_parallel.validate_batch([str(f) for f in test_files])
        end_time = time.perf_counter()

        duration_ms = (end_time - start_time) * 1000
        duration_per_file = duration_ms / len(test_files)

        print(
            f"Parallel validation ({len(test_files)} files): {duration_ms:.2f}ms ({duration_per_file:.2f}ms per file)"
        )

        assert (
            duration_per_file < REGRESSION_THRESHOLD_PER_FILE
        ), f"Parallel validation too slow: {duration_per_file:.2f}ms/file > {REGRESSION_THRESHOLD_PER_FILE}ms/file threshold"

    def test_cache_performance(self):
        """Test cache performance improvement."""
        test_file = self.examples_dir / "minimal.md"

        orchestrator_with_cache = EmployeeValidationOrchestrator(
            use_cache=True, parallel_validation=False
        )

        warmup_iterations = 10
        test_iterations = 100

        for _ in range(warmup_iterations):
            orchestrator_with_cache.validate_file(str(test_file))

        start_time = time.perf_counter()
        for _ in range(test_iterations):
            orchestrator_with_cache.validate_file(str(test_file))
        end_time = time.perf_counter()

        duration_ms = (end_time - start_time) * 1000
        duration_per_validation = duration_ms / test_iterations

        print(
            f"Cache performance (100 validations): {duration_ms:.2f}ms ({duration_per_validation:.4f}ms per validation)"
        )

        assert (
            duration_per_validation < REGRESSION_THRESHOLD_PER_VALIDATION
        ), f"Cache validation too slow: {duration_per_validation:.4f}ms > {REGRESSION_THRESHOLD_PER_VALIDATION}ms threshold"

    def test_throughput(self):
        """Test validation throughput."""
        test_file = self.examples_dir / "minimal.md"

        duration_seconds = 3.0
        start_time = time.perf_counter()
        end_time = start_time + duration_seconds

        total_validations = 0
        while time.perf_counter() < end_time:
            self.orchestrator.validate_file(str(test_file))
            total_validations += 1

        actual_duration = time.perf_counter() - start_time
        throughput = total_validations / actual_duration

        print(
            f"Throughput: {throughput:.2f} validations/second ({total_validations} validations in {actual_duration:.2f}s)"
        )

        assert (
            throughput > REGRESSION_THRESHOLD_THROUGHPUT
        ), f"Throughput too low: {throughput:.2f}/s < {REGRESSION_THRESHOLD_THROUGHPUT}/s threshold"

    def run_all_tests(self):
        """Run all performance regression tests."""
        print("\n" + "=" * 60)
        print("PERFORMANCE REGRESSION TESTS")
        print("=" * 60 + "\n")

        try:
            self.test_single_file_validation_performance()
            print("✓ Single file validation performance OK\n")
        except AssertionError as e:
            print(f"✗ Single file validation performance FAILED: {e}\n")

        try:
            self.test_batch_validation_performance()
            print("✓ Batch validation performance OK\n")
        except AssertionError as e:
            print(f"✗ Batch validation performance FAILED: {e}\n")

        try:
            self.test_parallel_validation_performance()
            print("✓ Parallel validation performance OK\n")
        except AssertionError as e:
            print(f"✗ Parallel validation performance FAILED: {e}\n")

        try:
            self.test_cache_performance()
            print("✓ Cache performance OK\n")
        except AssertionError as e:
            print(f"✗ Cache performance FAILED: {e}\n")

        try:
            self.test_throughput()
            print("✓ Throughput OK\n")
        except AssertionError as e:
            print(f"✗ Throughput FAILED: {e}\n")

        print("=" * 60)
        print("PERFORMANCE REGRESSION TESTS COMPLETE")
        print("=" * 60)


def main():
    """Run performance regression tests."""
    tests = PerformanceRegressionTests()
    tests.run_all_tests()


if __name__ == "__main__":
    main()
