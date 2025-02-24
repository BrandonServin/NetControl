from flask import jsonify, send_file
from io import BytesIO
from app.models.database import get_db_connection

def get_plans():
    """Obtiene todos los planes (sin datos binarios de archivo)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, type, state, file_name FROM plans')
    rows = cursor.fetchall()
    conn.close()

    plans = [{'id': row[0], 'name': row[1], 'type': row[2], 'state': row[3], 'file_name': row[4]} for row in rows]
    return jsonify({'plans': plans})

def add_plan(request):
    """Agrega un nuevo plan con datos y archivo opcional."""
    name = request.form.get('name')
    plan_type = request.form.get('type')
    state = request.form.get('state')

    if not name or not plan_type or not state:
        return jsonify({'error': 'Faltan datos para agregar el plan.'}), 400

    file = request.files.get('file')
    file_name, file_data = (file.filename, file.read()) if file and file.filename else (None, None)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO plans (name, type, state, file_name, file_data) VALUES (?, ?, ?, ?, ?)',
            (name, plan_type, state, file_name, file_data)
        )
        conn.commit()
        conn.close()
        return jsonify({'message': 'Plan agregado exitosamente!'})
    except Exception as e:
        return jsonify({'error': f'Error al agregar el plan: {str(e)}'}), 500

def download_file(plan_id):
    """Descarga el archivo asociado al plan indicado."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT file_name, file_data FROM plans WHERE id = ?', (plan_id,))
        row = cursor.fetchone()
        conn.close()

        if row and row[1]:
            return send_file(BytesIO(row[1]), as_attachment=True, download_name=row[0])
        return jsonify({'error': 'No se encontró archivo para este plan.'}), 404
    except Exception as e:
        return jsonify({'error': f'Error al descargar el archivo: {str(e)}'}), 500
