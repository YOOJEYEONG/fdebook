// Chrome DevTools Protocol로 실제 브라우저 동작을 확인한다. 의존성 없음(Node 내장 WebSocket).
// 사용: node browser-qa.mjs <outDir>
import { spawn } from 'node:child_process';
import { mkdirSync, writeFileSync, readdirSync, readFileSync, rmSync } from 'node:fs';
import { join } from 'node:path';

const OUT = process.argv[2];
const BASE = 'http://127.0.0.1:8787';
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PROFILE = join(OUT, 'profile');
const DL = join(OUT, 'downloads');
rmSync(PROFILE, { recursive: true, force: true });
rmSync(DL, { recursive: true, force: true });
mkdirSync(DL, { recursive: true });

const chrome = spawn(CHROME, [
  '--headless=new', '--remote-debugging-port=9333', `--user-data-dir=${PROFILE}`,
  '--no-first-run', '--no-default-browser-check', 'about:blank',
], { stdio: 'ignore' });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let targets;
for (let i = 0; i < 50; i++) {
  try { targets = await (await fetch('http://127.0.0.1:9333/json')).json(); if (targets.some((t) => t.type === 'page')) break; } catch {}
  await sleep(200);
}
const page = targets.find((t) => t.type === 'page');
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener('open', r, { once: true }));

let seq = 0;
const pending = new Map();
const consoleErrors = [];
ws.addEventListener('message', (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Runtime.exceptionThrown') consoleErrors.push(m.params.exceptionDetails.exception?.description ?? m.params.exceptionDetails.text);
  if (m.method === 'Log.entryAdded' && m.params.entry.level === 'error') consoleErrors.push(m.params.entry.text);
  if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') consoleErrors.push(JSON.stringify(m.params.args));
  if (m.method === 'Page.javascriptDialogOpening') send('Page.handleJavaScriptDialog', { accept: true });
});
function send(method, params = {}) {
  const id = ++seq;
  ws.send(JSON.stringify({ id, method, params }));
  return new Promise((r) => pending.set(id, (m) => r(m.result ?? m)));
}
const evalJs = async (expr) => {
  const r = await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true });
  if (r.exceptionDetails) throw new Error(`eval failed: ${expr}\n${r.exceptionDetails.exception?.description}`);
  return r.result.value;
};
async function go(path) {
  await send('Page.navigate', { url: BASE + path });
  for (let i = 0; i < 50; i++) { await sleep(100); if (await evalJs('document.readyState') === 'complete') break; }
  await sleep(250); // 모듈 스크립트 실행 대기
}
async function viewport(width, height = 900) {
  await send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: width < 600 });
}
async function shot(name) {
  const r = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
  writeFileSync(join(OUT, `${name}.png`), Buffer.from(r.data, 'base64'));
}
async function key(k, code, keyCode, text) {
  await send('Input.dispatchKeyEvent', { type: 'keyDown', key: k, code, windowsVirtualKeyCode: keyCode, text });
  await send('Input.dispatchKeyEvent', { type: 'keyUp', key: k, code, windowsVirtualKeyCode: keyCode });
}
const tab = () => key('Tab', 'Tab', 9);
const stored = () => evalJs(`localStorage.getItem('fde-study:v1')`);

const results = [];
function check(name, ok, detail = '') {
  results.push({ name, ok: Boolean(ok), detail: String(detail) });
  console.log(`${ok ? 'PASS' : 'FAIL'} ${name}${detail ? ` — ${detail}` : ''}`);
}

await send('Page.enable');
await send('Runtime.enable');
await send('Log.enable');
await send('Browser.setDownloadBehavior', { behavior: 'allow', downloadPath: DL });

const PAGES = ['/', '/weeks', '/weeks/1', '/weeks/7', '/map', '/project', '/interview', '/applications', '/evidence', '/settings', '/nope'];

// 1. 375px / 1280px 넘침 검사 + 스크린샷
for (const w of [375, 1280]) {
  await viewport(w);
  for (const p of PAGES) {
    const errs = consoleErrors.length;
    await go(p);
    if (p === '/nope') consoleErrors.splice(errs); // 의도된 404
    const over = await evalJs('document.documentElement.scrollWidth - window.innerWidth');
    check(`${w}px ${p} 가로 넘침 없음`, over <= 0, `scrollWidth-innerWidth=${over}`);
  }
  for (const p of ['/', '/weeks/1', '/settings', '/evidence']) {
    await go(p);
    await shot(`${w}${p === '/' ? '-home' : p.replaceAll('/', '-')}`);
  }
}
check('페이지 순회 중 콘솔 오류·CSP 위반 없음', consoleErrors.length === 0, consoleErrors.join(' | '));

// 2. 첫 방문: 오늘의 과제
await viewport(1280);
await go('/');
check('첫 방문 오늘의 과제가 1주차 첫 과제', (await evalJs(`document.querySelector('#today h2')?.textContent`)) === '공고 원문 9건 직접 읽기');
check('첫 방문 설정 안내 표시', await evalJs(`!!document.querySelector('#today .tip')`));

