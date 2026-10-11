# BITÁCORA DE CONSULTAS DE BASE DE DATOS
UNIVERSIDAD DE LA GUAJIRA
Facultad de Ingeniería — Ingeniería de Sistemas
Proyecto BrasaGo

# 1. Introducción
Esta bitácora documenta el proceso de creación de la base de datos del proyecto BrasaGo y la ejecución de un conjunto de consultas SQL representativas (consultas combinadas, agrupaciones y subconsultas) en los cuatro motores exigidos por el curso: MySQL, PostgreSQL, SQL Server y Oracle.
Para cada motor se presenta la misma batería de 8 consultas (con sus variantes), señalando las diferencias de sintaxis relevantes entre motores, junto con la evidencia visual de su ejecución. Cada consulta incluye además un **contexto de negocio**: el motivo operativo real de BrasaGo que llevó a ejecutar ese cambio o esa lectura sobre la base de datos.
La sección 6 presenta un patrón de auditoría inmutable (triggers) sobre `pedidos`, `detalles_pedidos` y `productos`, implementado en los cuatro motores. Finalmente, la sección 7 convierte las consultas en procedimientos almacenados con parámetros y agrega tres consultas avanzadas (función de ventana y CTE), también en los cuatro motores.

# 2. Motor: MySQL

Herramienta utilizada: DBeaver / terminal mysql

## 1. Create — Insertar un nuevo cliente

Inserta un registro nuevo en la tabla clientes con datos de prueba.

**Contexto de negocio:** Se registra un nuevo cliente porque un comensal se acaba de vincular al programa de fidelización de BrasaGo desde la app; sin este INSERT no podría asociarse ningún pedido a su cuenta.

```sql
INSERT INTO clientes(tipo_documento, numero_documento, nombre, telefono, email)
VALUES ("CC", "1043680256","Jaider Quintero Mendoza", "3122589615", "jq@example.com");
```

*Evidencia:* ![paso-1.png](Registro%20visual/mysql/paso-1.png)

## 2. Read — Consultar todos los clientes

Recupera todas las columnas y filas de la tabla clientes.

**Contexto de negocio:** El equipo de administración necesita revisar el padrón completo de clientes para depurar duplicados antes de la campaña de fidelización del mes.

```sql
SELECT * FROM clientes;
```

*Evidencia:* ![paso-2.png](Registro%20visual/mysql/paso-2.png)

## 2.1. Read — Seleccionar columnas específicas

Limita el resultado a nombre, telefono y email, evitando traer columnas innecesarias.

**Contexto de negocio:** El área de marketing solo necesita nombre, teléfono y correo para preparar el envío de las promociones de fin de semana, sin exponer datos innecesarios del cliente.

```sql
SELECT nombre, telefono, email
FROM clientes;
```

*Evidencia:* ![paso-2.1.png](Registro%20visual/mysql/paso-2.1.png)

## 2.2. Read — Uso de alias de tabla

Repite la consulta anterior usando un alias (C) para la tabla clientes.

**Contexto de negocio:** Se introduce el alias C para simplificar la lectura de la consulta antes de sumarle más tablas relacionadas en los pasos siguientes.

```sql
SELECT C.nombre, C.telefono, C.email
FROM clientes AS C;
```

*Evidencia:* ![paso-2.2.png](Registro%20visual/mysql/paso-2.2.png)

## 3. Consultar varias tablas (join implícito)

Combina clientes y pedidos mediante una condición WHERE que iguala las claves relacionadas.

**Contexto de negocio:** El área de cocina necesita saber qué pedidos corresponden a cada cliente para priorizar la preparación de los domicilios; se combinan clientes y pedidos por el campo cliente_id.

```sql
SELECT *
FROM clientes, pedidos
WHERE clientes.id = pedidos.cliente_id
```

*Evidencia:* ![paso-3.png](Registro%20visual/mysql/paso-3.png)

## 3.1. Join implícito con alias

Misma consulta anterior, usando alias C y p para abreviar los nombres de tabla.

**Contexto de negocio:** Se abrevian los nombres de tabla con alias para que la consulta sea más legible cuando se agreguen más condiciones de filtro en los siguientes pasos.

```sql
SELECT * FROM clientes AS C, pedidos AS p
WHERE C.id = p.cliente_id;
```

*Evidencia:* ![paso-3.1.png](Registro%20visual/mysql/paso-3.1.png)

## 3.2. Selección de columnas específicas con join implícito

Trae solo nombre y email del cliente, junto con todas las columnas de pedidos.

**Contexto de negocio:** El área de atención al cliente solo necesita el nombre y el correo del cliente junto con el detalle completo del pedido para resolver un reclamo puntual.

```sql
SELECT C.nombre, C.email, p.*
FROM clientes AS C, pedidos AS p
WHERE C.id = p.cliente_id;
```

*Evidencia:* ![paso-3.2.png](Registro%20visual/mysql/paso-3.2.png)

## 3.3. Join explícito (JOIN ON)

Misma consulta que 3.2, pero usando la sintaxis estándar JOIN ... ON, más legible y recomendada.

**Contexto de negocio:** Se migra a la sintaxis JOIN ... ON, recomendada por el curso, porque separa claramente la condición de relación entre tablas de los filtros de negocio.

```sql
SELECT C.nombre, C.email, p.*
FROM clientes AS C
JOIN pedidos AS p ON (C.id = p.cliente_id);
```

*Evidencia:* ![paso-3.3.png](Registro%20visual/mysql/paso-3.3.png)

## 4. Filtro por fecha (join implícito)

Agrega una condición adicional en el WHERE para filtrar pedidos de una fecha puntual.

**Contexto de negocio:** Un cliente reclama por un pedido puntual realizado en una fecha exacta; se filtra por esa fecha para ubicar el registro y resolver la inconsistencia reportada.

```sql
SELECT C.nombre, C.email, p.*
FROM clientes AS C, pedidos AS p
WHERE C.id = p.cliente_id AND fecha = "2026-05-18 19:19:29";
```

*Evidencia:* ![paso-4.png](Registro%20visual/mysql/paso-4.png)

## 4.2. Filtro por fecha (join explícito)

Misma condición de fecha, aplicada sobre la sintaxis JOIN ON.

**Contexto de negocio:** Se repite el mismo filtro de fecha usando JOIN ... ON para mantener la consistencia de sintaxis del resto de consultas del proyecto.

```sql
SELECT C.nombre, C.email, p.*
FROM clientes AS C
JOIN pedidos AS p ON (C.id = p.cliente_id)
WHERE fecha = "2026-05-18 19:19:29";
```

*Evidencia:* ![paso-4.2.png](Registro%20visual/mysql/paso-4.2.png)

## 5.1. Operador LIKE — emails que inician con 'm'

Usa el patrón 'm%' para encontrar emails cuyo primer carácter sea la letra m.

**Contexto de negocio:** Soporte técnico necesita ubicar a los clientes cuyo correo comienza con 'm' para una migración de dominio de correo programada por la operadora.

```sql
SELECT * FROM clientes AS C
WHERE C.email LIKE 'm%';
```

*Evidencia:* ![paso-5.1.png](Registro%20visual/mysql/paso-5.1.png)

## 5.2. Operador LIKE con CONCAT — dominio example

Construye el patrón '%example%' dinámicamente para ubicar cualquier correo de ese dominio.

**Contexto de negocio:** Se construye dinámicamente el patrón de búsqueda para ubicar todos los clientes registrados con correos del dominio de pruebas 'example.com', usado durante el piloto del sistema.

```sql
SELECT * FROM clientes AS C
WHERE C.email LIKE CONCAT('%','example','%');
```

*Evidencia:* ![paso-5.2.png](Registro%20visual/mysql/paso-5.2.png)

## 5.3. Múltiples JOIN con rango de fechas y ORDER BY

Une clientes, pedidos, detalles_pedidos y productos; filtra por rango de fechas y ordena ascendentemente.

**Contexto de negocio:** Gerencia solicita un reporte de ventas por producto en un rango de fechas puntual (por ejemplo, para medir el impacto de una promoción); se combinan las cuatro tablas para obtener el detalle completo del pedido.

```sql
SELECT * FROM clientes AS C
JOIN pedidos AS p ON C.id = p.cliente_id 
JOIN detalles_pedidos AS dp ON p.id = dp.pedido_id 
JOIN productos AS Pr ON Pr.id = dp.producto_id
WHERE 
p.fecha BETWEEN "2026-07-04" AND "2026-07-13"
ORDER BY p.fecha ASC;
```

*Evidencia:* ![paso-5.3.png](Registro%20visual/mysql/paso-5.3.png)

## 6. Describir estructura de una tabla

Muestra las columnas, tipos de dato y restricciones de la tabla detalles_pedidos.

**Contexto de negocio:** Antes de escribir la consulta de agrupamiento se revisa la estructura de la tabla para confirmar los nombres exactos de las columnas y evitar errores de sintaxis en el siguiente paso.

```sql
DESCRIBE detalles_pedidos;
```

*Evidencia:* ![paso-6.png](Registro%20visual/mysql/paso-6.png)

## 7. Consulta de agrupamiento (SUM, COUNT, AVG)

Agrupa los pedidos por cliente dentro de un rango de fechas, calculando totales, cantidad y promedio.

**Contexto de negocio:** Gerencia pide un reporte de ventas por cliente en un periodo determinado (total facturado, número de pedidos y ticket promedio) para identificar a los clientes más valiosos del restaurante.

```sql
SELECT C.id, C.nombre, SUM(p.total) AS TotalSuma,
  COUNT(p.cliente_id) AS CuentaTotal, AVG(p.total) AS Promedio
FROM clientes AS C, pedidos AS p
WHERE C.id = p.cliente_id AND p.fecha BETWEEN "2026-07-04" AND "2026-07-13"
GROUP BY C.id
ORDER BY TotalSuma DESC;
```

*Evidencia:* ![paso-7.png](Registro%20visual/mysql/paso-7.png)

## 8. Subconsulta — clientes sin pedidos en un rango

Usa NOT IN con una subconsulta para listar clientes que no registraron pedidos en marzo de 2026.

**Contexto de negocio:** Marketing necesita detectar a los clientes que no registraron pedidos en un mes para incluirlos en una campaña de reactivación por correo.

```sql
SELECT * FROM clientes AS C
WHERE C.id NOT IN (
  SELECT p.cliente_id FROM pedidos AS p
  WHERE p.fecha BETWEEN "2026-03-01" AND "2026-03-30");
```

*Evidencia:* ![paso-8.png](Registro%20visual/mysql/paso-8.png)

# 3. Motor: PostgreSQL

Herramienta utilizada: pgAdmin / psql

## 1. Create — Insertar un nuevo cliente

Inserta un registro nuevo en la tabla clientes con datos de prueba.

**Contexto de negocio:** Se registra un nuevo cliente porque un comensal se acaba de vincular al programa de fidelización de BrasaGo desde la app; sin este INSERT no podría asociarse ningún pedido a su cuenta.

```sql
INSERT INTO clientes (tipo_documento, numero_documento, nombre, telefono, email)
VALUES ('TI', '1043682056', 'Adriana Perez Mindiola', '3122564215', 'perz@example.com');

```

*Evidencia:* ![paso-1.png](Registro%20visual/postgresql/paso-1.png)

## 2. Read — Consultar todos los clientes

Recupera todas las columnas y filas de la tabla clientes.

**Contexto de negocio:** El equipo de administración necesita revisar el padrón completo de clientes para depurar duplicados antes de la campaña de fidelización del mes.

```sql
SELECT * FROM clientes;
```

*Evidencia:* ![paso-2.png](Registro%20visual/postgresql/paso-2.png)

## 2.1. Read — Seleccionar columnas específicas

Limita el resultado a nombre, telefono y email, evitando traer columnas innecesarias.

**Contexto de negocio:** El área de marketing solo necesita nombre, teléfono y correo para preparar el envío de las promociones de fin de semana, sin exponer datos innecesarios del cliente.

```sql
SELECT nombre, telefono, email FROM clientes;
```

*Evidencia:* ![paso-2.1.png](Registro%20visual/postgresql/paso-2.1.png)

## 2.2. Read — Uso de alias de tabla

Repite la consulta anterior usando un alias (C) para la tabla clientes.

**Contexto de negocio:** Se introduce el alias C para simplificar la lectura de la consulta antes de sumarle más tablas relacionadas en los pasos siguientes.

```sql
SELECT C.nombre, C.telefono, C.email FROM clientes AS C;
```

*Evidencia:* ![paso-2.2.png](Registro%20visual/postgresql/paso-2.2.png)

## 3. Consultar varias tablas (join implícito)

Combina clientes y pedidos mediante una condición WHERE que iguala las claves relacionadas.

**Contexto de negocio:** El área de cocina necesita saber qué pedidos corresponden a cada cliente para priorizar la preparación de los domicilios; se combinan clientes y pedidos por el campo cliente_id.

```sql
SELECT * FROM clientes, pedidos
WHERE clientes.id = pedidos.cliente_id;
```

*Evidencia:* ![paso-3.png](Registro%20visual/postgresql/paso-3.png)

## 3.1. Join implícito con alias

Misma consulta anterior, usando alias C y p para abreviar los nombres de tabla.

**Contexto de negocio:** Se abrevian los nombres de tabla con alias para que la consulta sea más legible cuando se agreguen más condiciones de filtro en los siguientes pasos.

```sql
SELECT * FROM clientes AS C, pedidos AS p
WHERE C.id = p.cliente_id;
```

*Evidencia:* ![paso-3.1.png](Registro%20visual/postgresql/paso-3.1.png)

## 3.2. Selección de columnas específicas con join implícito

Trae solo nombre y email del cliente, junto con todas las columnas de pedidos.

**Contexto de negocio:** El área de atención al cliente solo necesita el nombre y el correo del cliente junto con el detalle completo del pedido para resolver un reclamo puntual.

```sql
SELECT C.nombre, C.email, p.*
FROM clientes AS C, pedidos AS p
WHERE C.id = p.cliente_id;
```

*Evidencia:* ![paso-3.2.png](Registro%20visual/postgresql/paso-3.2.png)

## 3.3. Join explícito (JOIN ON)

Misma consulta que 3.2, pero usando la sintaxis estándar JOIN ... ON, más legible y recomendada.

**Contexto de negocio:** Se migra a la sintaxis JOIN ... ON, recomendada por el curso, porque separa claramente la condición de relación entre tablas de los filtros de negocio.

```sql
SELECT C.nombre, C.email, p.*
FROM clientes AS C
JOIN pedidos AS p ON (C.id = p.cliente_id);
```

*Evidencia:* ![paso-3.3.png](Registro%20visual/postgresql/paso-3.3.png)

## 4. Filtro por fecha (join implícito)

Agrega una condición adicional en el WHERE para filtrar pedidos de una fecha puntual.

**Contexto de negocio:** Un cliente reclama por un pedido puntual realizado en una fecha exacta; se filtra por esa fecha para ubicar el registro y resolver la inconsistencia reportada.

```sql
SELECT C.nombre, C.email, p.*
FROM clientes AS C
JOIN pedidos AS p ON (C.id = p.cliente_id)
WHERE p.fecha = '2026-07-13 18:12:10';
```

*Evidencia:* ![paso-4.png](Registro%20visual/postgresql/paso-4.png)

## 4.2. Filtro por fecha (join explícito)

Misma condición de fecha, aplicada sobre la sintaxis JOIN ON.

**Contexto de negocio:** Se repite el mismo filtro de fecha usando JOIN ... ON para mantener la consistencia de sintaxis del resto de consultas del proyecto.

```sql
SELECT C.nombre, C.email, p.*
FROM clientes AS C
JOIN pedidos AS p ON (C.id = p.cliente_id)
WHERE p.fecha = '2026-07-13 18:12:10';
```

*Evidencia:* ![paso-4.2.png](Registro%20visual/postgresql/paso-4.2.png)

## 5.1. Operador LIKE — emails que inician con 'm'

Usa el patrón 'm%' para encontrar emails cuyo primer carácter sea la letra m.

**Contexto de negocio:** Soporte técnico necesita ubicar a los clientes cuyo correo comienza con 'm' para una migración de dominio de correo programada por la operadora.

```sql
SELECT * FROM clientes AS C WHERE C.email LIKE 'm%';
```

*Evidencia:* ![paso-5.1.png](Registro%20visual/postgresql/paso-5.1.png)

## 5.2. Operador LIKE con CONCAT — dominio example

Construye el patrón '%example%' dinámicamente para ubicar cualquier email de ese dominio.

**Contexto de negocio:** Se construye dinámicamente el patrón de búsqueda para ubicar todos los clientes registrados con correos del dominio de pruebas 'example.com', usado durante el piloto del sistema.

```sql
SELECT * FROM clientes AS C
WHERE C.email LIKE '%' || 'example' || '%';
```

*Evidencia:* ![paso-5.2.png](Registro%20visual/postgresql/paso-5.2.png)

## 5.3. Múltiples JOIN con rango de fechas y ORDER BY

Une clientes, pedidos, detalles_pedidos y productos; filtra por rango de fechas y ordena ascendentemente.

**Contexto de negocio:** Gerencia solicita un reporte de ventas por producto en un rango de fechas puntual (por ejemplo, para medir el impacto de una promoción); se combinan las cuatro tablas para obtener el detalle completo del pedido.

```sql
SELECT * FROM clientes AS C
JOIN pedidos AS p ON (C.id = p.cliente_id)
JOIN detalles_pedidos AS dp ON (p.id = dp.pedido_id)
JOIN productos AS Pr ON (Pr.id = dp.producto_id)
WHERE p.fecha BETWEEN '2026-07-01' AND '2026-07-30'
ORDER BY p.fecha ASC;
```

*Evidencia:* ![paso-5.3.png](Registro%20visual/postgresql/paso-5.3.png)

## 6. Describir estructura de una tabla

Muestra las columnas, tipos de dato y restricciones de la tabla detalles_pedidos.

**Contexto de negocio:** Antes de escribir la consulta de agrupamiento se revisa la estructura de la tabla para confirmar los nombres exactos de las columnas y evitar errores de sintaxis en el siguiente paso.

```sql
\d productos_ventas
-- alternativa SQL pura:
SELECT column_name, data_type FROM information_schema.columns
WHERE table_name = 'detalles_pedidos';;
```

*Evidencia:* ![paso-6.png](Registro%20visual/postgresql/paso-6.png)

## 7. Consulta de agrupamiento (SUM, COUNT, AVG)

Agrupa los pedidos por cliente dentro de un rango de fechas, calculando totales, cantidad y promedio.

**Contexto de negocio:** Gerencia pide un reporte de ventas por cliente en un periodo determinado (total facturado, número de pedidos y ticket promedio) para identificar a los clientes más valiosos del restaurante.

```sql
SELECT C.id, C.nombre, SUM(V.total) AS TotalSuma,
  COUNT(V.cliente_id) AS CuentaTotal, AVG(V.total) AS Promedio
FROM clientes AS C, ventas AS V
WHERE C.id = V.cliente_id AND V.fecha BETWEEN '2024-03-01' AND '2024-03-30'
GROUP BY C.id
ORDER BY TotalSuma DESC;
```

