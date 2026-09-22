# BITÁCORA DE CONSULTAS DE BASE DE DATOS
UNIVERSIDAD DE LA GUAJIRA
Facultad de Ingeniería — Ingeniería de Sistemas
Proyecto BrasaGo

# 1. Introducción
Esta bitácora documenta el proceso de creación de la base de datos del proyecto BrasaGo y la ejecución de un conjunto de consultas SQL representativas (creación, lectura, combinación de tablas, filtros, agrupamiento y subconsultas) en los cuatro motores exigidos por el curso: MySQL, PostgreSQL, SQL Server y Oracle.
Para cada motor se presenta la misma batería de 8 consultas (con sus variantes), señalando las diferencias de sintaxis relevantes entre motores, junto con la evidencia visual de su ejecución.

# 2. Motor: MySQL

Herramienta utilizada: DBeaver / terminal mysql

## 1. Create — Insertar un nuevo cliente

Inserta un registro nuevo en la tabla clientes con datos de prueba.

```sql
INSERT INTO clientes(tipo_documento, numero_documento, nombre, telefono, email)
VALUES ("CC", "1043680256","Jaider Quintero Mendoza", "3122589615", "jq@example.com");
```

*Evidencia:* ![paso-1.png](Registro%20visual/mysql/paso-1.png)

## 2. Read — Consultar todos los clientes

Recupera todas las columnas y filas de la tabla clientes.

```sql
SELECT * FROM clientes;
```

*Evidencia:* ![paso-2.png](Registro%20visual/mysql/paso-2.png)

## 2.1. Read — Seleccionar columnas específicas

Limita el resultado a nombre, telefono y email, evitando traer columnas innecesarias.

```sql
SELECT nombre, telefono, email
FROM clientes;
```

*Evidencia:* ![paso-2.1.png](Registro%20visual/mysql/paso-2.1.png)

## 2.2. Read — Uso de alias de tabla

Repite la consulta anterior usando un alias (C) para la tabla clientes.

```sql
SELECT C.nombre, C.telefono, C.email
FROM clientes AS C;
```

*Evidencia:* ![paso-2.2.png](Registro%20visual/mysql/paso-2.2.png)

## 3. Consultar varias tablas (join implícito)

Combina clientes y pedidos mediante una condición WHERE que iguala las claves relacionadas.

```sql
SELECT *
FROM clientes, pedidos
WHERE clientes.id = pedidos.cliente_id
```

*Evidencia:* ![paso-3.png](Registro%20visual/mysql/paso-3.png)

## 3.1. Join implícito con alias

Misma consulta anterior, usando alias C y p para abreviar los nombres de tabla.

```sql
SELECT * FROM clientes AS C, pedidos AS p
WHERE C.id = p.cliente_id;
```

*Evidencia:* ![paso-3.1.png](Registro%20visual/mysql/paso-3.1.png)

## 3.2. Selección de columnas específicas con join implícito

Trae solo nombre y email del cliente, junto con todas las columnas de pedidos.

```sql
SELECT C.nombre, C.email, p.*
FROM clientes AS C, pedidos AS p
WHERE C.id = p.cliente_id;
```

*Evidencia:* ![paso-3.2.png](Registro%20visual/mysql/paso-3.2.png)

## 3.3. Join explícito (JOIN ON)

Misma consulta que 3.2, pero usando la sintaxis estándar JOIN ... ON, más legible y recomendada.

```sql
SELECT C.nombre, C.email, p.*
FROM clientes AS C
JOIN pedidos AS p ON (C.id = p.cliente_id);
```

*Evidencia:* ![paso-3.3.png](Registro%20visual/mysql/paso-3.3.png)

## 4. Filtro por fecha (join implícito)

Agrega una condición adicional en el WHERE para filtrar pedidos de una fecha puntual.

```sql
SELECT C.nombre, C.email, p.*
FROM clientes AS C, pedidos AS p
WHERE C.id = p.cliente_id AND fecha = "2026-05-18 19:19:29";
```

*Evidencia:* ![paso-4.png](Registro%20visual/mysql/paso-4.png)

## 4.2. Filtro por fecha (join explícito)

Misma condición de fecha, aplicada sobre la sintaxis JOIN ON.

