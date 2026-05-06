import http.client
import json
import ssl

def handler(request, response):
    """Vercel serverless function - proxy to VPS API."""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET'
    response.headers['Content-Type'] = 'application/json'
    
    try:
        # Connect to VPS API
        conn = http.client.HTTPConnection('129.226.213.48', timeout=5)
        conn.request('GET', '/api/status')
        res = conn.getresponse()
        data = res.read().decode()
        conn.close()
        
        response.status_code = 200
        response.send(data)
    except Exception as e:
        response.status_code = 500
        response.send(json.dumps({'error': str(e)}))
