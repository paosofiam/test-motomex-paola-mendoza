# Motomex API

Backend API en FastAPI para el chatbot de WhatsApp de Motomex. Consume MySQL local vía XAMPP.

## Requisitos previos

- **Python 3.14** instalado y disponible vía `py -3.14` (Windows Python Launcher).
- **XAMPP** corriendo con **MySQL** y **Apache** activos desde el panel de control (necesario para que phpMyAdmin y el API vean la misma base de datos).
- (Opcional) phpMyAdmin abierto en http://localhost/phpmyadmin para inspeccionar la BD.

## Levantar el entorno por primera vez

Desde la raíz del proyecto (`API-server/`), en PowerShell:

```powershell
# 1. Crear el entorno virtual
py -3.14 -m venv .venv

# 2. Activarlo
.\.venv\Scripts\Activate.ps1

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Copiar la plantilla de variables de entorno
Copy-Item .env.example .env
```

Edita `.env` si tus credenciales de MySQL en XAMPP son distintas al default (`root` sin password en `localhost:3306`). El archivo `.env` está en `.gitignore` y no se versiona.

## Iniciar el servidor local

Con el venv activo:

```powershell
uvicorn app.main:app --reload
```

El servidor queda escuchando en http://localhost:8000. Endpoints disponibles:

- http://localhost:8000/health → healthcheck (`{"status":"ok"}`).
- http://localhost:8000/docs → Swagger UI interactivo.
- http://localhost:8000/redoc → documentación ReDoc.

`--reload` reinicia el servidor automáticamente al guardar cambios en archivos `.py`.

## Sesiones siguientes

Solo es necesario activar el venv e iniciar el servidor:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

## Estructura del proyecto

```
API-server/
├── app/
│   ├── main.py            # Instancia FastAPI y endpoints raíz
│   ├── config.py          # Settings (carga .env vía pydantic-settings)
│   ├── database.py        # engine SQLAlchemy, SessionLocal, Base, get_db()
│   ├── models/            # Modelos SQLAlchemy (próxima fase)
│   ├── controllers/       # Routers / controllers FastAPI (próxima fase)
│   └── core/              # Utilidades transversales
├── migrations/            # Migraciones Alembic (próxima fase)
├── seeders/               # Scripts de seed (próxima fase)
├── specs/                 # Contratos y diagrama ER del proyecto
├── .env.example           # Plantilla de variables de entorno
├── requirements.txt
└── README.md
```

## Notas

- El API se conecta al **mismo MySQL** que usa phpMyAdmin de XAMPP, por lo que cualquier dato escrito desde el API es visible inmediatamente desde phpMyAdmin (y viceversa).
- La base de datos `motomex` deberá crearse antes de ejecutar migraciones (próxima fase). Puedes crearla manualmente desde phpMyAdmin con collation `utf8mb4_unicode_ci`.
