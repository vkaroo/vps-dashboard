from http.server import BaseHTTPRequestHandler
import http.client
import json
import os
import hmac
import hashlib
import urllib.parse

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")


def verify_init_data(init_data: str) -> dict:
    """Verify Telegram Mini App initData per official docs."""
    if not BOT_TOKEN:
        return {"ok": False, "error": "BOT_TOKEN not configured"}

    parsed = urllib.parse.parse_qs(init_data, keep_blank_values=True)
    received_hash = parsed.get("hash", [None])[0]
    if not received_hash:
        return {"ok": False, "error": "Missing hash"}

    # Build data-check-string: all fields except hash, sorted alphabetically
    data_check_pairs = []
    for k in sorted(parsed.keys()):
        if k == "hash":
            continue
        data_check_pairs.append(f"{k}={parsed[k][0]}")
    data_check_string = "\n".join(data_check_pairs)

    # secret_key = HMAC_SHA256(<bot_token>, "WebAppData")
    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()

    # hash = hex(HMAC_SHA256(data_check_string, secret_key))
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        return {"ok": False, "error": "Hash mismatch", "computed": computed_hash[:16], "received": received_hash[:16]}

    user_data = {}
    if "user" in parsed:
        try:
            user_data = json.loads(parsed["user"][0])
        except:
            pass

    return {"ok": True, "user": user_data}


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
            self._send_json(401, {"error": "Missing Telegram auth"})
            return

        result = verify_init_data(init_data)
        if not result["ok"]:
            self._send_json(401, {"error": result.get("error", "Unauthorized")})
            return

        try:
            conn = http.client.HTTPConnection("129.226.213.48", timeout=5)
            conn.request("GET", "/api/status")
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
