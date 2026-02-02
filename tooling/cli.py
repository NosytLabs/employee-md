"""Command-line interface for employee.md validator."""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, List, Optional

from .employee_validator import EmployeeValidationOrchestrator
from .validators import (
    ValidationResult,
    set_production_mode,
)
from .cache import reset_cache
from .logging_config import get_logger, ValidatorLogger
from .monitoring import (
    get_metrics,
    format_prometheus_metrics,
    format_statsd_metrics,
)
from .config import load_config, Config
from .constants import VERSION


class OutputFormatter:
    """Format validation results for different output types."""

    @staticmethod
    def format_text(result: ValidationResult, filename: Optional[str] = None) -> str:
        """Format results as human-readable text."""
        lines = []

        if filename:
            lines.append(f"\n{'='*60}")
            lines.append(f"File: {filename}")
            lines.append(f"{'='*60}\n")

        if result.is_valid:
            lines.append("✓ Validation passed!")
        else:
            lines.append("❌ Validation failed!")

        if result.errors:
            lines.append("\nErrors:")
            for error in result.errors:
                line = f"  ✗ {error.field}: {error.message}"
                if error.line_number:
                    line += f" (line {error.line_number})"
                lines.append(line)
                if error.suggestion:
                    lines.append(f"    💡 Suggestion: {error.suggestion}")

        if result.warnings:
            lines.append("\nWarnings:")
            for warning in result.warnings:
                line = f"  ⚠ {warning.field}: {warning.message}"
                if warning.line_number:
                    line += f" (line {warning.line_number})"
                lines.append(line)

        return "\n".join(lines)

    @staticmethod
    def format_json(result: ValidationResult, filename: Optional[str] = None) -> str:
        """Format results as JSON."""
        output: dict[str, Any] = {
            "valid": result.is_valid,
            "error_count": result.error_count,
            "warning_count": result.warning_count,
        }

        if filename:
            output["file"] = filename

        if result.errors:
            output["errors"] = [
                {
                    "field": e.field,
                    "message": e.message,
                    "line_number": e.line_number,
                    "severity": e.severity,
                }
                for e in result.errors
            ]

        if result.warnings:
            output["warnings"] = [
                {
                    "field": w.field,
                    "message": w.message,
                    "line_number": w.line_number,
                    "severity": w.severity,
                }
                for w in result.warnings
            ]

        return json.dumps(output, indent=2)

    @staticmethod
    def format_compact(result: ValidationResult, filename: Optional[str] = None) -> str:
        """Format results in a compact single-line format."""
        prefix = f"{filename}: " if filename else ""
        status = "✓ PASS" if result.is_valid else "✗ FAIL"
        details = f"{result.error_count}E/{result.warning_count}W"
        return f"{prefix}{status} ({details})"


def filter_files(files: List[str], config: Config) -> List[str]:
    """Apply file filters from configuration.

    Args:
        files: List of file paths to filter
        config: Configuration object containing filter rules

    Returns:
        Filtered list of file paths
    """
    filtered = []
    exclude_patterns = config.get("file_filters.exclude_patterns", [])

    for filepath in files:
        path = Path(filepath)
        should_exclude = False

        for pattern in exclude_patterns:
            directory = pattern.get("directory")
            excluded_files = pattern.get("files", [])

            if directory and path.parent.name == directory:
                if excluded_files and path.name in excluded_files:
                    should_exclude = True
                    break

        if not should_exclude:
            filtered.append(filepath)

    return filtered


