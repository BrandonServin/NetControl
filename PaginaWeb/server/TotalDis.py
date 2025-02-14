
from flask import Flask, jsonify
import platform
import subprocess
import re
import socket
import nmap
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
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
"""
def get_arp_table():
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
    """

def scan_network(network_ip, subnet_mask):
    try:
        nm = nmap.PortScanner(nmap_search_path=['C:\\Program Files (x86)\\Nmap\\nmap.exe'])
        nm.scan(hosts=f"{network_ip}/24", arguments="-sn")
        active_hosts = nm.all_hosts()
        
        devices = []
        for host in active_hosts:
            try:
                hostname = socket.gethostbyaddr(host)[0]
            except:
                hostname = host
            devices.append({'ip': host, 'hostname': hostname})
        return devices
    except nm.PortScannerError as e:
        return []



