from flask import Blueprint, render_template, request, jsonify
from app.models.database import db
from sqlalchemy.exc import IntegrityError
from app.models.speedtest import realizar_speedtest
from app.models.nmap import scan_network
from app.models.login import Login
from app.models.inventario import Inventario, UnidadActiva
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

    # Verificar si el modelo o el número de serie ya existen
    existente = Inventario.query.filter(
        (Inventario.modelo == data["modelo"]) | (Inventario.noSerie == data["noSerie"])
    ).first()

    if existente:
        return jsonify({"mensaje": "Error: Modelo o número de serie ya existen"}), 400

    try:
        nuevo_inv = Inventario(
            nombre=data["nombre"],
            modelo=data["modelo"],
            noSerie=data["noSerie"],
            cantidadTotal=data["cantidad"],
            cantidadActiva=0,
            cantidadInventario=data["cantidad"],
            ubicacion=data["ubicacion"],
            estado=data["estado"],
        )

        # Agregar el nuevo dispositivo a la base de datos
        db.session.add(nuevo_inv)
        db.session.commit()

        # Responder con un mensaje de éxito
        return jsonify({"mensaje": "Inventario agregado correctamente"}), 201
    except IntegrityError:
        # Manejar cualquier error de base de datos, como violación de restricciones
        db.session.rollback()
        return jsonify({"mensaje": "Error al guardar el inventario"}), 500
    

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
                "cantidadTotal": r.cantidadTotal,
                "cantidadActiva": r.cantidadActiva,
                "cantidadInventario": r.cantidadInventario,
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

# Activar dispositivo y registrar ubicación
@main.route("/activar_dispositivo", methods=["POST"])
def activar_dispositivo():
    data = request.json
    id_dispositivo = data["id"]
    ubicacion = data["ubicacion"]

    dispositivo = Inventario.query.get(id_dispositivo)

    if not dispositivo:
        return jsonify({"mensaje": "Error: Dispositivo no encontrado."}), 404

    # Verificar si aún hay unidades disponibles para activar
    if dispositivo.cantidadInventario <= 0:
        return jsonify({"mensaje": "Error: No hay unidades disponibles en inventario."}), 400

    # Crear una nueva entrada en UnidadActiva en lugar de modificar el Inventario
    nueva_unidad = UnidadActiva(inventario_id=dispositivo.id, ubicacion=ubicacion)
    db.session.add(nueva_unidad)

    # Actualizar los conteos en Inventario
    dispositivo.cantidadActiva += 1
    dispositivo.cantidadInventario -= 1

    db.session.commit()

    return jsonify({"mensaje": "Dispositivo activado correctamente."}), 200



@main.route("/dispositivos_activos/<modelo>", methods=["GET"])
def obtener_dispositivos_activos(modelo):
    dispositivos_activos = (
        UnidadActiva.query
        .join(Inventario, Inventario.id == UnidadActiva.inventario_id)
        .filter(Inventario.modelo == modelo)
        .all()
    )

    if not dispositivos_activos:
        return jsonify({"mensaje": "No se encontraron dispositivos activos para este modelo."}), 404

    # Retornar los dispositivos activos con su información
    return jsonify([
        {
            "id": ua.id,
            "nombre": ua.inventario.nombre,
            "modelo": ua.inventario.modelo,
            "noSerie": ua.inventario.noSerie,
            "ubicacion": ua.ubicacion  # La ubicación de la unidad activa
        }
        for ua in dispositivos_activos
    ])



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

# Ruta para evitar el error de favicon
@main.route('/favicon.ico')
def favicon():
    return '', 204