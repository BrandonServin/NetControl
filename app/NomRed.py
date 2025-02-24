import json
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

def obtener_contrasena(ssid):
    if not ssid:
        return None
    cmd = f'netsh wlan show profile name="{ssid}" key=clear'
    resultado = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    password = None
    for linea in resultado.stdout.splitlines():
        # Se convierte a minúsculas para comparar sin problemas de mayúsculas/minúsculas
        if "contenido de la clave" in linea.lower() or "key content" in linea.lower():
            password = linea.split(":", 1)[-1].strip()
            break
    return password

def obtener_info_red():
    cmd = "netsh wlan show interfaces"
    resultado = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    
    ssid, banda, cifrado = None, None, None

    for linea in resultado.stdout.splitlines():
        l = linea.strip()
        low = l.lower()
        # Obtener el SSID (evitando la línea de BSSID)
        if "ssid" in low and "bssid" not in low:
            ssid = l.split(":", 1)[-1].strip()
        # Intentar obtener la frecuencia para determinar la banda
        elif "frecuencia" in low or "frequency" in low:
            try:
                partes = l.split(":", 1)[-1].strip().split(" ")
                frecuencia_str = partes[0].replace(",", ".")
                unidad = partes[1].lower() if len(partes) > 1 else ""
                freq_val = float(frecuencia_str)
                # Si la unidad indica GHz, convertimos a MHz
                if "ghz" in unidad:
                    frecuencia_mhz = int(freq_val * 1000)
                else:
                    frecuencia_mhz = int(freq_val)
                banda = "2.4 GHz" if frecuencia_mhz < 3000 else "5 GHz"
            except Exception as e:
                print("Error procesando frecuencia:", e)
        # Si no se pudo obtener la banda por frecuencia, intentar con el canal
        elif ("canal" in low or "channel" in low) and not banda:
            try:
                channel_str = l.split(":", 1)[-1].strip().split(" ")[0]
                channel = int(channel_str)
                # Los canales 1-14 suelen corresponder a 2.4 GHz
                banda = "2.4 GHz" if channel <= 14 else "5 GHz"
            except Exception as e:
                print("Error procesando canal:", e)
        # Obtener el tipo de cifrado
        elif "cifrado" in low or "encryption" in low:
            cifrado = l.split(":", 1)[-1].strip()
            
    password = obtener_contrasena(ssid)
    return {"ssid": ssid, "banda": banda, "cifrado": cifrado, "password": password}

class MyRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Usamos la ruta /get_wifi_info para que coincida con el fetch del HTML
        if self.path == '/get_wifi_info':
            data = obtener_info_red()
            response = json.dumps(data).encode('utf-8')
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

def run(server_class=HTTPServer, handler_class=MyRequestHandler, host='0.0.0.0', port=5000):
    server_address = (host, port)
    httpd = server_class(server_address, handler_class)
    print(f"Servidor escuchando en {host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print("Servidor detenido.")
