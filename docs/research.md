# FDE 채용 자료조사 (역할: 채용 조사자)

- 작성: Opus 5.5 (`claude-opus-5-5`), 같은 세션에서 조사자 → 검증자 → 교육 설계자 순으로 역할 전환. 독립 검토 아님.
- 접근일: 2026-11-16 (모든 URL 공통)
- 수집 도구: WebSearch(후보 탐색), WebFetch(원문 열람). WebFetch는 페이지를 소형 모델이 요약·인용해 돌려주는 방식이므로 원문 전체를 사람이 직접 본 것은 아니다. 핵심 문장은 `docs/verification.md`에서 원문 인용 요청으로 재확인했다.
- Bash `curl`로 ATS API 원본 JSON을 받으려 했으나 이 세션에서 셸 네트워크 명령이 승인되지 않아 사용하지 못했다.

## 출처 유형 정의

| 유형 | 의미 |
|---|---|
| A. 회사 ATS/채용 페이지 | 회사가 직접 운영하는 페이지 또는 회사 계정의 Greenhouse/Lever 보드 |
| B. 채용 플랫폼 회사 게시 | 원티드 등에 회사가 직접 올린 공고. 회사 사이트 원문은 아님 |
| C. 2차 자료 | 대학 공지, 언론, 집계 사이트. 공고 근거로는 보조로만 사용 |

## 공고 표본 (서로 다른 9개 기업, 접근 성공 기준)

상태 표기: 현행 = 접근일에 지원 버튼 활성·마감 표시 없음. 마감 = 페이지에 마감 문구. 확인불가 = 상세 페이지 접근 실패 또는 목록에서 사라짐.

### 해외

**1. Palantir — Forward Deployed Software Engineer (New York, Hybrid)** · 유형 A · 현행
- URL: https://jobs.lever.co/palantir/dab396d4-2f14-4796-aac0-0d82883dccf0
- 필수(What We Require): 대졸 후 관련 경력 1년 이상. CS·수학·SW공학·물리·데이터사이언스 등 공학 배경. Python, Java, C++, TypeScript/JavaScript 등 코딩 능력. 최대 25% 고객사 출장 가능(개인 사정에 따라 유연).
- 우대: "Preferred" 항목 없음. "What We Value"에 분석적 문제 해결, 대규모 데이터 관심.
- 언어 조건: 명시 없음. 급여: $135,000–$200,000/년.

**2. Anthropic — Forward Deployed Engineer (London)** · 유형 A · 현행
- URL: https://job-boards.greenhouse.io/anthropic/jobs/5423029008
- 필수(You may be a good fit if): 기술·고객 대면 역할 4년 이상. LLM 프로덕션 경험(프롬프트 엔지니어링, 에이전트 개발, 평가). Python 능숙(추가 언어 권장). 모호성 대응, 조직 간 협업, 고객 discovery 의사소통.
- 우대: 금융·헬스케어/생명과학 등 엔터프라이즈 업계 배경, 엔터프라이즈 IT·AI 배포 패턴 경험("is a plus").
- 조건: 25–50% 고객사 출장. 전 직원 최소 25% 사무실 근무. 비자 후원 있으나 모든 경우 보장 안 함. 언어 조건 명시 없음. 급여 £225,000–£255,000.
- 업무 예: MCP 서버, 서브에이전트, 에이전트 스킬 등 산출물 제공.
- 참고: 같은 보드에 Paris, Munich FDE 공고도 목록에 있음(상세 미열람).

**3. Databricks — Sr. Forward Deployed Engineer (FDE) – Digital Native Business (SF Bay Area)** · 유형 A · 현행
- URL: https://www.databricks.com/company/careers/professional-services-operations/forward-deployed-engineer---fde-fullstack---digital-native-business--8488399002
- 자격(What we look for): 데이터 엔지니어링·데이터 플랫폼·SW 엔지니어링 6년 이상. 클라우드 2개 이상 실무 지식. Apache Spark 분산 처리 심층 경험. CI/CD, MLOps, AI API. 엔터프라이즈 고객·이해관계자 갈등 관리. 문서화·화이트보딩. Python/Scala/JS·TS 중 하나 이상. "Databricks Certification"이 목록에 있으나 필수/우대 구분 표기 없음.
- 조건: 고객 출장 20%. Bay Area 거주·이주 또는 월 1주 이상 방문. 언어 조건 명시 없음. 급여 $182,000–$250,208.

