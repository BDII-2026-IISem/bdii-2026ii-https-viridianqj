# Instalación de motores de base de datos — Proyecto BrasaGo

**Guía del docente:** https://tecnogua.com/academic/site/bd/introduccion/
**Proyecto final:** BrasaGo - Operación omnicanal de restaurante (12 tablas: sede, mesa, cliente, reserva, producto, insumo, receta_insumo, pedido, pedido_detalle, pago, domiciliario, entrega)

## 0. Preparación en WSL

Verifico Docker y creo la estructura base:

```bash
sudo systemctl is-active docker
docker compose version
docker --version

mkdir -p ~/ia-lab/services/motores-bd/{mysql,postgres,mssql,oracle}
mkdir -p ~/ia-lab/data/{mysql,postgres,mssql,oracle}
cd ia-lab && tree

docker network inspect ia-lab-network >/dev/null 2>&1 || docker network create ia-lab-network
docker network ls | grep ia-lab
```

Docker estaba instalado y activo. Se crearon las carpetas `services/motores-bd` y `data` para los cuatro motores, y la red compartida `ia-lab-network` (id `6ebf13e6d30a`) para que todos los contenedores se comuniquen entre sí.

**Evidencia:** 

![paso-1](Reguistro%20visual/paso-1.png) ![paso-2](Reguistro%20visual/paso-2.png) ![paso-3](Reguistro%20visual/paso-3.png)

## 1. Configuración común a los cuatro motores

Para cada motor sigo el mismo flujo: `docker-compose.yml` → `.env` → `README.md` → levantar contenedor → conectar y crear las 12 tablas → crear usuario `admin` con acceso remoto → conectar desde DBeaver → backup.

| Motor | Imagen | Contenedor | Puerto | Usuario inicial | Password |
| --- | --- | --- | --- | --- | --- |
| MySQL | `mysql:8.0` | `mysql-server` | 3306 | `root` | `5550101` |
| PostgreSQL | `postgres:17` | `postgres-server` | 5432 | `postgres` | `5550101` |
| MS SQL Server | `mcr.microsoft.com/mssql/server:2022-latest` | `mssql-server` | 1433 | `SA` | `BrasaGo5550101!` |
| Oracle XE | `gvenzl/oracle-xe:21-slim` | `oracle-server` | 1521 | `SYSTEM` | `5550101` |

En todos los motores habilito UFW y permito el puerto correspondiente (`sudo ufw allow <puerto>/tcp && sudo ufw enable && sudo ufw status`); la primera vez tuve que instalar UFW porque no venía en WSL (`sudo dpkg --configure -a && sudo apt update && sudo apt install ufw`).

Datos comunes para conectarme por DBeaver: host `172.17.112.120` (IP de `eth0`, obtenida con `ip a`), base de datos `BrasaGo`, usuario `admin`, password `5550101` (`BrasaGo5550101!` solo para `SA` en SQL Server).

Todos los backups se guardan en `/mnt/d/academia/bd`, mapeada dentro de cada contenedor como `/backups`.

---

## 2. MySQL

**`docker-compose.yml`:**
```yaml
services:
  mysql:
    image: mysql:8.0
    container_name: mysql-server
    restart: unless-stopped
    env_file: [.env]
    ports: ["3306:3306"]
    volumes:
      - ../../../data/mysql:/var/lib/mysql
      - /mnt/d/academia/bd:/backups
    command: >
      --character-set-server=utf8mb4
      --collation-server=utf8mb4_unicode_ci
      --bind-address=0.0.0.0
    networks: [ia-lab-network]
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
networks:
  ia-lab-network: { external: true }
```

**`.env`:**
```env
TZ=America/Bogota
MYSQL_ROOT_PASSWORD=5550101
MYSQL_DATABASE=BrasaGo
```

Levanto el contenedor (`cd .../mysql && sudo docker compose up -d`) y me conecto localmente:

```bash
sudo docker exec -it mysql-server mysql -u root -p
```

