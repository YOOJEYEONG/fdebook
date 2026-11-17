"""8.3 평가와 운영 보고: 정답이 붙은 합성 문의로 분류기를 평가하고, 수용 기준으로 판정한다."""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from app import CATEGORIES, URGENT, classify  # noqa: E402
from data import make_inquiries  # noqa: E402

data = make_inquiries()
results = [(r, *classify(r["text"])) for r in data]

routes = Counter(route for _, _, route in results)
print("경로:", {k: routes[k] for k in ("rule", "model", "human")})

print("분류별 지표(사람 검토로 간 건은 예측 없음으로 계산):")
recalls = {}
for c in CATEGORIES:
    tp = sum(r["gold_category"] == c and p == c for r, p, _ in results)
    fp = sum(r["gold_category"] != c and p == c for r, p, _ in results)
    fn = sum(r["gold_category"] == c and p != c for r, p, _ in results)
    precision = f"{tp / (tp + fp):.2f}" if tp + fp else "정의 안 됨"
    recalls[c] = tp / (tp + fn) if tp + fn else 0.0
    print(f"  {c}: 정밀도 {precision}, 재현율 {recalls[c]:.2f} (TP {tp}, FP {fp}, FN {fn})")

wrong = [(r["event_id"], r["text"], r["gold_category"], p) for r, p, route in results
         if route != "human" and p != r["gold_category"]]
print(f"자동 배정 중 오배정: {len(wrong)}건")
for item in wrong:
    print("  ", item)

urgent_gold = [r for r in data if r["gold_urgent"]]
urgent_found = sum(bool(URGENT.search(r["text"])) for r in urgent_gold)
print(f"긴급 탐지: {urgent_found}/{len(urgent_gold)}")

auto = routes["rule"] + routes["model"]
CRITERIA = [
    ("자동 배정 비율 >= 70%", auto / len(data) >= 0.70, f"{auto / len(data):.0%}"),
    ("오배정 비율 <= 5%", len(wrong) / auto <= 0.05, f"{len(wrong) / auto:.1%}"),
    ("모든 분류 재현율 >= 0.7", min(recalls.values()) >= 0.7, f"최저 {min(recalls.values()):.2f}"),
    ("긴급 누락 0건", urgent_found == len(urgent_gold), f"누락 {len(urgent_gold) - urgent_found}건"),
]
print("수용 기준:")
for name, ok, value in CRITERIA:
    print(f"  {'통과' if ok else '미달'}  {name}: {value}")

# 위 평가셋은 규칙을 만들 때 본 템플릿에서 나왔다. 규칙을 보지 않고 따로 쓴 '새 표현' 문의로 다시 잰다.
HELD_OUT = [
    ("물건이 아직도 안 왔어요", "배송"), ("기사님이 전화를 안 받아요", "배송"),
    ("돈 언제 돌려주나요", "환불"), ("주문 취소하면 포인트도 돌아오나요", "환불"),
    ("아이디가 기억이 안 나요", "계정"), ("2단계 확인 코드가 안 와요", "계정"),
    ("영수증 다시 받을 수 있나요", "기타"), ("상품 재입고 언제 돼요", "기타"),
]
held = [(gold, *classify(text)) for text, gold in HELD_OUT]
correct = sum(gold == p for gold, p, _ in held)
to_human = sum(route == "human" for _, _, route in held)
print(f"새 표현 {len(held)}건: 정답 {correct}, 사람 검토 {to_human}, 오배정 {len(held) - correct - to_human}")
for (text, gold), (_, p, route) in zip(HELD_OUT, held):
    print(f"  {text} -> {p}/{route} (정답 {gold})")
