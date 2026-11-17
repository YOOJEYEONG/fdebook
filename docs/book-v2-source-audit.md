# FDE 기술 학습북 v2 — 공식 출처 조사·교육 검증 감사

- 작성: Opus 5.5 (자료 조사·교육 검증 담당). 집필·Exact 구현 담당 Opus와 별개 작업이지만 **같은 모델 계열이므로 독립 검토라고 주장하지 않는다.**
- 접근일: 모든 URL 2026-11-17 (KST). 아래 "확인 수준" 열로 본문을 실제로 대조했는지, 접속(HTTP 200)만 확인했는지 구분한다.
- 범위: `docs/book-v2-plan.md` 목차 1–8장에 필요한 주제와 공식 학습 출처. 소스 코드·다른 문서는 수정하지 않았다.
- 기존 `docs/research.md`와의 관계: 기존 조사는 채용 공고 URL 중심(Palantir/Anthropic London/Databricks DNB/Scale/채널톡 등)이었다. 이번 조사는 (a) 각사 ATS 공식 API에서 **현재 게시 중인 다른 공고**를 새로 확인하고, (b) 기술 사실은 공고가 아닌 **RFC·공식 문서**로만 확인했다.

---

## 1. 역할 정의: 회사 공식 직무 소개 (5개사)

### 1.1 확인 방법
각사 웹페이지는 봇 차단(403)이 많아 각사가 쓰는 채용 시스템의 **공개 공식 API**로 원문을 받았다. 회사가 직접 게시한 직무 설명이므로 "회사 공식 직무 소개"로 취급하되, 기술 사실의 근거로는 쓰지 않는다.

| 회사 | 직무(원문 제목) | 공식 URL | 확인 수준 |
|---|---|---|---|
| Palantir | Forward Deployed Software Engineer (Seoul) | https://jobs.lever.co/palantir/1bb19522-3936-4adc-9ced-c3df8b5900b9 | 본문 대조 (Lever API) |
| Palantir | Forward Deployed Software Engineer (London) | https://jobs.lever.co/palantir/5168e8fd-fec1-4fea-b7a1-81bdaea65850 | 본문 대조 |
| Palantir | Forward Deployed **AI** Engineer (New York) | https://jobs.lever.co/palantir/636fc05c-d348-4a06-be51-597cb9e07488 | 본문 대조 |
| OpenAI | Forward Deployed Engineer – Seoul (게시 2026-06-23) | https://jobs.ashbyhq.com/openai/b43339a1-e830-4761-a193-3438f34f9ebb | 본문 대조 (Ashby API) |
| Anthropic | Staff Forward Deployed Engineer (갱신 2026-10-14) | https://job-boards.greenhouse.io/anthropic/jobs/5449229008 | 본문 대조 (Greenhouse API) |
| Databricks | Forward Deployed Engineer (Seoul) | https://databricks.com/company/careers/open-positions/job?gh_jid=8540455002 | 본문 대조 |
| Databricks | AI Engineer – FDE (Seoul) | https://databricks.com/company/careers/open-positions/job?gh_jid=8574655002 | 본문 대조 |
| Cohere | Forward Deployed Engineer, Agentic Platform (Korea) | https://jobs.ashbyhq.com/cohere/031c2335-db85-4265-8a88-a54b911be36a | 본문 대조 |

확인 실패·사용 금지:
- Palantir 공식 블로그 "Dev versus Delta" (`blog.palantir.com/...`)는 403으로 열지 못했다. "one customer, many capabilities" 문구는 2차 자료로만 확인되므로 **본문에 Palantir 공식 인용으로 쓰지 말 것.**
- `openai.com/careers/...` 페이지는 403. 같은 공고의 Ashby 원문으로 대체했다.
- Salesforce Agentforce FDE는 제3자 게시판에서만 확인되어 표본에서 뺐다.

### 1.2 공통 FDE 역량 (5개사 공고에 반복 등장)
| 역량 | 근거(공고 원문 요지) | 교재 대응 장 |
|---|---|---|
| 고객 조직에 들어가 문제를 정의하고 범위를 정함 | OpenAI "own discovery, technical scoping, system design, build, and production rollout"; Anthropic "scope the work, sequence it… anticipate security and procurement gates" | 1, 7 |
| 프로토타입에서 **운영 가능한 시스템**까지 전달 | OpenAI "from first prototype to stable production"; Anthropic "hand over systems the customer can run" | 4, 5 |
| 풀스택·데이터 통합 엔지니어링 | Palantir "data structures, storage systems, cloud infrastructure, front-end frameworks"; Databricks "data ingestion… CI/CD for production deployments" | 2, 3, 4 |
| 보안·권한·개인정보 | Palantir London "secure coding practices, vulnerability management, access controls, permissions, and privacy"; Anthropic "identity and access, and compliance requirements" | 2, 3, 5 |
| 비기술 이해관계자와 소통, 트레이드오프 결정 | OpenAI "trade-offs between scope, speed, and quality"; Databricks "Documentation and white-boarding skills" | 7 |
| 현장 피드백을 제품·재사용 자산으로 환원 | OpenAI "Codify working patterns into tools, playbooks"; Databricks "Reusable Assets & Scale" | 7 |

### 1.3 AI FDE 특화 역량 (같은 회사의 일반/AI 공고를 나란히 비교)
가장 깨끗한 비교는 **같은 회사·같은 도시의 두 공고**다.
- Databricks Seoul: 일반 FDE는 Spark 내부, 클라우드 2종 이상, CI/CD, 데이터 아키텍처가 중심이고 AI는 "Working knowledge of MLOps, ML/AI models and AI APIs" 수준. AI FDE는 "RAG, multi-agent systems, Text2SQL, fine-tuning", "**evaluation and optimizations**", pandas/scikit-learn/PyTorch 데이터 과학 경험을 요구.
- Palantir: FDSE는 데이터·인프라·프런트엔드 중심. FD AI Engineer는 "Past experience building solutions with LLMs", "**Machine Learning basics (Evaluation, Training, Problem Decomposition)**"을 필수로 요구.
- OpenAI·Anthropic·Cohere는 회사 자체가 모델 기업이라 FDE 공고가 곧 AI FDE다: OpenAI "eval-driven feedback", "how model behaviour affects product experience"; Anthropic "Hands-on experience with LLMs and agents is expected" (동시에 "You don't need to have shipped agents to production"); Cohere "clear success criteria and evaluation methodologies", "reliable, observable, safe, and auditable".

