from flask import Blueprint, render_template, request, jsonify
from app.models.database import db
from app.models.speedtest import realizar_speedtest
from app.models.nmap import scan_network
from app.models.login import Login
from app.models.inventario import Inventario
from app.models.reportes import Reportes

main = Blueprint("main", __name__)

# Cargar página principal
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

# Ruta para obtener todos los usuarios
@main.route("/login", methods=["POST"])
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


# - - - - - - - - - - - - Metodos De La Tabla Para El Apartado De Inventario - - - - - - - - - - - -
# Ruta para agregar un nuevo inventario
@main.route("/inventario", methods=["POST"])
def agregar_inv():
    data = request.json
    nuevo_inv = Inventario(
        nombre=data["nombre"],
        modelo=data["modelo"],
        noSerie=data["noSerie"],
        cantidad=data["cantidad"],
        ubicacion=data["ubicacion"],
        estado=data["estado"],
    )
    db.session.add(nuevo_inv)
    db.session.commit()
    return jsonify({"mensaje": "Inventario agregado correctamente"}), 201


# Ruta para obtener todos los reportes
@main.route("/inventario", methods=["GET"])
def obtener_inv():
    reportes = Inventario.query.all()
    return jsonify(
        [
            {
                "id": r.id,
                "nombre": r.nombre,
                "modelo": r.modelo,
                "noSerie": r.noSerie,
                "cantidad": r.cantidad,
                "ubicacion": r.ubicacion,
                "estado": r.estado,
            }
            for r in reportes
        ]
    )


# Ruta para eliminar un inventario por su ID
@main.route("/inventario/<int:id>", methods=["DELETE"])
def eliminar_inv(id):
    inventario = Inventario.query.get(id)
    if not inventario:
        return jsonify({"mensaje": "Elemento no encontrado"}), 404

    db.session.delete(inventario)
    db.session.commit()
    return jsonify({"mensaje": "Elemento eliminado correctamente"}), 200


# - - - - - - - - - - - - Metodos De La Tabla Para El Apartado De Fallas - - - - - - - - - - - -
# Ruta para obtener todos los reportes
@main.route("/reportes", methods=["GET"])
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
@main.route("/reportes", methods=["POST"])
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
@main.route("/reportes/<int:id>", methods=["PUT"])
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

# - - - - - - - - - - - - Metodo para hacer la prueba - - - - - - - - - - - -
# Ruta para iniciar la prueba de speedtest
@main.route("/iniciar_prueba")
def iniciar_prueba():
    resultado = realizar_speedtest()
    
    if "error" in resultado:
        return jsonify(resultado), 500  # Devuelve un error si algo falló
    
    return jsonify(resultado)

# - - - - - - - - - - - - Metodo para hacer el NMAP - - - - - - - - - - - -
@main.route('/scan')
def scan():
    resultado = scan_network()
    
    if "error" in resultado:
        return jsonify(resultado), 500  # Devuelve un error si algo falló
    
    return jsonify(resultado)