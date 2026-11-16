# 프로덕션 QA

- 날짜: 2026-11-16 (브라우저 검사 시작 08:41:18 UTC)
- URL: https://fdebook.vercel.app (전달받은 정보: GitHub main 830a51c, Vercel READY)
- 수행: Opus 5.5. 소스는 수정하지 않았습니다.
- 방법: `tools/browser-qa.mjs`를 세션 임시 폴더로 복사해 `BASE`만 프로덕션 URL로 바꾸고, 헤드리스 Chrome의 **새 임시 프로필**로 실행했습니다. 사용자의 실제 브라우저 기록은 쓰지 않았습니다.

## 결과

| 항목 | 결과 |
|---|---|
| 브라우저 검사 (복사본 `browser-qa.mjs`) | **68/68 통과** |
| 서버 라우트 (curl) | 페이지 10개, `/weeks/12`는 200. `/weeks/13`, `/weeks/abc`, `/nope`는 404. `/favicon.ico`는 204 |
| 정적 파일 | `/static/app.css`, `/static/app.js`, `/static/logic.js` 200. SHA-256이 로컬 파일과 같음 |
| 보안 헤더 (페이지) | CSP, `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer` 확인 |

브라우저 검사에 포함된 주요 항목:
- 375·1280px 페이지 11개 가로 넘침 0, 콘솔 오류·CSP 위반 0
- 체크 → 새로고침 후 체크·자기평가·메모 복원, 메모 HTML이 실행되지 않고 텍스트로 출력
- 메모 입력 직후 이동해도 저장
- 백업 파일 실제 다운로드 → 잘못된 백업(버전 2, 알 수 없는 과제 ID) 거부 및 데이터 보존 → 초기화 → 가져오기 후 데이터 동일
- 손상 저장 데이터 보호와 백업으로 복구
- 두 탭 동시 수정(같은 과제의 다른 필드 포함)이 서로 덮지 않음
- 키보드(건너뛰기 링크, Tab·Space로 체크), 설정·경로 전환, 근거 자료 경력 필터, 지원·면접 기록

## 발견 사항 (실패 아님)

1. **저장소 파일 일부가 공개 정적 파일로 제공됨 (낮음).**
   - 200으로 열리는 것: `/src/lib.rs`, `/docs/design.md`, `/tools/browser-qa.mjs`, `/skills-lock.json`, `/content/course.json`, `/static/logic.test.mjs`, `/Cargo.toml`.
   - 404인 것: 원시 로그(`docs/opus-*`), `.gitignore`, `.vercelignore`, `README.md`, `api/fde.rs`, `vercel.json`, `.agents/` 아래 파일.
   - 비밀값은 없지만 의도한 공개 범위는 아닙니다.
   - 권고: 공개 출력 디렉터리를 따로 지정하거나, 배포 업로드에서 빌드에 필요 없는 `docs/`, `tools/`, `skills-lock.json` 등을 제외합니다. `src/`, `content/`, `static/`은 빌드에 필요하므로 업로드에서 빼면 안 됩니다. 변경 후 Vercel 빌드로 확인이 필요합니다.
2. **`/static/*`는 함수가 아니라 Vercel이 정적 파일로 직접 제공함 (낮음).**
   - Content-Type이 서버 설정(`text/javascript`)이 아닌 `application/javascript; charset=utf-8`이고, 이 응답에는 CSP·nosniff 헤더가 없습니다.
   - 페이지 자체의 CSP는 적용되므로 동작과 보안 정책에는 영향이 없었습니다.

## 한계

- Chrome 헤드리스 한 종류만 확인했습니다. Safari, Firefox, 실제 모바일 기기, 화면 리더는 확인하지 않았습니다.
- 콜드 스타트 지연이나 부하는 측정하지 않았습니다.
- 배포 커밋(830a51c)과 Vercel 상태는 전달받은 정보이며 직접 확인하지 않았습니다. 정적 파일은 로컬 작업본과 해시가 같았습니다.
- 브라우저 검사의 첫 방문 항목은 임시 프로필 기준입니다. 배포 도메인에 기존 기록이 있는 사용자의 화면은 확인 대상이 아닙니다.
