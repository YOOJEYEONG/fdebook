// dist/ → ../.vercel/output (Vercel Build Output API v3). Only dist/ is copied, so
// `vercel deploy --prebuilt` publishes nothing else. Run after `bun run build`.
import { cpSync, existsSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { Glob } from 'bun';

const dist = new URL('../dist/', import.meta.url).pathname;
const out = new URL('../../.vercel/output/', import.meta.url).pathname;
if (!existsSync(`${dist}index.html`) || !existsSync(`${dist}404.html`)) throw new Error('no dist/: run bun run build first');

rmSync(out, { recursive: true, force: true });
cpSync(dist, `${out}static`, { recursive: true });

// Exact names content-hashed files in routes.json `files`; those may be cached for good.
const hashed = Object.values(JSON.parse(readFileSync(`${dist}routes.json`, 'utf8')).files as Record<string, string>);
const esc = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

// read/<id>/index.html answers /read/<id> (the app's links have no trailing slash).
const overrides: Record<string, { path: string }> = {};
for (const file of new Glob('**/index.html').scanSync({ cwd: dist, dot: true }))
  if (file !== 'index.html') overrides[file] = { path: file.slice(0, -'/index.html'.length) };

const security = {
  'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'X-Frame-Options': 'DENY',
  'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
  'Strict-Transport-Security': 'max-age=63072000',
};

writeFileSync(`${out}config.json`, JSON.stringify({
  version: 3,
  overrides,
  routes: [
    { src: '^/(.*)$', headers: security, continue: true },
    { src: `^/(${hashed.map(esc).join('|')})$`, headers: { 'Cache-Control': 'public, max-age=31536000, immutable' }, continue: true },
    { src: '^/(.+)/$', status: 308, headers: { Location: '/$1' } },
    { handle: 'filesystem' },
    { src: '^/.*$', dest: '/404.html', status: 404 },
  ],
}, null, 2) + '\n');

console.log(`.vercel/output: ${Object.keys(overrides).length} page paths, ${hashed.length} immutable files`);
