from flask import Flask, jsonify, render_template
import subprocess

app = Flask(__name__)

def get_wifi_details():
    ssid = None
    password = None

    try:
        # Obtener el SSID de la red conectada
        ssid_output = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces']).decode('utf-8')
        for line in ssid_output.split('\n'):
            if 'SSID' in line:
                ssid = line.split(':')[1].strip()
                break

        # Obtener la contraseña de la red conectada
        if ssid:
            password_output = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', ssid, 'key=clear']).decode('utf-8')
            for line in password_output.split('\n'):
                if 'Key Content' in line:
                    password = line.split(':')[1].strip()
                    break
    except subprocess.CalledProcessError:
        pass

    return ssid, password

@app.route('/')
def index():
    ssid, password = get_wifi_details()
    return render_template('Ajustes.html', ssid=ssid, password=password)

@app.route('/wifi-details')
def wifi_details():
    ssid, password = get_wifi_details()
    return jsonify({'ssid': ssid, 'password': password})

if __name__ == '__main__':
    app.run(debug=True)