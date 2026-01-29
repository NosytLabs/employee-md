#!/usr/bin/env python3
"""
Employee.md Validator
Validates employee.md YAML configuration files.
"""

import sys
import yaml
from datetime import datetime
from typing import Dict, List, Any
import json
import re

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_wallet(wallet: str) -> bool:
    """Validate crypto wallet address format."""
    if wallet.startswith('0x'):
        return len(wallet) == 42 and all(c in '0123456789abcdefABCDEF' for c in wallet[2:])
    return False

def validate_iso_date(date_str: str) -> bool:
    """Validate ISO 8601 date format."""
    try:
        datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return True
    except ValueError:
        return False

def validate_url(url: str) -> bool:
    """Validate URL format."""
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return re.match(pattern, url) is not None

PLACEHOLDER_VALUES = {"string", "number", "boolean", "object", "array", "list", "dict"}

def is_placeholder(value: Any) -> bool:
    return isinstance(value, str) and value.strip().lower() in PLACEHOLDER_VALUES

class EmployeeValidator:
    """Validator for employee.md configuration files."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_required_fields(self):
        """Validate required fields are present."""
        if 'role' not in self.config:
            self.errors.append("Missing required section: 'role'")
        else:
            if 'title' not in self.config['role']:
                self.errors.append("Missing required field: 'role.title'")
            if 'level' not in self.config['role']:
                self.errors.append("Missing required field: 'role.level'")

        if 'lifecycle' not in self.config:
            self.errors.append("Missing required section: 'lifecycle'")
        else:
            if 'status' not in self.config['lifecycle']:
                self.errors.append("Missing required field: 'lifecycle.status'")

    def validate_enums(self):
        """Validate enum values."""
        level_enum = ['junior', 'mid', 'senior', 'lead']
        if 'role' in self.config and 'level' in self.config['role']:
            if not is_placeholder(self.config['role']['level']) and self.config['role']['level'] not in level_enum:
                self.errors.append(f"Invalid role.level: {self.config['role']['level']}. Must be one of: {level_enum}")

        status_enum = ['onboarding', 'active', 'suspended', 'terminated']
        if 'lifecycle' in self.config and 'status' in self.config['lifecycle']:
            if not is_placeholder(self.config['lifecycle']['status']) and self.config['lifecycle']['status'] not in status_enum:
                self.errors.append(f"Invalid lifecycle.status: {self.config['lifecycle']['status']}. Must be one of: {status_enum}")

        spec_status_enum = ['draft', 'stable', 'deprecated']
        if 'spec' in self.config and 'status' in self.config['spec']:
            if not is_placeholder(self.config['spec']['status']) and self.config['spec']['status'] not in spec_status_enum:
                self.errors.append(f"Invalid spec.status: {self.config['spec']['status']}. Must be one of: {spec_status_enum}")

    def validate_types(self):
        """Validate field types."""
        type_rules = {
            'spec': {
                'name': str,
                'version': str,
                'kind': str,
                'status': str,
                'schema': str,
                'license': str,
                'homepage': str,
                'namespace': str,
                'compatibility': list,
                'supersedes': list,
                'extends': list,
            },
            'identity': {
                'agent_id': str,
                'version': str,
                'wallet': str,
                'created_at': str,
                'updated_at': str,
            },
            'role': {
                'title': str,
                'level': str,
                'department': str,
                'work_location': str,
                'employment_type': str,
            },
            'mission': {
                'purpose': str,
                'objectives': list,
                'success_criteria': list,
                'non_goals': list,
            },
            'scope': {
                'in_scope': list,
                'out_of_scope': list,
                'dependencies': list,
                'constraints': list,
            },
            'permissions': {
                'data_access': list,
                'system_access': list,
                'network_access': list,
                'tool_access': list,
            },
            'verification': {
                'required_checks': list,
                'evidence': list,
                'review_policy': str,
            },
            'principles': list,
            'operating_policy': dict,
            'workflows': dict,
            'outputs': dict,
            'economy': {
                'rate': (int, float),
                'currency': str,
                'payment_method': str,
                'billing_schedule': str,
                'budget_limit': (int, float),
                'cost_center': str,
            },
            'delegation': {
                'max_tasks': (int, float),
                'protocol': str,
                'task_timeout': (int, float),
                'sub_delegation': bool,
            },
            'lifecycle': {
                'status': str,
                'start_date': str,
                'end_date': str,
                'probation_end': str,
                'performance_rating': str,
                'next_review': str,
            },
            'compliance': {
                'data_classification': str,
                'audit_required': bool,
                'security_clearance': str,
            },
            'communication': {
                'timezone': str,
                'availability': str,
                'response_time': str,
            },
            'guardrails': {
                'max_spend_per_task': (int, float),
                'confidence_threshold': (int, float),
            },
            'ai_settings': {
                'model_preference': str,
                'token_limits': dict,
                'generation_params': dict,
                'tools_enabled': list,
                'memory_settings': dict,
                'reasoning_effort': str,
            },
            'knowledge_base': {
                'documentation_urls': list,
                'training_data': dict,
                'faq_links': list,
                'best_practices': list,
                'version_control': str,
            },
            'integration': {
                'apis': list,
                'webhooks': list,
                'services': list,
                'mcp_servers': list,
            },
            'performance': {
                'metrics': list,
                'kpis': list,
                'slas': list,
                'benchmarks': list,
            },
        }

        for section, fields in type_rules.items():
            if section in self.config:
                if isinstance(fields, dict):
                    for field, expected_type in fields.items():
                        if field in self.config[section]:
                            value = self.config[section][field]
                            if is_placeholder(value):
                                continue
                            if not isinstance(value, expected_type):
                                self.errors.append(
                                    f"Invalid type for {section}.{field}: "
                                    f"expected {expected_type}, got {type(value)}"
                                )
                else:
                    value = self.config[section]
                    if not is_placeholder(value) and not isinstance(value, fields):
                        self.errors.append(
                            f"Invalid type for {section}: expected {fields}, got {type(value)}"
                        )

    def validate_formats(self):
        """Validate field formats."""
        if 'identity' in self.config:
            if 'wallet' in self.config['identity'] and self.config['identity']['wallet']:
                if not is_placeholder(self.config['identity']['wallet']) and not validate_wallet(self.config['identity']['wallet']):
                    self.errors.append("Invalid wallet address format")
            if 'created_at' in self.config['identity'] and self.config['identity']['created_at']:
                if not is_placeholder(self.config['identity']['created_at']) and not validate_iso_date(self.config['identity']['created_at']):
                    self.errors.append("Invalid created_at format (must be ISO 8601)")

        if 'lifecycle' in self.config:
            for date_field in ['start_date', 'end_date', 'probation_end', 'next_review']:
                if date_field in self.config['lifecycle'] and self.config['lifecycle'][date_field]:
                    if not is_placeholder(self.config['lifecycle'][date_field]) and not validate_iso_date(self.config['lifecycle'][date_field]):
                        self.errors.append(f"Invalid lifecycle.{date_field} format (must be ISO 8601)")

        if 'knowledge_base' in self.config:
            if 'documentation_urls' in self.config['knowledge_base']:
                for url in self.config['knowledge_base']['documentation_urls']:
                    if not is_placeholder(url) and not validate_url(url):
                        self.errors.append(f"Invalid URL in knowledge_base.documentation_urls: {url}")

        if 'spec' in self.config:
            if 'schema' in self.config['spec'] and self.config['spec']['schema']:
                if not is_placeholder(self.config['spec']['schema']) and not validate_url(self.config['spec']['schema']):
                    self.errors.append("Invalid spec.schema format (must be URL)")
            if 'homepage' in self.config['spec'] and self.config['spec']['homepage']:
                if not is_placeholder(self.config['spec']['homepage']) and not validate_url(self.config['spec']['homepage']):
                    self.errors.append("Invalid spec.homepage format (must be URL)")

    def validate_ranges(self):
        """Validate numeric ranges."""
        if 'guardrails' in self.config:
            if 'confidence_threshold' in self.config['guardrails']:
                threshold = self.config['guardrails']['confidence_threshold']
                if isinstance(threshold, (int, float)) and not 0.0 <= threshold <= 1.0:
                    self.errors.append(f"Invalid confidence_threshold: {threshold}. Must be between 0.0 and 1.0")

        if 'ai_settings' in self.config:
            if 'generation_params' in self.config['ai_settings']:
                for param in ['temperature', 'top_p', 'frequency_penalty', 'presence_penalty']:
                    if param in self.config['ai_settings']['generation_params']:
                        value = self.config['ai_settings']['generation_params'][param]
                        if isinstance(value, (int, float)) and param in ['temperature', 'top_p']:
                            if not 0.0 <= value <= 1.0:
                                self.errors.append(f"Invalid ai_settings.generation_params.{param}: {value}. Must be between 0.0 and 1.0")
                        elif isinstance(value, (int, float)) and param in ['frequency_penalty', 'presence_penalty']:
                            if not -2.0 <= value <= 2.0:
                                self.errors.append(f"Invalid ai_settings.generation_params.{param}: {value}. Must be between -2.0 and 2.0")

    def validate(self) -> bool:
        """Run all validations."""
        self.validate_required_fields()
        self.validate_enums()
        self.validate_types()
        self.validate_formats()
        self.validate_ranges()
        return len(self.errors) == 0

    def print_report(self):
        """Print validation report."""
        if self.errors:
            print("❌ Validation failed!")
            for error in self.errors:
                print(f"  ✗ {error}")
        else:
            print("✓ Validation passed!")

        if self.warnings:
            print("\n⚠ Warnings:")
            for warning in self.warnings:
                print(f"  ⚠ {warning}")

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python validate.py <employee.md file>")
        sys.exit(1)

    filename = sys.argv[1]

    try:
        with open(filename, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"❌ YAML parsing error: {e}")
        sys.exit(1)

    validator = EmployeeValidator(config)
    if validator.validate():
        validator.print_report()
        sys.exit(0)
    else:
        validator.print_report()
        sys.exit(1)

if __name__ == '__main__':
    main()