교재 결론: **6장(AI FDE)의 핵심 차별점은 "LLM 호출법"이 아니라 "평가로 품질을 증명하는 능력"이다.** 5개사 중 AI 공고 전부가 평가(evaluation)를 명시했다. 1–5장 역량은 AI FDE에도 그대로 필요하다(Anthropic Staff 공고가 "building and operating production systems"을 먼저 요구).

### 1.4 해석 한계 (본문에 반드시 반영)
- 표본은 2026-11-17 시점 5개사 8개 공고다. **시장 전체, 한국 전체, 다른 시점으로 일반화하지 않는다.** 대부분 미국계 대기업·AI 모델 기업이며 경력 요구가 높다(OpenAI 5년+, Databricks 7년+, Anthropic Staff). Palantir London만 "6+ months" 수준.
- 공고 수가 많다는 사실은 취업 용이성을 뜻하지 않는다. 교재는 "이 책을 끝내면 FDE가 될 수 있다"는 식의 표현을 쓰지 않는다.
- 출장 비율(20–50%)·언어 요건(한/영)은 공고별로 다르다. 책에서 단일 수치로 요약하지 않는다.

---

## 2. 주제별 공식 학습 출처·핵심·함정

확인 수준: **본문** = 이번 세션에서 해당 내용을 열어 대조함. **접속** = HTTP 200만 확인, 집필자가 인용 전 해당 절을 직접 대조해야 함.

### 2.1 HTTP·API 통합 (2장)

| 주제 | 공식 출처 (URL) | 확인 | 가르칠 핵심 | 잘못 가르치기 쉬운 함정 |
|---|---|---|---|---|
| HTTP 의미론 | RFC 9110 HTTP Semantics https://www.rfc-editor.org/rfc/rfc9110 ; 입문 보조 MDN HTTP https://developer.mozilla.org/en-US/docs/Web/HTTP | 접속 | 메서드·상태 코드·헤더의 의미는 RFC 9110이 정의. 안전(safe)·멱등(idempotent) 메서드 구분(§9.2). 상태 코드 범주(§15) | RFC 7231/2616을 현행 표준으로 인용하는 오래된 자료. "PUT=수정, POST=생성"을 규칙처럼 가르치는 것(의미론은 멱등성 차이) |
| 429·재시도 신호 | RFC 6585(429) https://www.rfc-editor.org/rfc/rfc6585 ; RateLimit 헤더 초안 https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/ | 접속 | 429는 RFC 6585 정의, `Retry-After`는 RFC 9110 §10.2.3 | RateLimit 헤더를 확정 표준처럼 소개(아직 초안). 공급자별 헤더 이름을 표준이라 오해 |
| 오류 본문 형식 | RFC 9457 Problem Details https://www.rfc-editor.org/rfc/rfc9457 | 접속 | `application/problem+json`의 type/title/status/detail | RFC 7807을 현행으로 인용(9457이 대체) |
| JSON | RFC 8259 https://www.rfc-editor.org/rfc/rfc8259 | 접속 | 객체 이름 중복 시 동작 비정의, 큰 정수 정밀도 문제 | JSON 숫자를 항상 64비트 정수로 안전하다고 가정(JS에서 2^53 초과 손실) |
| 페이지네이션 | RFC 8288 Web Linking https://www.rfc-editor.org/rfc/rfc8288 ; GitHub REST pagination https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api | 접속 | `Link` 헤더 rel=next 따라가기, 커서 방식과 offset 방식 차이 | 페이지 번호를 직접 계산해 URL 조립(공급자는 `Link`를 따르라고 안내). offset 방식에서 데이터 변경 시 누락·중복 |
| 시간 제한·재시도·백오프 | AWS Builders' Library "Timeouts, retries, and backoff with jitter" https://builder.aws.com/content/3EumjoZascWd1oZiEgL8ORlv3qE/timeouts-retries-and-backoff-with-jitter (구 URL은 301 이동) | 본문 | 모든 원격 호출에 시간 제한. 지수 백오프+상한+지터. **재시도는 한 계층에서만**(3회×5계층 = 243배 부하 예시). 부작용 있는 호출은 API가 멱등일 때만 재시도. 토큰 버킷으로 재시도 제한 | 페이지에 "의견은 저자 개인의 것" 표기가 있음 → "AWS 공식 표준"이라 쓰지 말고 "AWS가 게시한 엔지니어링 글"로 표기. 지터 없는 고정 간격 재시도 예제. 4xx(400/401/403/422)까지 재시도 |
| CORS | MDN CORS https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS | 접속 | 브라우저가 강제하는 정책이며 서버 간 호출엔 적용되지 않음 | CORS를 인증·보안 장치로 설명. `curl`은 되는데 브라우저는 안 되는 이유를 서버 버그로 진단 |

### 2.2 인증·권한·OAuth (2장)

