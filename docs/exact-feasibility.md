# Expo Exact 웹 타깃 실행 가능성과 재현 방법

확인일: 2026-11-17. 확인 환경: macOS 27.2.1(Apple Silicon), Python 3.15.0, SQLite 3.54.0.

## 사용한 Exact

- 저장소: https://github.com/expo/exact (공식). Exact는 릴리스·태그·npm 패키지가 없고 앱이 체크아웃을 경로로 쓴다(저장소 `CLAUDE.md`/`AGENTS.md`).
- **고정 커밋: `de212e671a69f4fea18bed67d5b73b259ddf3061`**. 체크아웃 위치: `.cache-ext/exact`(Git에 올리지 않음). 확인 시 작업 트리 변경 없음.
- 읽은 공식 문서: `README.md`(Quick start), `AGENTS.md`, `docs/start-here-site.md`(웹사이트 필독), `docs/recipes/website.md`, `website-hosting.md`, `long-text.md`, `responsive-columns.md`, `web-look.md`, `tests.md`, `docs/agent-pitfalls.md`의 Websites 절, `bun exact.mjs contract vocab …` 응답.
- 스킬: `npx skills find`로 Exact 전용 스킬 없음. `expo/skills`는 React Native Expo용이라 해당 없음. Exact 저장소의 `skills/orchestrate`, `skills/panel`은 exact2 개발용 다중 모델 운영 스킬이라 설치하지 않았다. 앱 지침은 `exact new`가 쓴 `book/AGENTS.md`를 따랐다.
- 피드백: `bun exact.mjs feedback never`로 이 프로젝트에서 외부 전송을 껐다(노트는 보내지 않음). 겪은 문제는 아래 "막힌 점"에 기록한다.

## 재현 명령

```sh
# 1) 도구: Bun 1.4.2(Exact package.json 고정 버전)를 기존 Bun과 따로 설치
curl -fsSL https://bun.sh/install | BUN_INSTALL=~/.bun-1.4.2 bash -s bun-v1.4.2
export PATH=~/.bun-1.4.2/bin:$PATH EXACT_FEEDBACK=0

# 2) Exact를 고정 커밋으로 받기(저장소 루트에서)
git clone https://github.com/expo/exact.git .cache-ext/exact
git -C .cache-ext/exact checkout de212e671a69f4fea18bed67d5b73b259ddf3061

# 3) 웹 빌드 준비(공식): Rust 1.99.1, 웹 nightly-2026-08-21, wasm-bindgen 0.2.127, Binaryen, Chromium 등
(cd .cache-ext/exact && bun scripts/exact.mjs setup --platform web)

# 4) 학습북 빌드·테스트·검증·미리보기
cd book
bun tools/run-examples.ts --repeat 5   # 예제 31개를 각 5회 실행해 기대 출력과 비교
bun run build                          # tools/gen-book.ts → exact.mjs web-build --out dist
bun exact.mjs test web                 # app.test.contract 11개
bun exact.mjs verify                   # 테스트 + 390/1280px·라이트/다크 화면 검사 + 접근성 트리 + 새로고침
bun exact.mjs serve dist --port 8770   # http://127.0.0.1:8770/
bun tools/browser-qa.ts http://127.0.0.1:8770   # 서버가 떠 있을 때: 37개 경로 × 3개 폭 실제 Chromium 점검
```

`book`은 `bun scripts/exact.mjs new book --name "FDE 기술 학습북" --bundle-id dev.local.fdebook` 후 `bun exact.mjs pattern site`로 시작했다. `book/exact.mjs`는 Exact가 생성한 파일이며 `../.cache-ext/exact`를 가리킨다(`EXACT` 환경 변수로 다른 체크아웃 지정 가능).

## 확인 결과(실행 출력 요지)

