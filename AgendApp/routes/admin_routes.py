from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
from utils.reservations import cargar_reservas

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('usuario')
        pw = request.form.get('password')
        
        # Define aquí tus credenciales
        if user == 'admin' and pw == '12345':
            session['admin_auth'] = True
            return redirect(url_for('admin.agenda'))
        else:
            flash('Acceso Denegado')
            
    return render_template('login.html')

@admin_bp.route('/agenda')
def agenda():
    # Bloqueo: si no hay sesión, rebota al login
    if not session.get('admin_auth'):
        return redirect(url_for('admin.login'))
        
    reservas = cargar_reservas()
    ahora = datetime.now()
    hoy = ahora.strftime("%Y-%m-%d")
    manana = (ahora + timedelta(days=1)).strftime("%Y-%m-%d")
    
    citas_proximas = [r for r in reservas if r.get('date') in [hoy, manana]]
    citas_proximas.sort(key=lambda x: (x['date'], x['hora']))

    return render_template('admin_agenda.html', citas=citas_proximas, hoy=hoy, manana=manana)