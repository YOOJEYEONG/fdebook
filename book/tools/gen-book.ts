// Turns content/*.md into book.gen.ts, the data app.ts serves, and checks each section's structure.
// Run: bun tools/gen-book.ts   (package.json's build runs it first)
import { readdirSync, readFileSync, writeFileSync, existsSync } from 'node:fs';
import { join, extname } from 'node:path';

const root = join(import.meta.dir, '..');
const contentDir = join(root, 'content');
const exampleDir = join(root, 'examples');

type Block = { id: number; seq: number; kind: string; text: string; anchor: string; lang: string; file: string; run: string; output: string; answer: string; verified: boolean };
type Heading = { id: string; title: string };
type Section = {
  id: string; number: string; title: string; chapter: number; chapterTitle: string; summary: string;
  blocks: Block[]; outline: Heading[];
  prevId: string; prevTitle: string; nextId: string; nextTitle: string; position: number; total: number;
};

const chapters: { number: number; title: string; intro: string }[] = JSON.parse(readFileSync(join(contentDir, 'chapters.json'), 'utf8'));
const verified: Record<string, { ok: boolean }> = existsSync(join(exampleDir, 'verified.json'))
  ? JSON.parse(readFileSync(join(exampleDir, 'verified.json'), 'utf8')) : {};

const REQUIRED = ['학습 목표', '현장 상황', '원리', '예제', '흔한 오류', '이해 확인', '출처'];
const LANG: Record<string, string> = { '.py': 'python', '.sql': 'sql', '.yml': 'yaml', '.yaml': 'yaml', '.sh': 'bash', '.json': 'json', '.csv': 'csv', '.txt': 'text', '.md': 'markdown' };
const langOf = (file: string) => file.endsWith('Dockerfile') ? 'dockerfile' : LANG[extname(file)] ?? 'text';
const block = (kind: string, text: string, more: Partial<Block> = {}): Block =>
  ({ id: 0, seq: 0, kind, text, anchor: '', lang: '', file: '', run: '', output: '', answer: '', verified: false, ...more });

function exampleBlock(spec: string, runnable: boolean): Block {
  const [file, cmd] = spec.split('|').map(s => s.trim());
  const path = join(exampleDir, file);
  if (!existsSync(path)) throw new Error(`missing example ${file}`);
  const code = readFileSync(path, 'utf8').replace(/\s+$/, '');
  if (!runnable) return block('code', code, { lang: langOf(file), file: `examples/${file}` });
  const outPath = path.replace(/\.[^.]+$/, '.out');
  if (!existsSync(outPath)) throw new Error(`missing expected output for ${file}`);
  return block('code', code, {
    lang: langOf(file), file: `examples/${file}`,
    run: cmd ?? `python3 examples/${file}`,
    output: readFileSync(outPath, 'utf8').replace(/\s+$/, ''),
    verified: verified[file]?.ok === true,
  });
}

