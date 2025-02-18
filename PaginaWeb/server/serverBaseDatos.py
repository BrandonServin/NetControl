from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from NomRed import obtener_info_red
import os
import speedtest
import nmap
import socket
import subprocess
import re
import requests
from pyngrok import ngrok

app = Flask(__name__)
basedir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)  # Obtener la ruta donde está el archivo server.py
db_path = os.path.join(basedir, "assets", "python", "instance", "baseNetControl.db")
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{db_path}"  # Ruta a la base de datos en la carpeta 'data'
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

print(f"Ruta de la base de datos: {db_path}")

db = SQLAlchemy(app)
CORS(app)  # Habilitar CORS para comunicación con el frontend


# - - - - - - - - - - - - Metodos De La Tabla Para El Apartado De Fallas - - - - - - - - - - - -
# Modelo de la base de datos
class Reportes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    prioridad = db.Column(db.String(20), nullable=False)
    estado = db.Column(db.String(20), nullable=False)
    fecha = db.Column(db.String(10), nullable=False)


# Ruta para obtener todos los reportes
@app.route("/reportes", methods=["GET"])
def obtener_reportes():
    reportes = Reportes.query.all()
    return jsonify(
        [
            {
                "id": r.id,
                "titulo": r.titulo,
                "prioridad": r.prioridad,
                "estado": r.estado,
                "fecha": r.fecha,
            }
            for r in reportes
        ]
    )


# Ruta para agregar un nuevo reporte
@app.route("/reportes", methods=["POST"])
def agregar_reporte():
    data = request.json
    nuevo_reporte = Reportes(
        titulo=data["titulo"],
        prioridad=data["prioridad"],
        estado=data["estado"],
        fecha=data["fecha"],
    )
    db.session.add(nuevo_reporte)
    db.session.commit()
    return jsonify({"mensaje": "Reporte agregado correctamente"}), 201


# Ruta para actualizar el estado
@app.route("/reportes/<int:id>", methods=["PUT"])
def actualizar_reporte(id):
    data = request.json
    nuevo_estado = data.get("estado")

    if not nuevo_estado:
        return jsonify({"error": "Estado requerido"}), 400

    reporte = Reportes.query.get(id)

    if reporte is None:
        return jsonify({"error": "Reporte no encontrado"}), 404

    reporte.estado = nuevo_estado
    db.session.commit()

    return (
        jsonify(
            {
                "message": "Estado actualizado correctamente",
                "nuevo_estado": nuevo_estado,
            }
        ),
        200,
    )


# - - - - - - - - - - - - Fin De Los Metodos De La Tabla Para El Apartado De Fallas - - - - - - - - - - - -


# - - - - - - - - - - - - Metodos De La Tabla Para El Apartado De Inventario - - - - - - - - - - - -
class Inventario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(40), nullable=False)
    noSerie = db.Column(db.String(40), nullable=False)
    ubicacion = db.Column(db.String(40), nullable=False)
    estado = db.Column(db.String(20), nullable=False)


# Ruta para agregar un nuevo inventario
@app.route("/inventario", methods=["POST"])
def agregar_inv():
    data = request.json
    nuevo_inv = Inventario(
        nombre=data["nombre"],
        modelo=data["modelo"],
        noSerie=data["noSerie"],
        ubicacion=data["ubicacion"],
        estado=data["estado"],
    )
    db.session.add(nuevo_inv)
    db.session.commit()
    return jsonify({"mensaje": "Inventario agregado correctamente"}), 201


# Ruta para obtener todos los reportes
@app.route("/inventario", methods=["GET"])
def obtener_inv():
    reportes = Inventario.query.all()
    return jsonify(
        [
            {
                "id": r.id,
                "nombre": r.nombre,
                "modelo": r.modelo,
                "noSerie": r.noSerie,
                "ubicacion": r.ubicacion,
                "estado": r.estado,
            }
            for r in reportes
        ]
    )


# Ruta para eliminar un inventario por su ID
@app.route("/inventario/<int:id>", methods=["DELETE"])
def eliminar_inv(id):
    inventario = Inventario.query.get(id)
    if not inventario:
        return jsonify({"mensaje": "Elemento no encontrado"}), 404

    db.session.delete(inventario)
    db.session.commit()
    return jsonify({"mensaje": "Elemento eliminado correctamente"}), 200


