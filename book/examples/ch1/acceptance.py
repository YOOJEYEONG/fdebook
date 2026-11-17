"""1.3 성공 지표와 수용 기준: 고객과 합의한 기준을 실행 가능한 검사로 바꾸고 파일럿 결과에 적용한다."""

# 고객과 합의한 수용 기준(문서에 적은 것과 같은 내용). 숫자는 이 사례의 합의값이다.
CRITERIA = [
    ("자동 배정 비율", "auto_rate", ">=", 0.60, "사람 손을 거치지 않고 팀에 배정된 문의 비율"),
    ("오배정 비율", "misroute_rate", "<=", 0.05, "자동 배정 중 다른 팀으로 다시 넘긴 비율"),
    ("첫 응답 p90(분)", "first_reply_p90", "<=", 30, "문의 접수부터 첫 응답까지, 영업시간 기준"),
    ("긴급 문의 누락", "urgent_missed", "==", 0, "긴급인데 일반 대기열로 간 건수"),
]

# 파일럿 2주 결과(운영 로그에서 집계했다고 가정).
pilot = {"total": 1200, "auto_routed": 804, "misrouted": 31, "first_reply_minutes_p90": 26, "urgent_missed": 1}
baseline = {"auto_rate": 0.0, "misroute_rate": None, "first_reply_p90": 95, "urgent_missed": 3}

measured = {
    "auto_rate": pilot["auto_routed"] / pilot["total"],
    "misroute_rate": pilot["misrouted"] / pilot["auto_routed"],
    "first_reply_p90": pilot["first_reply_minutes_p90"],
    "urgent_missed": pilot["urgent_missed"],
}
OPS = {">=": lambda a, b: a >= b, "<=": lambda a, b: a <= b, "==": lambda a, b: a == b}


def show(value):
    return f"{value:.1%}" if isinstance(value, float) else str(value)


passed = 0
for name, key, op, target, meaning in CRITERIA:
    ok = OPS[op](measured[key], target)
    passed += ok
    before = baseline[key]
    print(f"{'통과' if ok else '미달'}  {name}: {show(measured[key])} (기준 {op} {show(target)}, 도입 전 {show(before) if before is not None else '측정 없음'})")
print(f"수용 기준 {passed}/{len(CRITERIA)} 충족")
if passed < len(CRITERIA):
    print("판정: 운영 전환 보류. 미달 항목의 원인과 대책을 고객과 검토한다.")
