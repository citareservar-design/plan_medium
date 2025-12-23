from flask import Blueprint, render_template
from datetime import datetime, timedelta # Añadimos timedelta
from utils.reservations import cargar_reservas

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/agenda')
def agenda():
    reservas = cargar_reservas()
    ahora = datetime.now()
    
    hoy = ahora.strftime("%Y-%m-%d")
    manana = (ahora + timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Filtramos las citas que sean de hoy O de mañana
    citas_proximas = [r for r in reservas if r.get('date') in [hoy, manana]]
    
    # Ordenamos primero por fecha y luego por hora
    citas_proximas.sort(key=lambda x: (x['date'], x['hora']))

    return render_template('admin_agenda.html', citas=citas_proximas, hoy=hoy, manana=manana)