*Evidencia:* ![paso-7.png](Registro%20visual/postgresql/paso-7.png)

## 8. Subconsulta — clientes sin ventas en un rango

Usa NOT IN con una subconsulta para listar clientes que no registraron pedidos en marzo de 2026.

**Contexto de negocio:** Marketing necesita detectar a los clientes que no registraron pedidos en un mes para incluirlos en una campaña de reactivación por correo.

```sql
SELECT * FROM clientes AS C
WHERE C.id NOT IN (
  SELECT p.cliente_id FROM pedidos AS p
  WHERE p.fecha BETWEEN '2026-03-01' AND '2026-03-30');
```

*Evidencia:* ![paso-8.png](Registro%20visual/postgresql/paso-8.png)

# 4. Motor: SQL Server

Herramienta utilizada: SSMS / sqlcmd

## 1. Create — Insertar un nuevo cliente

Inserta un registro nuevo en la tabla clientes con datos de prueba.

**Contexto de negocio:** Se registra un nuevo cliente porque un comensal se acaba de vincular al programa de fidelización de BrasaGo desde la app; sin este INSERT no podría asociarse ningún pedido a su cuenta.

```sql
INSERT INTO clientes (tipo_documento, numero_documento, nombre, telefono, email)
VALUES ('TI', '1589489185', 'Elizabet hernandez ochoa', '3152849637', 'Elizabeth@example.com');
```

*Evidencia:* ![paso-1.png](Registro%20visual/sqlserver/paso-1.png)

## 2. Read — Consultar todos los clientes

Recupera todas las columnas y filas de la tabla clientes.

**Contexto de negocio:** El equipo de administración necesita revisar el padrón completo de clientes para depurar duplicados antes de la campaña de fidelización del mes.

```sql
SELECT * FROM clientes;
```

*Evidencia:* ![paso-2.png](Registro%20visual/sqlserver/paso-2.png)

## 2.1. Read — Seleccionar columnas específicas

Limita el resultado a nombre, telefono y email, evitando traer columnas innecesarias.

**Contexto de negocio:** El área de marketing solo necesita nombre, teléfono y correo para preparar el envío de las promociones de fin de semana, sin exponer datos innecesarios del cliente.

```sql
SELECT nombre, telefono, email FROM clientes;
```

*Evidencia:* ![paso-2.1.png](Registro%20visual/sqlserver/paso-2.1.png)

## 2.2. Read — Uso de alias de tabla

Repite la consulta anterior usando un alias (C) para la tabla clientes.

**Contexto de negocio:** Se introduce el alias C para simplificar la lectura de la consulta antes de sumarle más tablas relacionadas en los pasos siguientes.

```sql
SELECT C.nombre, C.telefono, C.email FROM clientes AS C;
```

*Evidencia:* ![paso-2.2.png](Registro%20visual/sqlserver/paso-2.2.png)

## 3. Consultar varias tablas (join implícito)

Combina clientes y pedidos mediante una condición WHERE que iguala las claves relacionadas.

**Contexto de negocio:** El área de cocina necesita saber qué pedidos corresponden a cada cliente para priorizar la preparación de los domicilios; se combinan clientes y pedidos por el campo cliente_id.

```sql
SELECT * FROM clientes, pedidos
WHERE clientes.id = pedidos.cliente_id;
```

*Evidencia:* ![paso-3.png](Registro%20visual/sqlserver/paso-3.png)

## 3.1. Join implícito con alias

Misma consulta anterior, usando alias C y p para abreviar los nombres de tabla.

**Contexto de negocio:** Se abrevian los nombres de tabla con alias para que la consulta sea más legible cuando se agreguen más condiciones de filtro en los siguientes pasos.

```sql
SELECT * FROM clientes AS C, pedidos AS p
WHERE C.id = p.cliente_id;
```

*Evidencia:* ![paso-3.1.png](Registro%20visual/sqlserver/paso-3.1.png)

## 3.2. Selección de columnas específicas con join implícito

Trae solo nombre y email del cliente, junto con todas las columnas de pedidos.

**Contexto de negocio:** El área de atención al cliente solo necesita el nombre y el correo del cliente junto con el detalle completo del pedido para resolver un reclamo puntual.

```sql
SELECT C.nombre, C.email, p.*
FROM clientes AS C, pedidos AS p
WHERE C.id = p.cliente_id;
```

*Evidencia:* ![paso-3.2.png](Registro%20visual/sqlserver/paso-3.2.png)

## 3.3. Join explícito (JOIN ON)

Misma consulta que 3.2, pero usando la sintaxis estándar JOIN ... ON, más legible y recomendada.

**Contexto de negocio:** Se migra a la sintaxis JOIN ... ON, recomendada por el curso, porque separa claramente la condición de relación entre tablas de los filtros de negocio.

```sql
SELECT C.nombre, C.email, p.*
FROM clientes AS C
JOIN pedidos AS p ON (C.id = p.cliente_id);
```

*Evidencia:* ![paso-3.3.png](Registro%20visual/sqlserver/paso-3.3.png)

## 4. Filtro por fecha (join implícito)

Agrega una condición adicional en el WHERE para filtrar pedidos de una fecha puntual.

**Contexto de negocio:** Un cliente reclama por un pedido puntual realizado en una fecha exacta; se filtra por esa fecha para ubicar el registro y resolver la inconsistencia reportada.

```sql
SELECT C.nombre, C.email, p.*
FROM clientes AS C
JOIN pedidos AS p ON (C.id = p.cliente_id)
WHERE p.fecha = '2026-07-13 18:12:10';
```

*Evidencia:* ![paso-4.png](Registro%20visual/sqlserver/paso-4.png)

## 4.2. Filtro por fecha (join explícito)

Misma condición de fecha, aplicada sobre la sintaxis JOIN ON.

**Contexto de negocio:** Se repite el mismo filtro de fecha usando JOIN ... ON para mantener la consistencia de sintaxis del resto de consultas del proyecto.

```sql
SELECT C.nombre, C.email, p.*
FROM clientes AS C
JOIN pedidos AS p ON (C.id = p.cliente_id)
WHERE p.fecha = '2026-07-13 18:12:10';
```

*Evidencia:* ![paso-4.2.png](Registro%20visual/sqlserver/paso-4.2.png)

## 5.1. Operador LIKE — emails que inician con 'm'

Usa el patrón 'm%' para encontrar correos cuyo primer carácter sea la letra m.

**Contexto de negocio:** Soporte técnico necesita ubicar a los clientes cuyo correo comienza con 'm' para una migración de dominio de correo programada por la operadora.

```sql
SELECT * FROM clientes AS C WHERE C.email LIKE 'm%';
```

*Evidencia:* ![paso-5.1.png](Registro%20visual/sqlserver/paso-5.1.png)

## 5.2. Operador LIKE con CONCAT — dominio example

Construye el patrón '%example%' dinámicamente para ubicar cualquier email de ese dominio.

**Contexto de negocio:** Se construye dinámicamente el patrón de búsqueda para ubicar todos los clientes registrados con correos del dominio de pruebas 'example.com', usado durante el piloto del sistema.

```sql
SELECT * FROM clientes AS C
WHERE C.email LIKE '%' + 'example' + '%';
```

*Evidencia:* ![paso-5.2.png](Registro%20visual/sqlserver/paso-5.2.png)

## 6. Describir estructura de una tabla

Muestra las columnas, tipos de dato y restricciones de la tabla productos.

**Contexto de negocio:** Antes de escribir la consulta de agrupamiento se revisa la estructura de la tabla para confirmar los nombres exactos de las columnas y evitar errores de sintaxis en el siguiente paso.

```sql
EXEC sp_help 'productos';
-- alternativa SQL pura:
SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'productos';
```

*Evidencia:* ![paso-6.png](Registro%20visual/sqlserver/paso-6.png)

## 7. Consulta de agrupamiento (SUM, COUNT, AVG)

Agrupa las ventas por cliente dentro de un rango de fechas, calculando totales, cantidad y promedio.

**Contexto de negocio:** Gerencia pide un reporte de ventas por cliente en un periodo determinado (total facturado, número de pedidos y ticket promedio) para identificar a los clientes más valiosos del restaurante.

```sql
SELECT C.id, C.nombre, 
       SUM(p.total) AS TotalSuma,
       COUNT(p.cliente_id) AS CuentaTotal, 
       AVG(p.total) AS Promedio
FROM clientes AS C
JOIN pedidos AS p ON C.id = p.cliente_id
WHERE p.fecha BETWEEN '2026-03-01' AND '2026-03-30'
GROUP BY C.id, C.nombre
ORDER BY TotalSuma DESC;

```

*Evidencia:* ![paso-7.png](Registro%20visual/sqlserver/paso-7.png)

## 8. Subconsulta — clientes sin ventas en un rango

Usa NOT IN con una subconsulta para listar clientes que no registraron pedidos en marzo de 2026.

**Contexto de negocio:** Marketing necesita detectar a los clientes que no registraron pedidos en un mes para incluirlos en una campaña de reactivación por correo.

```sql
SELECT * FROM clientes AS C
WHERE C.id NOT IN (
  SELECT p.cliente_id FROM pedidos AS p
  WHERE p.fecha BETWEEN '2026-07-01' AND '2026-07-30');
```

*Evidencia:* ![paso-8.png](Registro%20visual/sqlserver/paso-8.png)

# 5. Motor: Oracle

Herramienta utilizada: SQL Developer / sqlplus

## 1. Create — Insertar un nuevo cliente

Inserta un registro nuevo en la tabla clientes con datos de prueba.

**Contexto de negocio:** Se registra un nuevo cliente porque un comensal se acaba de vincular al programa de fidelización de BrasaGo desde la app; sin este INSERT no podría asociarse ningún pedido a su cuenta.

```sql
INSERT INTO clientes(tipo_documento, numero_documento, nombre, telefono, email)
VALUES ('CC', '1055784129', 'elias neron valdez', '3006185397', 'nerona@example.com');
```

*Evidencia:* ![paso-1.png](Registro%20visual/oracle/paso-1.png)

## 2. Read — Consultar todos los clientes

Recupera todas las columnas y filas de la tabla clientes.

**Contexto de negocio:** El equipo de administración necesita revisar el padrón completo de clientes para depurar duplicados antes de la campaña de fidelización del mes.

```sql
SELECT * FROM clientes;
```

*Evidencia:* ![paso-2.png](Registro%20visual/oracle/paso-2.png)

## 2.1. Read — Seleccionar columnas específicas

Limita el resultado a nombre, telefono y email, evitando traer columnas innecesarias.

**Contexto de negocio:** El área de marketing solo necesita nombre, teléfono y correo para preparar el envío de las promociones de fin de semana, sin exponer datos innecesarios del cliente.

```sql
SELECT nombre, telefono, email FROM clientes;
```

*Evidencia:* ![paso-2.1.png](Registro%20visual/oracle/paso-2.1.png)

## 2.2. Read — Uso de alias de tabla

Repite la consulta anterior usando un alias (C) para la tabla clientes.

**Contexto de negocio:** Se introduce el alias C para simplificar la lectura de la consulta antes de sumarle más tablas relacionadas en los pasos siguientes.

```sql
SELECT C.nombre, C.telefono, C.email FROM clientes C;
```

*Evidencia:* ![paso-2.2.png](Registro%20visual/oracle/paso-2.2.png)

## 3. Consultar varias tablas (join implícito)

Combina clientes y pedidos mediante una condición WHERE que iguala las claves relacionadas.

**Contexto de negocio:** El área de cocina necesita saber qué pedidos corresponden a cada cliente para priorizar la preparación de los domicilios; se combinan clientes y pedidos por el campo cliente_id.

```sql
SELECT * FROM clientes, pedidos
WHERE clientes.id = pedidos.cliente_id
```

*Evidencia:* ![paso-3.png](Registro%20visual/oracle/paso-3.png)

## 3.1. Join implícito con alias

Misma consulta anterior, usando alias C y p para abreviar los nombres de tabla.

**Contexto de negocio:** Se abrevian los nombres de tabla con alias para que la consulta sea más legible cuando se agreguen más condiciones de filtro en los siguientes pasos.

```sql
SELECT * FROM clientes C, pedidos p
WHERE C.id = p.cliente_id;
```

*Evidencia:* ![paso-3.1.png](Registro%20visual/oracle/paso-3.1.png)

## 3.2. Selección de columnas específicas con join implícito

Trae solo nombre y email del cliente, junto con todas las columnas de pedidos.

**Contexto de negocio:** El área de atención al cliente solo necesita el nombre y el correo del cliente junto con el detalle completo del pedido para resolver un reclamo puntual.

```sql
SELECT C.nombre, C.email, p.*
FROM clientes C, pedidos p
WHERE C.id = p.cliente_id;
```

*Evidencia:* ![paso-3.2.png](Registro%20visual/oracle/paso-3.2.png)

## 3.3. Join explícito (JOIN ON)

Misma consulta que 3.2, pero usando la sintaxis estándar JOIN ... ON, más legible y recomendada.

**Contexto de negocio:** Se migra a la sintaxis JOIN ... ON, recomendada por el curso, porque separa claramente la condición de relación entre tablas de los filtros de negocio.

```sql
SELECT C.nombre, C.email, p.*
FROM clientes C
JOIN pedidos p ON (C.id = p.cliente_id);
```

*Evidencia:* ![paso-3.3.png](Registro%20visual/oracle/paso-3.3.png)

## 4. Filtro por fecha (join implícito)

Agrega una condición adicional en el WHERE para filtrar pedidos de una fecha puntual.

**Contexto de negocio:** Un cliente reclama por un pedido puntual realizado en una fecha exacta; se filtra por esa fecha para ubicar el registro y resolver la inconsistencia reportada.

```sql
SELECT c.nombre, c.email, p.*
FROM clientes c
JOIN pedidos p ON c.id = p.cliente_id
WHERE p.fecha = TO_DATE('2026-05-18 19:19:29','YYYY-MM-DD HH24:MI:SS');
```

*Evidencia:* ![paso-4.png](Registro%20visual/oracle/paso-4.png)

## 4.2. Filtro por fecha (join explícito)

Misma condición de fecha, aplicada sobre la sintaxis JOIN ON.

**Contexto de negocio:** Se repite el mismo filtro de fecha usando JOIN ... ON para mantener la consistencia de sintaxis del resto de consultas del proyecto.

```sql
SELECT C.nombre, C.email, p.*
FROM clientes C
JOIN pedidos p ON (C.id = p.cliente_id)
WHERE p.fecha = TO_DATE('2026-05-18 19:19:29','YYYY-MM-DD HH24:MI:SS');
```

*Evidencia:* ![paso-4.2.png](Registro%20visual/oracle/paso-4.2.png)

## 5.1. Operador LIKE — correos que inician con 'm'

Usa el patrón 'm%' para encontrar emails cuyo primer carácter sea la letra m.

**Contexto de negocio:** Soporte técnico necesita ubicar a los clientes cuyo correo comienza con 'm' para una migración de dominio de correo programada por la operadora.

```sql
SELECT * FROM clientes C WHERE C.email LIKE 'm%';
```

*Evidencia:* ![paso-5.1.png](Registro%20visual/oracle/paso-5.1.png)

## 5.2. Operador LIKE con CONCAT — dominio example

Construye el patrón '%example%' dinámicamente para ubicar cualquier correo de ese dominio.

**Contexto de negocio:** Se construye dinámicamente el patrón de búsqueda para ubicar todos los clientes registrados con correos del dominio de pruebas 'example.com', usado durante el piloto del sistema.

```sql
SELECT * FROM clientes C
WHERE C.email LIKE '%' || 'example' || '%';
```

*Evidencia:* ![paso-5.2.png](Registro%20visual/oracle/paso-5.2.png)

## 5.3. Múltiples JOIN con rango de fechas y ORDER BY

Une clientes, pedidos, detalles_pedidos y productos; filtra por rango de fechas y ordena ascendentemente.

**Contexto de negocio:** Gerencia solicita un reporte de ventas por producto en un rango de fechas puntual (por ejemplo, para medir el impacto de una promoción); se combinan las cuatro tablas para obtener el detalle completo del pedido.

```sql
SELECT * FROM clientes C
JOIN pedidos p ON (C.id = p.cliente_id)
JOIN detalles_pedidos dp ON (p.id = dp.pedido_id)
JOIN productos Pr ON (Pr.id = dp.producto_id)
WHERE p.fecha BETWEEN TO_DATE('2026-01-01','YYYY-MM-DD')
  AND TO_DATE('2026-03-30','YYYY-MM-DD')
ORDER BY p.fecha ASC;
```

*Evidencia:* ![paso-5.3.png](Registro%20visual/oracle/paso-5.3.png)

## 6. Describir estructura de una tabla

Muestra las columnas, tipos de dato y restricciones de la tabla detalles_pedidos.

**Contexto de negocio:** Antes de escribir la consulta de agrupamiento se revisa la estructura de la tabla para confirmar los nombres exactos de las columnas y evitar errores de sintaxis en el siguiente paso.

```sql
DESCRIBE detalles_pedidos;
```

*Evidencia:* ![paso-6.png](Registro%20visual/oracle/paso-6.png)

## 7. Consulta de agrupamiento (SUM, COUNT, AVG)

Agrupa los pedidos por cliente dentro de un rango de fechas, calculando totales, cantidad y promedio.

**Contexto de negocio:** Gerencia pide un reporte de ventas por cliente en un periodo determinado (total facturado, número de pedidos y ticket promedio) para identificar a los clientes más valiosos del restaurante.

```sql
SELECT C.id, C.nombre, SUM(p.total) AS TotalSuma,
  COUNT(p.cliente_id) AS CuentaTotal, AVG(p.total) AS Promedio
FROM clientes C, pedidos p
WHERE C.id = p.cliente_id AND p.fecha BETWEEN TO_DATE('2026-03-01','YYYY-MM-DD')
  AND TO_DATE('2026-03-30','YYYY-MM-DD')
GROUP BY C.id, C.nombre
ORDER BY TotalSuma DESC;
```

*Evidencia:* ![paso-7.png](Registro%20visual/oracle/paso-7.png)

## 8. Subconsulta — clientes sin ventas en un rango

Usa NOT IN con una subconsulta para listar clientes que no registraron pedidos en marzo de 2026.

**Contexto de negocio:** Marketing necesita detectar a los clientes que no registraron pedidos en un mes para incluirlos en una campaña de reactivación por correo.

```sql
SELECT * FROM clientes C
WHERE C.id NOT IN (
  SELECT p.cliente_id FROM pedidos p
  WHERE p.fecha BETWEEN TO_DATE('2026-03-01','YYYY-MM-DD')
  AND TO_DATE('2026-03-30','YYYY-MM-DD'));
```

*Evidencia:* ![paso-8.png](Registro%20visual/oracle/paso-8.png)

# 6. Triggers

