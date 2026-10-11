# Bitácora de ISS: backend de BrasaGo (Django + DRF)

Registro del avance del backend de **BrasaGo** (sistema omnicanal de restaurante) siguiendo la guía **Backend-2026 · Django + DRF (StoreLab)**. Cada unidad (ISS) resume qué se hizo, qué se adaptó respecto a la guía, cómo se verificó y qué capturas lo respaldan.

| | |
|---|---|
| **Proyecto** | BrasaGo, Proyectos Integradores 2026-II (Desarrollo Web) |
| **Autor** | Elkin Eliecer Aguas Giraldo |
| **Alcance** | Proyecto individual: negocio (ISS-00 a ISS-14), extensión del negocio con seis tablas adicionales y autenticación JWT con RBAC (ISS-15 a ISS-25) |
| **Guía de referencia** | [Aprendizaje ISS-00](https://www.tecnogua.com/academic/site/backend2026/django/aprendizaje/ISS-00-aprendizaje/) y enlaces *Construir* de cada ISS |
| **Unidades documentadas** | ISS-00 a ISS-25 (guía completa) y extensión del negocio |
| **Pruebas** | 178 tests OK en PostgreSQL, MySQL, SQL Server y Oracle |
| **Fecha de cierre** | 11 de octubre de 2026 |


---

## 1. Estado general

| ISS | Tema | Estado | Tests de la unidad | Total acumulado |
|---|---|---|---|---|
| ISS-00 | Entorno y proyecto Django | Bien | `check` limpio |  |
| ISS-01 | Settings y selección del motor | Bien | `check` limpio |  |
| ISS-02 | Apps client, product y sale | Bien | `check` limpio |  |
| ISS-03 | Custom User antes de la primera migración | Bien | 6 (`apps.security`) |  |
| ISS-04 | Modelo Client | Bien |  |  |
| ISS-05 | Product (sin ProductType) | Bien |  |  |
| ISS-06 | Order y OrderDetail | Bien | 5 (`apps.sale`) |  |
| ISS-07 | Serializers y JSON camelCase | Bien | 15 (`client`, `product`, `sale`) | 21 |
| ISS-08 | Client con ModelViewSet | Bien | 8 (`apps.client`) | 26 |
| ISS-09 | Catálogo con ModelViewSet | Bien | 11 (`apps.product`) | 31 |
| ISS-10 | Disponibles con ListAPIView | Bien | 12 (`apps.product`) | 32 |
| ISS-11 | Registro de venta con APIView | Bien | 12 (`apps.sale`) | 38 |
| ISS-12 | Consulta y anulación de ventas | Bien | 16 (`apps.sale`) | 42 |
| ISS-13 | Django Admin | Bien | 4 (`apps.common`) | 46 |
| ISS-14 | OpenAPI y verificación multimotor | Bien | 3 (`apps.common`) | 49 |
| Extensión | Seis tablas de negocio (reservas, insumos, recetas, pagos, domiciliarios, entregas) | Bien | 34 | 83 |
| ISS-15 | RefreshToken | Bien | 8 (`apps.security`) | 91 |
| ISS-16 | Role, RoleUser, Resource y ResourceRole | Bien | 8 (`apps.security`) | 99 |
| ISS-17 | Login OPEN | Bien | 13 (`apps.security`) | 112 |
| ISS-18 | Refresh con rotación | Bien | 10 (`apps.security`) | 122 |
| ISS-19 | Logout | Bien | 10 (`apps.security`) | 132 |
| ISS-20 | Perfil JWT con token | Bien | 11 (`apps.security`) | 143 |
| ISS-21 | HasResourceAccess | Bien | 11 (`apps.security`) | 154 |
| ISS-22 | RBAC sobre el negocio | Bien | 8 (`apps.security`) | 162 |
| ISS-23 | CRUD de la matriz | Bien | 6 (`apps.security`) | 168 |
| ISS-24 | Semilla RBAC y Swagger con Bearer | Bien | 5 | 173 |
| ISS-25 | Pruebas 401 y 403 | Bien | 5 (`apps.security`) | 178 |

La extensión del negocio se hizo entre ISS-14 e ISS-15 (9 de octubre).


---

## 2. Entorno y versiones

| Componente | Versión |
|---|---|
| Python | 3.14 |
| Django | 5.2.17 |
| Django REST Framework | 3.17.2 |
| djangorestframework-camel-case | 1.4.2 |
| djangorestframework-simplejwt | 5.5.1 |
| drf-spectacular | 0.30.0 |
| django-cors-headers | 4.9.0 |
| Motores de base de datos | PostgreSQL 17 (psycopg 3.3.6), MySQL 8.0 (mysqlclient 2.3.0), SQL Server 2022 (mssql-django 2.0.0, ODBC Driver 18) y Oracle XE 21 (oracledb 26.0.1), en Docker; se elige con `DB_ENGINE` |
| Sistema | Ubuntu sobre WSL (Windows) |

La guía fija Python 3.12, pero el proyecto se ejecutó con 3.14.

---

## 3. Decisiones de diseño y adaptaciones frente a la guía

| Tema | Guía (StoreLab) | BrasaGo | Motivo |
|---|---|---|---|
| Base de datos de Django | única | `brasago_django` (Django) y `brasago` (tablas del diagrama, scripts SQL) | Evitar choques de nombres de tabla |
| Nombres en la base | inglés | tablas y columnas en español con `db_table` / `db_column` | Coincidir con el diagrama |
| Estado del registro | `status` | atributo `status` en Python, columna `is_active` (`ACTIVE` / `INACTIVE`, por defecto `ACTIVE`) | Convención del curso y del diagrama |
| Tipo de producto y stock | `ProductType`, `stock` | no existen | No están en el diagrama de BrasaGo |
| Impuestos y descuentos | `tax`, `discounts` | no existen; `total = subtotal` | No están en el diagrama |
| Entidades | `Client`, `Product`, `Sale`, `ProductSale` | `Client`, `Product`, `Order`, `OrderDetail`, más `Branch` y `DiningTable` (app `venue`) | El pedido requiere sede y mesa |
| Rutas de la API | `/api/clients/`, `/api/products/`, `/api/sales/` | `/api/clientes/`, `/api/productos/`, `/api/pedidos/` | La narrativa nombra los recursos en español |
| Bloqueos de filas | `select_for_update` | sin bloqueos | Solo servían para el stock |
| Anulación de pedido | desactiva y devuelve stock | desactiva el pedido y sus detalles y marca `CANCELADO` | No hay stock |
| Reglas de mesa y canal | no existen | mesa obligatoria solo en canal `MESA`, y de la misma sede | Regla propia, por confirmar |
| Cliente del pedido | obligatorio | opcional | Una compra en mesa puede no tener cliente registrado |
| Autenticación | Refresh token en tabla propia | Refresh aleatorio guardado solo como `token_hash` SHA-256 (nunca en claro), con `family_id`, rotación y revocación de la familia ante reutilización | Seguridad; el diagrama lo llama `is_valid` y aquí es el estado `ACTIVE`/`INACTIVE` |
| Autorización | Permiso por rol | `HasResourceAccess` con la cadena `User → RoleUser → Role → ResourceRole → Resource` (todos activos), por método y ruta (`resolver_match.route`); denegar por defecto | Coincidir con el RBAC del diagrama |
| Perfil | Dentro de la matriz | `/api/auth/profile/` solo exige JWT y queda fuera de la matriz; `login`, `refresh` y `logout` también (84 recursos sembrados) | Todo usuario autenticado debe ver su perfil |
| Tablas de negocio | solo StoreLab | Se añaden `reservas`, `insumos`, `recetas_insumos`, `pagos`, `domiciliarios` y `entregas` | Cambio de alcance: completar el diagrama |
| Tablas de auditoría | no existen | No se modelan (el diagrama las muestra); se resolverían con triggers en la base si el profesor las exige | Fuera del alcance de la guía |
| Nombres de campos | inglés | Python en inglés y columnas/tablas en español con `db_column` / `db_table` | Coincidir con el diagrama |
| `grant_all_access` | no existe | Comando solo para desarrollo que da el rol `ADMIN` con todos los recursos a un usuario | Poder operar mientras se siembra la matriz |

---

## 4. Estructura actual

```
backend/
├── manage.py
├── requirements.txt
├── .env / .env.example / .gitignore
├── config/
│   ├── settings/__init__.py      (database_from_environ, REST_FRAMEWORK, CORS)
│   ├── project_python.py
│   ├── urls.py                   (admin/ y api/)
│   └── wsgi.py / asgi.py
└── apps/
    ├── common/      status, models, viewsets, factories, testing, test_admin, test_openapi
    ├── security/    User, RefreshToken, Role, RoleUser, Resource, ResourceRole,
    │                auth_views, rbac_views, permissions, authentication, tokens,
    │                comandos seed_rbac y grant_all_access, tests
    ├── client/      models, serializers, views, urls, admin, tests
    ├── product/     Product, Supply, RecipeItem (+ inventory_api), tests
    ├── venue/       Branch, DiningTable, Reservation, serializers, views, urls, admin, tests
    ├── sale/        Order, OrderDetail, Payment, managers, serializers, views, urls, admin, tests
    └── delivery/    Courier, Delivery, serializers, views, urls, admin, tests
```

### Tablas del modelo (base `brasago_django`)

`users`, `clientes`, `productos`, `sedes`, `mesas`, `pedidos`, `detalles_pedidos`, `reservas`, `insumos`, `recetas_insumos`, `pagos`, `domiciliarios`, `entregas`, `refresh_tokens`, `roles`, `role_users`, `resources`, `resource_roles` y las tablas propias de Django (`auth_*`, `django_*`).

### API disponible

| Método | Ruta | ISS | Descripción |
|---|---|---|---|
| GET, POST | `/api/clientes/` | 08 | Listar y crear clientes |
| GET, PUT, PATCH, DELETE | `/api/clientes/<id>/` | 08 | Consultar, actualizar y dar de baja (lógica) |
| GET, POST | `/api/productos/` | 09 | Listar y crear productos |
| GET, PUT, PATCH, DELETE | `/api/productos/<id>/` | 09 | Consultar, actualizar y dar de baja (lógica) |
| GET | `/api/productos/disponibles/` | 10 | Productos activos |
| GET, POST | `/api/pedidos/` | 11, 12 | Listar pedidos y registrar uno nuevo |
| GET, DELETE | `/api/pedidos/<id>/` | 12 | Consultar y anular |
| PATCH | `/api/pedidos/<id>/estado/` | Ext. | Cambiar el estado del pedido |
| CRUD | `/api/reservas/`, `/api/insumos/`, `/api/recetas/`, `/api/domiciliarios/`, `/api/entregas/` | Ext. | Extensión del negocio (baja lógica) |
| GET, POST | `/api/pagos/` | Ext. | Registrar y consultar pagos |
| POST | `/api/auth/login/` | 17 | Iniciar sesión (abierto) |
| POST | `/api/auth/refresh/` | 18 | Renovar con rotación (abierto) |
| POST | `/api/auth/logout/` | 19 | Cerrar sesión (abierto) |
| GET, PATCH | `/api/auth/profile/` | 20 | Perfil propio (solo JWT) |
| CRUD | `/api/users/`, `/api/roles/`, `/api/role-users/`, `/api/resources/`, `/api/resource-roles/` | 23 | Matriz RBAC |
| GET | `/api/schema/`, `/api/schema/swagger-ui/`, `/api/schema/redoc/` | 14 | OpenAPI, Swagger UI y ReDoc |

Desde ISS-22 las rutas de negocio exigen JWT y permiso en la matriz (401 sin identidad, 403 sin permiso); `GET /api/productos/disponibles/` y las rutas de autenticación siguen abiertas.

---

## 5. Bitácora por ISS


### ISS-00: Entorno y proyecto Django

[Guía (Construir)](https://www.tecnogua.com/academic/site/backend2026/django/manual/01-ISS-00-entorno-y-proyecto-django/)

**Objetivo.** Dejar listo el entorno de trabajo: entorno virtual, Django fijado a una versión, proyecto `config` y archivos base del repositorio.

**Qué se hizo**

- Entorno virtual `.venv` e instalación de Django `5.2.17`.
- `django-admin startproject config .` y `requirements.txt` con `pip freeze`.
- `.gitignore` con `.venv/`, `__pycache__/`, `.env`, `db.sqlite3`, `staticfiles/`, `media/`, entre otros.

**Verificación**

- `python -m django --version` → `5.2.17`.
- `python manage.py check` → *System check identified no issues*.
- En la guía quedaron en PASS AC-00-02 (archivos del proyecto) y AC-00-03 (ausencia de modelos de negocio).


#### Registro visual ISS-00

**`iss-00-2.png`**: Creación del `.gitignore` (`.venv/`, `__pycache__/`, `.env`, `db.sqlite3`, etc.) con la guía abierta en el navegador. 13:00.

![iss-00-2.png](Reguistro%20visual/ISS-00/iss-00-2.png)

**`iss-00-3.png`**: `python -m django --version` y `manage.py check` sin incidencias. En la guía se ven AC-00-02 y AC-00-03 en PASS. 13:01.

![iss-00-3.png](Reguistro%20visual/ISS-00/iss-00-3.png)

**`iss-00.png`**: Entorno virtual `.venv`, instalación de Django 5.2.17, `startproject config .`, `pip freeze > requirements.txt` y `python -m django --version` (5.2.17). Sáb 3-oct 12:58.

![iss-00.png](Reguistro%20visual/ISS-00/iss-00.png)


---


### ISS-01: Settings y selección del motor

[Guía (Construir)](https://www.tecnogua.com/academic/site/backend2026/django/manual/02-ISS-01-settings-y-seleccion-del-motor/)

**Objetivo.** Separar la configuración por paquete y elegir el motor de base de datos desde variables de entorno.

**Qué se hizo**

- Drivers instalados: `python-dotenv 1.2.3`, `psycopg[binary] 3.3.6` (PostgreSQL), `mysqlclient 2.3.0` (MySQL), `mssql-django 2.0.0` (SQL Server, con `pyodbc`) y `oracledb 26.0.1` (Oracle).
- `config/settings/__init__.py` con `database_from_environ()`, que arma `DATABASES` según `DB_ENGINE` (`postgresql`, `mysql`, `mssql`, `oracle`) y falla con `ImproperlyConfigured` si el motor es inválido o falta una variable.
- `.env.example` (plantilla) y `.env` (valores locales, fuera de Git). Motor activo: `postgresql`.
- `config/project_python.py` (`use_project_python()`): relanza `manage.py` con el Python de `.venv` aunque se invoque con `python3`.
- `manage.py` y `config/wsgi.py` cargan `.env` con `load_dotenv()`.
- Idioma `es`, zona horaria `America/Bogota`, `DEFAULT_AUTO_FIELD = BigAutoField`.

**Verificación.** Los tests de selección de motor se ejecutan en ISS-03 (6 tests).


#### Registro visual ISS-01

**`iss-01-2.png`**: Instalación de `mysqlclient 2.3.0` (se construye el wheel) y arranque de la instalación de `mssql-django 2.0.0`.

![iss-01-2.png](Reguistro%20visual/ISS-01/iss-01-2.png)

**`iss-01-3.png`**: Fin de la instalación de `mssql-django 2.0.0` y sus dependencias (`pyodbc`, `azure-identity`, etc.).

![iss-01-3.png](Reguistro%20visual/ISS-01/iss-01-3.png)

**`iss-01-4.png`**: Instalación de `oracledb 26.0.1` y `pip freeze > requirements.txt`. 13:15.

![iss-01-4.png](Reguistro%20visual/ISS-01/iss-01-4.png)

**`iss-01-5.png`**: Se crea `config/settings/` y los archivos `.env.example` y `.env` (motor `postgresql`, base `brasago`). 13:28.

![iss-01-5.png](Reguistro%20visual/ISS-01/iss-01-5.png)

**`iss-01-6.png`**: `config/settings/__init__.py`: funciones de configuración por motor (`_mysql`, `_mssql`, `_oracle`). 13:36.

![iss-01-6.png](Reguistro%20visual/ISS-01/iss-01-6.png)

**`iss-01-7.png`**: Resto de `settings`: `MIDDLEWARE`, `TEMPLATES`, `DATABASES = database_from_environ(os.environ)`, validadores, idioma `es` y zona `America/Bogota`. 13:39.

![iss-01-7.png](Reguistro%20visual/ISS-01/iss-01-7.png)

**`iss-01-8.png`**: `config/project_python.py` con `use_project_python()`, que relanza el comando con el Python de `.venv`. 13:40.

![iss-01-8.png](Reguistro%20visual/ISS-01/iss-01-8.png)

**`iss-01-9.png`**: Nuevo `manage.py`: usa `use_project_python()` y carga `.env` con `load_dotenv()`. 13:44.

![iss-01-9.png](Reguistro%20visual/ISS-01/iss-01-9.png)

**`iss-01-10.png`**: Nuevo `config/wsgi.py` que carga `.env` antes de crear la aplicación. 13:45.

![iss-01-10.png](Reguistro%20visual/ISS-01/iss-01-10.png)

**`iss-01.png`**: Árbol del proyecto y activación del entorno; instalación de `python-dotenv 1.2.3` y `psycopg[binary] 3.3.6`.

![iss-01.png](Reguistro%20visual/ISS-01/iss-01.png)


---


### ISS-02: Apps client, product y sale

[Guía (Construir)](https://www.tecnogua.com/academic/site/backend2026/django/manual/03-ISS-02-apps-client-product-y-sale/)

**Objetivo.** Crear las apps raíz dentro de `apps/` con una etiqueta explícita.

**Qué se hizo**

- `python manage.py startapp client|product|sale apps/<app>` y `apps/__init__.py`.
- `apps.py` de cada app con `name = "apps.<app>"`, `label` y `default_auto_field = BigAutoField`.
- Apps registradas en `INSTALLED_APPS` dentro de `config/settings/__init__.py`.

**Verificación**

- `manage.py check` sin incidencias.
- `manage.py showmigrations`: `client`, `product` y `sale` sin migraciones (todavía no hay modelos).


#### Registro visual ISS-02

**`iss-02-2.png`**: Creación de `apps/__init__.py`. 14:07.

![iss-02-2.png](Reguistro%20visual/ISS-02/iss-02-2.png)

**`iss-02-3.png`**: `apps.py` de las tres apps con `name = "apps.<app>"` y `label` explícito. 14:10.

![iss-02-3.png](Reguistro%20visual/ISS-02/iss-02-3.png)

**`iss-02-4.png`**: Reescritura de `config/settings/__init__.py` (se ve su parte final) para dejar el proyecto con las apps registradas. 14:15.

![iss-02-4.png](Reguistro%20visual/ISS-02/iss-02-4.png)

**`iss-02-5.png`**: `manage.py check` sin incidencias y `showmigrations`: `client`, `product` y `sale` aparecen sin migraciones. 14:17.

![iss-02-5.png](Reguistro%20visual/ISS-02/iss-02-5.png)

**`iss-02.png`**: `startapp` de `client`, `product` y `sale` dentro de `apps/`. 14:05.

![iss-02.png](Reguistro%20visual/ISS-02/iss-02.png)


---


### ISS-03: Custom User antes de la primera migración

[Guía (Construir)](https://www.tecnogua.com/academic/site/backend2026/django/manual/04-ISS-03-custom-user-antes-de-la-primera-migracion/)

**Objetivo.** Definir el usuario personalizado **antes** del primer `migrate`, porque cambiar `AUTH_USER_MODEL` después obliga a borrar tablas.

**Qué se hizo**

- App `common` con `status.py`: `RecordStatus` (`ACTIVE` / `INACTIVE`).
- App `security` con el modelo `User` (basado en `AbstractUser`), correo único, `status`, `created_at`, `updated_at` y `StoreUserManager`.
- `AUTH_USER_MODEL = "security.User"` en `settings`.
- Se aplica `security.0001_initial` junto con las migraciones de `admin`, `auth`, `contenttypes` y `sessions`.

**Verificación.** `manage.py test apps.security`: **6 tests OK** (selección de motor: cuatro motores, motor inválido y variable faltante).


#### Registro visual ISS-03

**`iss-03-2.png`**: `apps/security/apps.py` con `SecurityConfig` (label `security`). 14:26.

![iss-03-2.png](Reguistro%20visual/ISS-03/iss-03-2.png)

**`iss-03-3.png`**: Modelo `User` personalizado (`AbstractUser`) y `StoreUserManager`: correo único, `status`, `created_at`, `updated_at`. 14:29.

![iss-03-3.png](Reguistro%20visual/ISS-03/iss-03-3.png)

**`iss-03-4.png`**: Edición de `config/settings/__init__.py` en `nano`: se declara `AUTH_USER_MODEL = "security.User"` antes de la primera migración.

![iss-03-4.png](Reguistro%20visual/ISS-03/iss-03-4.png)

**`iss-03-5.png`**: Parte final de los tests de selección de motor (`DatabaseSelectionTests`): PostgreSQL, MySQL, SQL Server, Oracle, motor inválido y variable faltante. 14:36.

![iss-03-5.png](Reguistro%20visual/ISS-03/iss-03-5.png)

**`iss-03-6.png`**: `migrate` (se aplica `security.0001_initial`) y `manage.py test apps.security.tests.DatabaseSelectionTests`: 6 tests OK. 14:41.

![iss-03-6.png](Reguistro%20visual/ISS-03/iss-03-6.png)

**`iss-03-7.png`**: `manage.py test apps.security`: 6 tests OK. 14:44.

![iss-03-7.png](Reguistro%20visual/ISS-03/iss-03-7.png)

**`iss-03.png`**: Se crea `apps/common/` con `status.py` (`RecordStatus`: ACTIVE / INACTIVE). 14:24.

![iss-03.png](Reguistro%20visual/ISS-03/iss-03.png)


---


### ISS-04: Modelo Client

**Objetivo.** Primer modelo de negocio, con base abstracta reutilizable.

**Qué se hizo**

- `apps/common/models.py`: `TimeStampedModel` (`created_at`, `updated_at`) y `BrasaGoModel` (campo `status` + método para construir la restricción CHECK del estado).
- `Client` y migración `client.0001_initial` (captura de la primera versión, tomada de la guía).
- **Alineación con el diagrama de BrasaGo**, hecha después de comparar la tabla real con el diagrama:
  - tabla `clientes` con `tipo_documento`, `numero_documento` (único), `nombre`, `telefono`, `email` (sin unicidad) y sin `address`;
  - el estado se guarda en la columna `is_active` como texto `ACTIVE` / `INACTIVE` con valor por defecto `ACTIVE`, mediante `db_column`;
  - `User` incorpora `avatar` y también guarda el estado en `is_active`; `is_active` pasó a ser una propiedad que se deriva de `status`.
- Django pasó a trabajar en una base propia, `brasago_django`, para no mezclarse con las tablas del diagrama que están en `brasago` (ver *Incidencias*).

**Verificación.** `\d clientes` y `\d users` en PostgreSQL coinciden con el diagrama; `makemigrations --check` sin cambios.


#### Registro visual ISS-04

**`iss-04-2.png`**: Primera versión del modelo `Client` (`apps/client/models.py`), tomada de la guía. 16:41.

![iss-04-2.png](Reguistro%20visual/ISS-04/iss-04-2.png)

**`iss-04-3.png`**: `makemigrations client` y `migrate`: se aplica `client.0001_initial`. 16:43.

![iss-04-3.png](Reguistro%20visual/ISS-04/iss-04-3.png)

**`iss-04.png`**: `apps/common/models.py` con `TimeStampedModel` y `BrasaGoModel` (estado + restricción reutilizable). Dom 4-oct 16:40.

![iss-04.png](Reguistro%20visual/ISS-04/iss-04.png)


---


### ISS-05: Product (adaptación de ProductType y Product)

**Objetivo.** Publicar el catálogo de productos.

**Adaptación.** El diagrama de BrasaGo no incluye tipo de producto ni stock, así que esta unidad se reduce a `Product`.

**Qué se hizo**

- Tabla `productos`: `sku` (único), `nombre`, `descripcion`, `precio`, estado y marcas de tiempo, con `db_column` en español.
- Restricciones: `productos_is_active_valid` y `productos_precio_non_neg` (`precio >= 0`).
- Se quitó la unicidad del nombre: solo el `sku` es único.
- La migración se regeneró con las columnas finales (captura de 17:36). La captura `iss-05-2.png` corresponde a un intento anterior del mismo día con `--fake-initial`.

**Verificación.** `\d productos` en PostgreSQL con `nombre`, `descripcion`, `precio` y un único índice único (`sku`); `makemigrations --check` sin cambios.


#### Registro visual ISS-05

**`iss-05-2.png`**: `migrate product --fake-initial`: la migración se marca como `FAKED` y `showmigrations` la muestra aplicada. Captura previa del mismo día, 17:03.

![iss-05-2.png](Reguistro%20visual/ISS-05/iss-05-2.png)

**`iss-05.png`**: `apps/product/models.py`: `Product` alineado al diagrama (`sku`, `nombre`, `descripcion`, `precio`, restricciones). 17:36.

![iss-05.png](Reguistro%20visual/ISS-05/iss-05.png)


---


### ISS-06: Sale y ProductSale → Order y OrderDetail

[Guía (Construir)](https://www.tecnogua.com/academic/site/backend2026/django/manual/07-ISS-06-sale-y-productsale/)

**Objetivo.** Modelar el pedido y su detalle con precio histórico y llaves foráneas restrictivas.

**Adaptación a BrasaGo**

| Guía | BrasaGo |
|---|---|
| `Sale` (`sales`) | `Order` (`pedidos`) con `canal`, `estado`, sede, mesa opcional y cliente opcional |
| `ProductSale` (`product_sales`) | `OrderDetail` (`detalles_pedidos`) |
| `tax`, `discounts` | no existen en el diagrama; `total = subtotal` |
| `void()` devuelve stock | `void()` desactiva el pedido y sus detalles y marca `estado = CANCELADO` (no hay stock) |
| (no existe) | app nueva `venue`: `Branch` (`sedes`) y `DiningTable` (`mesas`) |

**Qué se hizo**

- `apps/venue/models.py`, `apps/sale/models.py` y `apps/sale/managers.py` (`OrderQuerySet` / `OrderManager`).
- Todas las llaves foráneas con `on_delete=RESTRICT`; el total del detalle se calcula en `save()` como `unit_price × quantity`.
- Restricciones CHECK: estado, canal, estado del pedido, montos no negativos y cantidad ≥ 1.
- Primera versión del modelo y, después de leer la guía, ajuste a sus criterios (se reinició la migración de `sale`).

**Criterios de aceptación (adaptados)**

| AC | Verificación |
|---|---|
| AC-06-01: existen las dos tablas | `\d pedidos` y `\d detalles_pedidos` |
| AC-06-02: llaves foráneas con `RESTRICT` | `test_foreign_keys_restrict_delete` |
| AC-06-03: total de línea = cantidad × precio | `test_total_is_quantity_times_unit_price` |
| AC-06-04: sin `ManyToManyField` | `test_no_many_to_many_on_product` |
| Precio histórico | `test_historical_price_is_preserved` |

**Resultado.** `manage.py test apps.sale`: **5 tests OK**; `makemigrations --check` sin cambios.


#### Registro visual ISS-06

**`iss-06-1.png`**: Se crea la app `venue` (`startapp` y `apps.py` con `VenueConfig`). 17:40.

![iss-06-1.png](Reguistro%20visual/ISS-06/iss-06-1.png)

**`iss-06-2.png`**: `manage.py check` y `apps/venue/models.py` con `Branch` (`sedes`) y `DiningTable` (`mesas`).

![iss-06-2.png](Reguistro%20visual/ISS-06/iss-06-2.png)

**`iss-06-3-parte-1.png`**: Primera versión de `apps/sale/models.py` (1/2): `Order` con canales, estados y llaves foráneas. 17:43.

![iss-06-3-parte-1.png](Reguistro%20visual/ISS-06/iss-06-3-parte-1.png)

**`iss-06-3-parte-2.png`**: Primera versión de `apps/sale/models.py` (2/2): restricciones de `Order` y modelo `OrderDetail`.

![iss-06-3-parte-2.png](Reguistro%20visual/ISS-06/iss-06-3-parte-2.png)

**`iss-06-4.png`**: `makemigrations` de `venue` y `sale`, `migrate`, `makemigrations --check` y comienzo de `\d pedidos`.

![iss-06-4.png](Reguistro%20visual/ISS-06/iss-06-4.png)

**`iss-06-5.png`**: Estructura real en PostgreSQL: `\d pedidos` (FK a `clientes`, `mesas` y `sedes`, restricciones CHECK) y comienzo de `\d detalles_pedidos`.

![iss-06-5.png](Reguistro%20visual/ISS-06/iss-06-5.png)

**`iss-06-6.png`**: Ajuste a la guía: se borra la migración de `sale`, se crea `managers.py` (`OrderQuerySet` / `OrderManager`) y empieza el nuevo `models.py`.

![iss-06-6.png](Reguistro%20visual/ISS-06/iss-06-6.png)

**`iss-06-7.png`**: Continuación de `models.py`: `Order.void()`, `OrderDetail` con `on_delete=RESTRICT` y cantidad validada.

![iss-06-7.png](Reguistro%20visual/ISS-06/iss-06-7.png)

**`iss-06-8.png`**: `apps/sale/tests.py` (`OrderDetailTests`, parte 1). 17:58.

![iss-06-8.png](Reguistro%20visual/ISS-06/iss-06-8.png)

**`iss-06-9.png`**: Fin de los tests (llave foránea `RESTRICT`, sin `ManyToMany`, `void()`), `makemigrations sale` con las restricciones nuevas y `migrate`.

![iss-06-9.png](Reguistro%20visual/ISS-06/iss-06-9.png)

**`iss-06-10.png`**: `migrate` OK, `makemigrations --check` sin cambios, `manage.py test apps.sale`: 5 tests OK; `\d detalles_pedidos`.

![iss-06-10.png](Reguistro%20visual/ISS-06/iss-06-10.png)


---


### ISS-07: Serializers y JSON camelCase

[Guía (Construir)](https://www.tecnogua.com/academic/site/backend2026/django/manual/08-ISS-07-serializers-y-json-camelcase/)

**Objetivo.** Exponer los modelos como JSON en camelCase.

**Qué se hizo**

- Paquetes: `djangorestframework 3.17.2`, `djangorestframework-camel-case 1.4.2` y `django-cors-headers 4.9.0`.
- `settings`: `rest_framework` y `corsheaders` en `INSTALLED_APPS`, `CorsMiddleware`, `CORS_ALLOW_ALL_ORIGINS` (desde `.env`) y bloque `REST_FRAMEWORK` con renderer y parsers camelCase (permiso `AllowAny` temporal hasta la fase de autenticación).
- `ClientSerializer`: correo en minúsculas, vacíos a `null`, nombre de al menos 2 caracteres.
- `ProductSerializer`: precio mínimo 0 (responde 400 en lugar de un error de base de datos).
- `OrderSerializer` y `OrderDetailSerializer` (solo lectura): `branchName`, `clientName`, `tableName` y `details` anidados.
- Tests: `test_serializers.py` en `client`, `product` y `sale`.
- Los dos tests heredados de `apps/product/tests.py` fallaron porque esperaban reglas de la guía (estado `INACTIVE` por defecto y nombre único); se reemplazaron por tests con las reglas de BrasaGo.

**Criterios de aceptación (adaptados)**

| AC | Verificación |
|---|---|
| AC-07-01: JSON con `createdAt` y sin `created_at` | `test_json_uses_camel_case` (cliente y producto) |
| AC-07-02: correo normalizado | `test_email_is_normalized` |
| AC-07-03 (adaptado): el pedido informa `branchName`, `clientName` y `details` | `test_order_exposes_names_and_details` |

**Resultado.** `apps.client apps.product apps.sale`: 15 tests OK; `manage.py test`: **21 tests OK**.


#### Registro visual ISS-07

**`iss-07-2.png`**: Entorno activado e instalación de `djangorestframework 3.17.2`, `djangorestframework-camel-case 1.4.2` y `django-cors-headers 4.9.0`.

![iss-07-2.png](Reguistro%20visual/ISS-07/iss-07-2.png)

**`iss-07-3.png`**: Script de Python que agrega `rest_framework`, `corsheaders`, el middleware de CORS y el bloque `REST_FRAMEWORK` a `settings`. 15:23.

![iss-07-3.png](Reguistro%20visual/ISS-07/iss-07-3.png)

**`iss-07-4.png`**: `apps/client/serializers.py` (`ClientSerializer`).

![iss-07-4.png](Reguistro%20visual/ISS-07/iss-07-4.png)

**`iss-07-5.png`**: `apps/product/serializers.py` (`ProductSerializer`). 15:28.

![iss-07-5.png](Reguistro%20visual/ISS-07/iss-07-5.png)

**`iss-07-6.png`**: `apps/sale/serializers.py` (`OrderDetailSerializer` y `OrderSerializer`).

![iss-07-6.png](Reguistro%20visual/ISS-07/iss-07-6.png)

**`iss-07-7.png`**: `apps/client/test_serializers.py`. 15:29.

![iss-07-7.png](Reguistro%20visual/ISS-07/iss-07-7.png)

**`iss-07-8.png`**: `apps/product/test_serializers.py`. 15:30.

![iss-07-8.png](Reguistro%20visual/ISS-07/iss-07-8.png)

**`iss-07-9.png`**: `apps/sale/test_serializers.py`. 15:31.

![iss-07-9.png](Reguistro%20visual/ISS-07/iss-07-9.png)

**`iss-07-10.png`**: Copia de seguridad de `apps/product/tests.py` y reescritura con tests de modelo adaptados a BrasaGo.

![iss-07-10.png](Reguistro%20visual/ISS-07/iss-07-10.png)

**`iss-07.png`**: Reescritura de `apps/sale/managers.py` con `OrderQuerySet` y `OrderManager`. Lun 5-oct 15:13.

![iss-07.png](Reguistro%20visual/ISS-07/iss-07.png)

**`test_default_status_and_type_restriction.png`**: Contenido original de `apps/product/tests.py`: esperaba estado `INACTIVE` por defecto y nombre de producto único. Esos dos tests fallaron al verificar ISS-07 y se reemplazaron.

![test_default_status_and_type_restriction.png](Reguistro%20visual/ISS-07/test_default_status_and_type_restriction.png)


---


### ISS-08: Client con ModelViewSet

[Guía (Construir)](https://www.tecnogua.com/academic/site/backend2026/django/manual/09-ISS-08-client-con-modelviewset/)

**Objetivo.** Primer recurso HTTP con CRUD y baja lógica.

**Qué se hizo**

- `ClientViewSet` (`ModelViewSet`), filtro `?status=ACTIVE|INACTIVE` y baja lógica en `perform_destroy` (la fila no se borra).
- Router `clientes` y `path("api/", include("apps.client.urls"))` en `config/urls.py`.
- `apps/client/tests.py` con 5 tests de API (cuerpos enviados en camelCase).

**Criterios de aceptación (adaptados)**

| AC | Verificación |
|---|---|
| POST válido → 201, estado `ACTIVE`, correo normalizado | `test_create_defaults_and_persists` |
| Datos inválidos y documento duplicado → 400 | `test_invalid_data_and_duplicate_document` |
| DELETE → 204 y la fila queda `INACTIVE` | `test_soft_delete_keeps_the_row` |
| Listar, consultar y actualizar | `test_list_retrieve_and_update` |
| Filtro por estado | `test_status_filter` |

**Resultado.** `test apps.client`: 8 tests OK; `manage.py test`: **26 tests OK**.


#### Registro visual ISS-08

**`iss-08-2.png`**: `apps/client/urls.py`: router con el recurso `clientes`. 15:45.

![iss-08-2.png](Reguistro%20visual/ISS-08/iss-08-2.png)

**`iss-08-3.png`**: Script que agrega `path("api/", include("apps.client.urls"))` a `config/urls.py`.

![iss-08-3.png](Reguistro%20visual/ISS-08/iss-08-3.png)

**`iss-08-4-parte-1.png`**: `apps/client/tests.py` (1/2): `ClientApiTests`. 15:46.

![iss-08-4-parte-1.png](Reguistro%20visual/ISS-08/iss-08-4-parte-1.png)

**`iss-08-4-parte-2.png`**: `apps/client/tests.py` (2/2): documento duplicado, baja lógica, listado y filtro por estado.

![iss-08-4-parte-2.png](Reguistro%20visual/ISS-08/iss-08-4-parte-2.png)

**`iss-08.png`**: `apps/client/views.py`: `ClientViewSet` con filtro `?status=` y baja lógica en `perform_destroy`.

![iss-08.png](Reguistro%20visual/ISS-08/iss-08.png)


---


### ISS-09: Catálogo con ModelViewSet

[Guía (Construir)](https://www.tecnogua.com/academic/site/backend2026/django/manual/10-ISS-09-catalogo-con-modelviewset/)

**Objetivo.** Publicar el catálogo con un criterio de CRUD homogéneo.

**Adaptación.** Sin `ProductType`, el catálogo es solo `Product`; se conserva la clase base `CatalogViewSet`.

**Qué se hizo**

- `CatalogViewSet` (filtro por estado y baja lógica) y `ProductViewSet`.
- Router `productos` y ruta en `config/urls.py`.
- `apps/product/tests.py` pasó a ser de API; los tests de modelo se movieron a `test_models.py`.

**Criterios de aceptación (adaptados)**

| AC | Verificación |
|---|---|
| Producto activo aparece en el catálogo | `test_create_retrieve_update_and_soft_delete` |
| `sku` duplicado → 400 (el nombre repetido se permite) | `test_duplicate_sku_rejected_but_duplicate_name_allowed` |
| Estado por defecto `ACTIVE` | `test_default_status_is_active` |
| Precio negativo → 400 | `test_negative_price_is_rejected` |

**Resultado.** `test apps.product`: 11 tests OK; `manage.py test`: **31 tests OK**.


#### Registro visual ISS-09

**`iss-09-2.png`**: `apps/product/urls.py`: router con el recurso `productos`. 15:57.

![iss-09-2.png](Reguistro%20visual/ISS-09/iss-09-2.png)

**`iss-09-3.png`**: Script que agrega la ruta de productos a `config/urls.py`.

![iss-09-3.png](Reguistro%20visual/ISS-09/iss-09-3.png)

**`iss-09-4-parte-1.png`**: `mv apps/product/tests.py` a `test_models.py` y nuevo `tests.py` de API (1/2).

![iss-09-4-parte-1.png](Reguistro%20visual/ISS-09/iss-09-4-parte-1.png)

**`iss-09-4-parte-2.png`**: `apps/product/tests.py` (2/2): actualización de precio, baja lógica y filtro por estado.

![iss-09-4-parte-2.png](Reguistro%20visual/ISS-09/iss-09-4-parte-2.png)

**`iss-09.png`**: `apps/product/views.py`: `CatalogViewSet` (base) y `ProductViewSet`.

![iss-09.png](Reguistro%20visual/ISS-09/iss-09.png)


---


### ISS-10: Disponibles con ListAPIView

[Guía (Construir)](https://www.tecnogua.com/academic/site/backend2026/django/manual/11-ISS-10-disponibles-con-listapiview/)

**Objetivo.** Endpoint de solo lectura con filtro fijo.

**Adaptación.** La guía filtra por estado, stock y tipo de producto; en BrasaGo solo queda el estado, de modo que "disponible" significa `ACTIVE`. Se dejó la versión mínima, lista para ampliarse cuando exista inventario.

**Qué se hizo**

- `AvailableProductListAPIView` (`ListAPIView`) en `GET /api/productos/disponibles/`.
- La ruta literal se declara antes del router para que `disponibles` no se confunda con un identificador.

**Verificación.** `test_product_crud_and_available_filter`: aparece el producto activo, `POST` responde 405, tras la baja lógica desaparece de la lista y la fila sigue en la tabla.

**Resultado.** `test apps.product`: 12 tests OK; `manage.py test`: **32 tests OK**.


#### Registro visual ISS-10

**`iss-10-2.png`**: `apps/product/urls.py` con la ruta `productos/disponibles/` (2/2).

![iss-10-2.png](Reguistro%20visual/ISS-10/iss-10-2.png)

**`iss-10-3.png`**: Test `test_product_crud_and_available_filter` agregado a `ProductApiTests`. 16:05.

![iss-10-3.png](Reguistro%20visual/ISS-10/iss-10-3.png)

**`iss-10.png`**: `apps/product/urls.py` con la ruta `productos/disponibles/` (1/2).

![iss-10.png](Reguistro%20visual/ISS-10/iss-10.png)


---


### ISS-11: Registro de venta con APIView

[Guía (Construir)](https://www.tecnogua.com/academic/site/backend2026/django/manual/12-ISS-11-registro-de-venta-con-apiview/)

**Objetivo.** Registrar un pedido con sus detalles en una única transacción.

**Adaptación a BrasaGo**

| Guía | BrasaGo |
|---|---|
| `Sale.objects.register(client, sale_date, items, discounts)` | `Order.objects.register(client, branch, table, channel, ordered_at, items)` |
| descuento y `tax` | no existen; `total = subtotal` |
| valida y descuenta stock | no hay stock |
| bloqueos `select_for_update` | sin bloqueos: solo servían al stock |
| cliente obligatorio | cliente opcional; si viene, debe estar `ACTIVE` |
| (no existe) | sede obligatoria y `ACTIVE`; mesa solo en el canal `MESA` y de la misma sede |

**Qué se hizo**

- `OrderQuerySet.register()` con todas las validaciones y el copiado del precio vigente (`unit_price`) a cada línea.
- `OrderItemSerializer` y `OrderRegisterSerializer` (entrada); `OrderRegisterAPIView` y `OrderCollectionAPIView` (`POST /api/pedidos/`).
- `apps/sale/tests.py` con tests de API; los de modelo se movieron a `test_models.py`.

**Criterios de aceptación (adaptados)**

| AC | Verificación |
|---|---|
| AC-11-01: 2×32000 + 1×8000 → subtotal y total 72000.00, `ACTIVE`, `PENDIENTE` | `test_register_snapshots_price_and_totals` |
| AC-11-02: el precio histórico sobrevive a un cambio de precio | mismo test |
| AC-11-03: mesa/canal inválidos o producto inactivo → 400, sin pedido | `test_table_and_channel_rules` y `test_inactive_client_product_or_branch_is_rejected` |
| AC-11-04: si falla un detalle no quedan `Order` ni `OrderDetail` | `test_detail_failure_rolls_back_the_order` |
| AC-11-05: cliente inactivo rechazado | `test_inactive_client_product_or_branch_is_rejected` |

**Resultado.** `test apps.sale`: 12 tests OK; `manage.py test`: **38 tests OK**.


#### Registro visual ISS-11

**`iss-11-2-parte-1.png`**: `apps/sale/serializers.py` (1/2): imports y serializers de lectura.

![iss-11-2-parte-1.png](Reguistro%20visual/ISS-11/iss-11-2-parte-1.png)

**`iss-11-2-parte-2.png`**: `apps/sale/serializers.py` (2/2): `OrderItemSerializer` y `OrderRegisterSerializer`.

![iss-11-2-parte-2.png](Reguistro%20visual/ISS-11/iss-11-2-parte-2.png)

**`iss-11-3.png`**: `apps/sale/views.py`: `OrderRegisterAPIView` y `OrderCollectionAPIView`.

![iss-11-3.png](Reguistro%20visual/ISS-11/iss-11-3.png)

**`iss-11-4.png`**: `apps/sale/urls.py`: ruta `pedidos/`. 16:16.

![iss-11-4.png](Reguistro%20visual/ISS-11/iss-11-4.png)

**`iss-11-5.png`**: Script que agrega la ruta de `sale` a `config/urls.py`.

![iss-11-5.png](Reguistro%20visual/ISS-11/iss-11-5.png)

**`iss-11-6-parte-1.png`**: `mv apps/sale/tests.py` a `test_models.py` y nuevo `tests.py` de API (1/3).

![iss-11-6-parte-1.png](Reguistro%20visual/ISS-11/iss-11-6-parte-1.png)

**`iss-11-6-parte-2.png`**: `apps/sale/tests.py` (2/3): totales y precio histórico.

![iss-11-6-parte-2.png](Reguistro%20visual/ISS-11/iss-11-6-parte-2.png)

**`iss-11-6-parte-3.png`**: `apps/sale/tests.py` (3/3): cliente/producto/sede inactivos y retroceso de la transacción si falla un detalle.

![iss-11-6-parte-3.png](Reguistro%20visual/ISS-11/iss-11-6-parte-3.png)

**`iss-11-7.png`**: `check`, `reverse('order-collection')` → `/api/pedidos/`, `test apps.sale`: 12 tests OK, `--check` sin cambios y `test` completo: 38 tests.

![iss-11-7.png](Reguistro%20visual/ISS-11/iss-11-7.png)

**`iss-11-parte-1.png`**: `apps/sale/managers.py` (1/2): `OrderQuerySet.register()` y validaciones iniciales.

![iss-11-parte-1.png](Reguistro%20visual/ISS-11/iss-11-parte-1.png)

**`iss-11-parte-2.png`**: `apps/sale/managers.py` (2/2): validación de mesa, sede, cliente y productos dentro de la transacción.

![iss-11-parte-2.png](Reguistro%20visual/ISS-11/iss-11-parte-2.png)


---


### ISS-12: Consulta y anulación de ventas

[Guía (Construir)](https://www.tecnogua.com/academic/site/backend2026/django/manual/13-ISS-12-consulta-y-anulacion-de-ventas/)

**Objetivo.** Consultar pedidos y anularlos sin borrar datos.

**Qué se hizo**

- `OrderReadViewSet` (listar, consultar y anular; sin crear ni editar por CRUD) y `GET` en la colección.
- Rutas `pedidos/` y `pedidos/<int:pk>/`.
- `DELETE` llama a `Order.void()`: el pedido y sus detalles quedan `INACTIVE` y el pedido `CANCELADO`; anular dos veces no vuelve a modificar nada.

**Criterios de aceptación (adaptados)**

| AC | Verificación |
|---|---|
| El detalle incluye líneas con el `unit_price` guardado | `test_detail_keeps_historical_price` |
| `DELETE` → 204 y la fila sigue, `INACTIVE` | `test_void_is_idempotent` |
| Anular dos veces no vuelve a tocar nada | `test_void_is_idempotent` (`updated_at` igual) |
| `PUT` y `PATCH` → 405; id inexistente → 404 | `test_detail_only_allows_get_and_delete` |

**Resultado.** `test apps.sale`: 16 tests OK; `manage.py test`: **42 tests OK**.


#### Registro visual ISS-12

**`iss-12-2.png`**: `apps/sale/urls.py`: rutas `pedidos/` y `pedidos/<int:pk>/`.

![iss-12-2.png](Reguistro%20visual/ISS-12/iss-12-2.png)

**`iss-12-3.png`**: Tests agregados a `apps/sale/tests.py`: detalle con precio histórico, listado y anulación idempotente.

![iss-12-3.png](Reguistro%20visual/ISS-12/iss-12-3.png)

**`iss-12.png`**: `apps/sale/views.py`: `OrderReadViewSet` (listar, consultar y anular) y `OrderCollectionAPIView` con `GET`.

![iss-12.png](Reguistro%20visual/ISS-12/iss-12.png)


---


### ISS-13: Django Admin

[Guía (Construir)](https://www.tecnogua.com/academic/site/backend2026/django/manual/14-ISS-13-django-admin/)

**Objetivo.** Operar los datos desde el admin de Django con las mismas reglas que la API.

**Qué se hizo**

- Superusuario creado con `createsuperuser` (el estado `ACTIVE` es necesario para entrar).
- Admin de `Client`, `Product`, `Branch`, `DiningTable`, `Order` y `OrderDetail` con `list_display`, `list_filter`, `search_fields` y `fieldsets`.
- Sedes y mesas se pueden crear desde el admin (son configuración).
- Pedidos y detalles son de solo lectura: sin alta ni borrado; los detalles aparecen en línea dentro del pedido.
- `apps/common/test_admin.py`: pruebas de humo (modelos registrados, listas que abren, alta prohibida, ficha del pedido y borrado prohibido).
- Prueba manual con datos reales: sede y mesa creadas en el admin, producto y pedido creados con `curl`, y pedido visible en el admin.

**Criterios de aceptación (adaptados)**

| AC | Verificación |
|---|---|
| Seis modelos registrados con `list_display`, `list_filter` y `search_fields` | `test_models_are_registered` y `test_changelists_open` |
| Formulario de cliente agrupado, sin contraseña | `fieldsets` de `Client` |
| El producto lista `sku` y precio, sin stock | columnas de `Product` |
| Pedidos y detalles sin alta ni borrado | `test_orders_and_details_cannot_be_added`, `test_order_change_page_opens_but_delete_is_forbidden` y captura `iss-13-9.png` |
| `check` limpio | `python manage.py check` |

**Resultado.** `test apps.common`: 4 tests OK; `manage.py test`: **46 tests OK**.


#### Registro visual ISS-13

**`iss-13-2.png`**: `apps/client/admin.py`. 20:56.

![iss-13-2.png](Reguistro%20visual/ISS-13/iss-13-2.png)

**`iss-13-3.png`**: `apps/product/admin.py`. 20:57.

![iss-13-3.png](Reguistro%20visual/ISS-13/iss-13-3.png)

**`iss-13-4.png`**: `apps/venue/admin.py` (`BranchAdmin` y `DiningTableAdmin`). 20:58.

![iss-13-4.png](Reguistro%20visual/ISS-13/iss-13-4.png)

**`iss-13-5-parte-1.png`**: `apps/sale/admin.py` (1/2): `OrderDetailInline` y `OrderAdmin`. 20:58.

![iss-13-5-parte-1.png](Reguistro%20visual/ISS-13/iss-13-5-parte-1.png)

**`iss-13-5-parte-2.png`**: `apps/sale/admin.py` (2/2): sin alta ni borrado de pedidos y consulta optimizada.

![iss-13-5-parte-2.png](Reguistro%20visual/ISS-13/iss-13-5-parte-2.png)

**`iss-13-6.png`**: `apps/common/test_admin.py`: pruebas de humo del admin.

![iss-13-6.png](Reguistro%20visual/ISS-13/iss-13-6.png)

**`iss-13-7.png`**: `check`, `test apps.common`: 4 tests OK, `--check` sin cambios y `test` completo: 46 tests.

![iss-13-7.png](Reguistro%20visual/ISS-13/iss-13-7.png)

**`iss-13-8.png`**: `runserver` y primeras peticiones a `/admin/` (redirección al login). 21:03.

![iss-13-8.png](Reguistro%20visual/ISS-13/iss-13-8.png)

**`iss-13-9.png`**: Sitio administrativo con la sesión iniciada: Clientes, Productos, Mesas y Sedes con "Añadir"; Pedidos y Detalles de pedidos solo con "Modificar".

![iss-13-9.png](Reguistro%20visual/ISS-13/iss-13-9.png)

**`iss-13-10.png`**: Lista de Sedes en el admin con "Sede Centro" recién creada.

![iss-13-10.png](Reguistro%20visual/ISS-13/iss-13-10.png)

**`iss-13-11.png`**: Lista de Mesas en el admin con una mesa asociada a Sede Centro.

![iss-13-11.png](Reguistro%20visual/ISS-13/iss-13-11.png)

**`iss-13-12.png`**: `curl` contra la API: creación del producto "Bandeja paisa" y de un pedido (subtotal y total 64000.00, estado `PENDIENTE`, claves en camelCase). 21:28.

![iss-13-12.png](Reguistro%20visual/ISS-13/iss-13-12.png)

**`iss-13-13.png`**: Lista de Productos en el admin: Bandeja paisa, BRG-001, 32000,00, Activo.

![iss-13-13.png](Reguistro%20visual/ISS-13/iss-13-13.png)

**`iss-13-14.png`**: Lista de Pedidos en el admin: pedido 1, Sede Centro, Recogida, 64000,00, Pendiente, Activo.

![iss-13-14.png](Reguistro%20visual/ISS-13/iss-13-14.png)

**`iss-13.png`**: `createsuperuser` y consulta de los superusuarios existentes (estado `ACTIVE`).

![iss-13.png](Reguistro%20visual/ISS-13/iss-13.png)


### ISS-14: OpenAPI, Swagger y verificación multimotor

[Guía (Construir)](https://www.tecnogua.com/academic/site/backend2026/django/manual/15-ISS-14-openapi/)

**Objetivo.** Documentar la API con OpenAPI (Swagger UI y ReDoc), dejar el entorno reproducible y cerrar la Fase I (negocio) con la verificación en los cuatro motores.

**Qué se hizo**

- Entorno virtual recreado dentro de `backend/` (al mover el proyecto desde `backend/ISS-00/`) e instalación de `requirements.txt`.
- `drf-spectacular==0.30.0`: `DEFAULT_SCHEMA_CLASS`, `SPECTACULAR_SETTINGS` (título «BrasaGo API», `CAMELIZE_NAMES`, hooks de camelCase y enums) y rutas `/api/schema/`, `/api/schema/swagger-ui/` y `/api/schema/redoc/`.
- `@extend_schema` en las vistas de pedidos para documentar petición y respuesta.
- `apps/common/test_openapi.py` (3 pruebas): esquema y documentación abiertos sin token, endpoints de negocio presentes y claves en camelCase.
- `.env.example` sin datos reales y con las variables de los cuatro motores (PostgreSQL, MySQL, SQL Server, Oracle).
- Una base `brasago_django` vacía por motor (MySQL `utf8mb4`, SQL Server, Oracle con usuario propio y servicio `XEPDB1`) y corrida de `check`, `migrate` y `test` con `DB_ENGINE=<motor>`.
- Evidencia consolidada en `multidialect.md`.

**Verificación**

- `manage.py check`: sin incidencias; `spectacular --validate`: código de salida 0.
- `manage.py test apps.common`: 7 tests OK; `manage.py test`: **49 tests OK** (PostgreSQL).
- El esquema contiene `/api/clientes/`, `/api/productos/`, `/api/productos/disponibles/` y `/api/pedidos/` y usa camelCase (`createdAt`).
- MySQL, SQL Server y Oracle: 23 migraciones y 49 tests OK con el mismo código (ver sección 7).


#### Registro visual ISS-14

**`iss-14-parte-1.png`**: Recreación del `.venv` y `pip install -r requirements.txt` (parte 1/3).

![iss-14-parte-1.png](Reguistro%20visual/ISS-14/iss-14-parte-1.png)

**`iss-14-parte-2.png`**: Fin de la instalación, `check`, `makemigrations --check` y `test`: 46 tests OK (parte 2/3).

![iss-14-parte-2.png](Reguistro%20visual/ISS-14/iss-14-parte-2.png)

**`iss-14-parte-3.png`**: `46 tests OK`, instalación de `drf-spectacular==0.30.0` y `pip freeze > requirements.txt` (parte 3/3).

![iss-14-parte-3.png](Reguistro%20visual/ISS-14/iss-14-parte-3.png)

**`iss-14-2.png`**: Script que añade `drf_spectacular`, `DEFAULT_SCHEMA_CLASS` y `SPECTACULAR_SETTINGS` a `config/settings/__init__.py`. 17:00.

![iss-14-2.png](Reguistro%20visual/ISS-14/iss-14-2.png)

**`iss-14-3.png`**: Script que agrega las rutas `schema`, `swagger-ui` y `redoc` a `config/urls.py`. 17:02.

![iss-14-3.png](Reguistro%20visual/ISS-14/iss-14-3.png)

**`iss-14-4.png`**: `config/urls.py` resultante, con las rutas del esquema y de las apps `client`, `product` y `sale`. 17:02.

![iss-14-4.png](Reguistro%20visual/ISS-14/iss-14-4.png)

**`iss-14-5.png`**: `apps/sale/views.py` con `@extend_schema` en `OrderCollectionAPIView`. 17:03.

![iss-14-5.png](Reguistro%20visual/ISS-14/iss-14-5.png)

**`iss-14-6.png`**: `apps/common/test_openapi.py`: esquema abierto, endpoints de negocio y camelCase. 17:04.

![iss-14-6.png](Reguistro%20visual/ISS-14/iss-14-6.png)

**`iss-14-7.png`**: `check`, `spectacular --validate` (exit code 0), `test apps.common` (7 OK), `makemigrations --check` y `test`: 49 tests OK. 17:06.

![iss-14-7.png](Reguistro%20visual/ISS-14/iss-14-7.png)

**`iss-14-8.png`**: Rutas presentes en el YAML generado (`/api/clientes/`, `/api/pedidos/`, `/api/productos/`, `/api/productos/disponibles/`) y 8 apariciones de `createdAt`. 17:08.

![iss-14-8.png](Reguistro%20visual/ISS-14/iss-14-8.png)

**`iss-14-9.png`**: Swagger UI en `127.0.0.1:8000/api/schema/swagger-ui/`: «BrasaGo API 1.0.0», OAS 3.0 y operaciones de `clientes`.

![iss-14-9.png](Reguistro%20visual/ISS-14/iss-14-9.png)

**`iss-14-10.png`**: Swagger UI: `GET /api/productos/` ejecutado desde «Try it out», respuesta 200.

![iss-14-10.png](Reguistro%20visual/ISS-14/iss-14-10.png)

**`iss-14-11.png`**: API navegable de DRF en `/api/productos/`: JSON con claves camelCase (`createdAt`, `updatedAt`).

![iss-14-11.png](Reguistro%20visual/ISS-14/iss-14-11.png)

**`iss-14-12.png`**: `.env.example` con variables de los cuatro motores y valores de ejemplo (sin datos reales). 17:16.

![iss-14-12.png](Reguistro%20visual/ISS-14/iss-14-12.png)

**`iss-14-13.png`**: Los cuatro contenedores en estado `healthy` y bloque agregado al `.env` (contraseñas ocultas en la captura). 17:24.

![iss-14-13.png](Reguistro%20visual/ISS-14/iss-14-13.png)

**`iss-14-14.png`**: Creación de la base `brasago_django` en MySQL, SQL Server y Oracle (usuario con `CONNECT`, `RESOURCE`, `DBA`); contraseñas ocultas. 17:25.

![iss-14-14.png](Reguistro%20visual/ISS-14/iss-14-14.png)

**`iss-14-15.png`**: MySQL: `check`, `migrate` (23 migraciones) y `test` con 49 pruebas. 17:26.

![iss-14-15.png](Reguistro%20visual/ISS-14/iss-14-15.png)

**`iss-14-16.png`**: Oracle: `check` y `migrate` con `DB_ENGINE=oracle`.

![iss-14-16.png](Reguistro%20visual/ISS-14/iss-14-16.png)



---


### Extensión del negocio: seis tablas que la guía no trae

No hay enlace de la guía: son las tablas del diagrama de BrasaGo que StoreLab no incluye (acordado al cambiar el alcance de la tarea).

**Objetivo.** Completar el modelo del diagrama de BrasaGo con las seis tablas de negocio que StoreLab no incluye: `reservas`, `insumos`, `recetas_insumos`, `pagos`, `domiciliarios` y `entregas`.

**Qué se hizo**

- `venue.Reservation` (`reservas`): cliente, mesa, inicio y fin, estado de la reserva; no permite solapar reservas de la misma mesa.
- `product.Supply` (`insumos`) y `product.RecipeItem` (`recetas_insumos`): insumo con unidad y stock mínimo; receta producto-insumo con cantidad positiva y par único.
- `sale.Payment` (`pagos`): método, monto positivo, estado y `paid_at`; no se paga un pedido anulado ni se supera el total. Más `PATCH /api/pedidos/<id>/estado/` con transiciones válidas del pedido (`PENDIENTE` → `EN PREPARACION` → `LISTO` → `ENTREGADO`, o `CANCELADO`).
- Nueva app `delivery`: `Courier` (`domiciliarios`) y `Delivery` (`entregas`), una entrega por pedido y solo para el canal `DOMICILIO`.
- Todas heredan de `BrasaGoModel` (estado `ACTIVE`/`INACTIVE`, FK con `RESTRICT`, borrado lógico), con admin, serializers, vistas y rutas: `/api/reservas/`, `/api/insumos/`, `/api/recetas/`, `/api/pagos/`, `/api/domiciliarios/`, `/api/entregas/`.
- Nombres de campos en inglés con `db_column` y `db_table` en español, igual que el resto del proyecto.

**Verificación**

- 34 pruebas nuevas (`test_inventory_api`, `test_reservations`, `delivery.test_api`, `sale.test_payments`).
- `manage.py test`: **83 tests OK** (49 + 34).
- Estructura de la tabla comprobada en PostgreSQL (`\d reservas`).


#### Registro visual de la extensión

**`tbl-1.png`**: `apps/venue/models.py`: modelo `Reservation` (reservas).

![tbl-1.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-1.png)

**`tbl-2.png`**: `apps/product/models.py`: modelos `Supply` e `RecipeItem` (insumos y recetas).

![tbl-2.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-2.png)

**`tbl-3.png`**: `apps/sale/models.py`: modelo `Payment` (pagos). 19:12.

![tbl-3.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-3.png)

**`tbl-4.png`**: Creación de la app `delivery` (`apps.py`, `__init__.py`, migraciones). 19:12.

![tbl-4.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-4.png)

**`tbl-5.png`**: `apps/delivery/models.py`: `Courier` y `Delivery` (entregas, con estados).

![tbl-5.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-5.png)

**`tbl-6.png`**: Registro de `apps.delivery.apps.DeliveryConfig` en `INSTALLED_APPS`. 19:13.

![tbl-6.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-6.png)

**`tbl-7.png`**: `admin.py` de `sale`: registro de `Payment`. 19:14.

![tbl-7.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-7.png)

**`tbl-8.png`**: `makemigrations venue product sale delivery`: migraciones iniciales de las tablas nuevas.

![tbl-8.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-8.png)

**`tbl-9.png`**: Reversión de migraciones (`migrate ... zero`) para regenerarlas con los nombres definitivos.

![tbl-9.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-9.png)

**`tbl-10.png`**: Borrado de las migraciones provisionales y script de ajuste de los modelos.

![tbl-10.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-10.png)

**`tbl-11.png`**: Modelo `Reservation` revisado: estados `PENDIENTE`, `CONFIRMADA`, etc., y restricciones.

![tbl-11.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-11.png)

**`tbl-12.png`**: Modelo `Supply` (`insumos`): unidad de medida y `stock_minimo`.

![tbl-12.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-12.png)

**`tbl-13.png`**: Modelo `Payment`: método (`EFECTIVO`, `TARJETA`, `TRANSFERENCIA`) y estado de pago.

![tbl-13.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-13.png)

**`tbl-14.png`**: Modelo `Delivery`: relación uno a uno con el pedido y FK al domiciliario.

![tbl-14.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-14.png)

**`tbl-15.png`**: `admin.py` de `venue` y `product`: reservas, insumos y recetas.

![tbl-15.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-15.png)

**`tbl-16.png`**: Migraciones definitivas: `0002_supply_recipeitem` y las de `venue`, `sale` y `delivery`. 19:29.

![tbl-16.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-16.png)

**`tbl-17.png`**: PostgreSQL: `\d reservas`, estructura real de la tabla.

![tbl-17.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-17.png)

**`tbl-18.png`**: Canales del pedido (`MESA`, `RECOGIDA`, `DOMICILIO`) usados por las reglas de entrega.

![tbl-18.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-18.png)

**`tbl-19.png`**: Serializer de `Supply` (`min_stock` ≥ 0).

![tbl-19.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-19.png)

**`tbl-20.png`**: Serializer de `Reservation` con `client_name` y `table_name`.

![tbl-20.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-20.png)

**`tbl-21.png`**: `apps/venue/views.py` y `urls.py`: `ReservationViewSet` en `/api/reservas/`. 19:38.

![tbl-21.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-21.png)

**`tbl-22.png`**: Validaciones de `Delivery`: solo pedidos de canal `DOMICILIO`.

![tbl-22.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-22.png)

**`tbl-23.png`**: `apps/delivery/views.py` y rutas `/api/domiciliarios/` y `/api/entregas/`.

![tbl-23.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-23.png)

**`tbl-24.png`**: Validaciones de `Payment`: pedido no anulado y sin sobrepago.

![tbl-24.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-24.png)

**`tbl-25.png`**: `PaymentViewSet` (crear, listar y consultar; sin borrado).

![tbl-25.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-25.png)

**`tbl-26.png`**: `apps/sale/urls.py`: `/api/pagos/` y `/api/pedidos/<id>/estado/`. 19:40.

![tbl-26.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-26.png)

**`tbl-27.png`**: `config/urls.py`: inclusión de las rutas de `venue`, `delivery` e inventario (primer script).

![tbl-27.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-27.png)

**`tbl-28.png`**: `config/urls.py`: segundo script de ajuste de las inclusiones.

![tbl-28.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-28.png)

**`tbl-29.png`**: `apps/common/factories.py`: datos de prueba compartidos (`make_world`, `make_order`).

![tbl-29.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-29.png)

**`tbl-30.png`**: Pruebas de insumos y recetas (cantidad mínima, borrado lógico).

![tbl-30.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-30.png)

**`tbl-31.png`**: Pruebas de reservas (nombre de mesa y rechazo de solapamientos).

![tbl-31.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-31.png)

**`tbl-32.png`**: Pruebas de entregas (alta para domicilio, pedido de recogida rechazado).

![tbl-32.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-32.png)

**`tbl-33.png`**: Pruebas del estado del pedido (flujo `EN PREPARACION` → `LISTO` → `ENTREGADO`).

![tbl-33.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-33.png)

**`tbl-34.png`**: `test` de las pruebas nuevas: 34 OK; en la captura siguiente, la suite completa pasa a 83. 19:53.

![tbl-34.png](Reguistro%20visual/Extensi%C3%B3n%20del%20negocio/tbl-34.png)



---


### ISS-15: RefreshToken

[Guía (Construir)](https://www.tecnogua.com/academic/site/backend2026/django/manual/16-ISS-15-refreshtoken/)

**Objetivo.** Guardar los refresh tokens de forma segura y poder rotarlos o revocarlos por familia de sesión.

**Qué se hizo**

- `djangorestframework-simplejwt==5.5.1` instalado, `rest_framework_simplejwt` en `INSTALLED_APPS` y `SIMPLE_JWT` (access de 60 min, refresh de 1 día).
- `apps/security/tokens.py`: generación de un valor aleatorio y su hash SHA-256 (`generate_refresh_value`, `hash_refresh_value`).
- Modelo `RefreshToken` (`refresh_tokens`): `token_hash` único de 64 caracteres, `device_info`, `family_id`, `expires_at`, `revoked_at`, `replaced_by` y estado (columna `is_valid` del diagrama). **El token en claro nunca se guarda.**
- Registro del modelo en el admin y migración `security.0002_refreshtoken`.
- `apps/security/test_refresh_token.py` (8 pruebas).

**Verificación**

- `test apps.security.test_refresh_token`: 8 tests OK; `manage.py test`: **91 tests OK**.
- PostgreSQL: `\d refresh_tokens` confirma las columnas, incluida `is_valid`.


#### Registro visual ISS-15

**`iss-15.png`**: Instalación de `simplejwt==5.5.1` y creación de `apps/security/tokens.py`.

![iss-15.png](Reguistro%20visual/ISS-15/iss-15.png)

**`iss-15-2.png`**: `INSTALLED_APPS` y bloque `SIMPLE_JWT` en los settings. 19:59.

![iss-15-2.png](Reguistro%20visual/ISS-15/iss-15-2.png)

**`iss-15-3.png`**: `RefreshToken` en `apps/security/models.py` (hash, familia, `replaced_by`, estado `is_valid`).

![iss-15-3.png](Reguistro%20visual/ISS-15/iss-15-3.png)

**`iss-15-4.png`**: `RefreshTokenAdmin` en `apps/security/admin.py`. 20:00.

![iss-15-4.png](Reguistro%20visual/ISS-15/iss-15-4.png)

**`iss-15-5.png`**: `test_refresh_token.py`: hash determinista, valores aleatorios, estados no utilizables.

![iss-15-5.png](Reguistro%20visual/ISS-15/iss-15-5.png)

**`iss-15-6.png`**: `makemigrations security`, `check`, `migrate`, 8 tests de la unidad y suite completa de 91. 20:01.

![iss-15-6.png](Reguistro%20visual/ISS-15/iss-15-6.png)

**`iss-15-7.png`**: `\d refresh_tokens` en PostgreSQL.

![iss-15-7.png](Reguistro%20visual/ISS-15/iss-15-7.png)



---


### ISS-16: Role, RoleUser, Resource y ResourceRole

[Guía (Construir)](https://www.tecnogua.com/academic/site/backend2026/django/manual/17-ISS-16-role-roleuser-resource-y-resourcerole/)

**Objetivo.** Modelar la matriz de autorización del diagrama: usuario → rol → recurso.

**Qué se hizo**

- `Role` (`roles`), `RoleUser` (`role_users`), `Resource` (`resources`: método + ruta) y `ResourceRole` (`resource_roles`) sobre `BrasaGoModel`, con pares únicos y FK `RESTRICT`.
- El recurso guarda la ruta como la devuelve `resolver_match.route` (por ejemplo `api/clientes/<int:pk>/`), para que la comprobación sea exacta.
- Admin de los cuatro modelos y migración `security.0003`.
- Comando `seed_rbac`: crea un recurso por cada método y ruta de la API (idempotente).
- Pruebas de modelos (`test_rbac_models`): unicidad, CHECK de estado, rol con vínculos no borrable y siembra idempotente.

**Verificación**

- `test apps.security`: 22 tests OK; `manage.py test`: **99 tests OK**.
- PostgreSQL: consulta de `resources` (método y ruta) y `\d role_users`.


#### Registro visual ISS-16

**`iss-16.png`**: Primeros modelos RBAC en `apps/security/models.py`. 20:07.

![iss-16.png](Reguistro%20visual/ISS-16/iss-16.png)

**`iss-16-2.png`**: Admin de `RoleUser`, `Resource` y `ResourceRole` con `list_display` y `list_filter`. 20:07.

![iss-16-2.png](Reguistro%20visual/ISS-16/iss-16-2.png)

**`iss-16-3.png`**: Comando `seed_rbac` en `management/commands/`.

![iss-16-3.png](Reguistro%20visual/ISS-16/iss-16-3.png)

**`iss-16-4.png`**: Archivos de pruebas RBAC creados. 20:09.

![iss-16-4.png](Reguistro%20visual/ISS-16/iss-16-4.png)

**`iss-16-5.png`**: `makemigrations`, `migrate` (`0003`), 22 tests de `apps.security` y suite completa de 99. 20:09.

![iss-16-5.png](Reguistro%20visual/ISS-16/iss-16-5.png)

**`iss-16-6.png`**: PostgreSQL: conteo y muestra de `resources` y estructura de `role_users`. 20:09.

![iss-16-6.png](Reguistro%20visual/ISS-16/iss-16-6.png)



---


### ISS-17: Login OPEN

[Guía (Construir)](https://www.tecnogua.com/academic/site/backend2026/django/manual/18-ISS-17-login-open/)

**Objetivo.** Autenticar con usuario o correo y contraseña y devolver un par access/refresh.

**Qué se hizo**

- `LoginSerializer` y `LoginAPIView`: acepta `username` o `email`, rechaza con 401 un mensaje genérico (no revela si la cuenta existe) y exige usuario `ACTIVE`.
- El access es un JWT de SimpleJWT; el refresh es un valor aleatorio cuyo hash se guarda en `refresh_tokens` junto con el `User-Agent`.
- Respuesta en camelCase: `access`, `refresh`, `tokenType`, `accessExpiresIn`.
- `apps/common/testing.py`: ayudas para crear usuarios y autenticar en las pruebas.
- Ruta `/api/auth/login/` en `apps/security/urls.py` y en `config/urls.py`.
- `test_auth_login.py` (13 pruebas).

**Verificación**

- `test apps.security.test_auth_login`: 13 tests OK; `manage.py test`: **112 tests OK**.
- Prueba manual con `curl`: respuesta con el par de tokens y una fila nueva en `refresh_tokens` (solo el hash).


#### Registro visual ISS-17

**`iss-17.png`**: `apps/common/testing.py` y `LoginSerializer`. 20:17.

![iss-17.png](Reguistro%20visual/ISS-17/iss-17.png)

**`iss-17-2.png`**: `LoginAPIView`: credenciales inválidas → 401 y emisión del refresh. 20:17.

![iss-17-2.png](Reguistro%20visual/ISS-17/iss-17-2.png)

**`iss-17-3.png`**: `apps/security/urls.py` y registro de `apps.security.urls` en `config/urls.py`. 20:18.

![iss-17-3.png](Reguistro%20visual/ISS-17/iss-17-3.png)

**`iss-17-4.png`**: `test_auth_login.py`: 401, 400 y 200 según el caso, incluido un Bearer inválido. 20:18.

![iss-17-4.png](Reguistro%20visual/ISS-17/iss-17-4.png)

**`iss-17-5.png`**: `check`, 13 tests de login y suite completa de 112 (con la advertencia de longitud de clave HMAC). 20:18.

![iss-17-5.png](Reguistro%20visual/ISS-17/iss-17-5.png)

**`iss-17-6.png`**: Login real con `curl` y la fila resultante en `refresh_tokens` (solo `token_hash`); tokens ocultos en la captura.

![iss-17-6.png](Reguistro%20visual/ISS-17/iss-17-6.png)



---


### ISS-18: Refresh con rotación

[Guía (Construir)](https://www.tecnogua.com/academic/site/backend2026/django/manual/19-ISS-18-refresh-con-rotacion/)

**Objetivo.** Renovar el access rotando el refresh y detectando su reutilización.

**Qué se hizo**

- `RefreshSerializer` y `RefreshAPIView`: busca el hash con bloqueo de fila, marca el token usado como reemplazado y emite uno nuevo en la misma familia.
- Reutilización de un token ya rotado o revocado → se revoca toda la familia y se responde 401 (la respuesta se devuelve después del bloque atómico para no perder la revocación).
- Token vencido o desconocido → 401; usuario inactivo → 401 y el token se desactiva; un `Authorization` inválido no bloquea el refresh.
- `test_auth_refresh.py` (10 pruebas).

**Verificación**

- `test apps.security.test_auth_refresh`: 10 tests OK; `manage.py test`: **122 tests OK**.


#### Registro visual ISS-18

**`iss-18.png`**: `RefreshSerializer` en `apps/security/serializers.py`. 20:28.

![iss-18.png](Reguistro%20visual/ISS-18/iss-18.png)

**`iss-18-2.png`**: `RefreshAPIView` con rotación y revocación de la familia. 20:28.

![iss-18-2.png](Reguistro%20visual/ISS-18/iss-18-2.png)

**`iss-18-3.png`**: Ruta `/api/auth/refresh/` en `apps/security/urls.py`. 20:29.

![iss-18-3.png](Reguistro%20visual/ISS-18/iss-18-3.png)

**`iss-18-4.png`**: `test_auth_refresh.py`: rotación, reutilización, vencido, inactivo y Bearer inválido.

![iss-18-4.png](Reguistro%20visual/ISS-18/iss-18-4.png)

**`iss-18-5.png`**: `check`, 10 tests de refresh y suite completa de 122. 20:29.

![iss-18-5.png](Reguistro%20visual/ISS-18/iss-18-5.png)



---


### ISS-19: Logout

[Guía (Construir)](https://www.tecnogua.com/academic/site/backend2026/django/manual/20-ISS-19-logout/)

**Objetivo.** Cerrar una sesión revocando su refresh token.

**Qué se hizo**

- `LogoutSerializer` y `LogoutAPIView`: revoca el token recibido y responde 204; un token desconocido o ya cerrado responde 401.
- El logout de una sesión no afecta a otras familias (por ejemplo, el portátil sigue pudiendo renovar).
- Un `Authorization` inválido se ignora, igual que en el refresh.
- `test_auth_logout.py` (10 pruebas).

**Verificación**

- `test apps.security.test_auth_logout`: 10 tests OK; `manage.py test`: **132 tests OK**.


#### Registro visual ISS-19

**`iss-19.png`**: `LogoutSerializer` y `LogoutAPIView` (parche de `auth_views.py`).

![iss-19.png](Reguistro%20visual/ISS-19/iss-19.png)

**`iss-19-2.png`**: Ruta `/api/auth/logout/` en `apps/security/urls.py`. 20:46.

![iss-19-2.png](Reguistro%20visual/ISS-19/iss-19-2.png)

**`iss-19-3.png`**: `test_auth_logout.py`: 204, 401 y 400, y sesiones independientes.

![iss-19-3.png](Reguistro%20visual/ISS-19/iss-19-3.png)

**`iss-19-4.png`**: `check`, 10 tests de logout y suite completa de 132. 20:47.

![iss-19-4.png](Reguistro%20visual/ISS-19/iss-19-4.png)



---


### ISS-20: Perfil JWT con token

[Guía (Construir)](https://www.tecnogua.com/academic/site/backend2026/django/manual/21-ISS-20-perfil-jwt-con-token/)

**Objetivo.** Exponer el perfil del usuario autenticado y validar el JWT de forma uniforme.

**Qué se hizo**

- `BrasaGoJWTAuthentication`: valida el access y exige que el usuario esté `ACTIVE`; usuario inactivo con JWT válido → 401.
- `ProfileAPIView`: GET y PATCH del propio perfil (solo JWT); POST y DELETE → 405; la unicidad de correo se valida con mensaje en español.
- El perfil queda fuera de la matriz RBAC: solo exige estar autenticado.
- Tests de perfil (`test_auth_profile.py`).

**Verificación**

- `manage.py test`: **143 tests OK**.


#### Registro visual ISS-20

**`iss-20.png`**: `apps/security/authentication.py` y serializers del perfil. 20:53.

![iss-20.png](Reguistro%20visual/ISS-20/iss-20.png)

**`iss-20-2.png`**: `ProfileAPIView` en `rbac_views.py` y ruta en `urls.py`. 20:54.

![iss-20-2.png](Reguistro%20visual/ISS-20/iss-20-2.png)

**`iss-20-3.png`**: Ajuste de `REST_FRAMEWORK` para usar la autenticación JWT del proyecto. 20:54.

![iss-20-3.png](Reguistro%20visual/ISS-20/iss-20-3.png)

**`iss-20-4.png`**: `test_auth_profile.py`: 200, 401, 405 y conflicto de correo.

![iss-20-4.png](Reguistro%20visual/ISS-20/iss-20-4.png)



---


### ISS-21: HasResourceAccess

[Guía (Construir)](https://www.tecnogua.com/academic/site/backend2026/django/manual/22-ISS-21-hasresourceaccess/)

**Objetivo.** Autorizar cada petición según la matriz RBAC.

**Qué se hizo**

- `HasResourceAccess`: toma `request.user`, sigue la cadena `User → RoleUser → Role → ResourceRole → Resource` (todos `ACTIVE`) y compara método y `resolver_match.route`.
- Sin identidad → 401; autenticado sin permiso → 403 (denegar por defecto); `OPTIONS` y `HEAD` se tratan como lectura.
- El permiso concede según el patrón de ruta, no por id concreto.
- Ayudas de prueba `grant_access`, `grant` y `grant_crud` en `apps/common/testing.py`.
- `test_permissions.py` (11 pruebas).

**Verificación**

- `test apps.security.test_permissions`: 11 tests OK; `manage.py test`: **154 tests OK**.


#### Registro visual ISS-21

**`iss-21.png`**: `apps/security/permissions.py`: clase `HasResourceAccess`. 21:07.

![iss-21.png](Reguistro%20visual/ISS-21/iss-21.png)

**`iss-21-2.png`**: Ayudas de `apps/common/testing.py` para autenticar y conceder acceso. 21:08.

![iss-21-2.png](Reguistro%20visual/ISS-21/iss-21-2.png)

**`iss-21-3.png`**: `test_permissions.py`: 403 sin permiso y `OPTIONS` permitido.

![iss-21-3.png](Reguistro%20visual/ISS-21/iss-21-3.png)

**`iss-21-4-parte-1.png`**: 11 tests de `test_permissions` en OK (1/2).

![iss-21-4-parte-1.png](Reguistro%20visual/ISS-21/iss-21-4-parte-1.png)

**`iss-21-4-parte-2.png`**: Suite completa: 154 tests en OK (2/2). 21:10.

![iss-21-4-parte-2.png](Reguistro%20visual/ISS-21/iss-21-4-parte-2.png)



---


### ISS-22: RBAC sobre el negocio

[Guía (Construir)](https://www.tecnogua.com/academic/site/backend2026/django/manual/23-ISS-22-rbac-sobre-el-negocio/)

**Objetivo.** Proteger la API de negocio con JWT y `HasResourceAccess` y dejar un camino de administración para desarrollo.

**Qué se hizo**

- Las vistas de clientes, productos, pedidos, reservas, insumos, recetas, pagos, domiciliarios y entregas exigen identidad y permiso; `GET /api/productos/disponibles/` y los endpoints de autenticación quedan abiertos.
- `grant_all_access <usuario>` (solo desarrollo): crea el rol `ADMIN`, siembra los recursos y lo asigna al usuario.
- `test_rbac_business.py` (8 pruebas) y actualización de las pruebas anteriores: donde esperaban 405 sin permiso ahora esperan **403** (la autorización se evalúa antes que el método).
- Aviso de longitud de `SECRET_KEY` (8 bytes) corregido rotando la clave en `.env`.

**Verificación**

- `test apps.security.test_rbac_business`: 8 tests OK; `test apps.client apps.product apps.sale apps.venue apps.delivery`: 70 OK tras ajustar los 403.
- `manage.py test`: **162 tests OK**; `spectacular --validate` con salida 0.


#### Registro visual ISS-22

**`iss-22.png`**: Longitud de `SECRET_KEY` y comprobación de `authentication.py`. 13:33.

![iss-22.png](Reguistro%20visual/ISS-22/iss-22.png)

**`iss-22-2.png`**: Ajuste de `test_rbac_models.py` para silenciar la salida de `seed_rbac`. 13:35.

![iss-22-2.png](Reguistro%20visual/ISS-22/iss-22-2.png)

**`iss-22-3.png`**: Ayudas de `apps/common/testing.py` para pruebas con RBAC. 13:35.

![iss-22-3.png](Reguistro%20visual/ISS-22/iss-22-3.png)

**`iss-22-4.png`**: Script que protege las vistas de negocio. 13:36.

![iss-22-4.png](Reguistro%20visual/ISS-22/iss-22-4.png)

**`iss-22-5.png`**: Script de actualización de los asserts (de 200 abierto a 401 sin sesión). 13:36.

![iss-22-5.png](Reguistro%20visual/ISS-22/iss-22-5.png)

**`iss-22-6.png`**: `test_rbac_business.py`: 401 sin token, 403 sin permiso y 200 con permiso.

![iss-22-6.png](Reguistro%20visual/ISS-22/iss-22-6.png)

**`iss-22-7.png`**: Comando `grant_all_access` (rol `ADMIN` para desarrollo). 13:37.

![iss-22-7.png](Reguistro%20visual/ISS-22/iss-22-7.png)

**`iss-22-8.png`**: 8 tests de negocio en OK y las dos fallas esperadas `403 != 405`.

![iss-22-8.png](Reguistro%20visual/ISS-22/iss-22-8.png)

**`iss-22-9.png`**: Corrección de las fallas: 405 → 403; queda una por ajustar.

![iss-22-9.png](Reguistro%20visual/ISS-22/iss-22-9.png)

**`iss-22-10.png`**: Reemplazo de `HTTP_405_METHOD_NOT_ALLOWED` por `HTTP_403_FORBIDDEN`; 70 tests de negocio OK. 13:41.

![iss-22-10.png](Reguistro%20visual/ISS-22/iss-22-10.png)

**`iss-22-11.png`**: Suite completa: 162 tests OK y `spectacular --validate`. 13:42.

![iss-22-11.png](Reguistro%20visual/ISS-22/iss-22-11.png)



---


### ISS-23: CRUD de la matriz

[Guía (Construir)](https://www.tecnogua.com/academic/site/backend2026/django/manual/24-ISS-23-crud-de-la-matriz/)

**Objetivo.** Administrar usuarios, roles, asignaciones, recursos y permisos desde la API.

**Qué se hizo**

- Rutas `/api/users/`, `/api/roles/`, `/api/role-users/`, `/api/resources/` y `/api/resource-roles/` (`SimpleRouter`) con `lookup_value_converter = "int"` para que la ruta registrada sea `<int:pk>`.
- Usuarios: contraseña obligatoria al crear, validada, guardada con hash y nunca devuelta.
- Borrado lógico en todos; un rol con vínculos no se puede eliminar físicamente.
- `test_matrix.py` (6 pruebas): CRUD de roles, contraseña, cadena usuario-rol-recurso y 401/403.
- Pruebas manuales en Swagger UI: creación del rol «mesero» (201) y baja (204); ReDoc muestra los nuevos grupos.
- Corrección de la ruta `<str:pk>` por `<int:pk>` en las pruebas, para igualar lo que devuelve el resolver.

**Verificación**

- `test apps.security.test_matrix`: 6 tests OK; `manage.py test`: **168 tests OK**.
- `seed_rbac` idempotente y `spectacular --validate` en 0.


#### Registro visual ISS-23

**`iss-23.png`**: Validación de la contraseña obligatoria en `UserSerializer`. 13:47.

![iss-23.png](Reguistro%20visual/ISS-23/iss-23.png)

**`iss-23-2.png`**: `rbac_views.py`: viewsets de la matriz. 13:48.

![iss-23-2.png](Reguistro%20visual/ISS-23/iss-23-2.png)

**`iss-23-3.png`**: Rutas del router en `apps/security/urls.py` y `check` limpio. 13:48.

![iss-23-3.png](Reguistro%20visual/ISS-23/iss-23-3.png)

**`iss-23-4-parte-1.png`**: `test_matrix.py` (1/3).

![iss-23-4-parte-1.png](Reguistro%20visual/ISS-23/iss-23-4-parte-1.png)

**`iss-23-4-parte-2.png`**: `test_matrix.py` (2/3).

![iss-23-4-parte-2.png](Reguistro%20visual/ISS-23/iss-23-4-parte-2.png)

**`iss-23-4-parte-3.png`**: `test_matrix.py` (3/3) y primera corrida con `KeyError: 'name'`.

![iss-23-4-parte-3.png](Reguistro%20visual/ISS-23/iss-23-4-parte-3.png)

**`iss-23-5.png`**: Cambio de `<pk>` por `<str:pk>` y 6 tests de la matriz en OK. 13:51.

![iss-23-5.png](Reguistro%20visual/ISS-23/iss-23-5.png)

**`iss-23-6.png`**: `seed_rbac` repetido (idempotente) y `spectacular --validate`. 13:51.

![iss-23-6.png](Reguistro%20visual/ISS-23/iss-23-6.png)

**`iss-23-7.png`**: Suite completa: 168 tests OK. 13:55.

![iss-23-7.png](Reguistro%20visual/ISS-23/iss-23-7.png)

**`iss-23-8.png`**: Swagger UI: `GET` autenticado con Bearer, respuesta 200 (token oculto).

![iss-23-8.png](Reguistro%20visual/ISS-23/iss-23-8.png)

**`iss-23-9.png`**: Swagger UI: `POST /api/roles/` con `{"name": "mesero"}`, respuesta 201 (token oculto). 14:12.

![iss-23-9.png](Reguistro%20visual/ISS-23/iss-23-9.png)

**`iss-23-10.png`**: Swagger UI: `DELETE /api/roles/2/`, respuesta 204 (token oculto).

![iss-23-10.png](Reguistro%20visual/ISS-23/iss-23-10.png)

**`iss-23-11.png`**: Swagger UI: nueva petición `POST /api/roles/` (token oculto).

![iss-23-11.png](Reguistro%20visual/ISS-23/iss-23-11.png)

**`iss-23-12.png`**: Cambio de contraseña del superusuario y lista de roles: `ADMIN` activo y `mesero` inactivo tras la baja lógica. 14:16.

![iss-23-12.png](Reguistro%20visual/ISS-23/iss-23-12.png)

**`iss-23-13.png`**: ReDoc con los grupos `auth`, `clientes`, `domiciliarios`, `entregas`, `insumos`, `pagos`, `resources`…

![iss-23-13.png](Reguistro%20visual/ISS-23/iss-23-13.png)

**`iss-23-14.png`**: Admin de Django con las tablas de la extensión (domiciliarios, entregas, insumos, recetas, pagos…).

![iss-23-14.png](Reguistro%20visual/ISS-23/iss-23-14.png)



---


### ISS-24: Semilla RBAC y Swagger con Bearer

[Guía (Construir)](https://www.tecnogua.com/academic/site/backend2026/django/manual/25-ISS-24-semilla-rbac-y-swagger-con-bearer/)

**Objetivo.** Sembrar la matriz con los recursos reales de la API y dejar el acceso inicial listo.

**Qué se hizo**

- `seed_rbac` solo siembra las vistas que gobierna `HasResourceAccess` (`governed_by_matrix()`): login, refresh, logout y profile se excluyen porque no pasan por la matriz. Resultado: **84 recursos**.
- Limpieza de recursos antiguos con `<str:pk>` y `api/auth/` y nueva siembra; `grant_all_access elkin` concede los 84 recursos al rol `ADMIN`.
- Pruebas añadidas: `test_auth_open_routes_are_not_seeded` y `test_profile_is_not_governed_by_the_matrix`; ajuste de `test_seeded_routes_match_what_the_resolver_returns`.
- Esquema de seguridad `jwtAuth` (`BrasaGoJWTScheme`) para que Swagger muestre «Authorize» y envíe el Bearer; el aviso «could not resolve authenticator» desaparece.

**Verificación**

- `test apps.security.test_matrix apps.security.test_seed`: 10 OK; `test apps.security.test_permissions`: 12 OK.
- `manage.py test`: **173 tests OK** y `spectacular --validate` en 0; `seed_rbac` idempotente (84 en total).


#### Registro visual ISS-24

**`iss-24.png`**: Reemplazo de `<str:pk>` por `<int:pk>` en `test_matrix.py` y `check`. 14:20.

![iss-24.png](Reguistro%20visual/ISS-24/iss-24.png)

**`iss-24-2.png`**: Falla: `test_auth_open_routes_are_not_seeded` (`api/auth/login/` sí se sembraba). 14:21.

![iss-24-2.png](Reguistro%20visual/ISS-24/iss-24-2.png)

**`iss-24-3.png`**: Parche de `seed_rbac` (filtro `governed_by_matrix`). 14:22.

![iss-24-3.png](Reguistro%20visual/ISS-24/iss-24-3.png)

**`iss-24-4.png`**: `test_matrix` y `test_seed`: 10 tests OK. 14:23.

![iss-24-4.png](Reguistro%20visual/ISS-24/iss-24-4.png)

**`iss-24-5.png`**: Limpieza de recursos antiguos, `seed_rbac` (20 nuevos, 84 en total) y `grant_all_access elkin`. 14:23.

![iss-24-5.png](Reguistro%20visual/ISS-24/iss-24-5.png)

**`iss-24-6.png`**: Suite completa: falla `api/auth/profile/` en `test_seeded_routes...` (172 tests, 1 falla). 14:25.

![iss-24-6.png](Reguistro%20visual/ISS-24/iss-24-6.png)

**`iss-24-7.png`**: Revisión del código de `test_permissions.py` (líneas 105 a 140). 14:26.

![iss-24-7.png](Reguistro%20visual/ISS-24/iss-24-7.png)

**`iss-24-8.png`**: Ajuste de la prueba y `test_permissions`: 12 tests OK. 14:26.

![iss-24-8.png](Reguistro%20visual/ISS-24/iss-24-8.png)

**`iss-24-9.png`**: Repetición de la limpieza: nada que borrar; `seed_rbac` en 84; `grant_all_access` otra vez. 14:27.

![iss-24-9.png](Reguistro%20visual/ISS-24/iss-24-9.png)

**`iss-24-10.png`**: Suite completa: 173 tests OK y `spectacular --validate`. 14:28.

![iss-24-10.png](Reguistro%20visual/ISS-24/iss-24-10.png)



---


### ISS-25: Pruebas 401 y 403

[Guía (Construir)](https://www.tecnogua.com/academic/site/backend2026/django/manual/26-ISS-25-pruebas-401-y-403/)

**Objetivo.** Cerrar la guía con pruebas de extremo a extremo de lo que el RBAC debe negar.

**Qué se hizo**

- `test_rbac_denials.py` (5 pruebas): sin token → 401; token válido sin permiso → 403; conceder `GET` no concede `POST`; usuario inactivo con JWT válido → 401; falta de permiso → 403 y falta de identidad → 401 con login real.
- Con esta unidad termina la guía (no existe ISS-26).

**Verificación**

- `test apps.security.test_rbac_denials`: 5 tests OK; `manage.py test`: **178 tests OK**; `check` limpio y `spectacular --validate` con salida 0.


#### Registro visual ISS-25

**`iss-25.png`**: `test_rbac_denials.py`: 401, 403 y 200 según el permiso.

![iss-25.png](Reguistro%20visual/ISS-25/iss-25.png)

**`iss-25-2.png`**: 5 tests de denegación, `check`, suite completa de 178 y `spectacular --validate`. 14:30.

![iss-25-2.png](Reguistro%20visual/ISS-25/iss-25-2.png)


---


## 6. Incidencias y correcciones

| # | ISS | Qué pasó | Causa | Solución |
|---|---|---|---|---|
| 1 | 04 | `column "avatar" of relation "users" does not exist` al crear un usuario | La migración `0001` ya estaba aplicada con los modelos anteriores y `migrate` no la repite | Se regeneraron las migraciones de `security`, `client` y `product` sobre una base nueva |
| 2 | 04 | Django apuntaba a `brasago`, que ya tenía las tablas del diagrama (`clientes`, `pedidos`, `productos`…) | Misma base para dos usos | Se creó `brasago_django` y se cambió `POSTGRES_DB` en `.env` |
| 3 | 05 | `productos` con columnas en inglés y nombre único | Modelo tomado de la guía | `db_column` en español y se quitó la unicidad del nombre |
| 4 | 06 | `ImportError: cannot import name 'OrderManager'` | `managers.py` seguía con el `SaleManager` de la guía | Se reescribió `managers.py` con `OrderQuerySet` / `OrderManager` |
| 5 | 07 | Fallaron 2 tests de `apps/product/tests.py` | Esperaban reglas de la guía (estado `INACTIVE`, nombre único) | Se reemplazaron por tests con las reglas de BrasaGo (captura `test_default_status_and_type_restriction.png`) |
| 6 | 08 | `NameError: name 'include' is not defined` en `config/urls.py` | El script de parche creyó que el import ya existía porque el texto aparece en un comentario del archivo | Se corrigió el import con `sed` |
| 7 | 13 | No se podía iniciar sesión en el admin | Credencial de acceso incorrecta | Diagnóstico desde el shell y restablecimiento del acceso (`iss-13-9.png`) |
| 8 | 13 | `POST /api/pedidos/` respondió 400 (`Clave primaria "1" inválida`) | Todavía no existían productos | Se creó el producto por la API y el pedido se registró correctamente (`iss-13-12.png`) |
| 9 | 14 | Los motores adicionales no podían migrar sobre las bases existentes | Cada motor necesita su base vacía; Oracle exige un usuario con `CONNECT`, `RESOURCE` y `DBA` para que Django cree el usuario de pruebas | Una base `brasago_django` por motor (`iss-14-14.png`) |
| 10 | Ext. | Migraciones provisionales de las seis tablas con nombres no definitivos | Primer borrador de los modelos | `migrate ... zero`, borrado de las migraciones y regeneración (`tbl-8.png` a `tbl-10.png`, `tbl-16.png`) |
| 11 | 17 | Login con 400 «Invalid control character» al probar con `curl` | La variable con la contraseña tenía caracteres de control | Leer la contraseña con `read -r -s` |
| 12 | 17 | Logins con 401 durante las pruebas manuales | Contraseña del superusuario olvidada o incorrecta | `changepassword` (`iss-23-12.png`) |
| 13 | 17 | `InsecureKeyLengthWarning`: la clave HMAC tenía 8 bytes | `SECRET_KEY` demasiado corta en `.env` | Rotar la clave a una de 32 bytes o más (ISS-22, `iss-22.png`) |
| 14 | 17 | drf-spectacular: «could not resolve authenticator» | La autenticación personalizada no tenía esquema | Se agregó `BrasaGoJWTScheme` (esquema `jwtAuth`) |
| 15 | 22 | Fallaron los tests con `403 != 405` (`iss-22-8.png`, `iss-22-9.png`) | Con RBAC la autorización se evalúa antes que el método permitido | Los asserts ahora esperan 403 (`iss-22-10.png`) |
| 16 | 23 | `KeyError: 'name'` y rutas `<pk>` que no coincidían con las sembradas (`iss-23-4-parte-3.png`, `iss-23-5.png`) | La ruta registrada por el resolver es `<int:pk>` y no `<str:pk>` | `lookup_value_converter = "int"` y pruebas con `<int:pk>` (`iss-24.png`) |
| 17 | 24 | `seed_rbac` sembraba login, refresh, logout y profile (89 recursos) (`iss-24-2.png`, `iss-24-6.png`) | Esas rutas no pasan por `HasResourceAccess` | Filtro `governed_by_matrix()`: 84 recursos; se ajustó `test_seeded_routes...` y se agregó `test_profile_is_not_governed_by_the_matrix` |
| 18 | 25 | En Oracle fallaron 18 tests: `NotSupportedError: LIMIT/OFFSET is not supported with select_for_update` (`Captura de pantalla (952).png`, `prueba-9.png`) | Oracle no permite `FOR UPDATE` junto con `LIMIT`, y `.first()` agrega el límite | `next(iter(RefreshToken.objects.select_for_update().filter(...)), None)` en `auth_views.py` (líneas 131 y 198); Oracle quedó en OK (`Captura de pantalla (953).png`) |


## 7. Verificación multimotor

La misma base de código, sin cambios por motor, se ejecutó con `DB_ENGINE=<motor>` (selección en `config/database.py`). El detalle de ISS-14 (49 tests) está en `multidialect.md`; esta tabla recoge la corrida final con la guía completa (**178 tests**).

| Motor | Imagen / driver | Resultado | Duración | Evidencia |
|---|---|---|---|---|
| PostgreSQL 17 | `postgres:17`, psycopg 3.3.6 | 178 tests OK; también con `--keepdb -v 2` | n/d | `prueba-1.png` a `prueba-6.png` |
| MySQL 8.0 | `mysql:8.0`, mysqlclient 2.3.0 | 178 tests OK | 47,3 s | `prueba-7.png` |
| SQL Server 2022 | `mssql:2022-latest`, mssql-django 2.0.0, ODBC Driver 18 | 178 tests OK | 45,6 s | `prueba-8.png` |
| Oracle XE 21 | `gvenzl/oracle-xe:21-slim`, oracledb 26.0.1 | Primera corrida: 18 errores (`select_for_update` con `LIMIT`); tras el parche, suite en OK | 36,4 s (corrida con errores) | `prueba-9.png`, `Captura de pantalla (952).png`, `Captura de pantalla (953).png` |

Comprobaciones adicionales (PostgreSQL): `check` limpio, `makemigrations --check` sin cambios, `spectacular --validate` con salida 0, `showmigrations` con 29 migraciones aplicadas y `seed_rbac` idempotente (84 recursos).

#### Registro visual de las pruebas

**`prueba-1.png`**: PostgreSQL: motor y base (`brasago_django`), 29 migraciones aplicadas y corrida de 178 tests con `--keepdb -v 2`.

![prueba-1.png](Reguistro%20visual/pruebas/prueba-1.png)

**`prueba-2.png`**: `test -v 2` (1/3): modelos de pedidos, pagos y estados del pedido, todos `ok`.

![prueba-2.png](Reguistro%20visual/pruebas/prueba-2.png)

**`prueba-3.png`**: `test -v 2` (2/3): refresh, matriz RBAC y permisos, todos `ok`.

![prueba-3.png](Reguistro%20visual/pruebas/prueba-3.png)

**`prueba-4.png`**: `test -v 2` (3/3): denegaciones RBAC y modelos de seguridad, todos `ok`.

![prueba-4.png](Reguistro%20visual/pruebas/prueba-4.png)

**`prueba-5.png`**: Prueba de `test_rbac_denials` en detalle con `-v 2`: la base de pruebas se recrea y se aplican las migraciones.

![prueba-5.png](Reguistro%20visual/pruebas/prueba-5.png)

**`prueba-6.png`**: PostgreSQL: 5 tests de denegación en OK, suite completa con 178 tests y `seed_rbac` idempotente (84 recursos). 19:11.

![prueba-6.png](Reguistro%20visual/pruebas/prueba-6.png)

**`prueba-7.png`**: MySQL: variables del `.env` (solo nombres), respaldo `.env.postgres.bak`, conexión OK y 178 tests en 47,340 s, OK. 19:14.

![prueba-7.png](Reguistro%20visual/pruebas/prueba-7.png)

**`prueba-8.png`**: SQL Server: conexión OK (`microsoft`) y 178 tests en 45,562 s, OK; restaura el `.env` a PostgreSQL. 19:16.

![prueba-8.png](Reguistro%20visual/pruebas/prueba-8.png)

**`prueba-9.png`**: Oracle: conexión OK al servicio `XEPDB1` y primera corrida con 18 errores `LIMIT/OFFSET is not supported with select_for_update`. 19:17.

![prueba-9.png](Reguistro%20visual/pruebas/prueba-9.png)

**`Captura de pantalla (952).png`**: Búsqueda de `select_for_update` en el código y lista de los tests de refresh y logout que fallaron en Oracle.

![Captura de pantalla (952).png](Reguistro%20visual/pruebas/Captura%20de%20pantalla%20%28952%29.png)

**`Captura de pantalla (953).png`**: Parche en `auth_views.py` (líneas 131 y 198) y nueva corrida completa en Oracle: OK. 19:27.

![Captura de pantalla (953).png](Reguistro%20visual/pruebas/Captura%20de%20pantalla%20%28953%29.png)


---


## 8. Desviaciones respecto a la guía

| Tema | Guía | BrasaGo |
|---|---|---|
| Refresh token | Valor en la base | Solo `token_hash` (SHA-256); el valor en claro nunca se guarda |
| Estado del token | `is_valid` booleano | Columna `is_valid` con `ACTIVE`/`INACTIVE` (convención del curso) |
| Autorización | Rol con permisos | Denegar por defecto: 401 sin identidad y 403 sin permiso, por método y patrón de ruta |
| Perfil, login, refresh y logout | Pueden sembrarse | Quedan fuera de la matriz (84 recursos sembrados) |
| Tablas de negocio | StoreLab | Seis tablas más: reservas, insumos, recetas_insumos, pagos, domiciliarios y entregas |
| Tablas de auditoría | (no se piden) | No modeladas; se harían con triggers en la base si se exigen |
| `grant_all_access` | no existe | Solo desarrollo: no debe usarse en producción |
| Oracle | Sin verificar en la guía (`ORA-28000`, `ORA-01017`) | Verificado con usuario propio y con el ajuste de `select_for_update` |

---


## 9. Seguridad de la evidencia y pendientes

- En las capturas de ISS-14 (`iss-14-13.png`, `iss-14-14.png`), ISS-17 (`iss-17-6.png`) e ISS-23 (`iss-23-8.png` a `iss-23-11.png`) se **ocultaron** contraseñas de bases de datos, tokens y cabeceras `Authorization`. Algunas líneas vecinas quedaron también tapadas.
- Las contraseñas de los motores se mostraron en comandos y chats de trabajo: conviene rotarlas antes de publicar el repositorio.
- `.env.example` contiene solo marcadores (`tu_password_aqui`); `.env` está en `.gitignore`.
- Pendientes recomendados: límite de intentos en el login (throttling) y tablas `*_audit` si el profesor las exige.

---


## Anexo: contexto del proyecto

Documentos de referencia que originan el modelo de datos.


**`BrasaGo.png`**: Narrativa del proyecto BrasaGo y entidades de negocio sugeridas 

![BrasaGo.png](Reguistro%20visual/Contexto/BrasaGo.png)

**`BrasaGo 2 - brasago.png`**: Diagrama entidad-relación de la base de datos `brasago` (12 tablas de negocio, tablas RBAC y tablas de auditoría).

![BrasaGo 2 - brasago - public.png](Reguistro%20visual/Contexto/BrasaGo%202%20-%20brasago%20-%20public.png)

**`rback.png`**: Modelo transversal de autenticación y autorización RBAC definido para los proyectos.

![rback.png](Reguistro%20visual/Contexto/rback.png)
