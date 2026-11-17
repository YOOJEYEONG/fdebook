# 학습북 v2 자료 조사

접근일: 2026-11-17(모든 출처 동일). 조사·작성: Opus 5.5 세션. 기존 `docs/research.md`의 통계·기술 문구는 재사용하지 않았고, 아래 출처를 새로 열어 확인했다.

## 1. 조사 방법과 원칙

- 역할 설명은 기업이 직접 운영하는 채용 시스템의 원문만 쓴다. 웹 페이지가 막혀 있는 경우(openai.com/careers는 403) 같은 기업의 공식 채용 게시판 API(Ashby, Greenhouse, Lever)에서 받은 원문을 읽었다. 집계 사이트(jointaro, builtin 등)는 근거로 쓰지 않는다.
- 공고 문구는 "이 기업이 이 직무에 무엇을 기대한다고 썼는가"의 근거로만 쓴다. "FDE 시장 규모", "연봉", "채용이 쉽다/어렵다" 같은 일반화는 하지 않는다. 공고 몇 개로 기술 사실을 정당화하지 않는다.
- 기술 설명은 표준(RFC·IETF 초안)과 각 기술의 공식 문서를 우선한다.
- 원문을 옮기지 않고 한국어로 새로 설명한다. 인용은 짧은 핵심 구절에 한한다.

## 2. 역할 출처 — 공식 채용 원문

| ID | 기업·직무 | 원문 위치 | 게시/갱신 |
|---|---|---|---|
| R1 | OpenAI, Forward Deployed Engineer – Seoul | https://jobs.ashbyhq.com/openai/b43339a1-e830-4761-a193-3438f34f9ebb (Ashby 공개 API `api.ashbyhq.com/posting-api/job-board/openai`) | 2026-06-23 게시 |
| R2 | OpenAI, Forward Deployed Software Engineer – SF | https://jobs.ashbyhq.com/openai/00207abc-49b7-465c-a219-f7c1140f8047 | 2025-11-15 게시 |
| R3 | Anthropic, Forward Deployed Engineer (Applied AI) – London | https://job-boards.greenhouse.io/anthropic/jobs/5423029008 | 2026-09-14 갱신 |
| R4 | Anthropic, Staff Forward Deployed Engineer | https://job-boards.greenhouse.io/anthropic/jobs/5449229008 | 2026-10-14 갱신 |
| R5 | Palantir, Forward Deployed Software Engineer – London | https://jobs.lever.co/palantir/5168e8fd-fec1-4fea-b7a1-81bdaea65850 | Lever 공개 API |
| R6 | Palantir, Forward Deployed AI Engineer – New York | https://jobs.lever.co/palantir/636fc05c-d348-4a06-be51-597cb9e07488 | Lever 공개 API |

### 공고에서 확인한 공통 업무(근거 ID)

| 역량 | 공고 표현(요약 번역) | 근거 | 다루는 장 |
|---|---|---|---|
| 고객 문제 발견·범위 설정 | discovery, technical scoping을 맡는다 / PoC와 운영 배포의 작업 범위와 계획을 쓴다 / 빌드 전 범위와 기술 전략을 정한다 | R1, R2, R4 | 1장 |
| 처음부터 운영까지 책임 | 첫 프로토타입부터 안정적 운영까지 / 첫 대화부터 운영 방식을 바꾸는 제품 출시까지 | R1, R5 | 1, 4, 8장 |
| 풀스택 구현 | 프론트엔드·백엔드 운영 수준 코드(Python, JavaScript 등) / 풀스택 솔루션 설계·구현 / Postgres·MySQL 같은 관계형 DB 경험 | R1, R2 | 2, 3, 4장 |
| 데이터 다루기 | 가정이 깨지는 규모의 데이터를 다룬다 / 데이터 처리 파이프라인 | R5, R6 | 3장 |
| 보안·권한·개인정보 | 보안 코딩, 취약점 관리, 접근 통제·권한·개인정보 고려 / 보안·조달 관문을 미리 예상 | R5, R4 | 3.5, 5.5장 |
| 트레이드오프 판단 | 범위·속도·품질 사이 트레이드오프 / 설계 결정을 이끈다 | R1, R4 | 7장 |
| 커뮤니케이션 | 엔지니어·제품·고객 이해관계자와 명확히 소통 / 다양한 이해관계자에게 기술 개념 전달 | R1, R3 | 7장 |
| 패턴 정리와 현장 피드백 | 반복 가능한 배포 패턴을 도구·플레이북으로 정리 / 현장 피드백을 제품·연구팀에 전달 | R1, R2, R3 | 7.3장 |
| 고객이 운영할 수 있는 인수인계 | 고객이 운영할 수 있는 시스템을 넘긴다 | R4 | 7.3장 |