```sql
USE BrasaGo;

CREATE TABLE sede (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE mesa (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sede_id BIGINT NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    descripcion VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_mesa_sede FOREIGN KEY (sede_id) REFERENCES sede(id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE cliente (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    tipo_documento VARCHAR(20) NOT NULL,
    numero_documento VARCHAR(30) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    telefono VARCHAR(30),
    email VARCHAR(150),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_cliente_documento UNIQUE (tipo_documento, numero_documento)
) ENGINE=InnoDB;

CREATE TABLE reserva (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    cliente_id BIGINT NOT NULL,
    mesa_id BIGINT NOT NULL,
    fecha_inicio DATETIME NOT NULL,
    fecha_fin DATETIME,
    estado VARCHAR(30) NOT NULL DEFAULT 'PENDIENTE',
    observaciones VARCHAR(500),
    CONSTRAINT fk_reserva_cliente FOREIGN KEY (cliente_id) REFERENCES cliente(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_reserva_mesa FOREIGN KEY (mesa_id) REFERENCES mesa(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT ck_reserva_fecha CHECK (fecha_fin IS NULL OR fecha_fin > fecha_inicio)
) ENGINE=InnoDB;

CREATE TABLE producto (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sku VARCHAR(50) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    descripcion VARCHAR(500),
    precio DECIMAL(12,2) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_producto_sku UNIQUE (sku),
    CONSTRAINT ck_producto_precio CHECK (precio >= 0)
) ENGINE=InnoDB;

CREATE TABLE insumo (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    unidad_medida VARCHAR(30) NOT NULL,
    stock_minimo DECIMAL(12,3) NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_insumo_codigo UNIQUE (codigo),
    CONSTRAINT ck_insumo_stock_minimo CHECK (stock_minimo >= 0)
) ENGINE=InnoDB;

CREATE TABLE receta_insumo (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    principal_id BIGINT NOT NULL,
    relacionado_id BIGINT NOT NULL,
    datos_relacion JSON,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_receta_producto FOREIGN KEY (principal_id) REFERENCES producto(id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_receta_insumo FOREIGN KEY (relacionado_id) REFERENCES insumo(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT uq_receta_producto_insumo UNIQUE (principal_id, relacionado_id)
) ENGINE=InnoDB;

CREATE TABLE pedido (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    cliente_id BIGINT,
    origen_id BIGINT,
    canal VARCHAR(30) NOT NULL,
    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    subtotal DECIMAL(12,2) NOT NULL DEFAULT 0,
    total DECIMAL(12,2) NOT NULL DEFAULT 0,
    estado VARCHAR(30) NOT NULL DEFAULT 'PENDIENTE',
    CONSTRAINT fk_pedido_cliente FOREIGN KEY (cliente_id) REFERENCES cliente(id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_pedido_sede FOREIGN KEY (origen_id) REFERENCES sede(id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT ck_pedido_subtotal CHECK (subtotal >= 0),
    CONSTRAINT ck_pedido_total CHECK (total >= 0)
) ENGINE=InnoDB;

CREATE TABLE pedido_detalle (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    pedido_id BIGINT NOT NULL,
    producto_id BIGINT NOT NULL,
    cantidad DECIMAL(12,2) NOT NULL,
    valor_unitario DECIMAL(12,2) NOT NULL,
    total DECIMAL(12,2) NOT NULL,
    observaciones VARCHAR(500),
    CONSTRAINT fk_detalle_pedido FOREIGN KEY (pedido_id) REFERENCES pedido(id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_detalle_producto FOREIGN KEY (producto_id) REFERENCES producto(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT ck_detalle_cantidad CHECK (cantidad > 0),
    CONSTRAINT ck_detalle_valor CHECK (valor_unitario >= 0),
    CONSTRAINT ck_detalle_total CHECK (total >= 0)
) ENGINE=InnoDB;

CREATE TABLE pago (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    referencia_tipo VARCHAR(30) NOT NULL,
    referencia_id BIGINT NOT NULL,
    metodo VARCHAR(30) NOT NULL,
    monto DECIMAL(12,2) NOT NULL,
    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(30) NOT NULL DEFAULT 'PENDIENTE',
    CONSTRAINT ck_pago_monto CHECK (monto > 0)
) ENGINE=InnoDB;

CREATE TABLE domiciliario (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    descripcion VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE entrega (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    referencia_id BIGINT NOT NULL,
    domiciliario_id BIGINT NOT NULL,
    fecha_inicio DATETIME,
    fecha_fin DATETIME,
    total DECIMAL(12,2) NOT NULL DEFAULT 0,
    estado VARCHAR(30) NOT NULL DEFAULT 'PENDIENTE',
    observaciones VARCHAR(500),
    CONSTRAINT fk_entrega_pedido FOREIGN KEY (referencia_id) REFERENCES pedido(id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_entrega_domiciliario FOREIGN KEY (domiciliario_id) REFERENCES domiciliario(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT ck_entrega_total CHECK (total >= 0),
    CONSTRAINT ck_entrega_fechas CHECK (fecha_fin IS NULL OR fecha_inicio IS NULL OR fecha_fin >= fecha_inicio),
    CONSTRAINT uq_entrega_pedido UNIQUE (referencia_id)
) ENGINE=InnoDB;

SHOW TABLES;
```

Creo el usuario remoto y verifico la conexión:

```sql
CREATE USER 'admin'@'%' IDENTIFIED BY '5550101';
GRANT ALL PRIVILEGES ON BrasaGo.* TO 'admin'@'%';
FLUSH PRIVILEGES;
-- MySQL 8 usa caching_sha2_password por defecto; DBeaver requiere mysql_native_password:
ALTER USER 'admin'@'%' IDENTIFIED WITH mysql_native_password BY '5550101';
FLUSH PRIVILEGES;
```

**Backup** — la redirección `>` desde WSL dio `Permission denied`, así que genero el archivo dentro del contenedor, en la carpeta montada `/backups`:

```sql
SYSTEM mysqldump -u root -p5550101 BrasaGo > /backups/backup_BrasaGo_$(date +%Y%m%d).sql;
```

**Evidencia:**

![Evidencia de la configuración de MySQL](Reguistro%20visual/paso-4.png)
*docker-compose.yml de MySQL*

![Evidencia de la instalación de UFW](Reguistro%20visual/paso-5.png)
*Instalación de UFW (no venía por defecto en WSL)*

![Evidencia de la configuración de UFW](Reguistro%20visual/paso-6.png)
*Puerto 3306 permitido en UFW*

![Evidencia de la creación del archivo .env](Reguistro%20visual/paso-7.png)
*Archivo .env de MySQL*

![Evidencia de la creación de README.md](Reguistro%20visual/paso-8.png)
*README.md de MySQL*

![Evidencia al levantar MySQL](Reguistro%20visual/paso-9.png)
*Contenedor mysql-server corriendo*

![Proyecto final del semestre](Reguistro%20visual/BrasaGo.png)
*Modelo del proyecto final BrasaGo*

