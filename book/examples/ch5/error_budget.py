"""5.4 장애 대응: SLO와 오류 예산으로 '얼마나 나빴는가'를 숫자로 말하고, 타임라인에서 지표를 뽑는다."""
from datetime import datetime

SLO = 0.999                 # 30일 동안 성공 응답 비율 목표
WINDOW_MINUTES = 30 * 24 * 60
budget = (1 - SLO) * WINDOW_MINUTES
print(f"SLO {SLO:.1%} / 30일 -> 오류 예산 {budget:.1f}분")

# 장애 타임라인(사후 검토 문서의 핵심 자료). 시각은 KST.
timeline = [
    ("2026-11-12 14:02", "배포 v2.3 완료"),
    ("2026-11-12 14:09", "문의 생성 5xx 급증 시작(사용자 영향 시작)"),
    ("2026-11-12 14:21", "경보 발생, 담당자 호출"),
    ("2026-11-12 14:30", "원인 후보: v2.3의 DB 연결 수 설정"),
    ("2026-11-12 14:34", "v2.2로 롤백 결정"),
    ("2026-11-12 14:41", "롤백 완료, 5xx 정상화(사용자 영향 종료)"),
]
t = {event: datetime.strptime(ts, "%Y-%m-%d %H:%M") for ts, event in timeline}
start = t["문의 생성 5xx 급증 시작(사용자 영향 시작)"]
detected = t["경보 발생, 담당자 호출"]
recovered = t["롤백 완료, 5xx 정상화(사용자 영향 종료)"]
minutes = lambda a, b: int((b - a).total_seconds() // 60)
print(f"탐지까지 {minutes(start, detected)}분, 탐지 후 복구까지 {minutes(detected, recovered)}분, "
      f"영향 {minutes(start, recovered)}분")

# 영향 동안 요청의 40%가 실패했다면, 완전 장애로 환산한 시간은 영향 시간 × 실패 비율.
failure_ratio = 0.40
spent = minutes(start, recovered) * failure_ratio
print(f"소모한 오류 예산 {spent:.1f}분 = 예산의 {spent / budget:.0%}")
print("남은 예산", f"{budget - spent:.1f}분:", "새 기능 배포를 늦추고 안정화 작업 우선" if spent / budget > 0.25 else "계획대로")
