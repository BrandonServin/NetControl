from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

def obtener_contrasena(ssid):
    if not ssid:
        return None
    cmd = f'netsh wlan show profile name="{ssid}" key=clear'
    resultado = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    password = None
    for linea in resultado.stdout.split("\n"):
        if "Contenido de la clave" in linea or "Key Content" in linea:
            password = linea.split(":", 1)[-1].strip()
            break
    return password

def obtener_info_red():
    cmd = "netsh wlan show interfaces"
    resultado = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    
    ssid, banda, cifrado = None, None, None

    for linea in resultado.stdout.split("\n"):
        # Obtenemos el SSID actual (evitando la línea de BSSID)
        if "SSID" in linea and "BSSID" not in linea:
            ssid = linea.split(":", 1)[-1].strip()
        # Obtenemos la frecuencia para determinar la banda
        elif "Frecuencia" in linea or "Frequency" in linea:
            try:
                frecuencia_mhz = int(linea.split(":", 1)[-1].strip().split(" ")[0])
                banda = "2.4 GHz" if frecuencia_mhz < 3000 else "5 GHz"
            except Exception:
                banda = None
        # Obtenemos el tipo de cifrado
        elif "Cifrado" in linea or "Encryption" in linea:
            cifrado = linea.split(":", 1)[-1].strip()

    # Obtener la contraseña utilizando el SSID
    password = obtener_contrasena(ssid)

    return {"ssid": ssid, "banda": banda, "cifrado": cifrado, "password": password}