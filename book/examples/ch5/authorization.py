"""5.5 객체 수준 권한 검사(OWASP API1:2023): 로그인했다고 모든 ID를 볼 수 있으면 안 된다."""

TICKETS = {
    101: {"tenant": "가나물류", "subject": "배송 지연", "owner": "kim"},
    102: {"tenant": "다라상사", "subject": "계약 해지 문의", "owner": "park"},
}
USERS = {
    "kim": {"tenant": "가나물류", "role": "agent"},
    "lee": {"tenant": "가나물류", "role": "viewer"},
    "park": {"tenant": "다라상사", "role": "agent"},
}


def get_ticket_vulnerable(user, ticket_id):
    """인증만 확인하고, 요청한 ID가 누구의 것인지 확인하지 않는다."""
    if user not in USERS:
        return 401, None
    ticket = TICKETS.get(ticket_id)
    return (200, ticket["subject"]) if ticket else (404, None)


def get_ticket(user, ticket_id):
    """객체마다 '이 사용자가 이 객체에 접근할 수 있는가'를 서버에서 확인한다."""
    if user not in USERS:
        return 401, None
    ticket = TICKETS.get(ticket_id)
    if ticket is None or ticket["tenant"] != USERS[user]["tenant"]:
        return 404, None  # 다른 회사의 문의는 존재 여부도 알리지 않는다
    return 200, ticket["subject"]


def close_ticket(user, ticket_id):
    """기능 수준 권한도 확인한다: 같은 회사여도 viewer는 닫을 수 없다(API5:2023)."""
    status, _ = get_ticket(user, ticket_id)
    if status != 200:
        return status
    return 204 if USERS[user]["role"] == "agent" else 403


print("취약한 코드  kim -> 102:", get_ticket_vulnerable("kim", 102), "<- 다른 회사의 문의가 보인다")
print("고친 코드    kim -> 102:", get_ticket("kim", 102))
print("고친 코드    kim -> 101:", get_ticket("kim", 101))
print("고친 코드    lee -> 101:", get_ticket("lee", 101))
print("닫기         lee -> 101:", close_ticket("lee", 101))
print("닫기         kim -> 101:", close_ticket("kim", 101))
print("닫기         park -> 101:", close_ticket("park", 101))

# 권한 규칙 표를 테스트로 고정한다: (사용자, 문의, 기대 상태)
cases = [("kim", 101, 200), ("kim", 102, 404), ("park", 102, 200), ("park", 101, 404), ("nobody", 101, 401)]
failures = [c for c in cases if get_ticket(c[0], c[1])[0] != c[2]]
print(f"권한 표 {len(cases)}건 확인, 실패 {len(failures)}건")
