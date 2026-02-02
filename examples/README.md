# Examples

This directory contains reference implementations of `employee.md` for various AI agent personas. Use these templates to jumpstart your agent configuration.

## 📂 Available Examples

### Core Templates

| File | Persona | Complexity | Key Features |
|------|---------|------------|--------------|
| **[minimal.md](minimal.md)** | Worker | ⭐ Minimal | Minimum valid spec. The "Hello World" of agent employment. |
| **[ai-assistant.md](ai-assistant.md)** | AI Assistant | ⭐⭐ Basic | Standard assistant with tools, memory, and personality. |
| **[senior-dev.md](senior-dev.md)** | Senior Developer | ⭐⭐⭐ Intermediate | Coding capabilities, high permissions, delegation, team collaboration. |

### Specialized Roles

| File | Persona | Complexity | Key Features |
|------|---------|------------|--------------|
| **[devops-engineer.md](devops-engineer.md)** | DevOps Engineer | ⭐⭐⭐⭐ Advanced | Infrastructure as Code, on-call rotation, high privileges, monitoring. |
| **[product-manager.md](product-manager.md)** | Product Manager | ⭐⭐⭐ Intermediate | Market analysis, stakeholder management, human-in-the-loop decisions. |
| **[data-analyst.md](data-analyst.md)** | Data Analyst | ⭐⭐⭐ Intermediate | Database connections, read-only permissions, reporting metrics. |
| **[security-auditor.md](security-auditor.md)** | Security Auditor | ⭐⭐⭐⭐ Advanced | SOC2 compliance, high security clearance, restricted access. |
| **[freelancer.md](freelancer.md)** | Freelancer | ⭐⭐⭐ Intermediate | Contract work, crypto payments (x402), milestone tracking. |

### Platform Integrations

| File | Platform | Purpose |
|------|----------|---------|
| **[molt-bot-integration.md](molt-bot-integration.md)** | Molt.bot | Integration with Molt.bot workspaces |
| **[zhc-worker.md](zhc-worker.md)** | ZHC | JouleWork pricing, energy accounting, P&L tracking |

## 🚀 Quick Start

### 1. Choose a Template

Select an example that closest matches your use case:

```bash
# For a general-purpose coding assistant
cp examples/senior-dev.md my-agent.md

# For infrastructure automation
cp examples/devops-engineer.md my-agent.md

# For product strategy
cp examples/product-manager.md my-agent.md
```

### 2. Customize

Edit the file to match your specific requirements:

```yaml
# Update identity
identity:
  agent_id: "my-unique-agent-001"
  display_name: "My Custom Agent"

# Adjust scope
scope:
  in_scope:
    - "Your specific tasks"
  
# Set permissions
permissions:
  data_access:
    - "your-resources"
```

### 3. Validate

Ensure your configuration is valid:

```bash
# Using the CLI
employee-validate my-agent.md

# Or using Python directly
python -m tooling.cli my-agent.md
```

## 📝 Example Categories

### By Complexity

**Beginner (Minimal Setup)**
- `minimal.md` - Start here for the basics

**Intermediate (Production Ready)**
- `ai-assistant.md` - General purpose assistant
- `senior-dev.md` - Software development
- `product-manager.md` - Product strategy

**Advanced (Enterprise)**
- `devops-engineer.md` - Infrastructure & operations
- `security-auditor.md` - Security & compliance

### By Use Case

**Software Development**
- `senior-dev.md` - Full-stack development
- `devops-engineer.md` - Infrastructure & CI/CD

**Business & Strategy**
- `product-manager.md` - Product strategy
- `data-analyst.md` - Data & analytics

**Security & Compliance**
- `security-auditor.md` - Security auditing

**Flexible Work**
- `freelancer.md` - Contract-based work

## 🎯 Feature Highlights by Example

### minimal.md
- ✅ Required fields only
- ✅ Quick validation
- ✅ Best for testing

### senior-dev.md
- ✅ Full development capabilities
- ✅ Code review workflow
- ✅ Team delegation
- ✅ CI/CD integration

### devops-engineer.md (NEW)
- ✅ Infrastructure as Code
- ✅ Kubernetes & Terraform
- ✅ 24/7 on-call support
- ✅ Multi-region deployment
- ✅ Security hardening

### product-manager.md (NEW)
- ✅ Market research
- ✅ Stakeholder management
- ✅ PRD documentation
- ✅ Data-driven decisions
- ✅ Human review workflows

### security-auditor.md
- ✅ Compliance frameworks (SOC2, ISO27001)
- ✅ Audit trails
- ✅ Restricted permissions
- ✅ Security scanning

### freelancer.md
- ✅ Crypto payments (x402)
- ✅ Milestone tracking
- ✅ Contract terms

## 🔧 Customization Tips

### 1. Start with Scope
Define what your agent should and shouldn't do:

```yaml
scope:
  in_scope:
    - "Specific tasks your agent handles"
  out_of_scope:
    - "Tasks that require human judgment"
```

### 2. Set Appropriate Guardrails
Always configure safety constraints:

```yaml
guardrails:
  prohibited_actions:
    - "anything-dangerous"
  confidence_threshold: 0.8
```

### 3. Configure Integrations
Add the tools your agent needs:

```yaml
integration:
  mcp_servers:
    - name: "your-tools"
      endpoint: "http://localhost:8080"
```

## 📚 Related Resources

- [Main Specification](../employee.md) - Full specification reference
- [Integration Guide](../INTEGRATION.md) - Framework integration details
- [Schema](../tooling/schema.json) - JSON Schema for validation

---

**Need a new example?** Open an issue to request additional personas or use cases!