# - - - - - - - - - - - - Metodos De La Tabla Para El Apartado De Login - - - - - - - - - - - -
class Login(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    usuario = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    
# Ruta para obtener todos los usuarios
@app.route("/login", methods=["POST"])
def iniciar_sesion():
    data = request.json  # Obtener los datos enviados desde el frontend
    usuario = data.get("usuario")
    password = data.get("password")

    # Buscar el usuario en la base de datos
    user = Login.query.filter_by(usuario=usuario).first()

    if user and user.password == password:
        return jsonify({"success": True, "message": "Inicio de sesión exitoso"})
    else:
        return jsonify({"success": False, "message": "Usuario o contraseña incorrectos"}), 401


#- - - - - - - - - - - - Metodos De MMap- - - - - - - - - - - -
# Mostramos la cantidad de dispositivos conectados
def get_local_ip():
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
    # Usamos la API de macvendors.com para obtener el fabricante
    url = f"https://api.macvendors.com/{mac_address}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return "Desconocido"

@app.route('/scan')
def scan():
    ip = get_local_ip()
    subnet = '.'.join(ip.split('.')[:-1]) + '.0/24'

    try:
        result = subprocess.run(['nmap', '-sP', subnet], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        error = result.stderr.decode('utf-8')

        if error:
            return jsonify({"error": error}), 500

        devices = []
        device_info = {}

        for line in output.split('\n'):
            if "Nmap scan report for" in line:
                match = re.search(r'Nmap scan report for (.+)', line)
                if match:
                    device_info = {"Nombre": match.group(0), "Ip": match.group(1), "Mac": None, "Estado": "Up", "Fabricante": None}
            elif "Host is up" in line:
                pass  # Ya sabemos que el host está activo
            elif "MAC Address" in line:
                match = re.search(r'MAC Address: ([0-9A-Fa-f:]+) \((.+)\)', line)
                if match:
                    device_info["Mac"] = match.group(1)
                    device_info["Fabricante"] = get_vendor(match.group(1))

            if "Nombre" in device_info and device_info["Nombre"] and device_info["Mac"]:
                devices.append(device_info)
                device_info = {}

        return jsonify({
            "subnet": subnet,
            "dispositivos_conectados": len(devices),
            "dispositivos": devices
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


#Metodo para obtener detalles de la red
@app.route('/get_wifi_info', methods=['GET'])
def get_wifi_info():
    """Ruta para obtener la información completa de la red WiFi."""
    return jsonify(obtener_info_red())

# - - - - - - - - - - - - Metodo para hacer la prueba - - - - - - - - - - - -
# Ruta para iniciar la prueba de speedtest
@app.route("/iniciar_prueba")
def iniciar_prueba():
    try:
        # Inicializa Speedtest
        st = speedtest.Speedtest()

        # Encuentra el mejor servidor automáticamente
        st.get_best_server()

        # Realiza las pruebas de descarga y subida
        download_speed = st.download()
        upload_speed = st.upload()

        # Obtiene los resultados
        results = st.results.dict()

        # Devuelve los resultados en Mbps y el ping en ms
        return jsonify(
            {
                "download": round(download_speed / 1_000_000, 2),  # Convertir a Mbps
                "upload": round(upload_speed / 1_000_000, 2),  # Convertir a Mbps
                "ping": results["ping"],
            }
        )
    except speedtest.SpeedtestException as e:
        # Maneja errores específicos de Speedtest
        return jsonify({"error": f"Error de Speedtest: {str(e)}"}), 500
    except Exception as e:
        # Maneja errores inesperados
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


# - - - - - - - - - - - - Fin del Metodo - - - - - - - - - - - -
app = Flask(__name__, template_folder='.')
@app.route("/")
def home():
    #return "¡Servidor Flask con ngrok funcionando!"
    file_path = os.path.abspath(os.path.join(os.getcwd(), "../../index.html"))
    return send_from_directory(os.path.dirname(file_path), os.path.basename(file_path))
# Cargar pagina 
#@app.route("/")  # <- Asegúrate de tener esta ruta
#def index():
 #   return render_template("index.html")


if __name__ == "__main__":
    public_url = ngrok.connect(5000)
    print(f"Servidor público: {public_url}")

    # Iniciar la aplicación Flask
    app.run(port=5000)
    app.run(debug=True)
