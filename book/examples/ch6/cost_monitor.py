"""6.6 비용·지연·모니터링: 요청 로그의 토큰 수로 비용을 계산하고, 한도와 경보 규칙을 적용한다.

단가는 일부러 입력값으로 둔다. 모델 가격은 바뀌므로 공식 가격표의 현재 값을 넣는다(아래 값은 계산 예시용 가정)."""
import math

PRICE_PER_MILLION = {"input": 3.00, "output": 15.00, "cache_read": 0.30}  # 가정값, 단위: 달러 / 100만 토큰
DAILY_BUDGET = 0.10                                                       # 가정한 하루 예산(달러)
MAX_OUTPUT_TOKENS = 800                                                   # 요청당 출력 상한
PER_USER_DAILY_REQUESTS = 3                                               # 사용자당 하루 요청 한도

REQUESTS = [  # (사용자, 입력 토큰, 캐시에서 읽은 입력 토큰, 출력 토큰, 지연 ms)
    ("u1", 2400, 2000, 180, 1900), ("u2", 2600, 2000, 220, 2100), ("u1", 2300, 2000, 150, 1700),
    ("u3", 9800, 0, 790, 6400), ("u1", 2500, 2000, 210, 2000), ("u4", 2450, 2000, 160, 1800),
    ("u2", 2550, 2000, 240, 2300), ("u1", 2400, 2000, 170, 1900),
]


def cost(input_tokens, cached, output_tokens):
    uncached = input_tokens - cached
    return (uncached * PRICE_PER_MILLION["input"] + cached * PRICE_PER_MILLION["cache_read"]
            + output_tokens * PRICE_PER_MILLION["output"]) / 1_000_000


def percentile(values, p):
    ordered = sorted(values)
    return ordered[max(0, math.ceil(p / 100 * len(ordered)) - 1)]


spent, used, served, latencies, tokens = 0.0, {}, [], [], {"input": 0, "cached": 0}
for user, tokens_in, cached, tokens_out, ms in REQUESTS:
    used[user] = used.get(user, 0) + 1
    if used[user] > PER_USER_DAILY_REQUESTS:
        print(f"{user}: 하루 한도 {PER_USER_DAILY_REQUESTS}회 초과 -> 429로 거절(모델 호출 안 함)")
        continue
    c = cost(tokens_in, cached, min(tokens_out, MAX_OUTPUT_TOKENS))
    spent += c
    served.append(c)
    latencies.append(ms)
    tokens["input"] += tokens_in
    tokens["cached"] += cached
    flag = "  <- 캐시 없음, 긴 입력" if cached == 0 else ""
    print(f"{user}: 입력 {tokens_in}(캐시 {cached}) 출력 {tokens_out} -> ${c:.5f}{flag}")

print(f"처리 {len(served)}건, 합계 ${spent:.4f}, 건당 평균 ${spent / len(served):.5f}, 최대 ${max(served):.5f}")
print(f"지연 p50 {percentile(latencies, 50)}ms, p95 {percentile(latencies, 95)}ms")
print(f"처리한 입력 토큰 중 캐시에서 읽은 비율 {tokens['cached'] / tokens['input']:.0%}")
if spent > 0.8 * DAILY_BUDGET:
    print(f"경보: 하루 예산의 {spent / DAILY_BUDGET:.0%} 사용")
else:
    print(f"예산 사용 {spent / DAILY_BUDGET:.0%}: 정상")