// 3. 키보드: 건너뛰기 링크 → 본문, Tab으로 체크박스 → Space
await go('/weeks/1');
await tab();
check('첫 Tab은 본문 건너뛰기 링크', (await evalJs('document.activeElement.className')) === 'skip');
await key('Enter', 'Enter', 13, '\r');
await sleep(100);
check('건너뛰기 링크 Enter 후 본문으로 이동', (await evalJs('location.hash')) === '#main');
let reached = false;
for (let i = 0; i < 40; i++) {
  await tab();
  if (await evalJs(`document.activeElement.id === 'w1-read-done'`)) { reached = true; break; }
}
check('Tab만으로 첫 과제 체크박스 도달', reached);
const outline = await evalJs(`getComputedStyle(document.activeElement).outlineStyle`);
check('키보드 포커스 표시(outline) 있음', outline !== 'none', outline);
await shot('1280-keyboard-focus');
await key(' ', 'Space', 32, ' ');
await sleep(200);
check('Space로 체크', await evalJs(`document.getElementById('w1-read-done').checked`));
check('체크 저장 안내 표시', (await evalJs(`document.querySelector('#w1-read .saved').textContent`)) === '체크를 저장했습니다');

// 4. 자기평가·메모 후 새로고침 복원
await evalJs(`(() => { const s = document.getElementById('w1-read-rating'); s.value = 'met'; s.dispatchEvent(new Event('change')); })()`);
await evalJs(`(() => { const t = document.getElementById('w1-read-note'); t.value = '<img src=x onerror="window.__xss=1">메모'; t.dispatchEvent(new Event('input')); })()`);
await sleep(900);
await go('/weeks/1');
check('새로고침 후 체크 복원', await evalJs(`document.getElementById('w1-read-done').checked`));
check('새로고침 후 자기평가 복원', (await evalJs(`document.getElementById('w1-read-rating').value`)) === 'met');
check('새로고침 후 메모 복원(텍스트 그대로)', (await evalJs(`document.getElementById('w1-read-note').value`)).startsWith('<img'));
await go('/');
check('홈 다음 과제가 두 번째 과제로 이동', (await evalJs(`document.querySelector('#today h2').textContent`)) === '내 역량 차이표 만들기');
check('홈 체크/자기평가 따로 집계', (await evalJs(`[document.getElementById('stat-done').textContent, document.getElementById('stat-met').textContent].join('|')`)) === '1 / 30|1 / 30');

// 5. 설정 저장과 경로 전환
await go('/settings');
await evalJs(`(() => { const f = document.getElementById('settings-form'); f.elements.experienceYears.value = '3'; f.elements.hoursPerWeek.value = '5'; f.querySelector('input[value=data]').checked = true; f.requestSubmit(); })()`);
await sleep(200);
const s1 = JSON.parse(await stored()).settings;
check('설정 저장', s1.experienceYears === 3 && s1.hoursPerWeek === 5 && s1.track === 'data', JSON.stringify(s1));
await evalJs(`(() => { const f = document.getElementById('settings-form'); f.elements.hoursPerWeek.value = '0'; f.requestSubmit(); })()`);
await sleep(150);
check('잘못된 주당 시간 거부', (await evalJs(`!document.getElementById('st-error').hidden`)) && JSON.parse(await stored()).settings.hoursPerWeek === 5);
await go('/weeks/7');
check('대체 경로 선택 시 LLM 과제가 경로 밖 표시', await evalJs(`document.getElementById('w7-classify').classList.contains('off-track') && !document.getElementById('w7-pipeline').classList.contains('off-track')`));

// 6. 근거 자료 경력 필터
await go('/evidence');
const before = await evalJs(`document.querySelectorAll('.posting:not([hidden])').length`);
await evalJs(`(() => { const b = document.querySelector('input[name=exp]'); b.click(); })()`);
const after = await evalJs(`[...document.querySelectorAll('.posting:not([hidden])')].map(p => p.id).join(',')`);
check('경력 3년 필터: 1~2년 요구 공고만 표시', after === 'R1,R7,R8,R9', `${before}건 → ${after}`);

// 7. 지원 기록: 잘못된 URL 거부, 정상 추가, 메모 텍스트 출력
await go('/applications');
await evalJs(`(() => { const f = document.getElementById('app-form'); f.elements.company.value = '테스트사'; f.elements.url.value = 'javascript:alert(1)'; f.requestSubmit(); })()`);
await sleep(150);
check('javascript: URL 지원 기록 거부', (await evalJs(`!document.getElementById('ap-error').hidden && document.querySelectorAll('#app-list li').length === 0`)));
await evalJs(`(() => { const f = document.getElementById('app-form'); f.elements.url.value = 'https://example.com/job'; f.elements.memo.value = '<img src=x onerror="window.__xss=1">'; f.requestSubmit(); })()`);
await sleep(150);
check('지원 기록 추가', (await evalJs(`document.querySelectorAll('#app-list li').length`)) === 1);
check('메모 HTML이 실행되지 않고 텍스트로 출력', await evalJs(`!document.querySelector('#app-list img') && document.querySelector('#app-list .note').textContent.startsWith('<img') && !window.__xss`));
await evalJs(`document.querySelector('#app-list button.secondary').click()`);
await evalJs(`(() => { const f = document.getElementById('app-form'); f.elements.status.value = 'interview'; f.requestSubmit(); })()`);
await sleep(150);
check('지원 기록 수정', JSON.parse(await stored()).applications[0].status === 'interview');

