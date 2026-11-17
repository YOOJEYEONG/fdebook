"""8.2 처음부터 끝까지: 합성 문의 60건을 웹훅으로 보내고, 중복·위조를 섞고, 고객사별로 조회한다."""
import json
import sys
import threading
import urllib.error
import urllib.request
from urllib.parse import urlencode
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from app import make_server, open_db, sign  # noqa: E402
from data import make_inquiries  # noqa: E402

NOW = 1_763_000_000
KEYS = {"webhook": b"demo-webhook-secret", "pseudonym": b"demo-pseudonym-key"}  # 예제용 값
TOKENS = {"token-gana": "가나물류", "token-dara": "다라상사"}

db = open_db()
server = make_server(db, KEYS, TOKENS, clock=lambda: NOW)
threading.Thread(target=server.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{server.server_address[1]}"


def send(event, secret=KEYS["webhook"], tamper=False):
    raw = json.dumps(event, ensure_ascii=False).encode()
    headers = {"Content-Type": "application/json", "X-Timestamp": str(NOW), "X-Signature": sign(secret, NOW, raw)}
    if tamper:
        raw = raw.replace("A-".encode(), "B-".encode())
    request = urllib.request.Request(f"{base}/webhooks/inquiry", raw, headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=5) as r:
            return r.status, json.loads(r.read())["detail"]
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())["detail"]


def get(path, token):
    request = urllib.request.Request(base + path, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(request, timeout=5) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


data = make_inquiries()
outcomes = Counter()
for row in data:
    event = {k: row[k] for k in ("event_id", "tenant", "email", "text")}
    status, detail = send(event)
    outcomes[(status, detail.split("/")[-1] if status == 200 else detail)] += 1
print("1) 수신 60건:", dict(sorted(outcomes.items())))

first = {k: data[0][k] for k in ("event_id", "tenant", "email", "text")}
print("2) 같은 이벤트 재전송:", send(first))
print("   본문 변조:", send({**first, "event_id": "evt_x1"}, tamper=True))
print("   다른 비밀값:", send({**first, "event_id": "evt_x2"}, secret=b"wrong"))

count = db.execute("SELECT COUNT(*), COUNT(DISTINCT customer) FROM inquiries").fetchone()
print(f"3) 저장: 문의 {count[0]}건, 서로 다른 고객 가명 {count[1]}개, 이메일 원문 저장 여부:",
      db.execute("SELECT COUNT(*) FROM inquiries WHERE customer LIKE '%@%'").fetchone()[0] > 0)

# 한국어 쿼리 값은 퍼센트 인코딩해야 한다. "/inquiries?category=계정"을 그대로 보내면 UnicodeEncodeError가 난다.
status, body = get("/inquiries?" + urlencode({"category": "계정"}), "token-dara")
print(f"4) 다라상사 계정 문의: {status}, {len(body['items'])}건, 첫 항목 {body['items'][0]}")
status, body = get("/inquiries", "token-gana")
print(f"   가나물류 전체: {len(body['items'])}건, 다른 고객사 항목 포함 여부:",
      any(i["event_id"] in {r["event_id"] for r in data if r["tenant"] != "가나물류"} for i in body["items"]))
print("   토큰 없음:", get("/inquiries", "nope")[0])
review = db.execute("SELECT COUNT(*) FROM inquiries WHERE route = 'human'").fetchone()[0]
print(f"5) 사람 검토 대기열: {review}건")
server.shutdown()