```sql
SELECT C.nombre, C.email, p.*
FROM clientes AS C
JOIN pedidos AS p ON (C.id = p.cliente_id)
WHERE fecha = "2026-05-18 19:19:29";
```

*Evidencia:* ![paso-4.2.png](Registro%20visual/mysql/paso-4.2.png)

## 5.1. Operador LIKE — emails que inician con 'm'

Usa el patrón 'm%' para encontrar emails cuyo primer carácter sea la letra m.

```sql
SELECT * FROM clientes AS C
WHERE C.email LIKE 'm%';
```

*Evidencia:* ![paso-5.1.png](Registro%20visual/mysql/paso-5.1.png)

## 5.2. Operador LIKE con CONCAT — dominio example

Construye el patrón '%example%' dinámicamente para ubicar cualquier correo de ese dominio.

```sql
SELECT * FROM clientes AS C
WHERE C.email LIKE CONCAT('%','example','%');
```

*Evidencia:* ![paso-5.2.png](Registro%20visual/mysql/paso-5.2.png)

## 5.3. Múltiples JOIN con rango de fechas y ORDER BY

Une clientes, pedidos, detalles_pedidos y productos; filtra por rango de fechas y ordena ascendentemente.

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

```sql
DESCRIBE detalles_pedidos;
```

*Evidencia:* ![paso-6.png](Registro%20visual/mysql/paso-6.png)

## 7. Consulta de agrupamiento (SUM, COUNT, AVG)

Agrupa los pedidos por cliente dentro de un rango de fechas, calculando totales, cantidad y promedio.

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

```sql
INSERT INTO clientes (tipo_documento, numero_documento, nombre, telefono, email)
VALUES ('TI', '1043682056', 'Adriana Perez Mindiola', '3122564215', 'perz@example.com');

```

*Evidencia:* ![paso-1.png](Registro%20visual/postgresql/paso-1.png)

## 2. Read — Consultar todos los clientes

Recupera todas las columnas y filas de la tabla clientes.

```sql
SELECT * FROM clientes;
```

*Evidencia:* ![paso-2.png](Registro%20visual/postgresql/paso-2.png)

## 2.1. Read — Seleccionar columnas específicas

Limita el resultado a nombre, telefono y email, evitando traer columnas innecesarias.

```sql
SELECT nombre, telefono, email FROM clientes;
```

*Evidencia:* ![paso-2.1.png](Registro%20visual/postgresql/paso-2.1.png)

## 2.2. Read — Uso de alias de tabla

Repite la consulta anterior usando un alias (C) para la tabla clientes.

```sql
SELECT C.nombre, C.telefono, C.email FROM clientes AS C;
```

*Evidencia:* ![paso-2.2.png](Registro%20visual/postgresql/paso-2.2.png)

## 3. Consultar varias tablas (join implícito)

Combina clientes y pedidos mediante una condición WHERE que iguala las claves relacionadas.

```sql
SELECT * FROM clientes, pedidos
WHERE clientes.id = pedidos.cliente_id;
```

*Evidencia:* ![paso-3.png](Registro%20visual/postgresql/paso-3.png)

## 3.1. Join implícito con alias

Misma consulta anterior, usando alias C y p para abreviar los nombres de tabla.

```sql
SELECT * FROM clientes AS C, pedidos AS p
WHERE C.id = p.cliente_id;
```

*Evidencia:* ![paso-3.1.png](Registro%20visual/postgresql/paso-3.1.png)

## 3.2. Selección de columnas específicas con join implícito

Trae solo nombre y email del cliente, junto con todas las columnas de pedidos.

```sql
SELECT C.nombre, C.email, p.*
FROM clientes AS C, pedidos AS p
WHERE C.id = p.cliente_id;
```

*Evidencia:* ![paso-3.2.png](Registro%20visual/postgresql/paso-3.2.png)

## 3.3. Join explícito (JOIN ON)

Misma consulta que 3.2, pero usando la sintaxis estándar JOIN ... ON, más legible y recomendada.

```sql
SELECT C.nombre, C.email, p.*
FROM clientes AS C
JOIN pedidos AS p ON (C.id = p.cliente_id);
```

*Evidencia:* ![paso-3.3.png](Registro%20visual/postgresql/paso-3.3.png)