// 8. 면접 기록
await go('/interview');
await evalJs(`(() => { const f = document.getElementById('interview-form'); f.elements.type.value = 'demo'; f.elements.score.value = 'weak'; f.elements.note.value = '숫자 없이 설명함'; f.requestSubmit(); })()`);
await sleep(150);
check('면접 기록 추가', (await evalJs(`document.querySelectorAll('#interview-list li').length`)) === 1);

// 9. 백업 내보내기
await go('/settings');
const snapshot = await stored();
await evalJs(`document.getElementById('export').click()`);
let file;
for (let i = 0; i < 30 && !file; i++) { await sleep(200); file = readdirSync(DL).find((f) => f.endsWith('.json')); }
check('백업 파일 다운로드', file, file);
const backupPath = join(DL, file);
const backup = JSON.parse(readFileSync(backupPath, 'utf8'));
check('백업에 현재 데이터 포함', JSON.stringify(backup.data) === snapshot);

// 10. 잘못된 백업: 기존 데이터 보존
const badPath = join(OUT, 'bad-backup.json');
writeFileSync(badPath, JSON.stringify({ ...backup, version: 2 }));
const unknownIdPath = join(OUT, 'unknown-id-backup.json');
writeFileSync(unknownIdPath, JSON.stringify({ ...backup, data: { ...backup.data, tasks: { 'w99-x': backup.data.tasks['w1-read'] } } }));
const doc = await send('DOM.getDocument');
const setFile = async (path) => {
  const { nodeId } = await send('DOM.querySelector', { nodeId: (await send('DOM.getDocument')).root.nodeId, selector: '#import-file' });
  await send('DOM.setFileInputFiles', { nodeId, files: [path] });
  await sleep(300);
};
void doc;
for (const [label, p] of [['버전 2', badPath], ['알 수 없는 과제 ID', unknownIdPath]]) {
  await setFile(p);
  check(`잘못된 백업(${label}) 거부 메시지`, (await evalJs(`document.getElementById('import-result').textContent`)).includes('가져올 수 없는 백업'));
  check(`잘못된 백업(${label}) 후 적용 버튼 숨김·데이터 보존`, (await evalJs(`document.getElementById('import-apply').hidden`)) && (await stored()) === snapshot);
}
await shot('1280-settings-bad-backup');

// 11. 초기화 후 백업 가져오기 왕복
await evalJs(`document.getElementById('reset').click()`);
await sleep(200);
check('초기화', JSON.parse(await stored()).applications.length === 0);
await go('/settings');
await setFile(backupPath);
check('정상 백업 검사 통과 안내', (await evalJs(`document.getElementById('import-result').textContent`)).includes('검사 통과'));
await evalJs(`document.getElementById('import-apply').click()`);
await sleep(200);
check('백업 왕복 후 데이터 동일', (await stored()) === snapshot);

// 12. 손상된 저장 데이터: 덮어쓰지 않음
await evalJs(`localStorage.setItem('fde-study:v1', '{깨진 데이터')`);
await go('/weeks/1');
check('손상 데이터 경고 표시', await evalJs(`!document.getElementById('notice').hidden`));
await evalJs(`document.getElementById('w1-gap-done').click()`);
await sleep(200);
check('손상 데이터 상태에서 저장하지 않고 원본 보존', (await stored()) === '{깨진 데이터');
check('저장 실패 시 체크 되돌림', !(await evalJs(`document.getElementById('w1-gap-done').checked`)));
await shot('1280-corrupt-notice');
await go('/settings');
check('손상 원본 내려받기 버튼 표시', await evalJs(`!document.getElementById('download-raw').hidden`));
await setFile(backupPath);
await evalJs(`document.getElementById('import-apply').click()`);
await sleep(200);
check('손상 상태에서 백업 가져오기로 복구', (await stored()) === snapshot);

// 13. 375px 메뉴 키보드 이동
await viewport(375);
await go('/');
await tab(); await tab(); await tab();
check('375px 세 번째 Tab은 상단 메뉴 첫 링크', (await evalJs(`document.activeElement.closest('nav')?.getAttribute('aria-label')`)) === '학습 메뉴');
await shot('375-home-after');

check('전체 시나리오 중 콘솔 오류 없음', consoleErrors.length === 0, consoleErrors.join(' | '));

writeFileSync(join(OUT, 'results.json'), JSON.stringify(results, null, 2));
const failed = results.filter((r) => !r.ok).length;
console.log(`\n${results.length - failed}/${results.length} 통과`);
ws.close();
chrome.kill();
process.exit(failed ? 1 : 0);