### AI 특화 역량(일반 FDE와 구분)

| 역량 | 근거 | 다루는 장 |
|---|---|---|
| LLM·생성 모델 기반 시스템 구축, 모델 동작이 제품 경험에 미치는 영향 이해 | R1 | 6.1 |
| 평가(eval) 기반 피드백, 평가 프레임워크 | R1, R3, R6("Evaluation") | 6.4 |
| MCP 서버·서브에이전트·에이전트 스킬 같은 산출물 | R3 | 6.2 |
| 프롬프트 엔지니어링·에이전트 개발·대규모 배포 | R3 | 6.1, 6.2, 6.6 |

판단: R5(Palantir FDSE)는 LLM 경험을 필수로 요구하지 않고, R4는 "에이전트를 운영에 출시한 경험은 필요 없다, 운영 시스템 구축·운영 경험은 깊어야 한다"고 쓴다. 따라서 이 책은 1–5·7장을 FDE 공통 기반, 6장을 AI FDE 추가 역량으로 나눈다.

### 쓰지 않기로 한 것
- 연봉·이동 비율·경력 연수는 공고마다 다르고 바뀌므로 본문에 일반 사실로 쓰지 않는다(1.1절에서 "공고마다 다르다"고만 언급).
- "Palantir가 이 직무를 개척했다"는 Palantir 자신의 주장(R5)이므로 회사 주장으로만 표기한다.

## 3. 기술 출처와 주장 대응표

