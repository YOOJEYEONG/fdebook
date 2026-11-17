"""4.4 배포와 롤백: 새 버전을 일부 트래픽에만 보내고(카나리), 지표가 나빠지면 자동으로 되돌린다."""
import random

STEPS = [5, 25, 50, 100]          # 새 버전으로 보내는 트래픽 비율(%)
MAX_ERROR_RATE = 0.02             # 새 버전의 오류율이 이보다 높으면 롤백
MAX_ERROR_RATE_INCREASE = 0.01    # 기존 버전보다 이만큼 이상 나빠도 롤백


def observe(version, requests, rng):
    """한 단계 동안의 요청 결과를 흉내 낸다. 실제로는 모니터링 시스템(5.1절)에서 읽는다."""
    error_rate = {"v1": 0.005, "v2-good": 0.006, "v2-bad": 0.04}[version]
    errors = sum(rng.random() < error_rate for _ in range(requests))
    return errors / requests


def rollout(new_version, seed):
    rng = random.Random(seed)
    print(f"== {new_version} 배포 시작 (현재 v1)")
    for percent in STEPS:
        new_requests = 50 * percent
        old_rate = observe("v1", 5000, rng)  # 기존 버전의 같은 시간대 기준 오류율
        new_rate = observe(new_version, new_requests, rng)
        verdict = "진행"
        if new_rate > MAX_ERROR_RATE or new_rate - old_rate > MAX_ERROR_RATE_INCREASE:
            verdict = "롤백"
        print(f"  {percent:>3}% -> 새 버전 오류율 {new_rate:.3%}, 기존 {old_rate:.3%}: {verdict}")
        if verdict == "롤백":
            print(f"  트래픽 100%를 v1로 되돌리고 {new_version} 배포를 중단함")
            return "v1"
    print(f"  {new_version}: 트래픽 100% 전환 완료")
    return new_version


print("운영 버전:", rollout("v2-good", seed=1))
print("운영 버전:", rollout("v2-bad", seed=1))
