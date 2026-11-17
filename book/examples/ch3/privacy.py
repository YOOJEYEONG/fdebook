"""3.5 개인정보 최소화: 분석에 필요한 열만 남기고, 식별자는 키가 있는 해시로 가명화하고, 화면에는 가린다."""
import hashlib
import hmac
import os
import re

# 가명화 키는 데이터와 따로 보관한다. 예제는 환경 변수가 없을 때 고정값을 쓴다(실제로는 없으면 실패해야 한다).
PSEUDONYM_KEY = os.environ.get("PSEUDONYM_KEY", "example-only-key").encode()

tickets = [
    {"name": "김하나", "email": "hana.kim@example.com", "phone": "010-1234-5678",
     "address": "서울시 ○○구 ○○로 1", "category": "배송", "message": "010-1234-5678로 연락 주세요"},
    {"name": "이두리", "email": "duri.lee@example.com", "phone": "010-9876-5432",
     "address": "부산시 ○○구 ○○로 2", "category": "환불", "message": "환불은 언제 되나요?"},
    {"name": "김하나", "email": "hana.kim@example.com", "phone": "010-1234-5678",
     "address": "서울시 ○○구 ○○로 1", "category": "배송", "message": "아직 안 왔어요"},
]


def pseudonym(value):
    """같은 값은 같은 가명이 되어 집계·조인이 가능하다. 키를 모르면 원래 값을 역산하기 어렵다."""
    return "u_" + hmac.new(PSEUDONYM_KEY, value.encode(), hashlib.sha256).hexdigest()[:12]


def mask_email(email):
    local, domain = email.split("@")
    return local[0] + "***@" + domain


def mask_phone(phone):
    return phone[:4] + "****-" + phone[-4:]


def redact_free_text(text):
    """자유 입력 칸에 섞인 전화번호도 지운다."""
    return re.sub(r"01\d-?\d{3,4}-?\d{4}", "[전화번호]", text)


print("분석용 데이터(이름·주소·연락처 없음):")
for t in tickets:
    print(" ", {"user": pseudonym(t["email"]), "category": t["category"], "message": redact_free_text(t["message"])})

print("상담 화면용(가림):")
for t in tickets[:2]:
    print(" ", t["name"][0] + "*" * (len(t["name"]) - 1), mask_email(t["email"]), mask_phone(t["phone"]))

print("같은 사람의 문의 수:", len({pseudonym(t["email"]) for t in tickets}), "명이", len(tickets), "건")
# 공격자가 유출된 분석 데이터와 '흔한 이메일 후보 목록'을 가졌다고 하자.
candidates = ["kim@example.com", "hana.kim@example.com", "lee@example.com"]
leaked_plain = hashlib.sha256(b"hana.kim@example.com").hexdigest()  # 키 없는 해시로 가명화했다면
found = [c for c in candidates if hashlib.sha256(c.encode()).hexdigest() == leaked_plain]
print("키 없는 SHA-256 가명:", "후보 목록으로 되찾음 ->", found)
leaked_keyed = pseudonym("hana.kim@example.com")
found = [c for c in candidates if "u_" + hashlib.sha256(c.encode()).hexdigest()[:12] == leaked_keyed]
print("키 있는 HMAC 가명 :", "키 없이 되찾지 못함 ->", found)
