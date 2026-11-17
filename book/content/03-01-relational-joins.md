---
id: relational-joins
chapter: 3
number: 3.1
title: 관계 모델, 키, 조인
summary: 기본 키와 외래 키로 표를 잇고, INNER·LEFT JOIN과 자리표시자로 안전하게 질의하기.
---

## 학습 목표와 선수 개념

- 표·행·열, 기본 키, 외래 키가 무엇을 보장하는지 설명한다.
- INNER JOIN과 LEFT JOIN의 결과 차이를 예측하고, LEFT JOIN 조건 위치 실수를 피한다.
- 사용자 입력을 SQL 문자열에 붙이지 않고 자리표시자로 넘긴다.

선수 개념: 리스트와 딕셔너리. SQL은 처음이어도 된다.

## 현장 상황

고객사가 "고객별 미해결 문의 현황" 보고서를 원한다. 기존 담당자가 만든 보고서에는 문의가 없는 고객이 아예 빠져 있었다. 영업팀은 "문의가 0건인 고객"도 봐야 이탈 위험을 판단할 수 있다고 한다. 표 두 개를 어떻게 잇느냐의 차이가 업무 판단을 바꾸는 사례다. 공식 공고들도 Postgres·MySQL 같은 관계형 DB 경험을 FDE 요건으로 적는다(OpenAI FDSE 공고).

## 원리와 용어

**관계형 데이터베이스**는 데이터를 **표(table)**로 저장한다. 표의 각 **행(row)**은 하나의 대상(고객 한 명, 문의 한 건)이고, **열(column)**은 속성(이름, 상태)이다.

- **기본 키(primary key)**: 행을 하나로 특정하는 열. 중복과 빈 값을 허용하지 않는다. 예: `customers.id`.
- **외래 키(foreign key)**: 다른 표의 기본 키를 가리키는 열. `tickets.customer_id`는 `customers.id`를 가리킨다. DB가 "존재하지 않는 고객의 문의"를 막아 준다.
- **제약(constraint)**: `NOT NULL`, `CHECK`, `UNIQUE`처럼 DB가 강제하는 규칙. 애플리케이션 코드가 실수해도 잘못된 데이터가 저장되지 않게 하는 마지막 방어선이다.

**조인(JOIN)**은 키를 기준으로 두 표의 행을 이어 붙인다.

- **INNER JOIN**: 양쪽에 짝이 있는 행만 남긴다. 문의가 없는 고객은 사라진다.
- **LEFT JOIN**: 왼쪽 표의 행은 모두 남기고, 짝이 없으면 오른쪽 열을 `NULL`로 채운다. `COUNT(t.id)`는 `NULL`을 세지 않으므로 문의 없는 고객이 0이 된다.

**SQL 인젝션**: 사용자 입력을 문자열로 이어 붙여 SQL을 만들면, 입력에 따옴표와 조건을 섞어 질의의 의미를 바꿀 수 있다. Python `sqlite3` 문서는 문자열 연산으로 질의를 조립하지 말고 `?` 자리표시자에 값을 따로 넘기라고 명시한다. 자리표시자로 넘긴 값은 SQL 문법이 아니라 하나의 값으로만 취급된다.

## 예제: 고객과 문의

Python에 내장된 SQLite로 메모리 DB를 만들어 실습한다. 설치할 것이 없다.

::example ch3/joins.py

해설:

- 1번은 INNER JOIN이라 문의가 없는 `마바유통`이 나오지 않는다. 목적이 "열린 문의 목록"이면 맞는 결과다.
- 2번은 "고객별 현황"이므로 LEFT JOIN이 맞다. 상태 조건(`t.status = 'open'`)을 `ON` 절에 두어, 짝을 찾을 때만 적용했다.
- 3번은 같은 조건을 `WHERE`에 두었다. `WHERE`는 조인이 끝난 뒤 행을 거르므로 `t.status`가 `NULL`인 마바유통 행이 제거되어 INNER JOIN과 같아졌다. 보고서에서 고객이 사라지는 가장 흔한 원인이다.
- 4번에서 외래 키가 존재하지 않는 고객 99의 문의를 거부했다. SQLite는 `PRAGMA foreign_keys = ON`을 켜야 이 검사를 한다(다른 DB는 보통 기본으로 검사한다).
- 5번에서 문자열 조립은 `' OR '1'='1` 때문에 조건이 항상 참이 되어 3명을 돌려줬다. 자리표시자는 그 문자열 전체를 요금제 이름으로 보고 0명을 돌려준다.

## 흔한 오류와 디버깅

- **조인 후 행이 늘어남**: 한쪽 키가 유일하지 않으면 행이 곱해진다(고객 1명 × 문의 3건 = 3행). 합계가 이상하게 크면 조인 키의 유일성을 먼저 확인한다.
- **`COUNT(*)`와 `COUNT(열)` 혼동**: LEFT JOIN 뒤 `COUNT(*)`는 짝 없는 행도 1로 센다. 오른쪽 표의 열을 센다.
- **NULL 비교**: `x = NULL`은 참이 되지 않는다. `x IS NULL`을 쓴다.
- **보고서 숫자 검증**: 새 질의의 결과는 작은 표본을 손으로 세어 비교한다. 고객 3명·문의 4건처럼 손으로 확인할 수 있는 데이터를 만들어 두는 습관이 디버깅 시간을 줄인다.

## 이해 확인

::quiz
`SELECT c.name, COUNT(*) FROM customers c LEFT JOIN tickets t ON t.customer_id = c.id GROUP BY c.id`를 예제 데이터에 실행하면 마바유통의 값은 얼마인가? 왜 그런가?
::answer
1이다. LEFT JOIN은 문의가 없는 마바유통에도 오른쪽 열이 `NULL`인 행 하나를 만들고, `COUNT(*)`는 행 자체를 세므로 1이 된다. 문의 수를 원하면 `COUNT(t.id)`를 써야 0이 나온다.
::end

::quiz
검색창 입력으로 고객을 찾는 코드 `con.execute(f"SELECT * FROM customers WHERE name LIKE '%{q}%'")`를 안전하게 고쳐라.
::answer
값을 자리표시자로 넘기고, 와일드카드 `%`는 값 쪽에 붙인다: `con.execute("SELECT * FROM customers WHERE name LIKE ?", (f"%{q}%",))`. 사용자가 `%`나 `_`를 글자 그대로 찾게 하려면 `ESCAPE` 절로 이스케이프 규칙도 정한다.
::end

## 출처

- Python 문서 `sqlite3` — 자리표시자와 SQL 인젝션 경고. https://docs.python.org/3/library/sqlite3.html (접근일 2026-11-17)
- SQLite "SQLite Foreign Key Support" — 외래 키 검사는 `PRAGMA foreign_keys`로 켠다. https://www.sqlite.org/foreignkeys.html (접근일 2026-11-17)
- SQLite "SELECT" — JOIN과 WHERE 처리. https://www.sqlite.org/lang_select.html (접근일 2026-11-17)
- OpenAI Forward Deployed Software Engineer 공고 — 관계형 DB 경험 요건. https://jobs.ashbyhq.com/openai/00207abc-49b7-465c-a219-f7c1140f8047 (접근일 2026-11-17)
