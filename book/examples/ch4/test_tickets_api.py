"""4.2 테스트: 순수 함수의 단위 테스트와, 실제 HTTP로 계약을 확인하는 통합 테스트.

보통은 `python3 -m unittest -v examples/ch4/test_tickets_api.py`로 실행한다. 이 파일을 직접 실행하면
책의 출력과 비교할 수 있도록 소요 시간을 빼고 결과만 출력한다."""
import json
import sys
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tickets_api import make_server, open_db, validate  # noqa: E402


class ValidateTest(unittest.TestCase):
    """단위 테스트: 네트워크도 DB도 없이 빠르게 경계값을 확인한다."""

    def test_accepts_minimal_valid_ticket(self):
        self.assertEqual(validate({"subject": "환불", "body": "언제 되나요"}), [])

    def test_reports_every_problem_at_once(self):
        fields = [e["field"] for e in validate({"subject": " ", "channel": "fax", "extra": 1})]
        self.assertEqual(sorted(fields), ["body", "channel", "extra", "subject"])

    def test_subject_length_boundary(self):
        self.assertEqual(validate({"subject": "가" * 120, "body": "x"}), [])
        self.assertEqual(validate({"subject": "가" * 121, "body": "x"})[0]["problem"], "최대 120자")

    def test_rejects_wrong_type(self):
        self.assertEqual(validate({"subject": 7, "body": "x"})[0]["field"], "subject")


class ApiContractTest(unittest.TestCase):
    """통합 테스트: 실제 서버를 띄워 상태 코드·헤더·본문 형식이 계약대로인지 확인한다."""

    def setUp(self):
        self.server = make_server(open_db())  # 테스트마다 새 DB: 서로 영향을 주지 않는다
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.base = f"http://127.0.0.1:{self.server.server_address[1]}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def request(self, method, path, payload=None):
        data = None if payload is None else json.dumps(payload).encode()
        req = urllib.request.Request(self.base + path, data, {"Content-Type": "application/json"}, method=method)
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.status, r.headers["Content-Type"], json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, e.headers["Content-Type"], json.loads(e.read())

    def test_create_then_read(self):
        status, _, created = self.request("POST", "/tickets", {"subject": "배송", "body": "늦어요"})
        self.assertEqual((status, created["channel"], created["status"]), (201, "email", "open"))
        status, _, read = self.request("GET", f"/tickets/{created['id']}")
        self.assertEqual((status, read), (200, created))

    def test_invalid_body_is_problem_json(self):
        status, content_type, body = self.request("POST", "/tickets", {"subject": ""})
        self.assertEqual(status, 422)
        self.assertTrue(content_type.startswith("application/problem+json"))
        self.assertEqual(body["status"], 422)

    def test_unknown_ticket_is_404(self):
        self.assertEqual(self.request("GET", "/tickets/999")[0], 404)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    names = [case.id() for group in suite for case in group]  # run()이 suite를 비우므로 먼저 적어 둔다
    result = unittest.TestResult()
    suite.run(result)
    failed = {test.id() for test, _ in result.failures + result.errors}
    for name in names:
        print(("FAIL " if name in failed else "ok   ") + name.split(".", 1)[1])
    for test, trace in result.failures + result.errors:
        print(trace)
    print(f"{result.testsRun}개 실행, 실패 {len(result.failures)}, 오류 {len(result.errors)}")
    sys.exit(0 if result.wasSuccessful() else 1)
