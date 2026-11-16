import {
  STORAGE_KEY, emptyData, validateData, validateBackup, makeBackup, progress, nextTask,
  weeksNeeded, minutesLabel, isSafeUrl, newId, MAX_TEXT,
} from './logic.js';

const index = JSON.parse(document.getElementById('course-index').textContent);
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

// ---------- 저장소 ----------
// corrupt: 저장된 값을 읽을 수 없음. 사용자가 명시적으로 초기화·가져오기 전까지 덮어쓰지 않는다.
const store = { available: true, corrupt: false, raw: null, errors: [] };
let data = load();

function load() {
  store.available = true;
  store.corrupt = false;
  store.raw = null;
  store.errors = [];
  let raw;
  try {
    raw = localStorage.getItem(STORAGE_KEY);
  } catch {
    store.available = false;
    return emptyData();
  }
  if (raw === null) return emptyData();
  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch {
    parsed = undefined;
  }
  const r = parsed === undefined ? { ok: false, errors: ['JSON 형식이 아닙니다'] } : validateData(parsed, index);
  if (r.ok) return r.data;
  store.corrupt = true;
  store.raw = raw;
  store.errors = r.errors;
  return emptyData();
}

/** 새 데이터를 저장하고 성공했을 때만 화면 상태를 바꾼다. */
function commit(next) {
  if (store.corrupt) {
    notice('저장된 기록을 읽을 수 없어 저장을 멈췄습니다. 설정·백업 화면에서 원본을 내려받은 뒤 초기화하거나 백업을 가져오세요.');
    return false;
  }
  if (!store.available) {
    data = next;
    notice('이 브라우저에서 저장소를 쓸 수 없습니다. 변경은 이 탭을 닫으면 사라집니다. 백업 파일로 내보내 두세요.');
    return true;
  }
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  } catch {
    notice('저장에 실패했습니다(저장 공간 부족 또는 차단). 화면의 기존 기록은 그대로입니다.');
    return false;
  }
  data = next;
  return true;
}

const clone = () => structuredClone(data);

// 다른 탭이 기록을 바꾸면 이 탭의 기준 데이터를 다시 읽는다. 그러지 않으면 다음 저장이 다른 탭의 변경을 덮어쓴다.
window.addEventListener('storage', (e) => {
  if (e.key !== STORAGE_KEY && e.key !== null) return;
  data = load();
  notice('다른 탭에서 기록이 바뀌었습니다. 새로고침하면 이 화면에도 최신 기록이 보입니다.');
});

function notice(msg) {
  const el = $('#notice');
  if (!el) return;
  el.textContent = msg;
  el.hidden = !msg;
}

function startupNotice() {
  if (store.corrupt) {
    notice('저장된 기록을 읽을 수 없습니다. 기존 값은 지우지 않았고, 저장도 멈췄습니다. 설정·백업 화면에서 처리하세요.');
  } else if (!store.available) {
    notice('이 브라우저에서 저장소를 쓸 수 없습니다(사생활 보호 모드 또는 차단). 변경은 이 탭을 닫으면 사라집니다.');
  }
}

// ---------- 공통 진행률 ----------
function renderWeekProgress() {
  const p = progress(index, data);
  for (const el of $$('[data-week-progress]')) {
    const w = p.byWeek[el.dataset.weekProgress];
    el.textContent = w ? `체크 ${w.done}/${w.total}` : '';
  }
}

