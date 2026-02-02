"""Configuration management for employee.md validator."""

import os
import json
import logging
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union, cast

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for employee.md validator."""

    def __init__(
        self, config_file: Optional[str] = None, env_prefix: str = "EMPLOYEE_MD_"
    ):
        """Initialize configuration.

        Args:
            config_file: Path to configuration file (.employe-validatorrc, config.yaml)
            env_prefix: Prefix for environment variables
        """
        self.config_file = config_file
        self.env_prefix = env_prefix
        self._config: Dict[str, Any] = {}

        self._load_defaults()
        self._load_config_file()
        self._load_env_vars()

    def _load_defaults(self) -> None:
        """Load default configuration values."""
        self._config = {
            "parallel": False,
            "production": False,
            "verbose": False,
            "quiet": False,
            "cache": {"enabled": True, "size": 100, "ttl": 300},
            "logging": {"level": "INFO", "format": "text"},
            "metrics": {"enabled": False, "format": "prometheus"},
            "allowed_directories": [],
            "file_filters": {
                "exclude_patterns": [
                    {
                        "directory": "examples",
                        "files": ["README.md", "molt-bot-integration.md"],
                    }
                ]
            },
        }

    def _load_config_file(self) -> None:
        """Load configuration from file."""
        if not self.config_file:
            self._auto_discover_config_file()

        if self.config_file:
            config_path = Path(self.config_file)

            if not config_path.exists():
                return

            try:
                with open(config_path, "r") as f:
                    if config_path.suffix in [".yaml", ".yml"]:
                        file_config = yaml.safe_load(f)
                    elif config_path.suffix == ".json":
                        file_config = json.load(f)
                    else:
                        file_config = self._parse_rc_file(f)

                self._merge_config(file_config)
            except Exception as e:
                logger.warning(f"Failed to load config file {config_path}: {e}")

    def _auto_discover_config_file(self) -> None:
        """Auto-discover configuration file in current directory and parents."""
        search_paths = [
            Path.cwd() / ".employe-validatorrc",
            Path.cwd() / "config.yaml",
            Path.cwd() / "config.yml",
        ]

        for config_path in search_paths:
            if config_path.exists():
                self.config_file = str(config_path)
                return
        for parent in Path.cwd().parents:
            parent_config = parent / ".employe-validatorrc"
            if parent_config.exists():
                self.config_file = str(parent_config)
                return

    def _parse_rc_file(self, file) -> Dict[str, Any]:
        """Parse .rc-style configuration file.

        Format:
        KEY=VALUE
        KEY.SUBKEY=VALUE
        """
        config: Dict[str, Any] = {}
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip().lower()
                value = value.strip()

                if "." in key:
                    parts = key.split(".")
                    current = config
                    for part in parts[:-1]:
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                    current[parts[-1]] = self._parse_value(value)
                else:
                    config[key] = self._parse_value(value)

        return config

    def _parse_value(self, value: str) -> Any:
        """Parse string value to appropriate type."""
        value = value.strip()

        if value.lower() in ("true", "yes", "on"):
            return True
        elif value.lower() in ("false", "no", "off"):
            return False
        elif value.isdigit():
            return int(value)
        elif value.replace(".", "", 1).isdigit():
            return float(value)
        else:
            return value

    def _load_env_vars(self) -> None:
        """Load configuration from environment variables."""
        env_mappings: Dict[str, Union[str, Tuple[str, str]]] = {
            f"{self.env_prefix}PARALLEL": "parallel",
            f"{self.env_prefix}PRODUCTION": "production",
            f"{self.env_prefix}VERBOSE": "verbose",
            f"{self.env_prefix}QUIET": "quiet",
            f"{self.env_prefix}LOG_LEVEL": ("logging", "level"),
            f"{self.env_prefix}LOG_FORMAT": ("logging", "format"),
            f"{self.env_prefix}CACHE_ENABLED": ("cache", "enabled"),
            f"{self.env_prefix}CACHE_SIZE": ("cache", "size"),
            f"{self.env_prefix}CACHE_TTL": ("cache", "ttl"),
            f"{self.env_prefix}METRICS_ENABLED": ("metrics", "enabled"),
            f"{self.env_prefix}METRICS_FORMAT": ("metrics", "format"),
        }

        for env_var, config_key in env_mappings.items():
            value = os.environ.get(env_var)
            if value is not None:
                if isinstance(config_key, tuple):
                    parent_key, child_key = config_key
                    if parent_key not in self._config:
                        self._config[parent_key] = {}
                    self._config[parent_key][child_key] = self._parse_value(value)
                else:
                    config_key_str = cast(str, config_key)
                    self._config[config_key_str] = self._parse_value(value)

    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """Merge new configuration into existing config."""
        for key, value in new_config.items():
            if (
                key in self._config
                and isinstance(self._config[key], dict)
                and isinstance(value, dict)
            ):
                self._config[key].update(value)
            else:
                self._config[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.

        Args:
            key: Configuration key (supports dot notation for nested keys)
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        if "." in key:
            parts = key.split(".")
            current = self._config
            for part in parts[:-1]:
                if part not in current:
                    return default
                current = current[part]
            return current.get(parts[-1], default)

        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value.

        Args:
            key: Configuration key (supports dot notation for nested keys)
            value: Value to set
        """
        if isinstance(value, str):
            value = self._parse_value(value)

        if "." in key:
            parts = key.split(".")
            current = self._config
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
        else:
            self._config[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary."""
        return self._config.copy()


def load_config(
    config_file: Optional[str] = None, env_prefix: str = "EMPLOYEE_MD_"
) -> Config:
    """Load configuration.

    Args:
        config_file: Path to configuration file
        env_prefix: Prefix for environment variables

    Returns:
        Config instance
    """
    return Config(config_file, env_prefix)
