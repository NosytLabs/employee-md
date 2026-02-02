"""Integration tests for configuration management."""

import os
import tempfile
import yaml
from pathlib import Path

from tooling.config import Config, load_config


class TestConfig:
    """Test configuration loading and management."""

    def test_default_config(self):
        """Test default configuration values."""
        config = Config()

        assert config.get("parallel") == False
        assert config.get("production") == False
        assert config.get("verbose") == False
        assert config.get("quiet") == False
        assert config.get("cache.enabled") == True
        assert config.get("cache.size") == 100
        assert config.get("cache.ttl") == 300
        assert config.get("logging.level") == "INFO"
        assert config.get("logging.format") == "text"
        assert config.get("metrics.enabled") == False
        assert config.get("metrics.format") == "prometheus"

    def test_load_yaml_config(self):
        """Test loading configuration from YAML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(
                {
                    "parallel": True,
                    "cache": {"enabled": False, "size": 200},
                    "logging": {"level": "DEBUG"},
                },
                f,
            )
            config_path = f.name

        try:
            config = Config(config_file=config_path)

            assert config.get("parallel") == True
            assert config.get("cache.enabled") == False
            assert config.get("cache.size") == 200
            assert config.get("logging.level") == "DEBUG"
        finally:
            os.unlink(config_path)

    def test_load_json_config(self):
        """Test loading configuration from JSON file."""
        import json

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(
                {"parallel": True, "production": True, "cache": {"enabled": False}}, f
            )
            config_path = f.name

        try:
            config = Config(config_file=config_path)

            assert config.get("parallel") == True
            assert config.get("production") == True
            assert config.get("cache.enabled") == False
        finally:
            os.unlink(config_path)

    def test_load_rc_config(self):
        """Test loading .rc-style configuration file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".rc", delete=False) as f:
            f.write("parallel=true\n")
            f.write("cache.enabled=false\n")
            f.write("cache.size=200\n")
            f.write("logging.level=DEBUG\n")
            config_path = f.name

        try:
            config = Config(config_file=config_path)

            assert config.get("parallel") == True
            assert config.get("cache.enabled") == False
            assert config.get("cache.size") == 200
            assert config.get("logging.level") == "DEBUG"
        finally:
            os.unlink(config_path)

    def test_env_vars_override_config(self):
        """Test environment variables override config file."""
        os.environ["EMPLOYEE_MD_PARALLEL"] = "true"
        os.environ["EMPLOYEE_MD_CACHE_ENABLED"] = "false"

        try:
            config = Config()

            assert config.get("parallel") == True
            assert config.get("cache.enabled") == False
        finally:
            del os.environ["EMPLOYEE_MD_PARALLEL"]
            del os.environ["EMPLOYEE_MD_CACHE_ENABLED"]

    def test_env_vars_override_file_config(self):
        """Test environment variables override file config."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump({"parallel": False}, f)
            config_path = f.name

        os.environ["EMPLOYEE_MD_PARALLEL"] = "true"

        try:
            config = Config(config_file=config_path)

            assert config.get("parallel") == True
        finally:
            os.unlink(config_path)
            del os.environ["EMPLOYEE_MD_PARALLEL"]

    def test_get_nested_config(self):
        """Test getting nested configuration values."""
        config = Config()

        assert config.get("cache.enabled") == True
        assert config.get("cache.size") == 100
        assert config.get("logging.level") == "INFO"
        assert config.get("metrics.format") == "prometheus"

    def test_set_config(self):
        """Test setting configuration values."""
        config = Config()

        config.set("parallel", True)
        assert config.get("parallel") == True

        config.set("cache.size", 200)
        assert config.get("cache.size") == 200

        config.set("cache.enabled", False)
        assert config.get("cache.enabled") == False

    def test_set_nested_config(self):
        """Test setting nested configuration values."""
        config = Config()

        config.set("cache.size", 200)
        assert config.get("cache.size") == 200

        config.set("logging.level", "DEBUG")
        assert config.get("logging.level") == "DEBUG"

    def test_get_default_value(self):
        """Test getting default value for non-existent key."""
        config = Config()

        assert config.get("nonexistent.key") == None
        assert config.get("nonexistent.key", "default") == "default"

    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = Config()

        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert "parallel" in config_dict
        assert "cache" in config_dict
        assert "logging" in config_dict
        assert "metrics" in config_dict

    def test_config_auto_discovery(self):
        """Test auto-discovery of config file."""
        config = Config()

        config.set("parallel", True)
        assert config.get("parallel") == True

    def test_parse_value_boolean(self):
        """Test parsing boolean values."""
        config = Config()

        config.set("test_true", "true")
        assert config.get("test_true") == True

        config.set("test_yes", "yes")
        assert config.get("test_yes") == True

        config.set("test_on", "on")
        assert config.get("test_on") == True

        config.set("test_false", "false")
        assert config.get("test_false") == False

        config.set("test_no", "no")
        assert config.get("test_no") == False

        config.set("test_off", "off")
        assert config.get("test_off") == False

    def test_parse_value_numeric(self):
        """Test parsing numeric values."""
        config = Config()

        config.set("test_int", "123")
        assert config.get("test_int") == 123

        config.set("test_float", "123.456")
        assert config.get("test_float") == 123.456

    def test_merge_config(self):
        """Test merging configuration from multiple sources."""
        config = Config()

        assert config.get("cache.size") == 100
        assert config.get("logging.level") == "INFO"

        config._merge_config({"cache": {"size": 200}})
        assert config.get("cache.size") == 200
        assert config.get("cache.enabled") == True

        config._merge_config({"logging": {"level": "DEBUG", "format": "json"}})
        assert config.get("logging.level") == "DEBUG"
        assert config.get("logging.format") == "json"

    def test_load_config_function(self):
        """Test load_config convenience function."""
        config = load_config()

        assert isinstance(config, Config)
        assert config.get("parallel") == False
        assert config.get("production") == False

    def test_load_config_with_file(self):
        """Test load_config with custom file path."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump({"parallel": True}, f)
            config_path = f.name

        try:
            config = load_config(config_file=config_path)

            assert config.get("parallel") == True
        finally:
            os.unlink(config_path)

    def test_load_config_with_env_prefix(self):
        """Test load_config with custom env prefix."""
        os.environ["CUSTOM_PREFIX_PARALLEL"] = "true"

        try:
            config = load_config(env_prefix="CUSTOM_PREFIX_")

            assert config.get("parallel") == True
        finally:
            del os.environ["CUSTOM_PREFIX_PARALLEL"]
