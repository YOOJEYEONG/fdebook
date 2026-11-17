# 학습북 v2 진행 상태

갱신: 2026-11-17. 기준 설계: `docs/book-v2-plan.md`.

현재 상태: 완료(로컬 검증까지). 36절 본문·예제 31개·Exact 웹 빌드·QA 완료. 미리보기 http://127.0.0.1:8770/ . 기존 배포·Git 기록은 건드리지 않음(commit/push 없음).

## 단계 1. Exact 확인 — 완료
- 공식 저장소 https://github.com/expo/exact 을 `.cache-ext/exact`에 복제. 고정 커밋 `de212e671a69f4fea18bed67d5b73b259ddf3061`.
- 읽은 문서: README(Quick start), AGENTS.md/CLAUDE.md, docs/start-here-site.md, recipes/website.md, website-hosting.md, long-text.md, responsive-columns.md, web-look.md.
- 스킬: `npx skills find`로 Exact 전용 스킬 없음 확인. `expo/skills`는 React Native Expo용이라 해당 없음. Exact 저장소의 `skills/orchestrate`, `skills/panel`은 exact2 자체 개발용 멀티모델 운영 스킬이라 설치하지 않음. 앱용 지침은 `exact new`가 쓰는 `book/AGENTS.md`.
- Bun 1.4.2(고정 버전)를 `~/.bun-1.4.2`에 별도 설치. `bun scripts/exact.mjs setup --platform web` 모두 ok.
- `exact new book` + `pattern site` 후 `bun exact.mjs test web` 6/6 통과(기존 앱 서버가 8787을 쓰고 있어 스탠드인 API 포트를 8797로 변경).

## 단계 2. 자료 조사 — 완료
- `docs/book-v2-research.md`: 공식 채용 원문 6건(OpenAI·Anthropic·Palantir 공식 채용 게시판 API), 기술 출처 26건, 주장·출처 대응표, 범위 결정, 목차 확정(8장 36절).

## 단계 3. Exact 읽기 UI 시제품 — 완료
- `book/`: `exact new` + `pattern site`에서 시작. `content/*.md` → `tools/gen-book.ts` → `book.gen.ts` → `app.ts`(grants 없음) → `app.contract`.
- 라우트 `home "/"`, `read "/read/:id" render=build pages=sectionIds()`: 모든 절이 빌드 때 정적 HTML로 만들어진다.
- 확인: 1280px 화면에서 사이드 목차·본문·소목차·코드 복사(`copyText`)·해설 열기 동작. 홈의 `list`가 넓은 화면에서 목록-상세 분할을 일으켜 `column`으로 바꿈.
- `tools/run-examples.ts`: 본문이 참조하는 모든 예제를 실행해 `.out`과 비교, `examples/verified.json` 기록.

## 단계 4. 본문 집필 — 완료
- 2–5장 20절 완료(예제 20개, `--repeat 5` 반복 실행 일치). 2.2 예제에서 반복 실행으로 연결 재설정 버그를 발견해 고치고 본문 '흔한 오류'에 반영.
- Docker 데몬이 꺼져 있어 4.4 Dockerfile 빌드는 미실행(본문에 명시).
- 재개 후: `docs/book-v2-source-audit.md` 대조. 반영: MCP 판을 2026-07-28(latest)로 고정, 구조화 출력의 refusal/max_tokens·enum 대소문자 예외와 `output_format` deprecated, 정밀도 '정의 안 됨' 처리와 불균형 정확도 함정, AWS 글은 '표준 아님' 표기, 12-Factor는 커뮤니티 방법론 표기, Actions는 커밋 SHA 고정·`permissions: contents: read`, Stripe 이전 URL, sqlite3 `autocommit` 함정.
- 1·6·7·8장 16절 집필. 전체 36절, 실행 예제 31개를 `bun tools/run-examples.ts --repeat 5`로 각 5회 실행해 모두 기대 출력과 일치.
- 집필 중 실제로 발견한 버그를 본문 교재로 반영: 2.2(본문 미수신 거절 시 연결 재설정), 8.2(한국어 쿼리 비인코딩 UnicodeEncodeError), 8.3(합성 데이터 과적합: 새 표현 8건 전부 사람 검토).

## 단계 5. Exact 전체 빌드·QA — 완료
- `app.test.contract`를 학습북용 11개 테스트로 교체(목차, 직접 URL, 이전/다음, 처음/끝, 해설, 코드 복사, 모바일 목차, 넓은 화면, 없는 절, 404, 키보드). `bun exact.mjs test web` 11/11.
- `bun exact.mjs verify`: 첫 실행 63건 → 최종 2건(최대 글자 크기에서 Markdown 인용·목록 넘침). 고친 것: 빌드 HTML 채택 실패(폭 의존 `if` → `display`), rem 글꼴, 24px 링크, 코드 상자 내부 가로 스크롤, 단어 끊김, 긴 URL, `html lang="ko"`, 본문 건너뛰기 링크.
- 실제 Chromium(`tools/browser-qa.ts`): 37경로 × 320/375/1280px 111회 로드, HTTP·콘솔 오류·가로 넘침·제목 문제 0, Tab 순서와 Enter로 목차 열기 확인.
- 출처 URL 78개 확인: 76개 200, Palantir Lever 2건은 최종 시점 500/시간 초과(같은 날 API로 본문 대조함).
- 문서: `docs/book-v2-qa.md`, `docs/exact-feasibility.md`, `book/README.md`. 스크린샷 `docs/book-v2-qa-shots/`.
- Git 위생: 루트 `.gitignore`에 `.cache-ext/`, `__pycache__/` 추가. `book/.gitignore`(Exact 생성)가 `dist/`, `target/`, `.exact/`, `.env.local`을 제외. 기존 파일은 지우지 않음.

## 남은 한계
`docs/book-v2-qa.md` 6절 참조: Docker 빌드 미실행, 최대 글자 크기 2건, 6장 가짜 모델, 어휘 검색, 8장 과적합(본문의 결론), 자체 검토(독립 검토 아님).
