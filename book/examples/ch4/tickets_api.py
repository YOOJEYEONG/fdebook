"""4.1 작은 백엔드와 인터페이스 계약: 계약(CONTRACT)이 검증·오류·문서의 단일 근거가 된다."""
import json
import sqlite3
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# POST /tickets 요청 본문의 계약. 문서(OpenAPI)와 검증 코드가 같은 내용을 말해야 한다.
CONTRACT = {
    "subject": {"type": str, "required": True, "max_length": 120},
    "body": {"type": str, "required": True, "max_length": 5000},
    "channel": {"type": str, "required": False, "enum": ["email", "chat", "phone"], "default": "email"},
}


def validate(payload):
    """계약을 어긴 항목을 모두 모아 돌려준다. 빈 목록이면 통과."""
    if not isinstance(payload, dict):
        return [{"field": "", "problem": "본문은 JSON 객체여야 합니다"}]
    errors = []
    for name in payload:
        if name not in CONTRACT:
            errors.append({"field": name, "problem": "계약에 없는 필드"})
    for name, rule in CONTRACT.items():
        if name not in payload:
            if rule["required"]:
                errors.append({"field": name, "problem": "필수"})
            continue
        value = payload[name]
        if not isinstance(value, rule["type"]):
            errors.append({"field": name, "problem": f"{rule['type'].__name__} 이어야 합니다"})
        elif "max_length" in rule and len(value) > rule["max_length"]:
            errors.append({"field": name, "problem": f"최대 {rule['max_length']}자"})
        elif "enum" in rule and value not in rule["enum"]:
            errors.append({"field": name, "problem": f"{rule['enum']} 중 하나"})
        elif rule["type"] is str and not value.strip():
            errors.append({"field": name, "problem": "비어 있을 수 없음"})
    return errors


def open_db():
    db = sqlite3.connect(":memory:", check_same_thread=False)
    db.execute("""CREATE TABLE tickets (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  subject TEXT NOT NULL, body TEXT NOT NULL, channel TEXT NOT NULL,
                  status TEXT NOT NULL DEFAULT 'open')""")
    return db


def make_server(db):
    lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def send_json(self, status, body, content_type="application/json"):
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", f"{content_type}; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def problem(self, status, title, **extra):
            self.send_json(status, {"type": "about:blank", "title": title, "status": status, **extra},
                           "application/problem+json")

        def do_POST(self):
            raw = self.rfile.read(int(self.headers.get("Content-Length", "0")))
            if self.path != "/tickets":
                return self.problem(404, "Not Found")
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                return self.problem(400, "Bad Request", detail="본문이 JSON이 아닙니다")
            errors = validate(payload)
            if errors:
                return self.problem(422, "Unprocessable Content", errors=errors)
            with lock, db:
                cursor = db.execute("INSERT INTO tickets (subject, body, channel) VALUES (?, ?, ?)",
                                    (payload["subject"].strip(), payload["body"],
                                     payload.get("channel", CONTRACT["channel"]["default"])))
            self.send_json(201, self.read(cursor.lastrowid))

        def do_GET(self):
            ticket_id = self.path.removeprefix("/tickets/")
            if not ticket_id.isdigit():
                return self.problem(404, "Not Found")
            ticket = self.read(int(ticket_id))
            return self.send_json(200, ticket) if ticket else self.problem(404, "Not Found")

        def read(self, ticket_id):
            row = db.execute("SELECT id, subject, body, channel, status FROM tickets WHERE id = ?",
                             (ticket_id,)).fetchone()
            return dict(zip(["id", "subject", "body", "channel", "status"], row)) if row else None

        def log_message(self, *args):
            pass

    return ThreadingHTTPServer(("127.0.0.1", 0), Handler)


if __name__ == "__main__":
    import urllib.error
    import urllib.request

    server = make_server(open_db())
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_address[1]}"

    def post(payload):
        request = urllib.request.Request(f"{base}/tickets", json.dumps(payload, ensure_ascii=False).encode(),
                                         {"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                return response.status, json.loads(response.read())
        except urllib.error.HTTPError as error:
            return error.code, json.loads(error.read())

    print(post({"subject": "배송 지연", "body": "주문 A-1이 아직 안 왔어요", "channel": "chat"}))
    print(post({"subject": "  ", "channel": "fax", "priority": "high"}))
    with urllib.request.urlopen(f"{base}/tickets/1", timeout=5) as response:
        print(response.status, json.loads(response.read()))
    server.shutdown()
