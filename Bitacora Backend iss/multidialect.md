# Verificación multidialecto: BrasaGo

Ejecución del mismo código, sin cambios, sobre cuatro motores de base de datos. Es la evidencia que pide el GATE de negocio de la guía Backend-2026 (Django + DRF), que cierra la Fase I en ISS-14.

| | |
|---|---|
| **Proyecto** | BrasaGo, backend Django + DRF |
| **Fecha** | 8 de octubre de 2026, 17:24 a 17:32|
| **Django** | 5.2.17 (Python 3.14) |
| **Pruebas ejecutadas** | 49 (modelos, serializers, API, admin y OpenAPI) |

## 1. Entorno

Los cuatro motores corren en contenedores Docker, todos en estado `healthy` al iniciar la prueba.

| Motor | Imagen | Contenedor | Puerto |
|---|---|---|---|
| PostgreSQL | `postgres:17` | `postgres-server` | 5432 |
| MySQL | `mysql:8.0` | `mysql-server` | 3306 |
| SQL Server | `mcr.microsoft.com/mssql/server:2022-latest` | `mssql-server` | 1433 |
| Oracle XE | `gvenzl/oracle-xe:21-slim` | `oracle-server` | 1521 |

Drivers de Python: `psycopg[binary] 3.3.6` (PostgreSQL), `mysqlclient 2.3.0` (MySQL), `mssql-django 2.0.0` con `pyodbc` y *ODBC Driver 18 for SQL Server* (SQL Server) y `oracledb 26.0.1` (Oracle).

## 2. Procedimiento

1. Variables de cada motor en `.env` (la plantilla `.env.example` las documenta sin valores reales).
2. Una base vacía `brasago_django` por motor:
   - MySQL: `utf8mb4` con colación `utf8mb4_unicode_ci`.
   - SQL Server: base `brasago_django`.
   - Oracle: usuario `brasago_django` con los roles `CONNECT`, `RESOURCE` y `DBA`, en el servicio `XEPDB1`. El rol `DBA` permite que las pruebas de Django creen su usuario temporal.
3. El motor se elige por comando, con el prefijo `DB_ENGINE=<motor>`. Para cada uno:

```bash
DB_ENGINE=<motor> python manage.py check
DB_ENGINE=<motor> python manage.py migrate
DB_ENGINE=<motor> python manage.py test
```

## 3. Resultados

| Motor | `check` | `migrate` | Pruebas | Resultado |
|---|---|---|---|---|
| MySQL 8.0 | sin incidencias | 23 migraciones OK | 49 OK (1,239 s) | bien PASS |
| SQL Server 2022 | sin incidencias | 23 migraciones OK | 49 OK (1,781 s) | bien PASS |
| Oracle XE 21 | sin incidencias | 23 migraciones OK | 49 OK (1,723 s) | bien PASS |
| PostgreSQL 17 | sin incidencias | 23 migraciones OK | 49 OK | bien PASS |

> **Nota sobre PostgreSQL.** Es el motor de desarrollo del proyecto y venía pasando todas las pruebas (46 en OK el 5 de octubre, antes de ISS-14). La corrida con las 49 pruebas de ISS-14 también quedó en OK.

Las 23 migraciones corresponden a `contenttypes` (2), `auth` (12), `security` (1), `admin` (3), `client` (1), `product` (1), `venue` (1), `sale` (1) y `sessions` (1).

### Salida resumida de cada motor

**MySQL**

```
Found 49 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.................................................
Ran 49 tests in 1.239s

OK
Destroying test database for alias 'default'...
```

**SQL Server**

```
Found 49 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.................................................
Ran 49 tests in 1.781s

OK
Destroying test database for alias 'default'...
```

**Oracle**

```
Found 49 test(s).
Creating test database for alias 'default'...
Creating test user...
System check identified no issues (0 silenced).
.................................................
Ran 49 tests in 1.723s

OK
Destroying test database for alias 'default'...
Destroying test user...
Destroying test database tables...
```

## 4. Observaciones

- **Mismo código en tres motores.** Las migraciones y los 49 tests pasaron sin tocar el código: la selección de motor, el campo de estado guardado en `is_active`, las restricciones CHECK y las llaves foráneas con `RESTRICT` se comportan igual.
- **Oracle.** La guía lo registra como no verificado en su entorno (errores `ORA-28000` y `ORA-01017`, de cuenta bloqueada o clave inválida). Aquí quedó verificado de punta a punta, usando un usuario propio en lugar del esquema `SYSTEM`.
- **SQL Server.** Requiere el *ODBC Driver 18 for SQL Server* en el equipo (`odbcinst -q -d` lo lista). El usuario administrador es `SA`.
- **Pruebas aisladas.** Django crea y destruye una base de datos de prueba por corrida; en Oracle crea un usuario temporal, y por eso el rol `DBA`.

## 5. Estado frente al GATE de negocio

| Criterio | Resultado |
|---|---|
| Migraciones aplicadas en el motor | MySQL bien, SQL Server bien, Oracle bien, PostgreSQL  |
| Suite de pruebas completa | MySQL bien, SQL Server bien, Oracle bien, PostgreSQL  |
| Multidialecto (PostgreSQL, MySQL, SQL Server) | los cuatro motores verificados |
| Oracle | verificado |

## 6. Corrida final: guía completa

Suite de **178 tests**, 10-11 de octubre de 2026.

| Motor | Resultado | Duración |
|---|---|---|
| PostgreSQL 17 | bien 178 OK | n/d |
| MySQL 8.0 | bien 178 OK | 47,3 s |
| SQL Server 2022 | bien 178 OK | 45,6 s |
| Oracle XE 21 | bien OK tras el ajuste (primera corrida: 18 errores) |  |

**Incidencia en Oracle.** `NotSupportedError: LIMIT/OFFSET is not supported with select_for_update on this database backend`, por `RefreshToken.objects.select_for_update().filter(...).first()` en `apps/security/auth_views.py` (líneas 131 y 198). Corrección: `next(iter(RefreshToken.objects.select_for_update().filter(...)), None)`. Con ese cambio la suite completa pasó en Oracle.
