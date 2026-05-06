from http.server import BaseHTTPRequestHandler
import http.client
import json
import os
import hmac
import hashlib
import urllib.parse

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")


def verify_init_data(init_data: str) -> dict:
    if not BOT_TOKEN:
        return {"ok": False, "error": "BOT_TOKEN not configured"}

    parsed = urllib.parse.parse_qs(init_data, keep_blank_values=True)
    received_hash = parsed.get("hash", [None])[0]
    if not received_hash:
        return {"ok": False, "error": "Missing hash"}

    pairs = [f"{k}={parsed[k][0]}" for k in sorted(parsed.keys()) if k != "hash"]
    data_check_string = "\n".join(pairs)

    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    computed = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed, received_hash):
        return {"ok": False, "error": "Unauthorized"}

    return {"ok": True}


class handler(BaseHTTPRequestHandler):
    def _send_json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "X-Telegram-Init-Data")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        init_data = self.headers.get("X-Telegram-Init-Data", "")
        if not init_data:
            self._send_json(401, {"error": "Missing auth"})
            return

        result = verify_init_data(init_data)
        if not result["ok"]:
            self._send_json(401, {"error": "Unauthorized"})
            return

        # Get cmd from query string
        parsed_url = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed_url.query)
        cmd = params.get("cmd", [None])[0]

        if not cmd:
            self._send_json(400, {"error": "Missing cmd parameter"})
            return

        try:
            conn = http.client.HTTPConnection("129.226.213.48", 3456, timeout=30)
            encoded_cmd = urllib.parse.quote(cmd)
            conn.request("GET", f"/exec?cmd={encoded_cmd}")
            res = conn.getresponse()
            data = res.read().decode()
            conn.close()
            self._send_json(200, json.loads(data))
        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "X-Telegram-Init-Data")
        self.end_headers()