// ---------- 오늘의 학습 ----------
function initHome() {
  const p = progress(index, data);
  const today = $('#today');
  const t = nextTask(index, data);
  today.replaceChildren();
  if (data.settings.experienceYears === null) {
    const tip = el('p', 'tip');
    tip.append('처음이라면 ', link('/settings', '설정'), '에서 경력·희망 지역·주당 시간을 입력하세요. 근거 자료의 경력 필터와 예상 기간이 바뀝니다.');
    today.append(tip);
  }
  if (t) {
    const w = index.weeks.find((x) => x.n === t.week);
    today.append(
      el('p', 'week-tag', `${w.n}주차 · ${w.title}`),
      el('p', 'problem', w.problem),
      el('h2', null, t.title),
      el('p', 'meta', `예상 ${minutesLabel(t.minutes)}`),
    );
    const go = link(`/weeks/${t.week}#${t.id}`, p.done === 0 ? '첫 과제 시작하기' : '이어서 하기');
    go.className = 'button';
    today.append(el('p', null, '', go));
  } else {
    today.append(el('p', 'problem', '기본 경로의 모든 과제를 체크했습니다. 자기평가가 미흡인 과제를 다시 보고, 면접 연습과 지원 기록으로 넘어가세요.'));
    today.append(el('p', null, '', link('/interview', '면접 준비로 가기')));
  }

  $('#stat-done').textContent = `${p.done} / ${p.total}`;
  $('#stat-met').textContent = `${p.met} / ${p.total}`;
  $('#stat-left').textContent = minutesLabel(p.leftMinutes);
  const pct = p.total ? Math.round((p.done / p.total) * 100) : 0;
  const bar = $('#overall');
  bar.value = pct;
  bar.textContent = `${pct}%`;
  const route = data.settings.track === 'ai' ? '기본 경로(LLM)' : '대체 경로(데이터 파이프라인)';
  $('#estimate').textContent =
    `주 ${data.settings.hoursPerWeek}시간 기준 남은 과제는 약 ${weeksNeeded(p.leftMinutes, data.settings.hoursPerWeek)}주 분량입니다. 7–8주차는 ${route}로 계산합니다.`;
}

// ---------- 주차 과제 ----------
function initTasks() {
  const track = data.settings.track;
  for (const art of $$('[data-task]')) {
    const id = art.dataset.task;
    const rec = data.tasks[id] ?? { done: false, rating: '', note: '', updatedAt: '' };
    const done = $('input[name=done]', art);
    const rating = $('select[name=rating]', art);
    const note = $('textarea[name=note]', art);
    const status = $('.saved', art);
    done.checked = rec.done;
    rating.value = rec.rating;
    note.value = rec.note;

    const off = art.dataset.track !== 'all' && art.dataset.track !== track;
    art.classList.toggle('off-track', off);
    const tn = $('[data-track-note]', art);
    if (tn && off) tn.textContent += ' — 지금 선택한 경로가 아니어서 진도에 세지 않습니다. 설정에서 바꿀 수 있습니다.';

    // 바뀐 필드 하나만 최신 저장 데이터에 덮어쓴다. 다른 탭이 같은 과제의 다른 필드를 바꿨어도
    // 이 탭의 오래된 폼 값이 그 변경을 지우지 않는다.
    const save = (field, msg) => {
      const next = clone();
      if (note.value.length > MAX_TEXT) note.value = note.value.slice(0, MAX_TEXT);
      const value = { done: done.checked, rating: rating.value, note: note.value }[field];
      const base = next.tasks[id] ?? { done: false, rating: '', note: '', updatedAt: '' };
      next.tasks[id] = { ...base, [field]: value, updatedAt: new Date().toISOString() };
      if (commit(next)) status.textContent = msg;
      else status.textContent = '저장하지 못했습니다';
      // 성공·실패 모두 화면을 저장된 값과 맞춘다(실패하면 입력 전 값, 성공하면 다른 탭의 최신 값 포함).
      const cur = data.tasks[id] ?? { done: false, rating: '', note: '' };
      done.checked = cur.done;
      rating.value = cur.rating;
      if (field !== 'note' && document.activeElement !== note) note.value = cur.note;
      renderWeekProgress();
    };
    done.addEventListener('change', () => save('done', done.checked ? '체크를 저장했습니다' : '체크를 해제했습니다'));
    rating.addEventListener('change', () => save('rating', '자기평가를 저장했습니다'));
    let timer = null;
    // 입력 직후 페이지를 떠나도 메모가 남도록 대기 중인 저장을 즉시 실행한다.
    const flush = () => {
      if (timer === null) return;
      clearTimeout(timer);
      timer = null;
      save('note', '메모를 저장했습니다');
    };
    note.addEventListener('input', () => {
      clearTimeout(timer);
      status.textContent = '입력 중…';
      timer = setTimeout(flush, 600);
    });
    note.addEventListener('blur', flush);
    window.addEventListener('pagehide', flush);
  }
}