| 주제 | 공식 출처 | 확인 | 가르칠 핵심 | 함정 |
|---|---|---|---|---|
| OAuth 2.0 기본 | RFC 6749 https://www.rfc-editor.org/rfc/rfc6749 ; Bearer RFC 6750 https://www.rfc-editor.org/rfc/rfc6750 | 접속 | 역할 4개(리소스 소유자·클라이언트·인가 서버·리소스 서버), authorization code 흐름, client credentials(서버 간) | OAuth를 "로그인 프로토콜"로 소개(인가 위임이다. 신원 확인은 OpenID Connect 영역) |
| 현행 보안 권고 | **RFC 9700 (BCP 240, 2025-01) OAuth 2.0 Security BCP** https://www.rfc-editor.org/rfc/rfc9700 | 본문 | implicit grant 피함(§2.1.2), password grant 사용 금지(§2.4), 공개 클라이언트 PKCE 필수(§2.1.1), redirect URI 정확 일치(§2.1·§4.1.3), 공개 클라이언트 refresh token은 sender-constrained 또는 rotation(§2.2.2), 액세스 토큰 audience 제한(§2.3), **토큰을 URL 쿼리에 넣지 말 것(§4.3.2)** | 2019년 이전 튜토리얼의 implicit/password grant 예제 그대로 사용 |
| PKCE | RFC 7636 https://www.rfc-editor.org/rfc/rfc7636 | 접속 | code_verifier/code_challenge(S256) | `plain` 방식을 기본으로 예시 |
| OAuth 2.1 | draft-ietf-oauth-v2-1 https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/ | 본문 | 2026-10-30 갱신된 **-17 초안**, RFC 아님 | "OAuth 2.1 표준"이라 단정. 본문 근거는 RFC 9700으로 한다 |
| JWT | RFC 7519 https://www.rfc-editor.org/rfc/rfc7519 ; JWT BCP RFC 8725 https://www.rfc-editor.org/rfc/rfc8725 | 접속 | 서명 검증은 허용 알고리즘 고정, `aud`/`iss`/`exp` 검증 | JWT를 암호화된 것으로 설명(기본은 서명만, 내용은 Base64URL로 누구나 읽음). `alg: none` 허용 |

### 2.3 멱등성·웹훅 서명 (2장)

| 주제 | 공식 출처 | 확인 | 가르칠 핵심 | 함정 |
|---|---|---|---|---|
| 멱등성 개념 | RFC 9110 §9.2.2 (위 URL) | 접속 | 같은 요청 N번 = 1번의 의도된 효과. GET/PUT/DELETE는 정의상 멱등, POST는 아님 | "멱등 = 응답이 같다"로 설명(효과가 같다는 뜻. 두 번째 DELETE가 404여도 멱등) |
| Idempotency-Key 헤더 | IETF 초안 draft-ietf-httpapi-idempotency-key-header-08 https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/ | 본문 | 2026-10-22 갱신, **RFC 아닌 초안**. 같은 키·다른 본문 → 422 권고, 원 요청 처리 중 재요청 → 409 권고, 키 필수인데 누락 → 400 권고. 값은 UUID 권장. 선택적 본문 지문(fingerprint) | 표준 확정처럼 서술. 키만 저장하고 본문 비교를 생략(다른 요청이 같은 키로 성공 처리됨). 처리 중 상태를 저장하지 않아 동시 중복 실행 |
| 사례 구현 | Stripe Idempotent requests https://docs.stripe.com/api/idempotent_requests | 접속 | 공급자 구현 사례로만 사용 | Stripe 규칙(보존 기간 등)을 일반 규칙으로 일반화 |
| HMAC | RFC 2104 https://www.rfc-editor.org/rfc/rfc2104 | 접속 | 공유 비밀 + 해시 = 무결성·출처 검증 | HMAC을 암호화로 설명 |
| GitHub 웹훅 검증 | https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries | 본문 | 헤더 `X-Hub-Signature-256: sha256=<hex>`, HMAC-SHA256, **원본 payload**에 대해 계산, `==` 대신 상수 시간 비교, UTF-8 처리. 공식 테스트 벡터: 비밀 `It's a Secret to Everybody`, 본문 `Hello, World!` → `757107ea0eb2509fc211221cce984b8a37570b6d7586c22c46f4379c8b043e17` (**로컬 Python 3.15 `hmac`로 재계산 일치 확인**) | SHA-1 `X-Hub-Signature`를 예시로 사용(레거시). JSON 파싱 후 재직렬화한 문자열로 서명 계산 |
| Stripe 웹훅 | https://docs.stripe.com/events/set-up-events.md , https://docs.stripe.com/events/manage-webhook-endpoints.md (구 `/webhooks/signature`는 여기로 이동) | 본문 | `Stripe-Signature` 헤더, **raw body** 필수(Express에서 `express.json()`이 먼저 돌면 실패), 비밀 교체 시 최대 7일 동안 서명 여러 개, 중복 이벤트는 event ID로 거름, 빠르게 2xx 반환 후 비동기 처리, 3xx는 실패로 간주, 헤더 항목 순서·개수에 의존 금지 | 기본 타임스탬프 허용 시간 수치를 이번에 문서에서 **확인하지 못함** → 숫자를 쓰려면 SDK 소스로 대조. 헤더의 `payload=`·`secret=` 디버그 항목을 검증에 사용(서명 안 됨) |
| 공급자 중립 규격 | Standard Webhooks spec https://github.com/standard-webhooks/standard-webhooks/blob/main/spec/standard-webhooks.md | 본문 | `webhook-id`/`webhook-timestamp`/`webhook-signature`, 서명 대상 `id.timestamp.payload`, `v1,<base64>` 형식, 공백 구분 다중 서명(비밀 교체), 타임스탬프 허용 범위로 재전송 공격 방지(구체 수치는 규격이 정하지 않음), `webhook-id`를 멱등 키로 사용, 비-2xx는 실패, 410이면 전송 중단 | 업계 규격이지 IETF 표준이 아님을 명시. GitHub(hex)와 Standard Webhooks(base64) 인코딩 혼동 |

### 2.4 데이터·SQL·트랜잭션·ETL·개인정보 (3장)

