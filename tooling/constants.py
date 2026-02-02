"""Constants for employee.md validation."""

VERSION = "2.1.0"

# Placeholder values that indicate a field is not yet filled
# All stored in lowercase for case-insensitive matching
PLACEHOLDER_VALUES = frozenset(
    {
        "tbd",
        "tba",
        "todo",
        "to be determined",
        "to be announced",
        "",
        # JSON Schema type placeholders
        "string",
        "number",
        "boolean",
        "object",
        "array",
        "list",
        "dict",
        "integer",
    }
)

LEVEL_ENUM = frozenset({"junior", "mid", "senior", "lead"})
STATUS_ENUM = frozenset({"onboarding", "active", "suspended", "terminated"})
SPEC_STATUS_ENUM = frozenset({"draft", "stable", "deprecated"})

VALIDATION_RULES = {
    "spec": {
        "name": str,
        "version": str,
        "kind": str,
        "status": str,
        "schema": str,
        "license": str,
        "homepage": str,
        "namespace": str,
        "compatibility": list,
        "supersedes": list,
        "extends": list,
    },
    "identity": {
        "agent_id": str,
        "version": str,
        "wallet": str,
        "created_at": str,
        "updated_at": str,
    },
    "role": {
        "title": str,
        "level": str,
        "department": str,
        "work_location": str,
        "employment_type": str,
    },
    "mission": {
        "purpose": str,
        "objectives": list,
        "success_criteria": list,
        "non_goals": list,
    },
    "scope": {
        "in_scope": list,
        "out_of_scope": list,
        "dependencies": list,
        "constraints": list,
    },
    "permissions": {
        "data_access": list,
        "system_access": list,
        "network_access": list,
        "tool_access": list,
    },
    "verification": {
        "required_checks": list,
        "evidence": list,
        "review_policy": str,
    },
    "operating_policy": {
        "always": list,
        "avoid": list,
        "ask_first": list,
        "evidence_required": list,
    },
    "workflows": {
        "intake": list,
        "execution": list,
        "review": list,
        "handoff": list,
    },
    "outputs": {
        "deliverables": list,
        "artifacts": list,
        "reporting": list,
    },
    "economy": {
        "rate": (int, float),
        "currency": str,
        "payment_method": str,
        "billing_schedule": str,
        "budget_limit": (int, float),
        "cost_center": str,
        "model": str,
        "pricing_model": str,
        "energy_accounting": bool,
        "profit_loss_tracking": bool,
        "insolvency_policy": str,
        "wallets": dict,
        "internal_token": str,
        "deductions": dict,
    },
    "delegation": {
        "max_tasks": (int, float),
        "protocol": str,
        "task_timeout": (int, float),
        "sub_delegation": bool,
    },
    "lifecycle": {
        "status": str,
        "start_date": str,
        "end_date": str,
        "probation_end": str,
        "performance_rating": str,
        "next_review": str,
    },
    "compliance": {
        "data_classification": str,
        "audit_required": bool,
        "security_clearance": str,
    },
    "communication": {
        "timezone": str,
        "availability": str,
        "response_time": str,
    },
    "guardrails": {
        "prohibited_actions": list,
        "required_approval": list,
        "max_spend_per_task": (int, float),
        "confidence_threshold": (int, float),
    },
    "ai_settings": {
        "model_preference": str,
        "token_limits": dict,
        "generation_params": dict,
        "tools_enabled": list,
        "memory_settings": dict,
        "reasoning_effort": str,
    },
    "knowledge_base": {
        "documentation_urls": list,
        "training_data": dict,
        "faq_links": list,
        "best_practices": list,
        "version_control": str,
    },
    "integration": {
        "apis": list,
        "webhooks": list,
        "services": list,
        "mcp_servers": list,
    },
    "performance": {
        "efficiency_score": (int, float),
        "thermodynamic_efficiency": (int, float),
        "profit_margin": (int, float),
        "metrics": list,
        "kpis": list,
        "slas": list,
        "benchmarks": list,
    },
    "protocols": {
        "a2a": dict,
        "x402": dict,
        "human_review": dict,
        "delegation": dict,
    },
}

REQUIRED_SECTIONS = frozenset({"role", "lifecycle"})
REQUIRED_FIELDS = {
    "role": frozenset({"title", "level"}),
    "lifecycle": frozenset({"status"}),
}

RANGE_CONSTRAINTS = {
    "guardrails.confidence_threshold": (0.0, 1.0),
    "ai_settings.generation_params.temperature": (0.0, 1.0),
    "ai_settings.generation_params.top_p": (0.0, 1.0),
    "ai_settings.generation_params.frequency_penalty": (-2.0, 2.0),
    "ai_settings.generation_params.presence_penalty": (-2.0, 2.0),
}

MAX_YAML_DEPTH = 50
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

DEFAULT_CACHE_MAX_SIZE = 100
DEFAULT_CACHE_TTL = 300  # 5 minutes in seconds

# LRU cache sizes for utility functions
ISO_DATE_CACHE_SIZE = 1024
URL_CACHE_SIZE = 1024
EMAIL_CACHE_SIZE = 1024

# LRU cache size for ThreadPoolExecutor
DEFAULT_MAX_WORKERS = 5

# Parallel processing limits
MAX_PARALLEL_WORKERS = 10

# ThreadPoolExecutor timeout in seconds
DEFAULT_TIMEOUT = 30

# Performance regression thresholds
REGRESSION_THRESHOLD = 50.0
REGRESSION_THRESHOLD_PER_FILE = 30.0
REGRESSION_THRESHOLD_PER_VALIDATION = 1.0
REGRESSION_THRESHOLD_THROUGHPUT = 50.0
