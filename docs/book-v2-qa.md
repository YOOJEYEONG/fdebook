# 학습북 v2 QA 기록

확인일: 2026-11-17. 대상: `book/`(Expo Exact 웹, 고정 커밋 `de212e671a69f4fea18bed67d5b73b259ddf3061`). 환경과 재현 명령은 `docs/exact-feasibility.md`.

검증 주체: 집필과 같은 Opus 5.5 세션이 수행했다. **독립 검토가 아니다.** 자료 조사 감사(`docs/book-v2-source-audit.md`)도 같은 모델 계열의 별도 작업이다.

## 1. 본문 완결성

| 항목 | 결과 | 근거 |
|---|---|---|
| 장·절 | 8장 36절 | `bun tools/gen-book.ts` → `book.gen.ts: 8 chapters, 36 sections` |
| 절별 필수 구성 | 36절 모두 통과 | 생성기가 절마다 제목 7종(학습 목표·현장 상황·원리·예제·흔한 오류·이해 확인·출처), 문제 2개 이상, 출처 URL을 검사하고 하나라도 빠지면 빌드를 멈춘다 |
| 문제와 해설 | 76문제, 모두 해설 있음 | `::answer` 없는 문제는 생성기가 거부 |
| 코드 블록 | 49개(실행 예제 31, 표시용 파일·참고 코드 18) | `book.gen.ts` 집계 |
| 분량 | 본문·해설 약 19.8만 자 | `book.gen.ts` 집계 |
| 실행하지 않은 참고 코드 | 6.1·6.2의 Claude API 요청 모양(유료 키 필요), 4.4의 `docker build` 명령, 1.4의 분석용 함수 | 본문에 "실행하지 않은 참고 예시" 또는 "분석용"으로 표시 |

## 2. 예제 실행·출력 대조

```text
$ bun tools/run-examples.ts --repeat 5
...
31/31 examples match their expected output
```

- 각 예제를 5회 실행해 매번 `examples/**/*.out`과 바이트 단위로 같아야 통과(`examples/verified.json`에 `runs: 5`). 무작위 요소(지터, 합성 데이터, 카나리)는 씨앗을 고정했고 본문에 그 사실과 이유를 적었다.
- 기대 출력은 처음 실행 결과를 기록한 뒤 저자가 읽고 확인했다. 확인 중 고친 것: 오해를 부르는 출력 문구(2.3, 2.4, 4.4), 시연 의미가 약한 예제(3.3 결측 사례, 3.4 멱등 재실행, 3.5 키 없는 해시 공격, 5.2 가설 판정), 정규식 오류(6.5 이메일), 확률 표기(6.4 정밀도 정의 불가).
- 반복 실행으로 발견한 실제 버그: 2.2 예제 서버가 인증 실패 시 요청 본문을 읽지 않고 응답해 간헐적으로 `ConnectionResetError`. 수정 후 30회 연속 통과, 본문 "흔한 오류"에 사례로 추가.
- 미실행: 4.4 Dockerfile 이미지 빌드(Docker 데몬이 꺼져 있음, `failed to connect to the docker API`). 본문에 미실행이라고 적었다.
- 실행 환경: Python 3.15.0, SQLite 3.54.0. 외부 네트워크 없이 `127.0.0.1` 임시 포트만 사용.

## 3. 출처 확인

- 본문 출처 URL 80개(코드 속 예시 주소 2개 제외 78개)를 `curl -L`로 확인: 76개 HTTP 200. Palantir Lever 공고 2건은 최종 확인 시점에 500/시간 초과였다. 두 공고의 본문은 같은 날 앞서 Lever 공개 API로 받아 대조했다(`docs/book-v2-research.md` R5, R6).
- `book-v2-source-audit.md` 대조로 고친 것: MCP 판(2026-07-28로 고정, "상태 없는 요청·요청별 기능 협상"), 구조화 출력의 예외(`refusal`, `max_tokens`, enum 대소문자)와 `output_format` deprecated, Idempotency-Key·OAuth 2.1을 초안으로 표기, AWS 글은 표준이 아님을 표기, 12-Factor는 커뮤니티 방법론으로 표기, Actions는 커밋 SHA 고정과 `permissions: contents: read`, Stripe 문서 이동 주소, Python 3.12 `sqlite3` `autocommit` 함정, 정확도 함정과 정밀도 정의 불가, 1.1절의 표본·해석 한계 문단.
- 본문을 대조하지 못해 인용하지 않은 것: 개인정보 보호법 제3조·제16조 문구(조문 번호 인용 없음, 3.5절은 개인정보보호위원회의 가명정보 안내만 인용), Stripe 서명 허용 시간 수치(숫자를 쓰지 않음), Palantir "Dev versus Delta" 블로그(사용 안 함).
- 감사 문서에서 '접속'만 확인됐던 출처를 인용한 경우, 인용한 내용을 페이지 본문에서 직접 찾아 대조했다: Docker best practices의 `USER`, GitHub secure use의 전체 커밋 SHA·최소 권한·신뢰할 수 없는 입력, W3C Trace Context의 `traceparent`, RFC 9700 4.3.2(토큰을 URI 쿼리에 넣지 말 것), RFC 9457 3.2절(확장 멤버), scikit-learn cross-validation의 "methodological mistake… overfitting", SQLite 외래 키 기본 비활성, `socketserver` 문서의 포트 0.