BrasaGo necesita un rastro inmutable de quién cambió qué y cuándo sobre sus registros operativos clave. En lugar de triggers sueltos, se implementa un patrón de auditoría por tabla (`pedidos`, `detalles_pedidos`, `productos`): cada tabla tiene su propia tabla `*_audit` que guarda una foto JSON del registro antes y después de cada INSERT/UPDATE/DELETE, y esa tabla de auditoría queda protegida por 3 triggers de guardia que la vuelven de solo-inserción y solo-desde-el-trigger correspondiente (nunca a mano ni desde la aplicación).

## Auditoría de `pedidos` — tabla `pedidos_audit`

**Contexto de negocio:** Gerencia y auditoría interna necesitan saber quién y cuándo cambió el estado, el total o el cliente de un pedido (por ejemplo, si un pedido se marcó como cancelado o se le cambió el total después de facturado), y que ese historial no se pueda alterar ni borrar después.

**Tabla de auditoría:**

### MySQL
```sql
CREATE TABLE IF NOT EXISTS pedidos_audit (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  pedido_id BIGINT NOT NULL,
  action_type ENUM('INSERT','UPDATE','DELETE') NOT NULL DEFAULT 'INSERT',
  changed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  changed_by VARCHAR(255) NOT NULL DEFAULT 'Admin',
  before_data JSON NULL,
  after_data JSON NULL
) ENGINE=InnoDB;
```
*Evidencia:* ![paso-1.png](Registro%20visual/triggers/paso-1.png)

### PostgreSQL
```sql
CREATE TABLE IF NOT EXISTS pedidos_audit (
  id BIGSERIAL PRIMARY KEY,
  pedido_id BIGINT NOT NULL,
  action_type VARCHAR(10) NOT NULL DEFAULT 'INSERT' CHECK (action_type IN ('INSERT','UPDATE','DELETE')),
  changed_at TIMESTAMP NOT NULL DEFAULT NOW(),
  changed_by VARCHAR(255) NOT NULL DEFAULT 'Admin',
  before_data JSONB,
  after_data JSONB
);
```
*Evidencia:* ![paso-2.png](Registro%20visual/triggers/paso-2.png)

### SQL Server
```sql
CREATE TABLE pedidos_audit (
  id BIGINT IDENTITY PRIMARY KEY,
  pedido_id BIGINT NOT NULL,
  action_type VARCHAR(10) NOT NULL DEFAULT 'INSERT' CHECK (action_type IN ('INSERT','UPDATE','DELETE')),
  changed_at DATETIME NOT NULL DEFAULT GETDATE(),
  changed_by VARCHAR(255) NOT NULL DEFAULT 'Admin',
  before_data NVARCHAR(MAX) NULL,
  after_data NVARCHAR(MAX) NULL
);
```
*Evidencia:* ![paso-3.png](Registro%20visual/triggers/paso-3.png)

### Oracle
```sql
CREATE TABLE pedidos_audit (
  id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  pedido_id NUMBER NOT NULL,
  action_type VARCHAR2(10) DEFAULT 'INSERT' NOT NULL CHECK (action_type IN ('INSERT','UPDATE','DELETE')),
  changed_at DATE DEFAULT SYSDATE NOT NULL,
  changed_by VARCHAR2(255) DEFAULT 'Admin' NOT NULL,
  before_data CLOB,
  after_data CLOB
);

-- Bandera de sesión usada por los triggers de auditoría e inmutabilidad
CREATE OR REPLACE PACKAGE pkg_audit_ctrl_pedidos AS
  from_trigger BOOLEAN := FALSE;
END pkg_audit_ctrl_pedidos;
/
```
*Evidencia:* ![paso-4.png](Registro%20visual/triggers/paso-4.png)

### Trigger AFTER INSERT sobre `pedidos`

**MySQL**
```sql
DROP TRIGGER IF EXISTS ai_pedidos_audit;
DELIMITER $$
CREATE TRIGGER ai_pedidos_audit
AFTER INSERT ON pedidos
FOR EACH ROW
BEGIN
  SET @from_pedidos_trigger = 1;
  INSERT INTO pedidos_audit (pedido_id, action_type, before_data, after_data)
  VALUES (NEW.id, 'INSERT', NULL, JSON_OBJECT(
      'id', NEW.id,
      'cliente_id', NEW.cliente_id,
      'sede_id', NEW.sede_id,
      'mesa_id', NEW.mesa_id,
      'canal', NEW.canal,
      'fecha', NEW.fecha,
      'subtotal', NEW.subtotal,
      'total', NEW.total,
      'estado', NEW.estado,
      'is_active', NEW.is_active,
      'created_at', NEW.created_at,
      'updated_at', NEW.updated_at
    ));
  SET @from_pedidos_trigger = NULL;
END$$
DELIMITER ;
```
*Evidencia:* ![paso-5.png](Registro%20visual/triggers/paso-5.png)

**PostgreSQL**
```sql
CREATE OR REPLACE FUNCTION fn_ai_pedidos_audit() RETURNS TRIGGER AS $$
BEGIN
  PERFORM set_config('myapp.from_pedidos_trigger', '1', true);
  INSERT INTO pedidos_audit (pedido_id, action_type, before_data, after_data)
  VALUES (NEW.id, 'INSERT', NULL, jsonb_build_object(
      'id', NEW.id,
      'cliente_id', NEW.cliente_id,
      'sede_id', NEW.sede_id,
      'mesa_id', NEW.mesa_id,
      'canal', NEW.canal,
      'fecha', NEW.fecha,
      'subtotal', NEW.subtotal,
      'total', NEW.total,
      'estado', NEW.estado,
      'is_active', NEW.is_active,
      'created_at', NEW.created_at,
      'updated_at', NEW.updated_at
    ));
  PERFORM set_config('myapp.from_pedidos_trigger', NULL, true);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER ai_pedidos_audit
AFTER INSERT ON pedidos
FOR EACH ROW
EXECUTE FUNCTION fn_ai_pedidos_audit();
```
*Evidencia:* ![paso-6.png](Registro%20visual/triggers/paso-6.png)

**SQL Server**
```sql
CREATE TRIGGER ai_pedidos_audit
ON pedidos
AFTER INSERT
AS
BEGIN
  SET NOCOUNT ON;
  EXEC sp_set_session_context @key = N'from_pedidos_trigger', @value = 1;

  INSERT INTO pedidos_audit (pedido_id, action_type, before_data, after_data)
  SELECT i.id, 'INSERT', NULL, (SELECT i.id AS id, i.cliente_id AS cliente_id, i.sede_id AS sede_id, i.mesa_id AS mesa_id, i.canal AS canal, i.fecha AS fecha, i.subtotal AS subtotal, i.total AS total, i.estado AS estado, i.is_active AS is_active, i.created_at AS created_at, i.updated_at AS updated_at FOR JSON PATH, WITHOUT_ARRAY_WRAPPER)
  FROM inserted i;

  EXEC sp_set_session_context @key = N'from_pedidos_trigger', @value = NULL;
END;
```
*Evidencia:* ![paso-7.png](Registro%20visual/triggers/paso-7.png)

**Oracle**
```sql
CREATE OR REPLACE TRIGGER ai_pedidos_audit
AFTER INSERT ON pedidos
FOR EACH ROW
BEGIN
  pkg_audit_ctrl_pedidos.from_trigger := TRUE;
  INSERT INTO pedidos_audit (pedido_id, action_type, before_data, after_data)
  VALUES (:NEW.id, 'INSERT', NULL, JSON_OBJECT(
      'id' VALUE :NEW.id,
      'cliente_id' VALUE :NEW.cliente_id,
      'sede_id' VALUE :NEW.sede_id,
      'mesa_id' VALUE :NEW.mesa_id,
      'canal' VALUE :NEW.canal,
      'fecha' VALUE :NEW.fecha,
      'subtotal' VALUE :NEW.subtotal,
      'total' VALUE :NEW.total,
      'estado' VALUE :NEW.estado,
      'is_active' VALUE :NEW.is_active,
      'created_at' VALUE :NEW.created_at,
      'updated_at' VALUE :NEW.updated_at
    ));
  pkg_audit_ctrl_pedidos.from_trigger := FALSE;
END;
/
```
*Evidencia:* ![paso-8.png](Registro%20visual/triggers/paso-8.png)

### Trigger AFTER UPDATE sobre `pedidos`

**MySQL**
```sql
DROP TRIGGER IF EXISTS au_pedidos_audit;
DELIMITER $$
CREATE TRIGGER au_pedidos_audit
AFTER UPDATE ON pedidos
FOR EACH ROW
BEGIN
  SET @from_pedidos_trigger = 1;
  INSERT INTO pedidos_audit (pedido_id, action_type, before_data, after_data)
  VALUES (NEW.id, 'UPDATE', JSON_OBJECT(
      'id', OLD.id,
      'cliente_id', OLD.cliente_id,
      'sede_id', OLD.sede_id,
      'mesa_id', OLD.mesa_id,
      'canal', OLD.canal,
      'fecha', OLD.fecha,
      'subtotal', OLD.subtotal,
      'total', OLD.total,
      'estado', OLD.estado,
      'is_active', OLD.is_active,
      'created_at', OLD.created_at,
      'updated_at', OLD.updated_at
    ), JSON_OBJECT(
      'id', NEW.id,
      'cliente_id', NEW.cliente_id,
      'sede_id', NEW.sede_id,
      'mesa_id', NEW.mesa_id,
      'canal', NEW.canal,
      'fecha', NEW.fecha,
      'subtotal', NEW.subtotal,
      'total', NEW.total,
      'estado', NEW.estado,
      'is_active', NEW.is_active,
      'created_at', NEW.created_at,
      'updated_at', NEW.updated_at
    ));
  SET @from_pedidos_trigger = NULL;
END$$
DELIMITER ;
```
*Evidencia:* ![paso-9.png](Registro%20visual/triggers/paso-9.png)

**PostgreSQL**
```sql
CREATE OR REPLACE FUNCTION fn_au_pedidos_audit() RETURNS TRIGGER AS $$
BEGIN
  PERFORM set_config('myapp.from_pedidos_trigger', '1', true);
  INSERT INTO pedidos_audit (pedido_id, action_type, before_data, after_data)
  VALUES (NEW.id, 'UPDATE', jsonb_build_object(
      'id', OLD.id,
      'cliente_id', OLD.cliente_id,
      'sede_id', OLD.sede_id,
      'mesa_id', OLD.mesa_id,
      'canal', OLD.canal,
      'fecha', OLD.fecha,
      'subtotal', OLD.subtotal,
      'total', OLD.total,
      'estado', OLD.estado,
      'is_active', OLD.is_active,
      'created_at', OLD.created_at,
      'updated_at', OLD.updated_at
    ), jsonb_build_object(
      'id', NEW.id,
      'cliente_id', NEW.cliente_id,
      'sede_id', NEW.sede_id,
      'mesa_id', NEW.mesa_id,
      'canal', NEW.canal,
      'fecha', NEW.fecha,
      'subtotal', NEW.subtotal,
      'total', NEW.total,
      'estado', NEW.estado,
      'is_active', NEW.is_active,
      'created_at', NEW.created_at,
      'updated_at', NEW.updated_at
    ));
  PERFORM set_config('myapp.from_pedidos_trigger', NULL, true);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER au_pedidos_audit
AFTER UPDATE ON pedidos
FOR EACH ROW
EXECUTE FUNCTION fn_au_pedidos_audit();
```
*Evidencia:* ![paso-10.png](Registro%20visual/triggers/paso-10.png)

**SQL Server**
```sql
CREATE TRIGGER au_pedidos_audit
ON pedidos
AFTER UPDATE
AS
BEGIN
  SET NOCOUNT ON;
  EXEC sp_set_session_context @key = N'from_pedidos_trigger', @value = 1;

  INSERT INTO pedidos_audit (pedido_id, action_type, before_data, after_data)
  SELECT i.id, 'UPDATE', (SELECT d.id AS id, d.cliente_id AS cliente_id, d.sede_id AS sede_id, d.mesa_id AS mesa_id, d.canal AS canal, d.fecha AS fecha, d.subtotal AS subtotal, d.total AS total, d.estado AS estado, d.is_active AS is_active, d.created_at AS created_at, d.updated_at AS updated_at FOR JSON PATH, WITHOUT_ARRAY_WRAPPER), (SELECT i.id AS id, i.cliente_id AS cliente_id, i.sede_id AS sede_id, i.mesa_id AS mesa_id, i.canal AS canal, i.fecha AS fecha, i.subtotal AS subtotal, i.total AS total, i.estado AS estado, i.is_active AS is_active, i.created_at AS created_at, i.updated_at AS updated_at FOR JSON PATH, WITHOUT_ARRAY_WRAPPER)
  FROM inserted i
  JOIN deleted d ON d.id = i.id;

  EXEC sp_set_session_context @key = N'from_pedidos_trigger', @value = NULL;
END;
```
*Evidencia:* ![paso-11.png](Registro%20visual/triggers/paso-11.png)

**Oracle**
```sql
CREATE OR REPLACE TRIGGER au_pedidos_audit
AFTER UPDATE ON pedidos
FOR EACH ROW
BEGIN
  pkg_audit_ctrl_pedidos.from_trigger := TRUE;
  INSERT INTO pedidos_audit (pedido_id, action_type, before_data, after_data)
  VALUES (:NEW.id, 'UPDATE', JSON_OBJECT(
      'id' VALUE :OLD.id,
      'cliente_id' VALUE :OLD.cliente_id,
      'sede_id' VALUE :OLD.sede_id,
      'mesa_id' VALUE :OLD.mesa_id,
      'canal' VALUE :OLD.canal,
      'fecha' VALUE :OLD.fecha,
      'subtotal' VALUE :OLD.subtotal,
      'total' VALUE :OLD.total,
      'estado' VALUE :OLD.estado,
      'is_active' VALUE :OLD.is_active,
      'created_at' VALUE :OLD.created_at,
      'updated_at' VALUE :OLD.updated_at
    ), JSON_OBJECT(
      'id' VALUE :NEW.id,
      'cliente_id' VALUE :NEW.cliente_id,
      'sede_id' VALUE :NEW.sede_id,
      'mesa_id' VALUE :NEW.mesa_id,
      'canal' VALUE :NEW.canal,
      'fecha' VALUE :NEW.fecha,
      'subtotal' VALUE :NEW.subtotal,
      'total' VALUE :NEW.total,
      'estado' VALUE :NEW.estado,
      'is_active' VALUE :NEW.is_active,
      'created_at' VALUE :NEW.created_at,
      'updated_at' VALUE :NEW.updated_at
    ));
  pkg_audit_ctrl_pedidos.from_trigger := FALSE;
END;
/
```
*Evidencia:* ![paso-12.png](Registro%20visual/triggers/paso-12.png)

### Trigger AFTER DELETE sobre `pedidos`

**MySQL**
```sql
DROP TRIGGER IF EXISTS ad_pedidos_audit;
DELIMITER $$
CREATE TRIGGER ad_pedidos_audit
AFTER DELETE ON pedidos
FOR EACH ROW
BEGIN
  SET @from_pedidos_trigger = 1;
  INSERT INTO pedidos_audit (pedido_id, action_type, before_data, after_data)
  VALUES (OLD.id, 'DELETE', JSON_OBJECT(
      'id', OLD.id,
      'cliente_id', OLD.cliente_id,
      'sede_id', OLD.sede_id,
      'mesa_id', OLD.mesa_id,
      'canal', OLD.canal,
      'fecha', OLD.fecha,
      'subtotal', OLD.subtotal,
      'total', OLD.total,
      'estado', OLD.estado,
      'is_active', OLD.is_active,
      'created_at', OLD.created_at,
      'updated_at', OLD.updated_at
    ), NULL);
  SET @from_pedidos_trigger = NULL;
END$$
DELIMITER ;
```
*Evidencia:* ![paso-13.png](Registro%20visual/triggers/paso-13.png)

**PostgreSQL**
```sql
CREATE OR REPLACE FUNCTION fn_ad_pedidos_audit() RETURNS TRIGGER AS $$
BEGIN
  PERFORM set_config('myapp.from_pedidos_trigger', '1', true);
  INSERT INTO pedidos_audit (pedido_id, action_type, before_data, after_data)
  VALUES (OLD.id, 'DELETE', jsonb_build_object(
      'id', OLD.id,
      'cliente_id', OLD.cliente_id,
      'sede_id', OLD.sede_id,
      'mesa_id', OLD.mesa_id,
      'canal', OLD.canal,
      'fecha', OLD.fecha,
      'subtotal', OLD.subtotal,
      'total', OLD.total,
      'estado', OLD.estado,
      'is_active', OLD.is_active,
      'created_at', OLD.created_at,
      'updated_at', OLD.updated_at
    ), NULL);
  PERFORM set_config('myapp.from_pedidos_trigger', NULL, true);
  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER ad_pedidos_audit
AFTER DELETE ON pedidos
FOR EACH ROW
EXECUTE FUNCTION fn_ad_pedidos_audit();
```
*Evidencia:* ![paso-14.png](Registro%20visual/triggers/paso-14.png)

**SQL Server**
```sql
CREATE TRIGGER ad_pedidos_audit
ON pedidos
AFTER DELETE
AS
BEGIN
  SET NOCOUNT ON;
  EXEC sp_set_session_context @key = N'from_pedidos_trigger', @value = 1;

  INSERT INTO pedidos_audit (pedido_id, action_type, before_data, after_data)
  SELECT d.id, 'DELETE', (SELECT d.id AS id, d.cliente_id AS cliente_id, d.sede_id AS sede_id, d.mesa_id AS mesa_id, d.canal AS canal, d.fecha AS fecha, d.subtotal AS subtotal, d.total AS total, d.estado AS estado, d.is_active AS is_active, d.created_at AS created_at, d.updated_at AS updated_at FOR JSON PATH, WITHOUT_ARRAY_WRAPPER), NULL
  FROM deleted d;

  EXEC sp_set_session_context @key = N'from_pedidos_trigger', @value = NULL;
END;
```
*Evidencia:* ![paso-15.png](Registro%20visual/triggers/paso-15.png)

**Oracle**
```sql
CREATE OR REPLACE TRIGGER ad_pedidos_audit
AFTER DELETE ON pedidos
FOR EACH ROW
BEGIN
  pkg_audit_ctrl_pedidos.from_trigger := TRUE;
  INSERT INTO pedidos_audit (pedido_id, action_type, before_data, after_data)
  VALUES (:OLD.id, 'DELETE', JSON_OBJECT(
      'id' VALUE :OLD.id,
      'cliente_id' VALUE :OLD.cliente_id,
      'sede_id' VALUE :OLD.sede_id,
      'mesa_id' VALUE :OLD.mesa_id,
      'canal' VALUE :OLD.canal,
      'fecha' VALUE :OLD.fecha,
      'subtotal' VALUE :OLD.subtotal,
      'total' VALUE :OLD.total,
      'estado' VALUE :OLD.estado,
      'is_active' VALUE :OLD.is_active,
      'created_at' VALUE :OLD.created_at,
      'updated_at' VALUE :OLD.updated_at
    ), NULL);
  pkg_audit_ctrl_pedidos.from_trigger := FALSE;
END;
/
```
*Evidencia:* ![paso-16.png](Registro%20visual/triggers/paso-16.png)