| ID | 출처 | 확인한 사실 | 쓰는 절 |
|---|---|---|---|
| T1 | RFC 9110 HTTP Semantics, https://www.rfc-editor.org/rfc/rfc9110 | 안전한 메서드는 GET·HEAD·OPTIONS·TRACE(9.2.1). 멱등 메서드는 PUT·DELETE와 안전한 메서드(9.2.2). Retry-After는 후속 요청 전 기다릴 시간(10.2.3). 상태 코드 5개 분류(15). 401/403/409/422 정의 | 2.1, 2.2, 2.4, 2.5 |
| T2 | RFC 6585, https://www.rfc-editor.org/rfc/rfc6585 | 429는 일정 시간 동안 요청이 너무 많음, Retry-After를 포함할 수 있음(MAY) | 2.4 |
| T3 | RFC 9457 Problem Details, https://www.rfc-editor.org/rfc/rfc9457 | `application/problem+json`, 멤버 type·title·status·detail·instance, RFC 7807 대체 | 2.2, 4.1 |
| T4 | RFC 6750 Bearer Token, https://www.rfc-editor.org/rfc/rfc6750 | 토큰을 가진 누구나 쓸 수 있음. `Authorization: Bearer`. invalid_token→401, insufficient_scope→403 | 2.2 |
| T5 | IETF draft-ietf-httpapi-idempotency-key-header-08, https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/ | 아직 RFC가 아닌 초안(2026-10-22 갱신). 같은 키·다른 본문 → 422, 처리 중 중복 → 409, 키 필수인데 없음 → 400, 만료 정책은 문서화 | 2.5 |
| T6 | AWS Builders' Library "Timeouts, retries, and backoff with jitter", https://builder.aws.com/content/3EumjoZascWd1oZiEgL8ORlv3qE/timeouts-retries-and-backoff-with-jitter | 모든 원격 호출에 시간 제한. 계층마다 재시도하면 부하가 곱해짐(5계층×3회 = 243배 예시) → 한 지점에서 재시도. 지수 백오프에 상한, 지터로 분산. 부작용 있는 API는 멱등성이 없으면 재시도 안전하지 않음 | 2.4 |
| T7 | GitHub Docs "Validating webhook deliveries", https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries | `X-Hub-Signature-256: sha256=<hex>`, HMAC-SHA256, 본문과 비밀값으로 계산, `==` 대신 상수 시간 비교 | 2.6 |
| T8 | Stripe Docs "Manage webhook endpoints", https://docs.stripe.com/webhooks/signature | 원시 본문 그대로 검증해야 함(프레임워크의 파싱이 검증을 깨뜨림), `t=`·`v1=` 헤더, 같은 이벤트가 여러 번 올 수 있으니 이벤트 ID로 중복 제거, 2xx를 빨리 반환하고 무거운 처리는 큐로 | 2.6 |
| T9 | Python `hmac` 문서, https://docs.python.org/3/library/hmac.html | `compare_digest`는 타이밍 분석을 막도록 설계, 외부 digest 비교에 `==` 대신 권장 | 2.6 |
| T10 | Python `sqlite3` 문서, https://docs.python.org/3/library/sqlite3.html | 문자열 조립은 SQL 인젝션에 취약, `?` 자리표시자 사용. `with con:`은 성공 시 commit, 예외 시 rollback, 연결은 닫지 않음 | 3.1, 3.2 |
| T11 | SQLite "Transaction", https://www.sqlite.org/lang_transaction.html | 명시적 트랜잭션 밖의 문장은 자동 트랜잭션. BEGIN 기본은 DEFERRED, IMMEDIATE는 즉시 쓰기 잠금. BEGIN…COMMIT은 중첩 불가(SAVEPOINT 사용) | 3.2 |
| T12 | SQLite "UPSERT", https://www.sqlite.org/lang_upsert.html | `INSERT … ON CONFLICT(…) DO UPDATE` 구문(3.24.0 이상) | 3.4 |
| T13 | The Twelve-Factor App "Config", https://12factor.net/config | 설정 = 배포마다 달라지는 것, 환경 변수에 저장, "지금 공개해도 자격 증명이 새지 않는가" 시험 | 4.3 |
| T14 | Docker Docs "Dockerfile reference", https://docs.docker.com/reference/dockerfile/ | FROM·WORKDIR·COPY·RUN·CMD·USER 지시어 | 4.4 |
| T15 | GitHub Docs "Workflow syntax for GitHub Actions", https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax | `on`, `jobs.<id>.runs-on`, `steps[*].uses/run` | 4.4 |
| T16 | OpenTelemetry "Signals", https://opentelemetry.io/docs/concepts/signals/ | 신호: traces("요청이 애플리케이션을 지나는 경로"), metrics("실행 중 측정값"), logs("사건의 기록"), baggage | 5.1 |
| T17 | Google SRE Book "Monitoring Distributed Systems", https://sre.google/sre-book/monitoring-distributed-systems/ | 네 가지 황금 신호(지연·트래픽·오류·포화). 성공/실패 지연을 구분. 원인보다 증상에 경보 | 5.1, 5.3 |
| T18 | Google SRE Book "Postmortem Culture", https://sre.google/sre-book/postmortem-culture/ | 사후 검토 = 사고·영향·조치·근본 원인·후속 조치의 기록. 개인을 탓하지 않음. 작성 기준(사용자 영향, 데이터 손실, 온콜 개입 등)을 미리 정함 | 5.4 |
| T19 | OWASP API Security Top 10 2023, https://api-security.owasp.org/editions/2023/en/0x11-t10 (owasp.org 주소에서 308 이동) | API1:2023 Broken Object Level Authorization 등 10개 항목 | 5.5 |
| T20 | OWASP Top 10 for LLM Applications 2025, https://genai.owasp.org/llm-top-10/ , LLM01 https://genai.owasp.org/llmrisk/llm01-prompt-injection/ | LLM01 Prompt Injection(직접/간접), LLM05 Improper Output Handling, LLM06 Excessive Agency, LLM10 Unbounded Consumption. 완화: 동작 제한, 출력 형식 검증, 최소 권한, 고위험 행동은 사람 승인, 외부 콘텐츠 분리·표시, 적대적 테스트 | 6.5, 6.6 |
| T21 | Claude Docs "Tool use", https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview | 도구 정의 `name`·`description`·`input_schema`. 클라이언트 도구 호출 시 `stop_reason: "tool_use"`와 `tool_use` 블록(id, name, input). 실행 결과는 `tool_result`와 `tool_use_id`로 돌려보냄 | 6.2 |
| T22 | Claude Docs "Structured outputs", https://platform.claude.com/docs/en/build-with-claude/structured-outputs | `output_config.format`의 `type: "json_schema"`로 스키마에 맞는 JSON을 제약 디코딩. 수치·문자열 길이 제약 등 일부 JSON Schema 기능 미지원 | 6.1 |
| T23 | Model Context Protocol 명세 2026-07-28 판(latest), https://modelcontextprotocol.io/specification/2026-07-28 (처음 조사 때 연 2025-11-25 판에서 재개 시 최신판으로 교체) | JSON-RPC 2.0, 호스트·클라이언트·서버, 서버 기능 resources·prompts·tools, 클라이언트 기능 elicitation, 기본 프로토콜 "상태 없는 독립 요청·요청별 기능 협상", 도구는 임의 코드 실행이므로 사용자 동의·도구 설명 불신 | 6.2 |
| T24 | scikit-learn "Model evaluation", https://scikit-learn.org/stable/modules/model_evaluation.html | precision = tp/(tp+fp), recall = tp/(tp+fn), F1 = 2tp/(2tp+fp+fn) | 6.4, 8.3 |
| T25 | Michael Nygard "Documenting Architecture Decisions", https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions | ADR = 제목·맥락·결정·상태·결과 | 7.2 |
| T26 | Python `http.server`·`urllib.request`·`unittest`·`csv`·`logging` 공식 문서, https://docs.python.org/3/library/ | 표준 라이브러리만으로 예제 실행(외부 계정·유료 API 불필요). `http.server`는 운영용이 아님(문서 경고) | 2–8장 예제 |

