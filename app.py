import json
import schedule
import time
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from threading import Thread

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Necesario para flash messages

def load_clients():
    """Carga la lista de usurio desde un archivo JSON."""
    with open('usuarios.json', 'r') as file:
        return json.load(file)

def save_clients(clients):
    """Guarda la lista de usuario en un archivo JSON."""
    with open('usuarios.json', 'w') as file:
        json.dump(clients, file, indent=2)

def send_birthday_email(client, clients):
    """Envía un correo electrónico de cumpleaños al usuario y a los demás usuarios como CC."""
    sender_email = "pruebassoftaware@gmail.com"
    sender_password = "ncxo vvfy btta"  # Asegúrate de usar una contraseña de aplicación de Google cvtm
    
    receiver_email = client["email"]

    # Crear la lista de CC con todos los correos de los usuarios excepto el del destinatario principal
    cc_emails = [c["email"] for c in clients if c["email"] != receiver_email]

    # Crear el mensaje
    msg = MIMEMultipart("related")
    
    # Modificar el asunto para incluir el nombre de la persona que cumple años
    msg["Subject"] = f"Hoy {client['name']} está de cumpleaños!"  
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Cc"] = ", ".join(cc_emails)  # Agregar los correos en CC

    # Contenido HTML del correo con Tailwind CSS
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="Content-Language" content="es">
    </head>
    <body style="font-family: Arial, sans-serif; background-color: #f3f4f6; margin: 0; padding: 0;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #ffffff; border-radius: 0.5rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); overflow: hidden;">
                <div style="text-align: center; padding: 2rem;">
                    <img src="cid:image1" alt="Tarjeta de Cumpleaños" style="max-width: 100%; height: auto; border-radius: 0.5rem;">
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    part1 = MIMEText(html_content, "html")
    msg.attach(part1)

    # Adjuntar la imagen con Content-ID
    try:
        gif_path = os.path.join(os.path.dirname(__file__), "Cumple.gif")
        with open(gif_path, "rb") as image_file:
            image = MIMEImage(image_file.read())
            image.add_header('Content-ID', '<image1>')
            msg.attach(image)
    except FileNotFoundError:
        print("Error: No se encontró la imagen.")
        return

    # Enviar el correo
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            # Aquí enviamos el correo solo al destinatario y a los CC
            server.sendmail(sender_email, [receiver_email] + cc_emails, msg.as_string())
        print(f"Correo enviado a {client['name']} ({client['email']})")
    except Exception as e:
        print(f"Error al enviar el correo a {client['name']} ({client['email']}): {e}")

def check_birthdays():
    """Verifica si hoy es el cumpleaños de algún cliente y envía el correo correspondiente."""
    clients = load_clients()
    today = datetime.today().strftime("%m-%d")
    for client in clients:
        if client["birthday"] == today:
            send_birthday_email(client, clients)

def run_schedule():
    """Ejecuta el scheduler en un hilo separado."""
    while True:
        schedule.run_pending()
        time.sleep(60)

@app.route('/')
def index():
    """Página principal que muestra la lista de usuarios."""
    clients = load_clients()
    return render_template('index.html', clients=clients)

@app.route('/add_user', methods=['POST'])
def add_user():
    """Agrega un nuevo usuario."""
    name = request.form.get('name')
    email = request.form.get('email')
    birthday = request.form.get('birthday')
    
    if not all([name, email, birthday]):
        flash('Todos los campos son requeridos', 'error')
        return redirect(url_for('index'))
    
    # Convertir la fecha al formato MM-DD
    try:
        birthday_date = datetime.strptime(birthday, '%Y-%m-%d')
        birthday = birthday_date.strftime('%m-%d')
    except ValueError:
        flash('Formato de fecha inválido', 'error')
        return redirect(url_for('index'))
    
    clients = load_clients()
    clients.append({
        "name": name,
        "email": email,
        "birthday": birthday
    })
    save_clients(clients)
    flash('Usuario agregado exitosamente', 'success')
    return redirect(url_for('index'))

@app.route('/delete_user/<int:index>')
def delete_user(index):
    """Elimina un usuario de la lista."""
    clients = load_clients()
    if 0 <= index < len(clients):
        clients.pop(index)
        save_clients(clients)
        flash('Usuario eliminado exitosamente', 'success')
    else:
        flash('Usuario no encontrado', 'error')
    return redirect(url_for('index'))

if __name__ == "__main__":
    # Iniciar el scheduler en un hilo separado
    scheduler_thread = Thread(target=run_schedule)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    # Programar la tarea para que se ejecute diariamente
    schedule.every().day.at("14:36").do(check_birthdays)
    
    # Iniciar la aplicación Flask
    app.run(debug=True)