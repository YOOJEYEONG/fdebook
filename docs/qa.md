# QA 기록 (역할: Rust 구현자 → QA 담당)

- 수행: Opus 5.5 (`claude-opus-5-5`). 구현과 QA를 같은 세션에서 차례로 했습니다. 독립 QA가 아닙니다.
- 날짜: 2026-11-16
- 환경: macOS (Darwin 27.2.0), rustc/cargo 1.100.0 (rustup 공식 설치 스크립트로 이번에 설치), Node v26.8.2, Google Chrome(헤드리스, `--headless=new`)
- 서버: `./target/release/fde-study` → http://127.0.0.1:8787

## 의존성 버전 확인

crates.io API(`https://crates.io/api/v1/crates/<이름>`)에서 2026-11-16에 최신 안정 버전을 확인했습니다.

| 크레이트 | 버전 | 용도 |
|---|---|---|
| axum | 0.8.9 | HTTP 라우팅 |
| tokio | 1.54.1 | 비동기 런타임 (`macros`, `rt-multi-thread`, `net`) |
| serde | 1.0.229 | 콘텐츠 JSON 역직렬화 |
| serde_json | 1.0.154 | 콘텐츠 JSON, 과제 색인 생성 |

넣지 않은 것: tower-http(정적 파일 3개는 `include_str!`로 처리), 템플릿 엔진(`format!` + 이스케이프 함수), anyhow(`Box<dyn Error>`로 충분), 프런트엔드 프레임워크·외부 폰트·CDN.

## 실행한 명령과 결과

| 명령 | 결과 |
|---|---|
| `cargo fmt --check` | 통과 |
| `cargo check` | 통과 |
| `cargo clippy --all-targets -- -D warnings` | 통과, 경고 0 |
| `cargo test` | 8개 통과 |
| `node --test static/logic.test.mjs` | 13개 통과 |
| `curl`로 라우트 16개 확인 | 페이지 10개, 정적 파일 3개는 200. `/weeks/13`, `/weeks/abc`, `/nope`는 404. CSP·nosniff·Referrer-Policy 헤더 확인 |
| `node tools/browser-qa.mjs <out>` | 61/61 통과 |

### Rust 테스트 (src/main.rs)
콘텐츠 전체 검증 통과, 12주, HTML·속성 이스케이프, `javascript:` 링크는 텍스트로만 출력, 과제 색인 JSON에 `<` 없음(script 탈출 방지), 과제 ID 중복 거부, http URL 거부, 시간 표기.

### JS 로직 테스트 (static/logic.test.mjs)
선택한 경로만 진도에 포함, 체크와 자기평가 분리 집계, 대체 경로 전환 반영, 다음 과제 선택, 백업 왕복 동일성, 거부 사례(버전 2, 알 수 없는 과제 ID, `__proto__` 키, 추가 필드, 잘못된 타입, `javascript:` URL, 중복 ID), URL 판정, 기간 올림.

### 브라우저 확인 (tools/browser-qa.mjs, 헤드리스 Chrome + DevTools Protocol)
임시 프로필로 실행했고, 사용자의 평소 브라우저 데이터는 쓰지 않았습니다.

- 375px·1280px: 페이지 11개(404 포함) 모두 가로 넘침 0 (22건)
- 페이지 순회와 전체 시나리오 중 콘솔 오류·CSP 위반 0 (의도된 `/nope` 404 제외)
- 첫 방문: 오늘의 과제가 1주차 첫 과제, 설정 안내 표시
- 키보드: 첫 Tab은 본문 건너뛰기 링크, Enter로 본문 이동, Tab만으로 과제 체크박스 도달, 포커스 outline 표시, Space로 체크 후 저장 안내. 375px에서 Tab으로 상단 메뉴 도달
- 새로고침 후 체크·자기평가·메모 복원, 홈의 다음 과제 이동, 체크(1/30)와 자기평가(1/30) 별도 집계
- 설정 저장, 잘못된 주당 시간(0) 거부 시 기존 값 유지, 대체 경로 선택 시 7주차 LLM 과제가 경로 밖으로 표시
- 근거 자료: 경력 3년 필터에서 R1, R7, R8, R9만 표시
- 지원 기록: `javascript:` URL 거부, 추가, 수정. 메모의 `<img onerror>`가 실행되지 않고 텍스트로 출력
- 면접 기록 추가
- 백업: 실제 파일 다운로드, 파일 내용 = 저장 데이터. 버전 2와 알 수 없는 과제 ID 백업은 거부되고 저장 데이터가 바뀌지 않음. 초기화 후 정상 백업을 가져오면 원래 데이터와 같음
- 손상 저장 데이터(`{깨진 데이터`): 경고 표시, 체크해도 원본을 덮지 않고 체크를 되돌림, 원본 내려받기 버튼 표시, 백업 가져오기로 복구

