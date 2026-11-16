# FDE 학습 공간

Forward Deployed Engineer 전환을 위한 개인 학습 페이지입니다. 12주 과정(가상 고객 A물류 사례), 역량 지도, 면접 연습 기록, 지원 현황, 공고 근거 자료를 한국어로 제공합니다. 취업을 보장하지 않으며, FDE가 일반 개발자보다 취업이 쉽다는 근거는 확인하지 못했습니다(`docs/research.md`).

## 실행

필요: Rust 1.85 이상(edition 2024). 이 저장소는 rustc 1.100.0으로 확인했습니다. 설치는 https://rustup.rs 를 따릅니다.

```sh
cargo run --release
```

주소: http://127.0.0.1:8787

포트를 바꾸려면 `FDE_PORT=9000 cargo run --release`. 서버는 127.0.0.1에만 바인딩하며 외부 서비스를 호출하지 않습니다.

## 데이터 저장 위치

- 학습 콘텐츠: `content/course.json`. 빌드할 때 바이너리에 포함되므로 수정 후 다시 빌드해야 합니다. 서버는 시작할 때 주차 번호, 과제 ID 중복, 참조 무결성, URL 형식을 검사하고 실패하면 시작하지 않습니다.
- 개인 기록(진도 체크, 자기평가, 메모, 면접 기록, 지원 기록, 설정): 브라우저 localStorage의 `fde-study:v1` 키. 서버에는 저장하지 않습니다.
- 브라우저 저장소는 주소(origin)별로 따로입니다. `127.0.0.1:8787`과 `localhost:8787`은 서로 다른 저장 공간이므로 한 주소만 쓰세요.

## 백업

설정·백업 화면에서 진행합니다.

- 내보내기: "백업 파일 내보내기" 버튼을 누르면 `fde-study-backup-YYYY-MM-DD.json` 파일이 받아집니다.
- 가져오기: 파일을 고르면 앱 식별자, 백업 버전(1), 모든 필드 형식, 과제·면접 유형 ID, URL 형식을 검사합니다. 검사를 통과해야 "가져온 내용으로 바꾸기" 버튼이 나타나고, 실패하면 이유를 보여 주고 기존 데이터는 그대로 둡니다.
- 저장된 기록이 손상되어 읽을 수 없으면 경고를 띄우고 저장을 멈춥니다. 원본을 내려받은 뒤 초기화하거나 백업을 가져와 복구합니다.

## 검사

```sh
cargo fmt --check
cargo check
cargo clippy --all-targets -- -D warnings
cargo test                              # 콘텐츠 검증, HTML 이스케이프, 안전한 링크
node --test static/logic.test.mjs       # 진도 집계, 백업 검증, 잘못된 입력 거부
node tools/browser-qa.mjs <출력 폴더>    # 서버 실행 중. 헤드리스 Chrome으로 실제 화면 확인
```

`tools/browser-qa.mjs`는 macOS의 `/Applications/Google Chrome.app`과 Node 22 이상(내장 WebSocket)을 사용합니다. 임시 프로필을 쓰므로 평소 브라우저의 기록은 건드리지 않습니다. 결과와 스크린샷은 출력 폴더에 남습니다.

## 구조

```text
Cargo.toml            의존성: axum, tokio, serde, serde_json
src/main.rs           서버, 콘텐츠 검증, 페이지 렌더링, Rust 테스트
content/course.json   12주 과정, 역량, 면접 문항, 근거 공고, 통계
static/app.css        화면 스타일
static/logic.js       순수 로직(검증, 진도 집계). 브라우저와 node 검사가 공유
static/app.js         화면 동작과 localStorage 저장
static/logic.test.mjs 로직 검사
tools/browser-qa.mjs  브라우저 동작 확인 스크립트
docs/                 설계, 조사, 검증, 커리큘럼, QA 기록
```

# fdebook