![Evidencia de la creación de las tablas](Reguistro%20visual/paso-10.png)
*Creación de las 12 tablas*

![Evidencia de la verificación con SHOW TABLES](Reguistro%20visual/paso-11.png)
*Verificación con SHOW TABLES*

![Evidencia de la creación del usuario remoto](Reguistro%20visual/paso-12.png)
*Usuario admin con acceso remoto*

![Evidencia de los datos para la conexión remota](Reguistro%20visual/paso-13.png)
*Datos de conexión remota (IP, puerto)*

![Evidencia de los datos para la conexión remota](Reguistro%20visual/paso-14.png)
*Cambio de plugin de autenticación del usuario admin*

![Evidencia de la configuración de conexión en DBeaver](Reguistro%20visual/Dbeaver_Mysql-1.png)
*Configuración de la conexión en DBeaver*

![Evidencia de la conexión exitosa en DBeaver](Reguistro%20visual/Dbeaver_Mysql.png)
*Conexión exitosa desde DBeaver*

![Evidencia del error de permisos al crear el backup](Reguistro%20visual/Paso-15.png)
*Error "Permission denied" en el primer intento de backup*

![Evidencia del backup creado correctamente](Reguistro%20visual/paso-16.png)
*Backup creado correctamente*

---

## 3. PostgreSQL

**`docker-compose.yml`:**
```yaml
services:
  postgres:
    image: postgres:17
    container_name: postgres-server
    restart: unless-stopped
    env_file: [.env]
    ports: ["5432:5432"]
    volumes:
      - ../../../data/postgres:/var/lib/postgresql/data
      - /mnt/d/academia/bd:/backups
    command: ["postgres", "-c", "listen_addresses=*"]
    networks: [ia-lab-network]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 20s
networks:
  ia-lab-network: { external: true }
```

**`.env`:**
```env
TZ=America/Bogota
POSTGRES_USER=postgres
POSTGRES_PASSWORD=5550101
POSTGRES_DB=BrasaGo
```

Conexión local y creación de tablas (mismo modelo, sintaxis PostgreSQL: `BIGSERIAL`, `JSONB`, sin `ENGINE`):

```bash
sudo docker exec -it postgres-server psql -U postgres -d BrasaGo
```

```sql
CREATE TABLE sede (
    id              BIGSERIAL PRIMARY KEY,
    nombre          VARCHAR(100) NOT NULL,
    descripcion     VARCHAR(255),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE mesa (
    id              BIGSERIAL PRIMARY KEY,
    sede_id         BIGINT NOT NULL,
    nombre          VARCHAR(50) NOT NULL,
    descripcion     VARCHAR(255),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_mesa_sede FOREIGN KEY (sede_id) REFERENCES sede(id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE cliente (
    id              BIGSERIAL PRIMARY KEY,
    tipo_documento  VARCHAR(20) NOT NULL,
    numero_documento VARCHAR(30) NOT NULL,
    nombre          VARCHAR(150) NOT NULL,
    telefono        VARCHAR(30),
    email           VARCHAR(150),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_cliente_documento UNIQUE (tipo_documento, numero_documento)
);

CREATE TABLE reserva (
    id              BIGSERIAL PRIMARY KEY,
    cliente_id      BIGINT NOT NULL,
    mesa_id         BIGINT NOT NULL,
    fecha_inicio    TIMESTAMP NOT NULL,
    fecha_fin       TIMESTAMP,
    estado          VARCHAR(30) NOT NULL DEFAULT 'PENDIENTE',
    observaciones   VARCHAR(500),
    CONSTRAINT fk_reserva_cliente FOREIGN KEY (cliente_id) REFERENCES cliente(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_reserva_mesa FOREIGN KEY (mesa_id) REFERENCES mesa(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT ck_reserva_fecha CHECK (fecha_fin IS NULL OR fecha_fin > fecha_inicio)
);

CREATE TABLE producto (
    id              BIGSERIAL PRIMARY KEY,
    sku             VARCHAR(50) NOT NULL,
    nombre          VARCHAR(150) NOT NULL,
    descripcion     VARCHAR(500),
    precio          NUMERIC(12,2) NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_producto_sku UNIQUE (sku),
    CONSTRAINT ck_producto_precio CHECK (precio >= 0)
);

CREATE TABLE insumo (
    id              BIGSERIAL PRIMARY KEY,
    codigo          VARCHAR(50) NOT NULL,
    nombre          VARCHAR(150) NOT NULL,
    unidad_medida   VARCHAR(30) NOT NULL,
    stock_minimo    NUMERIC(12,3) NOT NULL DEFAULT 0,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_insumo_codigo UNIQUE (codigo),
    CONSTRAINT ck_insumo_stock_minimo CHECK (stock_minimo >= 0)
);

CREATE TABLE receta_insumo (
    id              BIGSERIAL PRIMARY KEY,
    principal_id    BIGINT NOT NULL,
    relacionado_id  BIGINT NOT NULL,
    datos_relacion  JSONB,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_receta_producto FOREIGN KEY (principal_id) REFERENCES producto(id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_receta_insumo FOREIGN KEY (relacionado_id) REFERENCES insumo(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT uq_receta_producto_insumo UNIQUE (principal_id, relacionado_id)
);

CREATE TABLE pedido (
    id              BIGSERIAL PRIMARY KEY,
    cliente_id      BIGINT,
    origen_id       BIGINT,
    canal           VARCHAR(30) NOT NULL,
    fecha           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    subtotal        NUMERIC(12,2) NOT NULL DEFAULT 0,
    total           NUMERIC(12,2) NOT NULL DEFAULT 0,
    estado          VARCHAR(30) NOT NULL DEFAULT 'PENDIENTE',
    CONSTRAINT fk_pedido_cliente FOREIGN KEY (cliente_id) REFERENCES cliente(id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_pedido_sede FOREIGN KEY (origen_id) REFERENCES sede(id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT ck_pedido_subtotal CHECK (subtotal >= 0),
    CONSTRAINT ck_pedido_total CHECK (total >= 0)
);

CREATE TABLE pedido_detalle (
    id              BIGSERIAL PRIMARY KEY,
    pedido_id       BIGINT NOT NULL,
    producto_id     BIGINT NOT NULL,
    cantidad        NUMERIC(12,2) NOT NULL,
    valor_unitario  NUMERIC(12,2) NOT NULL,
    total           NUMERIC(12,2) NOT NULL,
    observaciones   VARCHAR(500),
    CONSTRAINT fk_detalle_pedido FOREIGN KEY (pedido_id) REFERENCES pedido(id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_detalle_producto FOREIGN KEY (producto_id) REFERENCES producto(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT ck_detalle_cantidad CHECK (cantidad > 0),
    CONSTRAINT ck_detalle_valor CHECK (valor_unitario >= 0),
    CONSTRAINT ck_detalle_total CHECK (total >= 0)
);

CREATE TABLE pago (
    id              BIGSERIAL PRIMARY KEY,
    referencia_tipo VARCHAR(30) NOT NULL,
    referencia_id   BIGINT NOT NULL,
    metodo          VARCHAR(30) NOT NULL,
    monto           NUMERIC(12,2) NOT NULL,
    fecha           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado          VARCHAR(30) NOT NULL DEFAULT 'PENDIENTE',
    CONSTRAINT ck_pago_monto CHECK (monto > 0)
);

CREATE TABLE domiciliario (
    id              BIGSERIAL PRIMARY KEY,
    nombre          VARCHAR(150) NOT NULL,
    descripcion     VARCHAR(255),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE entrega (
    id              BIGSERIAL PRIMARY KEY,
    referencia_id   BIGINT NOT NULL,
    domiciliario_id BIGINT NOT NULL,
    fecha_inicio    TIMESTAMP,
    fecha_fin       TIMESTAMP,
    total           NUMERIC(12,2) NOT NULL DEFAULT 0,
    estado          VARCHAR(30) NOT NULL DEFAULT 'PENDIENTE',
    observaciones   VARCHAR(500),
    CONSTRAINT fk_entrega_pedido FOREIGN KEY (referencia_id) REFERENCES pedido(id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_entrega_domiciliario FOREIGN KEY (domiciliario_id) REFERENCES domiciliario(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT ck_entrega_total CHECK (total >= 0),
    CONSTRAINT ck_entrega_fechas CHECK (fecha_fin IS NULL OR fecha_inicio IS NULL OR fecha_fin >= fecha_inicio),
    CONSTRAINT uq_entrega_pedido UNIQUE (referencia_id)
);
```