| 주제 | 공식 출처 | 확인 | 가르칠 핵심 | 함정 |
|---|---|---|---|---|
| 트랜잭션 입문 | PostgreSQL 18 Tutorial: Transactions https://www.postgresql.org/docs/current/tutorial-transactions.html | 접속 | 원자성, BEGIN/COMMIT/ROLLBACK, savepoint | — |
| 격리 수준 | PostgreSQL 18 Transaction Isolation https://www.postgresql.org/docs/current/transaction-iso.html | 본문 | 기본은 **Read Committed**. Read Uncommitted는 Read Committed처럼 동작(dirty read 없음). Repeatable Read/Serializable은 SQLSTATE `40001` 직렬화 실패 **재시도를 애플리케이션이 준비해야 함** | 다른 DB의 기본값을 일반화. Serializable이면 재시도 불필요하다고 설명 |
| 로컬 DB | SQLite Isolation https://www.sqlite.org/isolation.html ; Transaction https://www.sqlite.org/lang_transaction.html ; NULL 처리 https://www.sqlite.org/nulls.html | 본문(isolation) | 기본 직렬화, 쓰기 1개. WAL 모드는 스냅샷 격리. 읽기→쓰기 승격 실패(SQLITE_BUSY_SNAPSHOT)는 `BEGIN IMMEDIATE`로 회피 | 같은 연결 안에서 격리를 기대(같은 연결엔 격리 없음) |
| Python sqlite3 | https://docs.python.org/3/library/sqlite3.html | 본문 | Python 3.12에 `autocommit` 추가. **기본값은 아직 `LEGACY_TRANSACTION_CONTROL`**이고 향후 `False`로 바뀔 예정. 레거시 모드는 INSERT/UPDATE/DELETE/REPLACE 앞에 암묵적 BEGIN. `with con:`은 커밋/롤백만 하고 **연결을 닫지 않음**. `?`/`:name` 자리표시자 사용 | 3.11 이하 자료 그대로 사용. `with con:`이 close한다고 설명. f-string으로 SQL 조립 |
| SQL 주입 | OWASP SQL Injection Prevention Cheat Sheet https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html | 접속 | 매개변수화 쿼리가 1차 방어. 식별자(테이블·열 이름)는 바인딩 불가 → 허용 목록 | 따옴표 이스케이프를 방어책으로 가르침 |
| 결측·정제 | pandas Missing data https://pandas.pydata.org/docs/user_guide/missing_data.html | 접속 | `NaN`/`None`/`NA` 차이, 결측 비교 결과 | 결측을 0이나 빈 문자열로 일괄 치환 |
| 품질 검사 | dbt data tests https://docs.getdbt.com/docs/build/data-tests | 접속 | unique/not_null/accepted_values/relationships 같은 선언적 검사 = "실패 행을 찾는 쿼리" | 특정 도구 사용법을 ETL 원리로 혼동. 교재 본문은 도구 없이 SQL로 같은 검사를 먼저 보여 줄 것 |
| 개인정보 최소화 | 개인정보 보호법(시행 2026-09-11, 법률 제21445호) https://www.law.go.kr/법령/개인정보보호법 ; GDPR Art.5(1)(c) https://eur-lex.europa.eu/eli/reg/2016/679/oj | 접속(시행일만 본문) | 목적에 필요한 최소 수집, 가명·익명 처리, 합성 데이터 사용 | **제3조·제16조 조문 원문을 이번 세션에서 대조하지 못함** → 조문 번호·문구 인용 전 국가법령정보센터 원문 대조 필수. 법률 자문처럼 서술 금지 |

### 2.5 제품 구현·전달: Docker·CI/CD·설정 (4장)

| 주제 | 공식 출처 | 확인 | 가르칠 핵심 | 함정 |
|---|---|---|---|---|
| Docker 입문 | Docker Get started https://docs.docker.com/get-started/ ; Best practices https://docs.docker.com/build/building/best-practices/ ; Multi-stage https://docs.docker.com/build/building/multi-stage/ | 접속 | 이미지 vs 컨테이너, 레이어 캐시 순서, 멀티 스테이지로 런타임 이미지 축소 | 컨테이너 안 `localhost`가 호스트라고 설명 |
| 빌드 비밀값 | Docker Build secrets https://docs.docker.com/build/building/secrets/ | 본문 | build arg·ENV는 **최종 이미지에 남음**. `docker build --secret id=...,src=...` + `RUN --mount=type=secret,id=...` (기본 `/run/secrets/<id>`) | `ARG API_KEY`로 비밀 전달 예제 |
| CI 보안 | GitHub Actions Secure use https://docs.github.com/en/actions/reference/security/secure-use ; 개요 https://docs.github.com/en/actions | 본문 | 비신뢰 입력(PR 제목 등)을 `run`에 직접 보간하지 말고 env 변수로 전달. `GITHUB_TOKEN` 기본 읽기 전용, 잡 단위로 승격. 서드파티 액션은 **전체 커밋 SHA로 고정**. `pull_request_target`·`workflow_run`에서 비신뢰 PR 코드 체크아웃 금지. 클라우드 자격 증명은 OIDC 단기 토큰. 구조화 데이터(JSON) 안 비밀은 마스킹 보장 안 됨 | `@v4` 태그 고정을 안전하다고 설명. 마스킹을 비밀 보호 수단으로 신뢰 |
| 설정·비밀 분리 | The Twelve-Factor App: Config https://12factor.net/config ; OWASP Secrets Management Cheat Sheet https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html | 접속 | 코드와 설정 분리, 비밀은 저장소에 두지 않음 | 12-Factor를 표준으로 표기(커뮤니티 방법론). 환경 변수 = 안전한 비밀 저장소로 설명(Stripe 문서도 "vault 우선, 없으면 env") |
| 전달 성과 지표 | DORA metrics https://dora.dev/guides/dora-metrics/ | 접속 | 배포 빈도·변경 리드타임·변경 실패율·복구 시간 | 지표 정의가 개정되므로 집필 시점 페이지로 재대조 |

### 2.6 운영: 관측·SLO·장애 대응 (5장)

