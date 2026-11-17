"""2.5 멱등성 키: 응답을 못 받은 결제 요청을 안전하게 다시 보내기."""
import hashlib
import json
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

payments = []          # 실제 부작용: 결제 기록
seen = {}              # Idempotency-Key -> (본문 지문, 상태, 응답 본문)
lock = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
        key = self.headers.get("Idempotency-Key")
        status, reply = self.create_payment(key, body)
        data = json.dumps(reply, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(data)

    def create_payment(self, key, body):
        if not key:
            return 400, {"detail": "Idempotency-Key 헤더가 필요합니다."}
        fingerprint = hashlib.sha256(body).hexdigest()
        with lock:  # 같은 키의 동시 요청이 둘 다 결제하지 않도록 확인과 기록을 한 번에
            if key in seen:
                old_fingerprint, status, reply = seen[key]
                if old_fingerprint != fingerprint:
                    return 422, {"detail": "같은 키를 다른 본문에 다시 썼습니다."}
                return status, reply  # 처음 처리한 결과를 그대로 돌려준다
            order = json.loads(body)
            payments.append(order)
            reply = {"payment_id": f"P-{len(payments)}", "amount": order["amount"]}
            seen[key] = (fingerprint, 201, reply)
            return 201, reply

    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
url = f"http://127.0.0.1:{server.server_address[1]}/payments"


def pay(key, amount):
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Idempotency-Key"] = key
    request = urllib.request.Request(url, json.dumps({"amount": amount}).encode(), headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read())


key = "order-2026-0042"  # 클라이언트가 한 번의 '결제 의도'마다 새로 만든다(실제로는 uuid4)
print("첫 요청      :", pay(key, 30000))
print("같은 요청 재전송:", pay(key, 30000), "<- 네트워크 오류로 응답을 못 받았다고 가정")
print("키 재사용·금액 다름:", pay(key, 50000))
print("키 없음      :", pay(None, 30000))
print("실제 결제 건수:", len(payments))
server.shutdown()
