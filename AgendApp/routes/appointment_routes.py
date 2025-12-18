import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime

# Importamos los servicios y utilidades necesarios
from services.appointment_service import crear_cita, obtener_horas_disponibles
from utils.reservations import cargar_reservas, guardar_reservas

# Definimos el Blueprint
appointment_bp = Blueprint('appointment', __name__)

@appointment_bp.route('/')
def index():
    # En lugar de render_template('inicio.html'), redirigimos al form
    return redirect(url_for('appointment.form'))

@appointment_bp.route('/form', methods=['GET', 'POST'])
def form():
    hoy = datetime.now().strftime("%Y-%m-%d")
    
    # -------- POST (Crear cita) --------
    if request.method == 'POST':
        try:
            data = request.form.to_dict()
            
            # Pasamos request.host_url para construir el link de cancelación en el correo
            resultado = crear_cita(data, request.host_url) 

            if "error" in resultado:
                flash(f"❌ {resultado['error']}", "danger")
                # Al usar Blueprints, url_for necesita el nombre del blueprint: 'appointment.form'
                return redirect(url_for('appointment.form'))

            return redirect(url_for('appointment.reserva_exitosa'))

        except Exception as e:
            flash(f"❌ Error al procesar la reserva: {str(e)}", "danger")
            return redirect(url_for('appointment.form'))

    # -------- GET (Mostrar formulario) --------
    fecha_a_mostrar = request.args.get('date', hoy)
    reservas = cargar_reservas()
    horas_libres = obtener_horas_disponibles(reservas, fecha_a_mostrar)

    form_data = {
        'nombre': request.args.get('nombre', ''),
        'email': request.args.get('email', ''),
        'notas': request.args.get('notes', ''),
        'tipo_una': request.args.get('tipo_una', ''),
        'telefono': request.args.get('telefono', ''),
        'hora_previa': request.args.get('hora', '')
    }

    return render_template(
        'form.html',
        hoy=hoy,
        horas_libres=horas_libres,
        fecha_seleccionada=fecha_a_mostrar,
        form_data=form_data
    )

@appointment_bp.route('/cancelar/<timestamp>')
def cancelar_cita(timestamp):
    reservas = cargar_reservas()
    total_antes = len(reservas)
    nuevas_reservas = [r for r in reservas if r.get('timestamp') != timestamp]

    if len(nuevas_reservas) < total_antes:
        guardar_reservas(nuevas_reservas)
        return redirect(url_for('appointment.cancelacion_exitosa'))

    flash("Cita no encontrada o ya fue cancelada.", "warning")
    return redirect(url_for('appointment.index'))

@appointment_bp.route('/reserva_exitosa')
def reserva_exitosa(): 
    return render_template('reserva_exitosa.html')

@appointment_bp.route('/cancelacion_exitosa')
def cancelacion_exitosa(): 
    return render_template('cancelacion_exitosa.html')

@appointment_bp.route('/citas', methods=['GET', 'POST'])
def citas():
    reservas = cargar_reservas()
    citas_cliente, email_buscado = None, None

    if request.method == 'POST':
        email_buscado = request.form.get('email_cliente', '').strip().lower()
        citas_cliente = [r for r in reservas if r.get('email', '').lower() == email_buscado]

    return render_template('citas.html', 
                           citas_cliente=citas_cliente, 
                           email_buscado=email_buscado)