### 스크린샷 직접 검토
1280px 홈·1주차·설정·근거 자료·손상 경고, 375px 1주차·근거 자료를 열어 봤습니다. 본문 72ch 폭, 왼쪽 메뉴(1280px)와 줄바꿈 상단 메뉴(375px), 고객 상황 노트, 포커스 테두리가 의도대로 보였습니다. 스크린샷은 세션 임시 폴더에 있고 저장소에는 넣지 않았습니다. `tools/browser-qa.mjs`를 다시 실행하면 다시 만들어집니다.

## 스킬 적용 사례

- ponytail (full): 정적 파일은 `include_str!`, 체크는 `<input type="checkbox">`, 백업은 `Blob` 다운로드와 `<input type="file">`, 확인창은 `confirm()`을 썼습니다. 의존성은 4개이고 프레임워크는 쓰지 않았습니다. 생략하지 않은 것: 백업 전체 스키마 검사, 저장 실패·손상 시 데이터 보존, 출력 이스케이프, 접근성. 비단순 로직마다 실행 가능한 검사를 남겼습니다.
- rust-best-practices: 프로덕션 경로에 `unwrap`/`expect`가 없고 `?`와 `Result`를 씁니다(`expect`는 테스트에만). 인자는 `&str`, `&[String]`. `cargo clippy -D warnings`를 통과했고, 테스트 이름은 동작 서술형입니다. 타입 상태 패턴 같은 고급 패턴은 넣지 않았습니다.
- frontend-design: 첫 화면의 중심을 "오늘의 고객 과제"로 했습니다. 숫자 히어로·그라디언트·전부 대문자 라벨·동일 카드 반복을 피했고, 번호는 주차와 과제 순서에만 썼습니다. 강조 요소는 고객 상황 노트 하나(왼쪽 강조선)입니다. 시스템 고딕, 72ch, 16px/1.7, 포커스 표시, reduced motion을 반영했습니다. 버튼과 결과 문구는 같은 동사를 씁니다(내보내기 → "내보냈습니다").
- find-skills: 새 스킬을 설치하지 않았습니다. 기존 설치(rust-best-practices, frontend-design)로 충분했습니다.

## 남은 한계

- 실제 화면 리더(VoiceOver 등)로는 확인하지 않았습니다. 레이블·랜드마크·`aria-live`는 코드로만 확인했습니다.
- Safari, Firefox, 실제 모바일 기기에서는 확인하지 않았습니다. 375px은 Chrome 에뮬레이션입니다.
- 명도 대비는 설계 색상값 기준이며 자동 대비 측정 도구로 재지는 않았습니다.
- 저장소 차단 환경(localStorage 예외)의 안내 문구는 코드 경로만 있고 브라우저로 재현하지 않았습니다.
- 콘텐츠의 공고 정보는 2026-11-16 기준입니다. 공고는 바뀔 수 있으며 `docs/verification.md`의 남은 검증 과제(OpenAI 서울 원문 등)는 그대로입니다.
- 콘텐츠를 바꾸면 다시 빌드해야 합니다.

## 리뷰 후 갱신 (2026-11-16)

리뷰 수정과 Vercel 어댑터 추가 뒤 결과는 `docs/review.md`에 있습니다. Rust 테스트는 `src/lib.rs`로 옮겼고, 브라우저 검사는 68건(회귀 7건 추가)입니다.
