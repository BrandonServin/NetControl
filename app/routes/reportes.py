from flask import Blueprint, jsonify, request
from app.models.database import db
from app.models.reportes import Reportes

reportes_bp = Blueprint("reportes", __name__)

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