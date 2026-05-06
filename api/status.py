from http.server import BaseHTTPRequestHandler
import http.client
import json
import os
import hmac
import hashlib
import urllib.parse

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")


def verify_init_data(init_data: str) -> dict:
    """Verify Telegram Mini App initData using HMAC-SHA256."""
    if not BOT_TOKEN:
        return {"ok": False, "error": "BOT_TOKEN not configured"}

    # Parse WITHOUT decoding — keep raw %7B%22... values
    parsed = urllib.parse.parse_qs(init_data, keep_blank_values=True)
    received_hash = parsed.get("hash", [None])[0]
    if not received_hash:
        return {"ok": False, "error": "Missing hash", "keys": list(parsed.keys())}

    # Build data-check-string using RAW (encoded) values from the original string
    # Telegram computes hash on the raw query string values, not decoded
    raw_pairs = []
    for part in init_data.split("&"):
        if part.startswith("hash="):
            continue
        raw_pairs.append(part)  # keep as-is: "user=%7B%22id%22..."
    raw_pairs.sort()
    data_check_string = "\n".join(raw_pairs)

    # HMAC-SHA256 with secret = SHA256(bot_token)
    secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        return {
            "ok": False,
            "error": "Hash mismatch",
            "computed": computed_hash[:16],
            "received": received_hash[:16],
            "pairs_count": len(raw_pairs),
        }

    # Extract user info
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
            self._send_json(
                401,
                {
                    "error": result["error"],
                    "debug": {k: v for k, v in result.items() if k != "ok"},
                },
            )
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