| 주제 | 공식 출처 | 확인 | 가르칠 핵심 | 함정 |
|---|---|---|---|---|
| 관측 개념 | OpenTelemetry Observability primer https://opentelemetry.io/docs/concepts/observability-primer/ ; Signals https://opentelemetry.io/docs/concepts/signals/ | 본문(signals) | 안정 신호: traces·metrics·logs·baggage. events·profiles는 개발/제안 단계 | profiles를 안정 기능으로 소개 |
| 분산 추적 전파 | W3C Trace Context https://www.w3.org/TR/trace-context/ | 접속 | `traceparent` 헤더로 서비스 간 trace 연결 | 서비스마다 자체 요청 ID만 쓰고 연결 안 함 |
| 지연 분포 | Prometheus Histograms and summaries https://prometheus.io/docs/practices/histograms/ | 본문 | summary 분위수는 인스턴스 간 **평균·합산 불가**("statistically nonsensical"). 서비스 전체 p95는 histogram + `histogram_quantile(0.95, sum by (le) (rate(...[5m])))`. classic histogram 오차는 버킷 폭에 좌우 | 인스턴스별 p99를 평균 내서 전체 p99라 함. 평균 지연만으로 SLO 판단 |
| SLI/SLO/SLA | Google SRE Book ch.4 https://sre.google/sre-book/service-level-objectives/ ; Workbook Implementing SLOs https://sre.google/workbook/implementing-slos/ | 본문(ch.4) | SLI=측정값, SLO=목표, SLA=결과(보상)가 있는 계약. 평균보다 백분위. 100% 목표 금지 → 오류 예산. SLO는 적게, 현재 성능을 목표로 삼지 말 것 | SLA와 SLO 혼용. "99.9% = 하루 1분 다운"식 잘못된 환산(99.9%/30일 ≈ 43.2분, 직접 계산해 보여 줄 것) |
| 장애 대응·회고 | SRE Book Managing incidents https://sre.google/sre-book/managing-incidents/ ; Postmortem culture https://sre.google/sre-book/postmortem-culture/ | 접속 | 역할 분리(지휘·운영·소통), 비난 없는 회고 | 회고를 책임자 지목 문서로 작성 |

### 2.7 보안·위협 모델 (5장)

| 주제 | 공식 출처 | 확인 | 가르칠 핵심 | 함정 |
|---|---|---|---|---|
| 웹 위험 분류 | OWASP Top 10:2025 https://top10.owasp.org/2025 (구 `owasp.org/Top10/2025/`는 308 이동) | 본문 | A01 Broken Access Control, A02 Security Misconfiguration, A03 Software Supply Chain Failures, A04 Cryptographic Failures, A05 Injection, A06 Insecure Design, A07 Authentication Failures, A08 Software or Data Integrity Failures, A09 Security Logging and Alerting Failures, A10 Mishandling of Exceptional Conditions | 2021판 순위(A03 Injection 등) 인용. Top 10을 체크리스트·표준 준수 기준으로 설명(인식 제고 문서) |
| API 위험 | OWASP API Security Top 10 2023 https://owasp.org/API-Security/editions/2023/en/0x11-t10/ | 접속 | BOLA(객체 수준 권한) — 고객 데이터 통합에서 가장 흔한 실수: ID만 바꿔 남의 레코드 조회 | 인증 성공 = 권한 있음으로 처리 |
| 위협 모델링 | OWASP Threat Modeling Cheat Sheet https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html | 접속 | 무엇을 만드나/무엇이 잘못될 수 있나/어떻게 대응/잘했나 4질문, 신뢰 경계 | 도구·양식 작성 자체를 목표로 함 |
| 보안 개발 수명주기 | NIST SP 800-218 SSDF https://csrc.nist.gov/pubs/sp/800/218/final | 접속 | 조직 수준 실천 목록. 교재에선 참고 수준 | 개인 학습 체크리스트로 축소 |

### 2.8 AI FDE: LLM·구조화 출력·도구 호출·RAG·MCP (6장)

| 주제 | 공식 출처 | 확인 | 가르칠 핵심 | 함정 |
|---|---|---|---|---|
| 도구 호출 루프 | Claude Tool use overview https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview ; OpenAI Function calling https://platform.openai.com/docs/guides/function-calling | 본문(Claude) | **클라이언트 도구는 내 코드가 실행**, 서버 도구는 공급자가 실행. 응답 `stop_reason: "tool_use"` + `tool_use` 블록 → 내가 실행 → `tool_result`(`tool_use_id` 일치)로 반환 → 최종 답. 필수 인자가 없으면 모델이 값을 추측할 수 있음(문서 명시). `tools` 정의도 입력 토큰 비용 | "모델이 API를 직접 호출한다"는 설명. 모델이 만든 인자를 검증 없이 실행. 특정 SDK 버전 필드를 영구 규칙처럼 서술 |
| 구조화 출력 | Claude Structured outputs https://platform.claude.com/docs/en/build-with-claude/structured-outputs | 본문 | `output_config.format`(JSON schema)와 `strict: true` 도구. 제약 디코딩으로 스키마 준수. **예외: `stop_reason: "refusal"`, `"max_tokens"`일 때 스키마 불일치 가능. enum 대소문자 미보장.** 미지원: 재귀 스키마, `minimum`/`maxLength` 등 수치·문자열 제약. `additionalProperties: false` 필수. 구 `output_format` 파라미터는 deprecated | "스키마 준수 = 값이 정확함"으로 설명(형식만 보장, 내용 정확성은 평가로 확인). 응답 파싱 전 `stop_reason` 확인 생략 |
| 임베딩·검색 | Claude Embeddings https://platform.claude.com/docs/en/build-with-claude/embeddings ; RAG 원 논문 Lewis et al. 2020 https://arxiv.org/abs/2005.11401 | 본문(임베딩) | Anthropic은 자체 임베딩 모델 없음, Voyage AI(MongoDB) 안내. 쿼리/문서 `input_type` 구분. 정규화된 벡터에선 내적=코사인 | 특정 벡터 DB를 RAG 필수 요소로 설명. 임베딩 유사도 = 사실 정확성. 교재 기본 예제가 유료 API를 요구(계획서 위반) → **로컬 대안: 키워드/BM25 또는 TF-IDF 검색으로 같은 평가 루프를 먼저 구현** |
| MCP | MCP Specification (latest = **2026-07-28**) https://modelcontextprotocol.io/specification/latest | 본문 | JSON-RPC 2.0, host/client/server. 서버 기능: resources·prompts·tools. 클라이언트 기능: elicitation. **최신 판은 "Stateless, self-contained requests", "Per-request capability negotiation", `server/discover`.** 도구 = 임의 코드 실행, 도구 설명(annotation)은 신뢰할 수 없는 입력, 호출 전 사용자 동의 | 2024–2025 튜토리얼의 세션·initialize 중심 설명을 현행처럼 서술. **본문에 사용하는 판(revision) 날짜를 고정 표기할 것** |
| 비용·지연 | Claude Tool use overview(가격 절) 위 URL | 본문 | 비용 = 입력 토큰(도구 정의 포함) + 출력 토큰 + 서버 도구 별도 과금 | 가격·모델 ID를 본문에 하드코딩(변동). 접근일과 함께 "집필 시점" 표기 |

