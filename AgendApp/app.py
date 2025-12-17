import os
from flask import Flask, render_template, request, redirect, flash, url_for
from datetime import datetime

# Importar utilidades
from utils import (
    cargar_reservas, guardar_reservas, normalizar_fecha, normalizar_hora,
    get_horas_ocupadas_por_superposicion, check_new_reservation_overlap,
    format_google_calendar_datetime, enviar_correo_confirmacion, 
    DURACION_SERVICIOS, HORAS_DISPONIBLES
)

app = Flask(__name__)
app.secret_key = 'clave-secreta-segura-debes-cambiarla'

@app.route('/')
def index():
    if os.path.exists(os.path.join(app.root_path, 'templates', 'inicio.html')):
        return render_template('inicio.html')
    return redirect(url_for('form'))

@app.route('/form', methods=['GET', 'POST'])
def form():
    reservas = cargar_reservas()
    hoy = datetime.now().strftime("%Y-%m-%d")

    if request.method == 'POST':
        try:
            # Captura de datos del formulario (coincidiendo con el atributo 'name' del HTML)
            nombre = request.form.get('nombre')
            email = request.form.get('email')
            telefono = request.form.get('telefono')
            tipo_una = request.form.get('tipo_una')
            date = request.form.get('date')
            hora = request.form.get('hora')
            # Sincronizado: El HTML usa name="notes"
            notas = request.form.get('notes', '')

            # Validar que los datos esenciales existan
            if not all([nombre, email, tipo_una, date, hora]):
                flash("❌ Por favor completa todos los campos obligatorios.", "danger")
                return redirect(url_for('form'))

            fecha_normalizada = normalizar_fecha(date)
            hora_normalizada = normalizar_hora(hora)
            duration_minutes = DURACION_SERVICIOS.get(tipo_una, 60)
            
            # Validación de solapamiento
            if check_new_reservation_overlap(reservas, fecha_normalizada, hora_normalizada, duration_minutes):
                flash(f"⛔ La hora {hora_normalizada} ya está ocupada. Elige otra.", "danger")
                return redirect(url_for('form'))

            # Guardar reserva
            timestamp_cita = datetime.now().isoformat()
            nueva_reserva = {
                "nombre": nombre, "email": email, "notas": notas, 
                "tipo_una": tipo_una, "telefono": telefono, "date": fecha_normalizada, 
                "hora": hora_normalizada, "duracion": duration_minutes, "timestamp": timestamp_cita
            }
            reservas.append(nueva_reserva)
            guardar_reservas(reservas) 

            # Generar links y enviar correo
            start, end = format_google_calendar_datetime(fecha_normalizada, hora_normalizada, duration_minutes)
            calendar_link = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text=Cita%20Cocoa%20Nails&dates={start}/{end}"
            cancel_link = url_for('cancelar_cita', timestamp=timestamp_cita, _external=True)

            if not enviar_correo_confirmacion(nueva_reserva, calendar_link, cancel_link):
                flash('⚠️ Reserva guardada, pero falló el envío del correo.', 'warning')

            return redirect(url_for('reserva_exitosa'))

        except Exception as e:
            flash(f"❌ Error al procesar la reserva: {str(e)}", "danger")
            return redirect(url_for('form'))

    # Lógica para mostrar formulario (GET)
    fecha_a_mostrar = request.args.get('date') or hoy
    horas_reservadas = get_horas_ocupadas_por_superposicion(reservas, fecha_a_mostrar)
    horas_libres = [h for h in HORAS_DISPONIBLES if h not in horas_reservadas]
    
    form_data = {
        'nombre': request.args.get('nombre', ''),
        'email': request.args.get('email', ''),
        'notas': request.args.get('notes', ''), # Se lee del campo 'notes'
        'tipo_una': request.args.get('tipo_una', ''),
        'telefono': request.args.get('telefono', ''),
        'hora_previa': request.args.get('hora', '')
    }
    
    return render_template('form.html', hoy=hoy, horas_libres=horas_libres, 
                           fecha_seleccionada=fecha_a_mostrar, form_data=form_data)

@app.route('/reserva_exitosa')
def reserva_exitosa():
    return render_template('reserva_exitosa.html')

@app.route('/cancelar/<timestamp>')
def cancelar_cita(timestamp):
    reservas = cargar_reservas()
    nuevas_reservas = [r for r in reservas if r.get('timestamp') != timestamp]
    if len(nuevas_reservas) < len(reservas):
        guardar_reservas(nuevas_reservas)
        return redirect(url_for('cancelacion_exitosa'))
    flash("Cita no encontrada.", "warning")
    return redirect(url_for('index'))

@app.route('/cancelacion_exitosa')
def cancelacion_exitosa():
    return render_template('cancelacion_exitosa.html')

@app.route('/citas', methods=['GET', 'POST'])
def citas():
    reservas = cargar_reservas()
    citas_cliente = None
    email_buscado = None
    if request.method == 'POST':
        email_buscado = request.form.get('email_cliente', '').strip().lower()
        citas_cliente = [r for r in reservas if r.get('email', '').lower() == email_buscado]
    return render_template('citas.html', citas_cliente=citas_cliente, email_buscado=email_buscado)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)