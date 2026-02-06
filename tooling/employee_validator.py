"""Main employee.md validator orchestrator."""

import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from concurrent.futures import TimeoutError

from .validators import (
    ValidationResult,
    ValidationError,
    RequiredFieldValidator,
    TypeValidator,
    EnumValidator,
    FormatValidator,
    RangeValidator,
)
from .parser import SecureYAMLParser, YAMLErrorContext
from .cache import get_cache
from .monitoring import get_metrics
from .constants import MAX_PARALLEL_WORKERS, DEFAULT_TIMEOUT


class EmployeeValidationOrchestrator:
    """Orchestrates all validation steps for employee.md files."""

    def __init__(
        self,
        use_cache: bool = True,
        parallel_validation: bool = False,
        enable_cache: Optional[bool] = None,
    ):
        """
        Initialize validator orchestrator.

        Args:
            use_cache: Enable caching of validation results
            parallel_validation: Enable parallel execution of validators
        """
        if enable_cache is not None:
            use_cache = enable_cache
        self.use_cache = use_cache
        self.parallel_validation = parallel_validation
        self._validator_factories: List[Callable[[], Any]] = [
            RequiredFieldValidator,
            EnumValidator,
            TypeValidator,
            FormatValidator,
            RangeValidator,
        ]
        self._cache = get_cache() if use_cache else None
        self._metrics = get_metrics()

    def validate_file(
        self, filepath: str, run_parallel_validators: Optional[bool] = None
    ) -> ValidationResult:
        """Validate an employee.md file.

        Args:
            filepath: Path to YAML file

        Returns:
            ValidationResult with errors and warnings
        """
        start_time = self._metrics.record_validation_start()
        effective_parallel = (
            self.parallel_validation
            if run_parallel_validators is None
            else run_parallel_validators
        )
        cache_key = None
        if self._cache:
            cache_key = self._get_file_cache_key(filepath)
            if cache_key:
                cached = self._cache.get(key=cache_key)
                if cached is not None:
                    self._metrics.record_validation_end(start_time, cached.is_valid)
                    return cached
        try:
            parser = SecureYAMLParser(
                allowed_directories=[str(Path(filepath).parent.resolve())]
            )
            data, _ = parser.parse_file(filepath)
        except YAMLErrorContext as e:
            error = ValidationError(
                field="file",
                message=str(e),
                line_number=e.line_number,
                severity="error",
            )
            self._metrics.record_validation_end(start_time, False)
            return ValidationResult(is_valid=False, errors=[error], warnings=[])

        result = self.validate_data(data, run_parallel_validators=effective_parallel)
        if self._cache and cache_key:
            self._cache.set(None, result, key=cache_key)
        self._metrics.record_validation_end(start_time, result.is_valid)
        return result

    def _get_file_cache_key(self, filepath: str) -> Optional[str]:
        try:
            resolved_path = Path(filepath).absolute()
            stat_info = resolved_path.stat()
        except OSError:
            return None
        return f"file:{resolved_path}:{stat_info.st_mtime_ns}:{stat_info.st_size}"

    def _create_validators(self) -> List[Any]:
        return [factory() for factory in self._validator_factories]

    def validate_data(
        self, data: Dict[str, Any], run_parallel_validators: Optional[bool] = None
    ) -> ValidationResult:
        """Validate parsed employee.md data.

        Args:
            data: Parsed YAML data as dictionary

        Returns:
            ValidationResult with errors and warnings
        """
        # Check cache
        if self._cache:
            cached = self._cache.get(data)
            if cached is not None:
                return cached

        all_errors: List[ValidationError] = []
        all_warnings: List[ValidationError] = []

        # Run all validators (parallel or sequential)
        use_parallel = (
            self.parallel_validation
            if run_parallel_validators is None
            else run_parallel_validators
        )

        if use_parallel:
            all_errors, all_warnings = self._run_validators_parallel(data)
        else:
            all_errors, all_warnings = self._run_validators_sequential(data)

        final_result = ValidationResult(
            is_valid=len(all_errors) == 0, errors=all_errors, warnings=all_warnings
        )

        # Cache result
        if self._cache:
            self._cache.set(data, final_result)

        return final_result

    def _run_validators_sequential(
        self, data: Dict[str, Any]
    ) -> Tuple[List[ValidationError], List[ValidationError]]:
        """Run all validators sequentially.

        Args:
            data: Parsed YAML data

        Returns:
            Tuple of (errors, warnings)
        """
        all_errors: List[ValidationError] = []
        all_warnings: List[ValidationError] = []

        for validator in self._create_validators():
            validator_start = time.perf_counter()
            result = validator.validate(data)
            self._metrics.record_validator_time(
                validator.__class__.__name__, time.perf_counter() - validator_start
            )
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)

        return all_errors, all_warnings

    def _run_validators_parallel(
        self, data: Dict[str, Any]
    ) -> Tuple[List[ValidationError], List[ValidationError]]:
        """Run all validators in parallel using thread pool.

        Args:
            data: Parsed YAML data

        Returns:
            Tuple of (errors, warnings)
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        all_errors: List[ValidationError] = []
        all_warnings: List[ValidationError] = []

        def run_validator(validator):
            validator_start = time.perf_counter()
            result = validator.validate(data)
            self._metrics.record_validator_time(
                validator.__class__.__name__, time.perf_counter() - validator_start
            )
            return result

        validators = self._create_validators()
        with ThreadPoolExecutor(max_workers=len(validators)) as executor:
            future_to_validator = {
                executor.submit(run_validator, validator): validator
                for validator in validators
            }

            for future in as_completed(future_to_validator):
                validator = future_to_validator[future]
                try:
                    result = future.result(timeout=DEFAULT_TIMEOUT)
                    all_errors.extend(result.errors)
                    all_warnings.extend(result.warnings)
                except TimeoutError:
                    all_errors.append(
                        ValidationError(
                            field="validation",
                            message=f"Validator {validator.__class__.__name__} timed out after {DEFAULT_TIMEOUT}s",
                            severity="error",
                        )
                    )
                except Exception as e:
                    all_errors.append(
                        ValidationError(
                            field="validation",
                            message=f"Validator {validator.__class__.__name__} failed: {e}",
                            severity="error",
                        )
                    )

        return all_errors, all_warnings

    def validate_batch(self, filepaths: List[str]) -> Dict[str, ValidationResult]:
        """Validate multiple files in batch.

        Args:
            filepaths: List of paths to YAML files

        Returns:
            Dictionary mapping filepath to ValidationResult
        """
        results = {}

        if self.parallel_validation and len(filepaths) > 1:
            from concurrent.futures import ThreadPoolExecutor, as_completed

            with ThreadPoolExecutor(
                max_workers=min(len(filepaths), MAX_PARALLEL_WORKERS)
            ) as executor:
                future_to_filepath = {
                    executor.submit(self.validate_file, filepath, False): filepath
                    for filepath in filepaths
                }

                for future in as_completed(future_to_filepath):
                    filepath = future_to_filepath[future]
                    try:
                        results[filepath] = future.result(timeout=DEFAULT_TIMEOUT)
                    except TimeoutError:
                        results[filepath] = ValidationResult(
                            is_valid=False,
                            errors=[
                                ValidationError(
                                    field="file",
                                    message=f"Validation of {filepath} timed out after {DEFAULT_TIMEOUT}s",
                                    severity="error",
                                )
                            ],
                        )
                    except Exception as e:
                        results[filepath] = ValidationResult(
                            is_valid=False,
                            errors=[
                                ValidationError(
                                    field="file",
                                    message=f"Failed to validate {filepath}: {e}",
                                    severity="error",
                                )
                            ],
                        )
        else:
            for filepath in filepaths:
                results[filepath] = self.validate_file(filepath)

        return results

    def validate_files(self, filepaths: List[str]) -> Dict[str, ValidationResult]:
        return self.validate_batch(filepaths)
