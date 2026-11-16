// 실행: node --test static/logic.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import {
  emptyData, validateData, validateBackup, makeBackup, progress, nextTask, isSafeUrl, weeksNeeded,
} from './logic.js';

// 서버가 페이지에 넣는 색인과 같은 모양을 course.json에서 직접 만든다.
const course = JSON.parse(readFileSync(new URL('../content/course.json', import.meta.url), 'utf8'));
const index = {
  courseVersion: course.version,
  weeks: course.weeks.map((w) => ({ n: w.n, title: w.title, problem: w.problem })),
  tasks: course.weeks.flatMap((w) => w.tasks.map((t) => ({ id: t.id, week: w.n, title: t.title, minutes: t.minutes, track: t.track }))),
  interviewTypes: course.interview.map((t) => ({ id: t.id, name: t.name })),
};
const rec = (over = {}) => ({ done: true, rating: '', note: '', updatedAt: '2026-11-16T00:00:00.000Z', ...over });

test('progress counts only the selected track and separates check from rating', () => {
  const d = emptyData();
  d.tasks['w1-read'] = rec({ rating: 'met' });
  d.tasks['w7-pipeline'] = rec(); // 대체 경로 과제: 기본 경로에서는 세지 않는다
  d.tasks['w2-problem'] = rec({ done: false, rating: 'evidence' });
  const p = progress(index, d);
  const aiTotal = index.tasks.filter((t) => t.track !== 'data').length;
  assert.deepEqual([p.done, p.met, p.total], [1, 2, aiTotal]);
});

test('switching to data track counts the pipeline task', () => {
  const d = emptyData();
  d.settings.track = 'data';
  d.tasks['w7-pipeline'] = rec();
  assert.equal(progress(index, d).byWeek[7].done, 1);
});

test('nextTask returns first unchecked task in order', () => {
  const d = emptyData();
  d.tasks['w1-read'] = rec();
  assert.equal(nextTask(index, d).id, 'w1-gap');
});

test('backup round trip keeps data identical', () => {
  const d = emptyData();
  d.settings.experienceYears = 3;
  d.tasks['w3-client'] = rec({ note: '<img src=x onerror=alert(1)>' });
  d.interviews.push({ id: 'a1', type: 'demo', date: '2026-11-16', score: 'met', note: '' });
  d.applications.push({ id: 'b1', company: '예시', url: 'https://example.com/job', status: 'applied', date: '', memo: '' });
  const r = validateBackup(JSON.parse(JSON.stringify(makeBackup(d, index))), index);
  assert.deepEqual(r.data, d);
});

test('backup with unknown version is rejected', () => {
  const b = makeBackup(emptyData(), index);
  b.version = 2;
  assert.equal(validateBackup(b, index).ok, false);
});

test('backup with unknown task id is rejected', () => {
  const b = makeBackup(emptyData(), index);
  b.data.tasks['w99-x'] = rec();
  assert.equal(validateBackup(b, index).ok, false);
});

test('backup with __proto__ task key is rejected', () => {
  const b = JSON.parse('{"app":"fde-study","version":1,"courseVersion":"x","exportedAt":"x","data":{"settings":{"experienceYears":null,"region":"both","hoursPerWeek":10,"track":"ai"},"tasks":{"__proto__":{"done":true,"rating":"","note":"","updatedAt":""}},"interviews":[],"applications":[]}}');
  assert.equal(validateBackup(b, index).ok, false);
});

test('backup with extra field is rejected', () => {
  const b = makeBackup(emptyData(), index);
  b.data.settings.admin = true;
  assert.equal(validateBackup(b, index).ok, false);
});

test('backup with wrong field type is rejected', () => {
  const b = makeBackup(emptyData(), index);
  b.data.settings.hoursPerWeek = '10';
  assert.equal(validateBackup(b, index).ok, false);
});

test('application with javascript url is rejected', () => {
  const d = emptyData();
  d.applications.push({ id: 'b1', company: 'x', url: 'javascript:alert(1)', status: 'applied', date: '', memo: '' });
  assert.equal(validateData(d, index).ok, false);
});

test('duplicate record ids are rejected', () => {
  const d = emptyData();
  const r = { id: 'same', type: 'demo', date: '', score: '', note: '' };
  d.interviews.push(r, { ...r });
  assert.equal(validateData(d, index).ok, false);
});

test('isSafeUrl accepts https only-style web urls', () => {
  assert.deepEqual([isSafeUrl('https://a.b'), isSafeUrl('data:text/html,x'), isSafeUrl('not a url')], [true, false, false]);
});

test('weeksNeeded rounds up', () => {
  assert.equal(weeksNeeded(601, 10), 2);
});
