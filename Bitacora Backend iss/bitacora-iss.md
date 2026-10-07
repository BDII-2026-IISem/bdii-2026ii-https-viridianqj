# Bitácora de ISS: backend de BrasaGo (Django + DRF)

Registro del avance del backend de **BrasaGo** (sistema omnicanal de restaurante) siguiendo la guía **Backend-2026 · Django + DRF (StoreLab)**. Cada unidad (ISS) resume qué se hizo, qué se adaptó respecto a la guía, cómo se verificó y qué capturas lo respaldan.

| | |
|---|---|
| **Proyecto** | BrasaGo, Proyectos Integradores 2026-II (Desarrollo Web) |
| **Autor** | Elkin Eliecer Aguas Giraldo|
| **Alcance** | Proyecto individual, solo la parte de negocio (sin autenticación ni RBAC) |
| **Guía de referencia** | [Aprendizaje ISS-00](https://www.tecnogua.com/academic/site/backend2026/django/aprendizaje/ISS-00-aprendizaje/) y enlaces *Construir* de cada ISS |
| **Unidades documentadas** | ISS-00 a ISS-13 |


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
| ISS-14 | OpenAPI |  pendiente | | |


---

## 2. Entorno y versiones

| Componente | Versión |
|---|---|
| Python | 3.14 |
| Django | 5.2.17 |
| Django REST Framework | 3.17.2 |
| djangorestframework-camel-case | 1.4.2 |
| django-cors-headers | 4.9.0 |
| Motor de base de datos | PostgreSQL (psycopg 3.3.6); drivers de MySQL, SQL Server y Oracle instalados |
| Sistema | Ubuntu sobre WSL (Windows) |

la guía fija Python 3.12, pero el proyecto se ejecutó con 3.14.

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

---

## 4. Estructura actual

```
backend/ISS-00/
├── manage.py
├── requirements.txt
├── .env / .env.example / .gitignore
├── config/
│   ├── settings/__init__.py      (database_from_environ, REST_FRAMEWORK, CORS)
│   ├── project_python.py
│   ├── urls.py                   (admin/ y api/)
│   └── wsgi.py / asgi.py
└── apps/
    ├── common/      status.py, models.py, test_admin.py
    ├── security/    User personalizado (AUTH_USER_MODEL)
    ├── client/      models, serializers, views, urls, admin, tests
    ├── product/     models, serializers, views, urls, admin, tests
    ├── venue/       models (Branch, DiningTable), admin
    └── sale/        models, managers, serializers, views, urls, admin, tests
```

### Tablas del modelo (base `brasago_django`)

`users`, `clientes`, `productos`, `sedes`, `mesas`, `pedidos`, `detalles_pedidos` y las tablas propias de Django (`auth_*`, `django_*`).

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

---


## Anexo: contexto del proyecto

Documentos de referencia que originan el modelo de datos.


**`BrasaGo.png`**: Narrativa del proyecto BrasaGo y entidades de negocio sugeridas 

![BrasaGo.png](Reguistro%20visual/Contexto/BrasaGo.png)

**`BrasaGo 2 - brasago.png`**: Diagrama entidad-relación de la base de datos `brasago` (12 tablas de negocio, tablas RBAC y tablas de auditoría).

![BrasaGo 2 - brasago - public.png](Reguistro%20visual/Contexto/BrasaGo%202%20-%20brasago%20-%20public.png)

**`rback.png`**: Modelo transversal de autenticación y autorización RBAC definido para los proyectos.

![rback.png](Reguistro%20visual/Contexto/rback.png)