### Triggers de guardia sobre `pedidos_audit` (inmutabilidad)

Estos 3 triggers hacen que `pedidos_audit` sea de solo-inserción: nadie puede modificar o borrar un registro de auditoría, y solo puede insertarse desde los triggers de `pedidos` (nunca a mano ni desde la aplicación).

**MySQL**
```sql
DROP TRIGGER IF EXISTS biu_pedidos_audit_block_update;
DELIMITER $$
CREATE TRIGGER biu_pedidos_audit_block_update
BEFORE UPDATE ON pedidos_audit
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'pedidos_audit es inmutable: UPDATE prohibido.';
END$$
DELIMITER ;

DROP TRIGGER IF EXISTS bid_pedidos_audit_block_delete;
DELIMITER $$
CREATE TRIGGER bid_pedidos_audit_block_delete
BEFORE DELETE ON pedidos_audit
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'pedidos_audit es inmutable: DELETE prohibido.';
END$$
DELIMITER ;

DROP TRIGGER IF EXISTS bii_pedidos_audit_guard_insert;
DELIMITER $$
CREATE TRIGGER bii_pedidos_audit_guard_insert
BEFORE INSERT ON pedidos_audit
FOR EACH ROW
BEGIN
  IF COALESCE(@from_pedidos_trigger, 0) <> 1 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'INSERT en pedidos_audit solo permitido desde triggers de pedidos.';
  END IF;
END$$
DELIMITER ;
```
*Evidencia:* ![paso-17.png](Registro%20visual/triggers/paso-17.png)

**PostgreSQL**
```sql
CREATE OR REPLACE FUNCTION fn_biu_pedidos_audit_block_update() RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'pedidos_audit es inmutable: UPDATE prohibido.';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER biu_pedidos_audit_block_update
BEFORE UPDATE ON pedidos_audit
FOR EACH ROW
EXECUTE FUNCTION fn_biu_pedidos_audit_block_update();

CREATE OR REPLACE FUNCTION fn_bid_pedidos_audit_block_delete() RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'pedidos_audit es inmutable: DELETE prohibido.';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER bid_pedidos_audit_block_delete
BEFORE DELETE ON pedidos_audit
FOR EACH ROW
EXECUTE FUNCTION fn_bid_pedidos_audit_block_delete();

CREATE OR REPLACE FUNCTION fn_bii_pedidos_audit_guard_insert() RETURNS TRIGGER AS $$
BEGIN
  IF current_setting('myapp.from_pedidos_trigger', true) IS DISTINCT FROM '1' THEN
    RAISE EXCEPTION 'INSERT en pedidos_audit solo permitido desde triggers de pedidos.';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER bii_pedidos_audit_guard_insert
BEFORE INSERT ON pedidos_audit
FOR EACH ROW
EXECUTE FUNCTION fn_bii_pedidos_audit_guard_insert();
```
*Evidencia:* ![paso-18.png](Registro%20visual/triggers/paso-18.png)

**SQL Server**
```sql
-- SQL Server no soporta triggers BEFORE: se usan INSTEAD OF para bloquear/filtrar
CREATE TRIGGER biu_pedidos_audit_block_update
ON pedidos_audit
INSTEAD OF UPDATE
AS
BEGIN
    RAISERROR('pedidos_audit es inmutable: UPDATE prohibido.', 16, 1);
END;
GO

CREATE TRIGGER bid_pedidos_audit_block_delete
ON pedidos_audit
INSTEAD OF DELETE
AS
BEGIN
    RAISERROR('pedidos_audit es inmutable: DELETE prohibido.', 16, 1);
END;
GO

CREATE TRIGGER bii_pedidos_audit_guard_insert
ON pedidos_audit
INSTEAD OF INSERT
AS
BEGIN
    SET NOCOUNT ON;
    IF ISNULL(CAST(SESSION_CONTEXT(N'from_pedidos_trigger') AS INT), 0) <> 1
    BEGIN
        RAISERROR('INSERT en pedidos_audit solo permitido desde triggers de pedidos.', 16, 1);
        RETURN;
    END;
END;
GO

```
*Evidencia:* ![paso-19.png](Registro%20visual/triggers/paso-19.png)

**Oracle**
```sql
CREATE OR REPLACE TRIGGER biu_pedidos_audit_block_update
BEFORE UPDATE ON pedidos_audit
FOR EACH ROW
BEGIN
  RAISE_APPLICATION_ERROR(-20010, 'pedidos_audit es inmutable: UPDATE prohibido.');
END;
/

CREATE OR REPLACE TRIGGER bid_pedidos_audit_block_delete
BEFORE DELETE ON pedidos_audit
FOR EACH ROW
BEGIN
  RAISE_APPLICATION_ERROR(-20011, 'pedidos_audit es inmutable: DELETE prohibido.');
END;
/

CREATE OR REPLACE TRIGGER bii_pedidos_audit_guard_insert
BEFORE INSERT ON pedidos_audit
FOR EACH ROW
BEGIN
  IF NOT pkg_audit_ctrl_pedidos.from_trigger THEN
    RAISE_APPLICATION_ERROR(-20012, 'INSERT en pedidos_audit solo permitido desde triggers de pedidos.');
  END IF;
END;
/
```
*Evidencia:* ![paso-20.png](Registro%20visual/triggers/paso-20.png)

## Auditoría de `detalles_pedidos` — tabla `detalles_pedidos_audit`

**Contexto de negocio:** Cuando un cliente reclama por el detalle de su cuenta (una línea de pedido borrada, una cantidad modificada), el restaurante necesita reconstruir exactamente qué decía esa línea antes y después del cambio, sin depender de la memoria del mesero.

**Tabla de auditoría:**

### MySQL
```sql
CREATE TABLE IF NOT EXISTS detalles_pedidos_audit (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  detalle_id BIGINT NOT NULL,
  action_type ENUM('INSERT','UPDATE','DELETE') NOT NULL DEFAULT 'INSERT',
  changed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  changed_by VARCHAR(255) NOT NULL DEFAULT 'Admin',
  before_data JSON NULL,
  after_data JSON NULL
) ENGINE=InnoDB;
```
*Evidencia:* ![paso-21.png](Registro%20visual/triggers/paso-21.png)

### PostgreSQL
```sql
CREATE TABLE IF NOT EXISTS detalles_pedidos_audit (
  id BIGSERIAL PRIMARY KEY,
  detalle_id BIGINT NOT NULL,
  action_type VARCHAR(10) NOT NULL DEFAULT 'INSERT' CHECK (action_type IN ('INSERT','UPDATE','DELETE')),
  changed_at TIMESTAMP NOT NULL DEFAULT NOW(),
  changed_by VARCHAR(255) NOT NULL DEFAULT 'Admin',
  before_data JSONB,
  after_data JSONB
);
```
*Evidencia:* ![paso-22.png](Registro%20visual/triggers/paso-22.png)

### SQL Server
```sql
CREATE TABLE detalles_pedidos_audit (
  id BIGINT IDENTITY PRIMARY KEY,
  detalle_id BIGINT NOT NULL,
  action_type VARCHAR(10) NOT NULL DEFAULT 'INSERT' CHECK (action_type IN ('INSERT','UPDATE','DELETE')),
  changed_at DATETIME NOT NULL DEFAULT GETDATE(),
  changed_by VARCHAR(255) NOT NULL DEFAULT 'Admin',
  before_data NVARCHAR(MAX) NULL,
  after_data NVARCHAR(MAX) NULL
);
```
*Evidencia:* ![paso-23.png](Registro%20visual/triggers/paso-23.png)

### Oracle
```sql
CREATE TABLE detalles_pedidos_audit (
  id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  detalle_id NUMBER NOT NULL,
  action_type VARCHAR2(10) DEFAULT 'INSERT' NOT NULL CHECK (action_type IN ('INSERT','UPDATE','DELETE')),
  changed_at DATE DEFAULT SYSDATE NOT NULL,
  changed_by VARCHAR2(255) DEFAULT 'Admin' NOT NULL,
  before_data CLOB,
  after_data CLOB
);

-- Bandera de sesión usada por los triggers de auditoría e inmutabilidad
CREATE OR REPLACE PACKAGE pkg_audit_ctrl_detalles_pedidos AS
  from_trigger BOOLEAN := FALSE;
END pkg_audit_ctrl_detalles_pedidos;
/
```
*Evidencia:* ![paso-24.png](Registro%20visual/triggers/paso-24.png)

### Trigger AFTER INSERT sobre `detalles_pedidos`

**MySQL**
```sql
DROP TRIGGER IF EXISTS ai_detalles_pedidos_audit;
DELIMITER $$
CREATE TRIGGER ai_detalles_pedidos_audit
AFTER INSERT ON detalles_pedidos
FOR EACH ROW
BEGIN
  SET @from_detalles_pedidos_trigger = 1;
  INSERT INTO detalles_pedidos_audit (detalle_id, action_type, before_data, after_data)
  VALUES (NEW.id, 'INSERT', NULL, JSON_OBJECT(
      'id', NEW.id,
      'pedido_id', NEW.pedido_id,
      'producto_id', NEW.producto_id,
      'cantidad', NEW.cantidad,
      'valor_unitario', NEW.valor_unitario,
      'total', NEW.total,
      'observaciones', NEW.observaciones,
      'is_active', NEW.is_active,
      'created_at', NEW.created_at,
      'updated_at', NEW.updated_at
    ));
  SET @from_detalles_pedidos_trigger = NULL;
END$$
DELIMITER ;
```
*Evidencia:* ![paso-25.png](Registro%20visual/triggers/paso-25.png)

**PostgreSQL**
```sql
CREATE OR REPLACE FUNCTION fn_ai_detalles_pedidos_audit() RETURNS TRIGGER AS $$
BEGIN
  PERFORM set_config('myapp.from_detalles_pedidos_trigger', '1', true);
  INSERT INTO detalles_pedidos_audit (detalle_id, action_type, before_data, after_data)
  VALUES (NEW.id, 'INSERT', NULL, jsonb_build_object(
      'id', NEW.id,
      'pedido_id', NEW.pedido_id,
      'producto_id', NEW.producto_id,
      'cantidad', NEW.cantidad,
      'valor_unitario', NEW.valor_unitario,
      'total', NEW.total,
      'observaciones', NEW.observaciones,
      'is_active', NEW.is_active,
      'created_at', NEW.created_at,
      'updated_at', NEW.updated_at
    ));
  PERFORM set_config('myapp.from_detalles_pedidos_trigger', NULL, true);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER ai_detalles_pedidos_audit
AFTER INSERT ON detalles_pedidos
FOR EACH ROW
EXECUTE FUNCTION fn_ai_detalles_pedidos_audit();
```
*Evidencia:* ![paso-26.png](Registro%20visual/triggers/paso-26.png)

**SQL Server**
```sql
CREATE TRIGGER ai_detalles_pedidos_audit
ON detalles_pedidos
AFTER INSERT
AS
BEGIN
  SET NOCOUNT ON;
  EXEC sp_set_session_context @key = N'from_detalles_pedidos_trigger', @value = 1;

  INSERT INTO detalles_pedidos_audit (detalle_id, action_type, before_data, after_data)
  SELECT i.id, 'INSERT', NULL, (SELECT i.id AS id, i.pedido_id AS pedido_id, i.producto_id AS producto_id, i.cantidad AS cantidad, i.valor_unitario AS valor_unitario, i.total AS total, i.observaciones AS observaciones, i.is_active AS is_active, i.created_at AS created_at, i.updated_at AS updated_at FOR JSON PATH, WITHOUT_ARRAY_WRAPPER)
  FROM inserted i;

  EXEC sp_set_session_context @key = N'from_detalles_pedidos_trigger', @value = NULL;
END;
```
*Evidencia:* ![paso-27.png](Registro%20visual/triggers/paso-27.png)

**Oracle**
```sql
CREATE OR REPLACE TRIGGER ai_detalles_pedidos_audit
AFTER INSERT ON detalles_pedidos
FOR EACH ROW
BEGIN
  pkg_audit_ctrl_detalles_pedidos.from_trigger := TRUE;
  INSERT INTO detalles_pedidos_audit (detalle_id, action_type, before_data, after_data)
  VALUES (:NEW.id, 'INSERT', NULL, JSON_OBJECT(
      'id' VALUE :NEW.id,
      'pedido_id' VALUE :NEW.pedido_id,
      'producto_id' VALUE :NEW.producto_id,
      'cantidad' VALUE :NEW.cantidad,
      'valor_unitario' VALUE :NEW.valor_unitario,
      'total' VALUE :NEW.total,
      'observaciones' VALUE :NEW.observaciones,
      'is_active' VALUE :NEW.is_active,
      'created_at' VALUE :NEW.created_at,
      'updated_at' VALUE :NEW.updated_at
    ));
  pkg_audit_ctrl_detalles_pedidos.from_trigger := FALSE;
END;
/
```
*Evidencia:* ![paso-28.png](Registro%20visual/triggers/paso-28.png)

### Trigger AFTER UPDATE sobre `detalles_pedidos`

**MySQL**
```sql
DROP TRIGGER IF EXISTS au_detalles_pedidos_audit;
DELIMITER $$
CREATE TRIGGER au_detalles_pedidos_audit
AFTER UPDATE ON detalles_pedidos
FOR EACH ROW
BEGIN
  SET @from_detalles_pedidos_trigger = 1;
  INSERT INTO detalles_pedidos_audit (detalle_id, action_type, before_data, after_data)
  VALUES (NEW.id, 'UPDATE', JSON_OBJECT(
      'id', OLD.id,
      'pedido_id', OLD.pedido_id,
      'producto_id', OLD.producto_id,
      'cantidad', OLD.cantidad,
      'valor_unitario', OLD.valor_unitario,
      'total', OLD.total,
      'observaciones', OLD.observaciones,
      'is_active', OLD.is_active,
      'created_at', OLD.created_at,
      'updated_at', OLD.updated_at
    ), JSON_OBJECT(
      'id', NEW.id,
      'pedido_id', NEW.pedido_id,
      'producto_id', NEW.producto_id,
      'cantidad', NEW.cantidad,
      'valor_unitario', NEW.valor_unitario,
      'total', NEW.total,
      'observaciones', NEW.observaciones,
      'is_active', NEW.is_active,
      'created_at', NEW.created_at,
      'updated_at', NEW.updated_at
    ));
  SET @from_detalles_pedidos_trigger = NULL;
END$$
DELIMITER ;
```
*Evidencia:* ![paso-29.png](Registro%20visual/triggers/paso-29.png)

**PostgreSQL**
```sql
CREATE OR REPLACE FUNCTION fn_au_detalles_pedidos_audit() RETURNS TRIGGER AS $$
BEGIN
  PERFORM set_config('myapp.from_detalles_pedidos_trigger', '1', true);
  INSERT INTO detalles_pedidos_audit (detalle_id, action_type, before_data, after_data)
  VALUES (NEW.id, 'UPDATE', jsonb_build_object(
      'id', OLD.id,
      'pedido_id', OLD.pedido_id,
      'producto_id', OLD.producto_id,
      'cantidad', OLD.cantidad,
      'valor_unitario', OLD.valor_unitario,
      'total', OLD.total,
      'observaciones', OLD.observaciones,
      'is_active', OLD.is_active,
      'created_at', OLD.created_at,
      'updated_at', OLD.updated_at
    ), jsonb_build_object(
      'id', NEW.id,
      'pedido_id', NEW.pedido_id,
      'producto_id', NEW.producto_id,
      'cantidad', NEW.cantidad,
      'valor_unitario', NEW.valor_unitario,
      'total', NEW.total,
      'observaciones', NEW.observaciones,
      'is_active', NEW.is_active,
      'created_at', NEW.created_at,
      'updated_at', NEW.updated_at
    ));
  PERFORM set_config('myapp.from_detalles_pedidos_trigger', NULL, true);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER au_detalles_pedidos_audit
AFTER UPDATE ON detalles_pedidos
FOR EACH ROW
EXECUTE FUNCTION fn_au_detalles_pedidos_audit();
```
*Evidencia:* ![paso-30.png](Registro%20visual/triggers/paso-30.png)

**SQL Server**
```sql
CREATE TRIGGER au_detalles_pedidos_audit
ON detalles_pedidos
AFTER UPDATE
AS
BEGIN
  SET NOCOUNT ON;
  EXEC sp_set_session_context @key = N'from_detalles_pedidos_trigger', @value = 1;

  INSERT INTO detalles_pedidos_audit (detalle_id, action_type, before_data, after_data)
  SELECT i.id, 'UPDATE', (SELECT d.id AS id, d.pedido_id AS pedido_id, d.producto_id AS producto_id, d.cantidad AS cantidad, d.valor_unitario AS valor_unitario, d.total AS total, d.observaciones AS observaciones, d.is_active AS is_active, d.created_at AS created_at, d.updated_at AS updated_at FOR JSON PATH, WITHOUT_ARRAY_WRAPPER), (SELECT i.id AS id, i.pedido_id AS pedido_id, i.producto_id AS producto_id, i.cantidad AS cantidad, i.valor_unitario AS valor_unitario, i.total AS total, i.observaciones AS observaciones, i.is_active AS is_active, i.created_at AS created_at, i.updated_at AS updated_at FOR JSON PATH, WITHOUT_ARRAY_WRAPPER)
  FROM inserted i
  JOIN deleted d ON d.id = i.id;

  EXEC sp_set_session_context @key = N'from_detalles_pedidos_trigger', @value = NULL;
END;
```
*Evidencia:* ![paso-31.png](Registro%20visual/triggers/paso-31.png)

**Oracle**
```sql
CREATE OR REPLACE TRIGGER au_detalles_pedidos_audit
AFTER UPDATE ON detalles_pedidos
FOR EACH ROW
BEGIN
  pkg_audit_ctrl_detalles_pedidos.from_trigger := TRUE;
  INSERT INTO detalles_pedidos_audit (detalle_id, action_type, before_data, after_data)
  VALUES (:NEW.id, 'UPDATE', JSON_OBJECT(
      'id' VALUE :OLD.id,
      'pedido_id' VALUE :OLD.pedido_id,
      'producto_id' VALUE :OLD.producto_id,
      'cantidad' VALUE :OLD.cantidad,
      'valor_unitario' VALUE :OLD.valor_unitario,
      'total' VALUE :OLD.total,
      'observaciones' VALUE :OLD.observaciones,
      'is_active' VALUE :OLD.is_active,
      'created_at' VALUE :OLD.created_at,
      'updated_at' VALUE :OLD.updated_at
    ), JSON_OBJECT(
      'id' VALUE :NEW.id,
      'pedido_id' VALUE :NEW.pedido_id,
      'producto_id' VALUE :NEW.producto_id,
      'cantidad' VALUE :NEW.cantidad,
      'valor_unitario' VALUE :NEW.valor_unitario,
      'total' VALUE :NEW.total,
      'observaciones' VALUE :NEW.observaciones,
      'is_active' VALUE :NEW.is_active,
      'created_at' VALUE :NEW.created_at,
      'updated_at' VALUE :NEW.updated_at
    ));
  pkg_audit_ctrl_detalles_pedidos.from_trigger := FALSE;
END;
/
```
*Evidencia:* ![paso-32.png](Registro%20visual/triggers/paso-32.png)

