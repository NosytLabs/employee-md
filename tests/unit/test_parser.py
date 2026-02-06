"""Tests for SecureYAMLParser."""

import pytest
from pathlib import Path
import tempfile
import yaml

from tooling.parser import SecureYAMLParser, YAMLErrorContext


class TestSecureYAMLParser:
    """Tests for SecureYAMLParser class."""

    def test_parse_valid_yaml(self):
        parser = SecureYAMLParser()
        yaml_content = """
        spec:
          name: test
          version: 1.0
        """
        data, error_line = parser.parse_string(yaml_content)
        # YAML converts "1.0" to float 1.0
        assert data == {"spec": {"name": "test", "version": 1.0}}
        assert error_line is None

    def test_parse_file_success(self, tmp_path):
        parser = SecureYAMLParser(allowed_directories=[str(tmp_path)])
        test_file = tmp_path / "test.yaml"

        yaml_content = """
        role:
          title: Agent
          level: senior
        """
        test_file.write_text(yaml_content)

        data, error_line = parser.parse_file(str(test_file))
        assert data == {"role": {"title": "Agent", "level": "senior"}}
        assert error_line is None

    def test_parse_invalid_yaml(self):
        parser = SecureYAMLParser()
        yaml_content = """
        spec:
          name: test
          version: 1.0
          invalid: [
        """

        with pytest.raises(YAMLErrorContext) as exc_info:
            parser.parse_string(yaml_content)

        assert "YAML parsing error" in str(exc_info.value)

    def test_parse_non_existent_file(self):
        parser = SecureYAMLParser()

        with pytest.raises(YAMLErrorContext) as exc_info:
            parser.parse_file("nonexistent_file.yaml")

        assert "File not found" in str(exc_info.value)

    def test_parse_empty_yaml(self):
        parser = SecureYAMLParser()
        data, error_line = parser.parse_string("")
        assert data == {}
        assert error_line is None

    def test_parse_yaml_with_null(self):
        parser = SecureYAMLParser()
        yaml_content = """
        spec:
          name: null
        """
        data, error_line = parser.parse_string(yaml_content)
        assert data == {"spec": {"name": None}}
        assert error_line is None

    def test_parse_yaml_with_lists(self):
        parser = SecureYAMLParser()
        yaml_content = """
        permissions:
          data_access:
            - read
            - write
        """
        data, error_line = parser.parse_string(yaml_content)
        assert data == {"permissions": {"data_access": ["read", "write"]}}
        assert error_line is None

    def test_parse_yaml_with_nested_dicts(self):
        parser = SecureYAMLParser()
        yaml_content = """
        economy:
          wallets:
            outbound: wallet123
            inbound: wallet456
        """
        data, error_line = parser.parse_string(yaml_content)
        assert data == {
            "economy": {"wallets": {"outbound": "wallet123", "inbound": "wallet456"}}
        }
        assert error_line is None

    def test_file_size_limit(self):
        parser = SecureYAMLParser(max_size=100)
        yaml_content = "data: " + "x" * 200

        with pytest.raises(YAMLErrorContext) as exc_info:
            parser.parse_string(yaml_content)

        assert "too large" in str(exc_info.value).lower()

    def test_depth_limit(self):
        parser = SecureYAMLParser(max_depth=3)
        yaml_content = """
        a:
          b:
            c:
              d:
                e: deep
        """

        with pytest.raises(YAMLErrorContext) as exc_info:
            parser.parse_string(yaml_content)

        assert "too deep" in str(exc_info.value).lower()

    def test_depth_within_limit(self):
        parser = SecureYAMLParser(max_depth=5)
        yaml_content = """
        a:
          b:
            c:
              d: value
        """
        data, error_line = parser.parse_string(yaml_content)
        assert data == {"a": {"b": {"c": {"d": "value"}}}}
        assert error_line is None

    def test_calculate_depth_flat(self):
        parser = SecureYAMLParser()
        depth = parser._calculate_depth({"a": 1, "b": 2, "c": 3})
        assert depth == 1

    def test_calculate_depth_nested(self):
        parser = SecureYAMLParser()
        depth = parser._calculate_depth({"a": {"b": {"c": {"d": "value"}}}})
        assert depth == 4

    def test_calculate_depth_with_lists(self):
        parser = SecureYAMLParser()
        depth = parser._calculate_depth({"items": [{"nested": "value"}]})
        assert depth == 3

    def test_path_traversal_protection(self):
        # By default, only CWD is allowed
        parser = SecureYAMLParser()

        # Test absolute path to system file (should be denied)
        with pytest.raises(YAMLErrorContext) as exc_info:
            parser.parse_file("/etc/passwd")
        assert "Path traversal" in str(exc_info.value)

        # Test relative path traversal
        with pytest.raises(YAMLErrorContext) as exc_info:
            parser.parse_file("../../../etc/passwd")

        # Should raise either path traversal error or file not found
        assert "Path traversal" in str(exc_info.value)

    def test_is_safe_path_valid(self):
        parser = SecureYAMLParser()
        path = Path(__file__).resolve()
        assert parser._is_safe_path(path) is True

    def test_parse_root_list_raises_error(self):
        parser = SecureYAMLParser()
        yaml_content = """
        - item1
        - item2
        """

        with pytest.raises(YAMLErrorContext) as exc_info:
            parser.parse_string(yaml_content)

        assert "dictionary" in str(exc_info.value).lower()

    def test_extract_line_number_from_error(self):
        parser = SecureYAMLParser()

        yaml_content = """
        spec:
          name: test
          version: [invalid
        """

        try:
            parser.parse_string(yaml_content)
        except YAMLErrorContext as e:
            assert e.line_number is not None or "YAML parsing error" in str(e)

    def test_parse_unicode_content(self):
        parser = SecureYAMLParser()
        yaml_content = """
        role:
          title: Test Agent
          emoji: 🤖
        """
        data, error_line = parser.parse_string(yaml_content)
        assert data["role"]["emoji"] == "🤖"
        assert error_line is None

    def test_parse_special_characters(self):
        parser = SecureYAMLParser()
        yaml_content = """
        spec:
          name: "test-spec_v1.0"
        """
        data, error_line = parser.parse_string(yaml_content)
        assert data == {"spec": {"name": "test-spec_v1.0"}}
        assert error_line is None

    @pytest.fixture
    def tmp_path(self, tmp_path):
        return tmp_path
