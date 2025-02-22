import socket
import requests
import subprocess
import re

def get_local_ip():
    """Obtiene la IP local del dispositivo."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'  # Si no se puede obtener la IP, se asigna localhost
    finally:
        s.close()
    return ip


def get_vendor(mac_address):
    """Obtiene el fabricante de un dispositivo a partir de su dirección MAC usando la API macvendors.com."""
    url = f"https://api.macvendors.com/{mac_address}"
    response = requests.get(url)
    return response.text if response.status_code == 200 else "Desconocido"


def scan_network():
    """Escanea la red local en busca de dispositivos activos."""
    ip = get_local_ip()
    subnet = '.'.join(ip.split('.')[:-1]) + '.0/24'

    try:
        result = subprocess.run(['nmap', '-sP', subnet], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        error = result.stderr.decode('utf-8')

        if error:
            return {"error": error}

        devices = []
        device_info = {}

        for line in output.split('\n'):
            if "Nmap scan report for" in line:
                match = re.search(r'Nmap scan report for (.+)', line)
                if match:
                    device_info = {"Nombre": match.group(0), "Ip": match.group(1), "Mac": None, "Estado": "Up", "Fabricante": None}
            elif "MAC Address" in line:
                match = re.search(r'MAC Address: ([0-9A-Fa-f:]+) \((.+)\)', line)
                if match:
                    device_info["Mac"] = match.group(1)
                    device_info["Fabricante"] = get_vendor(match.group(1))

            if "Nombre" in device_info and device_info["Nombre"] and device_info["Mac"]:
                devices.append(device_info)
                device_info = {}

        return {
            "subnet": subnet,
            "dispositivos_conectados": len(devices),
            "dispositivos": devices
        }
    except Exception as e:
        return {"error": str(e)}