Usuario remoto (PostgreSQL usa superusuario en vez de permisos por base de datos):

```sql
CREATE USER admin WITH PASSWORD '5550101';
ALTER USER admin WITH SUPERUSER;
```

**Backup:**
```bash
sudo docker exec postgres-server pg_dump -U postgres -d BrasaGo -f /backups/backup_BrasaGo_$(date +%Y%m%d).sql
```

**Evidencia:**

![Evidencia de la creación de docker-compose de PostgreSQL](Reguistro%20visual/paso-17.png)
*docker-compose.yml de PostgreSQL*

![Evidencia de la verificación del archivo .env de PostgreSQL](Reguistro%20visual/paso-18.png)
*Archivo .env de PostgreSQL*

![Evidencia de la creación del README de PostgreSQL](Reguistro%20visual/paso-19.png)
*README.md de PostgreSQL*

![Evidencia del error al levantar PostgreSQL](Reguistro%20visual/paso-20.png)
*Contenedor postgres-server corriendo*

![Proyecto final del semestre](Reguistro%20visual/BrasaGo.png)
*Modelo del proyecto final BrasaGo*

![Evidencia de la creación de tablas en PostgreSQL](Reguistro%20visual/paso-21.png)
*Creación de las 12 tablas*

![Evidencia de la creación del usuario admin en PostgreSQL](Reguistro%20visual/paso-22.png)
*Usuario admin con permisos de superusuario*

![Evidencia de la configuración para la conexión remota a PostgreSQL](Reguistro%20visual/paso-24.png)
*Datos de conexión remota (IP, puerto)*

![Evidencia de la conexión a PostgreSQL desde DBeaver](Reguistro%20visual/DBeaver_Post.png)
*Conexión exitosa desde DBeaver*

![Evidencia del backup de BrasaGo y la consulta del archivo .env](Reguistro%20visual/paso-23.png)
*Backup creado y verificación del .env*

---

## 4. MS SQL Server

**`docker-compose.yml`:**
```yaml
services:
  mssql:
    image: mcr.microsoft.com/mssql/server:2022-latest
    container_name: mssql-server
    restart: unless-stopped
    user: root
    env_file: [.env]
    ports: ["0.0.0.0:1433:1433"]
    volumes:
      - ../../../data/mssql:/var/opt/mssql
      - /mnt/d/academia/bd:/backups
    networks: [ia-lab-network]
    healthcheck:
      test: ["CMD-SHELL", "/opt/mssql-tools18/bin/sqlcmd -S localhost -U SA -P $$MSSQL_SA_PASSWORD -C -Q 'SELECT 1' || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 10
      start_period: 40s
networks:
  ia-lab-network: { external: true }
```

