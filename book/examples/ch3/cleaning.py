"""3.3 정제: 결측, 중복, 형식 불일치를 규칙으로 고치고 고칠 수 없는 행은 이유와 함께 격리한다."""
import csv
import re
from collections import Counter
from datetime import date, datetime
from pathlib import Path

PLANS = {"basic", "enterprise"}
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def parse_date(text):
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):  # 모호한 05-03-2026(5월 3일? 3월 5일?)은 받지 않는다
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"알 수 없는 날짜 형식 {text!r}")


def clean(row):
    name = row["name"].strip()
    if not name:
        raise ValueError("이름 없음")
    email = row["email"].strip().lower() or None  # 빈 값은 '없음'으로 명시한다
    if email and not EMAIL.match(email):
        raise ValueError(f"이메일 형식 오류 {email!r}")
    digits = re.sub(r"\D", "", row["phone"])
    if not re.fullmatch(r"010\d{8}", digits):
        raise ValueError(f"전화번호 형식 오류 {row['phone']!r}")
    plan = row["plan"].strip().lower()
    if plan not in PLANS:
        raise ValueError(f"알 수 없는 요금제 {plan!r}")
    return {"customer_id": row["customer_id"].strip(), "name": name, "email": email,
            "phone": f"{digits[:3]}-{digits[3:7]}-{digits[7:]}",
            "signup_date": parse_date(row["signup_date"].strip()), "plan": plan}


source = Path(__file__).with_name("raw_contacts.csv")
clean_rows, rejected, duplicates = {}, [], 0
with source.open(encoding="utf-8", newline="") as f:
    for line_no, row in enumerate(csv.DictReader(f), start=2):  # 1행은 헤더
        try:
            record = clean(row)
        except ValueError as error:
            rejected.append((line_no, row["customer_id"], str(error)))
            continue
        if record["customer_id"] in clean_rows:
            duplicates += 1
            continue
        clean_rows[record["customer_id"]] = record

print("정제된 행:")
for r in clean_rows.values():
    print(f"  {r['customer_id']} {r['name']} {r['email']} {r['phone']} {r['signup_date']} {r['plan']}")
print("격리된 행:")
for line_no, cid, reason in rejected:
    print(f"  {line_no}행 {cid}: {reason}")
total = len(clean_rows) + len(rejected) + duplicates
print(f"요약: 입력 {total}행 = 정제 {len(clean_rows)} + 격리 {len(rejected)} + 중복 제거 {duplicates}")
print("이메일 없는 고객:", sum(r["email"] is None for r in clean_rows.values()))
print("요금제 분포:", dict(Counter(r["plan"] for r in clean_rows.values())))
assert all(isinstance(r["signup_date"], date) for r in clean_rows.values())