## 4. Filtro por fecha (join implícito)

Agrega una condición adicional en el WHERE para filtrar pedidos de una fecha puntual.

```sql
SELECT C.nombre, C.email, p.*
FROM clientes AS C
JOIN pedidos AS p ON (C.id = p.cliente_id)
WHERE p.fecha = '2026-07-13 18:12:10';
```

*Evidencia:* ![paso-4.png](Registro%20visual/postgresql/paso-4.png)

## 4.2. Filtro por fecha (join explícito)

Misma condición de fecha, aplicada sobre la sintaxis JOIN ON.

```sql
SELECT C.nombre, C.email, p.*
FROM clientes AS C
JOIN pedidos AS p ON (C.id = p.cliente_id)
WHERE p.fecha = '2026-07-13 18:12:10';
```

*Evidencia:* ![paso-4.2.png](Registro%20visual/postgresql/paso-4.2.png)

## 5.1. Operador LIKE — emails que inician con 'm'

Usa el patrón 'm%' para encontrar emails cuyo primer carácter sea la letra m.

```sql
SELECT * FROM clientes AS C WHERE C.email LIKE 'm%';
```

*Evidencia:* ![paso-5.1.png](Registro%20visual/postgresql/paso-5.1.png)

## 5.2. Operador LIKE con CONCAT — dominio example

Construye el patrón '%example%' dinámicamente para ubicar cualquier email de ese dominio.

```sql
SELECT * FROM clientes AS C
WHERE C.email LIKE '%' || 'example' || '%';
```

*Evidencia:* ![paso-5.2.png](Registro%20visual/postgresql/paso-5.2.png)

## 5.3. Múltiples JOIN con rango de fechas y ORDER BY

Une clientes, pedidos, detalles_pedidos y productos; filtra por rango de fechas y ordena ascendentemente.

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

```sql
\d productos_ventas
-- alternativa SQL pura:
SELECT column_name, data_type FROM information_schema.columns
WHERE table_name = 'detalles_pedidos';;
```

*Evidencia:* ![paso-6.png](Registro%20visual/postgresql/paso-6.png)

## 7. Consulta de agrupamiento (SUM, COUNT, AVG)

Agrupa los pedidos por cliente dentro de un rango de fechas, calculando totales, cantidad y promedio.

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

```sql
INSERT INTO clientes (tipo_documento, numero_documento, nombre, telefono, email)
VALUES ('TI', '1589489185', 'Elizabet hernandez ochoa', '3152849637', 'Elizabeth@example.com');
```

*Evidencia:* ![paso-1.png](Registro%20visual/sqlserver/paso-1.png)

## 2. Read — Consultar todos los clientes

Recupera todas las columnas y filas de la tabla clientes.

```sql
SELECT * FROM clientes;
```

*Evidencia:* ![paso-2.png](Registro%20visual/sqlserver/paso-2.png)

## 2.1. Read — Seleccionar columnas específicas

Limita el resultado a nombre, telefono y email, evitando traer columnas innecesarias.

```sql
SELECT nombre, telefono, email FROM clientes;
```

*Evidencia:* ![paso-2.1.png](Registro%20visual/sqlserver/paso-2.1.png)

## 2.2. Read — Uso de alias de tabla

Repite la consulta anterior usando un alias (C) para la tabla clientes.

```sql
SELECT C.nombre, C.telefono, C.email FROM clientes AS C;
```

*Evidencia:* ![paso-2.2.png](Registro%20visual/sqlserver/paso-2.2.png)

## 3. Consultar varias tablas (join implícito)

Combina clientes y pedidos mediante una condición WHERE que iguala las claves relacionadas.

```sql
SELECT * FROM clientes, pedidos
WHERE clientes.id = pedidos.cliente_id;
```

*Evidencia:* ![paso-3.png](Registro%20visual/sqlserver/paso-3.png)

## 3.1. Join implícito con alias

Misma consulta anterior, usando alias C y p para abreviar los nombres de tabla.

```sql
SELECT * FROM clientes AS C, pedidos AS p
WHERE C.id = p.cliente_id;
```

*Evidencia:* ![paso-3.1.png](Registro%20visual/sqlserver/paso-3.1.png)

## 3.2. Selección de columnas específicas con join implícito

