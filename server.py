from http.server import HTTPServer, BaseHTTPRequestHandler
import json, os, socket
import threading
import time
import urllib.request
import urllib.error

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')
STATIC_DIR = os.path.dirname(__file__)
PORT = 8765

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


def sync_izzi_data():
    """
    Este hilo consulta periódicamente la API de Izzi, actualiza procesos y auto-agrega IPs nuevas.
    """
    IZZI_API_URL = "https://rpabackizzi.azurewebsites.net/Bots/getBots"
    
    while True:
        try:
            req = urllib.request.Request(IZZI_API_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                api_data = json.loads(response.read().decode('utf-8'))
            
            # Convertimos la lista de izzi en un diccionario { "192.168...": "Nombre Proceso" }
            izzi_dict = {}
            for item in api_data:
                ip = item.get("botIp")
                proceso = item.get("procesoName")
                if ip and proceso:
                    izzi_dict[str(ip).strip()] = str(proceso).strip()
            
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    cyber_data = json.load(f)
                    
                cambios = False
                existing_ips = {str(e.get("ip", "")).strip(): e for e in cyber_data if e.get("ip")}
                
                # 1. Actualizar procesos de IPs existentes
                for equipo in cyber_data:
                    ip = str(equipo.get("ip", "")).strip()
                    if ip in izzi_dict:
                        nuevo_proceso = izzi_dict[ip]
                        if equipo.get("p") != nuevo_proceso:
                            equipo["p"] = nuevo_proceso
                            cambios = True

                # 2. Agregar automáticamente IPs nuevas que vengan en Izzi
                max_id = max([e.get("id", 0) for e in cyber_data], default=0)
                for ip, proceso in izzi_dict.items():
                    if ip not in existing_ips:
                        max_id += 1
                        nuevo_equipo = {
                            "id": max_id,
                            "m": ip,
                            "ip": ip,
                            "p": proceso,
                            "o": "LINUX",
                            "u": "ugenome",
                            "pw": "UbuntuCyb2026$"
                        }
                        cyber_data.append(nuevo_equipo)
                        existing_ips[ip] = nuevo_equipo
                        cambios = True
                
                if cambios:
                    with open(DATA_FILE, 'w', encoding='utf-8') as f:
                        json.dump(cyber_data, f, indent=4)
                    print(f"  [Auto-Sync] Datos de CyberIps actualizados desde Izzi ({len(cyber_data)} equipos).")
                    
        except Exception as e:
            print(f"  [Auto-Sync Error] No se pudo sincronizar con Izzi: {e}")
        
        time.sleep(30)

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

    # Iniciar hilo de sincronización en segundo plano
    sync_thread = threading.Thread(target=sync_izzi_data, daemon=True)
    sync_thread.start()

    httpd.serve_forever()
