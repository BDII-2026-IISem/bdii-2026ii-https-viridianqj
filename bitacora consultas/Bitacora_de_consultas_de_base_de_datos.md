# BITÁCORA DE CONSULTAS DE BASE DE DATOS
UNIVERSIDAD DE LA GUAJIRA
Facultad de Ingeniería — Ingeniería de Sistemas
Proyecto BrasaGo

# 1. Introducción
Esta bitácora documenta el proceso de creación de la base de datos del proyecto BrasaGo y la ejecución de un conjunto de consultas SQL representativas (consultas combinadas, agrupaciones y subconsultas) en los cuatro motores exigidos por el curso: MySQL, PostgreSQL, SQL Server y Oracle.
Para cada motor se presenta la misma batería de 8 consultas (con sus variantes), señalando las diferencias de sintaxis relevantes entre motores, junto con la evidencia visual de su ejecución. Cada consulta incluye además un **contexto de negocio**: el motivo operativo real de BrasaGo que llevó a ejecutar ese cambio o esa lectura sobre la base de datos.
Finalmente, la sección 6 presenta un patrón de auditoría inmutable (triggers) sobre `pedidos`, `detalles_pedidos` y `productos`, implementado en los cuatro motores.

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

## Firma

**Elkin Eliecer Aguas Giraldo**
Estudiante de Ingeniería de Sistemas — Facultad de Ingeniería — Universidad de La Guajira
Rol: responsable de la instalación, configuración y verificación de los cuatro motores
Fecha del informe: 29/09/26