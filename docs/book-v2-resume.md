# Exact 학습북 재개 지점

> 2026-11-17 재개 후 완료. 최종 상태는 `docs/book-v2-status.md`와 `docs/book-v2-qa.md`. 아래는 중단 당시 기록이다.

Opus 5.5 세션: `85b36578-9654-4847-aa39-ec8c88d99a98`.
2026-11-17 작업 중 Claude Code에서 `You've hit your 5-hour limit · resets 3:20pm (Asia/Seoul)` 반환. 작업은 미완료이며 기존 배포는 교체하지 않았다.

## 완료 또는 진행 결과
- 새 설계: docs/book-v2-plan.md.
- 기술 자료 조사: docs/book-v2-research.md.
- 별도 조사·검토 역할의 결과: docs/book-v2-source-audit.md. 본문 대조와 접속만 확인한 출처를 구분한다. 재개 시 이 문서를 반드시 읽고 현재 교재와 대조할 것.
- Exact 고정 커밋 및 환경: docs/book-v2-status.md 참조. 프로젝트는 book/, 공식 저장소 캐시는 .cache-ext/exact. 웹 타깃 기본 테스트 6개 통과.
- 교재 본문 Markdown 20개 절 작성. 직전 보고 기준 예제 20개가 예상 출력과 일치했다. 이 숫자는 전체 책의 완료를 의미하지 않는다.
- AI 장 예제 작성 중 한도 도달. 마지막 작업은 ch6 검색 예제 수정 및 AI 공식 문서 확인이었다.

## 재개 순서
1. docs/book-v2-plan.md, book/AGENTS.md 및 진행 상태를 다시 읽고 실제 파일을 확인한다.
2. docs/book-v2-source-audit.md와 기존 원고의 기술 주장·출처 버전·표준/초안 구분을 대조한다. 출처 확인만 한 내용을 검증됐다고 간주하지 않는다.
3. 6장 AI FDE, 1장 업무·사고, 7장 고객 커뮤니케이션, 8장 종합 예제 본문을 완결한다. 설명·예제·문제·해설이 없는 절을 빈 목차로 남기지 않는다.
4. 모든 예제를 실행하고 교재의 출력과 대조한다. Docker 환경 등 미검증 항목은 구분한다.
5. 최종 콘텐츠 생성과 Exact 웹 빌드. 초기 시안의 홈 분할 문제는 column 전환으로 수정했다고 진행 문서에 기록되어 있으므로 최종 원고에서도 재발하지 않는지 확인한다. 코드 복사·해설·고유 URL·이전다음·모바일 목차를 확인한다.
6. 320/375/1280px, 키보드, 본문·코드 overflow, 직접 URL/새로고침, 브라우저 오류를 검증한다. book-v2-qa.md와 exact-feasibility.md에 근거를 작성한다.
7. 전체 책을 로컬에서 실행하고 주소와 스크린샷을 보고한다. 기존 배포/개인 기록은 유지한다. Opus는 git commit/push/deploy하지 않는다.
8. 후속 Git 준비에서 `.cache-ext/`, book 빌드 산출물·로컬 상태·비밀값은 올리지 않는다. Exact 고정 커밋과 환경 재현 명령은 소스로 기록한다.

## CLI 재개
작업 디렉터리에서 `claude --model claude-opus-5-5 --resume 85b36578-9654-4847-aa39-ec8c88d99a98`로 대화를 열 수 있다. 한도 초기화 전에는 구현 작업을 진행할 수 없다.
