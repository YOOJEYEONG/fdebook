# FDE 기술 학습북 (Expo Exact 웹)

Forward Deployed Engineer에게 필요한 기술을 페이지 안에서 배우는 한국어 교재다. 8장 36절, 각 절은 학습 목표·현장 상황·원리와 용어·예제(실행 코드 또는 분석 사례)·흔한 오류·연습문제와 해설·공식 출처(접근일)로 이루어진다. 예제 31개는 Python 3 표준 라이브러리만 쓰며 외부 계정이나 유료 API가 필요 없다.

기존 저장소의 학습 공간(루트의 Rust 앱, `content/course.json`)과는 별개이며 그것을 바꾸지 않는다.

## 준비

Expo Exact는 릴리스가 없어 공식 저장소를 고정 커밋으로 받아 경로로 쓴다. 자세한 근거와 출력은 `../docs/exact-feasibility.md`.

```sh
curl -fsSL https://bun.sh/install | BUN_INSTALL=~/.bun-1.4.2 bash -s bun-v1.4.2
export PATH=~/.bun-1.4.2/bin:$PATH EXACT_FEEDBACK=0
git clone https://github.com/expo/exact.git ../.cache-ext/exact
git -C ../.cache-ext/exact checkout de212e671a69f4fea18bed67d5b73b259ddf3061
(cd ../.cache-ext/exact && bun scripts/exact.mjs setup --platform web)
```

## 실행

```sh
bun run build                         # 본문 생성(tools/gen-book.ts) 후 dist/에 정적 사이트 빌드
bun exact.mjs serve dist --port 8770  # http://127.0.0.1:8770/
```

예제는 이 폴더에서 `python3 examples/…` 로 실행한다(각 절에 명령과 기대 출력이 있다).

## 검사

```sh
bun tools/run-examples.ts --repeat 5    # 본문이 참조하는 예제를 모두 5회씩 실행해 *.out과 비교 → examples/verified.json
bun tools/gen-book.ts                   # 절마다 필수 제목 7개, 문제 2개 이상, 출처 링크가 있는지 검사
bun exact.mjs test web                  # app.test.contract: 목차, 직접 URL, 이전/다음, 해설, 코드 복사, 모바일 목차, 키보드, 404
bun exact.mjs verify                    # 위 테스트 + 화면·접근성·새로고침 검사
bun tools/browser-qa.ts http://127.0.0.1:8770   # 서버 실행 중: 37개 경로 × 320/375/1280px, 콘솔 오류, 가로 넘침, Tab 순서
```

## 구조

```text
content/NN-NN-*.md     절 원문(Markdown). ::example(실행 예제) ::file(파일 표시) ::quiz/::answer/::end(문제·해설)
content/chapters.json  장 제목과 소개
examples/              실행 예제와 기대 출력(*.out)
tools/gen-book.ts      원문 → book.gen.ts, 구조 검사
tools/run-examples.ts  예제 실행·대조
tools/browser-qa.ts    실제 Chromium 점검
book.gen.ts            생성 파일(직접 고치지 않는다)
app.ts                 Exact 데이터 모듈(네트워크 권한 없음)
app.contract           Exact 뷰: 홈, /read/:id, 404
app.test.contract      Exact 테스트
```

새 절을 추가하려면 `content/`에 파일을 만들고(앞부분에 `id`, `chapter`, `number`, `title`, `summary`), 실행 예제는 `bun tools/run-examples.ts --record`로 출력을 기록한 뒤 **직접 읽어 확인**하고, `bun run build`로 다시 빌드한다.
