"""5.3 성능·지연·비용: N+1 질의를 세어 보고, 평균이 숨기는 꼬리 지연을 백분위수로 본다."""
import math
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE tickets (id INTEGER PRIMARY KEY, customer_id INTEGER, subject TEXT);
CREATE INDEX tickets_customer ON tickets(customer_id);
""")
db.executemany("INSERT INTO customers VALUES (?, ?)", [(i, f"고객{i}") for i in range(1, 51)])
db.executemany("INSERT INTO tickets VALUES (?, ?, ?)", [(i, (i % 50) + 1, f"문의{i}") for i in range(1, 201)])

queries = []
db.set_trace_callback(queries.append)  # 실행된 SQL을 모두 기록한다


def page_n_plus_one():
    rows = db.execute("SELECT id, customer_id, subject FROM tickets ORDER BY id LIMIT 50").fetchall()
    return [(tid, db.execute("SELECT name FROM customers WHERE id = ?", (cid,)).fetchone()[0], subject)
            for tid, cid, subject in rows]  # 문의마다 고객을 한 번씩 더 묻는다


def page_join():
    return db.execute("""SELECT t.id, c.name, t.subject FROM tickets t
                         JOIN customers c ON c.id = t.customer_id ORDER BY t.id LIMIT 50""").fetchall()


queries.clear()
a = page_n_plus_one()
n_plus_one = len(queries)
queries.clear()
b = page_join()
print(f"N+1 방식: 질의 {n_plus_one}번 / JOIN 방식: 질의 {len(queries)}번 / 결과 같음: {a == b}")
db.set_trace_callback(None)


def percentile(values, p):
    """가장 가까운 순위(nearest-rank) 방식의 백분위수."""
    ordered = sorted(values)
    return ordered[max(0, math.ceil(p / 100 * len(ordered)) - 1)]


# 100건의 응답 시간(ms): 대부분 빠르지만 몇 건이 아주 느리다.
latencies = [40] * 90 + [60] * 5 + [900, 1200, 1500, 2500, 4000]
mean = sum(latencies) / len(latencies)
print(f"평균 {mean:.0f}ms, p50 {percentile(latencies, 50)}ms, p95 {percentile(latencies, 95)}ms, "
      f"p99 {percentile(latencies, 99)}ms, 최대 {max(latencies)}ms")
print("평균보다 느린 요청:", sum(v > mean for v in latencies), "건 / 100건")

# 비용 추정: 질의 1번에 0.002원이라는 단가는 설명을 위한 가정값이다. 실제 단가는 쓰는 서비스의 가격표로 바꾼다.
COST_PER_QUERY_WON = 0.002
pages_per_day = 1_000_000
for name, count in (("N+1", n_plus_one), ("JOIN", 1)):
    print(f"하루 {pages_per_day:,}쪽 조회 시 {name}: 질의 {count * pages_per_day:,}번, {count * pages_per_day * COST_PER_QUERY_WON:,.0f}원(가정 단가)")
