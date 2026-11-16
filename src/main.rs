//! FDE 학습 공간: 콘텐츠 JSON을 읽어 한국어 학습 페이지를 SSR로 제공하는 로컬 서버.
//! 개인 진도는 브라우저 localStorage에만 저장되고 서버는 아무것도 쓰지 않는다.

use std::{collections::HashSet, fmt::Write as _, net::SocketAddr, sync::Arc};

use axum::{
    Router,
    extract::{Path, State},
    http::{HeaderValue, StatusCode, header},
    response::{IntoResponse, Response},
    routing::get,
};
use serde::Deserialize;

const COURSE_JSON: &str = include_str!("../content/course.json");
const CSS: &str = include_str!("../static/app.css");
const APP_JS: &str = include_str!("../static/app.js");
const LOGIC_JS: &str = include_str!("../static/logic.js");

const CSP: &str = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; \
                   object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'";

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Course {
    version: String,
    verified_on: String,
    scenario: Scenario,
    rubric: Vec<RubricLevel>,
    competencies: Vec<Competency>,
    weeks: Vec<Week>,
    interview: Vec<InterviewType>,
    evidence: Vec<Evidence>,
    excluded: Vec<Excluded>,
    stats: Vec<Stat>,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Scenario {
    name: String,
    summary: String,
    stakeholders: Vec<String>,
    stages: Vec<Stage>,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Stage {
    title: String,
    week: u8,
    deliverable: String,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct RubricLevel {
    id: String,
    name: String,
    description: String,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Competency {
    id: String,
    name: String,
    description: String,
    evidence: Vec<String>,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Week {
    n: u8,
    title: String,
    goal: String,
    problem: String,
    intro: Vec<String>,
    competencies: Vec<String>,
    evidence: Vec<String>,
    tasks: Vec<Task>,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Task {
    id: String,
    title: String,
    minutes: u32,
    track: String,
    steps: Vec<String>,
    deliverable: String,
    criteria: Vec<String>,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct InterviewType {
    id: String,
    name: String,
    week: u8,
    prompts: Vec<String>,
    good: Vec<String>,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Evidence {
    id: String,
    company: String,
    title: String,
    region: String,
    location: String,
    status: String,
    source_type: String,
    url: String,
    accessed: String,
    experience: String,
    experience_min: Option<u8>,
    required: Vec<String>,
    preferred: Vec<String>,
    conditions: Vec<String>,
    note: String,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Excluded {
    name: String,
    reason: String,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Stat {
    id: String,
    claim: String,
    source: String,
    url: String,
    accessed: String,
    caveat: String,
}

struct App {
    course: Course,
    /// 모든 페이지에 넣는 과제 색인 JSON. `<`를 이스케이프해 script 블록 밖으로 나갈 수 없다.
    index_json: String,
}

type Shared = Arc<App>;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let course: Course = serde_json::from_str(COURSE_JSON)?;
    validate(&course)?;
    let index_json = task_index_json(&course);
    let app = Arc::new(App { course, index_json });

    let router = Router::new()
        .route("/", get(home))
        .route("/weeks", get(weeks))
        .route("/weeks/{n}", get(week))
        .route("/map", get(map))
        .route("/project", get(project))
        .route("/interview", get(interview))
        .route("/applications", get(applications))
        .route("/evidence", get(evidence))
        .route("/settings", get(settings))
        .route("/static/app.css", get(|| async { asset("text/css", CSS) }))
        .route(
            "/static/app.js",
            get(|| async { asset("text/javascript", APP_JS) }),
        )
        .route(
            "/static/logic.js",
            get(|| async { asset("text/javascript", LOGIC_JS) }),
        )
        // 아이콘 파일은 없다. 브라우저 자동 요청이 404 오류로 남지 않게 빈 응답을 준다.
        .route("/favicon.ico", get(|| async { StatusCode::NO_CONTENT }))
        .fallback(not_found)
        .with_state(app);

    let port: u16 = match std::env::var("FDE_PORT") {
        Ok(v) => v
            .parse()
            .map_err(|_| format!("FDE_PORT 값이 포트 번호가 아닙니다: {v}"))?,
        Err(_) => 8787,
    };
    // localhost 전용. 외부 공개가 필요하면 바인딩 주소를 명시적으로 바꿔야 한다.
    let addr = SocketAddr::from(([127, 0, 0, 1], port));
    let listener = tokio::net::TcpListener::bind(addr).await?;
    println!("FDE 학습 공간: http://{addr}");
    axum::serve(listener, router).await?;
    Ok(())
}

// ---------- 검증 ----------

fn validate(c: &Course) -> Result<(), String> {
    for (i, w) in c.weeks.iter().enumerate() {
        if usize::from(w.n) != i + 1 {
            return Err(format!("주차 번호가 1부터 연속이 아닙니다: {}", w.n));
        }
    }
    let evidence: HashSet<&str> = c.evidence.iter().map(|e| e.id.as_str()).collect();
    let competencies: HashSet<&str> = c.competencies.iter().map(|x| x.id.as_str()).collect();
    let week_count = c.weeks.len();
    let week_ok = |n: u8| (1..=week_count).contains(&usize::from(n));

    let mut task_ids = HashSet::new();
    for w in &c.weeks {
        for t in &w.tasks {
            if !task_ids.insert(t.id.as_str()) {
                return Err(format!("과제 ID 중복: {}", t.id));
            }
            if !matches!(t.track.as_str(), "all" | "ai" | "data") {
                return Err(format!("알 수 없는 경로 {}: {}", t.track, t.id));
            }
            if !t.id.bytes().all(|b| b.is_ascii_alphanumeric() || b == b'-') {
                return Err(format!("과제 ID 형식 오류: {}", t.id));
            }
        }
        for id in &w.evidence {
            if !evidence.contains(id.as_str()) {
                return Err(format!("{}주차가 없는 근거 {id}를 참조합니다", w.n));
            }
        }
        for id in &w.competencies {
            if !competencies.contains(id.as_str()) {
                return Err(format!("{}주차가 없는 역량 {id}를 참조합니다", w.n));
            }
        }
    }
    for x in &c.competencies {
        if let Some(id) = x.evidence.iter().find(|id| !evidence.contains(id.as_str())) {
            return Err(format!("역량 {}이 없는 근거 {id}를 참조합니다", x.id));
        }
    }
    if let Some(s) = c.scenario.stages.iter().find(|s| !week_ok(s.week)) {
        return Err(format!("프로젝트 단계의 주차가 범위 밖입니다: {}", s.week));
    }
    if let Some(t) = c.interview.iter().find(|t| !week_ok(t.week)) {
        return Err(format!("면접 유형 {}의 주차가 범위 밖입니다", t.id));
    }
    for e in &c.evidence {
        if !safe_url(&e.url) {
            return Err(format!("근거 {}의 URL은 https여야 합니다", e.id));
        }
        if !matches!(
            e.status.as_str(),
            "current" | "ongoing" | "closed" | "unknown"
        ) || !matches!(e.region.as_str(), "korea" | "overseas")
            || !matches!(e.source_type.as_str(), "A" | "B" | "C")
        {
            return Err(format!(
                "근거 {}의 상태·지역·출처 유형 값이 잘못됐습니다",
                e.id
            ));
        }
    }
    // 브라우저 검사(logic.js의 RATINGS)와 같은 값이어야 자기평가 저장이 맞물린다.
    let rubric: Vec<&str> = c.rubric.iter().map(|r| r.id.as_str()).collect();
    if rubric != ["weak", "met", "evidence"] {
        return Err(format!(
            "루브릭 ID는 weak, met, evidence여야 합니다: {rubric:?}"
        ));
    }
    if let Some(s) = c.stats.iter().find(|s| !safe_url(&s.url)) {
        return Err(format!("통계 {}의 URL은 https여야 합니다", s.id));
    }
    Ok(())
}

fn safe_url(url: &str) -> bool {
    url.starts_with("https://") && !url.contains(['"', '<', '>', ' '])
}

// ---------- HTML 도우미 ----------

/// 텍스트와 속성 값 양쪽에 안전한 HTML 이스케이프.
fn esc(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    for ch in s.chars() {
        match ch {
            '&' => out.push_str("&amp;"),
            '<' => out.push_str("&lt;"),
            '>' => out.push_str("&gt;"),
            '"' => out.push_str("&quot;"),
            '\'' => out.push_str("&#39;"),
            _ => out.push(ch),
        }
    }
    out
}

fn ext_link(url: &str, text: &str) -> String {
    if safe_url(url) {
        format!(
            "<a href=\"{}\" rel=\"noopener noreferrer\" target=\"_blank\">{}<span class=\"sr-only\"> (새 창)</span></a>",
            esc(url),
            esc(text)
        )
    } else {
        esc(text)
    }
}

fn list(items: &[String]) -> String {
    let mut s = String::from("<ul>");
    for i in items {
        let _ = write!(s, "<li>{}</li>", esc(i));
    }
    s.push_str("</ul>");
    s
}

fn minutes_label(m: u32) -> String {
    match (m / 60, m % 60) {
        (0, r) => format!("{r}분"),
        (h, 0) => format!("{h}시간"),
        (h, r) => format!("{h}시간 {r}분"),
    }
}

fn track_label(track: &str) -> &'static str {
    match track {
        "ai" => "기본 경로 (LLM 적용)",
        "data" => "대체 경로 (데이터 파이프라인)",
        _ => "",
    }
}

fn status_label(status: &str) -> &'static str {
    match status {
        "current" => "현행",
        "ongoing" => "상시채용",
        "closed" => "마감 (과거 공고)",
        _ => "확인불가",
    }
}

fn source_label(t: &str) -> &'static str {
    match t {
        "A" => "회사 채용 페이지",
        "B" => "채용 플랫폼에 회사가 게시",
        _ => "2차 자료",
    }
}

fn task_index_json(c: &Course) -> String {
    let weeks: Vec<_> = c
        .weeks
        .iter()
        .map(|w| serde_json::json!({ "n": w.n, "title": w.title, "problem": w.problem }))
        .collect();
    let tasks: Vec<_> = c
        .weeks
        .iter()
        .flat_map(|w| {
            w.tasks.iter().map(move |t| {
                serde_json::json!({
                    "id": t.id, "week": w.n, "title": t.title, "minutes": t.minutes, "track": t.track
                })
            })
        })
        .collect();
    let interview_types: Vec<_> = c
        .interview
        .iter()
        .map(|t| serde_json::json!({ "id": t.id, "name": t.name }))
        .collect();
    serde_json::json!({
        "courseVersion": c.version,
        "weeks": weeks,
        "tasks": tasks,
        "interviewTypes": interview_types,
    })
    .to_string()
    .replace('<', "\\u003c")
}

const NAV: [(&str, &str, &str); 8] = [
    ("/", "오늘의 학습", "home"),
    ("/weeks", "주차별 과정", "weeks"),
    ("/map", "역량 지도", "map"),
    ("/project", "고객 프로젝트", "project"),
    ("/interview", "면접 준비", "interview"),
    ("/applications", "지원 현황", "applications"),
    ("/evidence", "근거 자료", "evidence"),
    ("/settings", "설정·백업", "settings"),
];

fn layout(app: &App, page: &str, title: &str, body: &str) -> String {
    let mut nav = String::new();
    for (href, label, id) in NAV {
        let current = if id == page {
            " aria-current=\"page\""
        } else {
            ""
        };
        let _ = write!(nav, "<li><a href=\"{href}\"{current}>{label}</a></li>");
    }
    format!(
        r##"<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · FDE 학습 공간</title>
<link rel="stylesheet" href="/static/app.css">
<script type="module" src="/static/app.js"></script>
</head>
<body data-page="{page}">
<a class="skip" href="#main">본문으로 건너뛰기</a>
<div class="shell">
<header class="side">
<p class="brand"><a href="/">FDE 학습 공간</a></p>
<nav aria-label="학습 메뉴"><ul>{nav}</ul></nav>
<p class="side-note">자료 검증일 {verified}<br>진도는 이 브라우저에만 저장됩니다.</p>
</header>
<main id="main" tabindex="-1">
<div id="notice" class="notice" role="alert" hidden></div>
{body}
</main>
</div>
<script type="application/json" id="course-index">{index}</script>
</body>
</html>"##,
        title = esc(title),
        page = page,
        nav = nav,
        verified = esc(&app.course.verified_on),
        body = body,
        index = app.index_json,
    )
}

fn html(body: String) -> Response {
    let mut res = ([(header::CONTENT_TYPE, "text/html; charset=utf-8")], body).into_response();
    secure_headers(&mut res);
    res
}

fn asset(content_type: &'static str, body: &'static str) -> Response {
    let mut res = ([(header::CONTENT_TYPE, content_type)], body).into_response();
    secure_headers(&mut res);
    res
}

fn secure_headers(res: &mut Response) {
    let h = res.headers_mut();
    h.insert(
        header::CONTENT_SECURITY_POLICY,
        HeaderValue::from_static(CSP),
    );
    h.insert(
        header::X_CONTENT_TYPE_OPTIONS,
        HeaderValue::from_static("nosniff"),
    );
    h.insert(
        header::REFERRER_POLICY,
        HeaderValue::from_static("no-referrer"),
    );
    h.insert(header::CACHE_CONTROL, HeaderValue::from_static("no-cache"));
}

// ---------- 페이지 ----------

async fn home(State(app): State<Shared>) -> Response {
    let first = app.course.weeks.first();
    let fallback = first.map_or(String::new(), |w| {
        format!(
            "<p class=\"problem\">{}</p><p><a class=\"button\" href=\"/weeks/1\">1주차 시작하기</a></p>",
            esc(&w.problem)
        )
    });
    let body = format!(
        r##"<section class="today" aria-labelledby="today-h">
<h1 id="today-h">오늘의 고객 과제</h1>
<div id="today">{fallback}</div>
</section>
<section aria-labelledby="progress-h">
<h2 id="progress-h">진행 상황</h2>
<p class="muted">과제 체크는 수행했다는 표시이고, 자기평가는 루브릭에 따른 판단입니다. 둘은 따로 셉니다.</p>
<dl class="stats">
<div><dt>체크한 과제</dt><dd id="stat-done">–</dd></div>
<div><dt>자기평가 충족 이상</dt><dd id="stat-met">–</dd></div>
<div><dt>남은 예상 시간</dt><dd id="stat-left">–</dd></div>
</dl>
<label class="progress-label" for="overall">전체 체크 진행률</label>
<progress id="overall" max="100" value="0">0%</progress>
<p id="estimate" class="muted"></p>
</section>
<section aria-labelledby="about-h">
<h2 id="about-h">이 과정이 약속하지 않는 것</h2>
<p>이 과정은 취업을 보장하지 않습니다. FDE가 일반 개발자보다 취업이 쉽다는 자료(지원자 수, 합격률)는 찾지 못했습니다. 공고 수 증가 보도와 그 한계는 <a href="/evidence#stats">근거 자료</a>에 있습니다.</p>
</section>"##
    );
    html(layout(&app, "home", "오늘의 학습", &body))
}

async fn weeks(State(app): State<Shared>) -> Response {
    let mut items = String::new();
    for w in &app.course.weeks {
        let minutes: u32 = w
            .tasks
            .iter()
            .filter(|t| t.track != "data")
            .map(|t| t.minutes)
            .sum();
        let _ = write!(
            items,
            r##"<li class="week-row">
<h2><a href="/weeks/{n}">{n}주차. {title}</a></h2>
<p>{goal}</p>
<p class="meta">과제 {count}개 · 기본 경로 약 {time} · <span data-week-progress="{n}">진행률 계산 중</span></p>
</li>"##,
            n = w.n,
            title = esc(&w.title),
            goal = esc(&w.goal),
            count = w.tasks.len(),
            time = minutes_label(minutes),
        );
    }
    let body = format!(
        r##"<h1>주차별 과정</h1>
<p class="lead">기본값은 주 10시간 × 12주입니다. 설정에서 주당 시간을 바꾸면 오늘의 학습 화면의 예상 기간이 바뀝니다. 실습 언어는 Python 기본, 필요하면 TypeScript를 씁니다.</p>
<ol class="week-list">{items}</ol>"##
    );
    html(layout(&app, "weeks", "주차별 과정", &body))
}

async fn week(State(app): State<Shared>, Path(n): Path<String>) -> Response {
    let Some(w) = n
        .parse::<usize>()
        .ok()
        .and_then(|n| n.checked_sub(1))
        .and_then(|i| app.course.weeks.get(i))
    else {
        return not_found(State(app)).await;
    };

    let intro: String = w
        .intro
        .iter()
        .map(|p| format!("<p>{}</p>", esc(p)))
        .collect();
    let evidence: String = w
        .evidence
        .iter()
        .filter_map(|id| app.course.evidence.iter().find(|e| &e.id == id))
        .map(|e| {
            format!(
                "<li><a href=\"/evidence#{id}\">{id} {company}</a> <span class=\"meta\">{status}</span></li>",
                id = esc(&e.id),
                company = esc(&e.company),
                status = status_label(&e.status),
            )
        })
        .collect();
    let competencies: String = w
        .competencies
        .iter()
        .filter_map(|id| app.course.competencies.iter().find(|c| &c.id == id))
        .map(|c| {
            format!(
                "<li><a href=\"/map#{}\">{}</a></li>",
                esc(&c.id),
                esc(&c.name)
            )
        })
        .collect();

    let mut tasks = String::new();
    for (i, t) in w.tasks.iter().enumerate() {
        let track = if t.track == "all" {
            String::new()
        } else {
            format!(
                "<p class=\"track\" data-track-note=\"{}\">{}</p>",
                esc(&t.track),
                track_label(&t.track)
            )
        };
        let steps: String = t
            .steps
            .iter()
            .map(|s| format!("<li>{}</li>", esc(s)))
            .collect();
        let id = esc(&t.id);
        let _ = write!(
            tasks,
            r##"<article class="task" id="{id}" data-task="{id}" data-track="{track_id}">
<h3>과제 {num}. {title} <span class="meta">약 {time}</span></h3>
{track}
<h4>순서</h4>
<ol class="steps">{steps}</ol>
<h4>제출할 산출물</h4>
<p>{deliverable}</p>
<h4>완료 기준</h4>
{criteria}
<fieldset class="record">
<legend>내 기록</legend>
<label class="check"><input type="checkbox" name="done" id="{id}-done"> 과제를 수행했고 산출물이 있습니다</label>
<label for="{id}-rating">자기평가</label>
<select id="{id}-rating" name="rating">
<option value="">아직 평가하지 않음</option>
<option value="weak">미흡</option>
<option value="met">충족</option>
<option value="evidence">증거 수준</option>
</select>
<label for="{id}-note">메모 (산출물 위치, 막힌 점)</label>
<textarea id="{id}-note" name="note" rows="3" maxlength="5000"></textarea>
<p class="saved" role="status" aria-live="polite"></p>
</fieldset>
</article>"##,
            track_id = esc(&t.track),
            num = i + 1,
            title = esc(&t.title),
            time = minutes_label(t.minutes),
            deliverable = esc(&t.deliverable),
            criteria = list(&t.criteria),
        );
    }

    let rubric: String = app
        .course
        .rubric
        .iter()
        .map(|r| {
            format!(
                "<div><dt>{}</dt><dd>{}</dd></div>",
                esc(&r.name),
                esc(&r.description)
            )
        })
        .collect();

    let prev = if w.n > 1 {
        format!("<a href=\"/weeks/{0}\">{0}주차로</a>", w.n - 1)
    } else {
        String::new()
    };
    let next = if usize::from(w.n) < app.course.weeks.len() {
        format!("<a href=\"/weeks/{0}\">{0}주차로</a>", w.n + 1)
    } else {
        "<a href=\"/interview\">면접 준비로</a>".to_string()
    };

    let body = format!(
        r##"<p class="crumb"><a href="/weeks">주차별 과정</a></p>
<h1>{n}주차. {title}</h1>
<p class="lead">{goal}</p>
<section class="problem-note" aria-labelledby="problem-h">
<h2 id="problem-h">고객 상황</h2>
<p>{problem}</p>
</section>
<section aria-labelledby="why-h">
<h2 id="why-h">왜 이걸 하나</h2>
{intro}
<div class="refs">
<div><h3>관련 역량</h3><ul>{competencies}</ul></div>
<div><h3>근거 공고</h3><ul>{evidence}</ul></div>
</div>
</section>
<section aria-labelledby="tasks-h">
<h2 id="tasks-h">과제</h2>
<details class="rubric"><summary>자기평가 기준 보기</summary><dl>{rubric}</dl></details>
{tasks}
</section>
<nav class="pager" aria-label="주차 이동">{prev}{next}</nav>"##,
        n = w.n,
        title = esc(&w.title),
        goal = esc(&w.goal),
        problem = esc(&w.problem),
    );
    html(layout(&app, "weeks", &format!("{}주차", w.n), &body))
}

async fn map(State(app): State<Shared>) -> Response {
    let mut rows = String::new();
    for c in &app.course.competencies {
        let weeks: String = app
            .course
            .weeks
            .iter()
            .filter(|w| w.competencies.contains(&c.id))
            .map(|w| format!("<li><a href=\"/weeks/{0}\">{0}주차</a></li>", w.n))
            .collect();
        let evidence: String = c
            .evidence
            .iter()
            .filter_map(|id| app.course.evidence.iter().find(|e| &e.id == id))
            .map(|e| {
                format!(
                    "<li><a href=\"/evidence#{0}\">{0} {1}</a></li>",
                    esc(&e.id),
                    esc(&e.company)
                )
            })
            .collect();
        let _ = write!(
            rows,
            r##"<section class="competency" id="{id}" aria-labelledby="{id}-h">
<h2 id="{id}-h">{name}</h2>
<p>{desc}</p>
<div class="refs">
<div><h3>근거 공고 {count}건</h3><ul class="inline">{evidence}</ul></div>
<div><h3>다루는 주차</h3><ul class="inline">{weeks}</ul></div>
</div>
</section>"##,
            id = esc(&c.id),
            name = esc(&c.name),
            desc = esc(&c.description),
            count = c.evidence.len(),
        );
    }
    let body = format!(
        r##"<h1>역량 지도</h1>
<p class="lead">공고 원문에서 반복된 요구를 8개 역량으로 묶었습니다. 근거 건수는 상세를 확인한 공고 9건과 2차 자료 1건 기준이며, 표본이 작아 일반화할 수 없습니다.</p>
{rows}"##
    );
    html(layout(&app, "map", "역량 지도", &body))
}

async fn project(State(app): State<Shared>) -> Response {
    let s = &app.course.scenario;
    let stages: String = s
        .stages
        .iter()
        .map(|st| {
            format!(
                r##"<li><h3><a href="/weeks/{w}">{title}</a></h3><p>{w}주차 산출물: {d}</p><p class="meta" data-week-progress="{w}">진행률 계산 중</p></li>"##,
                w = st.week,
                title = esc(&st.title),
                d = esc(&st.deliverable),
            )
        })
        .collect();
    let body = format!(
        r##"<h1>고객 프로젝트</h1>
<section class="problem-note" aria-labelledby="sc-h">
<h2 id="sc-h">{name}</h2>
<p>{summary}</p>
</section>
<section aria-labelledby="people-h">
<h2 id="people-h">이해관계자</h2>
{people}
</section>
<section aria-labelledby="stage-h">
<h2 id="stage-h">단계와 산출물</h2>
<p class="muted">각 단계는 해당 주차 과제로 이어집니다. 산출물은 한 저장소에 모아 두면 11주차 사례 문서를 쓰기 쉽습니다.</p>
<ol class="stages">{stages}</ol>
</section>"##,
        name = esc(&s.name),
        summary = esc(&s.summary),
        people = list(&s.stakeholders),
    );
    html(layout(&app, "project", "고객 프로젝트", &body))
}

async fn interview(State(app): State<Shared>) -> Response {
    let mut types = String::new();
    let mut options = String::new();
    for t in &app.course.interview {
        let _ = write!(
            types,
            r##"<section class="itype" id="i-{id}" aria-labelledby="i-{id}-h">
<h3 id="i-{id}-h">{name}</h3>
<p class="meta">관련: <a href="/weeks/{w}">{w}주차</a></p>
<h4>연습 문항</h4>{prompts}
<h4>좋은 답의 기준</h4>{good}
</section>"##,
            id = esc(&t.id),
            name = esc(&t.name),
            w = t.week,
            prompts = list(&t.prompts),
            good = list(&t.good),
        );
        let _ = write!(
            options,
            "<option value=\"{}\">{}</option>",
            esc(&t.id),
            esc(&t.name)
        );
    }
    let body = format!(
        r##"<h1>면접 준비</h1>
<p class="lead">아래 문항은 이 앱이 만든 연습용 문항입니다. 실제 회사의 면접 문항이 아닙니다. 녹화하거나 동료와 연습한 뒤 기준에 따라 스스로 채점하세요.</p>
<section aria-labelledby="log-h">
<h2 id="log-h">연습 기록</h2>
<form id="interview-form" class="form" novalidate>
<label for="iv-type">유형</label>
<select id="iv-type" name="type" required>{options}</select>
<label for="iv-date">날짜</label>
<input id="iv-date" name="date" type="date">
<label for="iv-score">자기 채점</label>
<select id="iv-score" name="score">
<option value="">채점하지 않음</option>
<option value="weak">미흡</option>
<option value="met">충족</option>
<option value="evidence">증거 수준</option>
</select>
<label for="iv-note">돌아보기 (잘한 점, 다음에 바꿀 점)</label>
<textarea id="iv-note" name="note" rows="4" maxlength="5000"></textarea>
<p class="form-error" id="iv-error" role="alert" hidden></p>
<button type="submit">연습 기록 추가</button>
</form>
<p id="iv-summary" class="muted" role="status" aria-live="polite"></p>
<ul id="interview-list" class="records"></ul>
</section>
<section aria-labelledby="types-h">
<h2 id="types-h">유형별 문항</h2>
{types}
</section>"##
    );
    html(layout(&app, "interview", "면접 준비", &body))
}

async fn applications(State(app): State<Shared>) -> Response {
    let body = r##"<h1>지원 현황</h1>
<p class="lead">지원하기 전에 공고 원문을 다시 열어 상태와 조건을 확인하세요. 기록은 이 브라우저에만 저장되고 어디에도 제출되지 않습니다.</p>
<form id="app-form" class="form" novalidate>
<input type="hidden" name="id" id="ap-id">
<label for="ap-company">회사 (필수)</label>
<input id="ap-company" name="company" required maxlength="100" autocomplete="off">
<label for="ap-url">공고 URL</label>
<input id="ap-url" name="url" type="url" maxlength="2000" placeholder="https://" autocomplete="off">
<label for="ap-status">상태</label>
<select id="ap-status" name="status">
<option value="interested">관심</option>
<option value="applied">지원 완료</option>
<option value="screen">서류 통과</option>
<option value="interview">면접 중</option>
<option value="offer">합격</option>
<option value="rejected">불합격</option>
<option value="hold">보류 (조건 미충족 등)</option>
</select>
<label for="ap-date">날짜</label>
<input id="ap-date" name="date" type="date">
<label for="ap-memo">메모 (원문 확인 날짜, 조건, 다음 할 일)</label>
<textarea id="ap-memo" name="memo" rows="4" maxlength="5000"></textarea>
<p class="form-error" id="ap-error" role="alert" hidden></p>
<div class="actions">
<button type="submit" id="ap-submit">지원 기록 추가</button>
<button type="button" id="ap-cancel" class="secondary" hidden>수정 취소</button>
</div>
</form>
<p id="ap-summary" class="muted" role="status" aria-live="polite"></p>
<ul id="app-list" class="records"></ul>"##;
    html(layout(&app, "applications", "지원 현황", body))
}

async fn evidence(State(app): State<Shared>) -> Response {
    let mut cards = String::new();
    for e in &app.course.evidence {
        let exp = e.experience_min.map_or(String::new(), |m| m.to_string());
        let region = if e.region == "korea" {
            "한국 근무"
        } else {
            "해외"
        };
        let _ = write!(
            cards,
            r##"<article class="posting" id="{id}" data-region="{region_id}" data-status="{status}" data-exp="{exp}">
<h3>{id}. {company} — {title}</h3>
<p class="meta">{region} · {location} · <strong>{status_label}</strong> · {source} · 접근일 {accessed}</p>
<p>원문: {link}</p>
<p><strong>경력:</strong> {experience}</p>
<h4>필수 또는 요구 역량</h4>{required}
<h4>우대</h4>{preferred}
<h4>지역·근무·언어 조건</h4>{conditions}
<p class="meta">검증: {note}</p>
</article>"##,
            id = esc(&e.id),
            region_id = esc(&e.region),
            status = esc(&e.status),
            company = esc(&e.company),
            title = esc(&e.title),
            location = esc(&e.location),
            status_label = status_label(&e.status),
            source = source_label(&e.source_type),
            accessed = esc(&e.accessed),
            link = ext_link(&e.url, &e.url),
            experience = esc(&e.experience),
            required = list(&e.required),
            preferred = list(&e.preferred),
            conditions = list(&e.conditions),
            note = esc(&e.note),
        );
    }
    let stats: String = app
        .course
        .stats
        .iter()
        .map(|s| {
            format!(
                "<li><p>{}</p><p class=\"meta\">{} · 접근일 {} · {}</p><p><strong>한계:</strong> {}</p></li>",
                esc(&s.claim),
                esc(&s.source),
                esc(&s.accessed),
                ext_link(&s.url, "원문"),
                esc(&s.caveat)
            )
        })
        .collect();
    let excluded: String = app
        .course
        .excluded
        .iter()
        .map(|x| {
            format!(
                "<li><strong>{}</strong>: {}</li>",
                esc(&x.name),
                esc(&x.reason)
            )
        })
        .collect();

    let body = format!(
        r##"<h1>근거 자료</h1>
<p class="lead">공식 채용 페이지와 채용 플랫폼의 공고 원문을 {verified}에 열람해 정리했습니다. 공고는 수시로 바뀌므로 지원 전에 원문을 다시 확인하세요. 정리 과정과 재검증 기록은 저장소의 docs/research.md, docs/verification.md에 있습니다.</p>
<form id="ev-filter" class="filters" aria-describedby="ev-count">
<fieldset>
<legend>지역</legend>
<label><input type="radio" name="region" value="all" checked> 전체</label>
<label><input type="radio" name="region" value="korea"> 한국 근무</label>
<label><input type="radio" name="region" value="overseas"> 해외</label>
</fieldset>
<fieldset>
<legend>상태</legend>
<label><input type="checkbox" name="status" value="current" checked> 현행</label>
<label><input type="checkbox" name="status" value="ongoing" checked> 상시채용</label>
<label><input type="checkbox" name="status" value="closed" checked> 마감 (과거)</label>
<label><input type="checkbox" name="status" value="unknown" checked> 확인불가</label>
</fieldset>
<fieldset>
<legend>경력</legend>
<label><input type="checkbox" name="exp" value="mine"> 내 경력 연수로 충족하는 공고만</label>
<p class="muted" id="exp-hint">경력 연수만 비교합니다. 비밀취급인가, 거주지, 출장 같은 다른 조건과 지원 자격은 보장하지 않습니다. 경력이 미명시된 공고는 이 필터에서 빠집니다.</p>
</fieldset>
</form>
<p id="ev-count" role="status" aria-live="polite"></p>
<div id="postings">{cards}</div>
<p id="ev-empty" class="empty" hidden>조건에 맞는 공고가 없습니다. 필터를 줄이거나 설정에서 경력 연수를 확인하세요.</p>
<section id="stats" aria-labelledby="stats-h">
<h2 id="stats-h">공고 수 통계와 한계</h2>
<p>공고 수 증가는 수요 신호일 뿐 취업이 쉽다는 근거가 아닙니다. 공고당 지원자 수, 합격률 같은 비교 자료는 찾지 못했습니다.</p>
<ul class="records">{stats}</ul>
</section>
<section aria-labelledby="ex-h">
<h2 id="ex-h">확인하지 못해 제외한 자료</h2>
<ul>{excluded}</ul>
</section>"##,
        verified = esc(&app.course.verified_on),
    );
    html(layout(&app, "evidence", "근거 자료", &body))
}

async fn settings(State(app): State<Shared>) -> Response {
    let body = r##"<h1>설정·백업</h1>
<section aria-labelledby="pref-h">
<h2 id="pref-h">학습 설정</h2>
<form id="settings-form" class="form" novalidate>
<label for="st-exp">개발 경력 (년)</label>
<input id="st-exp" name="experienceYears" type="number" min="0" max="50" step="1" inputmode="numeric" aria-describedby="st-exp-hint">
<p class="muted" id="st-exp-hint">비워 두면 근거 자료의 경력 필터를 쓸 수 없습니다.</p>
<label for="st-region">희망 지역</label>
<select id="st-region" name="region">
<option value="both">한국과 해외 모두</option>
<option value="korea">한국 근무</option>
<option value="overseas">해외</option>
</select>
<label for="st-hours">주당 학습 시간</label>
<input id="st-hours" name="hoursPerWeek" type="number" min="1" max="60" step="1" inputmode="numeric" required>
<fieldset>
<legend>7–8주차 경로</legend>
<label><input type="radio" name="track" value="ai"> 기본 경로: LLM 적용·평가</label>
<label><input type="radio" name="track" value="data"> 대체 경로: 데이터 파이프라인·품질</label>
</fieldset>
<p class="form-error" id="st-error" role="alert" hidden></p>
<button type="submit">설정 저장</button>
</form>
</section>
<section aria-labelledby="backup-h">
<h2 id="backup-h">백업</h2>
<p>진도, 자기평가, 메모, 면접 기록, 지원 기록, 설정을 JSON 파일 하나로 내보냅니다. 브라우저 데이터를 지우거나 다른 브라우저로 옮기기 전에 내보내세요.</p>
<p id="storage-state" class="muted"></p>
<div class="actions"><button type="button" id="export">백업 파일 내보내기</button></div>
<label for="import-file">백업 파일 가져오기</label>
<input id="import-file" type="file" accept="application/json,.json" aria-describedby="import-hint">
<p class="muted" id="import-hint">파일 전체를 검사한 뒤 문제가 없을 때만 바꿀 수 있습니다. 문제가 있으면 지금 데이터는 그대로 남습니다.</p>
<div id="import-result" role="status" aria-live="polite"></div>
<div class="actions"><button type="button" id="import-apply" hidden>가져온 내용으로 바꾸기</button></div>
</section>
<section aria-labelledby="reset-h">
<h2 id="reset-h">초기화</h2>
<p>저장된 모든 기록을 지웁니다. 되돌릴 수 없으니 먼저 백업을 내보내세요.</p>
<div class="actions">
<button type="button" id="download-raw" class="secondary" hidden>읽을 수 없는 저장 원본 내려받기</button>
<button type="button" id="reset" class="danger">모든 기록 지우기</button>
</div>
</section>"##;
    html(layout(&app, "settings", "설정·백업", body))
}

async fn not_found(State(app): State<Shared>) -> Response {
    let body = r##"<h1>페이지를 찾을 수 없습니다</h1>
<p>주소가 바뀌었거나 없는 주차입니다. <a href="/weeks">주차별 과정</a>에서 다시 고르세요.</p>"##;
    let mut res = html(layout(&app, "missing", "없는 페이지", body));
    *res.status_mut() = StatusCode::NOT_FOUND;
    res
}

#[cfg(test)]
mod tests {
    use super::*;

    fn course() -> Course {
        serde_json::from_str(COURSE_JSON).expect("course.json parses")
    }

    #[test]
    fn course_json_should_pass_validation() {
        assert_eq!(validate(&course()), Ok(()));
    }

    #[test]
    fn course_should_have_twelve_weeks() {
        assert_eq!(course().weeks.len(), 12);
    }

    #[test]
    fn esc_should_escape_html_and_attribute_characters() {
        assert_eq!(
            esc(r##"<script>alert('x')</script> & "q""##),
            "&lt;script&gt;alert(&#39;x&#39;)&lt;/script&gt; &amp; &quot;q&quot;"
        );
    }

    #[test]
    fn ext_link_should_render_text_only_for_unsafe_scheme() {
        assert_eq!(
            ext_link("javascript:alert(1)", "<b>x</b>"),
            "&lt;b&gt;x&lt;/b&gt;"
        );
    }

    #[test]
    fn task_index_should_not_contain_raw_angle_bracket() {
        let mut c = course();
        c.weeks[0].title = "</script><script>alert(1)</script>".into();
        assert!(!task_index_json(&c).contains('<'));
    }

    #[test]
    fn validate_should_reject_duplicate_task_ids() {
        let mut c = course();
        let dup = c.weeks[0].tasks[0].id.clone();
        c.weeks[1].tasks[0].id = dup;
        assert!(validate(&c).is_err());
    }

    #[test]
    fn validate_should_reject_non_https_evidence_url() {
        let mut c = course();
        c.evidence[0].url = "http://example.com".into();
        assert!(validate(&c).is_err());
    }

    #[test]
    fn minutes_label_should_format_hours_and_minutes() {
        assert_eq!(minutes_label(150), "2시간 30분");
    }
}
