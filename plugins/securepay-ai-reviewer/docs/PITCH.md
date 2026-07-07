# 5-minute pitch

## 0:00-0:30 Opening

카카오페이에서 코드는 단순히 동작하면 되는 것이 아닙니다. 결제, 송금, 자산관리, 투자, 대출, 보험까지 이어지는 금융 코드입니다. 작은 로그 한 줄, timeout 하나, idempotency 누락 하나, AI Agent tool 권한 하나가 개인정보 위험, 중복 결제, 장애, 신뢰 하락으로 이어질 수 있습니다.

## 0:30-1:10 Public problem

카카오페이 공개 자료는 세 가지 흐름을 보여줍니다.

첫째, 카카오페이는 다양한 금융 서비스를 운영합니다.  
둘째, ESG/보안 자료는 Privacy by Design, CISO 거버넌스, 24/7 SOC, 취약점 분석, ISMS-P, ISO, PCI DSS를 강조합니다.  
셋째, 기술 블로그는 AI Agent와 카카오페이 결제 Open API를 MCP로 연동하는 흐름, SDD 기반 agentic coding, AI 시대 PR 리뷰 병목을 공개적으로 다룹니다.

즉 문제는 명확합니다. AI가 코드를 빠르게 만들고 결제 도구까지 호출하는 시대에, 금융 개발자는 더 일관된 AI Senior Reviewer가 필요합니다.

## 1:10-2:00 Solution

SecurePay AI Reviewer는 Codex Plugin 기반 Financial AI Code Review Copilot입니다.

핵심은 복잡한 AI가 아닙니다.

```text
LLM senior-review prompt + Rule Engine + Python CLI
```

개발자는 PR 전 한 줄만 실행합니다.

```bash
python3 scripts/securepay_review.py samples/payment-service --category payment
python3 scripts/securepay_review.py samples/payment-agent --category payagent
```

결과는 Risk, Security, Quality, Deployment, Trust Score와 Must Fix, Tests To Add, Auto Fix Plan으로 나옵니다.

## 2:00-3:00 What is different

이건 단순 코드리뷰가 아닙니다.

일반 리뷰가 "코드가 괜찮은가"를 묻는다면, SecurePay AI Reviewer는 "이 금융 변경을 내일 카카오페이에 배포해도 되는가"를 묻습니다.

특히 결제 AI Agent까지 봅니다.

- 결제 승인/취소/환불 tool에 confirmation이 있는가
- AI prompt가 tool을 과도하게 허용하지 않는가
- prompt injection에 취약하지 않은가
- 결제 action이 audit log를 남기는가
- 결제/개인정보가 log나 prompt에 과다 노출되지 않는가

## 3:00-4:00 Business value

도입 효과는 명확합니다.

- Senior reviewer 품질을 팀 전체 기본값으로 만든다.
- 보안/개인정보/운영 안정성 리뷰를 반복 가능하게 만든다.
- AI Agent 결제 기능의 배포 전 안전 게이트가 된다.
- 신규 개발자의 금융 도메인 학습을 돕는다.
- 사람 리뷰어는 기계적 누락이 아니라 비즈니스 판단과 트레이드오프에 집중한다.

## 4:00-4:40 MVP feasibility

6시간 MVP로 가능합니다.

- plugin manifest
- Codex Skill
- Python Rule Engine
- unsafe payment sample
- unsafe payment agent sample
- Markdown/JSON report
- Auto Fix Plan
- submission.zip

3일이면 git diff mode, generated tests, Open API schema checks, richer payment-agent state-machine checks까지 확장할 수 있습니다.

## 4:40-5:00 Closing

SecurePay AI Reviewer는 사람 리뷰어를 대체하지 않습니다. 사람이 보기 전에 금융 리스크를 먼저 정리하는 AI Senior Reviewer입니다. 카카오페이가 내일부터 써볼 수 있는 이유는 단순합니다. 로컬에서 돌고, 설명 가능하고, 카카오페이 공개 자료의 실제 문제에 맞춰져 있으며, 30초 안에 가치를 보여줍니다.
