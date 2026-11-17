"""5.1 로그·메트릭·트레이스: 같은 요청 ID로 세 신호를 잇는다. 시간은 예제 출력을 고정하려고 미리 정한 값을 쓴다."""
import json
from collections import Counter

# 요청 6건의 처리 결과(실제로는 서버가 측정한다). 지연 단위는 밀리초.
REQUESTS = [
    {"id": "req-01", "route": "GET /tickets/{id}", "status": 200, "db_ms": 12, "api_ms": 0},
    {"id": "req-02", "route": "POST /tickets", "status": 201, "db_ms": 18, "api_ms": 95},
    {"id": "req-03", "route": "GET /tickets/{id}", "status": 404, "db_ms": 9, "api_ms": 0},
    {"id": "req-04", "route": "POST /tickets", "status": 502, "db_ms": 17, "api_ms": 3000},
    {"id": "req-05", "route": "GET /tickets/{id}", "status": 200, "db_ms": 11, "api_ms": 0},
    {"id": "req-06", "route": "POST /tickets", "status": 201, "db_ms": 21, "api_ms": 110},
]

metrics = Counter()
latencies = {}
spans = []
error_logs = []

print("== 로그: 한 줄에 JSON 하나, 사람이 아니라 기계가 검색한다")
for r in REQUESTS:
    total = r["db_ms"] + r["api_ms"] + 3  # 3ms는 요청 파싱·응답 직렬화
    level = "error" if r["status"] >= 500 else "info"
    log = {"level": level, "request_id": r["id"], "route": r["route"], "status": r["status"], "duration_ms": total}
    if r["status"] == 502:
        log["error"] = "배송사 API 시간 초과(3000ms)"
    line = json.dumps(log, ensure_ascii=False)
    print(line)
    if level == "error":
        error_logs.append(line)

    # 메트릭: 개별 요청이 아니라 집계. 라벨은 경로·상태 분류처럼 값의 종류가 적은 것만.
    metrics[(r["route"], f"{r['status'] // 100}xx")] += 1
    latencies.setdefault(r["route"], []).append(total)

    # 트레이스: 요청 하나가 거친 단계(span)들. 부모-자식 관계와 소요 시간.
    spans.append((r["id"], [("handle " + r["route"], total, 0), ("db.query", r["db_ms"], 1)]
                  + ([("http POST shipping-api", r["api_ms"], 1)] if r["api_ms"] else [])))

print("== 메트릭: 경로·상태 분류별 요청 수")
for (route, klass), count in sorted(metrics.items()):
    print(f"  http_requests_total{{route=\"{route}\", class=\"{klass}\"}} {count}")
for route, values in sorted(latencies.items()):
    print(f"  {route} 지연(ms): 최소 {min(values)}, 최대 {max(values)}")
errors = sum(c for (route, klass), c in metrics.items() if klass == "5xx")
print(f"  5xx 오류율: {errors}/{len(REQUESTS)} = {errors / len(REQUESTS):.1%}")

print("== 트레이스: 오류 로그의 request_id로 해당 요청의 경로를 연다")
slow_id = json.loads(error_logs[0])["request_id"]  # 로그 검색: level == "error"
print("  request_id:", slow_id)
for request_id, tree in spans:
    if request_id == slow_id:
        for name, ms, depth in tree:
            print(f"  {'  ' * depth}{name:<28} {ms:>5}ms {'#' * (ms // 150)}".rstrip())
