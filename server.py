from http.server import HTTPServer, BaseHTTPRequestHandler
import json, os, socket

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')
STATIC_DIR = os.path.dirname(__file__)
PORT = 8080

class Handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self._cors()

    def do_GET(self):
        if self.path in ('/', '/index.html'):
            self._serve_file('index.html', 'text/html; charset=utf-8')
        elif self.path == '/api/data':
            self._get_data()
        else:
            self.send_error(404, 'Not Found')

    def do_POST(self):
        if self.path == '/api/data':
            self._post_data()
        else:
            self.send_error(404, 'Not Found')

    # ── handlers ──────────────────────────────────────────────────────────────

    def _get_data(self):
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    body = f.read().encode('utf-8')
            else:
                body = b'[]'
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(body))
            self._cors()
            self.wfile.write(body)
        except Exception as e:
            self.send_error(500, str(e))

    def _post_data(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            json.loads(body)           # validate JSON
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                f.write(body.decode('utf-8'))
            resp = b'{"ok":true}'
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(resp))
            self._cors()
            self.wfile.write(resp)
        except Exception as e:
            self.send_error(500, str(e))

    def _serve_file(self, filename, content_type):
        path = os.path.join(STATIC_DIR, filename)
        try:
            with open(path, 'rb') as f:
                body = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', len(body))
            self.end_headers()
            self.wfile.write(body)
        except FileNotFoundError:
            self.send_error(404, 'File not found')

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, fmt, *args):
        print(f"  [{self.address_string()}]  {fmt % args}")


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    try:
        ip = socket.gethostbyname(socket.gethostname())
    except Exception:
        ip = '?.?.?.?'

    httpd = HTTPServer(('0.0.0.0', PORT), Handler)

    print()
    print('  +-----------------------------------------+')
    print('  |      CyberIPs - Servidor activo         |')
    print('  +-----------------------------------------+')
    print(f'  |  Local :  http://localhost:{PORT}          |')
    print(f'  |  Red   :  http://{ip:<24} |')
    print(f'  |  Puerto:  {PORT}                           |')
    print('  +-----------------------------------------+')
    print('  |  Comparte la URL de Red con tu equipo   |')
    print('  |  Ctrl+C para detener el servidor        |')
    print('  +-----------------------------------------+')
    print()

    httpd.serve_forever()