### Trigger AFTER DELETE sobre `detalles_pedidos`

**MySQL**
```sql
DROP TRIGGER IF EXISTS ad_detalles_pedidos_audit;
DELIMITER $$
CREATE TRIGGER ad_detalles_pedidos_audit
AFTER DELETE ON detalles_pedidos
FOR EACH ROW
BEGIN
  SET @from_detalles_pedidos_trigger = 1;
  INSERT INTO detalles_pedidos_audit (detalle_id, action_type, before_data, after_data)
  VALUES (OLD.id, 'DELETE', JSON_OBJECT(
      'id', OLD.id,
      'pedido_id', OLD.pedido_id,
      'producto_id', OLD.producto_id,
      'cantidad', OLD.cantidad,
      'valor_unitario', OLD.valor_unitario,
      'total', OLD.total,
      'observaciones', OLD.observaciones,
      'is_active', OLD.is_active,
      'created_at', OLD.created_at,
      'updated_at', OLD.updated_at
    ), NULL);
  SET @from_detalles_pedidos_trigger = NULL;
END$$
DELIMITER ;
```
*Evidencia:* ![paso-33.png](Registro%20visual/triggers/paso-33.png)

**PostgreSQL**
```sql
CREATE OR REPLACE FUNCTION fn_ad_detalles_pedidos_audit() RETURNS TRIGGER AS $$
BEGIN
  PERFORM set_config('myapp.from_detalles_pedidos_trigger', '1', true);
  INSERT INTO detalles_pedidos_audit (detalle_id, action_type, before_data, after_data)
  VALUES (OLD.id, 'DELETE', jsonb_build_object(
      'id', OLD.id,
      'pedido_id', OLD.pedido_id,
      'producto_id', OLD.producto_id,
      'cantidad', OLD.cantidad,
      'valor_unitario', OLD.valor_unitario,
      'total', OLD.total,
      'observaciones', OLD.observaciones,
      'is_active', OLD.is_active,
      'created_at', OLD.created_at,
      'updated_at', OLD.updated_at
    ), NULL);
  PERFORM set_config('myapp.from_detalles_pedidos_trigger', NULL, true);
  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER ad_detalles_pedidos_audit
AFTER DELETE ON detalles_pedidos
FOR EACH ROW
EXECUTE FUNCTION fn_ad_detalles_pedidos_audit();
```
*Evidencia:* ![paso-34.png](Registro%20visual/triggers/paso-34.png)

**SQL Server**
```sql
CREATE TRIGGER ad_detalles_pedidos_audit
ON detalles_pedidos
AFTER DELETE
AS
BEGIN
  SET NOCOUNT ON;
  EXEC sp_set_session_context @key = N'from_detalles_pedidos_trigger', @value = 1;

  INSERT INTO detalles_pedidos_audit (detalle_id, action_type, before_data, after_data)
  SELECT d.id, 'DELETE', (SELECT d.id AS id, d.pedido_id AS pedido_id, d.producto_id AS producto_id, d.cantidad AS cantidad, d.valor_unitario AS valor_unitario, d.total AS total, d.observaciones AS observaciones, d.is_active AS is_active, d.created_at AS created_at, d.updated_at AS updated_at FOR JSON PATH, WITHOUT_ARRAY_WRAPPER), NULL
  FROM deleted d;

  EXEC sp_set_session_context @key = N'from_detalles_pedidos_trigger', @value = NULL;
END;
```
*Evidencia:* ![paso-35.png](Registro%20visual/triggers/paso-35.png)

**Oracle**
```sql
CREATE OR REPLACE TRIGGER ad_detalles_pedidos_audit
AFTER DELETE ON detalles_pedidos
FOR EACH ROW
BEGIN
  pkg_audit_ctrl_detalles_pedidos.from_trigger := TRUE;
  INSERT INTO detalles_pedidos_audit (detalle_id, action_type, before_data, after_data)
  VALUES (:OLD.id, 'DELETE', JSON_OBJECT(
      'id' VALUE :OLD.id,
      'pedido_id' VALUE :OLD.pedido_id,
      'producto_id' VALUE :OLD.producto_id,
      'cantidad' VALUE :OLD.cantidad,
      'valor_unitario' VALUE :OLD.valor_unitario,
      'total' VALUE :OLD.total,
      'observaciones' VALUE :OLD.observaciones,
      'is_active' VALUE :OLD.is_active,
      'created_at' VALUE :OLD.created_at,
      'updated_at' VALUE :OLD.updated_at
    ), NULL);
  pkg_audit_ctrl_detalles_pedidos.from_trigger := FALSE;
END;
/
```
*Evidencia:* ![paso-36.png](Registro%20visual/triggers/paso-36.png)

### Triggers de guardia sobre `detalles_pedidos_audit` (inmutabilidad)

Estos 3 triggers hacen que `detalles_pedidos_audit` sea de solo-inserción: nadie puede modificar o borrar un registro de auditoría, y solo puede insertarse desde los triggers de `detalles_pedidos` (nunca a mano ni desde la aplicación).

**MySQL**
```sql
DROP TRIGGER IF EXISTS biu_detalles_pedidos_audit_block_update;
DELIMITER $$
CREATE TRIGGER biu_detalles_pedidos_audit_block_update
BEFORE UPDATE ON detalles_pedidos_audit
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'detalles_pedidos_audit es inmutable: UPDATE prohibido.';
END$$
DELIMITER ;

DROP TRIGGER IF EXISTS bid_detalles_pedidos_audit_block_delete;
DELIMITER $$
CREATE TRIGGER bid_detalles_pedidos_audit_block_delete
BEFORE DELETE ON detalles_pedidos_audit
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'detalles_pedidos_audit es inmutable: DELETE prohibido.';
END$$
DELIMITER ;

DROP TRIGGER IF EXISTS bii_detalles_pedidos_audit_guard_insert;
DELIMITER $$
CREATE TRIGGER bii_detalles_pedidos_audit_guard_insert
BEFORE INSERT ON detalles_pedidos_audit
FOR EACH ROW
BEGIN
  IF COALESCE(@from_detalles_pedidos_trigger, 0) <> 1 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'INSERT en detalles_pedidos_audit solo permitido desde triggers de detalles_pedidos.';
  END IF;
END$$
DELIMITER ;
```
*Evidencia:* ![paso-37.png](Registro%20visual/triggers/paso-37.png)

**PostgreSQL**
```sql
CREATE OR REPLACE FUNCTION fn_biu_detalles_pedidos_audit_block_update() RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'detalles_pedidos_audit es inmutable: UPDATE prohibido.';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER biu_detalles_pedidos_audit_block_update
BEFORE UPDATE ON detalles_pedidos_audit
FOR EACH ROW
EXECUTE FUNCTION fn_biu_detalles_pedidos_audit_block_update();

CREATE OR REPLACE FUNCTION fn_bid_detalles_pedidos_audit_block_delete() RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'detalles_pedidos_audit es inmutable: DELETE prohibido.';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER bid_detalles_pedidos_audit_block_delete
BEFORE DELETE ON detalles_pedidos_audit
FOR EACH ROW
EXECUTE FUNCTION fn_bid_detalles_pedidos_audit_block_delete();

CREATE OR REPLACE FUNCTION fn_bii_detalles_pedidos_audit_guard_insert() RETURNS TRIGGER AS $$
BEGIN
  IF current_setting('myapp.from_detalles_pedidos_trigger', true) IS DISTINCT FROM '1' THEN
    RAISE EXCEPTION 'INSERT en detalles_pedidos_audit solo permitido desde triggers de detalles_pedidos.';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER bii_detalles_pedidos_audit_guard_insert
BEFORE INSERT ON detalles_pedidos_audit
FOR EACH ROW
EXECUTE FUNCTION fn_bii_detalles_pedidos_audit_guard_insert();
```
*Evidencia:* ![paso-38.png](Registro%20visual/triggers/paso-38.png)

**SQL Server**
```sql
-- SQL Server no soporta triggers BEFORE: se usan INSTEAD OF para bloquear/filtrar
CREATE TRIGGER biu_detalles_pedidos_audit_block_update
ON detalles_pedidos_audit
INSTEAD OF UPDATE
AS
BEGIN
  RAISERROR('detalles_pedidos_audit es inmutable: UPDATE prohibido.', 16, 1);
END;
GO

CREATE TRIGGER bid_detalles_pedidos_audit_block_delete
ON detalles_pedidos_audit
INSTEAD OF DELETE
AS
BEGIN
  RAISERROR('detalles_pedidos_audit es inmutable: DELETE prohibido.', 16, 1);
END;
GO

CREATE TRIGGER bii_detalles_pedidos_audit_guard_insert
ON detalles_pedidos_audit
INSTEAD OF INSERT
AS
BEGIN
  SET NOCOUNT ON;
  IF ISNULL(CAST(SESSION_CONTEXT(N'from_detalles_pedidos_trigger') AS INT), 0) <> 1
  BEGIN
    RAISERROR('INSERT en detalles_pedidos_audit solo permitido desde triggers de detalles_pedidos.', 16, 1);
    RETURN;
  END;

  INSERT INTO detalles_pedidos_audit (detalle_id, action_type, changed_at, changed_by, before_data, after_data)
  SELECT detalle_id, action_type, ISNULL(changed_at, GETDATE()), ISNULL(changed_by, 'Admin'), before_data, after_data
  FROM inserted;
END;
GO

```
*Evidencia:* ![paso-39.png](Registro%20visual/triggers/paso-39.png)

**Oracle**
```sql
CREATE OR REPLACE TRIGGER biu_detalles_pedidos_audit_block_update
BEFORE UPDATE ON detalles_pedidos_audit
FOR EACH ROW
BEGIN
  RAISE_APPLICATION_ERROR(-20010, 'detalles_pedidos_audit es inmutable: UPDATE prohibido.');
END;
/

CREATE OR REPLACE TRIGGER bid_detalles_pedidos_audit_block_delete
BEFORE DELETE ON detalles_pedidos_audit
FOR EACH ROW
BEGIN
  RAISE_APPLICATION_ERROR(-20011, 'detalles_pedidos_audit es inmutable: DELETE prohibido.');
END;
/

CREATE OR REPLACE TRIGGER bii_detalles_pedidos_audit_guard_insert
BEFORE INSERT ON detalles_pedidos_audit
FOR EACH ROW
BEGIN
  IF NOT pkg_audit_ctrl_detalles_pedidos.from_trigger THEN
    RAISE_APPLICATION_ERROR(-20012, 'INSERT en detalles_pedidos_audit solo permitido desde triggers de detalles_pedidos.');
  END IF;
END;
/
```
*Evidencia:* ![paso-40.png](Registro%20visual/triggers/paso-40.png)

## Auditoría de `productos` — tabla `productos_audit`

**Contexto de negocio:** Los cambios de precio, nombre o estado (activo/inactivo) de un producto del menú afectan directamente lo que se cobra; se necesita un rastro inmutable de quién cambió qué y cuándo, útil también para resolver disputas con clientes o proveedores.

**Tabla de auditoría:**

### MySQL
```sql
CREATE TABLE IF NOT EXISTS productos_audit (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  producto_id BIGINT NOT NULL,
  action_type ENUM('INSERT','UPDATE','DELETE') NOT NULL DEFAULT 'INSERT',
  changed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  changed_by VARCHAR(255) NOT NULL DEFAULT 'Admin',
  before_data JSON NULL,
  after_data JSON NULL
) ENGINE=InnoDB;
```
*Evidencia:* ![paso-41.png](Registro%20visual/triggers/paso-41.png)

### PostgreSQL
```sql
CREATE TABLE IF NOT EXISTS productos_audit (
  id BIGSERIAL PRIMARY KEY,
  producto_id BIGINT NOT NULL,
  action_type VARCHAR(10) NOT NULL DEFAULT 'INSERT' CHECK (action_type IN ('INSERT','UPDATE','DELETE')),
  changed_at TIMESTAMP NOT NULL DEFAULT NOW(),
  changed_by VARCHAR(255) NOT NULL DEFAULT 'Admin',
  before_data JSONB,
  after_data JSONB
);
```
*Evidencia:* ![paso-42.png](Registro%20visual/triggers/paso-42.png)

### SQL Server
```sql
CREATE TABLE productos_audit (
  id BIGINT IDENTITY PRIMARY KEY,
  producto_id BIGINT NOT NULL,
  action_type VARCHAR(10) NOT NULL DEFAULT 'INSERT' CHECK (action_type IN ('INSERT','UPDATE','DELETE')),
  changed_at DATETIME NOT NULL DEFAULT GETDATE(),
  changed_by VARCHAR(255) NOT NULL DEFAULT 'Admin',
  before_data NVARCHAR(MAX) NULL,
  after_data NVARCHAR(MAX) NULL
);
```
*Evidencia:* ![paso-43.png](Registro%20visual/triggers/paso-43.png)

### Oracle
```sql
CREATE TABLE productos_audit (
  id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  producto_id NUMBER NOT NULL,
  action_type VARCHAR2(10) DEFAULT 'INSERT' NOT NULL CHECK (action_type IN ('INSERT','UPDATE','DELETE')),
  changed_at DATE DEFAULT SYSDATE NOT NULL,
  changed_by VARCHAR2(255) DEFAULT 'Admin' NOT NULL,
  before_data CLOB,
  after_data CLOB
);

-- Bandera de sesión usada por los triggers de auditoría e inmutabilidad
CREATE OR REPLACE PACKAGE pkg_audit_ctrl_productos AS
  from_trigger BOOLEAN := FALSE;
END pkg_audit_ctrl_productos;
/
```
*Evidencia:* ![paso-44.png](Registro%20visual/triggers/paso-44.png)

### Trigger AFTER INSERT sobre `productos`

**MySQL**
```sql
DROP TRIGGER IF EXISTS ai_productos_audit;
DELIMITER $$
CREATE TRIGGER ai_productos_audit
AFTER INSERT ON productos
FOR EACH ROW
BEGIN
  SET @from_productos_trigger = 1;
  INSERT INTO productos_audit (producto_id, action_type, before_data, after_data)
  VALUES (NEW.id, 'INSERT', NULL, JSON_OBJECT(
      'id', NEW.id,
      'sku', NEW.sku,
      'nombre', NEW.nombre,
      'descripcion', NEW.descripcion,
      'precio', NEW.precio,
      'is_active', NEW.is_active,
      'created_at', NEW.created_at,
      'updated_at', NEW.updated_at
    ));
  SET @from_productos_trigger = NULL;
END$$
DELIMITER ;
```
*Evidencia:* ![paso-45.png](Registro%20visual/triggers/paso-45.png)

**PostgreSQL**
```sql
CREATE OR REPLACE FUNCTION fn_ai_productos_audit() RETURNS TRIGGER AS $$
BEGIN
  PERFORM set_config('myapp.from_productos_trigger', '1', true);
  INSERT INTO productos_audit (producto_id, action_type, before_data, after_data)
  VALUES (NEW.id, 'INSERT', NULL, jsonb_build_object(
      'id', NEW.id,
      'sku', NEW.sku,
      'nombre', NEW.nombre,
      'descripcion', NEW.descripcion,
      'precio', NEW.precio,
      'is_active', NEW.is_active,
      'created_at', NEW.created_at,
      'updated_at', NEW.updated_at
    ));
  PERFORM set_config('myapp.from_productos_trigger', NULL, true);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER ai_productos_audit
AFTER INSERT ON productos
FOR EACH ROW
EXECUTE FUNCTION fn_ai_productos_audit();
```
*Evidencia:* ![paso-46.png](Registro%20visual/triggers/paso-46.png)

**SQL Server**
```sql
CREATE TRIGGER ai_productos_audit
ON productos
AFTER INSERT
AS
BEGIN
  SET NOCOUNT ON;
  EXEC sp_set_session_context @key = N'from_productos_trigger', @value = 1;

  INSERT INTO productos_audit (producto_id, action_type, before_data, after_data)
  SELECT i.id, 'INSERT', NULL, (SELECT i.id AS id, i.sku AS sku, i.nombre AS nombre, i.descripcion AS descripcion, i.precio AS precio, i.is_active AS is_active, i.created_at AS created_at, i.updated_at AS updated_at FOR JSON PATH, WITHOUT_ARRAY_WRAPPER)
  FROM inserted i;

  EXEC sp_set_session_context @key = N'from_productos_trigger', @value = NULL;
END;
```
*Evidencia:* ![paso-47.png](Registro%20visual/triggers/paso-47.png)

**Oracle**
```sql
CREATE OR REPLACE TRIGGER ai_productos_audit
AFTER INSERT ON productos
FOR EACH ROW
BEGIN
  pkg_audit_ctrl_productos.from_trigger := TRUE;
  INSERT INTO productos_audit (producto_id, action_type, before_data, after_data)
  VALUES (:NEW.id, 'INSERT', NULL, JSON_OBJECT(
      'id' VALUE :NEW.id,
      'sku' VALUE :NEW.sku,
      'nombre' VALUE :NEW.nombre,
      'descripcion' VALUE :NEW.descripcion,
      'precio' VALUE :NEW.precio,
      'is_active' VALUE :NEW.is_active,
      'created_at' VALUE :NEW.created_at,
      'updated_at' VALUE :NEW.updated_at
    ));
  pkg_audit_ctrl_productos.from_trigger := FALSE;
END;
/
```
*Evidencia:* ![paso-48.png](Registro%20visual/triggers/paso-48.png)

### Trigger AFTER UPDATE sobre `productos`

**MySQL**
```sql
DROP TRIGGER IF EXISTS au_productos_audit;
DELIMITER $$
CREATE TRIGGER au_productos_audit
AFTER UPDATE ON productos
FOR EACH ROW
BEGIN
  SET @from_productos_trigger = 1;
  INSERT INTO productos_audit (producto_id, action_type, before_data, after_data)
  VALUES (NEW.id, 'UPDATE', JSON_OBJECT(
      'id', OLD.id,
      'sku', OLD.sku,
      'nombre', OLD.nombre,
      'descripcion', OLD.descripcion,
      'precio', OLD.precio,
      'is_active', OLD.is_active,
      'created_at', OLD.created_at,
      'updated_at', OLD.updated_at
    ), JSON_OBJECT(
      'id', NEW.id,
      'sku', NEW.sku,
      'nombre', NEW.nombre,
      'descripcion', NEW.descripcion,
      'precio', NEW.precio,
      'is_active', NEW.is_active,
      'created_at', NEW.created_at,
      'updated_at', NEW.updated_at
    ));
  SET @from_productos_trigger = NULL;
END$$
DELIMITER ;
```
*Evidencia:* ![paso-49.png](Registro%20visual/triggers/paso-49.png)

