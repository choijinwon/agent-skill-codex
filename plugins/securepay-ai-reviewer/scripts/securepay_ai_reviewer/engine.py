from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Iterable


SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".kt",
    ".go",
    ".rb",
    ".php",
    ".sql",
    ".yaml",
    ".yml",
    ".json",
    ".md",
}

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "dist", "build"}


@dataclass(frozen=True)
class ReviewOptions:
    categories: tuple[str, ...] = ("all",)
    include_fix_plan: bool = True


@dataclass(frozen=True)
class Rule:
    rule_id: str
    category: str
    title: str
    severity: str
    pattern: re.Pattern[str]
    rationale: str
    recommendation: str
    fix_example: str
    weight: int


@dataclass
class Finding:
    rule_id: str
    category: str
    severity: str
    title: str
    file: str
    line: int
    evidence: str
    rationale: str
    recommendation: str
    fix_example: str


@dataclass
class ScoreCard:
    risk_score: int
    security_score: int
    quality_score: int
    deployment_score: int
    trust_score: int
    finding_count: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int


@dataclass
class ReviewReport:
    target: str
    profile: str
    scores: ScoreCard
    findings: list[Finding] = field(default_factory=list)
    fix_plan: list[dict[str, str]] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    def to_markdown(self) -> str:
        score = self.scores
        lines = [
            "# SecurePay AI Reviewer Report",
            "",
            f"- Target: `{self.target}`",
            f"- Profile: `{self.profile}`",
            f"- Findings: {score.finding_count} total, {score.critical_count} critical, {score.high_count} high",
            "",
            "## Scorecard",
            "",
            "| Metric | Score | Meaning |",
            "| --- | ---: | --- |",
            f"| Risk Score | {score.risk_score}/100 | 100 means low release risk |",
            f"| Security Score | {score.security_score}/100 | Secret, injection, auth, privacy safety |",
            f"| Quality Score | {score.quality_score}/100 | Testability, maintainability, architecture |",
            f"| Deployment Score | {score.deployment_score}/100 | Timeout, retry, error handling, rollback readiness |",
            f"| Trust Score | {score.trust_score}/100 | Weighted final score for reviewer confidence |",
            "",
            "## Findings",
            "",
        ]
        if not self.findings:
            lines.append("No findings matched the current rule set.")
        for finding in self.findings:
            lines.extend(
                [
                    f"### {finding.severity.upper()} · {finding.title}",
                    "",
                    f"- Rule: `{finding.rule_id}`",
                    f"- Category: `{finding.category}`",
                    f"- Location: `{finding.file}:{finding.line}`",
                    f"- Evidence: `{finding.evidence}`",
                    f"- Why it matters: {finding.rationale}",
                    f"- Recommendation: {finding.recommendation}",
                    "",
                    "```text",
                    finding.fix_example,
                    "```",
                    "",
                ]
            )
        if self.fix_plan:
            lines.extend(["## Auto Fix Plan", ""])
            for idx, fix in enumerate(self.fix_plan, start=1):
                lines.extend(
                    [
                        f"{idx}. `{fix['file']}` · {fix['rule_id']}",
                        f"   - Change: {fix['change']}",
                        f"   - Suggested code: `{fix['suggested_code']}`",
                    ]
                )
        return "\n".join(lines)