## 4. Exact 테스트와 verify

```text
$ bun exact.mjs test web
test "the cover lists every chapter and opens a section": ok
test "a section opens at its own URL, and next and previous walk the book": ok
test "the first section has no previous": ok
test "the last section has no next": ok
test "an answer stays closed until asked for": ok
test "a code block copies its code and shows the output it printed": ok
test "a phone opens the table of contents from the header and a link closes it": ok
test "a wide window shows the table of contents beside the text": ok
test "a section id that does not exist says so, with a way home": ok
test "a path no route matches is the not-found page": ok
test "the keyboard reaches and works the header and the answers": ok
11 passed, 0 failed
```

`bun exact.mjs verify` 최종: 테스트 11/11, 390×844·1280×900 라이트·다크 화면 검사 0건, 접근성 트리 0건, 새로고침 0건, Contract verify 0건. 남은 것: 최대 글자 크기 2건(아래 한계). 처음 실행의 63건(px 글꼴 29, 링크 높이 14, 코드 넘침 2, 단어 끊김 2, 최대 글자 15, 빌드 HTML 채택 실패 1)은 `docs/exact-feasibility.md` "막힌 점"대로 고쳤다. 스크린샷: `book/.exact/verify/`.

## 5. 실제 브라우저 점검

`bun tools/browser-qa.ts http://127.0.0.1:8770`(Exact가 설치한 Playwright Chromium, 미리보기 서버 대상):

```text
pages checked: 111 (37 paths x 3 widths)
Tab stops at 375px on /read/fde-role: a:본문으로 -> a:FDE 기술 학습북 -> button:목차 -> a:학습 목표와 선수 개념 -> a:현장 상황
Enter on the 목차 button opens the panel: true
no problems
```

- 37개 경로(홈 + 36절) × 320/375/1280px: 모두 HTTP 200, 콘솔 오류 0, 페이지 가로 스크롤 0(긴 코드 줄은 코드 상자 안에서만 가로 스크롤), 모든 쪽에 1단계 제목.
- 직접 URL: `curl`로 36개 `/read/<id>` 모두 200, `/read/no-such`와 `/nope/x`는 404와 "없는 페이지". 각 절 HTML은 빌드 시 완성되어 스크립트 없이도 본문이 있다. `<html lang="ko">`.
- 키보드: Tab 순서가 건너뛰기 링크 → 홈 → 목차 버튼 → 소목차 순이고, 숨겨진(폭 1000px 미만) 사이드 목차는 Tab에 걸리지 않는다. 넓은 화면에서는 "본문으로" 링크로 사이드 목차 36개 링크를 건너뛴다.
- 스크린샷(`docs/book-v2-qa-shots/`): `final-home-1280.png`, `final-evaluation-example-1280.png`(사이드 목차·소목차 링크로 이동한 예제), `final-toc-open-375.png`(모바일 목차), `final-answer-open-375.png`(해설 열림), `final-code-320.png`(320px 코드 상자 내부 스크롤), Exact agent로 찍은 `home-*`, `capstone-build-*`, `webhooks-example-*`(320/375/1280).

## 6. 남은 한계

1. Docker 이미지 빌드 미실행(데몬 꺼짐).
2. 최대 글자 크기(루트 53px)에서 Markdown 인용·목록의 일부 줄이 16–61px 넘침(Exact Markdown 렌더러 내부 들여쓰기).
3. 6장 LLM 예제는 유료 API 대신 결정적 가짜 모델을 쓴다. 실제 모델의 확률적 출력, 비용, 지연은 이 책에서 측정하지 않았다(본문에 명시).
4. 6.3 검색 예제는 글자 2-gram 어휘 검색이며 의미 임베딩이 아니다(본문에 실패 사례와 함께 명시).
5. 8장 분류기는 합성 데이터에 과적합되어 있고, 새 표현 8건은 모두 사람 검토로 간다. 본문이 이를 결론(운영 전환 보류)으로 다룬다.
6. 검증은 같은 세션의 자체 검토다. 독립 검토(다른 사람·다른 모델)는 하지 않았다.
7. 빌드 JS 약 650KB(본문 포함). 페이지 HTML은 스크립트 전에도 완성되어 있다.
