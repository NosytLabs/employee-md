"""Performance benchmarks for employee.md validator."""

import sys
import time
from pathlib import Path
from typing import List, Dict, Callable
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tooling.employee_validator import EmployeeValidationOrchestrator
from tooling.monitoring import MetricsCollector, get_metrics, reset_metrics


class BenchmarkRunner:
    """Run performance benchmarks for the validator."""

    def __init__(self):
        self.results: Dict[str, Dict] = {}

    def run_benchmark(
        self,
        name: str,
        func: Callable,
        iterations: int = 10,
        warmup_iterations: int = 3,
    ) -> Dict[str, float]:
        """Run a benchmark with warmup.

        Args:
            name: Name of the benchmark
            func: Function to benchmark
            iterations: Number of iterations
            warmup_iterations: Number of warmup iterations

        Returns:
            Dictionary with timing results
        """
        warmup_times = []

        for _ in range(warmup_iterations):
            func()

        times = []
        for _ in range(iterations):
            start_time = time.perf_counter()
            func()
            end_time = time.perf_counter()
            times.append(end_time - start_time)

        results = {
            "min": min(times),
            "max": max(times),
            "mean": sum(times) / len(times),
            "median": sorted(times)[len(times) // 2],
            "total": sum(times),
            "iterations": iterations,
        }

        self.results[name] = results
        return results

    def compare_sequential_vs_parallel(
        self,
        orchestrator_sequential: EmployeeValidationOrchestrator,
        orchestrator_parallel: EmployeeValidationOrchestrator,
        files: List[str],
        iterations: int = 5,
    ) -> Dict[str, Dict]:
        """Compare sequential vs parallel validation performance.

        Args:
            orchestrator_sequential: Orchestrator with parallel=False
            orchestrator_parallel: Orchestrator with parallel=True
            files: List of file paths to validate
            iterations: Number of iterations

        Returns:
            Dictionary with comparison results
        """

        def run_sequential():
            orchestrator_sequential.validate_batch(files)

        def run_parallel():
            orchestrator_parallel.validate_batch(files)

        sequential_results = self.run_benchmark(
            f"sequential_{len(files)}_files", run_sequential, iterations
        )

        parallel_results = self.run_benchmark(
            f"parallel_{len(files)}_files", run_parallel, iterations
        )

        speedup = sequential_results["mean"] / parallel_results["mean"]

        return {
            "sequential": sequential_results,
            "parallel": parallel_results,
            "speedup": speedup,
            "file_count": len(files),
        }

    def benchmark_cache_hit_rate(
        self,
        orchestrator: EmployeeValidationOrchestrator,
        files: List[str],
        iterations: int = 10,
    ) -> Dict[str, float]:
        """Benchmark cache hit rate.

        Args:
            orchestrator: Orchestrator with cache enabled
            files: List of file paths to validate
            iterations: Number of iterations

        Returns:
            Dictionary with cache statistics
        """
        reset_metrics()
        metrics = get_metrics()

        for _ in range(iterations):
            for filepath in files:
                orchestrator.validate_file(filepath)

        summary = metrics.get_summary()
        total_requests = summary["cache_hits"] + summary["cache_misses"]
        hit_rate = summary["cache_hit_rate"] if total_requests > 0 else 0.0

        return {
            "cache_hits": summary["cache_hits"],
            "cache_misses": summary["cache_misses"],
            "hit_rate": hit_rate,
            "total_requests": total_requests,
        }

    def benchmark_throughput(
        self,
        orchestrator: EmployeeValidationOrchestrator,
        files: List[str],
        duration_seconds: int = 5,
    ) -> Dict[str, float]:
        """Benchmark validation throughput.

        Args:
            orchestrator: Orchestrator instance
            files: List of file paths to validate
            duration_seconds: Duration of benchmark

        Returns:
            Dictionary with throughput statistics
        """
        start_time = time.perf_counter()
        end_time = start_time + duration_seconds
        total_validations = 0

        while time.perf_counter() < end_time:
            for filepath in files:
                orchestrator.validate_file(filepath)
                total_validations += 1

        actual_duration = time.perf_counter() - start_time
        throughput = total_validations / actual_duration

        return {
            "total_validations": total_validations,
            "duration_seconds": actual_duration,
            "throughput_per_second": throughput,
            "throughput_per_minute": throughput * 60,
        }

    def print_results(self) -> None:
        """Print benchmark results in a formatted table."""
        print("\n" + "=" * 80)
        print("BENCHMARK RESULTS")
        print("=" * 80 + "\n")

        for name, results in self.results.items():
            print(f"Benchmark: {name}")
            print("-" * 40)

            if "min" in results:
                print(f"  Min:     {results['min']*1000:.3f} ms")
                print(f"  Max:     {results['max']*1000:.3f} ms")
                print(f"  Mean:    {results['mean']*1000:.3f} ms")
                print(f"  Median:  {results['median']*1000:.3f} ms")
                print(f"  Total:   {results['total']*1000:.3f} ms")
                print(f"  Iters:   {results['iterations']}")

            elif "sequential" in results:
                seq = results["sequential"]
                par = results["parallel"]
                print(f"  Sequential Mean: {seq['mean']*1000:.3f} ms")
                print(f"  Parallel Mean:   {par['mean']*1000:.3f} ms")
                print(f"  Speedup:        {results['speedup']:.2f}x")
                print(f"  Files:           {results['file_count']}")

            elif "cache_hits" in results:
                print(f"  Cache Hits:    {results['cache_hits']}")
                print(f"  Cache Misses:  {results['cache_misses']}")
                print(f"  Hit Rate:      {results['hit_rate']*100:.2f}%")
                print(f"  Total Requests: {results['total_requests']}")

            elif "total_validations" in results:
                print(f"  Total Validations:  {results['total_validations']}")
                print(f"  Duration:           {results['duration_seconds']:.2f} s")
                print(f"  Throughput/sec:     {results['throughput_per_second']:.2f}")
                print(f"  Throughput/min:     {results['throughput_per_minute']:.2f}")

            print()


def main():
    """Run all benchmarks."""
    examples_dir = Path(__file__).parent.parent.parent / "examples"
    test_files = [
        str(examples_dir / "ai-assistant.md"),
        str(examples_dir / "senior-dev.md"),
        str(examples_dir / "freelancer.md"),
        str(examples_dir / "data-analyst.md"),
        str(examples_dir / "security-auditor.md"),
    ]

    runner = BenchmarkRunner()

    print("Running performance benchmarks for employee.md validator...")
    print(f"Test files: {len(test_files)}")

    orchestrator_sequential = EmployeeValidationOrchestrator(
        use_cache=True, parallel_validation=False
    )

    orchestrator_parallel = EmployeeValidationOrchestrator(
        use_cache=True, parallel_validation=True
    )

    comparison = runner.compare_sequential_vs_parallel(
        orchestrator_sequential, orchestrator_parallel, test_files, iterations=10
    )

    cache_stats = runner.benchmark_cache_hit_rate(
        orchestrator_sequential, test_files, iterations=5
    )

    throughput = runner.benchmark_throughput(
        orchestrator_parallel, test_files, duration_seconds=3
    )

    runner.results["sequential_vs_parallel"] = comparison
    runner.results["cache_hit_rate"] = cache_stats
    runner.results["throughput"] = throughput

    runner.print_results()


if __name__ == "__main__":
    main()
