"""8.2 상담 문의 분류 시스템: 웹훅 수신(2.6) → 중복 제거·저장(2.5, 3.2) → 가명화(3.5) → 분류(6.1) → 테넌트별 조회(5.5).

표준 라이브러리만 쓴다. 분류의 '모델' 단계는 결정적인 대체 함수이며, 실제 시스템에서는 LLM 호출 + 스키마 검증으로 바꾼다."""
import hashlib
import hmac
import json
import re
import sqlite3
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (event_id TEXT PRIMARY KEY);
CREATE TABLE IF NOT EXISTS inquiries (
  event_id TEXT PRIMARY KEY REFERENCES events(event_id),
  tenant   TEXT NOT NULL,
  customer TEXT NOT NULL,              -- 가명(HMAC). 이메일 원문은 저장하지 않는다
  text     TEXT NOT NULL,
  category TEXT NOT NULL CHECK (category IN ('배송', '환불', '계정', '기타', '검토필요')),
  urgent   INTEGER NOT NULL CHECK (urgent IN (0, 1)),
  route    TEXT NOT NULL CHECK (route IN ('rule', 'model', 'human'))
);
CREATE INDEX IF NOT EXISTS inquiries_tenant ON inquiries(tenant, category);
"""
CATEGORIES = ("배송", "환불", "계정", "기타")
RULES = {  # 확신이 높은 단서만 규칙으로 둔다
    "배송": ["배송", "송장", "택배", "도착"],
    "환불": ["환불", "반품", "결제 취소"],
    "계정": ["비밀번호", "로그인", "인증"],
}
MODEL_HINTS = {  # '모델' 단계의 대체: 규칙보다 넓은 단서. 실제로는 LLM이 이 자리를 맡는다
    "환불": ["돈이 안", "카드에 그대로", "환불 계좌"],
    "계정": ["탈퇴", "휴대폰 번호"],
    "기타": ["세금계산서", "영업시간", "제휴", "앱이", "상담원"],
}
URGENT = re.compile(r"급해요|오늘 꼭|사기")


def open_db(path=":memory:"):
    db = sqlite3.connect(path, check_same_thread=False)
    db.executescript(SCHEMA)
    db.commit()
    return db


def sign(secret, timestamp, raw):
    return "sha256=" + hmac.new(secret, f"{timestamp}.".encode() + raw, hashlib.sha256).hexdigest()


def pseudonym(key, email):
    return "c_" + hmac.new(key, email.strip().lower().encode(), hashlib.sha256).hexdigest()[:12]


def classify(text):
    """(분류, 경로)를 돌려준다. 규칙이 정확히 한 분류를 가리킬 때만 규칙으로 정한다."""
    hits = [c for c, words in RULES.items() if any(w in text for w in words)]
    if len(hits) == 1:
        return hits[0], "rule"
    proposal = next((c for c, words in MODEL_HINTS.items() if any(w in text for w in words)), None)
    if proposal in CATEGORIES:  # 모델 출력도 허용 목록으로 검증한다(6.1절)
        return proposal, "model"
    return "검토필요", "human"


def ingest(db, keys, headers, raw, now):
    """웹훅 하나를 처리한다. (HTTP 상태, 설명)을 돌려준다."""
    try:
        timestamp = int(headers.get("X-Timestamp", ""))
    except ValueError:
        return 400, "서명 헤더 없음"
    if abs(now - timestamp) > 300:
        return 400, "오래된 요청"
    if not hmac.compare_digest(sign(keys["webhook"], timestamp, raw), headers.get("X-Signature", "")):
        return 401, "서명 불일치"
    event = json.loads(raw)
    category, route = classify(event["text"])
    try:
        with db:  # 이벤트 기록과 문의 저장을 한 트랜잭션으로(3.2절)
            db.execute("INSERT INTO events VALUES (?)", (event["event_id"],))
            db.execute("INSERT INTO inquiries VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (event["event_id"], event["tenant"], pseudonym(keys["pseudonym"], event["email"]),
                        event["text"], category, int(bool(URGENT.search(event["text"]))), route))
    except sqlite3.IntegrityError:
        return 200, "중복 이벤트(무시)"
    return 200, f"{category}/{route}"


def query(db, tenant, category=None):
    sql, args = "SELECT event_id, category, urgent, route FROM inquiries WHERE tenant = ?", [tenant]
    if category:
        sql, args = sql + " AND category = ?", args + [category]
    rows = db.execute(sql + " ORDER BY urgent DESC, event_id", args).fetchall()
    return [dict(zip(("event_id", "category", "urgent", "route"), r)) for r in rows]


def make_server(db, keys, tokens, clock):
    """tokens: Bearer 토큰 -> 테넌트. clock: 현재 시각(초)을 돌려주는 함수(테스트에서 고정)."""
    lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def reply(self, status, body):
            data = json.dumps(body, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_POST(self):
            raw = self.rfile.read(int(self.headers.get("Content-Length", "0")))
            if self.path != "/webhooks/inquiry":
                return self.reply(404, {"detail": "없는 경로"})
            with lock:
                status, detail = ingest(db, keys, self.headers, raw, clock())
            self.reply(status, {"detail": detail})

        def do_GET(self):
            url = urlparse(self.path)
            tenant = tokens.get(self.headers.get("Authorization", "").removeprefix("Bearer "))
            if tenant is None:
                return self.reply(401, {"detail": "인증 필요"})
            if url.path != "/inquiries":
                return self.reply(404, {"detail": "없는 경로"})
            category = parse_qs(url.query).get("category", [None])[0]
            self.reply(200, {"tenant": tenant, "items": query(db, tenant, category)})  # 테넌트는 토큰에서만

        def log_message(self, *args):
            pass

    return ThreadingHTTPServer(("127.0.0.1", 0), Handler)