**PostgreSQL**
```sql
CREATE OR REPLACE FUNCTION fn_au_productos_audit() RETURNS TRIGGER AS $$
BEGIN
  PERFORM set_config('myapp.from_productos_trigger', '1', true);
  INSERT INTO productos_audit (producto_id, action_type, before_data, after_data)
  VALUES (NEW.id, 'UPDATE', jsonb_build_object(
      'id', OLD.id,
      'sku', OLD.sku,
      'nombre', OLD.nombre,
      'descripcion', OLD.descripcion,
      'precio', OLD.precio,
      'is_active', OLD.is_active,
      'created_at', OLD.created_at,
      'updated_at', OLD.updated_at
    ), jsonb_build_object(
      'id', NEW.id,
      'sku', NEW.sku,
      'nombre', NEW.nombre,
      'descripcion', NEW.descripcion,
      'precio', NEW.precio,
      'is_active', NEW.is_active,
      'created_at', NEW.created_at,
      'updated_at', NEW.updated_at
    ));
  PERFORM set_config('myapp.from_productos_trigger', NULL, true);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER au_productos_audit
AFTER UPDATE ON productos
FOR EACH ROW
EXECUTE FUNCTION fn_au_productos_audit();
```
*Evidencia:* ![paso-50.png](Registro%20visual/triggers/paso-50.png)

**SQL Server**
```sql
CREATE TRIGGER au_productos_audit
ON productos
AFTER UPDATE
AS
BEGIN
  SET NOCOUNT ON;
  EXEC sp_set_session_context @key = N'from_productos_trigger', @value = 1;

  INSERT INTO productos_audit (producto_id, action_type, before_data, after_data)
  SELECT i.id, 'UPDATE', (SELECT d.id AS id, d.sku AS sku, d.nombre AS nombre, d.descripcion AS descripcion, d.precio AS precio, d.is_active AS is_active, d.created_at AS created_at, d.updated_at AS updated_at FOR JSON PATH, WITHOUT_ARRAY_WRAPPER), (SELECT i.id AS id, i.sku AS sku, i.nombre AS nombre, i.descripcion AS descripcion, i.precio AS precio, i.is_active AS is_active, i.created_at AS created_at, i.updated_at AS updated_at FOR JSON PATH, WITHOUT_ARRAY_WRAPPER)
  FROM inserted i
  JOIN deleted d ON d.id = i.id;

  EXEC sp_set_session_context @key = N'from_productos_trigger', @value = NULL;
END;
```
*Evidencia:* ![paso-51.png](Registro%20visual/triggers/paso-51.png)

**Oracle**
```sql
CREATE OR REPLACE TRIGGER au_productos_audit
AFTER UPDATE ON productos
FOR EACH ROW
BEGIN
  pkg_audit_ctrl_productos.from_trigger := TRUE;
  INSERT INTO productos_audit (producto_id, action_type, before_data, after_data)
  VALUES (:NEW.id, 'UPDATE', JSON_OBJECT(
      'id' VALUE :OLD.id,
      'sku' VALUE :OLD.sku,
      'nombre' VALUE :OLD.nombre,
      'descripcion' VALUE :OLD.descripcion,
      'precio' VALUE :OLD.precio,
      'is_active' VALUE :OLD.is_active,
      'created_at' VALUE :OLD.created_at,
      'updated_at' VALUE :OLD.updated_at
    ), JSON_OBJECT(
      'id' VALUE :NEW.id,
      'sku' VALUE :NEW.sku,
      'nombre' VALUE :NEW.nombre,
      'descripcion' VALUE :NEW.descripcion,
      'precio' VALUE :NEW.precio,
      'is_active' VALUE :NEW.is_active,
      'created_at' VALUE :NEW.created_at,
      'updated_at' VALUE :NEW.updated_at
    ));
  pkg_audit_ctrl_productos.from_trigger := FALSE;
END;
/
```
*Evidencia:* ![paso-52.png](Registro%20visual/triggers/paso-52.png)

### Trigger AFTER DELETE sobre `productos`

**MySQL**
```sql
DROP TRIGGER IF EXISTS ad_productos_audit;
DELIMITER $$
CREATE TRIGGER ad_productos_audit
AFTER DELETE ON productos
FOR EACH ROW
BEGIN
  SET @from_productos_trigger = 1;
  INSERT INTO productos_audit (producto_id, action_type, before_data, after_data)
  VALUES (OLD.id, 'DELETE', JSON_OBJECT(
      'id', OLD.id,
      'sku', OLD.sku,
      'nombre', OLD.nombre,
      'descripcion', OLD.descripcion,
      'precio', OLD.precio,
      'is_active', OLD.is_active,
      'created_at', OLD.created_at,
      'updated_at', OLD.updated_at
    ), NULL);
  SET @from_productos_trigger = NULL;
END$$
DELIMITER ;
```
*Evidencia:* ![paso-53.png](Registro%20visual/triggers/paso-53.png)

**PostgreSQL**
```sql
CREATE OR REPLACE FUNCTION fn_ad_productos_audit() RETURNS TRIGGER AS $$
BEGIN
  PERFORM set_config('myapp.from_productos_trigger', '1', true);
  INSERT INTO productos_audit (producto_id, action_type, before_data, after_data)
  VALUES (OLD.id, 'DELETE', jsonb_build_object(
      'id', OLD.id,
      'sku', OLD.sku,
      'nombre', OLD.nombre,
      'descripcion', OLD.descripcion,
      'precio', OLD.precio,
      'is_active', OLD.is_active,
      'created_at', OLD.created_at,
      'updated_at', OLD.updated_at
    ), NULL);
  PERFORM set_config('myapp.from_productos_trigger', NULL, true);
  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER ad_productos_audit
AFTER DELETE ON productos
FOR EACH ROW
EXECUTE FUNCTION fn_ad_productos_audit();
```
*Evidencia:* ![paso-54.png](Registro%20visual/triggers/paso-54.png)

**SQL Server**
```sql
CREATE TRIGGER ad_productos_audit
ON productos
AFTER DELETE
AS
BEGIN
  SET NOCOUNT ON;
  EXEC sp_set_session_context @key = N'from_productos_trigger', @value = 1;

  INSERT INTO productos_audit (producto_id, action_type, before_data, after_data)
  SELECT d.id, 'DELETE', (SELECT d.id AS id, d.sku AS sku, d.nombre AS nombre, d.descripcion AS descripcion, d.precio AS precio, d.is_active AS is_active, d.created_at AS created_at, d.updated_at AS updated_at FOR JSON PATH, WITHOUT_ARRAY_WRAPPER), NULL
  FROM deleted d;

  EXEC sp_set_session_context @key = N'from_productos_trigger', @value = NULL;
END;
```
*Evidencia:* ![paso-55.png](Registro%20visual/triggers/paso-55.png)

**Oracle**
```sql
CREATE OR REPLACE TRIGGER ad_productos_audit
AFTER DELETE ON productos
FOR EACH ROW
BEGIN
  pkg_audit_ctrl_productos.from_trigger := TRUE;
  INSERT INTO productos_audit (producto_id, action_type, before_data, after_data)
  VALUES (:OLD.id, 'DELETE', JSON_OBJECT(
      'id' VALUE :OLD.id,
      'sku' VALUE :OLD.sku,
      'nombre' VALUE :OLD.nombre,
      'descripcion' VALUE :OLD.descripcion,
      'precio' VALUE :OLD.precio,
      'is_active' VALUE :OLD.is_active,
      'created_at' VALUE :OLD.created_at,
      'updated_at' VALUE :OLD.updated_at
    ), NULL);
  pkg_audit_ctrl_productos.from_trigger := FALSE;
END;
/
```
*Evidencia:* ![paso-56.png](Registro%20visual/triggers/paso-56.png)

### Triggers de guardia sobre `productos_audit` (inmutabilidad)

Estos 3 triggers hacen que `productos_audit` sea de solo-inserción: nadie puede modificar o borrar un registro de auditoría, y solo puede insertarse desde los triggers de `productos` (nunca a mano ni desde la aplicación).

**MySQL**
```sql
DROP TRIGGER IF EXISTS biu_productos_audit_block_update;
DELIMITER $$
CREATE TRIGGER biu_productos_audit_block_update
BEFORE UPDATE ON productos_audit
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'productos_audit es inmutable: UPDATE prohibido.';
END$$
DELIMITER ;

DROP TRIGGER IF EXISTS bid_productos_audit_block_delete;
DELIMITER $$
CREATE TRIGGER bid_productos_audit_block_delete
BEFORE DELETE ON productos_audit
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'productos_audit es inmutable: DELETE prohibido.';
END$$
DELIMITER ;

DROP TRIGGER IF EXISTS bii_productos_audit_guard_insert;
DELIMITER $$
CREATE TRIGGER bii_productos_audit_guard_insert
BEFORE INSERT ON productos_audit
FOR EACH ROW
BEGIN
  IF COALESCE(@from_productos_trigger, 0) <> 1 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'INSERT en productos_audit solo permitido desde triggers de productos.';
  END IF;
END$$
DELIMITER ;
```
*Evidencia:* ![paso-57.png](Registro%20visual/triggers/paso-57.png)

**PostgreSQL**
```sql
CREATE OR REPLACE FUNCTION fn_biu_productos_audit_block_update() RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'productos_audit es inmutable: UPDATE prohibido.';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER biu_productos_audit_block_update
BEFORE UPDATE ON productos_audit
FOR EACH ROW
EXECUTE FUNCTION fn_biu_productos_audit_block_update();

CREATE OR REPLACE FUNCTION fn_bid_productos_audit_block_delete() RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'productos_audit es inmutable: DELETE prohibido.';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER bid_productos_audit_block_delete
BEFORE DELETE ON productos_audit
FOR EACH ROW
EXECUTE FUNCTION fn_bid_productos_audit_block_delete();

CREATE OR REPLACE FUNCTION fn_bii_productos_audit_guard_insert() RETURNS TRIGGER AS $$
BEGIN
  IF current_setting('myapp.from_productos_trigger', true) IS DISTINCT FROM '1' THEN
    RAISE EXCEPTION 'INSERT en productos_audit solo permitido desde triggers de productos.';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER bii_productos_audit_guard_insert
BEFORE INSERT ON productos_audit
FOR EACH ROW
EXECUTE FUNCTION fn_bii_productos_audit_guard_insert();
```
*Evidencia:* ![paso-58.png](Registro%20visual/triggers/paso-58.png)

**SQL Server**
```sql
-- SQL Server no soporta triggers BEFORE: se usan INSTEAD OF para bloquear/filtrar
CREATE TRIGGER biu_productos_audit_block_update
ON productos_audit
INSTEAD OF UPDATE
AS
BEGIN
  RAISERROR('productos_audit es inmutable: UPDATE prohibido.', 16, 1);
END;
GO

CREATE TRIGGER bid_productos_audit_block_delete
ON productos_audit
INSTEAD OF DELETE
AS
BEGIN
  RAISERROR('productos_audit es inmutable: DELETE prohibido.', 16, 1);
END;
GO

CREATE TRIGGER bii_productos_audit_guard_insert
ON productos_audit
INSTEAD OF INSERT
AS
BEGIN
  SET NOCOUNT ON;
  IF ISNULL(CAST(SESSION_CONTEXT(N'from_productos_trigger') AS INT), 0) <> 1
  BEGIN
    RAISERROR('INSERT en productos_audit solo permitido desde triggers de productos.', 16, 1);
    RETURN;
  END;

  INSERT INTO productos_audit (producto_id, action_type, changed_at, changed_by, before_data, after_data)
  SELECT producto_id, action_type, ISNULL(changed_at, GETDATE()), ISNULL(changed_by, 'Admin'), before_data, after_data
  FROM inserted;
END;
GO

```
*Evidencia:* ![paso-59.png](Registro%20visual/triggers/paso-59.png)

**Oracle**
```sql
CREATE OR REPLACE TRIGGER biu_productos_audit_block_update
BEFORE UPDATE ON productos_audit
FOR EACH ROW
BEGIN
  RAISE_APPLICATION_ERROR(-20010, 'productos_audit es inmutable: UPDATE prohibido.');
END;
/

CREATE OR REPLACE TRIGGER bid_productos_audit_block_delete
BEFORE DELETE ON productos_audit
FOR EACH ROW
BEGIN
  RAISE_APPLICATION_ERROR(-20011, 'productos_audit es inmutable: DELETE prohibido.');
END;
/

CREATE OR REPLACE TRIGGER bii_productos_audit_guard_insert
BEFORE INSERT ON productos_audit
FOR EACH ROW
BEGIN
  IF NOT pkg_audit_ctrl_productos.from_trigger THEN
    RAISE_APPLICATION_ERROR(-20012, 'INSERT en productos_audit solo permitido desde triggers de productos.');
  END IF;
END;
/
```
*Evidencia:* ![paso-60.png](Registro%20visual/triggers/paso-60.png)

# 7. Procedimientos almacenados y consultas avanzadas

Cada consulta de las secciones 2 a 5 se convierte en un **procedimiento almacenado con parámetros** en los cuatro motores, y se agregan tres consultas avanzadas nuevas (funciones de ventana y CTE) que nacen ya como procedimiento. Para cada uno se presenta: la consulta de origen, su narrativa de negocio, los parámetros, el código por motor y la evidencia de la creación (`funcion_N.png`) y de la llamada (`llamada-N.png`). Los scripts completos están en la carpeta `procedimientos/`.

**Convención.** Nombres `sp_<verbo>_<tema>`; parámetros con prefijo `p_`. Diferencias entre motores:

| Motor | Escritura | Lectura (devuelve filas) | Cómo se llama |
|---|---|---|---|
| MySQL | `PROCEDURE` | `PROCEDURE` con `SELECT` | `CALL sp_x(...)` |
| PostgreSQL | `PROCEDURE` | `FUNCTION ... RETURNS TABLE` (un `PROCEDURE` no devuelve filas) | `CALL` / `SELECT * FROM sp_x(...)` |
| SQL Server | `PROCEDURE` | `PROCEDURE` con `SELECT` | `EXEC sp_x ...` |
| Oracle | `PROCEDURE` (con `COMMIT`) | `PROCEDURE` con `OUT SYS_REFCURSOR` | `EXEC sp_x(..., :rc); PRINT rc` |

## SP-01. Crear cliente

**Origen:** Consulta 1 (Create, INSERT de cliente)

**Narrativa:** El restaurante registra un comensal nuevo que se vincula al programa de fidelización desde la app. En lugar de repetir el INSERT con valores escritos a mano, el alta se encapsula en un procedimiento que recibe los datos del cliente y los inserta, de modo que la app o el personal siempre usen la misma regla.

**Parámetros:** `p_tipo_documento`, `p_numero_documento`, `p_nombre`, `p_telefono`, `p_email`

### MySQL 8.0

```sql
DELIMITER $$
DROP PROCEDURE IF EXISTS sp_crear_cliente$$
CREATE PROCEDURE sp_crear_cliente(
    IN p_tipo_documento   VARCHAR(20),
    IN p_numero_documento VARCHAR(30),
    IN p_nombre           VARCHAR(150),
    IN p_telefono         VARCHAR(20),
    IN p_email            VARCHAR(150))
BEGIN
    INSERT INTO clientes(tipo_documento, numero_documento, nombre, telefono, email)
    VALUES (p_tipo_documento, p_numero_documento, p_nombre, p_telefono, p_email);
END$$
DELIMITER ;
```

*Evidencia (creación):* ![funcion_1.png](Registro%20visual/mysql/funcion_1.png)

*Llamada:*

```sql
CALL sp_crear_cliente('CC','1043680257','Maria Perez Gomez','3001112233','maria.perez@example.com');
```

*Evidencia (llamada):* ![llamada-1.png](Registro%20visual/mysql/llamada-1.png)

### PostgreSQL 17

```sql
CREATE OR REPLACE PROCEDURE sp_crear_cliente(
    p_tipo_documento   VARCHAR,
    p_numero_documento VARCHAR,
    p_nombre           VARCHAR,
    p_telefono         VARCHAR,
    p_email            VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO clientes(tipo_documento, numero_documento, nombre, telefono, email)
    VALUES (p_tipo_documento, p_numero_documento, p_nombre, p_telefono, p_email);
END;
$$;
```

*Evidencia (creación):* ![funcion_1.png](Registro%20visual/postgresql/funcion_1.png)

*Llamada:*

```sql
CALL sp_crear_cliente('CC','1043680257','Maria Perez Gomez','3001112233','maria.perez@example.com');
```

*Evidencia (llamada):* ![llamada-1.png](Registro%20visual/postgresql/llamada-1.png)

### SQL Server 2022

```sql
CREATE OR ALTER PROCEDURE sp_crear_cliente
    @p_tipo_documento   VARCHAR(20),
    @p_numero_documento VARCHAR(30),
    @p_nombre           VARCHAR(150),
    @p_telefono         VARCHAR(20),
    @p_email            VARCHAR(150)
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO clientes(tipo_documento, numero_documento, nombre, telefono, email)
    VALUES (@p_tipo_documento, @p_numero_documento, @p_nombre, @p_telefono, @p_email);
END;
GO
```

*Evidencia (creación):* ![funcion_1.png](Registro%20visual/sqlserver/funcion_1.png)

*Llamada:*

```sql
EXEC sp_crear_cliente 'CC','1043680257','Maria Perez Gomez','3001112233','maria.perez@example.com';
```

*Evidencia (llamada):* ![llamada-1.png](Registro%20visual/sqlserver/llamada-1.png)

### Oracle XE 21

```sql
CREATE OR REPLACE PROCEDURE sp_crear_cliente(
    p_tipo_documento   IN VARCHAR2,
    p_numero_documento IN VARCHAR2,
    p_nombre           IN VARCHAR2,
    p_telefono         IN VARCHAR2,
    p_email            IN VARCHAR2)
AS
BEGIN
    INSERT INTO clientes(tipo_documento, numero_documento, nombre, telefono, email)
    VALUES (p_tipo_documento, p_numero_documento, p_nombre, p_telefono, p_email);
    COMMIT;
END sp_crear_cliente;
/
```

*Evidencia (creación):* ![funcion_1.png](Registro%20visual/oracle/funcion_1.png)

*Llamada:*

```sql
EXEC sp_crear_cliente('CC','1043680257','Maria Perez Gomez','3001112233','maria.perez@example.com');
```

*Evidencia (llamada):* ![llamada-2.png](Registro%20visual/oracle/llamada-2.png)

## SP-02. Buscar clientes por correo

**Origen:** Consultas 5.1 y 5.2 (LIKE)

**Narrativa:** Soporte técnico necesita ubicar clientes por una parte del correo (por ejemplo, para una migración de dominio). Las dos consultas LIKE fijas ('m%' y '%example%') se generalizan con un patrón recibido por parámetro y se busca en cualquier posición del correo.

**Parámetros:** `p_patron`: texto a buscar dentro del correo

### MySQL 8.0

```sql
DELIMITER $$
DROP PROCEDURE IF EXISTS sp_buscar_clientes_por_email$$
CREATE PROCEDURE sp_buscar_clientes_por_email(IN p_patron VARCHAR(100))
BEGIN
    SELECT c.id, c.nombre, c.telefono, c.email
    FROM clientes AS c
    WHERE c.email LIKE CONCAT('%', p_patron, '%')
    ORDER BY c.nombre;
END$$
DELIMITER ;
```

