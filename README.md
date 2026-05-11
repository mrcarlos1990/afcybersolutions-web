# AFCyber SOLUTIONS

Sitio web corporativo editable para `afcybersolutions.com.do`, desarrollado con Flask, SQLite, SQLAlchemy, Bootstrap 5 y panel de administración protegido.

## Funciones principales

- Página pública moderna, responsive y corporativa.
- Panel admin en `/admin` con login.
- Configuración editable de empresa, colores, modo claro/oscuro, logo, favicon, imágenes, contacto, redes y mapa.
- CRUD para servicios, proyectos, galería y testimonios.
- Administración de mensajes recibidos desde el formulario de contacto.
- Botones de WhatsApp con mensajes automáticos por servicio.
- Upload seguro de imágenes `jpg`, `jpeg`, `png`, `webp`.
- Contraseña hasheada y variables de entorno.
- Archivos listos para GitHub y Render.

## Estructura

```text
.
├── app.py
├── extensions.py
├── models.py
├── requirements.txt
├── Procfile
├── render.yaml
├── .env.example
├── static/
│   ├── css/
│   ├── js/
│   └── uploads/
└── templates/
    ├── public/
    └── admin/
```

## Instalación local

1. Crear entorno virtual:

```bash
python -m venv .venv
```

2. Activar entorno:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Crear archivo `.env` usando `.env.example` como base:

```env
SECRET_KEY=coloca-una-clave-segura
DATABASE_URL=sqlite:///instance/afcyber.db
ADMIN_USERNAME=admin
ADMIN_PASSWORD=coloca-una-contrasena-segura
FLASK_DEBUG=1
```

5. Ejecutar:

```bash
python app.py
```

6. Abrir:

- Web: `http://127.0.0.1:5000`
- Admin: `http://127.0.0.1:5000/admin`

La primera ejecución crea la base de datos, el usuario administrador y contenido inicial.

## Credenciales

El usuario administrador se crea desde:

- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`

Si no configuras `.env`, se usa temporalmente:

- Usuario: `admin`
- Contraseña: `admin12345`

Cambia esas credenciales antes de publicar.

## Despliegue en Render

1. Subir el proyecto a GitHub.
2. Crear un nuevo Web Service en Render.
3. Conectar el repositorio.
4. Usar:

```bash
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

5. Configurar variables:

```env
SECRET_KEY=clave-segura-produccion
DATABASE_URL=sqlite:///instance/afcyber.db
ADMIN_USERNAME=admin
ADMIN_PASSWORD=contrasena-segura
```

`render.yaml` ya incluye una configuración base opcional.

## Notas de edición

- Las imágenes se guardan en `static/uploads`.
- Los colores se aplican dinámicamente desde la base de datos.
- El mapa acepta un iframe de Google Maps o HTML embebido.
- Para iconos de servicios puedes usar nombres de [Lucide Icons](https://lucide.dev/icons/), por ejemplo `shield-check`, `network`, `cctv`, `workflow`.
