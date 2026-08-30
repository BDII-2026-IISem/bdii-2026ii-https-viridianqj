# Motores de bases de datos

## Introducción

Este documento reúne los comandos que uso para levantar, conectarme y administrar mis cuatro motores de base de datos: MySQL, PostgreSQL, MS SQL Server y Oracle Database XE. También dejo las rutas del proyecto y los comandos generales para consultar los contenedores Docker.

Estos comandos corresponden a mi proyecto `BrasaGo - Operación omnicanal de restaurante` y me permiten trabajar de forma organizada con los servicios y los datos persistentes guardados en `ia-lab`.

## Ubicación

Archivos de configuración:

```text
~/ia-lab/services/motores-bd/
```

Datos persistentes:

```text
~/ia-lab/data/
```

Red Docker compartida por los cuatro contenedores: `ia-lab-network`.

```bash
docker network inspect ia-lab-network >/dev/null 2>&1 || docker network create ia-lab-network
docker network ls | grep ia-lab
```

---

## 1. MySQL

### Entrar a la carpeta

```bash
cd ~/ia-lab/services/motores-bd/mysql
```

### Iniciar el motor

```bash
sudo docker compose up -d
```

### Conectarme desde el contenedor

```bash
sudo docker exec -it mysql-server mysql -u root -p
```

El comando pide la contraseña.

### Datos de conexión

```text
Servidor: 172.17.112.120
Puerto: 3306
Base de datos: BrasaGo
Usuario administrador: root
Contraseña de root: 5550101
Usuario remoto: admin
Contraseña de admin: 5550101
```

Comprobar el estado y la conexión:

```bash
sudo docker ps --filter "name=mysql-server" --format "table {{.Names}}\t{{.Ports}}"
sudo docker exec mysql-server mysqladmin ping -h localhost -u root -p5550101
```

Crear un backup:

```bash
sudo docker exec mysql-server mysql -u root -p
SYSTEM mysqldump -u root -p5550101 BrasaGo > /backups/backup_BrasaGo_$(date +%Y%m%d).sql;
ls -lh /mnt/d/academia/bd/backup_BrasaGo_$(date +%Y%m%d).sql
```

---

## 2. PostgreSQL

### Entrar a la carpeta

```bash
cd ~/ia-lab/services/motores-bd/postgres
```

### Iniciar el motor

```bash
sudo docker compose up -d
```

### Conectarme desde el contenedor

```bash
sudo docker exec -it postgres-server psql -U postgres -d BrasaGo
```

### Datos de conexión

```text
Servidor: 172.17.112.120
Puerto: 5432
Base de datos: BrasaGo
Usuario administrador: postgres
Contraseña de postgres: 5550101
Usuario remoto: admin
Contraseña de admin: 5550101
```

Comprobar el estado y la conexión:

```bash
sudo docker ps --filter "name=postgres-server" --format "table {{.Names}}\t{{.Ports}}"
sudo docker exec postgres-server pg_isready -U postgres -d BrasaGo
```

Crear un backup:

```bash
sudo docker exec postgres-server pg_dump -U postgres -d BrasaGo -f /backups/backup_BrasaGo_$(date +%Y%m%d).sql
ls -lh /mnt/d/academia/bd/backup_BrasaGo_$(date +%Y%m%d).sql
```

---

## 3. MS SQL Server

### Entrar a la carpeta

```bash
cd ~/ia-lab/services/motores-bd/mssql
```

### Iniciar el motor

```bash
sudo docker compose up -d
```

### Ver el estado

```bash
sudo docker ps --filter "name=mssql-server" --format "table {{.Names}}\t{{.Ports}}"
```

### Conectarme desde el contenedor

```bash
sudo docker exec -it mssql-server /opt/mssql-tools18/bin/sqlcmd \
-S localhost -U SA -P 'BrasaGo5550101!' -C
```

### Datos de conexión

```text
Servidor: 172.17.112.120
Puerto: 1433
Base de datos: BrasaGo
Usuario administrador: SA
Contraseña de SA: BrasaGo5550101!
Usuario remoto: admin
Contraseña de admin: 5550101
Edición: Developer
```

Crear un backup:

```bash
sudo docker exec mssql-server /opt/mssql-tools18/bin/sqlcmd -S localhost -U SA -P 'BrasaGo5550101!' -C -Q "BACKUP DATABASE [BrasaGo] TO DISK = N'/backups/backup_BrasaGo.bak' WITH INIT"
```

---

## 4. Oracle Database XE

### Entrar a la carpeta

```bash
cd ~/ia-lab/services/motores-bd/oracle
```

### Iniciar el motor

```bash
sudo docker compose up -d
```

### Conectarme desde el contenedor

```bash
sudo docker exec -it oracle-server sqlplus \
'system/5550101@//localhost:1521/BrasaGo'
```

### Datos de conexión

```text
Servidor: 172.17.112.120
Puerto: 1521
Service Name: BrasaGo
Usuario administrador: SYSTEM
Contraseña de SYSTEM: 5550101
Usuario del proyecto: admin
Contraseña de admin: 5550101
```

Para conectarme al esquema del proyecto:

```bash
sudo docker exec -it oracle-server bash
sqlplus 'admin/5550101@//localhost:1521/BrasaGo'
```

Crear un backup con Oracle Data Pump (uso EZCONNECT porque `@BrasaGo` solo, sin la ruta completa, produce el error `ORA-12154`):

```bash
sudo docker exec oracle-server expdp 'system/5550101@//localhost:1521/BrasaGo' directory=DATA_PUMP_DIR dumpfile=backup_BrasaGo.dmp logfile=backup_BrasaGo.log
```

---

## Comandos generales

Ver todos los contenedores:

```bash
sudo docker ps -a
```

Ver registros de un motor:

```bash
sudo docker logs mysql-server --tail 30
sudo docker logs postgres-server --tail 30
sudo docker logs mssql-server --tail 30
sudo docker logs oracle-server --tail 30
```

Detener un motor:

```bash
sudo docker compose down
```

Consultar la IP actual del equipo para conexiones remotas:

```bash
ip a
```

---

## Firma

**Elkin Eliecer Aguas Giraldo**
Estudiante de Ingeniería de Sistemas
Facultad de Ingeniería
Universidad de La Guajira
Rol: estudiante y responsable de la instalación, configuración y verificación de los cuatro motores
