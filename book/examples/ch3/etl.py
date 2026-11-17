"""3.4 증분 적재와 품질 검사: 워터마크 이후 바뀐 행만 가져와 UPSERT하고, 적재 전에 검사한다."""
import sqlite3

# 원천 시스템(고객사 CRM)의 변경 기록이라고 가정한다. updated_at은 ISO 8601 UTC 문자열.
source_batches = [
    [  # 첫 번째 실행 때 원천에 있던 행
        {"id": 1, "status": "open", "updated_at": "2026-11-01T09:00:00Z"},
        {"id": 2, "status": "open", "updated_at": "2026-11-01T09:05:00Z"},
    ],
    [  # 두 번째 실행: 1번이 닫히고 3번이 새로 생겼다. 2번은 그대로다.
        {"id": 1, "status": "closed", "updated_at": "2026-11-01T10:00:00Z"},
        {"id": 2, "status": "open", "updated_at": "2026-11-01T09:05:00Z"},
        {"id": 3, "status": "open", "updated_at": "2026-11-01T10:02:00Z"},
    ],
    [  # 세 번째 실행: 잘못된 상태값과 id 없는 행이 섞여 들어왔다
        {"id": 4, "status": "opne", "updated_at": "2026-11-01T11:00:00Z"},
        {"id": None, "status": "open", "updated_at": "2026-11-01T11:01:00Z"},
    ],
]

dw = sqlite3.connect(":memory:")
dw.executescript("""
CREATE TABLE tickets (id INTEGER PRIMARY KEY, status TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE etl_state (name TEXT PRIMARY KEY, watermark TEXT NOT NULL);
INSERT INTO etl_state VALUES ('tickets', '1970-01-01T00:00:00Z');
""")


def extract(batch, watermark):
    """원천에 'updated_at > watermark'를 묻는 것과 같다."""
    return [r for r in batch if r["updated_at"] > watermark]


def check(rows):
    problems = []
    ids = [r["id"] for r in rows]
    if any(i is None for i in ids):
        problems.append("id가 비어 있는 행")
    if len(ids) != len(set(ids)):
        problems.append("배치 안에 중복 id")
    bad = sorted({r["status"] for r in rows} - {"open", "closed"})
    if bad:
        problems.append(f"허용되지 않은 status {bad}")
    return problems


def run(batch_no):
    (watermark,) = dw.execute("SELECT watermark FROM etl_state WHERE name = 'tickets'").fetchone()
    rows = extract(source_batches[batch_no], watermark)
    problems = check(rows)
    if problems:
        print(f"실행 {batch_no + 1}: 추출 {len(rows)}행, 적재 중단 -> {problems}")
        return
    with dw:  # 적재와 워터마크 갱신을 한 트랜잭션으로
        dw.executemany("""
            INSERT INTO tickets (id, status, updated_at) VALUES (:id, :status, :updated_at)
            ON CONFLICT(id) DO UPDATE SET status = excluded.status, updated_at = excluded.updated_at
            WHERE excluded.updated_at > tickets.updated_at""", rows)
        if rows:
            dw.execute("UPDATE etl_state SET watermark = ? WHERE name = 'tickets'",
                       (max(r["updated_at"] for r in rows),))
    table = dw.execute("SELECT id, status FROM tickets ORDER BY id").fetchall()
    (new_watermark,) = dw.execute("SELECT watermark FROM etl_state").fetchone()
    print(f"실행 {batch_no + 1}: 추출 {len(rows)}행, 적재 후 {table}, 워터마크 {new_watermark}")


for n in range(3):
    run(n)
print("워터마크를 되돌려 2번째 배치를 다시 적재해도 결과가 같다(멱등):")
with dw:
    dw.execute("UPDATE etl_state SET watermark = '2026-11-01T09:05:00Z'")
run(1)