Trae solo nombre y email del cliente, junto con todas las columnas de pedidos.

```sql
SELECT C.nombre, C.email, p.*
FROM clientes AS C, pedidos AS p
WHERE C.id = p.cliente_id;
```

*Evidencia:* ![paso-3.2.png](Registro%20visual/sqlserver/paso-3.2.png)

## 3.3. Join explícito (JOIN ON)

Misma consulta que 3.2, pero usando la sintaxis estándar JOIN ... ON, más legible y recomendada.

```sql
SELECT C.nombre, C.email, p.*
FROM clientes AS C
JOIN pedidos AS p ON (C.id = p.cliente_id);
```

*Evidencia:* ![paso-3.3.png](Registro%20visual/sqlserver/paso-3.3.png)

## 4. Filtro por fecha (join implícito)

Agrega una condición adicional en el WHERE para filtrar pedidos de una fecha puntual.

```sql
SELECT C.nombre, C.email, p.*
FROM clientes AS C
JOIN pedidos AS p ON (C.id = p.cliente_id)
WHERE p.fecha = '2026-07-13 18:12:10';
```

*Evidencia:* ![paso-4.png](Registro%20visual/sqlserver/paso-4.png)

## 4.2. Filtro por fecha (join explícito)

Misma condición de fecha, aplicada sobre la sintaxis JOIN ON.

```sql
SELECT C.nombre, C.email, p.*
FROM clientes AS C
JOIN pedidos AS p ON (C.id = p.cliente_id)
WHERE p.fecha = '2026-07-13 18:12:10';
```

*Evidencia:* ![paso-4.2.png](Registro%20visual/sqlserver/paso-4.2.png)

## 5.1. Operador LIKE — emails que inician con 'm'

Usa el patrón 'm%' para encontrar correos cuyo primer carácter sea la letra m.

```sql
SELECT * FROM clientes AS C WHERE C.email LIKE 'm%';
```

*Evidencia:* ![paso-5.1.png](Registro%20visual/sqlserver/paso-5.1.png)

## 5.2. Operador LIKE con CONCAT — dominio example

Construye el patrón '%example%' dinámicamente para ubicar cualquier email de ese dominio.

```sql
SELECT * FROM clientes AS C
WHERE C.email LIKE '%' + 'example' + '%';
```

*Evidencia:* ![paso-5.2.png](Registro%20visual/sqlserver/paso-5.2.png)

## 6. Describir estructura de una tabla

Muestra las columnas, tipos de dato y restricciones de la tabla productos.

```sql
EXEC sp_help 'productos';
-- alternativa SQL pura:
SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'productos';
```

*Evidencia:* ![paso-6.png](Registro%20visual/sqlserver/paso-6.png)

## 7. Consulta de agrupamiento (SUM, COUNT, AVG)

Agrupa las ventas por cliente dentro de un rango de fechas, calculando totales, cantidad y promedio.

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

```sql
INSERT INTO clientes(tipo_documento, numero_documento, nombre, telefono, email)
VALUES ('CC', '1055784129', 'elias neron valdez', '3006185397', 'nerona@example.com');
```

*Evidencia:* ![paso-1.png](Registro%20visual/oracle/paso-1.png)

## 2. Read — Consultar todos los clientes

Recupera todas las columnas y filas de la tabla clientes.

```sql
SELECT * FROM clientes;
```

*Evidencia:* ![paso-2.png](Registro%20visual/oracle/paso-2.png)

## 2.1. Read — Seleccionar columnas específicas

Limita el resultado a nombre, telefono y email, evitando traer columnas innecesarias.

```sql
SELECT nombre, telefono, email FROM clientes;
```

*Evidencia:* ![paso-2.1.png](Registro%20visual/oracle/paso-2.1.png)

## 2.2. Read — Uso de alias de tabla

Repite la consulta anterior usando un alias (C) para la tabla clientes.

```sql
SELECT C.nombre, C.telefono, C.email FROM clientes C;
```

*Evidencia:* ![paso-2.2.png](Registro%20visual/oracle/paso-2.2.png)

## 3. Consultar varias tablas (join implícito)

Combina clientes y pedidos mediante una condición WHERE que iguala las claves relacionadas.

