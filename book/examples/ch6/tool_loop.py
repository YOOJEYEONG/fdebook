"""6.2 도구 호출 루프: 모델이 tool_use를 내면 애플리케이션이 실행하고 tool_result를 돌려준다.

메시지 모양은 Anthropic Messages API의 tool_use / tool_result 블록을 따른다. 모델은 정해진 각본대로 답하는
가짜이며, 루프·검증·한도 같은 애플리케이션 쪽 책임을 실행해 보는 것이 목적이다."""
import json

TOOLS = [  # 모델에게 알려 주는 도구 정의: name, description, input_schema
    {"name": "get_order_status", "description": "주문 번호로 배송 상태를 조회한다. 읽기 전용.",
     "input_schema": {"type": "object", "required": ["order_id"],
                      "properties": {"order_id": {"type": "string", "pattern": "^A-[0-9]+$"}}}},
]
ORDERS = {"A-1": {"status": "배송 중", "eta": "2026-11-19"}}


def get_order_status(order_id):
    order = ORDERS.get(order_id)
    if order is None:
        raise LookupError(f"주문 {order_id} 없음")
    return order


HANDLERS = {"get_order_status": get_order_status}


def fake_model(messages):
    """각본: 첫 턴에는 없는 도구와 잘못된 주문 번호, 다음 턴에는 올바른 호출, 결과를 받으면 답한다."""
    turn = sum(1 for m in messages if m["role"] == "assistant")
    if turn == 0:
        return {"stop_reason": "tool_use", "content": [
            {"type": "tool_use", "id": "toolu_1", "name": "cancel_order", "input": {"order_id": "A-1"}},
            {"type": "tool_use", "id": "toolu_2", "name": "get_order_status", "input": {"order_id": "1"}}]}
    if turn == 1:
        return {"stop_reason": "tool_use", "content": [
            {"type": "tool_use", "id": "toolu_3", "name": "get_order_status", "input": {"order_id": "A-1"}}]}
    last = messages[-1]["content"][0]["content"]
    return {"stop_reason": "end_turn", "content": [
        {"type": "text", "text": f"주문 A-1은 현재 {json.loads(last)['status']}이며 {json.loads(last)['eta']} 도착 예정입니다."}]}


def run_tool(block):
    """이름이 허용 목록에 있는지, 입력이 스키마에 맞는지 확인한 뒤 실행한다. 실패도 결과로 돌려준다."""
    handler = HANDLERS.get(block["name"])
    if handler is None:
        return {"type": "tool_result", "tool_use_id": block["id"], "is_error": True,
                "content": f"알 수 없는 도구: {block['name']}"}
    order_id = block["input"].get("order_id", "")
    if not (order_id.startswith("A-") and order_id[2:].isdigit()):
        return {"type": "tool_result", "tool_use_id": block["id"], "is_error": True,
                "content": "order_id는 A-숫자 형식이어야 합니다"}
    try:
        return {"type": "tool_result", "tool_use_id": block["id"],
                "content": json.dumps(handler(order_id), ensure_ascii=False)}
    except LookupError as error:
        return {"type": "tool_result", "tool_use_id": block["id"], "is_error": True, "content": str(error)}


def agent(question, max_steps=5):
    messages = [{"role": "user", "content": question}]
    for step in range(1, max_steps + 1):
        reply = fake_model(messages)
        messages.append({"role": "assistant", "content": reply["content"]})
        if reply["stop_reason"] != "tool_use":
            return reply["content"][0]["text"], step
        results = [run_tool(b) for b in reply["content"] if b["type"] == "tool_use"]
        for b, r in zip([b for b in reply["content"] if b["type"] == "tool_use"], results):
            print(f"  단계 {step}: {b['name']}({b['input']}) -> {'오류: ' if r.get('is_error') else ''}{r['content']}")
        messages.append({"role": "user", "content": results})  # 모든 tool_use에 결과를 하나씩 돌려준다
    return "단계 한도를 넘어 중단했습니다. 담당자에게 넘깁니다.", max_steps


answer, steps = agent("A-1 주문 어디쯤 왔어요?")
print(f"답({steps}단계):", answer)
