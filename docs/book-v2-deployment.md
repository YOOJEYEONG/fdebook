# Exact 학습북 배포

대상: YOOJEYEONG/fdebook main → Vercel yoojeyeongs-projects/fdebook → https://fdebook.vercel.app.

## 배포 구조
- 교재 소스는 book/, Expo Exact는 de212e671a69f4fea18bed67d5b73b259ddf3061로 고정한다.
- vercel.json의 buildCommand는 `bash book/tools/vercel-build.sh`. 고정 Bun·Rust 등 공식 웹 도구를 준비하고 Exact로 book/dist를 생성한다.
- book/tools/vercel-output.ts가 dist만 .vercel/output/static으로 복사하고 Build Output API v3 설정을 만든다. 원고·소스·캐시·예제·비밀값은 웹 공개 대상이 아니다.
- 기존 Axum 앱 소스는 보존한다. 배포에서는 api/를 제외하여 이전 Rust 함수와 rewrite가 다시 활성화되지 않도록 한다.
- GitHub Actions 배포와 별도 VERCEL_TOKEN 설정은 사용하지 않는다. 기존 Vercel Git 연결로 main 푸시를 빌드한다.
- 내용 해시 파일은 immutable 캐시, 절 HTML은 재검증한다. 직접 절 URL, 404, 기본 보안 헤더는 생성된 output/config.json에 지정한다.

## 수동으로 검증된 산출물 배포
```sh
export PATH="$HOME/.bun-1.4.2/bin:$PATH" EXACT_FEEDBACK=0
(cd book && bun run build && bun tools/vercel-output.ts)
vercel deploy --prebuilt --prod --skip-domain --scope yoojeyeongs-projects
# 준비된 배포를 확인한 뒤
vercel promote <준비된 배포 URL> --yes --scope yoojeyeongs-projects
```

2026-11-17 검증된 정적 산출물 배포 dpl_37pWzcbTi99wEoyTutK9Bf7CCCHY를 공개 주소에 적용했다. 홈·절은 200, 없는 절·이전 API·소스 경로는 404를 확인했다. 이 단계는 새 native Git 원격 빌드의 성공을 뜻하지 않는다.

## 검증 기록과 제약
- Exact 빌드 및 테스트 11개는 로컬에서 통과했다. 전체 책의 품질 검증은 docs/book-v2-qa.md 참조.
- 별도 깨끗한 로컬 작업 디렉터리에서 웹 빌드가 성공했다. 캐시 없는 빌드는 약 122초였으며 wasm-opt가 없는 경우 wasm 최적화 크기에 차이가 있었다.
- 공식 setup 전체를 이용하는 native Git 빌드는 실제 Vercel Linux 빌드 로그로 확인한다. 처음에는 툴체인·Chromium 다운로드·Rust 컴파일 시간이 필요하다。
- 구성 담당 Opus가 native 빌드 검증 중 사용 한도에 도달했다. 최종 원격 빌드 결과는 후속 배포 확인 기록을 따른다.
- 기존 브라우저의 localStorage는 교체로 삭제하지 않는다. 예전 진도 관리 화면은 새 책에 포함하지 않는다.