**`.env`:**
```env
TZ=America/Bogota
ACCEPT_EULA=Y
MSSQL_SA_PASSWORD=BrasaGo5550101!
MSSQL_PID=Developer
```
`MSSQL_PID` es la edición (`Developer`), no un usuario. SQL Server exige mayúsculas, minúsculas, números y símbolos en la contraseña de `SA`; por eso uso `BrasaGo5550101!` en vez de `5550101` sola.

**Instalación de `mssql-tools18` en WSL** (Ubuntu 24.04):
```bash
sudo apt update && sudo apt install -y curl ca-certificates gnupg
sudo rm -f /etc/apt/sources.list.d/mssql-release.list /etc/apt/sources.list.d/microsoft-prod.list
cd /tmp && curl -sSL -O https://packages.microsoft.com/config/ubuntu/24.04/packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
sudo apt update
sudo ACCEPT_EULA=Y apt install -y mssql-tools18 unixodbc-dev
echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc && source ~/.bashrc
which sqlcmd   # /opt/mssql-tools18/bin/sqlcmd
```
La primera prueba de conexión (`sqlcmd -S localhost,1433 -C`) falló con un error SSPI/Kerberos por no indicar usuario y contraseña; se resolvió especificando `-U sa -P 'BrasaGo5550101!'`.

Levanto el contenedor, creo la base y las tablas desde un archivo `.sql` (evita errores al pegar bloques largos en `sqlcmd`):

```bash
sudo docker exec -it mssql-server /opt/mssql-tools18/bin/sqlcmd -S localhost -U SA -P 'BrasaGo5550101!' -C -d master
```
```sql
CREATE DATABASE BrasaGo;
GO
```
```bash
nano ~/BrasaGo.sql   # pego el script de abajo, cada instrucción termina en GO
sudo docker exec -i mssql-server /opt/mssql-tools18/bin/sqlcmd -S localhost -U SA -P 'BrasaGo5550101!' -C -d BrasaGo < ~/BrasaGo.sql
```

```sql
CREATE TABLE sede (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255),
    direccion VARCHAR(255),
    is_active BIT NOT NULL DEFAULT 1,
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME()
);
GO

CREATE TABLE mesa (
    id INT IDENTITY(1,1) PRIMARY KEY,
    sede_id INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255),
    is_active BIT NOT NULL DEFAULT 1,
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT FK_mesa_sede FOREIGN KEY (sede_id) REFERENCES sede(id)
);
GO

CREATE TABLE cliente (
    id INT IDENTITY(1,1) PRIMARY KEY,
    tipo_documento VARCHAR(30) NOT NULL,
    numero_documento VARCHAR(50) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(30),
    email VARCHAR(150),
    is_active BIT NOT NULL DEFAULT 1,
    CONSTRAINT UQ_cliente_numero_documento UNIQUE (numero_documento)
);
GO

CREATE TABLE reserva (
    id INT IDENTITY(1,1) PRIMARY KEY,
    cliente_id INT NOT NULL,
    mesa_id INT NOT NULL,
    fecha_inicio DATETIME2 NOT NULL,
    fecha_fin DATETIME2,
    estado VARCHAR(30) NOT NULL,
    observaciones VARCHAR(MAX),
    CONSTRAINT FK_reserva_cliente FOREIGN KEY (cliente_id) REFERENCES cliente(id),
    CONSTRAINT FK_reserva_mesa FOREIGN KEY (mesa_id) REFERENCES mesa(id)
);
GO

CREATE TABLE producto (
    id INT IDENTITY(1,1) PRIMARY KEY,
    sku VARCHAR(50) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255),
    precio DECIMAL(10,2) NOT NULL,
    is_active BIT NOT NULL DEFAULT 1,
    CONSTRAINT UQ_producto_sku UNIQUE (sku)
);
GO

CREATE TABLE insumo (
    id INT IDENTITY(1,1) PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    unidad_medida VARCHAR(30) NOT NULL,
    stock_minimo DECIMAL(10,2) NOT NULL DEFAULT 0,
    is_active BIT NOT NULL DEFAULT 1,
    CONSTRAINT UQ_insumo_codigo UNIQUE (codigo)
);
GO

CREATE TABLE receta_insumo (
    id INT IDENTITY(1,1) PRIMARY KEY,
    principal_id INT NOT NULL,
    relacionado_id INT NOT NULL,
    datos_relacion VARCHAR(255),
    is_active BIT NOT NULL DEFAULT 1,
    CONSTRAINT FK_receta_insumo_producto FOREIGN KEY (principal_id) REFERENCES producto(id),
    CONSTRAINT FK_receta_insumo_insumo FOREIGN KEY (relacionado_id) REFERENCES insumo(id)
);
GO

CREATE TABLE pedido (
    id INT IDENTITY(1,1) PRIMARY KEY,
    sede_id INT NOT NULL,
    cliente_id INT,
    mesa_id INT,
    canal VARCHAR(30) NOT NULL,
    fecha DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    subtotal DECIMAL(10,2) NOT NULL DEFAULT 0,
    total DECIMAL(10,2) NOT NULL DEFAULT 0,
    estado VARCHAR(30) NOT NULL,
    CONSTRAINT FK_pedido_sede FOREIGN KEY (sede_id) REFERENCES sede(id),
    CONSTRAINT FK_pedido_cliente FOREIGN KEY (cliente_id) REFERENCES cliente(id),
    CONSTRAINT FK_pedido_mesa FOREIGN KEY (mesa_id) REFERENCES mesa(id)
);
GO

CREATE TABLE pedido_detalle (
    id INT IDENTITY(1,1) PRIMARY KEY,
    pedido_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT NOT NULL,
    valor_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    observaciones VARCHAR(MAX),
    CONSTRAINT FK_pedido_detalle_pedido FOREIGN KEY (pedido_id) REFERENCES pedido(id),
    CONSTRAINT FK_pedido_detalle_producto FOREIGN KEY (producto_id) REFERENCES producto(id)
);
GO

CREATE TABLE pago (
    id INT IDENTITY(1,1) PRIMARY KEY,
    pedido_id INT NOT NULL,
    metodo VARCHAR(50) NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    fecha DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    estado VARCHAR(30) NOT NULL,
    CONSTRAINT FK_pago_pedido FOREIGN KEY (pedido_id) REFERENCES pedido(id)
);
GO

CREATE TABLE domiciliario (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(30),
    is_active BIT NOT NULL DEFAULT 1,
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME()
);
GO

CREATE TABLE entrega (
    id INT IDENTITY(1,1) PRIMARY KEY,
    pedido_id INT NOT NULL,
    domiciliario_id INT NOT NULL,
    fecha_inicio DATETIME2,
    fecha_fin DATETIME2,
    estado VARCHAR(30) NOT NULL,
    observaciones VARCHAR(MAX),
    CONSTRAINT FK_entrega_pedido FOREIGN KEY (pedido_id) REFERENCES pedido(id),
    CONSTRAINT FK_entrega_domiciliario FOREIGN KEY (domiciliario_id) REFERENCES domiciliario(id),
    CONSTRAINT UQ_entrega_pedido UNIQUE (pedido_id)
);
GO
```