### 2.9 평가·정밀도·재현율 (6장)

| 주제 | 공식 출처 | 확인 | 가르칠 핵심 | 함정 |
|---|---|---|---|---|
| 지표 정의 | Google ML Crash Course: Accuracy, recall, precision https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall ; scikit-learn Model evaluation https://scikit-learn.org/stable/modules/model_evaluation.html | 본문(Google) | Accuracy=(TP+TN)/전체, Recall=TP/(TP+FN), Precision=TP/(TP+FP), FPR=FP/(FP+TN). 불균형 데이터에서 accuracy 오도(1% 양성이면 항상 음성 예측이 99%). 양성 예측 0건이면 precision 정의 불가(NaN) — 완벽하다는 뜻 아님. 임계값 이동 시 trade-off | 정밀도·재현율 분모 뒤바꿈. NaN precision을 1.0으로 처리. 다중 클래스에서 macro/micro 차이 설명 누락 |
| 검색 평가 | Manning et al. *Introduction to Information Retrieval* (Stanford NLP) — `nlp.stanford.edu/IR-book/` | **접속 실패(타임아웃)** | 집합 기반 precision/recall, precision@k | 재접속 확인 전 인용 금지 |
| LLM 평가 설계 | Claude "Define success criteria and build evaluations" https://platform.claude.com/docs/en/test-and-evaluate/develop-tests ; OpenAI Evals guide https://platform.openai.com/docs/guides/evals | 본문(Claude) | 성공 기준은 구체·측정 가능·달성 가능·관련성. 실제 입력 분포 + 가장자리 사례(빈 입력, 긴 입력, 모호·유해 입력). 자동 채점 우선(정확 일치, 코드 검사, LLM 채점). LLM 채점은 다른 모델·제한된 출력("yes/no만")·평가 대상을 태그로 분리 | 데모 몇 건으로 "잘 된다" 결론. LLM 채점자를 검증 없이 정답 취급. 평가셋으로 프롬프트를 조정한 뒤 같은 셋으로 성능 보고(과적합) |
| 위험 관리 틀 | NIST AI RMF https://www.nist.gov/itl/ai-risk-management-framework ; NIST AI 600-1 GenAI Profile https://doi.org/10.6028/NIST.AI.600-1 | 접속 | 참고 수준(조직 거버넌스) | 규제 준수 요건처럼 서술 |

### 2.10 프롬프트 인젝션 (6장)

| 주제 | 공식 출처 | 확인 | 가르칠 핵심 | 함정 |
|---|---|---|---|---|
| 위험 정의 | OWASP Top 10 for LLM Applications 2025, LLM01 https://genai.owasp.org/llmrisk/llm01-prompt-injection/ | 본문 | 직접 주입 vs **간접 주입**(검색 문서·웹페이지·파일 안 지시문). 대응 7가지: 시스템 프롬프트로 제한, 결정적 코드로 출력 형식 검증, 입출력 필터, 최소 권한·특권 기능은 코드에서 처리, 고위험 행동 사람 승인, 비신뢰 콘텐츠 분리·표시, 적대적 테스트. RAG·파인튜닝으로 완전 해결 안 됨, 확실한 방지법 없음 | "시스템 프롬프트에 '무시하지 마'라고 쓰면 막힌다" |
| 설계 관점 | UK NCSC "Prompt injection is not SQL injection" (2025-12-08) https://www.ncsc.gov.uk/blog-post/prompt-injection-is-not-sql-injection | 본문 | SQL 주입은 매개변수화로 데이터/명령을 분리할 수 있지만 LLM엔 그런 경계가 없음 → "혼동 가능한 대리인"으로 취급, **영향 축소**가 목표. LLM 권한을 처리하는 콘텐츠 중 가장 신뢰 낮은 주체 수준으로 제한. deny-list 지양. "막아 준다"는 제품 주장 경계. 입력·출력·도구 호출 로그 | SQL 주입과 같은 방식으로 "해결"된다고 설명. 키워드 차단 목록을 주 방어로 제시 |
| 실무 점검 | OWASP LLM Prompt Injection Prevention Cheat Sheet https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html ; NIST AI 100-2 E2025 https://csrc.nist.gov/pubs/ai/100/2/e2025/final ; Claude Mitigate jailbreaks https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks | 접속 | 보조 자료 | — |

### 2.11 고객 커뮤니케이션·설계 결정 (1장, 7장)

기술 표준이 없는 영역이다. 공식 문서는 "형식"의 근거로만 쓰고, 본문은 분석 사례·좋은/나쁜 예로 가르친다(계획서의 억지 코드 금지 원칙).