| 단계 | 결과 |
|---|---|
| `setup --platform web` | Rust 1.99.1, web nightly 2026-08-21(+rust-src, wasm32), Bun 1.4.2, wasm-bindgen 0.2.127, wasm-opt 132, node_modules, Chromium(Playwright 고정판), Cargo 크레이트 모두 `ok` |
| 패턴 `site` 원본 | `test web` 6/6 통과(실행 가능성 확인) |
| 학습북 `web-build` | `/` + `/read/:id` 36쪽 + `/404`를 빌드 시 HTML로 생성(`render=build pages=sectionIds()`). 정적 호스트에 그대로 올릴 수 있는 `dist/` |
| 학습북 `test web` | 11/11 통과 |
| 학습북 `verify` | 테스트 11/11, 390·1280px 라이트·다크 화면 검사 0건, 접근성 트리 0건, 새로고침 0건. 남은 2건은 최대 글자 크기(루트 53px)에서 Markdown 인용·목록 안의 긴 줄(아래 한계) |

## 구현 방식(Exact 기능 사용 근거)

- 뷰는 Contract(`book/app.contract`), 데이터는 `book/app.ts`(`grants = ''`, 네트워크 권한 없음). 본문은 `content/*.md`를 `tools/gen-book.ts`가 `book.gen.ts`로 바꿔 `app.ts`가 제공한다.
- 문단·목록·표·인용은 `text … markup="markdown"`(long-text 레시피대로 블록마다 `text` 하나), 제목은 `role="heading" aria-level` + `id`(소목차 `#s1` 링크), 코드 복사는 호스트 명령 `copyText`, 해설은 `state open` + `button aria-expanded aria-controls`, 장·절 이동은 `link href=path("read", id)`와 `routes`.
- 반응형은 `exactViewport()`의 폭으로 `display`만 바꾼다(구조는 같게). 모바일 목차 패널은 상태(`tocOpen`)로 연다.

## 막힌 점과 해결(공식 문서·도구 범위 안에서)

1. **포트 충돌**: 패턴의 스탠드인 API 포트 8787을 기존 학습 앱 서버가 쓰고 있었다. 기존 서버는 건드리지 않고 `.env`를 8797로 바꿨다. 이후 학습북은 API가 필요 없어 `server.ts`, `.env`, `app.json`의 `env`를 지웠다.
2. **목록-상세 분할**: 홈의 링크 목록을 `list`로 쓰자 넓은 화면에서 절 페이지가 홈 옆에 분할로 붙었다(웹 룩 레시피의 "a list whose rows push sits beside its detail"). 링크 목록을 `column`으로 바꿔 해결.
3. **빌드 HTML 채택 실패**: 넓은 화면에서만 사이드 목차를 `if`로 넣자 `verify`가 `refused adopt: expected <nav>, found <main>`을 보고했다(빌드 HTML과 브라우저 트리의 구조 불일치). 사이드 목차와 목차 버튼을 항상 두고 `display`만 폭에 따라 바꿔 해결.
4. **verify 지적 수정**: px 글꼴 → rem, 24px 미만 링크 높이, 코드 줄이 상자를 넘치는 문제(`min-width="max-content"`로 코드 상자 안에서 가로 스크롤), `overflow-wrap="anywhere"` → `break-word`, 긴 URL 줄바꿈.
5. **`html lang`**: 기본값이 `en`이어서 `app.json`에 `"lang": "ko"`를 넣었다(스키마 `lang` 항목).
6. **Contract 제약**: `reduce`는 거부되어 `sum(xs.map(…))`, `option` 필드 접근은 `match`로 바꿨다. 테스트의 `at`은 테스트 첫 줄에만 둘 수 있어 테스트를 나눴다.

## 한계

- Docker 데몬이 꺼져 있어 4.4절 Dockerfile의 이미지 빌드는 실행하지 않았다(본문에 명시).
- 웹 타깃만 확인했다. iOS·macOS 등 네이티브 빌드는 이 작업의 범위가 아니다.
- 최대 글자 크기(루트 53px, 390px)에서 Markdown 인용·목록 안의 일부 줄이 16–61px 넘친다(Exact Markdown 렌더러 내부 들여쓰기, 앱 쪽 `overflow-wrap="break-word"`로 해결되지 않음).
- `verify`의 접근성 트리 읽기는 200자를 넘는 이름·값이 잘려 "coverage incomplete"로 표시된다(긴 본문 문단 때문, 발견 사항 0건).
- 빌드 결과 JS는 약 650KB(본문 데이터 포함, 압축 전). 각 페이지 HTML은 빌드 시 완성되어 스크립트 전에도 읽을 수 있다.
