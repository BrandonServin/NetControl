# filepath: /C:/Users/Rafael Saucedo/Documents/GitHub/NetControl/PaginaWeb/server/server.py
from flask import Flask, jsonify
from flask_cors import CORS
import speedtest

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas

@app.route('/iniciar_prueba')
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
        return jsonify({
            'download': round(download_speed / 1_000_000, 2),  # Convertir a Mbps
            'upload': round(upload_speed / 1_000_000, 2),      # Convertir a Mbps
            'ping': results['ping']
        })
    except speedtest.SpeedtestException as e:
        # Maneja errores específicos de Speedtest
        return jsonify({'error': f"Error de Speedtest: {str(e)}"}), 500
    except Exception as e:
        # Maneja errores inesperados
        return jsonify({'error': f"Error inesperado: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)