## 4. 범위 결정

- 예제 언어: Python 3 표준 라이브러리(검증 환경 Python 3.15.0, SQLite 3.54.0). 설치 없이 실행되고 외부 계정이 필요 없다. 네트워크 예제는 같은 프로세스 안에서 `127.0.0.1`의 임시 포트로 서버를 띄워 외부 인터넷을 쓰지 않는다.
- 6장 LLM 예제는 유료 API 대신 결정적인 가짜 모델(규칙 기반 함수)로 루프·검증·평가 구조를 실행한다. 실제 API 요청 모양은 공식 문서(T21, T22)를 근거로 보여 주되 "실행하지 않은 참고 코드"로 표시한다.
- 6.3 검색 예제는 단어 빈도 벡터와 코사인 유사도로 만든다. 신경망 임베딩이 아니라는 점과, 실제 임베딩 모델로 바꿀 자리를 본문에 명시한다.
- Docker·GitHub Actions 파일은 문법 예시로 보여 준다. 이 세션에서 실제 컨테이너 빌드를 했는지는 QA 문서에 따로 기록한다.
- 비용 계산 예제는 실제 가격을 적지 않고 가격을 입력값으로 받는다(가격은 자주 바뀌므로 공식 가격표 확인을 안내).

## 5. 목차 확정(계획 초안 대비 보정)

1장 FDE 업무와 엔지니어링 사고(4절) · 2장 HTTP와 API 통합(6절) · 3장 데이터와 SQL(5절) · 4장 제품 구현과 전달(4절) · 5장 운영과 문제 해결(5절) · 6장 AI FDE(6절) · 7장 고객 커뮤니케이션과 설계 결정(3절) · 8장 종합 예제(3절). 총 36절.

보정: 계획의 "인증·권한"은 2.2(HTTP 의미)와 5.5(객체 수준 권한 검사)로 나눴다. 공고(R4, R5)가 보안·조달 관문을 명시하므로 5.5를 독립 절로 두었다.
