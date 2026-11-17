"""2.2 상태 코드와 오류 본문, 인증과 권한: 같은 요청이 401, 403, 422, 201로 갈리는 이유."""
import json
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# 예제용 토큰. 실제 토큰은 코드에 쓰지 않고 환경 변수나 비밀 저장소에서 읽는다(4.3절).
TOKENS = {"token-agent": {"user": "kim", "scopes": {"tickets:read"}},
          "token-admin": {"user": "lee", "scopes": {"tickets:read", "tickets:write"}}}


def problem(status, title, detail):
    """RFC 9457 problem details 형식의 오류 본문."""
    return status, {"type": "about:blank", "title": title, "status": status, "detail": detail}


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 오류로 거절하더라도 본문은 먼저 끝까지 읽는다. 읽지 않은 채 응답하고 연결을 닫으면
        # 클라이언트가 응답을 읽기 전에 연결이 재설정(reset)될 수 있다.
        raw = self.rfile.read(int(self.headers.get("Content-Length", "0")))
        status, body, extra = self.handle_create(raw)
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        content_type = "application/problem+json" if status >= 400 else "application/json"
        self.send_header("Content-Type", content_type + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        for name, value in extra.items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(data)

    def handle_create(self, raw):
        auth = self.headers.get("Authorization", "")
        token = auth.removeprefix("Bearer ") if auth.startswith("Bearer ") else ""
        account = TOKENS.get(token)
        if account is None:  # 누구인지 모른다: 인증 실패
            return *problem(401, "Unauthorized", "유효한 Bearer 토큰이 필요합니다."), {
                "WWW-Authenticate": 'Bearer error="invalid_token"'}
        if "tickets:write" not in account["scopes"]:  # 누구인지는 알지만 권한이 없다
            return *problem(403, "Forbidden", "tickets:write 권한이 필요합니다."), {}
        try:
            ticket = json.loads(raw or b"{}")
        except json.JSONDecodeError:
            return *problem(400, "Bad Request", "본문이 JSON이 아닙니다."), {}
        if not str(ticket.get("subject", "")).strip():  # 형식은 맞지만 내용이 규칙에 어긋난다
            return *problem(422, "Unprocessable Content", "subject는 비어 있을 수 없습니다."), {}
        return 201, {"id": "T-100", "subject": ticket["subject"], "created_by": account["user"]}, {
            "Location": "/tickets/T-100"}

    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
url = f"http://127.0.0.1:{server.server_address[1]}/tickets"


def call(label, token, body):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, data=body.encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            status, payload = response.status, json.loads(response.read())
    except urllib.error.HTTPError as error:
        status, payload = error.code, json.loads(error.read())
    summary = payload.get("detail") or f"created {payload['id']} by {payload['created_by']}"
    print(f"{label:<16} -> {status} {summary}")


call("토큰 없음", None, '{"subject": "환불 요청"}')
call("잘못된 토큰", "token-typo", '{"subject": "환불 요청"}')
call("읽기 권한만", "token-agent", '{"subject": "환불 요청"}')
call("JSON 아님", "token-admin", "subject=환불")
call("빈 제목", "token-admin", '{"subject": "  "}')
call("정상", "token-admin", '{"subject": "환불 요청"}')
server.shutdown()
