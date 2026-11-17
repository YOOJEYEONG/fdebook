"""6.3 검색 기반 생성(RAG)의 검색 부분: 질문과 비슷한 문서를 찾아 근거로 붙이고, 없으면 모른다고 한다.

신경망 임베딩 대신 글자 2-gram 빈도 벡터와 코사인 유사도를 쓴다. 외부 모델 없이 '벡터로 바꾸고 가까운 것을
찾는다'는 구조를 실행하기 위해서다. 실제 시스템에서는 vectorize()를 임베딩 모델 호출로 바꾼다."""
import math
from collections import Counter

DOCS = {
    "faq-01": "배송은 결제 완료 후 영업일 기준 2~3일 걸립니다. 도서 산간 지역은 하루 더 걸릴 수 있습니다.",
    "faq-02": "환불은 반품 상품이 창고에 도착한 뒤 영업일 기준 3일 안에 결제 수단으로 돌려드립니다.",
    "faq-03": "비밀번호를 잊으셨다면 로그인 화면의 비밀번호 재설정에서 이메일 인증 후 바꿀 수 있습니다.",
    "faq-04": "주문 취소는 상품이 출고되기 전까지 주문 내역에서 직접 할 수 있습니다.",
    "faq-05": "세금계산서는 사업자 회원만 발행할 수 있으며 결제 후 마이페이지에서 신청합니다.",
}


def vectorize(text):
    chars = [c for c in text if not c.isspace()]
    return Counter(a + b for a, b in zip(chars, chars[1:]))


def cosine(a, b):
    dot = sum(a[k] * b[k] for k in a.keys() & b.keys())
    norm = math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values()))
    return dot / norm if norm else 0.0


INDEX = {doc_id: vectorize(text) for doc_id, text in DOCS.items()}  # 문서는 미리 한 번 벡터로 바꿔 둔다


def search(question, k=2, threshold=0.08):  # 임계값은 평가셋(6.4절)으로 정한다
    q = vectorize(question)
    scored = sorted(((cosine(q, v), doc_id) for doc_id, v in INDEX.items()), reverse=True)[:k]
    return [(doc_id, round(score, 3)) for score, doc_id in scored if score >= threshold]


def build_prompt(question, hits):
    if not hits:
        return None
    sources = "\n".join(f'<doc id="{doc_id}">{DOCS[doc_id]}</doc>' for doc_id, _ in hits)
    return (f"아래 문서만 근거로 답하고, 문장마다 근거 문서 id를 [faq-00] 형식으로 붙이세요. "
            f"문서에 답이 없으면 '확인할 수 없습니다'라고 답하세요.\n{sources}\n질문: {question}")


for question in ["환불은 언제 들어와요?", "주문 취소 가능한가요?", "매장 영업시간이 어떻게 되나요?",
                 "돈은 언제 돌려받나요?"]:
    hits = search(question)
    best = max((round(cosine(vectorize(question), v), 3), d) for d, v in INDEX.items())
    print(f"Q: {question}")
    print(f"   검색 결과: {hits if hits else f'임계값 이상 문서 없음(최고 {best}) -> 상담원 연결'}")
prompt = build_prompt("환불은 언제 들어와요?", search("환불은 언제 들어와요?"))
print("== 모델에 보낼 프롬프트 ==")
print(prompt)
