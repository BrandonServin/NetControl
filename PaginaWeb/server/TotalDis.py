from flask import Flask, jsonify
import socket
import subprocess
import platform
import re

app = Flask(__name__)

def get_network_info():
    """Obtiene la dirección IP y la máscara de subred de la red activa."""
    try:
        system = platform.system()
        ip_address, subnet_mask = None, None

        if system == "Windows":
            command = "ipconfig"
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = result.stdout

            ip_match = re.search(r"(?:Dirección IPv4|IPv4 Address)[ .:]+(\d+\.\d+\.\d+\.\d+)", output)
            mask_match = re.search(r"(?:Máscara de subred|Subnet Mask)[ .:]+(\d+\.\d+\.\d+\.\d+)", output)

        else:  # Linux / macOS
            command = "ip -o -4 addr show | awk '{print $4}'"
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = result.stdout.strip()

            if output:
                ip_match = re.search(r"(\d+\.\d+\.\d+\.\d+)/(\d+)", output)
                if ip_match:
                    ip_address, cidr = ip_match.groups()
                    subnet_mask = cidr_to_mask(int(cidr))

        if ip_match:
            ip_address = ip_match.group(1)
        if mask_match:
            subnet_mask = mask_match.group(1)

        if not ip_address or not subnet_mask:
            raise Exception("No se pudo detectar la red correctamente.")

        return ip_address, subnet_mask
    except Exception as e:
        print(f"Error al obtener la información de la red: {e}")
        return None, None

def cidr_to_mask(cidr):
    """Convierte una notación CIDR en una máscara de subred."""
    mask = (0xFFFFFFFF >> (32 - cidr)) << (32 - cidr)
    return ".".join(str((mask >> (8 * i)) & 255) for i in range(4)[::-1])

def calculate_network_ip(ip_address, subnet_mask):
    """Calcula la dirección de red basada en la IP y la máscara de subred."""
    ip_parts = list(map(int, ip_address.split(".")))
    mask_parts = list(map(int, subnet_mask.split(".")))

    network_parts = [ip_parts[i] & mask_parts[i] for i in range(4)]
    return ".".join(map(str, network_parts))

def get_arp_table():
    """Obtiene la tabla ARP para listar dispositivos activos en la red."""
    command = "arp -a"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        return []

    devices = []
    for line in result.stdout.split("\n"):
        match = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
        if match:
            devices.append(match.group(1))

    return devices

def scan_network(network_ip):
    """Escanea la red en busca de dispositivos conectados."""
    devices = set(get_arp_table())  # Obtiene dispositivos de ARP

    try:
        print("Usando Nmap para escanear la red...")
        nmap_command = f"nmap -sn {network_ip}/24"
        result = subprocess.run(nmap_command, shell=True, capture_output=True, text=True)

        for line in result.stdout.split("\n"):
            match = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
            if match:
                devices.add(match.group(1))

    except Exception:
        print("Nmap no está instalado. Escaneo con ping.")

        for i in range(1, 255):
            ip = f"{network_ip}.{i}"
            if ping_ip(ip):
                devices.add(ip)

    return sorted(devices)

def ping_ip(ip):
    """Realiza un ping a una dirección IP para verificar si está activa."""
    command = ["ping", "-n", "1", ip] if platform.system() == "Windows" else ["ping", "-c", "1", ip]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0

@app.route('/api/dispositivos', methods=['GET'])
def obtener_dispositivos():
    ip_address, subnet_mask = get_network_info()
    if ip_address and subnet_mask:
        network_ip = calculate_network_ip(ip_address, subnet_mask)
        devices = scan_network(network_ip)
        return jsonify({'dispositivos_conectados': len(devices), 'ips': devices})
    else:
        return jsonify({'error': 'No se pudo detectar la red a la que estás conectado.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
