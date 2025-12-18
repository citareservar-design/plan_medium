from flask import Blueprint, render_template
from datetime import datetime
from utils.reservations import cargar_reservas

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/agenda')
def agenda():
    reservas = cargar_reservas()
    hoy = datetime.now().strftime("%Y-%m-%d")
    
    # Filtramos las citas de hoy y las ordenamos
    citas_hoy = [r for r in reservas if r.get('date') == hoy]
    citas_hoy.sort(key=lambda x: x['hora'])

    return render_template('admin_agenda.html', citas=citas_hoy, hoy=hoy)