| 주제 | 공식 출처 | 확인 | 가르칠 핵심 | 함정 |
|---|---|---|---|---|
| 설계 결정 기록 | Microsoft Azure Well-Architected "Maintain an ADR" https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record (2026-04-10) ; Nygard 원문 https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions ; https://adr.github.io/ | 본문(Microsoft) | 구조·품질 속성·되돌리기 어려운 결정만 기록. 문제·맥락, 검토한 대안, 결정, 트레이드오프, **확신도**, 상태(Proposed/Accepted/Superseded). **추가 전용(append-only)**: 승인된 기록을 고치지 말고 새 기록으로 대체·연결 | 모든 결정을 ADR로 씀. 기각한 대안 생략. 기존 ADR을 덮어씀 |
| 성공 지표·범위 | Claude develop-tests(성공 기준 절) 위 URL | 본문 | 구체·측정 가능한 성공 기준을 먼저 합의 | "고객 만족" 같은 측정 불가 목표 |
| 기술 문서 쓰기 | Google Technical Writing courses https://developers.google.com/tech-writing | 접속 | 독자 정의, 짧은 문장, 목록·표 | — |
| 효과·한계 보고, 회고 | SRE Postmortem culture 위 URL | 접속 | 사실·영향·원인·조치, 비난 없음 | 성과만 보고하고 한계·잔여 위험 누락 |
| 역할 맥락(사실 아님) | OpenAI Seoul FDE 공고 위 URL | 본문 | 공고가 요구하는 행동("trade-offs between scope, speed, and quality", "Communicate clearly with… customer stakeholders")을 **장 도입 동기**로만 사용 | 공고 문구를 커뮤니케이션 "방법론"의 근거로 사용 |

---

## 3. 이번 세션 로컬 실행 검증 (집필 예제 후보)

환경: macOS, Python 3.15.0, SQLite 3.54.0. 스크립트는 `/tmp/fdeaudit/scripts/traps.py`(저장소 밖, 저장소 미수정). 출력 원문:

```text
NULL = NULL -> [(None,)]
region != 'kr' rows -> [('C',)]
COUNT(*), COUNT(region) -> [(3, 2)]
LEFT JOIN + WHERE -> [('A', 10)]
LEFT JOIN + ON   -> [('A', 10), ('B', None), ('C', None)]
rollback: UNIQUE constraint failed: ticket.id -> count [(3,)]
precision=0.667 recall=0.667 accuracy=0.80
always-negative accuracy = 0.7
```

교육적으로 중요한 관찰:
1. `region != 'kr'`이 region이 NULL인 B를 **빠뜨린다**(NULL 비교는 UNKNOWN). 결측 처리 절의 핵심 예제로 적합.
2. `LEFT JOIN` 후 `WHERE t.status='open'`은 사실상 INNER JOIN이 된다. 조건을 `ON`으로 옮기면 고객 3명이 모두 남는다.
3. **실제로 겪은 함정:** `sqlite3.connect(..., autocommit=False)`에서 `executescript()`로 테이블을 만든 뒤 `commit()`을 빼먹자, 이후 `with con:` 블록의 롤백이 **테이블 생성까지 되돌려** `no such table: ticket`이 났다. 3.12+ `autocommit=False`는 "항상 트랜잭션이 열려 있음"을 체감시키는 좋은 디버깅 사례다. 교재 예제에서 설정 후 `con.commit()`을 명시하고, 이 오류를 "흔한 오류" 절에 넣을 것.
4. 10건 중 양성 3건 데이터에서 "항상 음성" 모델의 accuracy가 0.7 → accuracy만 보고하면 안 되는 이유를 숫자로 보여 줌.
5. GitHub 웹훅 테스트 벡터 HMAC 재계산 일치(§2.3).

---

## 4. 교재 품질 기준 (집필·검증 공통 체크리스트)

계획서 "절별 필수 구성" 7요소에 더해, 아래를 통과해야 "교재 본문"으로 인정한다.

### 4.1 설명
- 첫 등장 용어는 한국어 풀이 + 원어 병기(예: 멱등성(idempotency)). 약어는 처음 한 번 풀어 쓴다.
- "무엇"보다 **"왜 필요한가 → 없으면 어떤 사고가 나는가"** 순서. 예: 멱등성은 "타임아웃 후 재시도가 결제를 두 번 만든다"는 사고로 시작.
- 표준 문서 번호·절을 한 번 제시하되 원문을 번역 복제하지 않는다.
- 초안(Internet-Draft)·커뮤니티 규격·공급자 문서를 구분해 표기한다(본 문서 §2의 RateLimit, Idempotency-Key, OAuth 2.1, Standard Webhooks, 12-Factor).
- 변동성 높은 값(모델 ID, 가격, SDK 필드, MCP 판)은 "집필 시점 2026-11, 접근일" 표기 후 원문 링크.

### 4.2 예제
- 모든 코드 예제는 표준 라이브러리 또는 로컬 도구만으로 실행 가능해야 한다(Python `http.server`·`sqlite3`·`hmac`, 로컬 Docker). 유료 API 예제는 선택 심화로 분리하고 준비물·비용을 적는다.
- 각 예제: 실행 명령, **실제 실행한 출력**(위 §3처럼), 실행 환경 버전. 실행하지 않은 예제는 "미검증" 표시.
- 실패 경로를 반드시 하나 포함한다(서명 불일치, 중복 키, 롤백, 429). 성공 경로만 있는 예제는 FDE 교재로 부족하다.
- 무작위성(지터, LLM 출력)이 있는 예제는 시드 고정 또는 "출력 예시"로 표기하고 판정 기준을 따로 둔다.

### 4.3 연습문제·해설
- 절마다 2문제 이상: (1) 개념 판별 1개 (2) 상황 판단·디버깅 1개. "정의를 쓰시오"만 있는 문제는 불인정.
- 해설은 정답 + **왜 오답이 그럴듯한지** + 근거 출처 절. 예: "두 번째 DELETE가 404인데 멱등인가?" → 멱등은 상태 효과 기준(RFC 9110 §9.2.2).
- 해설은 접힌 상태로 제공(계획서 UX와 일치).

### 4.4 출처 표기
- 절 끝 "공식 학습 출처": 문서명, URL, 접근일, 해당 절 번호. 채용 공고는 1·6·7장 도입 동기에서만, 기술 근거로는 금지.
- 주장·출처 대응표(계획서 요구)는 이 문서 §2를 시작점으로 사용하되, "접속"만 확인된 행은 집필자가 인용 전 본문 대조.

---

## 5. 초보자(개발 기초를 아는 FDE 전환자)가 막힐 선수 개념

장 시작 "선수 개념" 상자에 넣고, 부족하면 짧은 보충 절을 둔다.

