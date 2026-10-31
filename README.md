# BrasaGo: Base de Datos II (2026-II)

Sistema omnicanal de restaurante. Repositorio del trabajo de Base de Datos II de **Elkin Eliecer Aguas Giraldo** (Ingeniería de Sistemas, Universidad de La Guajira).

El detalle paso a paso está en [proceso.md](proceso.md).

## Contenido

| Carpeta | Qué contiene |
|---|---|
| [paso a paso instalacion motores de bd](paso%20a%20paso%20instalacion%20motores%20de%20bd/) | Instalación de MySQL, PostgreSQL, SQL Server y Oracle con Docker |
| [bitacora](bitacora/) | Creación de la base de datos en los cuatro motores |
| [bitacora consultas](bitacora%20consultas/) | Consultas, **procedimientos almacenados** (sección 7), consultas avanzadas y **triggers**, con evidencia |
| [Bitacora Backend iss](Bitacora%20Backend%20iss/) | Bitácora del backend Django (ISS-00 a ISS-25) y verificación multimotor |
| [backend](backend/) | Código del proyecto Django + DRF |
| [Bitacora Frontend](Bitacora%20Frontend/) | Bitácora del frontend Angular (ISS-00 a ISS-11, adaptados a BrasaGo) con evidencias |
| [frontend](frontend/) | Código del frontend Angular 22 + PrimeNG 22 + Tailwind 4 |

## Ejecutar el backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # completar los valores reales
python manage.py migrate
python manage.py test
python manage.py runserver
```

Documentación de la API: `http://127.0.0.1:8000/api/schema/swagger-ui/`.

## Ejecutar el frontend

```bash
cd frontend
npm install
cp src/environments/primeng-license.example.ts src/environments/primeng-license.ts   # licencia Community
cp src/environments/dev-credentials.example.ts src/environments/dev-credentials.ts   # solo para seed_frontend.py
npm start          # http://localhost:4200
npm test
npm run build
```

El backend debe estar corriendo en `http://127.0.0.1:8000`. El inicio de sesión usa `POST /api/auth/login/`.

## Motores

| Motor | Versión |
|---|---|
| MySQL | 8.0 |
| PostgreSQL | 17 |
| SQL Server | 2022 |
| Oracle XE | 21 |
