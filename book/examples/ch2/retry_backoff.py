"""2.4 시간 제한, 재시도, 백오프: 실패하는 서버를 상대로 언제 다시 시도하고 언제 멈출지."""
import json
import random
import socket
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

script = iter([503, 429, 200])  # 서버가 차례로 돌려줄 상태 코드


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/slow":  # 응답하지 않는 서버 흉내
            threading.Event().wait(1.0)
        status = next(script, 200) if self.path == "/orders" else 200
        self.send_response(status)
        if status == 429:
            self.send_header("Retry-After", "2")  # 초 단위: 2초 뒤에 다시 오라
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": status}).encode())

    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{server.server_address[1]}"

RETRYABLE = {429, 502, 503, 504}
rng = random.Random(7)  # 예제 출력을 고정하려고 씨앗을 준다. 실제로는 씨앗 없이 쓴다.
waited = []


def sleep(seconds):
    """예제에서는 실제로 기다리지 않고 기록만 한다. 실제 코드는 time.sleep을 쓴다."""
    waited.append(round(seconds, 2))


def backoff(attempt, base_delay=0.5, cap=8.0):
    """상한이 있는 지수 백오프 + full jitter: 0과 min(cap, base*2^attempt) 사이 무작위."""
    return rng.uniform(0, min(cap, base_delay * 2 ** attempt))


def get_with_retry(url, max_attempts=4, timeout=0.3):
    for attempt in range(max_attempts):
        last = attempt + 1 == max_attempts
        try:
            with urllib.request.urlopen(url, timeout=timeout) as response:
                print(f"  시도 {attempt + 1}: {response.status} 성공")
                return json.loads(response.read())
        except urllib.error.HTTPError as error:
            if error.code not in RETRYABLE:
                print(f"  시도 {attempt + 1}: {error.code} 재시도하지 않는 오류")
                raise
            reason, retry_after = str(error.code), error.headers.get("Retry-After")
        except (TimeoutError, socket.timeout, urllib.error.URLError):
            reason, retry_after = "시간 초과", None
        if last:
            print(f"  시도 {attempt + 1}: {reason}, 더 시도하지 않음")
            raise RuntimeError(f"{max_attempts}번 시도 후 포기")
        delay = float(retry_after) if retry_after and retry_after.isdigit() else backoff(attempt)
        print(f"  시도 {attempt + 1}: {reason}, {delay:.2f}초 뒤 재시도 ({'Retry-After' if retry_after else '백오프'})")
        sleep(delay)


print("GET /orders")
get_with_retry(f"{base}/orders")
print("GET /slow (시간 제한 0.3초)")
try:
    get_with_retry(f"{base}/slow", max_attempts=2)
except RuntimeError as error:
    print(" ", error)
print("기다린 시간(초):", waited)
server.shutdown()