class ReviewEngine:
    def __init__(self, root: Path, options: ReviewOptions | None = None) -> None:
        self.target_label = _display_path(root)
        self.root = root.resolve()
        self.options = options or ReviewOptions()
        self.rules = _build_rules()

    def run(self) -> ReviewReport:
        profile = ",".join(self.options.categories)
        selected = self._selected_rules()
        findings: list[Finding] = []
        files = list(_iter_files(self.root))

        for file_path in files:
            text = _read_text(file_path)
            if text is None:
                continue
            rel = str(file_path.relative_to(self.root))
            findings.extend(self._scan_file(rel, text, selected))

        findings.extend(self._project_level_findings(files))
        findings.sort(key=lambda item: (_severity_rank(item.severity), item.file, item.line))
        scores = self._score(findings)
        fix_plan = self._fix_plan(findings) if self.options.include_fix_plan else []
        return ReviewReport(self.target_label, profile, scores, findings, fix_plan)

    def _selected_rules(self) -> list[Rule]:
        categories = set(self.options.categories)
        if "all" in categories:
            return self.rules
        aliases = {
            "payment": {"payment", "transaction", "concurrency", "api", "deployment"},
            "security": {"security", "privacy", "auth", "injection", "secret"},
            "performance": {"performance", "deployment"},
            "prompt": {"prompt", "agent", "payagent"},
            "api": {"api", "deployment"},
            "agent": {"agent", "prompt", "payagent", "privacy", "payment"},
            "payagent": {"agent", "prompt", "payagent", "privacy", "payment", "deployment"},
        }
        expanded = set(categories)
        for category in categories:
            expanded.update(aliases.get(category, set()))
        return [rule for rule in self.rules if rule.category in expanded]

    def _scan_file(self, rel: str, text: str, rules: list[Rule]) -> list[Finding]:
        findings: list[Finding] = []
        lines = text.splitlines()
        for line_no, line in enumerate(lines, start=1):
            for rule in rules:
                if rule.pattern.search(line):
                    findings.append(
                        Finding(
                            rule.rule_id,
                            rule.category,
                            rule.severity,
                            rule.title,
                            rel,
                            line_no,
                            line.strip()[:180],
                            rule.rationale,
                            rule.recommendation,
                            rule.fix_example,
                        )
                    )
        return findings

    def _project_level_findings(self, files: list[Path]) -> list[Finding]:
        rel_files = {str(path.relative_to(self.root)) for path in files}
        findings: list[Finding] = []
        has_source = any(path.suffix in {".py", ".js", ".ts", ".tsx", ".java", ".kt", ".go"} for path in files)
        has_tests = any("test" in path.name.lower() or "/test" in str(path).lower() for path in files)
        has_readme = any(path.name.lower() == "readme.md" for path in files)

        if has_source and not has_tests:
            findings.append(
                Finding(
                    "TEST-001",
                    "test",
                    "medium",
                    "No automated tests detected",
                    ".",
                    1,
                    "source files exist but no test files were found",
                    "Payment changes need executable evidence for rollback-safe releases.",
                    "Add focused unit tests and at least one integration test around payment success, failure, duplicate request, and timeout cases.",
                    "tests/test_payment_service.py with duplicate payment and timeout scenarios",
                )
            )
        if not has_readme:
            findings.append(
                Finding(
                    "DOC-001",
                    "readme",
                    "low",
                    "README is missing",
                    ".",
                    1,
                    f"{len(rel_files)} files scanned",
                    "Financial services need operational context, ownership, and runbook links during incidents.",
                    "Add README sections for owner, APIs, dependencies, SLO, rollback, and FDS/security notes.",
                    "README.md: owner, endpoints, alert channels, rollback command, known risk controls",
                )
            )
        return findings

    def _score(self, findings: list[Finding]) -> ScoreCard:
        totals = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for finding in findings:
            totals[finding.severity] = totals.get(finding.severity, 0) + 1

        security_penalty = sum(_penalty(f) for f in findings if f.category in {"security", "privacy", "auth", "injection", "secret"})
        quality_penalty = sum(_penalty(f) for f in findings if f.category in {"test", "architecture", "readme", "agent", "prompt"})
        deployment_penalty = sum(_penalty(f) for f in findings if f.category in {"deployment", "performance", "api", "transaction", "concurrency", "payment"})
        total_penalty = sum(_penalty(f) for f in findings)

        security_score = max(0, 100 - security_penalty)
        quality_score = max(0, 100 - quality_penalty)
        deployment_score = max(0, 100 - deployment_penalty)
        risk_score = max(0, 100 - total_penalty)
        trust_score = round((security_score * 0.4) + (deployment_score * 0.3) + (quality_score * 0.2) + (risk_score * 0.1))

        return ScoreCard(
            risk_score,
            security_score,
            quality_score,
            deployment_score,
            trust_score,
            len(findings),
            totals.get("critical", 0),
            totals.get("high", 0),
            totals.get("medium", 0),
            totals.get("low", 0),
        )

    def _fix_plan(self, findings: list[Finding]) -> list[dict[str, str]]:
        fixes: list[dict[str, str]] = []
        seen: set[tuple[str, str]] = set()
        for finding in findings:
            key = (finding.file, finding.rule_id)
            if key in seen:
                continue
            seen.add(key)
            fixes.append(
                {
                    "file": finding.file,
                    "rule_id": finding.rule_id,
                    "change": finding.recommendation,
                    "suggested_code": finding.fix_example,
                }
            )
        return fixes[:12]


