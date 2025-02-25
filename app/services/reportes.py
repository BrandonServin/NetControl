from flask import jsonify
from app.models.reportes import Reportes, db

def obtenerReportes():
    reportes = Reportes.query.all()
    return jsonify([
        {
            "id": r.id,
            "titulo": r.titulo,
            "prioridad": r.prioridad,
            "estado": r.estado,
            "fecha": r.fecha,
        }
        for r in reportes
    ])

def agregarReporte(data):
    nuevo_reporte = Reportes(
        titulo=data["titulo"],
        prioridad=data["prioridad"],
        estado=data["estado"],
        fecha=data["fecha"],
    )
    db.session.add(nuevo_reporte)
    db.session.commit()
    return jsonify({"mensaje": "Reporte agregado correctamente"}), 201

def actualizarReporte(id, data):
    nuevo_estado = data.get("estado")
    
    if not nuevo_estado:
        return jsonify({"error": "Estado requerido"}), 400
    
    reporte = Reportes.query.get(id)
    if reporte is None:
        return jsonify({"error": "Reporte no encontrado"}), 404
    
    reporte.estado = nuevo_estado
    db.session.commit()
    
    return jsonify({"message": "Estado actualizado correctamente", "nuevo_estado": nuevo_estado}), 200

def eliminarReporte(id):
    reporte = Reportes.query.get(id)
    if not reporte:
        return jsonify({"mensaje": "Elemento no encontrado"}), 404

    db.session.delete(reporte)
    db.session.commit()
    return jsonify({"mensaje": "Elemento eliminado correctamente"}), 200
