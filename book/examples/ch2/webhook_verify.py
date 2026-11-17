"""2.6 웹훅 서명 검증: 보낸 쪽이 진짜인지, 본문이 바뀌지 않았는지, 이미 처리한 이벤트인지."""
import hashlib
import hmac
import json

SECRET = b"whsec-example-only"  # 예제용. 실제 비밀값은 환경 변수에서 읽고 출력하지 않는다.
TOLERANCE_SECONDS = 300


def sign(secret, timestamp, raw_body):
    """보내는 쪽: '타임스탬프.본문'에 HMAC-SHA256을 계산한다."""
    message = f"{timestamp}.".encode() + raw_body
    return "sha256=" + hmac.new(secret, message, hashlib.sha256).hexdigest()


processed_event_ids = set()  # 실제로는 DB의 고유 제약으로 지킨다(3.2, 8.2절)


def receive(headers, raw_body, now):
    """받는 쪽: 파싱하기 전에 원시 바이트 그대로 검증한다."""
    try:
        timestamp = int(headers["X-Timestamp"])
        received = headers["X-Signature"]
    except (KeyError, ValueError):
        return 400, "서명 헤더 없음"
    if abs(now - timestamp) > TOLERANCE_SECONDS:
        return 400, "오래된 요청(재전송 공격 가능성)"
    expected = sign(SECRET, timestamp, raw_body)
    if not hmac.compare_digest(expected, received):  # ==를 쓰지 않는다
        return 401, "서명 불일치"
    event = json.loads(raw_body)
    if event["id"] in processed_event_ids:
        return 200, f"{event['id']} 이미 처리함(무시)"
    processed_event_ids.add(event["id"])
    return 200, f"{event['id']} 처리: {event['type']}"


now = 1_763_000_000
body = json.dumps({"id": "evt_1", "type": "ticket.created", "ticket": "T-7"}).encode()
good = {"X-Timestamp": str(now), "X-Signature": sign(SECRET, now, body)}

print("정상           :", receive(good, body, now))
print("같은 이벤트 재전송:", receive(good, body, now + 30))
tampered = body.replace(b"T-7", b"T-9")
print("본문 변조       :", receive(good, tampered, now))
print("다른 비밀값     :", receive({**good, "X-Signature": sign(b"wrong", now, body)}, body, now))
print("10분 지난 요청  :", receive(good, body, now + 600))
reparsed = json.dumps(json.loads(body), indent=2).encode()  # 프레임워크가 본문을 다시 직렬화한 경우
print("재직렬화된 본문 :", receive(good, reparsed, now))