**4. Scale AI — Frontier Agents Engineer (Forward Deployed Engineering) (San Francisco)** · 유형 A · 현행
- URL: https://job-boards.greenhouse.io/scaleai/jobs/4694861005
- 필수: SW 엔지니어링 4년 이상(분산 시스템·알고리즘·시스템 설계). Python 프로덕션 경험. LLM API·에이전트 프레임워크·MCP·검색·벡터DB 기반 AI 앱 구축/배포. AWS/Azure/GCP. 문제 해결·의사소통.
- 우대: 프로덕션 에이전트 배포, Docker/Kubernetes/IaC/CI/CD, 평가 프레임워크·LLM 관측·가드레일, 엔터프라이즈 아키텍처 리뷰.
- 조건: SF 또는 NY 사무실 주 3회 대면 가능 여부 질문. 출장 명시 없음. 언어 조건 명시 없음. 급여 $180,000–$225,000.
- 참고: 같은 보드에 Public Sector FDSE, 중동(Kuwait/Riyadh) Forward Deployed 공고도 있음(상세 미열람).

### 한국 근무

**5. Palantir — FDSE, Korea Forward Deployed (Seoul)** · 유형 A · 현행 · 유사 아닌 동일 직무, 단 미국 정부 업무
- URL: https://jobs.lever.co/palantir/a39bf84c-6648-4871-bd07-9b882d401c4c
- 필수: "Active Top Secret Clearance with eligibility and willingness to obtain SCI." (필수 항목은 이것 하나)
- 우대: 물류·물자·정비·항공·준비태세 분석 경험. 국내 출장 의향.
- 조건: 미국 정부 업무 지원, 근무지 서울, 상단 위치 표기는 Washington, D.C. 경력 연수·언어 조건 명시 없음. 급여 $135,000–$200,000.
- 해석 주의: 미국 비밀취급인가가 필수이므로 일반 한국 지원자 대상 공고로 보기 어렵다.

**6. 채널코퍼레이션(채널톡) — Forward Deployed Engineer (서울 강남, Hybrid)** · 유형 A(회사 Lever 보드 `zoyi`) · 현행
- URL: https://jobs.lever.co/zoyi/905bc3bd-d788-4d17-b463-ae23b6a910b2
- 요구 역량(별도 자격요건 섹션 없음): 경력 5년 이상 엔지니어링 역량, 높은 코딩 역량 전제, 문제 정의~실행 전 주기, 비즈니스 임팩트 사고, 대규모·복잡한 고객사 직접 소통.
- 지원서: AI로 비즈니스 문제를 해결한 경험, 고객·현장 사용자를 만나 문제를 발견한 경험을 자유 형식으로 작성.
- 우대: 별도 섹션 없음. 병역특례 지원 가능, 일본·글로벌 고객사 프로젝트 기회 언급.
- 언어 조건: 명시 없음.
- 미확인: 검색 요약에 나온 "3년 이상 개발 경력과 API·데이터 연동 경험"(channel.io/ko/careers?team=AX)은 원문을 열지 못해 미확인.

**7. 사이오닉에이아이 — FDE 상시 인재풀 (서울 강남)** · 유형 B(원티드) · 상시채용
- URL: https://www.wanted.co.kr/wd/394288
- 자격요건: 정답 없는 상황에서 문제 정의·실행, 새로운 기술과 고객 비즈니스 빠른 학습, SW 개발·시스템 이해 기반 직접 해결, 경청과 의견 공유, 결과 책임. 고객과 문제 해결·시스템 연동·운영 이슈 분석 경험 기술 요청. FDE 직함 경험 불필요.
- 업무: 고객 업무 흐름·데이터·제약 이해 후 문제 정의, 자사 STORM 기반 해결책 설계·구현, 설치·연동 이슈 해결.
- 우대: 없음. 경력: 1–3년. 언어: 명시 없음. 기술 스택 항목 비어 있음.

