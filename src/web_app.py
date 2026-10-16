"""Local web interface for the deterministic Clara recommendation demo."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from src.agent import run_agent
from src.feedback import log_feedback


ROOT = Path(__file__).resolve().parent.parent
WEB_ROOT = ROOT / "web"
MAX_BODY = 8192
SAFE_HEADERS = {
    "Content-Security-Policy": "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "no-store",
}


class ClaraHandler(BaseHTTPRequestHandler):
    server_version = "ClaraLocal/1.0"

    def _send(self, status, payload, content_type="application/json; charset=utf-8"):
        body = payload if isinstance(payload, bytes) else payload.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        for name, value in SAFE_HEADERS.items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status, value):
        self._send(status, json.dumps(value, ensure_ascii=False), "application/json; charset=utf-8")

    def _read_json(self):
        raw_length = self.headers.get("Content-Length", "")
        try:
            length = int(raw_length)
        except (TypeError, ValueError):
            raise ValueError("A valid Content-Length is required.")
        if length < 1 or length > MAX_BODY:
            raise ValueError("Request body must be between 1 and 8192 bytes.")
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ValueError("Request must contain valid UTF-8 JSON.")

    def _local_request(self):
        try:
            host_header = urlparse("//" + self.headers.get("Host", ""))
            host = host_header.hostname
            host_port = host_header.port
            server_port = self.server.server_address[1]
        except ValueError:
            return False
        if host not in {"localhost", "127.0.0.1", "::1"}:
            return False
        if host_port is not None and host_port != server_port:
            return False
        origin = self.headers.get("Origin")
        if origin:
            parsed_origin = urlparse(origin)
            if parsed_origin.scheme != "http" or parsed_origin.hostname not in {"localhost", "127.0.0.1", "::1"}:
                return False
            if parsed_origin.username or parsed_origin.password or parsed_origin.path not in {"", "/"}:
                return False
            if parsed_origin.query or parsed_origin.fragment:
                return False
            try:
                origin_port = parsed_origin.port or 80
            except ValueError:
                return False
            if origin_port != server_port:
                return False
        return True

    def do_GET(self):
        if not self._local_request():
            return self._json(403, {"error": "Local access only."})
        path = urlparse(self.path).path
        if path == "/":
            return self._send(200, (WEB_ROOT / "index.html").read_bytes(), "text/html; charset=utf-8")
        if path in {"/app.js", "/styles.css"}:
            kind = "text/javascript; charset=utf-8" if path.endswith(".js") else "text/css; charset=utf-8"
            return self._send(200, (WEB_ROOT / path.lstrip("/")).read_bytes(), kind)
        return self._json(404, {"error": "Not found."})

    def do_POST(self):
        if not self._local_request():
            return self._json(403, {"error": "Local access only."})
        path = urlparse(self.path).path
        try:
            payload = self._read_json()
        except ValueError as error:
            return self._json(400, {"error": str(error)})
        if path == "/api/run":
            query = payload.get("query") if isinstance(payload, dict) else None
            if not isinstance(query, str) or not query.strip() or len(query) > 500:
                return self._json(400, {"error": "Enter a query of 1 to 500 characters."})
            return self._json(200, run_agent(query.strip()))
        if path == "/api/feedback":
            if not isinstance(payload, dict):
                return self._json(400, {"error": "Feedback details are required."})
            query, product_id = payload.get("query"), payload.get("product_id")
            feedback, reason = payload.get("feedback"), payload.get("reason", "")
            if not isinstance(query, str) or len(query) > 500 or not isinstance(product_id, str) or len(product_id) > 40:
                return self._json(400, {"error": "Feedback details are invalid."})
            if not isinstance(feedback, str) or feedback not in {"helpful", "unsafe"} or not isinstance(reason, str) or len(reason) > 500:
                return self._json(400, {"error": "Choose helpful or unsafe and keep the note under 500 characters."})
            log_feedback(query=query, product_id=product_id, feedback=feedback, reason=reason.strip() or None)
            return self._json(200, {"saved": True})
        return self._json(404, {"error": "Not found."})

    def log_message(self, format, *args):
        # Keep queries, product names, and feedback out of the local server log.
        return


def main(host="127.0.0.1", port=8765):
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit("Clara web UI must bind to loopback only.")
    server = ThreadingHTTPServer((host, port), ClaraHandler)
    print(f"Clara local review UI: http://{host}:{port}/ (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    main(args.host, args.port)
