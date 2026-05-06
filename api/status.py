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

    parsed = urllib.parse.parse_qs(init_data)
    received_hash = parsed.get("hash", [None])[0]
    if not received_hash:
        return {"ok": False, "error": "Missing hash"}

    # Build data-check-string
    data_check_pairs = []
    for k, v in sorted(parsed.items()):
        if k != "hash":
            data_check_pairs.append(f"{k}={v[0]}")
    data_check_string = "\n".join(data_check_pairs)

    # HMAC-SHA256 with secret = SHA256(bot_token)
    secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        return {"ok": False, "error": "Invalid hash"}

    # Extract user info
    user_data = {}
    if "user" in parsed:
        try:
            user_data = json.loads(parsed["user"][0])
        except:
            pass

    return {"ok": True, "user": user_data}


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'X-Telegram-Init-Data')
        self.end_headers()

        # Get initData from header
        init_data = self.headers.get('X-Telegram-Init-Data', '')

        if not init_data:
            self.wfile.write(json.dumps({"error": "Missing Telegram auth"}).encode())
            return

        # Verify
        result = verify_init_data(init_data)
        if not result["ok"]:
            self.send_response(401)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": result["error"]}).encode())
            return

        # Proxy to VPS API
        try:
            conn = http.client.HTTPConnection('129.226.213.48', timeout=5)
            conn.request('GET', '/api/status')
            res = conn.getresponse()
            data = res.read().decode()
            conn.close()
            self.wfile.write(data.encode())
        except Exception as e:
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Telegram-Init-Data')
        self.end_headers()
