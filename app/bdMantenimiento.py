from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sqlite3
from io import BytesIO

app = Flask(__name__)
CORS(app)  # Permite solicitudes desde otros orígenes (útil en desarrollo)

DATABASE = 'database.db'

def init_db():
    """Inicializa la base de datos, creando la tabla 'plans' si no existe
    y realizando la migración para agregar las columnas 'file_name' y 'file_data' si faltan.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Crea la tabla si no existe (sin las columnas de archivo inicialmente)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            state TEXT NOT NULL
        )
    ''')
    
    # Verifica si las columnas de archivo existen y, si no, agrégalas.
    cursor.execute("PRAGMA table_info(plans)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'file_name' not in columns:
        cursor.execute("ALTER TABLE plans ADD COLUMN file_name TEXT")
    if 'file_data' not in columns:
        cursor.execute("ALTER TABLE plans ADD COLUMN file_data BLOB")
    
    conn.commit()
    conn.close()

init_db()

@app.route('/plans', methods=['GET'])
def get_plans():
    """Devuelve todos los planes (sin la data binaria del archivo)."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, type, state, file_name FROM plans')
    rows = cursor.fetchall()
    conn.close()
    
    plans = []
    for row in rows:
        plans.append({
            'id': row[0],
            'name': row[1],
            'type': row[2],
            'state': row[3],
            'file_name': row[4]
        })
    return jsonify({'plans': plans})

@app.route('/add_plan', methods=['POST'])
def add_plan():
    """
    Agrega un nuevo plan.
    Recibe datos mediante multipart/form-data:
      - name: nombre del plan
      - type: "Preventivo" o "Correctivo"
      - state: estado del plan
      - file: archivo opcional
    """
    name = request.form.get('name')
    plan_type = request.form.get('type')
    state = request.form.get('state')
    
    if not name or not plan_type or not state:
        return jsonify({'error': 'Faltan datos para agregar el plan.'}), 400
    
    file = request.files.get('file')
    if file and file.filename != '':
        file_name = file.filename
        file_data = file.read()
    else:
        file_name = None
        file_data = None

    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO plans (name, type, state, file_name, file_data)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, plan_type, state, file_name, file_data))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Plan agregado exitosamente!'})
    except Exception as e:
        return jsonify({'error': f'Error al agregar el plan: {str(e)}'}), 500

@app.route('/download/<int:plan_id>', methods=['GET'])
def download_file(plan_id):
    """
    Descarga el archivo asociado al plan indicado.
    Si no existe archivo, retorna un error.
    """
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT file_name, file_data FROM plans WHERE id = ?', (plan_id,))
        row = cursor.fetchone()
        conn.close()
        if row and row[1]:
            file_name, file_data = row
            return send_file(BytesIO(file_data), as_attachment=True, download_name=file_name)
        else:
            return jsonify({'error': 'No se encontró archivo para este plan.'}), 404
    except Exception as e:
        return jsonify({'error': f'Error al descargar el archivo: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