def validate_files(
    files: List[str],
    output_format: str = "text",
    no_cache: bool = False,
    parallel: bool = False,
    production_mode: bool = False,
    log_level: int = logging.INFO,
    metrics_format: Optional[str] = None,
    logger: Optional[ValidatorLogger] = None,
) -> int:
    """Validate multiple files and return exit code.

    Args:
        files: List of file paths to validate
        output_format: Output format (text, json, compact)
        no_cache: Disable caching
        parallel: Enable parallel validation
        production_mode: Enable production mode (sanitized errors)
        log_level: Logging level
        metrics_format: Optional metrics output format (prometheus, statsd)
        logger: Optional logger instance

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    if logger is None:
        logger = get_logger(level=log_level)

    logger.set_level(log_level)
    set_production_mode(production_mode)

    metrics = get_metrics()

    orchestrator = EmployeeValidationOrchestrator(
        use_cache=not no_cache, parallel_validation=parallel
    )

    all_valid = True
    batch_results = orchestrator.validate_batch(files)

    # Print results based on format
    if output_format == "json":
        # JSON format outputs all results as a JSON array
        output = []
        for filepath in files:
            result = batch_results[filepath]
            output.append(json.loads(OutputFormatter.format_json(result, filepath)))
        print(json.dumps(output, indent=2))
    else:
        # Text or compact format
        for filepath in files:
            result = batch_results[filepath]

            if output_format == "compact":
                print(OutputFormatter.format_compact(result, filepath))
            else:
                print(OutputFormatter.format_text(result, filepath))

            if not result.is_valid:
                all_valid = False
                for error in result.errors:
                    metrics.record_error(error.field)

    # Output metrics if requested
    if metrics_format:
        if metrics_format == "prometheus":
            print(format_prometheus_metrics(metrics))
        elif metrics_format == "statsd":
            print(format_statsd_metrics(metrics))

    # Log summary
    summary = metrics.get_summary()
    logger.info(
        f'Validation complete: {summary["total_validations"]} files, '
        f'{summary["successful_validations"]} passed, {summary["failed_validations"]} failed'
    )

    return 0 if all_valid else 1


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for CLI."""
    parser = argparse.ArgumentParser(
        prog="validate",
        description="Validate employee.md YAML configuration files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s employee.md                    Validate a single file
  %(prog)s examples/*.md                  Validate multiple files
  %(prog)s employee.md --format json       Output as JSON
  %(prog)s employee.md --no-cache         Disable caching
  %(prog)s examples/*.md --format compact Compact output for multiple files
  %(prog)s employee.md --parallel          Enable parallel validation
  %(prog)s employee.md --production        Enable production mode (sanitized errors)
  %(prog)s employee.md --verbose           Enable verbose logging
  %(prog)s employee.md --metrics prometheus  Export metrics in Prometheus format
        """,
    )

    parser.add_argument("files", nargs="*", help="YAML file(s) to validate")

    parser.add_argument("--config", "-c", help="Path to configuration file")

    parser.add_argument(
        "--format",
        "-f",
        choices=["text", "json", "compact"],
        default="text",
        help="Output format (default: text)",
    )

    parser.add_argument(
        "--no-cache", action="store_true", help="Disable caching of validation results"
    )

    parser.add_argument(
        "--clear-cache", action="store_true", help="Clear validation cache and exit"
    )

    parser.add_argument(
        "--parallel", action="store_true", help="Enable parallel validation execution"
    )

    parser.add_argument(
        "--production",
        action="store_true",
        help="Enable production mode (sanitizes error messages)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose (debug) logging"
    )

    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress all output except errors"
    )

    parser.add_argument(
        "--metrics",
        choices=["prometheus", "statsd"],
        default=None,
        help="Export validation metrics in specified format",
    )

    parser.add_argument(
        "--version", action="version", version=f"employee.md Validator v{VERSION}"
    )

    return parser


def main() -> int:
    """Main entry point for CLI."""
    parser = create_parser()
    args = parser.parse_args()

    # Handle cache clearing (before checking for files)
    if args.clear_cache:
        reset_cache()
        print("Cache cleared.")
        return 0

    # Check for files argument
    if not hasattr(args, "files") or not args.files:
        print(
            "Error: No files specified. Use --help for usage information.",
            file=sys.stderr,
        )
        return 1

    # Load configuration file if specified
    config_file = getattr(args, "config", None)
    config = load_config(config_file=config_file)

    # Determine log level (CLI args override config)
    if args.verbose:
        log_level = logging.DEBUG
    elif args.quiet:
        log_level = logging.ERROR
    else:
        log_level = getattr(logging, config.get("logging.level", "INFO"), logging.INFO)

    # Expand glob patterns
    files = []
    for pattern in args.files:
        path = Path(pattern)
        if path.exists():
            if path.is_file():
                files.append(str(path))
            elif path.is_dir():
                files.extend(str(p) for p in path.glob("**/*.md"))
        else:
            # Try glob expansion
            parent = Path(pattern).parent
            glob_pattern = Path(pattern).name
            if parent.exists():
                files.extend(str(p) for p in parent.glob(glob_pattern))

    # Apply file filters from configuration
    files = filter_files(files, config)

    if not files:
        print("Error: No files found to validate", file=sys.stderr)
        return 1

    return validate_files(
        files=files,
        output_format=args.format,
        no_cache=args.no_cache,
        parallel=args.parallel,
        production_mode=args.production,
        log_level=log_level,
        metrics_format=args.metrics,
    )


def create_parser_with_defaults(config: Config) -> argparse.ArgumentParser:
    """Create argument parser with config-based defaults."""
    parser = argparse.ArgumentParser(
        prog="validate",
        description="Validate employee.md YAML files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s employee.md
  %(prog)s employee.md --format json
  %(prog)s examples/*.md --format compact
  %(prog)s employee.md --parallel
  %(prog)s employee.md --production
  %(prog)s employee.md --verbose
  %(prog)s employee.md --metrics prometheus
        """,
    )

    parser.add_argument("files", nargs="+", help="YAML file(s) to validate")

    parser.add_argument("--config", "-c", help="Path to configuration file")

    parser.add_argument(
        "--format",
        "-f",
        choices=["text", "json", "compact"],
        default=config.get("logging.format", "text"),
        help="Output format (default: text)",
    )

    parser.add_argument(
        "--no-cache",
        action="store_true",
        default=not config.get("cache.enabled", True),
        help="Disable caching of validation results",
    )

    parser.add_argument(
        "--clear-cache", action="store_true", help="Clear validation cache and exit"
    )

    parser.add_argument(
        "--parallel",
        action="store_true",
        default=config.get("parallel", False),
        help="Enable parallel validation execution",
    )

    parser.add_argument(
        "--production",
        action="store_true",
        default=config.get("production", False),
        help="Enable production mode (sanitizes error messages)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=config.get("verbose", False),
        help="Enable verbose (debug) logging",
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        default=config.get("quiet", False),
        help="Suppress all output except errors",
    )

    parser.add_argument(
        "--metrics",
        choices=["prometheus", "statsd"],
        default=(
            config.get("metrics.format", None)
            if config.get("metrics.enabled", False)
            else None
        ),
        help="Export validation metrics in specified format",
    )

    parser.add_argument(
        "--version", action="version", version=f"employee.md Validator v{VERSION}"
    )

    return parser


if __name__ == "__main__":
    sys.exit(main())
