"""5.2 재현과 가설 검증: '월요일 보고서에 일요일 밤 문의가 빠진다'를 최소 입력으로 재현하고 고친다."""
from collections import Counter
from datetime import datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))

# DB에는 UTC로 저장되어 있다(3.4절 원칙). 한국 시각 일요일 23:30 문의는 UTC로 일요일 14:30이다.
TICKETS = [
    {"id": 1, "created_at": "2026-11-15T14:30:00Z"},  # KST 11/15(일) 23:30
    {"id": 2, "created_at": "2026-11-15T15:10:00Z"},  # KST 11/16(월) 00:10
    {"id": 3, "created_at": "2026-11-16T01:00:00Z"},  # KST 11/16(월) 10:00
]


def parse(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def daily_counts_buggy(tickets):
    """현재 코드: 저장된 문자열의 날짜 부분(UTC 날짜)으로 묶는다."""
    return Counter(t["created_at"][:10] for t in tickets)


def daily_counts_fixed(tickets):
    """수정: 보고서의 기준 시간대(KST)로 바꾼 뒤 날짜를 자른다."""
    return Counter(parse(t["created_at"]).astimezone(KST).date().isoformat() for t in tickets)


print("1) 재현: 고객이 말한 기대값과 현재 결과")
expected = {"2026-11-15": 1, "2026-11-16": 2}
actual = dict(daily_counts_buggy(TICKETS))
print("   기대(KST):", expected)
print("   현재    :", actual, "<- 같지 않음, 재현 성공" if actual != expected else "")

print("2) 가설을 하나씩 확인한다")
# 각 가설에 대해 '가설이 맞다면 참이어야 하는 관찰'을 코드로 쓴다.
hypotheses = [
    ("문의 일부가 DB에 저장되지 않았다", lambda: len(TICKETS) < 3),
    ("보고서가 UTC 날짜로 묶는다", lambda: daily_counts_buggy(TICKETS)["2026-11-15"] == 2),
    ("KST로 묶으면 기대값과 같다", lambda: dict(daily_counts_fixed(TICKETS)) == expected),
]
for claim, observed in hypotheses:
    print(f"   {claim:<20} -> {'지지' if observed() else '기각'}")

print("3) 수정 후 확인과 경계 시각")
print("   수정    :", dict(daily_counts_fixed(TICKETS)))
for ts in ("2026-11-15T14:59:59Z", "2026-11-15T15:00:00Z"):
    print(f"   {ts} -> KST 날짜 {parse(ts).astimezone(KST).date()}")
