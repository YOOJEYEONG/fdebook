// 순수 함수만 둔다: 브라우저(app.js)와 node 검사(logic.test.mjs)가 같이 쓴다.

export const STORAGE_KEY = 'fde-study:v1';
export const BACKUP_APP = 'fde-study';
export const BACKUP_VERSION = 1;
export const RATINGS = ['', 'weak', 'met', 'evidence'];
export const REGIONS = ['both', 'korea', 'overseas'];
export const TRACKS = ['ai', 'data'];
export const APP_STATUSES = ['interested', 'applied', 'screen', 'interview', 'offer', 'rejected', 'hold'];
export const MAX_TEXT = 5000;
export const MAX_RECORDS = 500;

export function emptyData() {
  return {
    settings: { experienceYears: null, region: 'both', hoursPerWeek: 10, track: 'ai' },
    tasks: {},
    interviews: [],
    applications: [],
  };
}

export function isSafeUrl(s) {
  if (typeof s !== 'string' || s.length > 2000) return false;
  try {
    const u = new URL(s);
    return u.protocol === 'https:' || u.protocol === 'http:';
  } catch {
    return false;
  }
}

const isObj = (v) => v !== null && typeof v === 'object' && !Array.isArray(v);
const isDate = (v) => v === '' || (typeof v === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(v));
const isText = (v, max = MAX_TEXT) => typeof v === 'string' && v.length <= max;
const isId = (v) => typeof v === 'string' && /^[A-Za-z0-9-]{1,64}$/.test(v);
const isInt = (v, min, max) => Number.isInteger(v) && v >= min && v <= max;

function exactKeys(obj, keys, where, errors) {
  const got = Object.keys(obj);
  for (const k of got) if (!keys.includes(k)) errors.push(`${where}: 알 수 없는 항목 "${k}"`);
  for (const k of keys) if (!got.includes(k)) errors.push(`${where}: "${k}" 항목이 없습니다`);
}

/**
 * 저장 데이터 전체를 검사한다. 하나라도 틀리면 ok=false이고 data는 돌려주지 않는다.
 * 통과하면 검사한 필드만으로 새 객체를 만들어 돌려준다(원본 객체를 그대로 쓰지 않음).
 */
export function validateData(d, index) {
  const errors = [];
  if (!isObj(d)) return { ok: false, errors: ['데이터가 객체가 아닙니다'] };
  exactKeys(d, ['settings', 'tasks', 'interviews', 'applications'], '데이터', errors);
  if (errors.length) return { ok: false, errors };

  const taskIds = new Set(index.tasks.map((t) => t.id));
  const typeIds = new Set(index.interviewTypes.map((t) => t.id));
  const out = emptyData();

  const s = d.settings;
  if (!isObj(s)) errors.push('설정이 객체가 아닙니다');
  else {
    exactKeys(s, ['experienceYears', 'region', 'hoursPerWeek', 'track'], '설정', errors);
    if (!(s.experienceYears === null || isInt(s.experienceYears, 0, 50))) errors.push('설정: 경력은 0–50 정수 또는 빈 값이어야 합니다');
    if (!REGIONS.includes(s.region)) errors.push('설정: 알 수 없는 지역 값');
    if (!isInt(s.hoursPerWeek, 1, 60)) errors.push('설정: 주당 시간은 1–60 정수여야 합니다');
    if (!TRACKS.includes(s.track)) errors.push('설정: 알 수 없는 경로 값');
    out.settings = { experienceYears: s.experienceYears, region: s.region, hoursPerWeek: s.hoursPerWeek, track: s.track };
  }

  if (!isObj(d.tasks)) errors.push('과제 기록이 객체가 아닙니다');
  else {
    for (const [id, t] of Object.entries(d.tasks)) {
      if (!taskIds.has(id)) { errors.push(`과제 기록: 알 수 없는 과제 ID "${id}"`); continue; }
      if (!isObj(t)) { errors.push(`과제 ${id}: 객체가 아닙니다`); continue; }
      exactKeys(t, ['done', 'rating', 'note', 'updatedAt'], `과제 ${id}`, errors);
      if (typeof t.done !== 'boolean') errors.push(`과제 ${id}: done은 참/거짓이어야 합니다`);
      if (!RATINGS.includes(t.rating)) errors.push(`과제 ${id}: 알 수 없는 자기평가 값`);
      if (!isText(t.note)) errors.push(`과제 ${id}: 메모는 ${MAX_TEXT}자 이하 문자열이어야 합니다`);
      if (!isText(t.updatedAt, 40)) errors.push(`과제 ${id}: 수정 시각 형식 오류`);
      out.tasks[id] = { done: t.done, rating: t.rating, note: t.note, updatedAt: t.updatedAt };
    }
  }

  const records = (list, name, keys, check) => {
    if (!Array.isArray(list)) { errors.push(`${name}이 목록이 아닙니다`); return []; }
    if (list.length > MAX_RECORDS) errors.push(`${name}: ${MAX_RECORDS}건을 넘습니다`);
    const seen = new Set();
    return list.map((r, i) => {
      const where = `${name} ${i + 1}번`;
      if (!isObj(r)) { errors.push(`${where}: 객체가 아닙니다`); return null; }
      exactKeys(r, keys, where, errors);
      if (!isId(r.id)) errors.push(`${where}: ID 형식 오류`);
      else if (seen.has(r.id)) errors.push(`${where}: ID 중복`);
      seen.add(r.id);
      check(r, where);
      return Object.fromEntries(keys.map((k) => [k, r[k]]));
    });
  };

  out.interviews = records(d.interviews, '면접 기록', ['id', 'type', 'date', 'score', 'note'], (r, w) => {
    if (!typeIds.has(r.type)) errors.push(`${w}: 알 수 없는 면접 유형`);
    if (!isDate(r.date)) errors.push(`${w}: 날짜는 YYYY-MM-DD 또는 빈 값`);
    if (!RATINGS.includes(r.score)) errors.push(`${w}: 알 수 없는 채점 값`);
    if (!isText(r.note)) errors.push(`${w}: 메모 길이 초과 또는 형식 오류`);
  });

  out.applications = records(d.applications, '지원 기록', ['id', 'company', 'url', 'status', 'date', 'memo'], (r, w) => {
    if (!isText(r.company, 100) || r.company.trim() === '') errors.push(`${w}: 회사명은 1–100자`);
    if (!(r.url === '' || isSafeUrl(r.url))) errors.push(`${w}: URL은 http(s) 주소 또는 빈 값`);
    if (!APP_STATUSES.includes(r.status)) errors.push(`${w}: 알 수 없는 상태 값`);
    if (!isDate(r.date)) errors.push(`${w}: 날짜는 YYYY-MM-DD 또는 빈 값`);
    if (!isText(r.memo)) errors.push(`${w}: 메모 길이 초과 또는 형식 오류`);
  });

  return errors.length ? { ok: false, errors } : { ok: true, data: out };
}

