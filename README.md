# 🎂 Sistema de Gestión de Cumpleaños

Un sistema web moderno y elegante para gestionar y celebrar los cumpleaños de los empleados de la empresa. Desarrollado con Flask y TailwindCSS.

## ✨ Características

- 📝 Gestión de usuarios con nombre, correo y fecha de cumpleaños
- 📧 Envío automático de correos electrónicos en el día del cumpleaños
- 🎨 Interfaz moderna y responsiva con TailwindCSS
- 🔍 Búsqueda en tiempo real de usuarios
- 📱 Diseño adaptable a dispositivos móviles
- 🎉 Animaciones y efectos visuales atractivos
- 📊 Paginación de resultados
- 🔔 Notificaciones con SweetAlert2

## 🚀 Tecnologías Utilizadas

- **Backend:**
  - Python 3.x
  - Flask
  - Schedule (para tareas programadas)
  - SMTP (para envío de correos)

- **Frontend:**
  - HTML5
  - TailwindCSS
  - JavaScript
  - Particles.js (efectos visuales)
  - SweetAlert2 (notificaciones)

## 📋 Requisitos Previos

- Python 3.x
- pip (gestor de paquetes de Python)
- Cuenta de correo Gmail para el envío de emails

## 🛠️ Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/gestion-cumpleanos.git
cd gestion-cumpleanos
```

2. Crear y activar un entorno virtual:
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Unix o MacOS:
source venv/bin/activate
```

3. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar las credenciales de correo:
   - Editar el archivo `app.py`
   - Actualizar las variables `sender_email` y `sender_password` con tus credenciales de Gmail
   - Nota: Para `sender_password`, usar una contraseña de aplicación de Google de Gmail

5. Colocar el archivo GIF:
   - Asegurarse de que el archivo `Cumple.gif` esté en el directorio raíz del proyecto

## 🚀 Uso

1. Iniciar el servidor:
```bash
python app.py
```

2. Abrir el navegador y acceder a:
```
http://localhost:5000
```

## 📧 Configuración del Correo

El sistema utiliza Gmail para enviar los correos electrónicos. Para configurarlo:

1. Activar la verificación en dos pasos en tu cuenta de Gmail
2. Generar una contraseña de aplicación:
   - Ir a Configuración de la cuenta de Google
   - Seguridad
   - Contraseñas de aplicación
   - Generar nueva contraseña
3. Usar esta contraseña en el archivo `app.py`

## ⏰ Programación de Tareas

El sistema verifica los cumpleaños diariamente a las 08:00 (8:00 AM). Para modificar este horario:

1. Editar el archivo `app.py`
2. Cambiar la línea:
```python
schedule.every().day.at("08:00").do(check_birthdays)
```

## 📁 Estructura del Proyecto

```
gestion-cumpleanos/
├── app.py              # Aplicación principal
├── requirements.txt    # Dependencias
├── usuarios.json      # Base de datos de usuarios
├── Cumple.gif        # Imagen para correos
└── templates/
    └── index.html    # Plantilla principal
```

## 🤝 Contribuir

Las contribuciones son bienvenidas. Para contribuir:

1. Hacer fork del proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit de tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 😋 No olvides Seguirme o darle estrella. 