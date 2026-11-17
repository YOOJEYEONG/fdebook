# fdebook

Forward Deployed Engineer에게 필요한 기술을 페이지 안에서 배우는 한국어 교재 **FDE 기술 학습북**(8장 36절)입니다. [Expo Exact](https://github.com/expo/exact)로 만든 정적 웹사이트이며 소스는 `book/`에 있습니다. 취업을 보장하지 않습니다.

## 학습북

- 빌드·검사·구조: `book/README.md`
- Exact 고정 커밋(`de212e671a69f4fea18bed67d5b73b259ddf3061`)과 재현 근거: `docs/exact-feasibility.md`
- 배포(Vercel Git 빌드): `docs/book-v2-deployment.md`

```sh
export PATH=~/.bun-1.4.2/bin:$PATH EXACT_FEEDBACK=0
cd book
bun run build                         # dist/에 정적 사이트
bun exact.mjs serve dist --port 8770  # http://127.0.0.1:8770/
```

## 배포 요약

`main`에 푸시하면 Vercel Git 빌드가 `vercel.json`의 `bash book/tools/vercel-build.sh`를 실행합니다. 이 스크립트는 Bun 1.4.2, Exact 고정 커밋, Exact 공식 `setup --platform web`(Rust·wasm 도구)을 준비하고 `book`을 빌드한 뒤 `book/tools/vercel-output.ts`로 `dist/`만 `.vercel/output`(Build Output API v3)에 둡니다. 소스·예제·문서·캐시·환경 파일은 배포되지 않습니다.

## 이전 학습 앱(Rust, 배포 안 함)

12주 과정·면접 기록·지원 현황을 다루던 개인 학습 앱의 소스는 그대로 둡니다(`Cargo.toml`, `src/`, `api/fde.rs`, `content/course.json`, `static/`, `tools/browser-qa.mjs`). `.vercelignore`로 Vercel 업로드에서 빠지므로 더 이상 배포되지 않고, 로컬에서 실행합니다.

```sh
cargo run --release   # http://127.0.0.1:8787 (Rust 1.85 이상)
```

개인 기록은 브라우저 localStorage(`fde-study:v1`)에만 있고 서버·저장소에 올라가지 않습니다. 백업 파일(`fde-study-backup-*.json`)은 `.gitignore`·`.vercelignore`로 제외됩니다. 설계·조사·검증 기록은 `docs/`에 있습니다.
