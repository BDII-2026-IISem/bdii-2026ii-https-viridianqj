# proceso.md: paso a paso del trabajo (BrasaGo)

**Estudiante:** Elkin Eliecer Aguas Giraldo, Ingeniería de Sistemas, Universidad de La Guajira
**Curso:** Base de Datos II, 2026-II
**Proyecto:** BrasaGo, sistema omnicanal de restaurante

Este archivo es el índice del proceso. Cada paso apunta al documento con el detalle, el código y las capturas. El historial de `git log` muestra la evolución en el tiempo.

---

## Primera parte: base de datos en cuatro motores

Motores: MySQL 8.0, PostgreSQL 17, SQL Server 2022 y Oracle XE 21, todos en Docker.

| Paso | Qué se hizo | Documento |
|---|---|---|
| 1 | Instalación de los cuatro motores con Docker y verificación de que están `healthy` | [paso a paso instalacion motores de bd](paso%20a%20paso%20instalacion%20motores%20de%20bd/README-motores-bd.md) y [instalacion-modelos-base-datos-2.md](paso%20a%20paso%20instalacion%20motores%20de%20bd/instalacion-modelos-base-datos-2.md) |
| 2 | Creación de la base de datos de BrasaGo, sus tablas y relaciones en cada motor | [Bitacora_de_creacion_de_base_de_datos.md](bitacora/Bitacora_de_creacion_de_base_de_datos.md) |
| 3 | Carga de datos de prueba (CSV generados) | carpeta [insertados](bitacora%20consultas/insertados/) |
| 4 | Consultas con narrativa: crear, leer, JOIN, filtros, LIKE, agrupamiento y subconsulta (8 consultas y variantes por motor) | [Bitacora_de_consultas_de_base_de_datos.md](bitacora%20consultas/Bitacora_de_consultas_de_base_de_datos.md), secciones 2 a 5 |
| 5 | **Consultas avanzadas y procedimientos almacenados con parámetros**: las consultas del paso 4 se convierten en 6 procedimientos y se agregan 3 consultas avanzadas (función de ventana `RANK`, CTE y `SUM OVER`) | misma bitácora, sección 7 (código completo por motor, narrativa y capturas) |
| 6 | **Triggers** de auditoría inmutable sobre `pedidos`, `detalles_pedidos` y `productos` (INSERT, UPDATE, DELETE y triggers de guardia) | misma bitácora, sección 6 |

### Cómo se hizo cada procedimiento (método)

1. Se parte de una consulta de la bitácora y se escribe su **narrativa de negocio** (quién la necesita y para qué).
2. Se identifican los valores que cambian (fechas, patrón, producto, mes) y se vuelven **parámetros** `p_...`.
3. Se escribe el procedimiento en cada motor, adaptando la sintaxis:
   - MySQL y SQL Server: procedimiento que devuelve el `SELECT`.
   - PostgreSQL: función `RETURNS TABLE` para lecturas y `PROCEDURE` para el alta.
   - Oracle: procedimiento con cursor de salida (`SYS_REFCURSOR`) y alias de tabla sin `AS`.
4. Se ejecuta el script de creación y se captura (`funcion_N.png`).
5. Se llama el procedimiento con valores de prueba y se captura el resultado (`llamada-N.png`).

| SP | Procedimiento | Consulta de origen |
|---|---|---|
| 01 | `sp_crear_cliente` | 1 (INSERT) |
| 02 | `sp_buscar_clientes_por_email` | 5.1 y 5.2 (LIKE) |
| 03 | `sp_pedidos_por_fecha` | 3.3 y 4.2 (JOIN y fecha) |
| 04 | `sp_detalle_ventas_rango` | 5.3 (cuatro JOIN) |
| 05 | `sp_ventas_por_cliente` | 7 (GROUP BY) |
| 06 | `sp_clientes_sin_pedidos` | 8 (NOT IN) |
| 07 | `sp_ranking_productos_mes` | Avanzada: `RANK() OVER` |
| 08 | `sp_clientes_sobre_promedio` | Avanzada: CTE |
| 09 | `sp_ventas_diarias_acumuladas` | Avanzada: `SUM() OVER` |

### Incidencia conocida

