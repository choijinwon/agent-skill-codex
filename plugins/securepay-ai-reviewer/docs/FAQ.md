# Expected Questions and Answers

1. Q: 이 Plugin은 무엇을 하나요?
   A: 금융 서비스 코드와 결제 AI Agent 코드를 배포 전 검토해 개인정보, 보안, 결제 안전성, API 안정성, 테스트, 운영 위험을 점수화하고 수정안을 제안합니다.

2. Q: 누가 사용하나요?
   A: 카카오페이 결제/API/AI Agent/플랫폼 개발자와 보안·품질 리뷰 담당자가 PR 전후에 사용합니다.

3. Q: 어떤 상황에서 사용하나요?
   A: 결제/환불/취소/상태조회 코드 변경, API 변경, AI Agent prompt/tool 변경, 운영 안정성 영향이 있는 변경 전에 사용합니다.

4. Q: 왜 이 문제를 선택했나요?
   A: 카카오페이 공개 자료가 금융 서비스 범위, 정보보호/개인정보보호 중요성, AI Agent 결제 API 연동, AI 시대 PR 리뷰 병목을 모두 보여주기 때문입니다.

5. Q: 단순 코드리뷰와 무엇이 다른가요?
   A: 단순 코드 스타일이 아니라 "금융 변경을 안전하게 배포할 수 있는가"를 평가합니다. 특히 결제 idempotency, transaction, audit, prompt/tool safety를 봅니다.

6. Q: AI를 어떻게 활용했나요?
   A: Codex Skill이 senior reviewer 관점을 제공하고, LLM은 위험 시나리오 해석, 테스트 아이디어, auto-fix 제안에 사용됩니다. 반복 탐지는 Rule Engine이 담당합니다.

7. Q: 왜 복잡한 ML 모델을 만들지 않았나요?
   A: 해커톤 MVP와 금융 도입성에서는 재현성, 설명 가능성, 빠른 검증이 중요합니다. LLM + Rule Engine + Python이 가장 현실적입니다.

8. Q: 어떻게 검증했나요?
   A: unsafe payment service와 unsafe payment agent 샘플을 스캔해 critical/high finding, scorecard, fix plan, JSON/Markdown 출력, CLI exit code를 확인했습니다.

9. Q: 공개 근거는 무엇인가요?
   A: 카카오페이 공식 홈페이지, ESG/정보보호 자료, 개인정보 처리방침, 기술 블로그의 PR/AI 리뷰, SDD, MCP Agent Toolkit, Pink Ward 글입니다.

10. Q: 외부 기업 자료를 쓰나요?
    A: 제출 문서에서는 사용하지 않습니다. 해커톤 규칙에 맞춰 카카오페이 공개 자료만 근거로 삼습니다.

11. Q: 개인정보는 어떤 것을 보나요?
    A: 카드, CVC, 계좌, 전화번호, 이메일, CI/DI, 주민등록번호, device ID, IP, 거래 정보의 로그·prompt·외부 전송 위험을 봅니다.

12. Q: 결제 안전성은 무엇을 보나요?
    A: idempotency, ledger uniqueness, transaction boundary, refund/cancel state, duplicate webhook, retry safety를 봅니다.

13. Q: AI Agent 안전성은 무엇을 보나요?
    A: tool over-authorization, confirmation 누락, prompt injection, untrusted content boundary, audit log, sensitive-data minimization을 봅니다.

14. Q: Auto Fix가 위험하지 않나요?
    A: 자동 커밋하지 않습니다. fix plan을 만들고 사용자가 승인해야 Codex가 작은 패치를 적용합니다.

15. Q: 점수는 어떤 의미인가요?
    A: 절대 안전 인증이 아니라 리뷰 우선순위와 merge risk를 빠르게 파악하기 위한 triage score입니다.

16. Q: Critical finding은 무엇인가요?
    A: secret, SQL injection, JWT 검증 약화처럼 즉시 차단해야 할 위험입니다.

17. Q: High finding은 무엇인가요?
    A: PII logging, payment idempotency 누락, timeout 누락, transaction boundary 누락, confirmation 없는 결제 tool 호출 등입니다.

18. Q: False positive는 어떻게 줄이나요?
    A: 첫 주는 non-blocking report로 운영하고, 서비스별 rule pack과 threshold를 조정합니다.

19. Q: Java/Kotlin/Spring에도 쓸 수 있나요?
    A: 현재는 주요 소스 확장자를 읽는 regex 기반 MVP입니다. 3일 버전에서 Spring transaction/controller/repository rule을 확장합니다.

20. Q: 테스트 생성도 하나요?
    A: MVP는 missing test와 test suggestion을 냅니다. Codex follow-up으로 unit/integration/concurrency 테스트를 생성하도록 확장합니다.

21. Q: README를 왜 검사하나요?
    A: 금융 서비스 운영에는 owner, rollback, alert, dependency, runbook이 필요하기 때문입니다.

22. Q: Prompt review가 왜 필요한가요?
    A: AI Agent가 PR, 로그, 이슈, 사용자 입력을 읽으면 prompt injection과 민감정보 노출 위험이 생깁니다.

23. Q: PayAgent review가 왜 중요한가요?
    A: 카카오페이 공개 기술 블로그가 결제 Open API와 AI Agent/MCP 연동을 다루고 있어, tool 호출 안전성 검증이 실제 문제와 직접 연결됩니다.

24. Q: 운영 안정성은 무엇을 보나요?
    A: timeout, retry, circuit breaker, rollback, alert, 장애 대응 문서, audit evidence를 봅니다.

25. Q: FDS와 어떻게 연결되나요?
    A: 확장 버전에서 fraud signal 누락, feature schema drift, retry duplicate signal을 rule pack으로 추가할 수 있습니다.

26. Q: CI에서 쓸 수 있나요?
    A: `--fail-under`로 Trust Score 기준을 걸 수 있고, 기준 미달 시 exit code 2를 반환합니다.

27. Q: 도입 후 효과는 어떻게 측정하나요?
    A: critical finding 수, PR rework time, escaped defect, 장애 재발, accepted fix rate, false-positive rate를 봅니다.

28. Q: 6시간 안에 정말 구현 가능한가요?
    A: 이미 plugin manifest, skill, Python scanner, sample, logs, report, zip packaging까지 가능한 구조입니다.

29. Q: 3일이면 무엇을 더 하나요?
    A: generated pytest, git diff mode, Open API schema comparison, service-profile rule pack, report polish를 추가합니다.

30. Q: 심사위원에게 한 문장으로 설명하면?
    A: "카카오페이 금융 개발자가 PR 전 한 줄로 결제·개인정보·AI Agent 위험을 점수화하고 수정안까지 받는 Codex Plugin입니다."