*Evidencia (creación):* ![funcion_2.png](Registro%20visual/mysql/funcion_2.png)

*Llamada:*

```sql
CALL sp_buscar_clientes_por_email('example');
```

*Evidencia (llamada):* ![llamada-2.png](Registro%20visual/mysql/llamada-2.png)

### PostgreSQL 17

```sql
CREATE OR REPLACE FUNCTION sp_buscar_clientes_por_email(p_patron VARCHAR)
RETURNS TABLE(id INT, nombre VARCHAR, telefono VARCHAR, email VARCHAR)
LANGUAGE sql AS $$
    SELECT c.id, c.nombre, c.telefono, c.email
    FROM clientes AS c
    WHERE c.email LIKE '%' || p_patron || '%'
    ORDER BY c.nombre;
$$;
```

*Evidencia (creación):* ![funcion_2.png](Registro%20visual/postgresql/funcion_2.png)

*Llamada:*

```sql
SELECT * FROM sp_buscar_clientes_por_email('example');
```

*Evidencia (llamada):* ![llamada-2.png](Registro%20visual/postgresql/llamada-2.png)

### SQL Server 2022

```sql
CREATE OR ALTER PROCEDURE sp_buscar_clientes_por_email
    @p_patron VARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT c.id, c.nombre, c.telefono, c.email
    FROM clientes AS c
    WHERE c.email LIKE CONCAT('%', @p_patron, '%')
    ORDER BY c.nombre;
END;
GO
```

*Evidencia (creación):* ![funcion_2.png](Registro%20visual/sqlserver/funcion_2.png)

*Llamada:*

```sql
EXEC sp_buscar_clientes_por_email 'example';
```

*Evidencia (llamada):* ![llamada-2.png](Registro%20visual/sqlserver/llamada-2.png)

### Oracle XE 21

```sql
CREATE OR REPLACE PROCEDURE sp_buscar_clientes_por_email(
    p_patron IN VARCHAR2,
    p_cursor OUT SYS_REFCURSOR)
AS
BEGIN
    OPEN p_cursor FOR
    SELECT c.id, c.nombre, c.telefono, c.email
      FROM clientes c
     WHERE c.email LIKE '%' || p_patron || '%'
     ORDER BY c.nombre;
END sp_buscar_clientes_por_email;
/
```

*Evidencia (creación):* ![funcion_2.png](Registro%20visual/oracle/funcion_2.png)

*Llamada:*

```sql
EXEC sp_buscar_clientes_por_email('example', :rc);
PRINT rc
```

*Evidencia (llamada):* ![llamada-3.png](Registro%20visual/oracle/llamada-3.png)

## SP-03. Pedidos por fecha

**Origen:** Consultas 3.3 y 4.2 (JOIN clientes-pedidos y filtro por fecha)

**Narrativa:** Atención al cliente debe ubicar los pedidos de un día para resolver un reclamo. El filtro por una fecha fija se convierte en un parámetro de tipo fecha y se compara solo el día (sin la hora).

**Parámetros:** `p_fecha`: día a consultar

### MySQL 8.0

```sql
DELIMITER $$
DROP PROCEDURE IF EXISTS sp_pedidos_por_fecha$$
CREATE PROCEDURE sp_pedidos_por_fecha(IN p_fecha DATE)
BEGIN
    SELECT c.nombre AS cliente, c.email, p.id AS pedido_id, p.canal,
           p.fecha, p.total, p.estado
    FROM clientes AS c
    JOIN pedidos AS p ON c.id = p.cliente_id
    WHERE DATE(p.fecha) = p_fecha
    ORDER BY p.fecha;
END$$
DELIMITER ;
```

*Evidencia (creación):* ![funcion_3.png](Registro%20visual/mysql/funcion_3.png)

*Llamada:*

```sql
CALL sp_pedidos_por_fecha('2026-05-18');
```

*Evidencia (llamada):* ![llamada-3.png](Registro%20visual/mysql/llamada-3.png)

### PostgreSQL 17

```sql
CREATE OR REPLACE FUNCTION sp_pedidos_por_fecha(p_fecha DATE)
RETURNS TABLE(cliente VARCHAR, email VARCHAR, pedido_id INT, canal VARCHAR,
              fecha TIMESTAMP, total NUMERIC, estado VARCHAR)
LANGUAGE sql AS $$
    SELECT c.nombre, c.email, p.id, p.canal, p.fecha, p.total, p.estado
    FROM clientes AS c
    JOIN pedidos AS p ON c.id = p.cliente_id
    WHERE p.fecha::date = p_fecha
    ORDER BY p.fecha;
$$;
```

*Evidencia (creación):* ![funcion_3.png](Registro%20visual/postgresql/funcion_3.png)

*Llamada:*

```sql
SELECT * FROM sp_pedidos_por_fecha('2026-05-18');
```

*Evidencia (llamada):* ![llamada-3.png](Registro%20visual/postgresql/llamada-3.png)

### SQL Server 2022

```sql
CREATE OR ALTER PROCEDURE sp_pedidos_por_fecha
    @p_fecha DATE
AS
BEGIN
    SET NOCOUNT ON;
    SELECT c.nombre AS cliente, c.email, p.id AS pedido_id, p.canal,
           p.fecha, p.total, p.estado
    FROM clientes AS c
    JOIN pedidos AS p ON c.id = p.cliente_id
    WHERE CAST(p.fecha AS DATE) = @p_fecha
    ORDER BY p.fecha;
END;
GO
```

*Evidencia (creación):* ![funcion_3.png](Registro%20visual/sqlserver/funcion_3.png)

*Llamada:*

```sql
EXEC sp_pedidos_por_fecha '2026-05-18';
```

*Evidencia (llamada):* ![llamada-3.png](Registro%20visual/sqlserver/llamada-3.png)

### Oracle XE 21

```sql
CREATE OR REPLACE PROCEDURE sp_pedidos_por_fecha(
    p_fecha IN DATE,
    p_cursor OUT SYS_REFCURSOR)
AS
BEGIN
    OPEN p_cursor FOR
    SELECT c.nombre AS cliente, c.email, p.id AS pedido_id, p.canal,
           p.fecha, p.total, p.estado
      FROM clientes c
      JOIN pedidos p ON c.id = p.cliente_id
     WHERE TRUNC(p.fecha) = p_fecha
     ORDER BY p.fecha;
END sp_pedidos_por_fecha;
/
```

*Evidencia (creación):* ![funcion_3.png](Registro%20visual/oracle/funcion_3.png)

*Llamada:*

```sql
EXEC sp_pedidos_por_fecha(DATE '2026-05-18', :rc);
PRINT rc
```

*Evidencia (llamada):* ![llamada-4.png](Registro%20visual/oracle/llamada-4.png)

## SP-04. Detalle de ventas por rango

**Origen:** Consulta 5.3 (cuatro JOIN, rango de fechas y ORDER BY)

**Narrativa:** Gerencia necesita el detalle de ventas por producto en un periodo, por ejemplo para medir una promoción. Se unen clientes, pedidos, detalles y productos y se devuelven solo las columnas útiles, con el rango de fechas como parámetros.

**Parámetros:** `p_desde`, `p_hasta`: fechas inicial y final (inclusivas)

### MySQL 8.0

```sql
DELIMITER $$
DROP PROCEDURE IF EXISTS sp_detalle_ventas_rango$$
CREATE PROCEDURE sp_detalle_ventas_rango(IN p_desde DATE, IN p_hasta DATE)
BEGIN
    SELECT p.fecha, p.id AS pedido_id, c.nombre AS cliente, pr.nombre AS producto,
           dp.cantidad, dp.valor_unitario, dp.total AS total_linea
    FROM clientes AS c
    JOIN pedidos AS p ON c.id = p.cliente_id
    JOIN detalles_pedidos AS dp ON p.id = dp.pedido_id
    JOIN productos AS pr ON pr.id = dp.producto_id
    WHERE DATE(p.fecha) BETWEEN p_desde AND p_hasta
    ORDER BY p.fecha ASC;
END$$
DELIMITER ;
```

*Evidencia (creación):* ![funcion_4.png](Registro%20visual/mysql/funcion_4.png)

*Llamada:*

```sql
CALL sp_detalle_ventas_rango('2026-07-04','2026-07-13');
```

*Evidencia (llamada):* ![llamada-4.png](Registro%20visual/mysql/llamada-4.png)

### PostgreSQL 17

```sql
CREATE OR REPLACE FUNCTION sp_detalle_ventas_rango(p_desde DATE, p_hasta DATE)
RETURNS TABLE(fecha TIMESTAMP, pedido_id INT, cliente VARCHAR, producto VARCHAR,
              cantidad NUMERIC, valor_unitario NUMERIC, total_linea NUMERIC)
LANGUAGE sql AS $$
    SELECT p.fecha, p.id, c.nombre, pr.nombre, dp.cantidad, dp.valor_unitario, dp.total
    FROM clientes AS c
    JOIN pedidos AS p ON c.id = p.cliente_id
    JOIN detalles_pedidos AS dp ON p.id = dp.pedido_id
    JOIN productos AS pr ON pr.id = dp.producto_id
    WHERE p.fecha::date BETWEEN p_desde AND p_hasta
    ORDER BY p.fecha ASC;
$$;
```

*Evidencia (creación):* ![funcion_4.png](Registro%20visual/postgresql/funcion_4.png)

*Llamada:*

```sql
SELECT * FROM sp_detalle_ventas_rango('2026-07-04','2026-07-13');
```

*Evidencia (llamada):* ![llamada-4.png](Registro%20visual/postgresql/llamada-4.png)

### SQL Server 2022

```sql
CREATE OR ALTER PROCEDURE sp_detalle_ventas_rango
    @p_desde DATE,
    @p_hasta DATE
AS
BEGIN
    SET NOCOUNT ON;
    SELECT p.fecha, p.id AS pedido_id, c.nombre AS cliente, pr.nombre AS producto,
           dp.cantidad, dp.valor_unitario, dp.total AS total_linea
    FROM clientes AS c
    JOIN pedidos AS p ON c.id = p.cliente_id
    JOIN detalles_pedidos AS dp ON p.id = dp.pedido_id
    JOIN productos AS pr ON pr.id = dp.producto_id
    WHERE CAST(p.fecha AS DATE) BETWEEN @p_desde AND @p_hasta
    ORDER BY p.fecha ASC;
END;
GO
```

*Evidencia (creación):* ![funcion_4.png](Registro%20visual/sqlserver/funcion_4.png)

*Llamada:*

```sql
EXEC sp_detalle_ventas_rango '2026-07-04','2026-07-13';
```

*Evidencia (llamada):* ![llamada-4.png](Registro%20visual/sqlserver/llamada-4.png)

### Oracle XE 21

```sql
CREATE OR REPLACE PROCEDURE sp_detalle_ventas_rango(
    p_desde IN DATE, p_hasta IN DATE,
    p_cursor OUT SYS_REFCURSOR)
AS
BEGIN
    OPEN p_cursor FOR
    SELECT p.fecha, p.id AS pedido_id, c.nombre AS cliente, pr.nombre AS producto,
           dp.cantidad, dp.valor_unitario, dp.total AS total_linea
      FROM clientes c
      JOIN pedidos p ON c.id = p.cliente_id
      JOIN detalles_pedidos dp ON p.id = dp.pedido_id
      JOIN productos pr ON pr.id = dp.producto_id
     WHERE TRUNC(p.fecha) BETWEEN p_desde AND p_hasta
     ORDER BY p.fecha ASC;
END sp_detalle_ventas_rango;
/
```

*Evidencia (creación):* ![funcion_4.png](Registro%20visual/oracle/funcion_4.png)

*Llamada:*

```sql
EXEC sp_detalle_ventas_rango(DATE '2026-07-04', DATE '2026-07-13', :rc);
PRINT rc
```

*Evidencia (llamada):* ![llamada-5.png](Registro%20visual/oracle/llamada-5.png)

## SP-05. Ventas por cliente

**Origen:** Consulta 7 (agrupamiento SUM, COUNT, AVG)

**Narrativa:** Gerencia pide identificar a los clientes más valiosos de un periodo: total facturado, número de pedidos y ticket promedio. El rango de fechas deja de estar escrito en la consulta y pasa a ser parámetro; el resultado se ordena del mayor al menor total.

**Parámetros:** `p_desde`, `p_hasta`

### MySQL 8.0

```sql
DELIMITER $$
DROP PROCEDURE IF EXISTS sp_ventas_por_cliente$$
CREATE PROCEDURE sp_ventas_por_cliente(IN p_desde DATE, IN p_hasta DATE)
BEGIN
    SELECT c.id AS cliente_id, c.nombre, SUM(p.total) AS total_suma,
           COUNT(p.id) AS cuenta_total, ROUND(AVG(p.total), 2) AS promedio
    FROM clientes AS c
    JOIN pedidos AS p ON c.id = p.cliente_id
    WHERE DATE(p.fecha) BETWEEN p_desde AND p_hasta
    GROUP BY c.id, c.nombre
    ORDER BY total_suma DESC;
END$$
DELIMITER ;
```

*Evidencia (creación):* ![funcion_5.png](Registro%20visual/mysql/funcion_5.png)

*Llamada:*

```sql
CALL sp_ventas_por_cliente('2026-07-04','2026-07-13');
```

*Evidencia (llamada):* ![llamada-5.png](Registro%20visual/mysql/llamada-5.png)

### PostgreSQL 17

```sql
CREATE OR REPLACE FUNCTION sp_ventas_por_cliente(p_desde DATE, p_hasta DATE)
RETURNS TABLE(cliente_id INT, nombre VARCHAR, total_suma NUMERIC,
              cuenta_total BIGINT, promedio NUMERIC)
LANGUAGE sql AS $$
    SELECT c.id, c.nombre, SUM(p.total), COUNT(p.id), ROUND(AVG(p.total), 2)
    FROM clientes AS c
    JOIN pedidos AS p ON c.id = p.cliente_id
    WHERE p.fecha::date BETWEEN p_desde AND p_hasta
    GROUP BY c.id, c.nombre
    ORDER BY SUM(p.total) DESC;
$$;
```

*Evidencia (creación):* ![funcion_5.png](Registro%20visual/postgresql/funcion_5.png)

*Llamada:*

```sql
SELECT * FROM sp_ventas_por_cliente('2026-07-04','2026-07-13');
```

*Evidencia (llamada):* ![llamada-5.png](Registro%20visual/postgresql/llamada-5.png)

### SQL Server 2022

```sql
CREATE OR ALTER PROCEDURE sp_ventas_por_cliente
    @p_desde DATE,
    @p_hasta DATE
AS
BEGIN
    SET NOCOUNT ON;
    SELECT c.id AS cliente_id, c.nombre, SUM(p.total) AS total_suma,
           COUNT(p.id) AS cuenta_total, ROUND(AVG(p.total), 2) AS promedio
    FROM clientes AS c
    JOIN pedidos AS p ON c.id = p.cliente_id
    WHERE CAST(p.fecha AS DATE) BETWEEN @p_desde AND @p_hasta
    GROUP BY c.id, c.nombre
    ORDER BY total_suma DESC;
END;
GO
```

*Evidencia (creación):* ![funcion_5.png](Registro%20visual/sqlserver/funcion_5.png)

*Llamada:*

```sql
EXEC sp_ventas_por_cliente '2026-07-04','2026-07-13';
```

*Evidencia (llamada):* ![llamada-5.png](Registro%20visual/sqlserver/llamada-5.png)

### Oracle XE 21

```sql
CREATE OR REPLACE PROCEDURE sp_ventas_por_cliente(
    p_desde IN DATE, p_hasta IN DATE,
    p_cursor OUT SYS_REFCURSOR)
AS
BEGIN
    OPEN p_cursor FOR
    SELECT c.id AS cliente_id, c.nombre, SUM(p.total) AS total_suma,
           COUNT(p.id) AS cuenta_total, ROUND(AVG(p.total), 2) AS promedio
      FROM clientes c
      JOIN pedidos p ON c.id = p.cliente_id
     WHERE TRUNC(p.fecha) BETWEEN p_desde AND p_hasta
     GROUP BY c.id, c.nombre
     ORDER BY total_suma DESC;
END sp_ventas_por_cliente;
/
```

*Evidencia (creación):* ![funcion_5.png](Registro%20visual/oracle/funcion_5.png)

*Llamada:*

```sql
EXEC sp_ventas_por_cliente(DATE '2026-07-04', DATE '2026-07-13', :rc);
PRINT rc
```

*Evidencia (llamada):* ![llamada-6.png](Registro%20visual/oracle/llamada-6.png)

## SP-06. Clientes sin pedidos

**Origen:** Consulta 8 (subconsulta NOT IN)

**Narrativa:** Marketing quiere reactivar a los clientes que no compraron en un periodo. La subconsulta con un mes fijo se reemplaza por un rango recibido por parámetro.

**Parámetros:** `p_desde`, `p_hasta`

### MySQL 8.0

```sql
DELIMITER $$
DROP PROCEDURE IF EXISTS sp_clientes_sin_pedidos$$
CREATE PROCEDURE sp_clientes_sin_pedidos(IN p_desde DATE, IN p_hasta DATE)
BEGIN
    SELECT c.id, c.nombre, c.telefono, c.email
    FROM clientes AS c
    WHERE c.id NOT IN (SELECT p.cliente_id FROM pedidos AS p
                       WHERE DATE(p.fecha) BETWEEN p_desde AND p_hasta)
    ORDER BY c.nombre;
END$$
DELIMITER ;
```

*Evidencia (creación):* ![funcion_6.png](Registro%20visual/mysql/funcion_6.png)

*Llamada:*

```sql
CALL sp_clientes_sin_pedidos('2026-03-01','2026-03-30');
```

*Evidencia (llamada):* ![llamada-6.png](Registro%20visual/mysql/llamada-6.png)

### PostgreSQL 17

```sql
CREATE OR REPLACE FUNCTION sp_clientes_sin_pedidos(p_desde DATE, p_hasta DATE)
RETURNS TABLE(id INT, nombre VARCHAR, telefono VARCHAR, email VARCHAR)
LANGUAGE sql AS $$
    SELECT c.id, c.nombre, c.telefono, c.email
    FROM clientes AS c
    WHERE c.id NOT IN (SELECT p.cliente_id FROM pedidos AS p
                       WHERE p.fecha::date BETWEEN p_desde AND p_hasta)
    ORDER BY c.nombre;
$$;
```

*Evidencia (creación):* ![funcion_6.png](Registro%20visual/postgresql/funcion_6.png)

*Llamada:*

```sql
SELECT * FROM sp_clientes_sin_pedidos('2026-03-01','2026-03-30');
```

*Evidencia (llamada):* ![llamada-6.png](Registro%20visual/postgresql/llamada-6.png)

### SQL Server 2022

```sql
CREATE OR ALTER PROCEDURE sp_clientes_sin_pedidos
    @p_desde DATE,
    @p_hasta DATE
AS
BEGIN
    SET NOCOUNT ON;
    SELECT c.id, c.nombre, c.telefono, c.email
    FROM clientes AS c
    WHERE c.id NOT IN (SELECT p.cliente_id FROM pedidos AS p
                       WHERE CAST(p.fecha AS DATE) BETWEEN @p_desde AND @p_hasta)
    ORDER BY c.nombre;
END;
GO
```

