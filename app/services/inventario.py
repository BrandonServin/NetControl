from flask import jsonify
from app.models.inventario import Inventario, UnidadActiva
from sqlalchemy.exc import IntegrityError
from app import db


def agregarInventario(data):
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

        return jsonify({"mensaje": "Inventario agregado correctamente"}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"mensaje": "Error al guardar el inventario"}), 
    
def obtenerInventario():
    reportes = Inventario.query.all()
    return jsonify([
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
    ])

def eliminarInventario(id):
    inventario = Inventario.query.get(id)
    if not inventario:
        return jsonify({"mensaje": "Elemento no encontrado"}), 404

    db.session.delete(inventario)
    db.session.commit()
    return jsonify({"mensaje": "Elemento eliminado correctamente"}), 200

def activarDispositivo(data):
    id_dispositivo = data["id"]
    ubicacion = data["ubicacion"]

    dispositivo = Inventario.query.get(id_dispositivo)
    if not dispositivo:
        return jsonify({"mensaje": "Error: Dispositivo no encontrado."}), 404

    if dispositivo.cantidadInventario <= 0:
        return jsonify({"mensaje": "Error: No hay unidades disponibles en inventario."}), 400

    nueva_unidad = UnidadActiva(inventario_id=dispositivo.id, ubicacion=ubicacion)
    db.session.add(nueva_unidad)

    dispositivo.cantidadActiva += 1
    dispositivo.cantidadInventario -= 1
    db.session.commit()

    return jsonify({"mensaje": "Dispositivo activado correctamente."}), 200

def obtDisActivos(modelo):
    dispositivos_activos = (
        UnidadActiva.query
        .join(Inventario, Inventario.id == UnidadActiva.inventario_id)
        .filter(Inventario.modelo == modelo)
        .all()
    )

    if not dispositivos_activos:
        return jsonify({"mensaje": "No se encontraron dispositivos activos para este modelo."}), 404

    return jsonify([
        {
            "id": ua.id,
            "nombre": ua.inventario.nombre,
            "modelo": ua.inventario.modelo,
            "noSerie": ua.inventario.noSerie,
            "ubicacion": ua.ubicacion
        }
        for ua in dispositivos_activos
    ])
