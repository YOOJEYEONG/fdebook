# 제품 리뷰 (2026-11-16)

- 수행: Opus 5.5 (`claude-opus-5-5`). 구현자와 같은 세션이 리뷰했으므로 독립 리뷰가 아닙니다.
- 대상: http://127.0.0.1:8787 (release 바이너리), `docs/design.md`, `docs/curriculum.md`와 대조.
- 적용 스킬: frontend-design(정보 위계, 문구), ponytail(최소 수정, 확장은 제안만), accessibility(WCAG 2.2 AA 점검 절차).

## 방법

1. 실제 브라우저(헤드리스 Chrome + DevTools Protocol)로 전체 페이지 11개를 1280px·375px·320px에서 열었습니다. 기록이 있는 상태와 대체 경로 상태도 확인했습니다.
2. axe-core 4.14.0(npm 공식 tarball을 세션 임시 폴더에만 받음. 프로젝트 의존성 아님)으로 `wcag2a/aa, wcag21a/aa, wcag22aa, best-practice` 규칙을 돌렸습니다.
3. 접근성 트리(`Accessibility.getFullAXTree`)로 접근 이름을 확인하고, 데이터 손실 시나리오(빠른 이동, 두 탭)를 직접 재현했습니다.
4. 콘텐츠는 `docs/verification.md`의 판정과 문장 단위로 대조했습니다.
5. 수정 후 `tools/browser-qa.mjs`(회귀 검사 7건 추가, 68건)와 axe를 다시 돌렸습니다.

Lighthouse는 실행하지 않았습니다(설치 필요). 화면 리더 실기기 확인은 하지 않았습니다.

## 심각도 기준

- 높음: 데이터 손실, 잘못된 직무 주장, 학습 목적 달성을 막는 결함
- 중간: WCAG AA 위반, 학습 효과를 크게 낮추는 누락
- 낮음: 불편, 일관성, 개선 제안

## 발견 사항

### 수정함

| # | 심각도 | 위치 | 재현 단계 | 영향 | 조치 |
|---|---|---|---|---|---|
| F1 | 높음 | `static/app.js:156`, `:187` (과제 메모) | 1주차 메모에 입력하고 0.6초 안에 메뉴 링크를 누르거나 새로고침 | 마지막 입력이 저장되지 않음. 재현 결과 저장값 "(없음)" | 대기 중인 저장을 `blur`·`pagehide`에서 즉시 실행. 회귀 검사 "메모 입력 직후 이동해도 저장" |
| F2 | 높음 | `static/app.js:66` (저장 기준 데이터) | 탭 A에서 2주차, 탭 B에서 1주차를 열고 B에서 체크, A에서 다른 과제 체크 | A가 오래된 메모리 데이터로 저장해 B의 체크가 사라짐(재현: `w1-plan` false) | `storage` 이벤트에서 기준 데이터를 다시 읽고 안내 표시. `load()`가 저장소 상태 플래그를 매번 초기화(`:15`) |
| F3 | 높음 | `static/app.js:156` (같은 과제의 오래된 폼) | 두 탭에서 같은 3주차를 열고 B에서 자기평가 "충족", A에서 체크 | 수정 전 A가 폼 전체를 저장해 B의 자기평가를 빈 값으로 덮음 | 바뀐 필드 하나만 최신 데이터에 덮어쓰고, 저장 후 폼을 저장값과 맞춤. 회귀 검사 3건 |
| F4 | 높음 | `content/course.json:48`, `docs/research.md:116-117` | 1주차 "왜 이걸 하나" | "모든 표본이 고객 대면 문제 정의와 프로덕션 코딩을 요구"는 사실과 다름. R5 Palantir Korea의 필수 항목은 비밀취급인가 하나뿐(검증표 V6) | "R5를 뺀 8건"으로 수정, research.md도 8/9로 수정 |
| F5 | 높음 | `content/course.json:96`, `docs/curriculum.md:10` | 1주차 과제 3 | "9건 중 6건이 AI를 필수 또는 경험으로 요구"는 과장. 마키나락스(R9)는 "관심", Databricks(R3)는 "실무 지식" | "AI·LLM 언급 6건(필수 3, 경험·지식 2, 관심 1)"로 수정 |
| F6 | 중간 | `static/app.css:187` | 설정에서 대체 경로 선택 후 7주차 | `opacity: 0.7` 때문에 LLM 과제 글자 대비 3.1:1~3.3:1 (axe color-contrast, WCAG 1.4.3 위반) | 투명도 제거, 점선 구분선 + 기존 경로 안내 문구로 표시 |
| F7 | 중간 | `src/lib.rs:593` | 화면 리더로 1주차 과제 기록 이동 | 체크박스 3개의 접근 이름과 그룹 이름("내 기록")이 모두 같아 어느 과제인지 구분 불가 | legend를 "내 기록: {과제명}"으로 변경 |
| F8 | 낮음 | `src/lib.rs:935`, `:840` | 근거 자료, 지원 현황 | h1 다음 바로 h3 (axe heading-order) | h2 "공고", "기록" 추가 |
| F9 | 낮음 | `src/lib.rs:980` | 설정 저장, 백업 내보내기 | 성공 문구가 라이브 영역이 아니라 화면 리더에 전달되지 않음 | `role="status" aria-live="polite"` |
| F10 | 낮음 | `static/app.css:210` | 375px 근거 자료 필터·과제 체크 | 체크박스·라디오 18×18px. 레이블이 붙어 있어 2.5.8 예외에 가깝지만 터치에 작음 | 24×24px로 확대 |
| F11 | 낮음 | `content/course.json:56`, `src/lib.rs:913` | 1주차 과제 1, 근거 자료 머리말 | "공고 9건"인데 근거 자료에는 10건, 머리말은 대학 공지(2차)도 "공고 원문"이라 표현 | "9건(R1–R9)", "공고 원문 9건, 대학 공지(2차 자료) 1건"으로 명시 |

