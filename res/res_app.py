# app.py
from flask import Flask, request, render_template, flash, redirect, url_for
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import json
import atexit # Para asegurar que el scheduler se apague limpiamente
import pytz # Para manejar zonas horarias

app = Flask(__name__)
app.secret_key = os.urandom(24) # Necesario para flash messages (mensajes temporales)

# --- Configuración de envío de correo para Gmail ---
# Estas variables deben ser configuradas en Azure App Services como "Configuración de la aplicación"
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com') # Servidor SMTP de Gmail
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587)) # Puerto estándar para TLS
EMAIL_SENDER = os.environ.get('EMAIL_SENDER', 'pruebassoftaware@gmail.com') # Tu dirección de correo de Gmail
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'pgvu cgap aeol lssz') # Contraseña de aplicación (generada en Gmail si usas 2FA)

# --- Archivo de datos de Cumpleaños ---
# En un entorno de producción, considera una base de datos como Azure SQL Database o Azure Cosmos DB
BIRTHDAYS_FILE = 'birthdays.json'

def load_birthdays():
    """Carga los datos de cumpleaños desde el archivo JSON."""
    if os.path.exists(BIRTHDAYS_FILE):
        try:
            with open(BIRTHDAYS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error al decodificar {BIRTHDAYS_FILE}. Creando archivo vacío.")
            return []
    return []

def save_birthdays(data):
    """Guarda los datos de cumpleaños en el archivo JSON."""
    with open(BIRTHDAYS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- Función para enviar correo usando SMTP de Gmail ---
def send_email_smtp(to_email, subject, body, cc_emails=None, image_path=None):
    """
    Envía un correo electrónico usando el servidor SMTP de Gmail.
    Args:
        to_email (str): La dirección de correo del destinatario principal.
        subject (str): El asunto del correo.
        body (str): El cuerpo del correo (texto plano).
        cc_emails (list, optional): Una lista de direcciones de correo para copiar (CC).
        image_path (str, optional): Ruta a la imagen a incluir en el correo.
    Returns:
        tuple: (bool, str) - True si el envío fue exitoso, False en caso contrario, y un mensaje.
    """
    try:
        msg = MIMEMultipart('related')
        msg['From'] = EMAIL_SENDER
        msg['To'] = to_email
        msg['Subject'] = subject
        if cc_emails:
            valid_cc_emails = [e.strip() for e in cc_emails if e and e.strip()]
            if valid_cc_emails:
                msg['Cc'] = ", ".join(valid_cc_emails)

        # Cuerpo HTML con referencia al CID de la imagen
        html_content = f"""
        <html>
            <head>
                <style>
                    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
                    
                    body {{
                        font-family: 'Poppins', Arial, sans-serif;
                        margin: 0;
                        padding: 20px;
                        background-color: #f8fafc;
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }}
                    
                    .card {{
                        background-color: #ffffff;
                        border-radius: 20px;
                        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                        overflow: hidden;
                        max-width: 500px;
                        width: 100%;
                    }}
                    
                    .card-header {{
                        background: linear-gradient(135deg, #1e3a8a, #0ea5e9);
                        padding: 25px;
                        text-align: center;
                        color: white;
                    }}
                    
                    .card-header h1 {{
                        margin: 0;
                        font-size: 24px;
                        font-weight: 600;
                        letter-spacing: 0.5px;
                    }}
                    
                    .card-body {{
                        padding: 30px;
                        text-align: center;
                    }}
                    
                    .gif-wrapper {{
                        background-color: #f8fafc;
                        padding: 15px;
                        border-radius: 15px;
                        margin: 20px 0;
                    }}
                    
                    .gif-wrapper img {{
                        max-width: 100%;
                        height: auto;
                        border-radius: 10px;
                        display: block;
                    }}
                    
                    .message {{
                        color: #1e3a8a;
                        font-size: 16px;
                        line-height: 1.6;
                        margin: 20px 0;
                    }}
                    
                    .highlight {{
                        color: #0ea5e9;
                        font-weight: 600;
                    }}
                    
                    .card-footer {{
                        background-color: #f8fafc;
                        padding: 20px;
                        text-align: center;
                        border-top: 1px solid #e2e8f0;
                        color: #64748b;
                        font-size: 13px;
                    }}
                    
                    .emoji {{
                        font-size: 28px;
                        margin: 0 5px;
                    }}
                </style>
            </head>
            <body>
                <div class="card">
                    <div class="card-body">
                        <div class="gif-wrapper">
                            <img src="cid:gifcumple" alt="Feliz Cumpleaños">
                        </div>
                    <div class="card-footer">
                        <p>Sistema de Gestión de Cumpleaños</p>
                    </div>
                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))

        # Adjuntar el GIF local
        if image_path and os.path.exists(image_path):
            with open(image_path, 'rb') as img:
                img_data = img.read()
                image = MIMEImage(img_data)
                image.add_header('Content-ID', '<gifcumple>')
                image.add_header('Content-Disposition', 'inline', filename=os.path.basename(image_path))
                msg.attach(image)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            recipients = [to_email]
            if cc_emails:
                recipients.extend(valid_cc_emails)
            server.sendmail(EMAIL_SENDER, recipients, msg.as_string())

        print(f"Correo enviado a {to_email} con CC a {cc_emails if cc_emails else 'nadie'} por SMTP.")
        return True, "Mensaje enviado exitosamente."
    except Exception as e:
        print(f"Error al enviar el mensaje por SMTP: {e}")
        return False, f"Error al enviar el mensaje por SMTP: {e}"

# --- Tarea programada para enviar cumpleaños automáticamente ---
def send_daily_birthdays():
    """
    Verifica los cumpleaños de hoy y envía correos automáticamente.
    Esta función se ejecuta a la hora programada (4:28 PM hora de Bogotá).
    """
    bogota_tz = pytz.timezone('America/Bogota')
    today_in_bogota = datetime.now(bogota_tz).strftime("%m-%d")

    print(f"[{datetime.now().isoformat()}] Verificando cumpleaños para hoy ({today_in_bogota}) en la zona horaria de Bogotá...")
    
    birthdays_data = load_birthdays()
    
    for person in birthdays_data:
        person_name = person.get("name")
        person_email = person.get("email")
        person_dob = person.get("dob")

        if person_dob == today_in_bogota:
            if person_name and person_email:
                cc_emails = [p.get("email") for p in birthdays_data if p.get("email") != person_email]
                
                subject = f"🎉 ¡Feliz Cumpleaños, {person_name}! 🎉"
                body = f"¡Feliz Cumpleaños {person_name}! Que este día esté lleno de alegría y buenos deseos."
                
                success, msg = send_email_smtp(person_email, subject, body, cc_emails, image_path='felizcumple.gif')
                if success:
                    print(f"[{datetime.now().isoformat()}] Correo de cumpleaños enviado automáticamente a {person_name} ({person_email}) con CC a {len(cc_emails)} personas.")
                else:
                    print(f"[{datetime.now().isoformat()}] FALLO al enviar correo de cumpleaños a {person_name} ({person_email}): {msg}")
            else:
                print(f"[{datetime.now().isoformat()}] Datos incompletos para la persona en cumpleaños: {person}")

# --- Configuración del Scheduler con zona horaria de Bogotá ---
# Se crea un scheduler en segundo plano con la zona horaria especificada.
scheduler = BackgroundScheduler(timezone=pytz.timezone('America/Bogota'))
# Añade la tarea para que se ejecute todos los días a las 4:30 PM (hora de Bogotá)
scheduler.add_job(send_daily_birthdays, 'cron', hour=15, minute=18)
scheduler.start() # Inicia el scheduler

# Registra una función para asegurar que el scheduler se apague limpiamente cuando la aplicación se cierre
atexit.register(lambda: scheduler.shutdown())


# --- Rutas de la aplicación web (interfaz de usuario) ---

@app.route('/')
def index():
    """Ruta para la página principal que redirige a la gestión de cumpleaños."""
    return redirect(url_for('manage_birthdays'))

@app.route('/manage_birthdays', methods=['GET', 'POST'])
def manage_birthdays():
    """Ruta para añadir y ver la lista de cumpleaños."""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        dob_str = request.form['dob'] # Viene como YYYY-MM-DD desde el input type="date"

        if not name or not email or not dob_str:
            flash("Todos los campos son obligatorios.", 'danger')
            return redirect(url_for('manage_birthdays'))

        try:
            # Convertir la fecha de nacimiento a formato MM-DD para el almacenamiento
            dob_obj = datetime.strptime(dob_str, '%Y-%m-%d')
            dob_formatted = dob_obj.strftime('%m-%d')
            
            birthdays_data = load_birthdays()
            
            birthdays_data.append({"name": name, "email": email, "dob": dob_formatted})
            save_birthdays(birthdays_data)
            flash(f"Cumpleaños de {name} añadido exitosamente.", 'success')
        except ValueError:
            flash("Formato de fecha inválido. Asegúrate de usar AAAA-MM-DD.", 'danger')
        except Exception as e:
            flash(f"Error al añadir cumpleaños: {e}", 'danger')
        return redirect(url_for('manage_birthdays'))
    
    # Para solicitudes GET, mostrar la lista de cumpleaños
    birthdays_data = load_birthdays()
    return render_template('manage_birthdays.html', birthdays=birthdays_data)

@app.route('/delete_birthday/<int:index>', methods=['POST'])
def delete_birthday(index):
    """Ruta para eliminar un cumpleaños de la lista."""
    try:
        birthdays_data = load_birthdays()
        if 0 <= index < len(birthdays_data):
            deleted_name = birthdays_data[index]['name']
            birthdays_data.pop(index)
            save_birthdays(birthdays_data)
            flash(f"Cumpleaños de {deleted_name} eliminado exitosamente.", 'success')
        else:
            flash("Índice de cumpleaños no válido.", 'danger')
    except Exception as e:
        flash(f"Error al eliminar cumpleaños: {e}", 'danger')
    return redirect(url_for('manage_birthdays'))

if __name__ == '__main__':
    # Inicializa el archivo birthdays.json con datos de ejemplo si no existe
    if not os.path.exists(BIRTHDAYS_FILE):
        initial_data = [
            {"name": "Ana Sofia", "email": "ana.sofia@example.com", "dob": "06-11"},
            {"name": "Carlos Gomez", "email": "carlos.gomez@example.com", "dob": "06-12"}
        ]
        save_birthdays(initial_data)
        print(f"Archivo {BIRTHDAYS_FILE} creado con datos de ejemplo iniciales.")

    # Cuando se ejecuta localmente, Flask corre en modo debug
    # En producción, Azure App Services usará Gunicorn para ejecutar la app
    app.run(debug=True, use_reloader=False)