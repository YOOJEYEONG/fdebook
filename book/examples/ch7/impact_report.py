"""7.3 효과와 한계 보고: 도입 전후 지표를 같은 정의로 비교하고, 숫자가 말하지 못하는 것을 함께 적는다."""

# 같은 정의로 잰 4주씩의 운영 지표(도입 전 4주, 도입 후 4주). 숫자는 이 사례의 가정값이다.
before = {"weeks": 4, "tickets": 11800, "first_reply_p90_min": 95, "misroute": 0.081, "urgent_missed": 3}
after = {"weeks": 4, "tickets": 13900, "first_reply_p90_min": 31, "misroute": 0.042, "urgent_missed": 0}

rows = [
    ("문의 수", "tickets", "{:,}건"),
    ("첫 응답 p90", "first_reply_p90_min", "{}분"),
    ("오배정 비율", "misroute", "{:.1%}"),
    ("긴급 문의 누락", "urgent_missed", "{}건"),
]
print("| 지표 | 도입 전 | 도입 후 | 변화 |")
print("|---|---|---|---|")
for name, key, fmt in rows:
    a, b = before[key], after[key]
    change = f"{(b - a) / a:+.0%}" if a else "-"
    print(f"| {name} | {fmt.format(a)} | {fmt.format(b)} | {change} |")

print()
print("한계와 해석 주의:")
growth = after["tickets"] / before["tickets"] - 1
print(f"- 같은 기간 문의 수가 {growth:.0%} 늘었다. 부하가 늘었는데도 응답이 빨라졌지만, 문의 유형 구성이 달라졌을 수 있다.")
print("- 도입 후 4주에 연휴가 없었고 도입 전 4주에는 연휴가 있었다. 계절 효과를 분리하지 못했다.")
print("- 긴급 누락 3건 -> 0건은 건수가 작아 우연일 수 있다. 다음 분기까지 계속 관찰한다.")
print("- 상담원 만족도는 측정하지 않았다(설문 미실시). 효과로 주장하지 않는다.")
