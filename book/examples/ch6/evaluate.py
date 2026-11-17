"""6.4 평가셋과 지표: 정답이 붙은 문의 20건으로 두 버전의 분류기를 비교한다.

v1, v2는 같은 문의에 두 버전의 프롬프트가 낸 예측을 기록해 둔 것이라고 가정한다."""
from collections import Counter

LABELS = ["배송", "환불", "계정", "기타"]
GOLD = ["배송", "배송", "배송", "배송", "배송", "배송", "환불", "환불", "환불", "환불",
        "환불", "계정", "계정", "계정", "계정", "기타", "기타", "기타", "배송", "환불"]
V1 = ["배송", "배송", "배송", "배송", "환불", "배송", "환불", "환불", "환불", "배송",
      "환불", "계정", "계정", "기타", "계정", "기타", "배송", "기타", "배송", "환불"]
V2 = ["배송", "배송", "배송", "배송", "배송", "배송", "환불", "환불", "환불", "환불",
      "환불", "계정", "기타", "기타", "기타", "기타", "기타", "기타", "배송", "환불"]


def report(name, predicted):
    pairs = Counter(zip(GOLD, predicted))
    print(f"== {name}: 정확도 {sum(g == p for g, p in zip(GOLD, predicted))}/{len(GOLD)}")
    print("   혼동 행렬(행=정답, 열=예측)")
    print(("   정답\\예측 " + "".join(f"{l} " for l in LABELS)).rstrip())  # 한글 한 글자는 고정폭 두 칸
    for g in LABELS:
        print(f"   {g}      " + "".join(f"{pairs[(g, p)]:>4} " for p in LABELS).rstrip())
    f1s = []
    for label in LABELS:
        tp = pairs[(label, label)]
        fp = sum(pairs[(g, label)] for g in LABELS if g != label)
        fn = sum(pairs[(label, p)] for p in LABELS if p != label)
        precision = f"{tp / (tp + fp):.2f}" if tp + fp else "정의 안 됨(예측 0건)"
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * tp / (2 * tp + fp + fn) if tp + fp + fn else 0.0
        f1s.append(f1)
        print(f"   {label}: 정밀도 {precision}, 재현율 {recall:.2f}, F1 {f1:.2f}")
    print(f"   매크로 F1 {sum(f1s) / len(f1s):.3f}")


report("v1", V1)
report("v2", V2)
print("== v2에서 새로 틀린 문의(회귀): 개선 평균 뒤에 숨은 것")
for i, (g, a, b) in enumerate(zip(GOLD, V1, V2)):
    if a == g and b != g:
        print(f"   #{i}: 정답 {g}, v1 {a}, v2 {b}")

print("== 불균형 데이터의 함정: 긴급 문의 탐지(20건 중 긴급 2건)")
urgent_gold = [1, 1] + [0] * 18
always_no = [0] * 20
accuracy = sum(g == p for g, p in zip(urgent_gold, always_no)) / 20
tp = sum(g == 1 and p == 1 for g, p in zip(urgent_gold, always_no))
print(f"   '항상 긴급 아님' 모델: 정확도 {accuracy:.0%}, 긴급 재현율 {tp}/{sum(urgent_gold)}, "
      f"정밀도 {'정의 안 됨(긴급 예측 0건)' if not any(always_no) else '-'}")