```sql
SELECT * FROM clientes, pedidos
WHERE clientes.id = pedidos.cliente_id
```

*Evidencia:* ![paso-3.png](Registro%20visual/oracle/paso-3.png)

## 3.1. Join implícito con alias

Misma consulta anterior, usando alias C y p para abreviar los nombres de tabla.

```sql
SELECT * FROM clientes C, pedidos p
WHERE C.id = p.cliente_id;
```

*Evidencia:* ![paso-3.1.png](Registro%20visual/oracle/paso-3.1.png)

## 3.2. Selección de columnas específicas con join implícito

Trae solo nombre y email del cliente, junto con todas las columnas de pedidos.

```sql
SELECT C.nombre, C.email, p.*
FROM clientes C, pedidos p
WHERE C.id = p.cliente_id;
```

*Evidencia:* ![paso-3.2.png](Registro%20visual/oracle/paso-3.2.png)

## 3.3. Join explícito (JOIN ON)

Misma consulta que 3.2, pero usando la sintaxis estándar JOIN ... ON, más legible y recomendada.

```sql
SELECT C.nombre, C.email, p.*
FROM clientes C
JOIN pedidos p ON (C.id = p.cliente_id);
```

*Evidencia:* ![paso-3.3.png](Registro%20visual/oracle/paso-3.3.png)

## 4. Filtro por fecha (join implícito)

Agrega una condición adicional en el WHERE para filtrar pedidos de una fecha puntual.

```sql
SELECT c.nombre, c.email, p.*
FROM clientes c
JOIN pedidos p ON c.id = p.cliente_id
WHERE p.fecha = TO_DATE('2026-05-18 19:19:29','YYYY-MM-DD HH24:MI:SS');
```

*Evidencia:* ![paso-4.png](Registro%20visual/oracle/paso-4.png)

## 4.2. Filtro por fecha (join explícito)

Misma condición de fecha, aplicada sobre la sintaxis JOIN ON.

```sql
SELECT C.nombre, C.email, p.*
FROM clientes C
JOIN pedidos p ON (C.id = p.cliente_id)
WHERE p.fecha = TO_DATE('2026-05-18 19:19:29','YYYY-MM-DD HH24:MI:SS');
```

*Evidencia:* ![paso-4.2.png](Registro%20visual/oracle/paso-4.2.png)

## 5.1. Operador LIKE — correos que inician con 'm'

Usa el patrón 'm%' para encontrar emails cuyo primer carácter sea la letra m.

```sql
SELECT * FROM clientes C WHERE C.email LIKE 'm%';
```

*Evidencia:* ![paso-5.1.png](Registro%20visual/oracle/paso-5.1.png)

## 5.2. Operador LIKE con CONCAT — dominio example

Construye el patrón '%example%' dinámicamente para ubicar cualquier correo de ese dominio.

```sql
SELECT * FROM clientes C
WHERE C.email LIKE '%' || 'example' || '%';
```

*Evidencia:* ![paso-5.2.png](Registro%20visual/oracle/paso-5.2.png)

## 5.3. Múltiples JOIN con rango de fechas y ORDER BY

Une clientes, pedidos, detalles_pedidos y productos; filtra por rango de fechas y ordena ascendentemente.

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

```sql
DESCRIBE detalles_pedidos;
```

*Evidencia:* ![paso-6.png](Registro%20visual/oracle/paso-6.png)

## 7. Consulta de agrupamiento (SUM, COUNT, AVG)

Agrupa los pedidos por cliente dentro de un rango de fechas, calculando totales, cantidad y promedio.

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

```sql
SELECT * FROM clientes C
WHERE C.id NOT IN (
  SELECT p.cliente_id FROM pedidos p
  WHERE p.fecha BETWEEN TO_DATE('2026-03-01','YYYY-MM-DD')
  AND TO_DATE('2026-03-30','YYYY-MM-DD'));
```

*Evidencia:* ![paso-8.png](Registro%20visual/oracle/paso-8.png)

## Firma

**Elkin Eliecer Aguas Giraldo**
Estudiante de Ingeniería de Sistemas — Facultad de Ingeniería — Universidad de La Guajira
Rol: responsable de la instalación, configuración y verificación de los cuatro motores
Fecha del informe: 22/09/26