**8. 센드버드코리아 — Forward Deployed Engineer (서울 삼성동)** · 유형 B(원티드) · 마감(표시 충돌)
- URL: https://www.wanted.co.kr/wd/306574
- 필수: 실무 SW 엔지니어링 2–3년(풀스택/백엔드 선호). Python 능숙. React·JS/TS 프런트 + Node.js/Django/Express 백엔드 풀스택 경험. CI/CD와 관측(로깅·지표·가동 모니터링) 이해. LLM API 이해, 시스템 프롬프트 논리 검토. 고객 직접 소통.
- 업무: 고객 맞춤 AI 에이전트 구축·연동·배포, RAG·지식베이스·커스텀 도구 백엔드 연동, 설정~모니터링, 문서화·아키텍처 다이어그램·기술 데모.
- 우대: 없음. 경력 표기 충돌: 상단 "경력 2-5년", 본문 2–3년. 언어: 명시 없음(본문 영어 작성).
- 상태 충돌: "해당 공고는 마감된 공고입니다." 와 마감일 "상시채용" 동시 표시. 과거 공고로 분류.

**9. 마키나락스 — Forward Deployed Software Engineer (서울 서초)** · 유형 B(원티드) · 마감(표시 충돌)
- URL: https://www.wanted.co.kr/wd/341457
- 필수: 관련 경력 2년 이상 또는 그에 준하는 역량. LLM/VLM 서비스 개발 관심. CS 기초, Git 협업. REST API 이해와 API·DB 설계. Docker/Kubernetes 환경 적응.
- 업무: AI 앱 백엔드, REST API·DB 스키마 설계·최적화, Kubernetes 기반 배포·운영 지원.
- 우대: 없음. 언어: 명시 없음. 상태: 센드버드와 같은 마감/상시 표시 충돌. 과거 공고로 분류.

### 부분 확인 / 접근 실패