function parse(md: string, where: string) {
  const fm = md.match(/^---\n([\s\S]*?)\n---\n/);
  if (!fm) throw new Error(`${where}: no front matter`);
  const meta = Object.fromEntries(fm[1].split('\n').map(l => { const i = l.indexOf(':'); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; }));
  const lines = md.slice(fm[0].length).split('\n');
  const blocks: Block[] = [];
  const outline: Heading[] = [];
  let para: string[] = [];
  const flush = () => { if (para.length) blocks.push(block('md', para.join('\n'))); para = []; };
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const h = line.match(/^(##|###) (.+)$/);
    if (h) {
      flush();
      const level = h[1].length;
      const anchor = `s${outline.length + 1}${level === 3 ? `-${blocks.length}` : ''}`;
      blocks.push(block(level === 2 ? 'h2' : 'h3', h[2], { anchor }));
      if (level === 2) outline.push({ id: anchor, title: h[2] });
      continue;
    }
    if (line.startsWith('```')) {
      flush();
      const lang = line.slice(3).trim() || 'text';
      const body: string[] = [];
      while (++i < lines.length && !lines[i].startsWith('```')) body.push(lines[i]);
      blocks.push(block('code', body.join('\n'), { lang }));
      continue;
    }
    if (line.startsWith('::example ') || line.startsWith('::file ')) {
      flush();
      blocks.push(exampleBlock(line.slice(line.indexOf(' ') + 1), line.startsWith('::example ')));
      continue;
    }
    if (line === '::quiz') {
      flush();
      const q: string[] = [], a: string[] = [];
      let into = q;
      while (++i < lines.length && lines[i] !== '::end') {
        if (lines[i] === '::answer') { into = a; continue; }
        into.push(lines[i]);
      }
      if (!a.length) throw new Error(`${where}: quiz without ::answer`);
      blocks.push(block('quiz', q.join('\n').trim(), { answer: a.join('\n').trim() }));
      continue;
    }
    if (line.trim() === '') { flush(); continue; }
    para.push(line);
  }
  flush();
  let q = 0;
  blocks.forEach((b, i) => { b.id = i; if (b.kind === 'quiz') b.seq = ++q; });
  return { meta, blocks, outline };
}

const files = readdirSync(contentDir).filter(f => /^\d\d-\d\d-.+\.md$/.test(f)).sort();
const problems: string[] = [];
const sections: Section[] = files.map(f => {
  const { meta, blocks, outline } = parse(readFileSync(join(contentDir, f), 'utf8'), f);
  const chapter = Number(meta.chapter);
  const ch = chapters.find(c => c.number === chapter);
  if (!ch) problems.push(`${f}: chapter ${chapter} not in chapters.json`);
  for (const want of REQUIRED) if (!outline.some(h => h.title.includes(want))) problems.push(`${f}: no heading with "${want}"`);
  const quizzes = blocks.filter(b => b.kind === 'quiz').length;
  if (quizzes < 2) problems.push(`${f}: ${quizzes} quiz(zes), need 2+`);
  if (!blocks.some(b => b.kind === 'md' && /https?:\/\//.test(b.text))) problems.push(`${f}: no source link`);
  for (const b of blocks) if (b.kind === 'md' && /\]\[|^ {4}\S/m.test(b.text)) problems.push(`${f}: reference link or indented code (unsupported Markdown)`);
  return {
    id: meta.id, number: meta.number, title: meta.title, chapter, chapterTitle: ch?.title ?? '', summary: meta.summary ?? '',
    blocks, outline, prevId: '', prevTitle: '', nextId: '', nextTitle: '', position: 0, total: 0,
  };
});
const ids = new Set<string>();
sections.forEach((s, i) => {
  if (!/^[a-z0-9-]+$/.test(s.id) || ids.has(s.id)) problems.push(`${s.number}: bad or duplicate id ${s.id}`);
  ids.add(s.id);
  s.position = i + 1; s.total = sections.length;
  if (i > 0) { s.prevId = sections[i - 1].id; s.prevTitle = `${sections[i - 1].number} ${sections[i - 1].title}`; }
  if (i < sections.length - 1) { s.nextId = sections[i + 1].id; s.nextTitle = `${sections[i + 1].number} ${sections[i + 1].title}`; }
});
if (problems.length) { console.error(problems.join('\n')); process.exit(1); }

const toc = chapters.map(c => ({
  number: c.number, title: c.title, intro: c.intro,
  sections: sections.filter(s => s.chapter === c.number).map(s => ({ id: s.id, number: s.number, title: s.title, summary: s.summary })),
}));
writeFileSync(join(root, 'book.gen.ts'),
  `// Generated by tools/gen-book.ts from content/. Do not edit.\nexport const TOC = ${JSON.stringify(toc)};\nexport const SECTIONS = ${JSON.stringify(sections)};\n`);
const codes = sections.flatMap(s => s.blocks.filter(b => b.run));
console.log(`book.gen.ts: ${chapters.length} chapters, ${sections.length} sections, ${codes.length} runnable examples (${codes.filter(b => b.verified).length} verified)`);