수정 후 axe 위반 0건(전체 페이지 × 1280/375px), 320px 가로 넘침 0, 24px 미만 대상 0.

### 미수정 (제안)

| # | 심각도 | 위치 | 재현 단계 | 영향 | 권고 |
|---|---|---|---|---|---|
| P1 | 높음 | `content/course.json` 전체 과제 `steps` (예: `:186` w3-client, `:203` w3-webhook, `:312` w5-docker, `:434` w7-classify, `:498` w8-eval) | 초보자가 3주차 과제 1을 그대로 따라 하기 | 지수 백오프, HMAC 서명, 멱등 처리, Docker 볼륨, 정밀도·재현율, 혼동 행렬, MCP 같은 개념에 설명·예제·학습 출처가 없음. "왜 하는지"는 공고로 근거를 댔지만 "어떻게 배우는지"의 출처가 0건. `docs/design.md:19`의 "목표 → 출처 있는 설명 → 실습" 중 설명 단계가 비어 있어 초보 학습자는 과제를 수행하기 어렵다 | 과제마다 `concepts`(2~4문장 설명)와 `references`(Python 공식 문서 `urllib.request`·`http.server`·`hmac`·`sqlite3`, Docker·GitHub Actions 공식 문서 등, 접근일 포함)를 추가하고, 3·4·7·8주차에는 30~60줄 시작 코드 예제를 둔다. 링크는 검증 절차를 거쳐 추가한다 |
| P2 | 중간 | `src/lib.rs:591-596` (완료 기준 목록, 자기평가 선택) | 완료 기준을 하나도 확인하지 않고 "증거 수준" 선택 | 자기평가가 완료 기준과 연결되지 않아 근거 없는 평가가 가능 | 완료 기준을 체크 목록으로 만들고, 모두 체크해야 "충족", 산출물 링크가 있어야 "증거 수준"을 고를 수 있게 한다 |
| P3 | 중간 | `static/logic.js` `validateData` (알 수 없는 과제 ID 거부) | 콘텐츠에서 과제를 삭제·개명한 뒤 예전 백업 가져오기 | 백업 전체가 거부되어 복구 경로가 없음 | 백업 버전별 ID 변환표를 두거나, 알 수 없는 과제 기록만 따로 보여 주고 나머지를 가져오는 선택지 제공 |
| P4 | 중간 | 면접 준비 화면 | 예시 답안이나 채점 예시 확인 | "좋은 답의 기준"만 있고 예시 답이 없어 초보자가 자기 채점 기준을 잡기 어려움 | 유형마다 미흡/충족 예시 답 1개씩 |
| P5 | 낮음 | 과제 단위 역량·근거 연결 (`docs/design.md` "과제마다 목표 역량·산출물·평가 기준·근거") | 과제 화면 | 역량·근거가 주차 단위로만 연결됨 | 과제에 `competencies` 필드 추가 |
| P6 | 낮음 | 주차 화면 "근거 공고" 목록 | 1주차 | "R1 Palantir", "R5 Palantir"처럼 회사명만 같아 구분이 어려움 | 지역이나 직무명을 함께 표시 |
| P7 | 낮음 | 외부 링크 | 근거 자료 원문 링크 | 새 창으로 열리는 것을 화면 리더에는 알리지만 시각적으로는 표시하지 않음 | "(새 창)"을 보이게 하거나 같은 창에서 열기 |
| P8 | 낮음 | 다른 탭 변경 후 | 탭 A에서 안내를 본 뒤 | 같은 화면의 다른 과제 폼은 새로고침 전까지 옛 값을 보여 줌(저장은 안전) | 필요하면 `storage` 이벤트에서 해당 페이지 폼을 다시 채운다 |

