// Runs every `::example` the content names and compares its stdout with the expected `.out` beside it.
// Run: bun tools/run-examples.ts           (compare; writes examples/verified.json)
//      bun tools/run-examples.ts --record  (write a missing .out from the run, for the author to review)
//      bun tools/run-examples.ts --repeat 5 (run each example 5 times: an example that passes only sometimes fails)
import { readdirSync, readFileSync, writeFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';

const root = join(import.meta.dir, '..');
const record = process.argv.includes('--record');
const repeatAt = process.argv.indexOf('--repeat');
const repeat = repeatAt > 0 ? Number(process.argv[repeatAt + 1]) : 1;
const specs = readdirSync(join(root, 'content')).filter(f => f.endsWith('.md')).sort()
  .flatMap(f => readFileSync(join(root, 'content', f), 'utf8').split('\n').filter(l => l.startsWith('::example ')).map(l => l.slice(10)));

const report: Record<string, { ok: boolean; command: string; note: string; runs: number }> = {};
let failed = 0;
for (const spec of specs) {
  const [file, cmd] = spec.split('|').map(s => s.trim());
  const command = cmd ?? `python3 examples/${file}`;
  const outPath = join(root, 'examples', file.replace(/\.[^.]+$/, '.out'));
  let note = '';
  for (let n = 1; n <= repeat && (note === '' || note === 'recorded'); n++) {
    const run = Bun.spawnSync(['/bin/sh', '-c', command], { cwd: root, env: { ...process.env, PYTHONHASHSEED: '0', PYTHONDONTWRITEBYTECODE: '1' }, timeout: 60_000 });
    const out = run.stdout.toString().replace(/\s+$/, '');
    const at = repeat > 1 ? ` on run ${n}` : '';
    if (run.exitCode !== 0) note = `exit ${run.exitCode}${at}: ${run.stderr.toString().trim().split('\n').at(-1)}`;
    else if (!existsSync(outPath)) {
      if (record) { writeFileSync(outPath, out + '\n'); note = 'recorded'; } else note = 'no .out';
    } else if (readFileSync(outPath, 'utf8').replace(/\s+$/, '') !== out) note = `output differs${at}`;
  }
  const ok = note === '' || note === 'recorded';
  if (!ok) failed++;
  report[file] = { ok, command, note, runs: repeat };
  console.log(`${ok ? 'ok  ' : 'FAIL'} ${command}${note ? `  (${note})` : ''}`);
}
writeFileSync(join(root, 'examples', 'verified.json'), JSON.stringify(report, null, 2) + '\n');
console.log(`${specs.length - failed}/${specs.length} examples match their expected output`);
process.exit(failed ? 1 : 0);