// ---------- 면접 기록 ----------
function initInterview() {
  const form = $('#interview-form');
  const list = $('#interview-list');
  const err = $('#iv-error');
  const typeName = (id) => index.interviewTypes.find((t) => t.id === id)?.name ?? id;
  const scoreName = { '': '채점 안 함', weak: '미흡', met: '충족', evidence: '증거 수준' };

  const render = () => {
    list.replaceChildren();
    const items = [...data.interviews].reverse();
    const covered = new Set(data.interviews.map((r) => r.type));
    $('#iv-summary').textContent = items.length
      ? `기록 ${items.length}건 · 연습한 유형 ${covered.size}/${index.interviewTypes.length}`
      : '아직 연습 기록이 없습니다. 아래 유형별 문항 중 하나를 골라 녹화하거나 동료와 연습한 뒤 기록하세요.';
    for (const r of items) {
      const li = el('li');
      li.append(el('h3', null, `${typeName(r.type)} · ${scoreName[r.score]}`), el('p', 'meta', r.date || '날짜 없음'));
      if (r.note) li.append(el('p', 'note', r.note));
      li.append(deleteButton(`${typeName(r.type)} 기록 삭제`, () => {
        const next = clone();
        next.interviews = next.interviews.filter((x) => x.id !== r.id);
        if (commit(next)) render();
      }));
      list.append(li);
    }
  };

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const f = new FormData(form);
    const rec = { id: newId(), type: f.get('type'), date: f.get('date'), score: f.get('score'), note: f.get('note') };
    const next = clone();
    next.interviews.push(rec);
    const v = validateData(next, index);
    if (!v.ok) return showError(err, v.errors);
    err.hidden = true;
    if (commit(v.data)) {
      form.reset();
      render();
    }
  });
  render();
}

// ---------- 지원 기록 ----------
function initApplications() {
  const form = $('#app-form');
  const list = $('#app-list');
  const err = $('#ap-error');
  const submit = $('#ap-submit');
  const cancel = $('#ap-cancel');
  const statusName = {
    interested: '관심', applied: '지원 완료', screen: '서류 통과', interview: '면접 중',
    offer: '합격', rejected: '불합격', hold: '보류',
  };

  const resetForm = () => {
    form.reset();
    $('#ap-id').value = '';
    submit.textContent = '지원 기록 추가';
    cancel.hidden = true;
  };

  const render = () => {
    list.replaceChildren();
    const counts = {};
    for (const a of data.applications) counts[a.status] = (counts[a.status] ?? 0) + 1;
    $('#ap-summary').textContent = data.applications.length
      ? Object.entries(counts).map(([k, n]) => `${statusName[k]} ${n}`).join(', ')
      : '아직 기록이 없습니다. 근거 자료에서 공고 원문을 확인한 뒤 첫 기록을 추가하세요.';
    for (const a of data.applications) {
      const li = el('li');
      li.append(el('h3', null, `${a.company} · ${statusName[a.status]}`));
      if (a.date) li.append(el('p', 'meta', a.date));
      if (a.url && isSafeUrl(a.url)) {
        const p = el('p', 'meta');
        const link = document.createElement('a');
        link.href = a.url;
        link.rel = 'noopener noreferrer';
        link.target = '_blank';
        link.textContent = a.url;
        p.append(link);
        li.append(p);
      }
      if (a.memo) li.append(el('p', 'note', a.memo));
      const edit = el('button', 'secondary', '수정');
      edit.type = 'button';
      edit.setAttribute('aria-label', `${a.company} 기록 수정`);
      edit.addEventListener('click', () => {
        for (const k of ['id', 'company', 'url', 'status', 'date', 'memo']) form.elements[k].value = a[k];
        submit.textContent = '수정 저장';
        cancel.hidden = false;
        $('#ap-company').focus();
      });
      const actions = el('div', 'actions');
      actions.append(edit, deleteButton(`${a.company} 기록 삭제`, () => {
        const next = clone();
        next.applications = next.applications.filter((x) => x.id !== a.id);
        if (commit(next)) render();
      }));
      li.append(actions);
      list.append(li);
    }
  };

  cancel.addEventListener('click', resetForm);
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const f = new FormData(form);
    const id = f.get('id');
    const rec = {
      id: id || newId(),
      company: String(f.get('company')).trim(),
      url: String(f.get('url')).trim(),
      status: f.get('status'),
      date: f.get('date'),
      memo: f.get('memo'),
    };
    const next = clone();
    const i = next.applications.findIndex((x) => x.id === id);
    if (i >= 0) next.applications[i] = rec;
    else next.applications.push(rec);
    const v = validateData(next, index);
    if (!v.ok) return showError(err, v.errors.map((m) => m.replace(/^지원 기록 \d+번: /, '')));
    err.hidden = true;
    if (commit(v.data)) {
      resetForm();
      render();
    }
  });
  render();
}

