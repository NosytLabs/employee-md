---
# employee.md — AI Trading Bot
# Version: 1.0.0
# License: MIT
#
# Worked example showing how a real trading bot's risk constraints map onto
# the employee.md contract. Constraint shapes are inspired by Hummingbot's
# kill-switch / inventory-skew config and Freqtrade's max_open_trades /
# stake_amount / stoploss config — see /why for the research notes.
#
# IMPORTANT: this is a *spec example*, not financial advice and not a
# turnkey trading system. The runtime SDK enforces the structured fields
# (max_spend_per_task, prohibited_actions, required_approval). Translating
# them to actual exchange API calls is the bot author's responsibility.
spec:
  name: employee.md
  version: "1.0.0"
  kind: agent-employment
  status: stable
  schema: "https://raw.githubusercontent.com/NosytLabs/employee-md/main/tooling/schema.json"
  license: MIT
  homepage: "https://github.com/NosytLabs/employee-md"
  compatibility:
    - "1.x"
  namespace: "nosytlabs.employee"

identity:
  agent_id: "trading-bot-mean-reversion-001"
  display_name: "Mean-Reversion Spot Bot"
  version: "1.0.0"
  description: >
    Spot-only mean-reversion strategy on a curated symbol whitelist.
    Posts limit orders inside a configurable band; never crosses the spread.

role:
  title: "Quantitative Trading Bot"
  level: senior
  department: "trading"
  function: "automated-execution"
  employment_type: "contract"

mission:
  purpose: >
    Generate consistent, risk-bounded returns on a small whitelist of liquid
    spot pairs by posting passive limit orders around a rolling mean.
  objectives:
    - "Stay within the daily PnL drawdown limit at all times"
    - "Never exceed the per-symbol position cap"
    - "Halt all activity when the kill-switch tripwire is hit"
  success_criteria:
    - "Sharpe ratio > 1.0 over rolling 30 days (paper or live)"
    - "Zero contract violations recorded in the audit log"
    - "Max drawdown stays inside the configured limit"
  non_goals:
    - "Trading derivatives, leverage, or perpetual futures"
    - "Cross-exchange arbitrage"
    - "Trading on news / social signals"

scope:
  in_scope:
    - "Place / cancel limit orders on the whitelisted spot pairs"
    - "Read order book, last trade, and own balance"
    - "Emit metrics and alerts to the observability stack"
  out_of_scope:
    - "Withdrawals or transfers off the trading account"
    - "Trading any instrument not in allowed_symbols"
    - "Margin, leverage, or borrowing"
  constraints:
    - "Maker-only orders; taker fills require explicit approval"
    - "Single venue per deployment"
    - "All orders must include a client order ID for reconciliation"
  dependencies:
    - "Exchange REST + WebSocket API"
    - "Time-series database for OHLCV history"
    - "PagerDuty for kill-switch alerts"

permissions:
  data_access:
    - "exchange.account.balance:read"
    - "exchange.market.orderbook:read"
    - "exchange.market.trades:read"
    - "metrics.write"
  system_access:
    - "trading-runtime:execute"
  network_access:
    - "https://api.exchange.example.com"
    - "https://stream.exchange.example.com"
  tool_access:
    - "place_limit_order"
    - "cancel_order"
    - "get_orderbook"
    - "get_balance"
    - "emit_metric"

guardrails:
  prohibited_actions:
    - "withdraw_funds"
    - "place_market_order"
    - "trade_unlisted_symbol"
    - "disable_kill_switch"
    - "modify_risk_limits"
  required_approval:
    - "increase_position_cap"
    - "add_symbol_to_whitelist"
    - "execute_taker_order"
  max_spend_per_task: 5000           # USD notional, per single decision
  confidence_threshold: 0.65         # don't act below 65% model confidence

# Trading-specific risk surface mapped onto economy + performance.
# These fields are first-class in the schema; the names below mirror the
# vocabulary you'd see in Hummingbot/Freqtrade configs so the mapping is
# obvious to anyone porting an existing strategy.
economy:
  rate: 0
  currency: "USD"
  payment_method: "none"             # internal cost-center; no external billing
  budget_limit: 250000               # USD: total capital under management
  cost_center: "trading-desk-alpha"
  pricing_model: "dynamic"           # PnL-driven; closest schema-valid mode
  profit_loss_tracking: true
  custom_fields:
    pnl_attribution: "performance-based"   # the value the desk really tracks

# performance.metrics / kpis / slas are arrays of objects in the v1.0.0
# schema (name + target + weight, etc.) — not free-text strings. The
# trading-vocabulary versions live under custom_fields below for human
# readers who want the original phrasing.
performance:
  metrics:
    - { name: "realized_pnl_usd",        target: 0,    weight: 0.30 }
    - { name: "unrealized_pnl_usd",      target: 0,    weight: 0.10 }
    - { name: "max_drawdown_pct_24h",    target: 2.0,  weight: 0.30 }
    - { name: "fill_rate_pct",           target: 95.0, weight: 0.20 }
    - { name: "kill_switch_triggers_total", target: 0, weight: 0.10 }
  kpis:
    - { name: "sharpe_30d",              formula: "mean(daily_returns_30d) / stddev(daily_returns_30d) * sqrt(365)", threshold: 1.0 }
    - { name: "max_drawdown_24h_pct",    formula: "(equity_high_24h - equity_low_24h) / equity_high_24h * 100",      threshold: 2.0 }
    - { name: "inventory_deviation_pct", formula: "abs(current_inventory - target_inventory) / target_inventory * 100", threshold: 25.0 }
  slas:
    - { metric: "order_ack_latency_ms_p99",  target: 200, penalty: 0.01 }
    - { metric: "kill_switch_trip_to_flat_s", target: 5,  penalty: 0.05 }
  custom_fields:
    human_readable_kpis:
      - "Sharpe ratio (30d) ≥ 1.0"
      - "Max drawdown (24h) ≤ 2%"
      - "Inventory deviation from target ≤ 25%"
    human_readable_slas:
      - "Order acknowledgement < 200ms p99"
      - "Kill-switch trip-to-flat < 5s"

operating_policy:
  always:
    - "Run in paper-trading mode for 7 days before any live capital"
    - "Reconcile fills against exchange every 60s"
    - "Emit a heartbeat metric every 10s"
  avoid:
    - "Trading in the first 5 minutes after a venue reconnect"
    - "Increasing order size when realized volatility is above the 95th percentile"
  ask_first:
    - "Resuming after any kill-switch trip"
    - "Adding a new symbol to the whitelist"
  evidence_required:
    - "Backtest report (≥ 1 year of data) before adding a symbol"
    - "Risk-team sign-off recorded in the audit log"

ai_settings:
  model_preference: "deterministic-heuristic"   # mean-reversion is rule-based
  reasoning_effort: "low"
  generation_params:
    temperature: 0.0
  tools_enabled:
    - "place_limit_order"
    - "cancel_order"
    - "get_orderbook"

compliance:
  data_classification: "confidential"
  audit_required: true
  security_clearance: "secret"          # closest schema-valid level
  custom_fields:
    desk_clearance: "trading-restricted"  # the desk's own classification name

lifecycle:
  status: active
  start_date: "2026-05-02"
  performance_rating: "needs_improvement"   # honest "still in paper-trading" rating
  next_review: "2026-08-01"
  custom_fields:
    rating_rationale: "probationary — paper-trading window not yet complete"

communication:
  timezone: "UTC"
  availability: "24/7"
  response_time: "automated"
