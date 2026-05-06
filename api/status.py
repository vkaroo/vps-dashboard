from http.server import BaseHTTPRequestHandler
import http.client
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        try:
            conn = http.client.HTTPConnection('129.226.213.48', timeout=5)
            conn.request('GET', '/api/status')
            res = conn.getresponse()
            data = res.read().decode()
            conn.close()
            self.wfile.write(data.encode())
        except Exception as e:
            self.wfile.write(json.dumps({'error': str(e)}).encode())
        return
