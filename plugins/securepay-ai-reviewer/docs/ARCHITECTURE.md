# Architecture

## Product thesis

SecurePay AI Reviewer is a financial AI senior reviewer for KakaoPay-style services.

It is intentionally not a complex AI system:

```text
Codex Skill
  -> local Python Rule Engine
  -> Markdown/JSON report
  -> LLM senior-review guidance
  -> Auto Fix Plan
```

The plugin focuses on explainability and 30-second demo value.

## Why Codex Plugin

Codex can inspect files, run local commands, reason over diffs, and propose patches. A plugin packages this workflow so every developer can invoke the same financial review rubric instead of copying prompts manually.

## Modules

```text
src/
  .codex-plugin/plugin.json
  skills/securepay-reviewer/SKILL.md
  scripts/securepay_review.py
  scripts/securepay_ai_reviewer/
    __init__.py
    engine.py
  samples/
    payment-service/
    payment-agent/
```

## Data flow

```text
Input:
  target path
  review category

Scan:
  enumerate supported files
  apply deterministic financial rules
  add project-level test/readme findings

Score:
  Risk
  Security
  Quality
  Deployment
  Trust

Output:
  Markdown for humans
  JSON for automation
  exit code for CI threshold
```

## Rule groups

- Privacy
- Financial security
- JWT/OAuth/authz
- Logging
- SQL injection/XSS
- Hard-coded secret
- API breaking change
- Performance
- Architecture
- Error handling
- Transaction
- Concurrency
- Retry/timeout
- Unit/integration tests
- README/runbook
- Prompt safety
- AI Agent/payment-tool safety

## PayAgent Safety Harness

To avoid being a simple code-review tool, the plugin includes payment AI Agent checks:

- Tool over-authorization
- Missing confirmation before approve/cancel/refund
- Prompt instruction that skips confirmation
- Missing audit evidence for sensitive payment action
- Untrusted user content mixed into system/developer prompt
- Sensitive payment data in logs

This is based on KakaoPay public material about payment Open API MCP Agent Toolkit and SDD/agentic-coding constraints.

## Auto Fix policy

The plugin never silently changes financial code.

Auto Fix means:

1. generate a finding-specific fix plan
2. ask Codex to prepare a patch
3. require explicit user approval
4. rerun scanner/tests

## Exit codes

- `0`: completed and threshold passed
- `1`: invalid target/runtime error
- `2`: completed but Trust Score below `--fail-under`