Verifico con `SELECT name FROM sys.tables;` → 12 tablas creadas.

Usuario remoto con rol `sysadmin` (`CHECK_POLICY = OFF` permite una contraseña simple solo para este login; `SA` sigue exigiendo la contraseña compleja):

```sql
CREATE LOGIN admin WITH PASSWORD = '5550101', CHECK_POLICY = OFF;
GO
ALTER SERVER ROLE sysadmin ADD MEMBER admin;
GO
ALTER LOGIN admin ENABLE;
GO
```

**Backup:**
```bash
sudo docker exec mssql-server /opt/mssql-tools18/bin/sqlcmd -S localhost -U SA -P 'BrasaGo5550101!' -C -Q "BACKUP DATABASE [BrasaGo] TO DISK = N'/backups/backup_BrasaGo.bak' WITH INIT"
```

**Evidencia:**

![Evidencia de la configuración de MS SQL Server](Reguistro%20visual/paso-25.png)
*docker-compose.yml de MS SQL Server*

![Evidencia de la configuración del archivo .env de MS SQL Server](Reguistro%20visual/paso-26.png)
*Archivo .env de MS SQL Server*

![Evidencia de la creación del README de MS SQL Server](Reguistro%20visual/paso-27.png)
*README.md de MS SQL Server*

![Evidencia del levantamiento de MS SQL Server](Reguistro%20visual/paso-28.png)
*Contenedor mssql-server corriendo*

![Evidencia de la instalación de mssql-tools en WSL](Reguistro%20visual/paso-29.png)
*Instalación de mssql-tools18 en WSL*

![Evidencia adicional de la instalación de mssql-tools](Reguistro%20visual/paso-30.png)
*Instalación de mssql-tools18 (continuación)*

![Evidencia de la verificación de sqlcmd](Reguistro%20visual/paso-31.png)
*Verificación de sqlcmd instalado*

![Evidencia del error ssl](Reguistro%20visual/paso-32.png)
*Error SSPI/Kerberos y conexión corregida con usuario y contraseña*

![Evidencia de la creación de las tablas de BrasaGo en SQL Server](Reguistro%20visual/paso-33.png)
*Creación de las 12 tablas*

![Evidencia del nuevo intento de configuración del usuario admin](Reguistro%20visual/paso-34.png)
*Usuario admin con rol sysadmin*

![Evidencia de las comprobaciones previas para la conexión remota](Reguistro%20visual/paso-35.png)
*Comprobaciones previas a la conexión remota*

![Evidencia de la conexión remota a SQL Server desde DBeaver](Reguistro%20visual/DBeaver-sql.png)
*Configuración de la conexión en DBeaver*

![Evidencia de la conexión exitosa a SQL Server desde DBeaver](Reguistro%20visual/DBeaver-sql2.png)
*Conexión exitosa desde DBeaver*

![Evidencia del backup de BrasaGo en SQL Server](Reguistro%20visual/paso-36.png)
*Backup creado correctamente*

---

## 5. Oracle XE

**`docker-compose.yml`:**
```yaml
services:
  oracle:
    image: gvenzl/oracle-xe:21-slim
    container_name: oracle-server
    restart: unless-stopped
    env_file: [.env]
    ports: ["0.0.0.0:1521:1521"]
    volumes:
      - ../../../data/oracle:/opt/oracle/oradata
      - /mnt/d/academia/bd:/backups
    networks: [ia-lab-network]
    healthcheck:
      test: ["CMD", "healthcheck.sh"]
      interval: 10s
      timeout: 5s
      retries: 10
      start_period: 120s
networks:
  ia-lab-network: { external: true }
```
El listener de `gvenzl/oracle-xe` ya acepta conexiones remotas por defecto (equivalente a `--bind-address=0.0.0.0` en MySQL); no uso `command:` porque reemplazaría el entrypoint de la imagen.