**10. 크래프톤 — AI FDE (서울 역삼)** · 유형 C만 확인 · 확인불가(과거로 추정)
- 회사 공고 상세(https://job-boards.greenhouse.io/krafton/jobs/8464196002)는 채용 목록으로 이동해 상세 없음. 접근일 목록 1쪽(50/66건)에 FDE 제목 없음. 2쪽 미확인.
- 2차: 서울대 컴퓨터공학부 공지(2026-05-22) https://cse.snu.ac.kr/en/community/notice/25161 — 계약직, 6개월 이상 근무, 역삼 대면 근무, "Claude Code, Codex, LLM API 등 AI 도구를 활용해 작동 가능한 프로토타입을 제작·시연". 자격요건은 이미지에 있어 텍스트로 확인 불가.
- 2차 언론: 학력·경력 요건 없는 채용이라는 보도(서울경제 영문판) — 원문 미열람, 미확인.

**OpenAI — Forward Deployed Engineer, Seoul** · 접근 실패
- https://openai.com/careers/forward-deployed-engineer-seoul-seoul-south-korea/ 및 /forward-deployed-engineer-seoul → HTTP 403. https://jobs.ashbyhq.com/openai 는 본문 없음. Ashby API는 응답 크기 제한(10MB) 초과.
- 검색 요약에 "5년 이상" 등이 보였으나 원문 미확인이므로 표본에서 제외.

**기타 미확인 후보(표본 제외)**: 리벨리온(집계 사이트만, 원문 410), RLWRLD(집계 사이트만), Reflection AI Seoul(404), 센드버드 현행 공고(회사 사이트가 delight.ai로 리디렉트, 미열람), Salesforce(집계 사이트만).

## 표본 요약

| # | 기업 | 지역 | 상태 | 출처 | 경력 | AI/LLM 명시 | Python 명시 | 출장/출근 |
|---|---|---|---|---|---|---|---|---|
| 1 | Palantir | 해외(NY) | 현행 | A | 1년+ | 일부("using AI") | 예(예시 언어) | 출장 ≤25% |
| 2 | Anthropic | 해외(London) | 현행 | A | 4년+ | 필수 | 필수 | 출장 25–50% |
| 3 | Databricks | 해외(SF) | 현행 | A | 6년+ | AI API·MLOps | 선택지 중 하나 | 출장 20% |
| 4 | Scale AI | 해외(SF) | 현행 | A | 4년+ | 필수 | 필수 | 주3회 출근 |
| 5 | Palantir Korea | 한국(美 정부) | 현행 | A | 미명시 | 미명시 | 미명시 | 국내 출장 |
| 6 | 채널코퍼레이션 | 한국 | 현행 | A | 5년+ | AI 문제 해결 경험 요구 | 미명시 | Hybrid |
| 7 | 사이오닉에이아이 | 한국 | 상시 | B | 1–3년 | 미명시(자사 STORM) | 미명시 | 미명시 |
| 8 | 센드버드코리아 | 한국 | 마감 | B | 2–3년(2–5 표기) | 필수 | 필수 | 미명시 |
| 9 | 마키나락스 | 한국 | 마감 | B | 2년+ | 관심 | 미명시 | 미명시 |
| 10 | 크래프톤 | 한국 | 확인불가 | C | 미확인 | 예(2차) | 미확인 | 대면 |

해외 현행 4, 한국 현행 2(그중 1건은 미국 비밀취급인가 필수), 한국 상시 1, 한국 과거 2, 한국 2차만 1.

## 반복 역량 (상세 확인 9건 기준)

- 고객 대면 문제 정의·소통: 8/9 (R5는 필수 항목이 비밀취급인가 하나뿐. 2026-11-16 리뷰에서 9/9를 수정)
- 프로덕션 코딩: 8/9 (R5 제외) (언어 명시 시 Python이 가장 많음: 4건 필수/예시, 1건 선택지). Rust 언급 0건.
- LLM/에이전트/AI 적용: 명시 필수 3(Anthropic, Scale, Sendbird), 경험·관심 요구 3(채널, 마키나락스, Databricks의 AI API).
- API·DB·시스템 연동: 4(Sendbird, 마키나락스, 사이오닉, Scale)
- 배포·운영·CI/CD·컨테이너·관측: 4(Databricks, Scale, Sendbird, 마키나락스)
- 평가·가드레일: 2(Anthropic 필수, Scale 우대)
- 문서화·데모·화이트보딩: 2(Databricks, Sendbird)
- 출장·대면 근무 조건 명시: 5(Palantir 2건, Anthropic, Databricks, Scale)

## 취업 용이성 가설: "FDE가 일반 개발자보다 취업이 쉽다"

판정: **근거 부족, 결론 내리지 않음.**

- 확인된 것은 공고 수 증가뿐이다. Fortune(2026-09-03)은 Lightcast 데이터로 "Job postings for “forward-deployed” engineers rose more than 1000% between January and August 2026"이라고 보도. 같은 기사 기준 전체 기술직 공고는 전년 대비 13% 증가. 출처: https://www.fortune.com/2026/09/03/forward-deployed-engineers-fast-growing-six-figure-silicon-valley-job-integrate-ai-with-customers-tech-careers-palantir/
- 인도: Analytics India Magazine이 Indeed 데이터로 2025-06→2026-06 약 19배 증가 보도. Indeed 스스로 "FDE sample is too small to support a reliable median salary"라고 밝힘. 출처: https://analyticsindiamag.com/ai-news/forward-deployed-engineer-job-postings-in-india-grew-nearly-19x-in-a-year-report
- 두 기사 모두 공고당 지원자 수, 채용률, 일반 SWE 대비 합격 난이도 자료가 없다. 1차 통계(Lightcast, Indeed Hiring Lab 원보고서)는 열람하지 못했다.
- 공고 증가는 수요 신호일 뿐 개인 합격 가능성을 뜻하지 않는다. 직함이 회사마다 다른 업무를 가리켜 제목 집계가 과대평가될 수 있다.
- 표본의 요구 조건은 오히려 진입 장벽을 보여준다: 9건 중 4건이 4년 이상, 미국 비밀취급인가, 20–50% 출장, 주 3회 출근. 진입 가능 사례도 있다(Palantir 1년+, 사이오닉 1–3년, 센드버드·마키나락스 2년+).

필요 자료: 같은 지역·기간의 FDE vs SWE 공고당 지원자 수, 서류·최종 합격률, 채용 소요 기간. 공개 1차 자료 확보 전까지 학습 앱은 "취업이 쉽다"는 문구를 쓰지 않는다.

## 표본 한계

- 9개사 중 해외 4개사(전부 미국계 대형 AI/데이터 기업). 일반 SaaS, 국내 대기업, 비AI 산업 표본 없음.
- 한국 공고 중 회사 자체 페이지 원문은 2건(채널, Palantir Korea). 나머지는 원티드 게시 또는 2차 자료.
- 한국 과거 공고 2건은 원티드 페이지에 마감·상시 표시가 동시에 있어 정확한 게시·마감 일자를 알 수 없음.
- 직급 편차 큼(1년+ ~ 6년+). 신입·전환자 대상 결론 일반화 불가.
- 언어 조건(영어·한국어 능력)은 9건 모두 명시 없음. 해외 공고의 영어 필요성은 추정일 뿐 근거 없음.
- WebFetch 요약 방식이라 인용 문장이 원문과 다를 위험이 남는다(재확인 1회 수행).
