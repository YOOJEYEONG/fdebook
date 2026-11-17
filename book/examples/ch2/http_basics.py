"""2.1 요청과 응답: 같은 프로세스 안에서 작은 HTTP 서버를 띄우고 urllib로 호출한다."""
import json
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TICKETS = {"1": {"id": "1", "subject": "배송 지연 문의", "status": "open"}}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        ticket_id = self.path.removeprefix("/tickets/")
        ticket = TICKETS.get(ticket_id)
        status, body = (200, ticket) if ticket else (404, {"error": "no such ticket"})
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):  # 예제 출력을 깔끔하게 유지한다
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)  # 포트 0: 운영체제가 빈 포트를 고른다
threading.Thread(target=server.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{server.server_address[1]}"

request = urllib.request.Request(f"{base}/tickets/1", headers={"Accept": "application/json"})
with urllib.request.urlopen(request, timeout=5) as response:
    print("status:", response.status)
    print("content-type:", response.headers["Content-Type"])
    ticket = json.loads(response.read().decode("utf-8"))
    print("subject:", ticket["subject"])

try:
    urllib.request.urlopen(f"{base}/tickets/999", timeout=5)
except urllib.error.HTTPError as error:  # urllib은 4xx/5xx를 예외로 던진다
    print("status:", error.code)
    print("body:", json.loads(error.read().decode("utf-8")))

server.shutdown()