**`.env`:**
```env
TZ=America/Bogota
ORACLE_PASSWORD=5550101
ORACLE_DATABASE=BrasaGo
```
`ORACLE_DATABASE` es el PDB (pluggable database), no un usuario; el administrador es `SYSTEM`.

**Incidencia al levantar el contenedor:** quedó en `Restarting` con `Cannot create folder` en `/opt/oracle/oradata/XE/XEPDB1`, por permisos de la carpeta montada. Solución:
```bash
sudo docker compose down
sudo chown -R 54321:54321 ~/ia-lab/data/oracle
sudo docker compose up -d
```
Tras el cambio de propietario, el contenedor quedó `Up (healthy)` y el PDB `BrasaGo` abrió en modo lectura y escritura.

Conexión local y creación de tablas (sintaxis PL/SQL: `NUMBER`, `VARCHAR2`, `GENERATED BY DEFAULT AS IDENTITY`):

```bash
sudo docker exec -it oracle-server bash
sqlplus 'system/5550101@//localhost:1521/BrasaGo'
```
```sql
CONN admin/5550101@//localhost:1521/BrasaGo
```

```sql
CREATE TABLE sede (
  id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  nombre VARCHAR2(100) NOT NULL,
  descripcion VARCHAR2(255),
  is_active NUMBER(1) DEFAULT 1 NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE mesa (
  id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  sede_id NUMBER NOT NULL,
  nombre VARCHAR2(100) NOT NULL,
  descripcion VARCHAR2(255),
  is_active NUMBER(1) DEFAULT 1 NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_mesa_sede FOREIGN KEY (sede_id) REFERENCES sede(id)
);

CREATE TABLE cliente (
  id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  tipo_documento VARCHAR2(30) NOT NULL,
  numero_documento VARCHAR2(50) NOT NULL,
  nombre VARCHAR2(100) NOT NULL,
  telefono VARCHAR2(30),
  email VARCHAR2(150),
  is_active NUMBER(1) DEFAULT 1 NOT NULL,
  CONSTRAINT uq_cliente_numero_documento UNIQUE (numero_documento)
);

CREATE TABLE reserva (
  id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  cliente_id NUMBER NOT NULL,
  mesa_id NUMBER NOT NULL,
  fecha_inicio TIMESTAMP NOT NULL,
  fecha_fin TIMESTAMP,
  estado VARCHAR2(30) NOT NULL,
  observaciones VARCHAR2(1000),
  CONSTRAINT fk_reserva_cliente FOREIGN KEY (cliente_id) REFERENCES cliente(id),
  CONSTRAINT fk_reserva_mesa FOREIGN KEY (mesa_id) REFERENCES mesa(id)
);

CREATE TABLE producto (
  id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  sku VARCHAR2(50) NOT NULL,
  nombre VARCHAR2(100) NOT NULL,
  descripcion VARCHAR2(255),
  precio NUMBER(10,2) NOT NULL,
  is_active NUMBER(1) DEFAULT 1 NOT NULL,
  CONSTRAINT uq_producto_sku UNIQUE (sku)
);

CREATE TABLE insumo (
  id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  codigo VARCHAR2(50) NOT NULL,
  nombre VARCHAR2(100) NOT NULL,
  unidad_medida VARCHAR2(30) NOT NULL,
  stock_minimo NUMBER(10,2) NOT NULL,
  is_active NUMBER(1) DEFAULT 1 NOT NULL,
  CONSTRAINT uq_insumo_codigo UNIQUE (codigo)
);

CREATE TABLE receta_insumo (
  id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  principal_id NUMBER NOT NULL,
  relacionado_id NUMBER NOT NULL,
  datos_relacion VARCHAR2(255),
  is_active NUMBER(1) DEFAULT 1 NOT NULL,
  CONSTRAINT fk_receta_producto FOREIGN KEY (principal_id) REFERENCES producto(id),
  CONSTRAINT fk_receta_insumo FOREIGN KEY (relacionado_id) REFERENCES insumo(id)
);

CREATE TABLE pedido (
  id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  cliente_id NUMBER,
  sede_id NUMBER NOT NULL,
  canal VARCHAR2(30) NOT NULL,
  fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  subtotal NUMBER(10,2) NOT NULL,
  total NUMBER(10,2) NOT NULL,
  estado VARCHAR2(30) NOT NULL,
  CONSTRAINT fk_pedido_cliente FOREIGN KEY (cliente_id) REFERENCES cliente(id),
  CONSTRAINT fk_pedido_sede FOREIGN KEY (sede_id) REFERENCES sede(id)
);

CREATE TABLE pedido_detalle (
  id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  pedido_id NUMBER NOT NULL,
  producto_id NUMBER NOT NULL,
  cantidad NUMBER NOT NULL,
  valor_unitario NUMBER(10,2) NOT NULL,
  subtotal NUMBER(10,2) NOT NULL,
  total NUMBER(10,2) NOT NULL,
  observaciones VARCHAR2(1000),
  CONSTRAINT fk_detalle_pedido FOREIGN KEY (pedido_id) REFERENCES pedido(id),
  CONSTRAINT fk_detalle_producto FOREIGN KEY (producto_id) REFERENCES producto(id)
);

CREATE TABLE pago (
  id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  referencia_tipo VARCHAR2(50) NOT NULL,
  referencia_id NUMBER NOT NULL,
  metodo VARCHAR2(50) NOT NULL,
  monto NUMBER(10,2) NOT NULL,
  fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  estado VARCHAR2(30) NOT NULL
);

CREATE TABLE domiciliario (
  id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  nombre VARCHAR2(100) NOT NULL,
  descripcion VARCHAR2(255),
  is_active NUMBER(1) DEFAULT 1 NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE entrega (
  id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  referencia_id NUMBER NOT NULL,
  domiciliario_id NUMBER NOT NULL,
  fecha_inicio TIMESTAMP,
  fecha_fin TIMESTAMP,
  estado VARCHAR2(30) NOT NULL,
  observaciones VARCHAR2(1000),
  CONSTRAINT fk_entrega_pedido FOREIGN KEY (referencia_id) REFERENCES pedido(id),
  CONSTRAINT fk_entrega_domiciliario FOREIGN KEY (domiciliario_id) REFERENCES domiciliario(id),
  CONSTRAINT uq_entrega_pedido UNIQUE (referencia_id)
);
```

