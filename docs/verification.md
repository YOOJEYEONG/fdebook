# 사실 검증 (역할: 사실 검증자)

- 수행: Opus 5.5, 조사자와 **같은 세션**의 별도 검증 패스. 별도 컨텍스트가 아니므로 독립 검증이 아니다. 조사자의 기억·요약을 쓰지 않고 원문 URL을 다시 열어 "정확한 문장 인용, 없으면 NOT FOUND" 형식으로 재질의했다.
- 접근일: 2026-11-16
- 한계: WebFetch는 소형 모델이 원문을 읽고 답하는 방식이다. 인용이 원문 그대로라는 보장은 없다. 원문 HTML/JSON 직접 비교(curl)는 셸 승인 문제로 못 했다.

판정: 확인 = 재열람 원문에서 문장 인용 확보. 수정 = 조사 초안과 다르게 고침. 미확인 = 원문 접근 실패 또는 문장 없음. 제외 = 본문·커리큘럼 근거에서 뺌.

## 주장–근거 대응표

| # | 주장 | 원문 근거(재열람 인용) | 판정 |
|---|---|---|---|
| 1 | Palantir NY FDSE는 대졸 후 1년 이상 경력 요구 | "1+ years of relevant, post-college work experience." | 확인 |
| 2 | Palantir NY 출장 최대 25% | "Ability and interest to travel up to 25%, as needed to client sites, but flexible based on personal preferences." | 확인 (조사 초안에 "flexible" 누락 → 수정) |
| 3 | Palantir NY 언어 예시에 Python 포함 | "programming languages such as Python, Java, C++, TypeScript/JavaScript, or similar." | 확인 |
| 4 | Palantir NY에 우대 섹션 없음 | Preferred: NOT FOUND, "What We Value"만 존재 | 확인 |
| 5 | Palantir Korea는 서울 근무, 미국 정부 업무 | "Although this position is in support of our US Government work, this role is located in Seoul, South Korea." | 확인 |
| 6 | Palantir Korea 필수는 TS 인가 하나 | "Active Top Secret Clearance with eligibility and willingness to obtain SCI." — What We Require 유일 항목 | 확인 |
| 7 | Palantir Korea 경력 연수 명시 | NOT FOUND | 미확인 → "미명시"로 기록 |
| 8 | Anthropic London 4년 이상 고객 대면 기술 역할 | "4+ years of experience in a technical, customer facing role such as Forward Deployed Engineer..." | 확인 |
| 9 | Anthropic LLM 프로덕션 경험 필요 | "Production experience with LLMs including advanced prompt engineering, agent development, evaluation..." | 확인 |
| 10 | Anthropic 출장 25–50% | "Travel frequently (25-50%) to customer sites to build in person with customers." | 확인 |
| 11 | Anthropic 사무실 근무 최소 25% | "we expect all staff to be in one of our offices at least 25% of the time." | 확인 |
| 12 | Anthropic 비자 후원 | "We do sponsor visas! However, we aren't able to successfully sponsor visas for every role and every candidate." | 확인 |
| 13 | Anthropic 8년 이상 요구 | 지원서 질문에 8년 이상 여부 문항만 있다는 1차 요약. 재열람 인용 미확보 | 제외 (필수 조건 아님) |
| 14 | Databricks 6년 이상 | "6+ years of experience in data engineering, data platforms & analytics, or software engineering" | 확인 |
| 15 | Databricks 인증이 필수 | 1차 요약은 "requirements"로 표현. 재열람: "What we look for" 목록에 "Databricks Certification", 필수/우대 표기 없음 | **수정**: "필수/우대 구분 없음" |
| 16 | Databricks 출장 20% | "Travel to customers 20% of the time" | 확인 |
| 17 | Databricks Bay Area 조건 | "Location: San Francisco Bay Area Preferred", "This role is San Francisco Bay Area-focused." | 확인 |
| 18 | Databricks 언어 | "Comfortable writing code in either Python, Scala, JavaScript/TypeScript, and modern frameworks" | 확인 |
| 19 | Scale AI 4년 이상 | "4+ years of software engineering experience with strong fundamentals in distributed systems" | 확인 |
| 20 | Scale AI Python 필수 | "Strong Python programming skills with experience building production software." | 확인 |
| 21 | Scale AI LLM API·에이전트·MCP | "Experience building or deploying AI-powered applications using modern LLM APIs, agent frameworks, MCP" | 확인 |
| 22 | Scale AI 주 3회 출근 | 지원 질문 "Are you open to working in person in our San Francisco or New York office 3 times a week?" | 확인 (요구가 아닌 질문 문항으로 표기) |
| 23 | 채널코퍼레이션 5년 이상 | "경력 5년 이상의 엔지니어링 역량을 기반으로" | 확인 |
| 24 | 채널 3년 이상·API·데이터 연동 경험 요구 | 검색 요약에만 존재. channel.io 원문 미열람 | **제외** |
| 25 | 채널 지원서에 AI 문제 해결 경험 서술 요구 | "서류 지원 시 아래 두 항목을 이력서 또는 별도 문서에 자유 형식으로 작성해 주세요." + 항목 내용(1차 요약) | 확인(항목 문구는 요약 수준) |
| 26 | 채널 언어 조건 | NOT FOUND | 확인(미명시) |
| 27 | 사이오닉 경력 1–3년, 상시채용 | "경력 1-3년", "상시채용" | 확인 |
| 28 | 사이오닉 우대사항 | NOT FOUND | 확인(없음) |
| 29 | 센드버드 마감 | "해당 공고는 마감된 공고입니다." | 확인 (마감일 "상시채용" 충돌 병기) |
| 30 | 센드버드 경력 | 상단 "경력 2-5년", 본문 "2–3 years of hands-on software engineering experience" | 확인 (충돌 병기) |
| 31 | 센드버드 Python·React/TS·CI/CD·관측 | 각 문장 인용 확보(research.md 8번) | 확인 |
| 32 | 마키나락스 마감, 2년 이상, Docker/K8s, REST API·DB | 각 문장 인용 확보, 우대 NOT FOUND | 확인 |
| 33 | 크래프톤 AI FDE 계약직·6개월·역삼 대면 | 서울대 공지(2차) 문장 인용 | 확인(2차 자료 한정) |
| 34 | 크래프톤 학력·경력 무관 채용 | 언론 검색 요약만 | **미확인**, 본문 근거 제외 |
| 35 | 크래프톤 공고 현재 열림 | 상세 URL이 목록으로 이동, 목록 1쪽에 없음 | 미확인(과거 추정) |
| 36 | OpenAI 서울 FDE 5년 이상 | openai.com 403, 원문 없음 | **제외** |
| 37 | 리벨리온·RLWRLD·Reflection AI FDE 공고 존재 | 집계 사이트만, 원문 410/404/미확보 | **제외** |
| 38 | FDE 공고 2026년 1–8월 1000% 이상 증가 | Fortune 기사 내 Lightcast 인용 문장 확보. Lightcast 원자료 미열람 | 확인(2차 보도 한정) |
| 39 | 인도 FDE 공고 약 19배 증가 | AIM 기사 내 Indeed 인용. Indeed 원자료 미열람 | 확인(2차 보도 한정) |
| 40 | FDE가 일반 개발자보다 취업이 쉽다 | 지원자 수·채용률·합격률 자료 없음. 두 기사 모두 해당 데이터 없음 | **미확인 — 결론 금지** |
| 41 | FDE 채용에 Rust 필요 | 9건 중 Rust 언급 0 | 근거 없음 → 커리큘럼에서 Rust를 직무 역량으로 가르치지 않음 |
| 42 | 해외 공고는 영어 능력 필수 | 9건 모두 언어 조건 NOT FOUND | 미확인, 추정 문구 사용 금지 |

