from datetime import datetime
from utils.reservations import (
    cargar_reservas, 
    guardar_reservas, 
    DURACION_SERVICIOS, 
    format_google_calendar_datetime, 
    enviar_correo_confirmacion,
    HORAS_DISPONIBLES
)

def obtener_horas_disponibles(reservas, fecha_a_mostrar):
    """Calcula horas libres filtrando las ocupadas y las pasadas."""
    from utils.reservations import get_horas_ocupadas_por_superposicion
    
    horas_ocupadas = get_horas_ocupadas_por_superposicion(reservas, fecha_a_mostrar)
    ahora = datetime.now()
    horas_libres = []

    for h in HORAS_DISPONIBLES:
        h = h.strip()
        if h in horas_ocupadas:
            continue
            
        # Evitar citas en el pasado si la fecha es hoy
        try:
            hora_cita_dt = datetime.strptime(f"{fecha_a_mostrar} {h}", "%Y-%m-%d %H:%M")
            if hora_cita_dt > ahora:
                horas_libres.append(h)
        except:
            continue
            
    return horas_libres

def obtener_horas_libres_reagendar(fecha):
    """Carga las reservas y devuelve las horas disponibles para una fecha específica."""
    reservas = cargar_reservas()
    return obtener_horas_disponibles(reservas, fecha)

def crear_cita(data, host_url):
    """Crea una nueva cita, la guarda y envía el correo de confirmación."""
    reservas = cargar_reservas()
    
    fecha = data.get('date')
    hora = data.get('hora')
    servicio = data.get('tipo_una')
    duracion = DURACION_SERVICIOS.get(servicio, 60)
    
    timestamp = str(datetime.now().timestamp()).replace('.', '')
    nueva_cita = {
        'nombre': data.get('nombre'),
        'email': data.get('email'),
        'telefono': data.get('telefono'),
        'date': fecha,
        'hora': hora,
        'tipo_una': servicio,
        'duracion': duracion,
        'notes': data.get('notes', ''),
        'timestamp': timestamp
    }
    
    reservas.append(nueva_cita)
    guardar_reservas(reservas)
    
    start, end = format_google_calendar_datetime(fecha, hora, duracion)
    cal_link = f"https://www.google.com/calendar/render?action=TEMPLATE&text=Cita+Nails&dates={start}/{end}"
    can_link = f"{host_url}cancelar/{timestamp}"
    
    enviar_correo_confirmacion(nueva_cita, cal_link, can_link)
    
    return {"status": "success"}

def cancelar_cita_por_id(id_cita):
    """Busca y elimina una cita por su timestamp único."""
    reservas = cargar_reservas()
    nuevas_reservas = [r for r in reservas if r.get('timestamp') != id_cita]
    
    if len(nuevas_reservas) < len(reservas):
        guardar_reservas(nuevas_reservas)
        return {"status": "success", "message": "Cita eliminada correctamente"}
    
    return {"status": "error", "message": "No se encontró la cita"}

def reagendar_cita_por_id(id_cita, nueva_fecha, nueva_hora):
    """Busca una cita por ID y actualiza su fecha y hora."""
    reservas = cargar_reservas()
    cita_encontrada = False
    
    for cita in reservas:
        if cita.get('timestamp') == id_cita:
            cita['date'] = nueva_fecha
            cita['hora'] = nueva_hora
            cita_encontrada = True
            break
            
    if cita_encontrada:
        guardar_reservas(reservas)
        return {"status": "success", "message": "Cita reagendada correctamente"}
    
    return {"status": "error", "message": "No se pudo encontrar la cita para reagendar"}