export function makeBackup(data, index, now = new Date()) {
  return { app: BACKUP_APP, version: BACKUP_VERSION, courseVersion: index.courseVersion, exportedAt: now.toISOString(), data };
}

export function validateBackup(obj, index) {
  if (!isObj(obj)) return { ok: false, errors: ['백업 파일 최상위가 객체가 아닙니다'] };
  const errors = [];
  exactKeys(obj, ['app', 'version', 'courseVersion', 'exportedAt', 'data'], '백업', errors);
  if (errors.length) return { ok: false, errors };
  if (obj.app !== BACKUP_APP) return { ok: false, errors: ['이 앱의 백업 파일이 아닙니다'] };
  if (obj.version !== BACKUP_VERSION) return { ok: false, errors: [`지원하지 않는 백업 버전입니다: ${String(obj.version)}`] };
  if (!isText(obj.courseVersion, 40) || !isText(obj.exportedAt, 40)) return { ok: false, errors: ['백업 메타 정보 형식 오류'] };
  const r = validateData(obj.data, index);
  return r.ok ? { ok: true, data: r.data, exportedAt: obj.exportedAt, courseVersion: obj.courseVersion } : r;
}

export function activeTasks(index, track) {
  return index.tasks.filter((t) => t.track === 'all' || t.track === track);
}

export function progress(index, data) {
  const tasks = activeTasks(index, data.settings.track);
  const byWeek = {};
  let done = 0, met = 0, leftMinutes = 0;
  for (const t of tasks) {
    const rec = data.tasks[t.id];
    const w = (byWeek[t.week] ??= { done: 0, total: 0 });
    w.total += 1;
    if (rec?.done) { done += 1; w.done += 1; } else leftMinutes += t.minutes;
    if (rec?.rating === 'met' || rec?.rating === 'evidence') met += 1;
  }
  return { done, met, total: tasks.length, leftMinutes, byWeek };
}

export function nextTask(index, data) {
  return activeTasks(index, data.settings.track).find((t) => !data.tasks[t.id]?.done) ?? null;
}

export function weeksNeeded(leftMinutes, hoursPerWeek) {
  return Math.ceil(leftMinutes / (hoursPerWeek * 60));
}

export function minutesLabel(m) {
  const h = Math.floor(m / 60), r = m % 60;
  if (h === 0) return `${r}분`;
  return r === 0 ? `${h}시간` : `${h}시간 ${r}분`;
}

export function newId() {
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
}