## 설계 대조 요약

- 맞음: 첫 화면 중심이 오늘의 고객 과제, 체크와 실력 평가 구분, 근거 자료의 URL·접근일·검증 상태, 빈 자료·잘못된 백업·저장 불가 안내, 375/1280px, 키보드 핵심 흐름, 외부 서비스 없음.
- 부족: 설명·예제·학습 출처(P1), 과제 단위 역량 연결(P5), 평가와 완료 기준 연결(P2).
- 직무 주장: 과장 2건(F4, F5)을 고쳤습니다. 취업 용이성 결론을 내리지 않는 원칙은 화면 전체에서 지켜졌습니다.

## Vercel 배포 어댑터 (추가 요청)

- 확인한 공식 자료(2026-11-16 접근): https://vercel.com/docs/functions/runtimes/rust ("The Rust runtime is available in Beta on all plans"), https://github.com/vercel/examples/tree/main/rust/axum (`api/axum.rs`, `Cargo.toml`, `vercel.json`, `.vercelignore`).
- 구현:
  - `src/lib.rs` `router()`가 콘텐츠 검증과 모든 라우트를 담당합니다. 로컬 서버 `src/main.rs`와 Vercel 함수 `api/fde.rs`가 같은 라우터를 재사용합니다.
  - `api/fde.rs`는 공식 예제와 같은 `ServiceBuilder::new().layer(VercelLayer::new()).service(router)` + `vercel_runtime::run`을 씁니다.
  - `Cargo.toml`에 `vercel_runtime = { version = "2.4.1", features = ["axum"] }`(crates.io 최신 안정 버전), `tower = "0.5.3"`, `[[bin]]` 두 개(`fde-study`, `fde`), `default-run = "fde-study"`, 공식 예제와 같은 release 프로필을 넣었습니다.
  - `vercel.json`은 모든 경로를 `/api/fde`로 rewrite합니다(공식 예제 방식).
  - `.vercelignore`는 공식 예제의 target 규칙에 `.env*`, 진도 백업 파일, 원시 로그, 로컬 스킬 폴더 제외를 더했습니다.
  - `.gitignore`는 사용자가 정한 규칙(`docs/opus-*` 원시 로그, `.vercel/`, `.DS_Store`)을 보존하고 `.env*`, 백업 파일만 추가했습니다.
- 로컬 확인: `cargo check --all-targets`, `clippy`, `cargo build --release`가 두 바이너리 모두 성공했습니다. `cargo run --release`는 그대로 127.0.0.1:8787에서 동작합니다.
- 확인하지 못한 것: Vercel 빌드와 실제 배포. Vercel 로그인·배포는 Codex 담당이라 실행하지 않았습니다. Vercel 빌더가 `api/` 밖의 `[[bin]]`(`src/main.rs`)이 있는 프로젝트를 문제없이 빌드하는지는 배포 로그로 확인해야 합니다. 실패하면 로컬 바이너리를 `required-features`로 분리하는 방안을 권합니다.
- 배포 시 주의: 개인 기록은 배포 도메인의 브라우저 localStorage에 저장되며 로컬(127.0.0.1)의 기록과 공유되지 않습니다. 옮기려면 백업 내보내기/가져오기를 씁니다. 서버는 상태를 저장하지 않으므로 비밀값이 필요 없습니다.

## 재실행한 검사 (수정 후)

| 명령 | 결과 |
|---|---|
| `cargo fmt --check` | 통과 |
| `cargo check --all-targets` | 통과 |
| `cargo clippy --all-targets -- -D warnings` | 통과 |
| `cargo test` | 8개 통과 (라이브러리로 이동한 테스트) |
| `node --test static/logic.test.mjs` | 13개 통과 |
| release 서버 재시작 후 `node tools/browser-qa.mjs` | 68/68 통과 (첫 실행은 67/68: 과제 제목 변경에 따른 검사 기대값을 갱신) |
| axe-core 재실행 | 위반 0건 |
