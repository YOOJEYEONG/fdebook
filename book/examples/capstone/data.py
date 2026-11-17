"""8.1 합성 데이터: 실제 고객 정보 없이 문의 데이터를 만든다. 같은 씨앗이면 언제나 같은 데이터가 나온다."""
import random

TEMPLATES = {
    "배송": ["주문 {o} 언제 도착하나요?", "{o} 배송이 3일째 멈춰 있어요", "송장번호 조회가 안 돼요 {o}",
             "택배가 다른 주소로 갔어요 {o}", "배송 조회하면 계속 준비중이에요"],
    "환불": ["{o} 환불은 언제 되나요?", "반품 보냈는데 돈이 안 들어왔어요", "결제 취소했는데 카드에 그대로예요",
             "환불 계좌를 바꾸고 싶어요", "{o} 부분 환불 가능할까요", "택배로 반품 보냈는데 환불 언제 돼요"],
    "계정": ["비밀번호를 잊어버렸어요", "로그인이 계속 실패해요", "이메일 인증 메일이 안 와요",
             "휴대폰 번호를 바꿨는데 인증이 안 돼요", "회원 탈퇴는 어디서 하나요", "제 주문 내역이 하나도 안 보여요"],
    "기타": ["세금계산서 발행해 주세요", "매장 영업시간이 궁금해요", "제휴 문의드립니다",
             "앱이 자꾸 꺼져요", "상담원 연결 부탁드려요"],
}
URGENT_HINTS = ["급해요", "오늘 꼭", "사기 같아요"]


def make_inquiries(n=60, seed=42):
    rng = random.Random(seed)
    rows = []
    for i in range(n):
        category = list(TEMPLATES)[i % 4]
        text = rng.choice(TEMPLATES[category]).format(o=f"A-{1000 + i}")
        urgent = rng.random() < 0.15
        if urgent:
            text += " " + rng.choice(URGENT_HINTS)
        rows.append({
            "event_id": f"evt_{i:04d}",
            "tenant": "가나물류" if i % 3 else "다라상사",
            "email": f"user{i % 25}@example.com",  # 같은 사람이 여러 번 문의한다
            "text": text,
            "gold_category": category,
            "gold_urgent": urgent,
        })
    return rows


if __name__ == "__main__":
    data = make_inquiries()
    print(f"문의 {len(data)}건, 고객사 {sorted({r['tenant'] for r in data})}, 서로 다른 고객 {len({r['email'] for r in data})}명")
    for category in TEMPLATES:
        print(f"  {category}: {sum(r['gold_category'] == category for r in data)}건")
    print(f"  긴급: {sum(r['gold_urgent'] for r in data)}건")
    print("예시 3건:")
    for r in data[:3]:
        print(" ", {k: r[k] for k in ("event_id", "tenant", "text", "gold_category", "gold_urgent")})
