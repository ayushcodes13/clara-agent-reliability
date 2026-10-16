import json
import threading
import unittest
from http.client import HTTPConnection
from unittest.mock import patch
from http.server import ThreadingHTTPServer

from src.web_app import ClaraHandler


class ClaraWebAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), ClaraHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.port = cls.server.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def request(self, method, path, payload=None, headers=None):
        connection = HTTPConnection("127.0.0.1", self.port)
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        extra_headers = headers or {}
        if body is not None:
            extra_headers.setdefault("Content-Type", "application/json")
        connection.request(method, path, body=body, headers=extra_headers)
        response = connection.getresponse()
        result = response.status, response.getheaders(), response.read()
        connection.close()
        return result

    def test_workspace_returns_local_security_headers(self):
        status, headers, body = self.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn(b"Review a query", body)
        response_headers = dict(headers)
        self.assertIn("frame-ancestors 'none'", response_headers["Content-Security-Policy"])
        self.assertEqual(response_headers["Cache-Control"], "no-store")

    def test_query_api_returns_real_doctor_review_hold(self):
        status, _, body = self.request("POST", "/api/run", {"query": "I am pregnant and facing hair fall"})
        result = json.loads(body)
        self.assertEqual(status, 200)
        self.assertEqual(result["route"]["route"], "doctor_review")
        self.assertTrue(result["user_response"][0]["doctor_review"]["requires_doctor_review"])
        self.assertIn("Query contains high-risk medical context", result["trace"]["route"]["reason"])

    def test_query_validation_and_nonlocal_host_are_rejected(self):
        status, _, _ = self.request("POST", "/api/run", {"query": "   "})
        self.assertEqual(status, 400)
        status, _, _ = self.request("POST", "/api/run", {"query": "safe sunscreen"}, {"Host": "example.com"})
        self.assertEqual(status, 403)

    def test_origin_must_match_the_local_server_port(self):
        status, _, _ = self.request(
            "POST", "/api/run", {"query": "safe sunscreen"},
            {"Origin": f"http://localhost:{self.port + 1}"},
        )
        self.assertEqual(status, 403)
        status, _, _ = self.request(
            "POST", "/api/run", {"query": "safe sunscreen"},
            {"Origin": f"http://localhost:{self.port}"},
        )
        self.assertEqual(status, 200)

    def test_host_with_a_different_port_is_rejected(self):
        status, _, _ = self.request(
            "POST", "/api/run", {"query": "safe sunscreen"},
            {"Host": f"localhost:{self.port + 1}"},
        )
        self.assertEqual(status, 403)
        status, _, _ = self.request(
            "POST", "/api/run", {"query": "safe sunscreen"},
            {"Origin": "http://localhost.evil:8765"},
        )
        self.assertEqual(status, 403)

    @patch("src.web_app.log_feedback")
    def test_feedback_is_explicit_and_written_via_local_logger(self, log_feedback):
        status, _, body = self.request("POST", "/api/feedback", {
            "query": "I need sunscreen for daily use", "product_id": "prod_003",
            "feedback": "helpful", "reason": "Clear evidence",
        })
        self.assertEqual(status, 200)
        self.assertTrue(json.loads(body)["saved"])
        log_feedback.assert_called_once_with(
            query="I need sunscreen for daily use", product_id="prod_003",
            feedback="helpful", reason="Clear evidence",
        )

    def test_feedback_type_validation_does_not_crash(self):
        status, _, _ = self.request("POST", "/api/feedback", {
            "query": "query", "product_id": "prod_003", "feedback": [], "reason": "",
        })
        self.assertEqual(status, 400)


if __name__ == "__main__":
    unittest.main()
