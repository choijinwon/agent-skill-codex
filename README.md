# SecurePay AI Reviewer

Financial AI Code Review Copilot for KakaoPay-style financial engineering.

SecurePay AI Reviewer is a Codex Plugin that reviews financial-service code like an AI senior engineer. It is not a generic chatbot, OCR tool, simple linter, or simple code-review summarizer. It combines:

```text
Codex Skill prompts + local Python Rule Engine + LLM senior-review reasoning
```

The MVP is intentionally simple and auditable. It can run locally in 30 seconds and produce a scorecard, merge-risk findings, missing tests, and concrete auto-fix suggestions.

## 30-second demo

From `submission.zip`, unzip and run:

```bash
cd src
python3 scripts/securepay_review.py samples/payment-service --category payment
python3 scripts/securepay_review.py samples/payment-agent --category payagent
```

Expected output:

- Risk Score
- Security Score
- Quality Score
- Deployment Score
- Trust Score
- Must-fix findings
- Auto Fix Plan

## What, who, when

What:

- A Codex Plugin that reviews payment, privacy, API, test, performance, operation, prompt, and AI Agent safety risks before a financial-service change is merged.

Who:

- KakaoPay backend engineers
- payment/API platform engineers
- AI Agent/MCP developers
- security/privacy reviewers
- engineering leads who need consistent pre-merge risk signals

When:

- Before merging payment or financial-service code
- Before changing payment API behavior
- Before deploying an AI Agent that can call payment tools
- Before adding prompts that contain user, ticket, log, or payment context

## Why this problem

This idea is grounded only in KakaoPay public material.

1. KakaoPay is a broad financial platform, not a single payment button. Its official brand page lists remittance, payment, membership, asset management, bills, investment, loan, insurance, and recommended financial products. Code review for this environment must cover money movement, user data, API behavior, and operations.

2. KakaoPay publicly emphasizes privacy and information security. Its ESG/security page describes CPO/CIAP responsibility, Privacy by Design, CISO-led governance, policy/regulation compliance, 24/7 SOC operation, vulnerability analysis, incident response, ISMS-P, ISO/IEC 27001/27017, and PCI DSS. A financial code-review plugin should turn those values into repeatable engineering checks.

3. KakaoPay's AI Agent/MCP public material shows payment Open API integration with AI agents, including payment link creation, payment status lookup, cancel flows, AI SDK integration, and future plans for AI-agent-specific payment flows. When AI can call payment tools, review must include prompt injection, tool permission, confirmation, audit evidence, and sensitive-data minimization.

4. KakaoPay's SDD public material explains that agentic coding improves productivity but can create uncontrolled code generation and hallucination, and that developers increasingly verify specs and design tests. SecurePay AI Reviewer operationalizes this shift inside Codex.

5. KakaoPay's PR/AI review public material explains that AI-generated code increases review pressure, large PRs become hard to understand, and AI can scan structural issues before human reviewers focus on business decisions. SecurePay AI Reviewer is exactly that: an AI first-pass senior reviewer for financial engineering risks.

Sources:

- KakaoPay brand page: https://www.kakaopay.com/brand
- KakaoPay ESG/security page: https://www.kakaopay.com/esg/social/information_security
- KakaoPay privacy policy: https://www.kakaopay.com/terms/privacy
- KakaoPay Tech Blog, PR review in the AI era: https://tech.kakaopay.com/post/kakaopayins-slow-pr-fast-dev/
- KakaoPay Tech Blog, SDD agentic coding: https://tech.kakaopay.com/post/ifkakao-agentic-coding/
- KakaoPay Tech Blog, payment Open API MCP Agent Toolkit: https://tech.kakaopay.com/post/kakaopay-mcp-agent-toolkit/
- KakaoPay Tech Blog, Pink Ward incident visibility/automation: https://tech.kakaopay.com/post/pink-ward/

## Why it is different from ordinary AI review

Ordinary AI review often asks, "Is this code okay?"

SecurePay AI Reviewer asks, "Can KakaoPay safely ship this financial change tomorrow?"

Key differences:

- It scores financial release risk, not only code style.
- It treats payment idempotency, transaction boundaries, retry, timeout, and audit evidence as first-class review items.
- It reviews AI Agent and prompt safety for payment-tool usage.
- It produces deterministic local findings plus LLM-generated senior-review guidance.
- It gives concrete auto-fix suggestions, but never silently changes financial code without user approval.
- It is packaged as a Codex Plugin so the workflow can be reused by teams, not copied as one-off prompts.

## Required features

- `/review`
- `/review security`
- `/review api`
- `/review performance`
- `/review payment`
- `/review prompt`
- `/review agent`
- `/review payagent`
- Local Python Rule Engine
- Markdown report
- JSON report
- Risk/Security/Quality/Deployment/Trust score
- Auto Fix Plan
- Sample unsafe payment service
- Sample unsafe payment agent
- Logs folder

