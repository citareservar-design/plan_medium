import os # Necesario para leer variables de entorno
from flask import Flask
from dotenv import load_dotenv # Necesario para el .env
from routes.appointment_routes import appointment_bp
from routes.admin_routes import admin_bp

# 1. Cargamos el archivo .env
load_dotenv()

app = Flask(__name__)

# 2. Traemos la clave desde el .env de forma segura
app.secret_key = os.getenv('FLASK_SECRET_KEY')


print(f"--- VARIABLE CARGADA: {app.secret_key} ---")

# Registramos los blueprints
app.register_blueprint(appointment_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')

@app.context_processor
def inject_config():
    from utils.reservations import cargar_config
    return dict(config=cargar_config())

if __name__ == '__main__':
    # host='0.0.0.0' permite que lo veas desde tu celular en la misma red WiFi
    app.run(host='0.0.0.0', port=5000, debug=True)