*Evidencia (creación):* ![funcion_6.png](Registro%20visual/sqlserver/funcion_6.png)

*Llamada:*

```sql
EXEC sp_clientes_sin_pedidos '2026-03-01','2026-03-30';
```

*Evidencia (llamada):* ![llamada-6.png](Registro%20visual/sqlserver/llamada-6.png)

### Oracle XE 21

```sql
CREATE OR REPLACE PROCEDURE sp_clientes_sin_pedidos(
    p_desde IN DATE, p_hasta IN DATE,
    p_cursor OUT SYS_REFCURSOR)
AS
BEGIN
    OPEN p_cursor FOR
    SELECT c.id, c.nombre, c.telefono, c.email
      FROM clientes c
     WHERE c.id NOT IN (SELECT p.cliente_id FROM pedidos p
                         WHERE TRUNC(p.fecha) BETWEEN p_desde AND p_hasta)
     ORDER BY c.nombre;
END sp_clientes_sin_pedidos;
/
```

*Evidencia (creación):* ![funcion_6.png](Registro%20visual/oracle/funcion_6.png)

*Llamada:*

```sql
EXEC sp_clientes_sin_pedidos(DATE '2026-03-01', DATE '2026-03-30', :rc);
PRINT rc
```

*Evidencia (llamada):* ![llamada-7.png](Registro%20visual/oracle/llamada-7.png)

## SP-07. Ranking de productos más vendidos del mes

**Origen:** Consulta avanzada nueva (función de ventana RANK)

**Narrativa:** Gerencia quiere saber qué productos lideran las ventas de un mes y con qué posición. Se agrupa por producto y se calcula su posición con `RANK() OVER (ORDER BY SUM(total) DESC)`; el parámetro `p_top` limita el ranking a los N primeros (los empates comparten posición).

**Parámetros:** `p_anio`, `p_mes`, `p_top`

### MySQL 8.0

```sql
DELIMITER $$
DROP PROCEDURE IF EXISTS sp_ranking_productos_mes$$
CREATE PROCEDURE sp_ranking_productos_mes(IN p_anio INT, IN p_mes INT, IN p_top INT)
BEGIN
    SELECT r.posicion, r.producto, r.unidades, r.ingresos
    FROM (
        SELECT RANK() OVER (ORDER BY SUM(dp.total) DESC) AS posicion,
               pr.nombre AS producto,
               SUM(dp.cantidad) AS unidades,
               SUM(dp.total)    AS ingresos
        FROM detalles_pedidos AS dp
        JOIN pedidos   AS p  ON p.id  = dp.pedido_id
        JOIN productos AS pr ON pr.id = dp.producto_id
        WHERE YEAR(p.fecha) = p_anio AND MONTH(p.fecha) = p_mes
        GROUP BY pr.id, pr.nombre
    ) AS r
    WHERE r.posicion <= p_top
    ORDER BY r.posicion, r.producto;
END$$
DELIMITER ;
```

*Evidencia (creación):* ![funcion_7.png](Registro%20visual/mysql/funcion_7.png)

*Llamada:*

```sql
CALL sp_ranking_productos_mes(2026,7,3);
```

*Evidencia (llamada):* ![llamada-7.png](Registro%20visual/mysql/llamada-7.png)

### PostgreSQL 17

```sql
CREATE OR REPLACE FUNCTION sp_ranking_productos_mes(p_anio INT, p_mes INT, p_top INT)
RETURNS TABLE(posicion BIGINT, producto VARCHAR, unidades NUMERIC, ingresos NUMERIC)
LANGUAGE sql AS $$
    SELECT r.posicion, r.producto, r.unidades, r.ingresos
    FROM (
        SELECT RANK() OVER (ORDER BY SUM(dp.total) DESC) AS posicion,
               pr.nombre AS producto,
               SUM(dp.cantidad) AS unidades,
               SUM(dp.total)    AS ingresos
        FROM detalles_pedidos AS dp
        JOIN pedidos   AS p  ON p.id  = dp.pedido_id
        JOIN productos AS pr ON pr.id = dp.producto_id
        WHERE EXTRACT(YEAR  FROM p.fecha) = p_anio
          AND EXTRACT(MONTH FROM p.fecha) = p_mes
        GROUP BY pr.id, pr.nombre
    ) AS r
    WHERE r.posicion <= p_top
    ORDER BY r.posicion, r.producto;
$$;
```

*Evidencia (creación):* ![funcion_7.png](Registro%20visual/postgresql/funcion_7.png)

*Llamada:*

```sql
SELECT * FROM sp_ranking_productos_mes(2026,7,3);
```

*Evidencia (llamada):* ![llamada-7.png](Registro%20visual/postgresql/llamada-7.png)

### SQL Server 2022

```sql
CREATE OR ALTER PROCEDURE sp_ranking_productos_mes
    @p_anio INT,
    @p_mes  INT,
    @p_top  INT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT r.posicion, r.producto, r.unidades, r.ingresos
    FROM (
        SELECT RANK() OVER (ORDER BY SUM(dp.total) DESC) AS posicion,
               pr.nombre AS producto,
               SUM(dp.cantidad) AS unidades,
               SUM(dp.total)    AS ingresos
        FROM detalles_pedidos AS dp
        JOIN pedidos   AS p  ON p.id  = dp.pedido_id
        JOIN productos AS pr ON pr.id = dp.producto_id
        WHERE YEAR(p.fecha) = @p_anio AND MONTH(p.fecha) = @p_mes
        GROUP BY pr.id, pr.nombre
    ) AS r
    WHERE r.posicion <= @p_top
    ORDER BY r.posicion, r.producto;
END;
GO
```

*Evidencia (creación):* ![funcion_7.png](Registro%20visual/sqlserver/funcion_7.png)

*Llamada:*

```sql
EXEC sp_ranking_productos_mes 2026,7,3;
```

*Evidencia (llamada):* ![llamada-7.png](Registro%20visual/sqlserver/llamada-7.png)

### Oracle XE 21

```sql
CREATE OR REPLACE PROCEDURE sp_ranking_productos_mes(
    p_anio IN NUMBER, p_mes IN NUMBER, p_top IN NUMBER,
    p_cursor OUT SYS_REFCURSOR)
AS
BEGIN
    OPEN p_cursor FOR
    SELECT r.posicion, r.producto, r.unidades, r.ingresos
      FROM (
            SELECT RANK() OVER (ORDER BY SUM(dp.total) DESC) AS posicion,
                   pr.nombre AS producto,
                   SUM(dp.cantidad) AS unidades,
                   SUM(dp.total)    AS ingresos
              FROM detalles_pedidos dp
              JOIN pedidos   p  ON p.id  = dp.pedido_id
              JOIN productos pr ON pr.id = dp.producto_id
             WHERE EXTRACT(YEAR FROM p.fecha) = p_anio
               AND EXTRACT(MONTH FROM p.fecha) = p_mes
             GROUP BY pr.id, pr.nombre
           ) r
     WHERE r.posicion <= p_top
     ORDER BY r.posicion, r.producto;
END sp_ranking_productos_mes;
/
```

*Evidencia (creación):* ![funcion_7.png](Registro%20visual/oracle/funcion_7.png)

*Llamada:*

```sql
EXEC sp_ranking_productos_mes(2026, 7, 3, :rc);
PRINT rc
```

*Evidencia (llamada):* ![llamada-8.png](Registro%20visual/oracle/llamada-8.png)

## SP-08. Clientes con ticket sobre el promedio

**Origen:** Consulta avanzada nueva (CTE)

**Narrativa:** Para dirigir ofertas a los mejores clientes se compara el ticket promedio de cada cliente con el ticket promedio general del periodo. Tres expresiones comunes de tabla (`periodo`, `general`, `por_cliente`) separan los pasos y la consulta final deja solo a quienes superan el promedio.

**Parámetros:** `p_desde`, `p_hasta`

### MySQL 8.0

```sql
DELIMITER $$
DROP PROCEDURE IF EXISTS sp_clientes_sobre_promedio$$
CREATE PROCEDURE sp_clientes_sobre_promedio(IN p_desde DATE, IN p_hasta DATE)
BEGIN
    WITH periodo AS (
        SELECT p.cliente_id, p.total
        FROM pedidos AS p
        WHERE DATE(p.fecha) BETWEEN p_desde AND p_hasta
    ),
    general AS (SELECT AVG(total) AS ticket FROM periodo),
    por_cliente AS (
        SELECT cliente_id, COUNT(*) AS pedidos, AVG(total) AS ticket
        FROM periodo GROUP BY cliente_id
    )
    SELECT c.nombre AS cliente, pc.pedidos,
           ROUND(pc.ticket, 2) AS ticket_cliente, ROUND(g.ticket, 2) AS ticket_general
    FROM por_cliente AS pc
    JOIN clientes AS c ON c.id = pc.cliente_id
    CROSS JOIN general AS g
    WHERE pc.ticket > g.ticket
    ORDER BY pc.ticket DESC;
END$$
DELIMITER ;
```

*Evidencia (creación):* ![funcion_8.png](Registro%20visual/mysql/funcion_8.png)

*Llamada:*

```sql
CALL sp_clientes_sobre_promedio('2026-07-01','2026-07-31');
```

*Evidencia (llamada):* ![llamada-8.png](Registro%20visual/mysql/llamada-8.png)

### PostgreSQL 17

```sql
CREATE OR REPLACE FUNCTION sp_clientes_sobre_promedio(p_desde DATE, p_hasta DATE)
RETURNS TABLE(cliente VARCHAR, pedidos BIGINT, ticket_cliente NUMERIC, ticket_general NUMERIC)
LANGUAGE sql AS $$
    WITH periodo AS (
        SELECT p.cliente_id, p.total
        FROM pedidos AS p
        WHERE p.fecha::date BETWEEN p_desde AND p_hasta
    ),
    general AS (SELECT AVG(total) AS ticket FROM periodo),
    por_cliente AS (
        SELECT cliente_id, COUNT(*) AS pedidos, AVG(total) AS ticket
        FROM periodo GROUP BY cliente_id
    )
    SELECT c.nombre, pc.pedidos, ROUND(pc.ticket, 2), ROUND(g.ticket, 2)
    FROM por_cliente AS pc
    JOIN clientes AS c ON c.id = pc.cliente_id
    CROSS JOIN general AS g
    WHERE pc.ticket > g.ticket
    ORDER BY pc.ticket DESC;
$$;
```

*Evidencia (creación):* ![funcion_8.png](Registro%20visual/postgresql/funcion_8.png)

*Llamada:*

```sql
SELECT * FROM sp_clientes_sobre_promedio('2026-07-01','2026-07-31');
```

*Evidencia (llamada):* ![llamada-8.png](Registro%20visual/postgresql/llamada-8.png)

### SQL Server 2022

```sql
CREATE OR ALTER PROCEDURE sp_clientes_sobre_promedio
    @p_desde DATE,
    @p_hasta DATE
AS
BEGIN
    SET NOCOUNT ON;
    WITH periodo AS (
        SELECT p.cliente_id, p.total
        FROM pedidos AS p
        WHERE CAST(p.fecha AS DATE) BETWEEN @p_desde AND @p_hasta
    ),
    general AS (SELECT AVG(total) AS ticket FROM periodo),
    por_cliente AS (
        SELECT cliente_id, COUNT(*) AS pedidos, AVG(total) AS ticket
        FROM periodo GROUP BY cliente_id
    )
    SELECT c.nombre AS cliente, pc.pedidos,
           ROUND(pc.ticket, 2) AS ticket_cliente, ROUND(g.ticket, 2) AS ticket_general
    FROM por_cliente AS pc
    JOIN clientes AS c ON c.id = pc.cliente_id
    CROSS JOIN general AS g
    WHERE pc.ticket > g.ticket
    ORDER BY pc.ticket DESC;
END;
GO
```

*Evidencia (creación):* ![funcion_8.png](Registro%20visual/sqlserver/funcion_8.png)

*Llamada:*

```sql
EXEC sp_clientes_sobre_promedio '2026-07-01','2026-07-31';
```

*Evidencia (llamada):* ![llamada-8.png](Registro%20visual/sqlserver/llamada-8.png)

### Oracle XE 21

```sql
CREATE OR REPLACE PROCEDURE sp_clientes_sobre_promedio(
    p_desde IN DATE, p_hasta IN DATE,
    p_cursor OUT SYS_REFCURSOR)
AS
BEGIN
    OPEN p_cursor FOR
    WITH periodo AS (
           SELECT p.cliente_id, p.total
             FROM pedidos p
            WHERE TRUNC(p.fecha) BETWEEN p_desde AND p_hasta
         ),
         general AS (SELECT AVG(total) AS ticket FROM periodo),
         por_cliente AS (
           SELECT cliente_id, COUNT(*) AS pedidos, AVG(total) AS ticket
             FROM periodo GROUP BY cliente_id
         )
    SELECT c.nombre AS cliente, pc.pedidos,
           ROUND(pc.ticket, 2) AS ticket_cliente, ROUND(g.ticket, 2) AS ticket_general
      FROM por_cliente pc
      JOIN clientes c ON c.id = pc.cliente_id
     CROSS JOIN general g
     WHERE pc.ticket > g.ticket
     ORDER BY pc.ticket DESC;
END sp_clientes_sobre_promedio;
/
```

*Evidencia (creación):* ![funcion_8.png](Registro%20visual/oracle/funcion_8.png)

*Llamada:*

```sql
EXEC sp_clientes_sobre_promedio(DATE '2026-07-01', DATE '2026-07-31', :rc);
PRINT rc
```

*Evidencia (llamada):* ![llamada-9.png](Registro%20visual/oracle/llamada-9.png)

## SP-09. Ventas diarias con acumulado

**Origen:** Consulta avanzada nueva (SUM OVER)

**Narrativa:** Administración quiere ver la venta de cada día y cómo se va acumulando en el periodo. Se agrupa por día y se aplica `SUM(venta_dia) OVER (ORDER BY dia)` para obtener el acumulado.

**Parámetros:** `p_desde`, `p_hasta`

### MySQL 8.0

```sql
DELIMITER $$
DROP PROCEDURE IF EXISTS sp_ventas_diarias_acumuladas$$
CREATE PROCEDURE sp_ventas_diarias_acumuladas(IN p_desde DATE, IN p_hasta DATE)
BEGIN
    SELECT d.dia, d.pedidos, d.venta_dia,
           SUM(d.venta_dia) OVER (ORDER BY d.dia) AS acumulado
    FROM (
        SELECT DATE(p.fecha) AS dia, COUNT(*) AS pedidos, SUM(p.total) AS venta_dia
        FROM pedidos AS p
        WHERE DATE(p.fecha) BETWEEN p_desde AND p_hasta
        GROUP BY DATE(p.fecha)
    ) AS d
    ORDER BY d.dia;
END$$

DELIMITER ;
DELIMITER ;
```

*Evidencia (creación):* ![funcion_9.png](Registro%20visual/mysql/funcion_9.png)

*Llamada:*

```sql
CALL sp_ventas_diarias_acumuladas('2026-07-01','2026-07-31');
```

*Evidencia (llamada):* ![llamada-9.png](Registro%20visual/mysql/llamada-9.png)

### PostgreSQL 17

```sql
CREATE OR REPLACE FUNCTION sp_ventas_diarias_acumuladas(p_desde DATE, p_hasta DATE)
RETURNS TABLE(dia DATE, pedidos BIGINT, venta_dia NUMERIC, acumulado NUMERIC)
LANGUAGE sql AS $$
    SELECT d.dia, d.pedidos, d.venta_dia,
           SUM(d.venta_dia) OVER (ORDER BY d.dia) AS acumulado
    FROM (
        SELECT p.fecha::date AS dia, COUNT(*) AS pedidos, SUM(p.total) AS venta_dia
        FROM pedidos AS p
        WHERE p.fecha::date BETWEEN p_desde AND p_hasta
        GROUP BY p.fecha::date
    ) AS d
    ORDER BY d.dia;
$$;
```

*Evidencia (creación):* ![funcion_9.png](Registro%20visual/postgresql/funcion_9.png)

*Llamada:*

```sql
SELECT * FROM sp_ventas_diarias_acumuladas('2026-07-01','2026-07-31');
```

*Evidencia (llamada):* ![llamada-9.png](Registro%20visual/postgresql/llamada-9.png)

### SQL Server 2022

```sql
CREATE OR ALTER PROCEDURE sp_ventas_diarias_acumuladas
    @p_desde DATE,
    @p_hasta DATE
AS
BEGIN
    SET NOCOUNT ON;
    SELECT d.dia, d.pedidos, d.venta_dia,
           SUM(d.venta_dia) OVER (ORDER BY d.dia) AS acumulado
    FROM (
        SELECT CAST(p.fecha AS DATE) AS dia, COUNT(*) AS pedidos, SUM(p.total) AS venta_dia
        FROM pedidos AS p
        WHERE CAST(p.fecha AS DATE) BETWEEN @p_desde AND @p_hasta
        GROUP BY CAST(p.fecha AS DATE)
    ) AS d
    ORDER BY d.dia;
END;
GO
```

*Evidencia (creación):* ![funcion_9.png](Registro%20visual/sqlserver/funcion_9.png)

*Llamada:*

```sql
EXEC sp_ventas_diarias_acumuladas '2026-07-01','2026-07-31';
```

*Evidencia (llamada):* ![llamada-9.png](Registro%20visual/sqlserver/llamada-9.png)

### Oracle XE 21

```sql
CREATE OR REPLACE PROCEDURE sp_ventas_diarias_acumuladas(
    p_desde IN DATE, p_hasta IN DATE,
    p_cursor OUT SYS_REFCURSOR)
AS
BEGIN
    OPEN p_cursor FOR
    SELECT d.dia, d.pedidos, d.venta_dia,
           SUM(d.venta_dia) OVER (ORDER BY d.dia) AS acumulado
      FROM (
            SELECT TRUNC(p.fecha) AS dia, COUNT(*) AS pedidos, SUM(p.total) AS venta_dia
              FROM pedidos p
             WHERE TRUNC(p.fecha) BETWEEN p_desde AND p_hasta
             GROUP BY TRUNC(p.fecha)
           ) d
     ORDER BY d.dia;
END sp_ventas_diarias_acumuladas;
/
```

*Evidencia (creación):* ![funcion_9.png](Registro%20visual/oracle/funcion_9.png)

*Llamada:*

```sql
EXEC sp_ventas_diarias_acumuladas(DATE '2026-07-01', DATE '2026-07-31', :rc);
PRINT rc
```

*Evidencia (llamada):* ![llamada-10.png](Registro%20visual/oracle/llamada-10.png)

## Firma

**Elkin Eliecer Aguas Giraldo**
Estudiante de Ingeniería de Sistemas — Facultad de Ingeniería — Universidad de La Guajira
Rol: responsable de la instalación, configuración y verificación de los cuatro motores
Fecha del informe: 29/09/26