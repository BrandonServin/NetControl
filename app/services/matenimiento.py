from flask import jsonify, send_file, Response, abort
from io import BytesIO
from app.models.database import db
from app.models.mantanimiento import Mantenimiento

def get_plans():
    """Obtiene todos los planes sin datos binarios de archivo."""
    plans = Mantenimiento.query.all()  # Obtiene todos los registros de la tabla `plans`
    plans_list = [plan.to_dict() for plan in plans]
    return jsonify({"plans": plans_list})

def add_plan(request):
    """Agrega un nuevo plan a la base de datos, incluyendo el archivo si se proporciona."""
    print(request.form)

    name = request.form.get("name")
    plan_type = request.form.get("type")
    state = request.form.get("state")
    file = request.files.get("file")  # Archivo recibido

    if not name or not plan_type or not state:
        return jsonify({"error": "Faltan datos"}), 400

    new_plan = Mantenimiento(
        name=name,
        type=plan_type,
        state=state,
        file_name=file.filename if file else None,
        file_data=file.read() if file else None,  # Guardar el archivo en binario
    )

    db.session.add(new_plan)
    db.session.commit()

    return jsonify({"message": "Plan agregado correctamente"}), 201

def download_file(plan_id):
    """Descarga el archivo almacenado en la base de datos."""
    plan = Mantenimiento.query.get(plan_id)

    if not plan:
        return jsonify({"error": "Plan no encontrado"}), 404
    
    if not plan.file_data:
        return jsonify({"error": "No hay archivo para este plan"}), 404

    # Convertir los datos binarios en un archivo descargable
    file_stream = BytesIO(plan.file_data)
    
    return send_file(
        file_stream,
        as_attachment=True,
        download_name=plan.file_name or "archivo.bin",
        mimetype="application/octet-stream",
    )
