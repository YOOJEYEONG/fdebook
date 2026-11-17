"""3.2 트랜잭션과 제약: 재고 예약은 '모두 되거나 하나도 안 되거나'여야 한다."""
import sqlite3

con = sqlite3.connect(":memory:")
con.executescript("""
CREATE TABLE stock (sku TEXT PRIMARY KEY, qty INTEGER NOT NULL CHECK (qty >= 0));
CREATE TABLE reservations (
  order_id TEXT NOT NULL, sku TEXT NOT NULL, qty INTEGER NOT NULL,
  PRIMARY KEY (order_id, sku)
);
INSERT INTO stock VALUES ('BOX-S', 5), ('TAPE', 1);
""")


def state():
    stock = dict(con.execute("SELECT sku, qty FROM stock ORDER BY sku"))
    count = con.execute("SELECT COUNT(*) FROM reservations").fetchone()[0]
    return f"재고 {stock}, 예약 {count}건"


def reserve_without_transaction(order_id, items):
    """나쁜 예: 줄마다 바로 커밋한다."""
    for sku, qty in items:
        con.execute("UPDATE stock SET qty = qty - ? WHERE sku = ?", (qty, sku))
        con.execute("INSERT INTO reservations VALUES (?, ?, ?)", (order_id, sku, qty))
        con.commit()


def reserve(order_id, items):
    """좋은 예: 한 트랜잭션. with 블록이 예외 없이 끝나면 커밋, 예외면 롤백."""
    with con:
        for sku, qty in items:
            con.execute("UPDATE stock SET qty = qty - ? WHERE sku = ?", (qty, sku))
            con.execute("INSERT INTO reservations VALUES (?, ?, ?)", (order_id, sku, qty))


order = [("BOX-S", 2), ("TAPE", 3)]  # TAPE는 1개뿐이라 두 번째 줄에서 CHECK 제약에 걸린다
print("시작          :", state())
try:
    reserve_without_transaction("A-1", order)
except sqlite3.IntegrityError as error:
    print("트랜잭션 없음 :", state(), "<- 실패했는데 BOX-S만 줄었다 /", error)

con.executescript("DELETE FROM reservations; UPDATE stock SET qty = 5 WHERE sku = 'BOX-S';")
try:
    reserve("A-1", order)
except sqlite3.IntegrityError as error:
    print("트랜잭션      :", state(), "<- 전부 되돌려졌다 /", error)

reserve("A-2", [("BOX-S", 2), ("TAPE", 1)])
print("정상 예약     :", state())
try:
    reserve("A-2", [("BOX-S", 1)])  # 같은 주문·품목을 두 번 예약하려 한다
except sqlite3.IntegrityError as error:
    print("중복 예약 시도:", state(), "/", error)
