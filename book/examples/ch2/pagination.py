"""2.3 페이지네이션: 읽는 도중 새 데이터가 들어올 때 오프셋 방식과 커서 방식의 차이."""

# 최신 글이 먼저 오는 목록. id가 클수록 최근이다.
tickets = [{"id": i, "subject": f"문의 {i}"} for i in range(1, 8)]


def newest_first():
    return sorted(tickets, key=lambda t: t["id"], reverse=True)


def page_by_offset(offset, limit):
    """GET /tickets?offset=…&limit=…"""
    return newest_first()[offset:offset + limit]


def page_by_cursor(cursor, limit):
    """GET /tickets?before=<cursor>&limit=… : 커서는 마지막으로 본 항목의 id."""
    rows = [t for t in newest_first() if cursor is None or t["id"] < cursor]
    page = rows[:limit]
    next_cursor = page[-1]["id"] if len(rows) > limit else None
    return page, next_cursor


def ids(rows):
    return [t["id"] for t in rows]


print("== 오프셋 방식 ==")
first = page_by_offset(0, 3)
print("1쪽:", ids(first))
tickets.append({"id": 8, "subject": "문의 8"})  # 1쪽을 읽은 직후 새 문의가 들어온다
second = page_by_offset(3, 3)
print("2쪽:", ids(second))
print("두 쪽에 모두 나온 항목:", sorted(set(ids(first)) & set(ids(second))), "/ 아무 쪽에도 안 나온 새 항목: [8]")

tickets.pop()  # 처음 상태로 되돌리고 커서 방식으로 다시 읽는다
print("== 커서 방식 ==")
page, cursor = page_by_cursor(None, 3)
print("1쪽:", ids(page), "next:", cursor)
tickets.append({"id": 8, "subject": "문의 8"})
seen = ids(page)
while cursor is not None:
    page, cursor = page_by_cursor(cursor, 3)
    print("다음 쪽:", ids(page), "next:", cursor)
    seen += ids(page)
print("중복:", len(seen) - len(set(seen)), "누락:", sorted(set(range(1, 8)) - set(seen)))