// ---------- 근거 자료 필터 ----------
function initEvidence() {
  const form = $('#ev-filter');
  const exp = data.settings.experienceYears;
  const expBox = $('input[name=exp]', form);
  if (exp === null) {
    expBox.disabled = true;
    $('#exp-hint').textContent += ' 설정에서 경력 연수를 입력하면 이 필터를 쓸 수 있습니다.';
  }
  if (data.settings.region !== 'both') $(`input[name=region][value=${data.settings.region}]`, form).checked = true;

  const apply = () => {
    const region = new FormData(form).get('region');
    const statuses = new Set($$('input[name=status]:checked', form).map((x) => x.value));
    let shown = 0;
    for (const card of $$('.posting')) {
      const min = card.dataset.exp === '' ? null : Number(card.dataset.exp);
      const ok =
        (region === 'all' || card.dataset.region === region) &&
        statuses.has(card.dataset.status) &&
        (!expBox.checked || (min !== null && exp !== null && exp >= min));
      card.hidden = !ok;
      if (ok) shown += 1;
    }
    $('#ev-count').textContent = `공고 ${shown}건 표시 중`;
    $('#ev-empty').hidden = shown > 0;
  };
  form.addEventListener('change', apply);
  apply();
}

// ---------- 설정·백업 ----------
function initSettings() {
  const form = $('#settings-form');
  const err = $('#st-error');
  const fill = () => {
    const s = data.settings;
    form.elements.experienceYears.value = s.experienceYears ?? '';
    form.elements.region.value = s.region;
    form.elements.hoursPerWeek.value = s.hoursPerWeek;
    $(`input[name=track][value=${s.track}]`, form).checked = true;
  };
  fill();

  const state = $('#storage-state');
  const describe = () => {
    if (store.corrupt) {
      state.textContent = `저장된 기록을 읽을 수 없습니다: ${store.errors.slice(0, 3).join(' / ')}. 원본은 지우지 않았습니다.`;
      $('#download-raw').hidden = false;
    } else if (!store.available) {
      state.textContent = '저장소를 쓸 수 없는 브라우저입니다. 백업 내보내기로만 기록을 보관할 수 있습니다.';
    } else {
      const p = progress(index, data);
      state.textContent = `현재 저장: 과제 체크 ${p.done}건, 면접 기록 ${data.interviews.length}건, 지원 기록 ${data.applications.length}건.`;
    }
  };
  describe();

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const f = new FormData(form);
    const expRaw = String(f.get('experienceYears')).trim();
    const next = clone();
    next.settings = {
      experienceYears: expRaw === '' ? null : Number(expRaw),
      region: f.get('region'),
      hoursPerWeek: Number(f.get('hoursPerWeek')),
      track: f.get('track') ?? '',
    };
    const v = validateData(next, index);
    if (!v.ok) return showError(err, v.errors.map((m) => m.replace(/^설정: /, '')));
    err.hidden = true;
    if (commit(v.data)) {
      notice('');
      flash(state, '설정을 저장했습니다.');
    }
  });

  $('#export').addEventListener('click', () => {
    if (store.corrupt) return flash(state, '저장된 기록을 읽을 수 없어 내보낼 수 없습니다. 원본 내려받기를 쓰세요.');
    const backup = makeBackup(data, index);
    download(`fde-study-backup-${backup.exportedAt.slice(0, 10)}.json`, JSON.stringify(backup, null, 2));
    flash(state, '백업 파일을 내보냈습니다.');
  });

  let pending = null;
  const result = $('#import-result');
  const apply = $('#import-apply');
  $('#import-file').addEventListener('change', async (e) => {
    pending = null;
    apply.hidden = true;
    result.replaceChildren();
    const file = e.target.files[0];
    if (!file) return;
    if (file.size > 2_000_000) return result.append(el('p', 'form-error', '파일이 2MB를 넘습니다. 이 앱의 백업 파일인지 확인하세요.'));
    let parsed;
    try {
      parsed = JSON.parse(await file.text());
    } catch {
      return result.append(el('p', 'form-error', 'JSON 파일이 아닙니다. 지금 데이터는 바뀌지 않았습니다.'));
    }
    const v = validateBackup(parsed, index);
    if (!v.ok) {
      result.append(el('p', 'form-error', '가져올 수 없는 백업입니다. 지금 데이터는 바뀌지 않았습니다.'));
      const ul = el('ul');
      for (const m of v.errors.slice(0, 8)) ul.append(el('li', null, m));
      if (v.errors.length > 8) ul.append(el('li', null, `외 ${v.errors.length - 8}건`));
      return result.append(ul);
    }
    pending = v.data;
    const done = Object.values(v.data.tasks).filter((t) => t.done).length;
    result.append(el('p', null,
      `검사 통과: ${v.exportedAt.slice(0, 10)}에 내보낸 백업, 과제 체크 ${done}건, 면접 기록 ${v.data.interviews.length}건, 지원 기록 ${v.data.applications.length}건. ` +
      '바꾸면 지금 기록은 이 백업으로 대체됩니다.'));
    if (v.courseVersion !== index.courseVersion) {
      result.append(el('p', 'muted', `다른 콘텐츠 버전(${v.courseVersion})에서 만든 백업입니다. 과제 ID는 모두 확인했습니다.`));
    }
    apply.hidden = false;
    apply.focus();
  });

  apply.addEventListener('click', () => {
    if (!pending) return;
    const wasCorrupt = store.corrupt;
    store.corrupt = false; // 사용자가 명시적으로 고른 백업으로만 손상 상태를 해제한다.
    if (commit(pending)) {
      pending = null;
      apply.hidden = true;
      $('#import-file').value = '';
      result.replaceChildren(el('p', null, '백업을 가져왔습니다.'));
      $('#download-raw').hidden = true;
      notice('');
      fill();
      describe();
    } else {
      store.corrupt = wasCorrupt;
    }
  });

  $('#download-raw').addEventListener('click', () => {
    if (store.raw !== null) download('fde-study-unreadable-original.txt', store.raw);
  });

  $('#reset').addEventListener('click', () => {
    if (!confirm('저장된 모든 기록을 지웁니다. 되돌릴 수 없습니다. 계속할까요?')) return;
    store.corrupt = false;
    store.raw = null;
    if (commit(emptyData())) {
      $('#download-raw').hidden = true;
      notice('');
      fill();
      describe();
      flash(state, '모든 기록을 지웠습니다.');
    }
  });
}

// ---------- DOM 도우미 ----------
function el(tag, cls, text = '', ...children) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text) n.textContent = text;
  n.append(...children);
  return n;
}

function link(href, text) {
  const a = document.createElement('a');
  a.href = href;
  a.textContent = text;
  return a;
}

function deleteButton(label, onDelete) {
  const b = el('button', 'danger', '삭제');
  b.type = 'button';
  b.setAttribute('aria-label', label);
  b.addEventListener('click', () => {
    if (confirm(`${label}할까요?`)) onDelete();
  });
  return b;
}

function showError(target, errors) {
  target.textContent = errors.slice(0, 3).join(' / ');
  target.hidden = false;
}

function flash(target, msg) {
  target.textContent = msg;
}

function download(name, text) {
  const url = URL.createObjectURL(new Blob([text], { type: 'application/json' }));
  const a = document.createElement('a');
  a.href = url;
  a.download = name;
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

// ---------- 시작 ----------
startupNotice();
const page = document.body.dataset.page;
if (page === 'home') initHome();
if ($('[data-task]')) initTasks();
if (page === 'interview') initInterview();
if (page === 'applications') initApplications();
if (page === 'evidence') initEvidence();
if (page === 'settings') initSettings();
renderWeekProgress();
