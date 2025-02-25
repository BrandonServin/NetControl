from flask import Blueprint, render_template, request, jsonify
from app.services.speedtest import realizar_speedtest
from app.services.nmap import scan_network
from app.services.login import iniciar_sesion
from app.services.inventario import agregarInventario, obtenerInventario, eliminarInventario, activarDispositivo, obtDisActivos, desactivarDispositivo
from app.services.reportes import obtenerReportes, agregarReporte, actualizarReporte, eliminarReporte
from app.services.NomRed import obtener_info_red
from app.services.matenimiento import get_plans, add_plan, download_file
from app.models.reportes import Reportes

main = Blueprint("main", __name__)

# - - - - - - - - - - - - Rutas de las paginas principales - - - - - - - - - - - -
@main.route("/")  
def index():
    return render_template("index.html")

@main.route("/inicio.html") 
def inicio():
    return render_template("inicio.html")

@main.route("/Fallas.html") 
def fallas():
    return render_template("Fallas.html")

@main.route("/Ajustes.html") 
def ajustes():
    return render_template("Ajustes.html")

@main.route("/Dispositivos.html") 
def dispositivos():
    return render_template("Dispositivos.html")

@main.route("/Inventario.html") 
def inventario():
    return render_template("Inventario.html")

@main.route("/Mantenimiento.html") 
def mantenimiento():
    return render_template("Mantenimiento.html")

# - - - - - - - - - - - - Ruta Para El Inicio De Sesión - - - - - - - - - - - -
# Ruta para obtener todos los usuarios
@main.route("/login", methods=["POST"])
def login():
    data = request.json  # Obtener los datos enviados desde el frontend
    return iniciar_sesion(data)


# - - - - - - - - - - - - Rutas De Inventario - - - - - - - - - - - -
@main.route("/inventario", methods=["POST"])
def agregar_inv():
    data = request.json
    return agregarInventario(data)

@main.route("/inventario", methods=["GET"])
def obtener_inv():
    return obtenerInventario()

@main.route("/inventario/<int:id>", methods=["DELETE"])
def eliminar_inv(id):
    return eliminarInventario(id)

@main.route("/activar_dispositivo", methods=["POST"])
def activar_dispositivo():
    return activarDispositivo(request.json)

@main.route("/dispositivos_activos/<modelo>", methods=["GET"])
def obtener_dispositivos_activos(modelo):
    return obtDisActivos(modelo)

@main.route("/eliminar_dispositivo/<int:id>", methods=["DELETE"])
def eliminar_disActivo(id):
    return desactivarDispositivo(id)


# - - - - - - - - - - - - Rutas De Fallas/Reportes - - - - - - - - - - - -
@main.route("/reportes", methods=["GET"])
def obtener_reportes():
    return obtenerReportes()

@main.route("/reportes", methods=["POST"])
def agregar_reporte():
    return agregarReporte(request.json)

@main.route("/reportes/<int:id>", methods=["PUT"])
def actualizar_reporte(id):
    return actualizarReporte(id, request.json)

@main.route("/reportes/<int:id>", methods=["DELETE"])
def eliminar_reporte(id):
    return eliminarReporte(id)


# - - - - - - - - - - - - Rutas De Informacion Del Wifi - - - - - - - - - - - -
@main.route('/get_wifi_info', methods=['GET'])
def get_wifi_info():
    """Ruta para obtener la información completa de la red WiFi."""
    return jsonify(obtener_info_red())


# - - - - - - - - - - - - Rutas Para Cargas Las Fallas - - - - - - - - - - - -
@main.route("/numero_fallas", methods=["GET"])
def numero_fallas():
    try:
        numero_fallas = Reportes.query.filter(Reportes.estado.notin_(["cancelado", "completado"])).count()
        return jsonify({"numero_fallas": numero_fallas})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# - - - - - - - - - - - - Ruta para hacer la prueba de speedtest - - - - - - - - - - - -
@main.route("/iniciar_prueba")
def iniciar_prueba():
    resultado = realizar_speedtest()
    
    if "error" in resultado:
        return jsonify(resultado), 500  # Devuelve un error si algo falló
    
    return jsonify(resultado)

# - - - - - - - - - - - - Rutas para el escaneo de dispositivos - - - - - - - - - - - -
@main.route('/scan')
def scan():
    resultado = scan_network()
    
    if "error" in resultado:
        return jsonify(resultado), 500  # Devuelve un error si algo falló
    
    return jsonify(resultado)

# - - - - - - - - - - - - Rutas Para Evitar El Error De Favicon - - - - - - - - - - - -
@main.route('/favicon.ico')
def favicon():
    return '', 204

# - - - - - - - - - - - - Rutas Para El Apartado De Planes- - - - - - - - - - - -
@main.route('/plans', methods=['GET'])
def get_plans_main():
    return get_plans()

@main.route('/add_plan', methods=['POST'])
def add_plan_main():
    return add_plan(request)

@main.route('/download/<int:plan_id>', methods=['GET'])
def download_main(plan_id):
    return download_file(plan_id)