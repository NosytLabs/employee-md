---
spec:
  name: employee.md
  version: "1.0"
  kind: agent-employment
  status: string
  schema: string
  license: string
  homepage: string

identity:
  agent_id: string           # Unique identifier (required)
  version: string           # Config version (e.g., "1.0")
  wallet: string            # Crypto wallet address (optional)
  created_at: string        # ISO date (optional)
  updated_at: string        # ISO date (optional)

role:
  title: string             # Job title (required)
  level: string              # junior | mid | senior | lead (required)
  department: string         # Team/department (optional)
  capabilities:             # List of skills (optional)
    - string
  skills:                   # Detailed skills with levels (optional)
    - name: string
      level: number
  work_location: string       # remote | office | hybrid (optional)
  employment_type: string    # full_time | part_time | contract (optional)

economy:
  rate: number              # Hourly/project rate (optional)
  currency: string          # USD | EUR | BTC | ETH (default: USD)
  payment_method: string     # x402 | crypto | fiat | none (optional)
  billing_schedule: string   # weekly | monthly | milestone (optional)
  budget_limit: number       # Monthly spend limit (optional)
  cost_center: string        # Department code (optional)

delegation:
  max_tasks: number         # Concurrent task limit (default: 5)
  protocol: string          # A2A | human_review | auto (default: auto)
  task_timeout: number      # Seconds before timeout (default: 3600)
  sub_delegation: boolean   # Allow delegating to other agents (default: false)
  escalation_path:          # List of agent IDs to escalate to (optional)
    - string

lifecycle:
  status: string            # onboarding | active | suspended | terminated (required)
  start_date: string        # ISO date (optional)
  end_date: string          # ISO date (optional)
  probation_end: string     # ISO date (optional)
  performance_rating: string # exceeds | meets | needs_improvement (optional)
  next_review: string        # ISO date (optional)

compliance:
  frameworks:               # SOC2, GDPR, HIPAA, etc. (optional)
    - string
  data_classification: string  # public | confidential | restricted (optional)
  audit_required: boolean    # Enable logging for compliance (default: false)
  security_clearance: string  # none | basic | secret | top_secret (default: none)

communication:
  channels:                # Slack, Email, Discord, etc. (optional)
    - string
  timezone: string           # IANA timezone (default: UTC)
  availability: string        # 9:00-18:00 UTC or "24/7" (optional)
  response_time: string      # Expected response time (optional)

guardrails:
  prohibited_actions:        # Actions agent must never take (optional)
    - string
  required_approval:        # Actions requiring human approval (optional)
    - string
  max_spend_per_task: number # Per-task spending limit (optional)
  confidence_threshold: number  # Min confidence to act (0.0-1.0, optional)

ai_settings:
  model_preference: string   # gpt-4, claude-3, llama-3, etc. (optional)
  token_limits:
    input: number           # Max input tokens (default: 128000)
    output: number          # Max output tokens (default: 4096)
    context: number         # Context window size (default: 200000)
  generation_params:
    temperature: number     # 0.0-1.0 (default: 0.7)
    top_p: number          # 0.0-1.0 (default: 1.0)
    frequency_penalty: number # -2.0-2.0 (default: 0.0)
    presence_penalty: number  # -2.0-2.0 (default: 0.0)
  tools_enabled:           # function_calling, code_execution, web_browsing (optional)
    - string
  memory_settings:
    context_retention: string  # conversation | session | persistent (default: conversation)
    max_history: number    # Max conversation turns to remember (default: 10)
    vector_store: boolean  # Enable vector-based memory (default: false)
  reasoning_effort: string  # low | medium | high (default: medium)

knowledge_base:
  documentation_urls:      # Internal documentation URLs (optional)
    - string
  training_data:
    sources:              # Data sources (s3, database, api) (optional)
      - string
    corpora:              # Training corpus names (optional)
      - string
    datasets:             # Dataset identifiers (optional)
      - string
  faq_links:               # FAQ or help documentation (optional)
    - string
  best_practices:          # Best practice guidelines (optional)
    - string
  version_control: string  # vcs_url for knowledge sync (optional)

integration:
  apis:                    # External API integrations (optional)
    - name: string
      endpoint: string
      auth_type: string    # api_key | oauth | jwt
      rate_limit: number
  webhooks:                # Webhook endpoints for events (optional)
    - event: string
      url: string
      method: string       # POST | PUT | PATCH
  services:                # Connected services (optional)
    - name: string
      type: string        # database | storage | queue | cache
      connection_string: string
  mcp_servers:             # MCP server connections (optional)
    - name: string
      endpoint: string
      capabilities:
        - string

performance:
  metrics:                # Performance metrics to track (optional)
    - name: string        # accuracy, speed, satisfaction, etc.
      target: number      # Target value
      weight: number      # Importance weight (0.0-1.0)
  kpis:                   # Key Performance Indicators (optional)
    - name: string
      formula: string     # Calculation formula
      threshold: number   # Threshold for alert
  slas:                   # Service Level Agreements (optional)
    - metric: string
      target: number
      penalty: number     # SLA breach penalty
  benchmarks:             # Test benchmarks (optional)
    - name: string
      dataset: string
      score: number

protocols:
  a2a:
    enabled: boolean       # Enable agent-to-agent communication (default: false)
    discovery_method: string # broadcast | registry | direct (default: broadcast)
    message_format: string  # json | yaml | protobuf (default: json)
    encryption: boolean    # Enable message encryption (default: true)
  x402:
    enabled: boolean       # Enable x402 payment protocol (default: false)
    wallet_address: string # Crypto wallet for payments (optional)
    settlement: string   # instant | net30 | net60 (default: instant)
    escrow: boolean      # Use escrow for transactions (default: true)
  human_review:
    enabled: boolean       # Enable human review workflow (default: false)
    review_triggers:      # Actions requiring review (optional)
      - string
    approval_timeout: number # Seconds before auto-reject (default: 86400)
    escalation_contacts:  # Human contacts for escalation (optional)
      - string
  delegation:
    enabled: boolean       # Enable task delegation (default: true)
    delegation_chain:      # Allowed delegation targets (optional)
      - string
    task_tracking: boolean # Track delegated tasks (default: true)
    notification: string   # slack | email | none (default: slack)

custom_fields: {}           # Any additional data (optional)
