"""6.1 LLM 출력을 프로그램이 믿을 수 있는 데이터로: 스키마 검증, 한 번의 재시도, 사람에게 넘기기.

실제 모델 대신 결정적인 가짜 모델을 쓴다. 모델이 실제로 내놓을 수 있는 세 가지 모양(정상, 설명이 섞인 JSON,
허용되지 않은 값)을 재현해 검증 코드가 각각을 어떻게 다루는지 보는 것이 목적이다."""
import json

SCHEMA = {  # 문의 분류 결과의 계약. API의 구조화 출력 기능에 넘기는 JSON Schema와 같은 내용이다.
    "type": "object",
    "required": ["category", "urgency", "summary"],
    "properties": {
        "category": {"enum": ["배송", "환불", "계정", "기타"]},
        "urgency": {"enum": ["low", "high"]},
        "summary": {"type": "string"},
    },
    "additionalProperties": False,
}

FAKE_REPLIES = {  # (stop_reason, 본문 텍스트)
    "T-1": [("end_turn", '{"category": "배송", "urgency": "high", "summary": "주문 A-1 배송 3일 지연"}')],
    "T-2": [("end_turn", '분류 결과입니다:\n```json\n{"category": "환불", "urgency": "low", "summary": "환불 일정 문의"}\n```'),
            ("end_turn", '{"category": "환불", "urgency": "low", "summary": "환불 일정 문의"}')],
    "T-3": [("end_turn", '{"category": "결제", "urgency": "urgent", "summary": "카드 이중 결제"}'),
            ("end_turn", '{"category": "기타", "urgency": "urgent", "summary": "카드 이중 결제"}')],
    "T-4": [("max_tokens", '{"category": "계정", "urgency": "High", "summary": "로그인이 계속 실패하고 비밀번'),
            ("end_turn", '{"category": "계정", "urgency": "High", "summary": "로그인 반복 실패"}')],
}


def fake_model(ticket_id, attempt):
    replies = FAKE_REPLIES[ticket_id]
    return replies[min(attempt, len(replies) - 1)]


def validate(stop_reason, text):
    """응답이 정상 종료됐는지 보고, JSON으로 읽고, 스키마를 확인한다. 실패 이유 목록을 돌려준다."""
    if stop_reason != "end_turn":  # max_tokens(잘림)나 refusal(거절)이면 스키마를 기대할 수 없다
        return None, [f"stop_reason={stop_reason}"]
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        return None, [f"JSON 아님: {error.msg}"]
    if not isinstance(data, dict):
        return None, ["객체가 아님"]
    problems = [f"필수 필드 없음: {k}" for k in SCHEMA["required"] if k not in data]
    problems += [f"허용되지 않은 필드: {k}" for k in data if k not in SCHEMA["properties"]]
    for key, rule in SCHEMA["properties"].items():
        if key in data and "enum" in rule and isinstance(data[key], str):
            # 대소문자만 다른 값은 허용 목록의 값으로 맞춘다(구조화 출력도 enum 대소문자는 보장하지 않는다).
            data[key] = next((v for v in rule["enum"] if v.casefold() == data[key].casefold()), data[key])
        if key in data and "enum" in rule and data[key] not in rule["enum"]:
            problems.append(f"{key}={data[key]!r}는 {rule['enum']} 중 하나여야 함")
        if key in data and rule.get("type") == "string" and not isinstance(data[key], str):
            problems.append(f"{key}는 문자열이어야 함")
    return (data if not problems else None), problems


def classify(ticket_id, max_attempts=2):
    for attempt in range(max_attempts):
        stop_reason, text = fake_model(ticket_id, attempt)
        data, problems = validate(stop_reason, text)
        if data:
            return {"result": data, "attempts": attempt + 1}
        print(f"  {ticket_id} 시도 {attempt + 1} 실패: {problems}")
        # 실제로는 실패 이유를 다음 요청에 덧붙여 다시 요청한다(또는 구조화 출력 기능으로 형식을 강제한다).
    return {"result": None, "route": "사람 검토 대기열", "attempts": max_attempts}


for ticket in ("T-1", "T-2", "T-3", "T-4"):
    print(ticket, "->", classify(ticket))
