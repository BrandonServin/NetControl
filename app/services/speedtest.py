import app.services.speedtest as speedtest

def realizar_speedtest():
    """Ejecuta una prueba de velocidad de internet con Speedtest."""
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download()
        upload_speed = st.upload()
        results = st.results.dict()

        return {
            "download": round(download_speed / 1_000_000, 2),  # Convertir a Mbps
            "upload": round(upload_speed / 1_000_000, 2),  # Convertir a Mbps
            "ping": results["ping"],
        }
    except speedtest.SpeedtestException as e:
        return {"error": f"Error de Speedtest: {str(e)}"}
    except Exception as e:
        return {"error": f"Error inesperado: {str(e)}"}
