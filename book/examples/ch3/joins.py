"""3.1 관계 모델, 키, 조인: 고객과 문의 두 표를 잇는 세 가지 질문."""
import sqlite3

con = sqlite3.connect(":memory:")
con.execute("PRAGMA foreign_keys = ON")  # SQLite는 외래 키 검사를 연결마다 켜야 한다
con.executescript("""
CREATE TABLE customers (
  id   INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  plan TEXT NOT NULL
);
CREATE TABLE tickets (
  id          INTEGER PRIMARY KEY,
  customer_id INTEGER NOT NULL REFERENCES customers(id),
  category    TEXT NOT NULL,
  status      TEXT NOT NULL CHECK (status IN ('open', 'closed'))
);
INSERT INTO customers VALUES (1, '가나물류', 'enterprise'), (2, '다라상사', 'basic'), (3, '마바유통', 'basic');
INSERT INTO tickets VALUES
  (10, 1, '배송', 'open'), (11, 1, '환불', 'closed'), (12, 1, '배송', 'open'),
  (13, 2, '계정', 'open');
""")

print("1) 열린 문의와 고객 이름 (INNER JOIN: 짝이 있는 행만)")
for row in con.execute("""
    SELECT t.id, c.name, t.category
    FROM tickets AS t JOIN customers AS c ON c.id = t.customer_id
    WHERE t.status = ? ORDER BY t.id""", ("open",)):
    print("  ", row)

print("2) 고객별 열린 문의 수 (LEFT JOIN: 문의 없는 고객도 0으로)")
for row in con.execute("""
    SELECT c.name, COUNT(t.id) AS open_count
    FROM customers AS c
    LEFT JOIN tickets AS t ON t.customer_id = c.id AND t.status = 'open'
    GROUP BY c.id ORDER BY open_count DESC, c.name"""):
    print("  ", row)

print("3) 흔한 실수: 조건을 WHERE에 두면 LEFT JOIN이 INNER JOIN처럼 된다")
for row in con.execute("""
    SELECT c.name, COUNT(t.id)
    FROM customers AS c LEFT JOIN tickets AS t ON t.customer_id = c.id
    WHERE t.status = 'open'
    GROUP BY c.id ORDER BY c.name"""):
    print("  ", row)

print("4) 외래 키가 막는 잘못된 데이터")
try:
    con.execute("INSERT INTO tickets VALUES (14, 99, '배송', 'open')")
except sqlite3.IntegrityError as error:
    print("   IntegrityError:", error)

print("5) 사용자 입력은 자리표시자로")
user_input = "basic' OR '1'='1"
unsafe = f"SELECT COUNT(*) FROM customers WHERE plan = '{user_input}'"
print("   문자열 조립:", con.execute(unsafe).fetchone()[0], "명  <- 조건이 무력화됨")
print("   자리표시자 :", con.execute("SELECT COUNT(*) FROM customers WHERE plan = ?", (user_input,)).fetchone()[0], "명")