def _build_rules() -> list[Rule]:
    return [
        Rule(
            "SECRET-001",
            "secret",
            "Hard-coded secret or token",
            "critical",
            re.compile(r"(?i)(api[_-]?key|secret|password|passwd|token)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
            "Leaked credentials in source code can directly compromise payment and user data systems.",
            "Move secrets to a vault or environment variable and rotate the exposed value.",
            "PAYMENT_API_KEY = os.environ['PAYMENT_API_KEY']",
            25,
        ),
        Rule(
            "PRIVACY-001",
            "privacy",
            "Sensitive personal or payment data in logs",
            "high",
            re.compile(r"(?i)(log|logger|print).*(card|cvc|cvv|rrn|resident|phone|email|account|birth)"),
            "Logs are copied to observability and incident systems; raw PII creates privacy and compliance risk.",
            "Mask or hash sensitive fields before logging and define retention rules.",
            "logger.info('payment approved user=%s card=%s', user_id, mask_card(card_no))",
            18,
        ),
        Rule(
            "INJECT-001",
            "injection",
            "Potential SQL injection",
            "critical",
            re.compile(r"(?i)(execute|query)\s*\(.*(%|\+|f['\"])"),
            "Payment and settlement queries must not concatenate user-controlled input.",
            "Use parameterized SQL or repository helpers that bind values.",
            "cursor.execute('select * from payments where user_id = ?', (user_id,))",
            25,
        ),
        Rule(
            "AUTH-001",
            "auth",
            "JWT verification appears disabled or weak",
            "critical",
            re.compile(r"(?i)(verify\s*=\s*False|algorithms\s*=\s*\[['\"]none['\"]\]|jwt\.decode\(.*verify)"),
            "Weak token verification can bypass account ownership and authorization checks.",
            "Require issuer, audience, expiration, signature verification, and key rotation.",
            "jwt.decode(token, key, algorithms=['RS256'], audience='kakaopay-api', issuer='auth')",
            25,
        ),
        Rule(
            "OAUTH-001",
            "auth",
            "OAuth redirect or state handling looks unsafe",
            "high",
            re.compile(r"(?i)(redirect_uri\s*=\s*['\"]http://|state\s*=\s*None|skip_state)"),
            "OAuth flows need redirect allowlists and CSRF state to protect account linking.",
            "Use HTTPS redirect allowlists and mandatory state validation.",
            "validate_state(request.args['state']); assert redirect_uri in allowed_redirects",
            18,
        ),
        Rule(
            "API-001",
            "api",
            "Possible breaking API change",
            "medium",
            re.compile(r"(?i)(delete\s+endpoint|remove\s+field|rename\s+field|breaking)"),
            "Payment clients and partner integrations need compatibility windows.",
            "Add versioning, compatibility tests, and migration notes.",
            "Expose /v2 while keeping /v1 until clients migrate; add contract tests",
            10,
        ),
        Rule(
            "DEPLOY-001",
            "deployment",
            "Outbound HTTP call without timeout",
            "high",
            re.compile(r"(?i)requests\.(get|post|put|delete)\((?!.*timeout\s*=)"),
            "Missing timeouts can exhaust worker pools and cascade into payment failures.",
            "Set connect/read timeouts and map timeout errors to retry-safe responses.",
            "requests.post(url, json=payload, timeout=(0.5, 2.0))",
            18,
        ),
        Rule(
            "PAY-001",
            "payment",
            "Payment operation without idempotency signal",
            "high",
            re.compile(r"(?i)def\s+(pay|approve|capture|refund|transfer|withdraw|deposit)"),
            "Financial operations must be safe under client retry, network retry, and duplicate webhook delivery.",
            "Require an idempotency key and persist a unique request ledger.",
            "def approve_payment(request, idempotency_key: str): ledger.ensure_once(idempotency_key)",
            18,
        ),
        Rule(
            "TX-001",
            "transaction",
            "Balance or payment state update needs transaction boundary",
            "high",
            re.compile(r"(?i)(balance\s*[+-]?=|status\s*=\s*['\"](approved|paid|refunded)|update payments set)"),
            "Money movement requires atomicity across state transitions, ledger writes, and event publication.",
            "Wrap updates in a database transaction and emit events after commit.",
            "with db.transaction(): update_ledger(); update_payment_status(); outbox.add(event)",
            18,
        ),
        Rule(
            "CONC-001",
            "concurrency",
            "Potential race condition on financial state",
            "high",
            re.compile(r"(?i)(balance|available_amount|daily_limit|remaining_limit)\s*[+\-]="),
            "Concurrent retries can double-apply money-state changes when updates are not guarded by locks or optimistic versions.",
            "Use transaction-level locking or optimistic concurrency and add a concurrent duplicate-request test.",
            "test two simultaneous approve requests produce one ledger row",
            12,
        ),
        Rule(
            "XSS-001",
            "security",
            "Potential XSS sink",
            "high",
            re.compile(r"(?i)(innerHTML|dangerouslySetInnerHTML|v-html)"),
            "Payment UIs often display merchant/user data and must not render unsanitized input.",
            "Use text rendering or an approved sanitizer with tests.",
            "element.textContent = merchantName",
            18,
        ),
        Rule(
            "PROMPT-001",
            "prompt",
            "Prompt may include untrusted user content without guardrails",
            "medium",
            re.compile(r"(?i)(system_prompt|developer_prompt|prompt)\s*[:=].*\{.*user"),
            "AI review or support agents can be prompt-injected through ticket, PR, or log content.",
            "Separate instructions from data and add explicit untrusted-content boundaries.",
            "<untrusted_user_content>{user_text}</untrusted_user_content>",
            10,
        ),
        Rule(
            "AGENT-001",
            "agent",
            "Payment agent tool call lacks explicit confirmation gate",
            "high",
            re.compile(r"(?i)(approve|cancel|refund|disable|deactivate|execute_payment).*tool"),
            "AI agents that can invoke payment, cancel, refund, or subscription tools need explicit user confirmation before irreversible or sensitive actions.",
            "Add a confirmation state before the tool call and require amount, merchant/product, target payment id, and user intent to match.",
            "if not confirmation.accepted: return ask_confirmation(payment_summary)",
            18,
        ),
        Rule(
            "AGENT-002",
            "payagent",
            "Payment agent prompt may over-authorize tool use",
            "high",
            re.compile(r"(?i)(you may call any tool|always call.*payment|do not ask.*confirm|skip confirmation)"),
            "Payment agents must not be prompted to call sensitive tools broadly or bypass confirmation.",
            "Restrict tool use by intent and action risk, and require confirmation for approve/cancel/refund/recurring-payment changes.",
            "Allowed tools: status_lookup without confirmation; approve/cancel/refund only after explicit confirmation.",
            18,
        ),
        Rule(
            "AGENT-003",
            "payagent",
            "Payment agent action lacks audit evidence",
            "medium",
            re.compile(r"(?i)(approve|cancel|refund|recurring).*(payment|subscription)(?!.*audit|.*event|.*log)"),
            "A payment agent action must leave auditable evidence for dispute handling, incident review, and privacy/security governance.",
            "Write an audit event with action, payment id, masked user id, tool name, confirmation id, and result.",
            "audit.record(action='refund', payment_id=tid, confirmation_id=cid, result='requested')",
            10,
        ),
        Rule(
            "PERF-001",
            "performance",
            "N+1 or unbounded loop risk",
            "medium",
            re.compile(r"(?i)for .* in .*(payments|users|transactions|orders).*:\s*$"),
            "Batch payment paths must avoid unbounded DB/API calls under traffic spikes.",
            "Batch queries, paginate, and add load tests for expected peak volume.",
            "fetch_payments_in_batch(ids); process with bounded page size",
            10,
        ),
    ]


def _iter_files(root: Path) -> Iterable[Path]:
    if root.is_file():
        yield root
        return
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield path


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def _display_path(path: Path) -> str:
    if not path.is_absolute():
        return path.as_posix()
    try:
        relative = path.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        return path.name
    return relative.as_posix() or "."


def _penalty(finding: Finding) -> int:
    base = {"critical": 25, "high": 18, "medium": 10, "low": 4}.get(finding.severity, 4)
    return base


def _severity_rank(severity: str) -> int:
    return {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(severity, 4)