## 수정 내역

1. Databricks 인증: "필수" → "필수/우대 구분 없음".
2. Palantir NY 출장: "개인 사정에 따라 유연" 추가.
3. 채널코퍼레이션 "3년 이상·API 연동" 주장 삭제(원문 미확인).
4. Anthropic "8년 이상" 조건 삭제(필수 조건 근거 없음).
5. Scale AI 출근 조건을 "요구"가 아닌 "지원서 질문"으로 표현.
6. 센드버드·마키나락스: 마감/상시 표시 충돌을 숨기지 않고 병기, 과거 공고로 분류.
7. OpenAI·리벨리온·RLWRLD·Reflection AI·크래프톤 학력무관 보도를 표본·근거에서 제외.
8. 취업 용이성: 공고 증가 통계를 "수요 신호(2차 보도)"로만 기록, 용이성 결론 삭제.

## 남은 검증 과제

- 원문 직접 비교: 셸 네트워크 허용 시 Greenhouse/Lever API JSON을 받아 인용 문장 문자열 대조.
- OpenAI 서울 공고: 브라우저 접근(로그인 불필요한 공개 페이지)으로 재시도.
- 크래프톤 채용 목록 2쪽, 채널 careers AX 페이지, delight.ai(센드버드) 현행 공고 확인.
- Lightcast·Indeed Hiring Lab 1차 자료와 지원자/채용률 지표 확보 시 가설 재판정.