| 장 | 막히기 쉬운 선수 개념 | 왜 막히나 / 보충 방법 |
|---|---|---|
| 2 | TCP 연결·DNS·TLS가 HTTP 아래에 있다는 그림 | 타임아웃 종류(연결 vs 읽기)를 구분 못함 → 그림 1장 |
| 2 | 바이트 vs 문자열, UTF-8, Base64 vs hex | 웹훅 서명 실패의 1순위 원인(raw body) → 같은 JSON의 재직렬화 전후 바이트 비교 실습 |
| 2 | 해시 vs HMAC vs 암호화 vs 서명 | 4개를 혼동 → 비교표 |
| 2 | 동시성(같은 요청 두 개가 동시에 도착) | 멱등 키의 "처리 중" 상태 필요성을 이해 못함 → 두 스레드 실습 |
| 2 | 리다이렉트·브라우저 vs 서버 호출 | OAuth 흐름과 CORS 오해 → 시퀀스 다이어그램 |
| 3 | NULL 3값 논리, 조인 종류 | §3 실행 예제 1·2 |
| 3 | 트랜잭션 경계와 자동 커밋 | §3 실행 예제 3 |
| 4 | 프로세스·포트·환경 변수, 파일 권한 | 컨테이너 네트워킹 오해 → `localhost` vs 서비스 이름 |
| 4 | Git 브랜치·PR·커밋 SHA | 액션 SHA 고정 이유 이해 불가 |
| 5 | 백분위수, 분포, 비율 계산 | p99 평균 오류, SLO 분 환산 → 직접 계산 문제 |
| 6 | 토큰, 컨텍스트 창, 확률적 출력 | "같은 입력 = 같은 출력" 기대 → 반복 실행 결과 비교 |
| 6 | 벡터·내적·코사인 유사도 | 2차원 손계산 예제 |
| 6 | 혼동 행렬(TP/FP/FN/TN), 임계값 | §3 실행 예제 4, 표로 채우기 연습 |
| 6 | JSON Schema 기초 | 구조화 출력·도구 정의 읽기 불가 → 최소 스키마 3개 |
| 7 | 이해관계자 구분(사용자·구매자·보안 담당·운영자) | 같은 데모를 모두에게 같은 방식으로 설명 → 청중별 좋은/나쁜 예 |

---

## 6. 계획서 목차에 대한 보정 제안

1. **6장 비중 재배치:** 공고 비교상 AI FDE의 차별점은 평가다. "평가셋·지표·회귀 확인"을 6장 중앙에 두고, LLM 호출·도구 호출은 평가 대상을 만드는 수단으로 배치.
2. **2장에 "재시도는 한 계층에서만"과 "멱등 키 처리 중 상태"를 독립 소절로.** 웹훅(수신 측 중복 처리)과 멱등 키(송신 측 재시도)를 한 쌍으로 가르치면 이해가 빠르다.
3. **3장 SQL 예제는 SQLite+Python 표준 라이브러리로 통일**, PostgreSQL 차이는 격리 수준·`40001` 재시도 박스로만.
4. **5장 보안은 OWASP Top 10:2025 + API Top 10의 BOLA + 6장 프롬프트 인젝션을 "권한 경계" 한 축으로 연결.** NCSC의 "최소 신뢰 주체 수준 권한" 원칙이 일반 보안(최소 권한)과 AI 보안을 잇는다.
5. **6장 RAG 기본 예제는 로컬 검색**(키워드/TF-IDF)으로, 임베딩 API는 선택 심화. 계획서의 "유료 API 필수 금지" 충족.
6. **MCP는 판 날짜(2026-07-28)를 고정**하고 구판과 달라진 점(무상태 요청, 요청별 기능 협상)을 한 줄 주석.
7. 1장 역할 소개는 §1.4 해석 한계 문단을 그대로 포함.

## 7. 미확인·후속 확인 필요 항목

| 항목 | 상태 | 조치 |
|---|---|---|
| Palantir "Dev versus Delta" 블로그 | 403 | 사용 금지 또는 브라우저로 원문 확인 후 사용 |
| Stripe 서명 기본 타임스탬프 허용 시간 | 문서에서 수치 미발견 | 숫자 쓰지 않거나 공식 SDK 소스로 대조 |
| 개인정보 보호법 제3조·제16조 조문 | 시행일만 확인 | 국가법령정보센터 원문 대조 후 인용 |
| Stanford IR Book | 접속 타임아웃 | 재시도, 실패 시 scikit-learn·Google MLCC로 대체 |
| "접속"만 확인한 행 전체 | HTTP 200 | 인용 전 해당 절 본문 대조 |
| OpenAI 공식 문서(function calling, evals) | 접속만 | 6장에서 공급자 비교를 넣을 경우 대조 |

## 8. 핵심 권고

1. **AI FDE를 "LLM을 쓰는 FDE"가 아니라 "평가로 품질을 증명하는 FDE"로 정의하라.** 근거: 같은 회사(Databricks Seoul, Palantir)의 일반/AI 공고 비교와 AI 공고 전부의 evaluation 요구.
2. **기술 근거는 RFC 9110/9700/9457/6585/8288·공식 문서만 쓰고, 초안(Idempotency-Key, OAuth 2.1, RateLimit)과 커뮤니티 규격(Standard Webhooks, 12-Factor)은 표기로 구분하라.**
3. **구판 자료 함정을 명시적으로 교정하라:** RFC 7231/7807 인용, implicit/password grant, SHA-1 웹훅 헤더, OWASP 2021 순위, Python 3.11 이하 sqlite3 트랜잭션, MCP 구판 세션 모델, 구조화 출력의 구 `output_format`.
4. **모든 예제는 로컬·무료로 실행하고 실제 출력을 붙여라.** §3처럼 실패 경로(NULL 누락, LEFT JOIN 오용, 미커밋 롤백, 불균형 accuracy)를 예제의 중심에 둬라.
5. **역할 서술은 5개사·8개 공고·2026-11-17 시점 표본임을 본문에 밝히고, 취업 용이성·시장 일반화 표현을 쓰지 마라.**
