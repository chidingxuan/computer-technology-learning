"""第02课构建材料：只使用Python标准库的健康检查服务。"""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class StatusHandler(BaseHTTPRequestHandler):
    """处理健康检查请求。"""

    def do_GET(self) -> None:
        if self.path != "/health":
            self.send_error(404)
            return

        body = json.dumps({"status": "ok"}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        print(f"request: {format % args}")


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", 8000), StatusHandler)
    print("status service listening on 0.0.0.0:8000", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