Verifico con `SELECT owner, table_name FROM all_tables WHERE owner = 'ADMIN' ORDER BY table_name;` → 12 tablas.

En DBeaver uso **Service Name** (`BrasaGo`) en lugar de **Database**, rol **Normal**, usuario `admin`.

**Backup** (con Data Pump, usuario `SYSTEM`) — el primer intento falló con `ORA-12154` porque `@BrasaGo` se tomó como alias TNS; se resolvió con EZCONNECT:
```bash
sudo docker exec oracle-server expdp 'system/5550101@//localhost:1521/BrasaGo' directory=DATA_PUMP_DIR dumpfile=backup_BrasaGo.dmp logfile=backup_BrasaGo.log
```

**Evidencia:**

![Evidencia de la creación y configuración de Oracle XE](Reguistro%20visual/paso-37.png)
*docker-compose.yml de Oracle XE*

![Evidencia de la configuración del archivo .env de Oracle XE](Reguistro%20visual/paso-38.png)
*Archivo .env de Oracle XE*

![Evidencia de la creación y verificación del README de Oracle XE](Reguistro%20visual/paso-39.png)
*README.md de Oracle XE*

![Evidencia del error al levantar Oracle XE](Reguistro%20visual/paso-40.png)
*Error "Cannot create folder" al levantar el contenedor*

![Evidencia de Oracle XE funcionando correctamente](Reguistro%20visual/paso-41.png)
*Contenedor corriendo tras corregir permisos*

![Evidencia de la conexión y creación del usuario admin en Oracle XE](Reguistro%20visual/paso-42.png)
*Conexión al esquema admin (sin tablas todavía)*

![Modelo del proyecto final BrasaGo](Reguistro%20visual/BrasaGo.png)
*Modelo del proyecto final BrasaGo*

![Evidencia de la creación de las tablas de BrasaGo en Oracle XE](Reguistro%20visual/paso-43.png)
*Creación de las 12 tablas*

![Evidencia de la verificación previa para la conexión remota a Oracle XE](Reguistro%20visual/paso-44.png)
*Comprobaciones previas a la conexión remota*

![Evidencia de la prueba de conexión en DBeaver](Reguistro%20visual/DBeaver-oracle.png)
*Configuración de la conexión en DBeaver*

![Evidencia de la conexión BrasaGo Oracle en DBeaver](Reguistro%20visual/DBeaver-oracle2.png)
*Conexión exitosa desde DBeaver*

![Evidencia del error al realizar el backup de Oracle](Reguistro%20visual/paso-45.png)
*Error ORA-12154 en el primer intento de backup*

![Evidencia del backup exitoso de BrasaGo en Oracle XE](Reguistro%20visual/paso-46.png)
*Backup exitoso con EZCONNECT*

![Evidencia de las variables del archivo .env de Oracle XE](Reguistro%20visual/paso-47.png)
*Verificación de las variables del .env*

---

## Variables `.env` por motor

| Motor | Variable | Valor |
| --- | --- | --- |
| MySQL | `MYSQL_ROOT_PASSWORD` / `MYSQL_DATABASE` | `5550101` / `BrasaGo` |
| PostgreSQL | `POSTGRES_PASSWORD` / `POSTGRES_DB` | `5550101` / `BrasaGo` |
| MS SQL Server | `MSSQL_SA_PASSWORD` | `BrasaGo5550101!` |
| Oracle XE | `ORACLE_PASSWORD` / `ORACLE_DATABASE` | `5550101` / `BrasaGo` |

Los cuatro usan `TZ=America/Bogota`.

## Conclusión

Instalé, configuré y verifiqué los cuatro motores solicitados —MySQL, PostgreSQL, MS SQL Server y Oracle XE— creando en cada uno la base de datos `BrasaGo`, sus 12 tablas, un usuario administrador con acceso remoto y un backup verificado, todo dentro de contenedores Docker conectados a la red compartida `ia-lab-network`. Resolví incidencias como errores de indentación YAML, permisos en los datos de Oracle y diferencias de sintaxis entre motores.

## Firma

**Elkin Eliecer Aguas Giraldo**
Estudiante de Ingeniería de Sistemas — Facultad de Ingeniería — Universidad de La Guajira
Rol: responsable de la instalación, configuración y verificación de los cuatro motores
Fecha del informe: 30/08/26