## Optional features

- Git diff mode
- `--fail-under` CI gate
- SARIF export
- service-profile rule packs
- generated pytest scenarios
- PR comment formatter

## Expansion features

- Payment Open API schema checks
- AI Agent payment-flow state-machine checks
- incident/postmortem checklist generation inspired by public Pink Ward material
- FDS signal review for fraud-detection feature changes
- MLflow-backed prompt and rule evaluation
- MCP server for approved internal policy/context after adoption

## Review checklist

- Privacy: phone, email, account, card, CVC, CI/DI, resident registration number, device ID, IP, transaction data, retention.
- Financial security: secret, hard-coded key, SQL injection, XSS, authz bypass, JWT, OAuth.
- Payment safety: idempotency, ledger uniqueness, transaction boundary, refund/cancel state machine, duplicate webhook.
- API stability: breaking change, schema drift, status code, versioning, compatibility, timeout semantics.
- Operations: timeout, retry, circuit breaker, rollback, alert, owner, README/runbook.
- Performance: N+1, unbounded loop, batch size, hot-path external call.
- Test quality: unit, integration, contract, concurrency, retry, failure, edge cases.
- Prompt/Agent: prompt injection, untrusted content boundary, tool permission, confirmation gate, audit log, data minimization.

## Score model

All scores are 0 to 100. Higher is better.

```text
Risk Score       = 100 - all finding penalties
Security Score   = 100 - security/privacy/auth/injection/secret penalties
Quality Score    = 100 - test/readme/architecture/prompt penalties
Deployment Score = 100 - payment/api/performance/transaction/concurrency/deployment penalties
Trust Score      = Security*0.4 + Deployment*0.3 + Quality*0.2 + Risk*0.1
```

Severity penalties:

- Critical: 25
- High: 18
- Medium: 10
- Low: 4

## Auto Fix design

Auto Fix is suggestion-first.

1. Rule Engine creates finding-specific `recommendation` and `fix_example`.
2. Codex reads the finding and opens the target file.
3. Codex proposes the smallest safe patch.
4. User approves before any financial code is changed.
5. Scanner and tests run again.

Examples:

- Secret: move to environment/vault and rotate exposed value.
- PII log: mask card/account/user fields.
- Payment operation: add idempotency key and unique ledger.
- Transaction: wrap ledger/status/outbox in one transaction.
- Agent tool: require explicit confirmation before approve/cancel/refund.
- Prompt: isolate untrusted user/ticket/log content.

## Python interface

CLI:

```bash
python3 scripts/securepay_review.py <target> --category payment --format markdown
python3 scripts/securepay_review.py <target> --category payagent --format json --fail-under 70
```

Input:

- target file or directory
- category: `all`, `security`, `api`, `performance`, `payment`, `prompt`, `agent`, `payagent`
- output format: `markdown` or `json`
- optional output path
- optional Trust Score threshold

Output JSON:

```json
{
  "target": "path",
  "profile": "payagent",
  "scores": {
    "risk_score": 0,
    "security_score": 70,
    "quality_score": 86,
    "deployment_score": 46,
    "trust_score": 63,
    "finding_count": 5
  },
  "findings": [],
  "fix_plan": []
}
```

Core classes:

- `ReviewEngine`
- `ReviewOptions`
- `Rule`
- `Finding`
- `ScoreCard`
- `ReviewReport`

## Submission structure

Final `submission.zip` is packaged as:

```text
submission.zip
├── src/
│   ├── .codex-plugin/plugin.json
│   ├── skills/securepay-reviewer/SKILL.md
│   ├── scripts/securepay_review.py
│   ├── scripts/securepay_ai_reviewer/
│   ├── samples/payment-service/
│   └── samples/payment-agent/
├── README.md
└── logs/
    ├── sample-payment-review.md
    ├── sample-security-review.json
    ├── sample-payagent-review.md
    └── RAW_AI_CONVERSATION_REQUIRED.md
```

Important: the raw AI conversation log must be exported from the chat environment and placed under `logs/` without editing, deletion, excerpting, or summarization. This repository does not fabricate that log.

## MVP scope

6-hour MVP:

- plugin manifest
- Codex Skill
- Python Rule Engine
- payment/security/privacy/API/prompt/agent rules
- two unsafe samples
- Markdown/JSON reports
- packaged `submission.zip`

3-day MVP:

- generated pytest scenarios
- git diff mode
- configurable rule packs
- CI gate
- Open API schema comparison
- richer payment-agent state-machine validation
- report polish for judge demo

## 5-minute pitch summary

KakaoPay already shows, through public material, that it is a financial platform, that privacy/security are core operating values, that AI Agent/MCP payment integration is being explored, and that AI coding increases the burden on human review. SecurePay AI Reviewer turns those public problems into a working Codex Plugin. It lets a developer run one command before merge and immediately see whether a financial change is safe enough to ship, where human review must focus, and what concrete fixes are needed.
