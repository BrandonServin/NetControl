from flask import Flask, jsonify
import socket
import subprocess
import platform
import re


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
    try:
        devices = set(get_arp_table())  # Obtiene dispositivos ARP
        
        # Verifica si nmap está disponible
        if subprocess.run("nmap -V", shell=True, capture_output=True).returncode != 0:
            print("Nmap no está instalado o no tiene permisos.")
            return len(devices)  # Usa solo ARP si nmap falla
        
        # Escaneo con Nmap
        nmap_command = f"nmap -sn {network_ip}/24"
        result = subprocess.run(nmap_command, shell=True, capture_output=True, text=True)

        for line in result.stdout.split("\n"):
            match = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
            if match:
                devices.add(match.group(1))
        
        return len(devices)  # Devuelve el número correcto
    
    except Exception as e:
        print(f"Error al escanear la red: {e}")
        return 0  # Evita que la API falle

def ping_ip(ip):
    """Realiza un ping a una dirección IP con tiempo de espera."""
    command = ["ping", "-n", "1", ip] if platform.system() == "Windows" else ["ping", "-c", "1", ip]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=2)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False  # Si tarda demasiado, se considera inactivo



def ping_ip(ip):
    """Realiza un ping a una dirección IP para verificar si está activa."""
    command = ["ping", "-n", "1", ip] if platform.system() == "Windows" else ["ping", "-c", "1", ip]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0


