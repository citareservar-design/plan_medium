import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta

# --- Configuración de Rutas Relativas ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, 'data', 'reservas.json')

HORAS_DISPONIBLES = [
    "08:00", "09:00", "10:00", "11:00", "12:00", 
    "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00"
]

DURACION_SERVICIOS = {
    "Semipermanente": 60,
    "Soft Gel": 120,
    "Poly Gel": 120,
    "Base Rubber": 60,
    "Decoración": 60,
}

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_FROM = 'citareservar@gmail.com' 
EMAIL_PASSWORD = 'dren psgm ncqx lrpy' 

# --- Funciones de I/O ---
def cargar_reservas():
    if os.path.exists(JSON_PATH):
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content: return []
                return json.loads(content)
        except (json.JSONDecodeError, Exception) as e:
            print(f"⚠️ Error al cargar: {e}")
            return []
    return []

def guardar_reservas(reservas):
    try:
        os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(reservas, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"❌ Error al guardar reservas: {e}")

# --- Funciones de Utilidad ---
def format_google_calendar_datetime(date_str, time_str, duration_minutes):
    try:
        dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        start = dt.strftime("%Y%m%dT%H%M%S")
        end = (dt + timedelta(minutes=duration_minutes)).strftime("%Y%m%dT%H%M%S")
        return start, end
    except: return "", ""

def get_horas_ocupadas_por_superposicion(reservas, fecha_a_mostrar):
    horas_ocupadas = set()
    reservas_del_dia = [r for r in reservas if r.get("date") == fecha_a_mostrar]
    for r in reservas_del_dia:
        try:
            inicio = datetime.strptime(f"{fecha_a_mostrar} {r['hora']}", "%Y-%m-%d %H:%M")
            duracion = r.get("duracion", 60)
            fin = inicio + timedelta(minutes=duracion)
            for h_disp in HORAS_DISPONIBLES:
                posible = datetime.strptime(f"{fecha_a_mostrar} {h_disp}", "%Y-%m-%d %H:%M")
                if inicio <= posible < fin:
                    horas_ocupadas.add(h_disp)
        except: continue
    return horas_ocupadas

# --- CORREOS ---

def enviar_correo_confirmacion(reserva, calendar_link, cancel_link):
    destinatario = reserva.get('email')
    destinatario_admin = 'diego251644@gmail.com'
    try:
        msg = MIMEMultipart("alternative")
        msg['From'] = f"AgendApp - Confirmación <{EMAIL_FROM}>"
        msg['To'] = destinatario
        msg['cc'] = destinatario_admin
        msg['Subject'] = '✨ ¡Cita Confirmada! - Editar empresa'
        
        html_body = f"""<div style="font-family:sans-serif; padding:20px; background:#f1f5f9;">
            <div style="background:white; border-radius:15px; max-width:500px; margin:auto; border:1px solid #e2e8f0; overflow:hidden;">
                <div style="background:#0ea5e9; padding:20px; text-align:center; color:white;"><h2>Cita Confirmada</h2></div>
                <div style="padding:20px;">
                    <p>Hola <b>{reserva.get('nombre')}</b>, tu cita para <b>{reserva.get('tipo_una')}</b> el día <b>{reserva.get('date')}</b> a las <b>{reserva.get('hora')}</b> está lista.</p>
                </div>
            </div>
        </div>"""
        msg.attach(MIMEText(html_body, 'html'))
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT); server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD); server.send_message(msg); server.quit()
        return True
    except: return False

def enviar_correo_reagendacion(reserva, calendar_link):
    destinatario = reserva.get('email')
    destinatario_admin = 'diego251644@gmail.com'
    try:
        msg = MIMEMultipart("alternative")
        msg['From'] = f"AgendApp - Reagendado <{EMAIL_FROM}>"
        msg['To'] = destinatario
        msg['cc'] = destinatario_admin
        msg['Subject'] = 'Cita Reagendada - Editar empresa'
        html_body = f"""<div style="font-family:sans-serif; padding:20px; background:#fff7ed;">
            <div style="background:white; border-radius:15px; max-width:500px; margin:auto; border:1px solid #fed7aa; overflow:hidden;">
                <div style="background:#f59e0b; padding:20px; text-align:center; color:white;"><h2>Cita Reagendada</h2></div>
                <div style="padding:20px;">
                     <p>Hola <b>{reserva.get('nombre')}</b>,</p>
                    <p>Tu cita fue reprogramada con éxito. Te esperamos en el horario acordado <b>{reserva.get('date')}</b> a las <b>{reserva.get('hora')}</b>.</p>
                    <p style="margin-top:20px; font-size:12px; color:#94a3b8;">Si no fuiste notificado(a) de esta reagendamiento, por favor comunícate con el negocio a través de WhatsApp</p>
                </div>
            </div>
        </div>"""
        msg.attach(MIMEText(html_body, 'html'))
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT); server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD); server.send_message(msg); server.quit()
        return True
    except: return False

def enviar_correo_cancelacion(reserva):
    """Envía correo notificando la CANCELACIÓN definitiva."""
    destinatario = reserva.get('email')
    destinatario_admin = 'diego251644@gmail.com'
    try:
        msg = MIMEMultipart("alternative")
        msg['From'] = f"AgendApp - Cancelación <{EMAIL_FROM}>"
        msg['To'] = destinatario
        msg['cc'] = destinatario_admin
        msg['Subject'] = 'Cita Cancelada - Editar empresa'
        
        html_body = f"""
        <div style="font-family:sans-serif; padding:20px; background:#fef2f2;">
            <div style="background:white; border-radius:15px; max-width:500px; margin:auto; border:1px solid #fecaca; overflow:hidden;">
                <div style="background:#ef4444; padding:20px; text-align:center; color:white;"><h2 style="margin:0;">Cita Cancelada</h2></div>
                <div style="padding:30px; color:#475569;">
                    <p>Hola <b>{reserva.get('nombre')}</b>,</p>
                    <p>Te informamos que la cita programada para el día <b>{reserva.get('date')}</b> ha sido <b>cancelada</b> exitosamente.</p>
                    <div style="background:#f8fafc; padding:15px; border-radius:10px; margin-top:20px;">
                        <p style="margin:0;"><b>Servicio:</b> {reserva.get('tipo_una')}</p>
                    </div>
                    <p style="margin-top:20px; font-size:12px; color:#94a3b8;">Si no fuiste notificado(a) de esta cancelación, por favor comunícate con el negocio a través de WhatsApp</p>
                </div>
            </div>
        </div>"""
        msg.attach(MIMEText(html_body, 'html'))
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT); server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD); server.send_message(msg); server.quit()
        return True
    except: return False