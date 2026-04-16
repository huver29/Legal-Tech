import json
import urllib.request
import urllib.error

url = 'http://127.0.0.1:8001/api/consulta'
payload = json.dumps({'query': 'Derecho a la salud'}).encode('utf-8')
req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req, timeout=120) as resp:
        print('status', resp.status)
        print(resp.read().decode('utf-8')[:1200])
except urllib.error.HTTPError as exc:
    print('HTTP', exc.code)
    print(exc.read().decode('utf-8'))
except urllib.error.URLError as exc:
    print('URLError', exc.reason)
except Exception as exc:
    print('ERROR', type(exc).__name__, exc)