En SQL Server las llamadas de `sp_detalle_ventas_rango` y `sp_ranking_productos_mes` no devuelven filas porque la tabla `detalles_pedidos` de ese motor no tiene los datos de prueba cargados. Los mismos procedimientos devuelven resultados en PostgreSQL, MySQL y Oracle.

---

## Segunda parte: proyecto Django (solo parte de negocio)

Backend Django 5.2 + Django REST Framework siguiendo la guía Backend-2026 (StoreLab), adaptado al modelo de BrasaGo. Bitácora completa de las unidades ISS-00 a ISS-25: [bitacora-iss.md](Bitacora%20Backend%20iss/bitacora-iss.md). Código en la carpeta [backend](backend/).

| Paso | Qué se hizo | Unidad (ISS) |
|---|---|---|
| 1 | Entorno, proyecto Django y settings con selección de motor (`DB_ENGINE`) | ISS-00, ISS-01 |
| 2 | Apps `client`, `product`, `sale`, `venue`, y modelos del negocio (Client, Product, Order, OrderDetail, Branch, DiningTable) | ISS-02 a ISS-06 |
| 3 | Serializers con JSON camelCase y API REST con ModelViewSet (clientes, catálogo, pedidos), disponibles, registro y anulación de pedidos | ISS-07 a ISS-12 |
| 4 | Django Admin | ISS-13 |
| 5 | **OpenAPI: Swagger UI y ReDoc** | ISS-14 |
| 6 | Extensión del negocio: reservas, insumos, recetas, pagos, domiciliarios y entregas | Extensión |
| 7 | Autenticación JWT y RBAC (referencia, no es parte del alcance de negocio) | ISS-15 a ISS-25 |

### Pruebas

**1. Pruebas automáticas.** `python manage.py test`: 178 pruebas OK en PostgreSQL, MySQL, SQL Server y Oracle (ver [multidialect.md](Bitacora%20Backend%20iss/multidialect.md)).

**2. Pruebas HTTP** (desde el terminal con `curl`; el servidor se levanta con `python manage.py runserver`):

```bash
# Crear un producto
curl -X POST http://127.0.0.1:8000/api/productos/ \
  -H "Content-Type: application/json" \
  -d '{"sku":"BRG-001","name":"Bandeja paisa","price":"32000.00"}'

# Listar productos disponibles
curl http://127.0.0.1:8000/api/productos/disponibles/

# Registrar un pedido
curl -X POST http://127.0.0.1:8000/api/pedidos/ \
  -H "Content-Type: application/json" \
  -d '{"branchId":1,"channel":"RECOGIDA","items":[{"productId":1,"quantity":2}]}'
```

Evidencia: capturas de `iss-11-*` e `iss-13-12.png` en [Reguistro visual](Bitacora%20Backend%20iss/Reguistro%20visual/). Desde ISS-22 las rutas de negocio exigen un token `Bearer` (se obtiene en `POST /api/auth/login/`).

**3. Swagger.** Documentación interactiva en `http://127.0.0.1:8000/api/schema/swagger-ui/` (y ReDoc en `/api/schema/redoc/`). Se probaron los endpoints con "Try it out" (ver capturas `iss-14-9.png` a `iss-14-11.png` y `iss-23-8.png` a `iss-23-11.png`).

### Notas de la verificación

- Misma base de código y mismas migraciones en los cuatro motores. En Oracle hubo que ajustar `select_for_update()` (no admite `LIMIT`).
- Los detalles de incidencias y correcciones están en la sección 6 de [bitacora-iss.md](Bitacora%20Backend%20iss/bitacora-iss.md).

---

## Historial de commits

Cada commit del repositorio es una entrega del trabajo; el orden cronológico se ve con `git log --reverse`.

| Fecha | Contenido |
|---|---|
| 2026-08-30 | Primer paso: repositorio e instalación de los motores |
| 2026-09-16 | Creación de las bases de datos por terminal y visualizador |
| 2026-09-22 | Documentación de consultas SQL |
| 2026-09-27 | Actualización de la documentación de consultas SQL (triggers) |
| 2026-10-07 | Avances de los ISS del backend |
| 2026-10-11 | Actualización del ISS del backend |
