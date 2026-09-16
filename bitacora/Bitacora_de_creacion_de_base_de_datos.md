# Bitácora de creación de base de datos — BrasaGo

## Motor: MySQL

## terminal 

### 0. Creación de la base de datos


```sql
CREATE DATABASE brasago;
```

_Evidencia:_ ![paso-0](Reguistro%20visual/paso-0.png)

### 1.entrar en la base de datos


```sql
use brasago;
```

_Evidencia:_ ![paso-1](Reguistro%20visual/paso-1.png)

### 2. Creación de la tabla users


```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(150) NOT NULL,
    password VARCHAR(255) NOT NULL,
    avatar VARCHAR(255),
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_users_username UNIQUE (username),
    CONSTRAINT uq_users_email UNIQUE (email)
) ENGINE=InnoDB;
```

_Evidencia:_ ![paso-2](Reguistro%20visual/paso-2.png)

### 3. Creación de la tabla roles

```sql
CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_roles_name UNIQUE (name)
) ENGINE=InnoDB;


```
_Evidencia:_ ![paso-3](Reguistro%20visual/paso-3.png)

### 4. Creación de la tabla resources

```sql
CREATE TABLE resources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    path VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_resources_path_method UNIQUE (path, method)
) ENGINE=InnoDB;
```
_Evidencia:_ ![paso-4](Reguistro%20visual/paso-4.png)

### 5. Creación de la tabla role_users

```sql

CREATE TABLE role_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role_id INT NOT NULL,
    user_id INT NOT NULL,
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_role_users_role_id_user_id UNIQUE (role_id, user_id),
    CONSTRAINT fk_role_users_role_id FOREIGN KEY (role_id) REFERENCES roles(id),
    CONSTRAINT fk_role_users_user_id FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB;

```
_Evidencia:_ ![paso-5](Reguistro%20visual/paso-5.png)

### 6. Creación de la tabla resource_roles

```sql
CREATE TABLE resource_roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resource_id INT NOT NULL,
    role_id INT NOT NULL,
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_resource_roles_resource_id_role_id UNIQUE (resource_id, role_id),
    CONSTRAINT fk_resource_roles_resource_id FOREIGN KEY (resource_id) REFERENCES resources(id),
    CONSTRAINT fk_resource_roles_role_id FOREIGN KEY (role_id) REFERENCES roles(id)
) ENGINE=InnoDB;

```
_Evidencia:_ ![paso-6](Reguistro%20visual/paso-6.png)

### 7. Creación de la tabla refresh_tokens

```sql
CREATE TABLE refresh_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(500) NOT NULL,
    device_info VARCHAR(255) NOT NULL,
    is_valid ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    expires_at DATETIME NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_refresh_tokens_user_id FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB;
```

_Evidencia:_ ![paso-7](Reguistro%20visual/paso-7.png)

### 8. Creación de la tabla sedes

```sql
CREATE TABLE sedes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255),
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;
```
_Evidencia:_ ![paso-8](Reguistro%20visual/paso-8.png)

### 9. Creación de la tabla mesas

```sql
CREATE TABLE mesas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sede_id INT NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    descripcion VARCHAR(255),
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_mesas_sede_id FOREIGN KEY (sede_id) REFERENCES sedes(id)
) ENGINE=InnoDB;


```
_Evidencia:_ ![paso-9](Reguistro%20visual/paso-9.png)

### 10. Creación de la tabla clientes

```sql
CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo_documento VARCHAR(20) NOT NULL,
    numero_documento VARCHAR(30) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(150),
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_clientes_numero_documento UNIQUE (numero_documento)
) ENGINE=InnoDB;
```
_Evidencia:_ ![paso-10](Reguistro%20visual/paso-10.png)

### 11. Creación de la tabla reservas

```sql
CREATE TABLE reservas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    mesa_id INT NOT NULL,
    fecha_inicio DATETIME NOT NULL,
    fecha_fin DATETIME,
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    observaciones VARCHAR(255),
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_reservas_cliente_id FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    CONSTRAINT fk_reservas_mesa_id FOREIGN KEY (mesa_id) REFERENCES mesas(id)
) ENGINE=InnoDB;
```
_Evidencia:_ ![paso-11](Reguistro%20visual/paso-11.png)

### 12. Creación de la tabla productos

```sql
CREATE TABLE productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sku VARCHAR(30) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    descripcion VARCHAR(255),
    precio DECIMAL(12,2) NOT NULL,
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_productos_sku UNIQUE (sku)
) ENGINE=InnoDB;
```
_Evidencia:_ ![paso-12](Reguistro%20visual/paso-12.png)

### 13. Creación de la tabla insumos

```sql
CREATE TABLE insumos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(30) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    unidad_medida VARCHAR(20) NOT NULL,
    stock_minimo DECIMAL(12,2),
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_insumos_codigo UNIQUE (codigo)
) ENGINE=InnoDB;

```
_Evidencia:_ ![paso-13](Reguistro%20visual/paso-13.png)

### 14. Creación de la tabla recetas_insumos

```sql
CREATE TABLE recetas_insumos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT NOT NULL,
    insumo_id INT NOT NULL,
    cantidad DECIMAL(12,2) NOT NULL,
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_recetas_insumos_producto_id_insumo_id UNIQUE (producto_id, insumo_id),
    CONSTRAINT fk_recetas_insumos_producto_id FOREIGN KEY (producto_id) REFERENCES productos(id),
    CONSTRAINT fk_recetas_insumos_insumo_id FOREIGN KEY (insumo_id) REFERENCES insumos(id)
) ENGINE=InnoDB;
```
_Evidencia:_ ![paso-14](Reguistro%20visual/paso-14.png)

### 15. Creación de la tabla domiciliarios
```sql
CREATE TABLE domiciliarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    descripcion VARCHAR(255),
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;
```
_Evidencia:_ ![paso-15](Reguistro%20visual/paso-15.png)

### 16. Creación de la tabla pedidos
```sql
CREATE TABLE pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    sede_id INT NOT NULL,
    mesa_id INT,
    canal VARCHAR(20) NOT NULL,
    fecha DATETIME NOT NULL,
    subtotal DECIMAL(12,2) NOT NULL,
    total DECIMAL(12,2) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_pedidos_cliente_id FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    CONSTRAINT fk_pedidos_sede_id FOREIGN KEY (sede_id) REFERENCES sedes(id),
    CONSTRAINT fk_pedidos_mesa_id FOREIGN KEY (mesa_id) REFERENCES mesas(id)
) ENGINE=InnoDB;
```
_Evidencia:_ ![paso-16](Reguistro%20visual/paso-16.png)

### 17. Creación de la tabla detalles_pedidos
```sql
CREATE TABLE detalles_pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad DECIMAL(12,2) NOT NULL,
    valor_unitario DECIMAL(12,2) NOT NULL,
    total DECIMAL(12,2) NOT NULL,
    observaciones VARCHAR(255),
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_detalles_pedidos_pedido_id FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    CONSTRAINT fk_detalles_pedidos_producto_id FOREIGN KEY (producto_id) REFERENCES productos(id)
) ENGINE=InnoDB;
```
_Evidencia:_ ![paso-17](Reguistro%20visual/paso-17.png)

### 18. Creación de la tabla pagos
```sql
CREATE TABLE pagos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT NOT NULL,
    metodo VARCHAR(30) NOT NULL,
    monto DECIMAL(12,2) NOT NULL,
    fecha DATETIME NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_pagos_pedido_id FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
) ENGINE=InnoDB;
```
_Evidencia:_ ![paso-18](Reguistro%20visual/paso-18.png)

### 19. Creación de la tabla entregas
```sql
CREATE TABLE entregas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT NOT NULL,
    domiciliario_id INT NOT NULL,
    fecha_inicio DATETIME,
    fecha_fin DATETIME,
    total DECIMAL(12,2),
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    observaciones VARCHAR(255),
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_entregas_pedido_id UNIQUE (pedido_id),
    CONSTRAINT fk_entregas_pedido_id FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    CONSTRAINT fk_entregas_domiciliario_id FOREIGN KEY (domiciliario_id) REFERENCES domiciliarios(id)
) ENGINE=InnoDB;
```
_Evidencia:_ ![paso-19](Reguistro%20visual/paso-19.png)

### Diagrma de la base de datos BrasaGo en DBeaver 

_Evidencia:_ ![paso-19](Reguistro%20visual/Diagrama.png)

## Ejecución por workbench

### 0. Creación de la base de datos


```sql
CREATE SCHEMA BrasaGoW;
```

_Evidencia:_ ![paso-0](Reguistro%20visual/workpaso-0.png)


### 1. Creación de la tabla users


```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(150) NOT NULL,
    password VARCHAR(255) NOT NULL,
    avatar VARCHAR(255),
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_users_username UNIQUE (username),
    CONSTRAINT uq_users_email UNIQUE (email)
) ENGINE=InnoDB;
```

_Evidencia:_ ![paso-1](Reguistro%20visual/workpaso-1.png)

### 2. Creación de la tabla roles

```sql
CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_roles_name UNIQUE (name)
) ENGINE=InnoDB;


```
_Evidencia:_ ![paso-2](Reguistro%20visual/workpaso-2.png)

### 3. Creación de la tabla resources

```sql
CREATE TABLE resources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    path VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_resources_path_method UNIQUE (path, method)
) ENGINE=InnoDB;
```
_Evidencia:_ ![paso-3](Reguistro%20visual/workpaso-3.png)

### 4. Creación de la tabla role_users

```sql

CREATE TABLE role_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role_id INT NOT NULL,
    user_id INT NOT NULL,
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_role_users_role_id_user_id UNIQUE (role_id, user_id),
    CONSTRAINT fk_role_users_role_id FOREIGN KEY (role_id) REFERENCES roles(id),
    CONSTRAINT fk_role_users_user_id FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB;

```
_Evidencia:_ ![paso-4](Reguistro%20visual/workpaso-4.png)

### 5. Creación de la tabla resource_roles

```sql
CREATE TABLE resource_roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resource_id INT NOT NULL,
    role_id INT NOT NULL,
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_resource_roles_resource_id_role_id UNIQUE (resource_id, role_id),
    CONSTRAINT fk_resource_roles_resource_id FOREIGN KEY (resource_id) REFERENCES resources(id),
    CONSTRAINT fk_resource_roles_role_id FOREIGN KEY (role_id) REFERENCES roles(id)
) ENGINE=InnoDB;

```
_Evidencia:_ ![paso-5](Reguistro%20visual/workpaso-5.png)

### 6. Creación de la tabla refresh_tokens

```sql
CREATE TABLE refresh_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(500) NOT NULL,
    device_info VARCHAR(255) NOT NULL,
    is_valid ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    expires_at DATETIME NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_refresh_tokens_user_id FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB;
```

_Evidencia:_ ![paso-6](Reguistro%20visual/workpaso-6.png)

### 7. Creación de la tabla sedes

```sql
CREATE TABLE sedes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255),
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;
```
_Evidencia:_ ![paso-7](Reguistro%20visual/workpaso-7.png)

### 8. Creación de la tabla mesas

```sql
CREATE TABLE mesas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sede_id INT NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    descripcion VARCHAR(255),
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_mesas_sede_id FOREIGN KEY (sede_id) REFERENCES sedes(id)
) ENGINE=InnoDB;


```
_Evidencia:_ ![paso-8](Reguistro%20visual/workpaso-8.png)

### 9. Creación de la tabla clientes

```sql
CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo_documento VARCHAR(20) NOT NULL,
    numero_documento VARCHAR(30) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(150),
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_clientes_numero_documento UNIQUE (numero_documento)
) ENGINE=InnoDB;
```
_Evidencia:_ ![paso-9](Reguistro%20visual/workpaso-9.png)

### 10. Creación de la tabla reservas

```sql
CREATE TABLE reservas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    mesa_id INT NOT NULL,
    fecha_inicio DATETIME NOT NULL,
    fecha_fin DATETIME,
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    observaciones VARCHAR(255),
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_reservas_cliente_id FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    CONSTRAINT fk_reservas_mesa_id FOREIGN KEY (mesa_id) REFERENCES mesas(id)
) ENGINE=InnoDB;
```
_Evidencia:_ ![paso-10](Reguistro%20visual/workpaso-10.png)

### 11. Creación de la tabla productos

```sql
CREATE TABLE productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sku VARCHAR(30) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    descripcion VARCHAR(255),
    precio DECIMAL(12,2) NOT NULL,
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_productos_sku UNIQUE (sku)
) ENGINE=InnoDB;
```
_Evidencia:_ ![paso-11](Reguistro%20visual/workpaso-11.png)

### 12. Creación de la tabla insumos

```sql
CREATE TABLE insumos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(30) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    unidad_medida VARCHAR(20) NOT NULL,
    stock_minimo DECIMAL(12,2),
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_insumos_codigo UNIQUE (codigo)
) ENGINE=InnoDB;

```
_Evidencia:_ ![paso-12](Reguistro%20visual/workpaso-12.png)

### 13. Creación de la tabla recetas_insumos

```sql
CREATE TABLE recetas_insumos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT NOT NULL,
    insumo_id INT NOT NULL,
    cantidad DECIMAL(12,2) NOT NULL,
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_recetas_insumos_producto_id_insumo_id UNIQUE (producto_id, insumo_id),
    CONSTRAINT fk_recetas_insumos_producto_id FOREIGN KEY (producto_id) REFERENCES productos(id),
    CONSTRAINT fk_recetas_insumos_insumo_id FOREIGN KEY (insumo_id) REFERENCES insumos(id)
) ENGINE=InnoDB;
```
_Evidencia:_ ![paso-13](Reguistro%20visual/workpaso-13.png)

### 14. Creación de la tabla domiciliarios
```sql
CREATE TABLE domiciliarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    descripcion VARCHAR(255),
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;
```
_Evidencia:_ ![paso-14](Reguistro%20visual/workpaso-14.png)

### 15. Creación de la tabla pedidos
```sql
CREATE TABLE pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    sede_id INT NOT NULL,
    mesa_id INT,
    canal VARCHAR(20) NOT NULL,
    fecha DATETIME NOT NULL,
    subtotal DECIMAL(12,2) NOT NULL,
    total DECIMAL(12,2) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_pedidos_cliente_id FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    CONSTRAINT fk_pedidos_sede_id FOREIGN KEY (sede_id) REFERENCES sedes(id),
    CONSTRAINT fk_pedidos_mesa_id FOREIGN KEY (mesa_id) REFERENCES mesas(id)
) ENGINE=InnoDB;
```
_Evidencia:_ ![paso-15](Reguistro%20visual/workpaso-15.png)

### 16. Creación de la tabla detalles_pedidos
```sql
CREATE TABLE detalles_pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad DECIMAL(12,2) NOT NULL,
    valor_unitario DECIMAL(12,2) NOT NULL,
    total DECIMAL(12,2) NOT NULL,
    observaciones VARCHAR(255),
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_detalles_pedidos_pedido_id FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    CONSTRAINT fk_detalles_pedidos_producto_id FOREIGN KEY (producto_id) REFERENCES productos(id)
) ENGINE=InnoDB;
```
_Evidencia:_ ![paso-16](Reguistro%20visual/workpaso-16.png)

### 17. Creación de la tabla pagos
```sql
CREATE TABLE pagos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT NOT NULL,
    metodo VARCHAR(30) NOT NULL,
    monto DECIMAL(12,2) NOT NULL,
    fecha DATETIME NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_pagos_pedido_id FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
) ENGINE=InnoDB;
```
_Evidencia:_ ![paso-17](Reguistro%20visual/workpaso-17.png)

### 18. Creación de la tabla entregas
```sql
CREATE TABLE entregas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT NOT NULL,
    domiciliario_id INT NOT NULL,
    fecha_inicio DATETIME,
    fecha_fin DATETIME,
    total DECIMAL(12,2),
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    observaciones VARCHAR(255),
    is_active ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_entregas_pedido_id UNIQUE (pedido_id),
    CONSTRAINT fk_entregas_pedido_id FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    CONSTRAINT fk_entregas_domiciliario_id FOREIGN KEY (domiciliario_id) REFERENCES domiciliarios(id)
) ENGINE=InnoDB;
```
_Evidencia:_ ![paso-18](Reguistro%20visual/workpaso-18.png)

### Modelo de la base de datos BrasaGoW en workbench

_Evidencia:_ ![paso-19](Reguistro%20visual/workmodelo.png)

## Motor: PostgreSQL

### 0. Creación de la base de datos


```sql
CREATE DATABASE BrasaGo;
```

_Evidencia:_ ![paso-0](Reguistro%20visual/postpaso-0.png)

### 1.crear un nuevo tipo de dato ENUM llamado estatus_enum.

```sql
-- Tipo ENUM reutilizable para el campo de estatus (is_active / is_valid)
CREATE TYPE estatus_enum AS ENUM ('ACTIVE', 'INACTIVE');
```

_Evidencia:_ ![paso-1](Reguistro%20visual/postpaso-1.png)

### 2. Creación de la tabla users

```sql
CREATE TABLE users (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(150) NOT NULL,
    password VARCHAR(255) NOT NULL,
    avatar VARCHAR(255),
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_users_username UNIQUE (username),
    CONSTRAINT uq_users_email UNIQUE (email)
);
```
_Evidencia:_ ![paso-2](Reguistro%20visual/postpaso-2.png)

### 3. Creación de la tabla roles

```sql
CREATE TABLE roles (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_roles_name UNIQUE (name)
);
```
_Evidencia:_ ![paso-3](Reguistro%20visual/postpaso-3.png)

### 4. Creación de la tabla resources
```sql
CREATE TABLE resources (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    path VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_resources_path_method UNIQUE (path, method)
);
```
_Evidencia:_ ![paso-4](Reguistro%20visual/postpaso-4.png)

### 5. Creación de la tabla role_users
```sql
CREATE TABLE role_users (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    role_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_role_users_role_id_user_id UNIQUE (role_id, user_id),
    CONSTRAINT fk_role_users_role_id FOREIGN KEY (role_id) REFERENCES roles(id),
    CONSTRAINT fk_role_users_user_id FOREIGN KEY (user_id) REFERENCES users(id)
);
```
_Evidencia:_ ![paso-5](Reguistro%20visual/postpaso-5.png)

### 6. Creación de la tabla resource_roles
```sql
CREATE TABLE resource_roles (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    resource_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_resource_roles_resource_id_role_id UNIQUE (resource_id, role_id),
    CONSTRAINT fk_resource_roles_resource_id FOREIGN KEY (resource_id) REFERENCES resources(id),
    CONSTRAINT fk_resource_roles_role_id FOREIGN KEY (role_id) REFERENCES roles(id)
);
```
_Evidencia:_ ![paso-6](Reguistro%20visual/postpaso-6.png)

### 7. Creación de la tabla refresh_tokens
```sql
CREATE TABLE refresh_tokens (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id INTEGER NOT NULL,
    token VARCHAR(500) NOT NULL,
    device_info VARCHAR(255) NOT NULL,
    is_valid estatus_enum NOT NULL DEFAULT 'ACTIVE',
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_refresh_tokens_user_id FOREIGN KEY (user_id) REFERENCES users(id)
);
```
_Evidencia:_ ![paso-7](Reguistro%20visual/postpaso-7.png)

### 8. Creación de la tabla sedes
```sql
CREATE TABLE sedes (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255),
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```
_Evidencia:_ ![paso-8](Reguistro%20visual/postpaso-8.png)

### 9. Creación de la tabla mesas
```sql
CREATE TABLE mesas (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sede_id INTEGER NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    descripcion VARCHAR(255),
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_mesas_sede_id FOREIGN KEY (sede_id) REFERENCES sedes(id)
);
```
_Evidencia:_ ![paso-9](Reguistro%20visual/postpaso-9.png)

### 10. Creación de la tabla clientes
```sql
CREATE TABLE clientes (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tipo_documento VARCHAR(20) NOT NULL,
    numero_documento VARCHAR(30) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(150),
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_clientes_numero_documento UNIQUE (numero_documento)
);
```
_Evidencia:_ ![paso-10](Reguistro%20visual/postpaso-10.png)

### 11. Creación de la tabla reservas
```sql
CREATE TABLE reservas (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cliente_id INTEGER NOT NULL,
    mesa_id INTEGER NOT NULL,
    fecha_inicio TIMESTAMP NOT NULL,
    fecha_fin TIMESTAMP,
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    observaciones VARCHAR(255),
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_reservas_cliente_id FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    CONSTRAINT fk_reservas_mesa_id FOREIGN KEY (mesa_id) REFERENCES mesas(id)
);
```
_Evidencia:_ ![paso-11](Reguistro%20visual/postpaso-11.png)

### 12. Creación de la tabla productos
```sql
CREATE TABLE productos (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sku VARCHAR(30) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    descripcion VARCHAR(255),
    precio NUMERIC(12,2) NOT NULL,
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_productos_sku UNIQUE (sku)
);
```
_Evidencia:_ ![paso-12](Reguistro%20visual/postpaso-12.png)

### 13. Creación de la tabla insumos
```sql
CREATE TABLE insumos (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo VARCHAR(30) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    unidad_medida VARCHAR(20) NOT NULL,
    stock_minimo NUMERIC(12,2),
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_insumos_codigo UNIQUE (codigo)
);
```
_Evidencia:_ ![paso-13](Reguistro%20visual/postpaso-13.png)

### 14. Creación de la tabla recetas_insumos
```sql
CREATE TABLE recetas_insumos (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    producto_id INTEGER NOT NULL,
    insumo_id INTEGER NOT NULL,
    cantidad NUMERIC(12,2) NOT NULL,
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_recetas_insumos_producto_id_insumo_id UNIQUE (producto_id, insumo_id),
    CONSTRAINT fk_recetas_insumos_producto_id FOREIGN KEY (producto_id) REFERENCES productos(id),
    CONSTRAINT fk_recetas_insumos_insumo_id FOREIGN KEY (insumo_id) REFERENCES insumos(id)
);
```
_Evidencia:_ ![paso-14](Reguistro%20visual/postpaso-14.png)

### 15. Creación de la tabla domiciliarios
```sql
CREATE TABLE domiciliarios (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    descripcion VARCHAR(255),
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```
_Evidencia:_ ![paso-15](Reguistro%20visual/postpaso-15.png)

### 16. Creación de la tabla pedidos
```sql
CREATE TABLE pedidos (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cliente_id INTEGER NOT NULL,
    sede_id INTEGER NOT NULL,
    mesa_id INTEGER,
    canal VARCHAR(20) NOT NULL,
    fecha TIMESTAMP NOT NULL,
    subtotal NUMERIC(12,2) NOT NULL,
    total NUMERIC(12,2) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_pedidos_cliente_id FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    CONSTRAINT fk_pedidos_sede_id FOREIGN KEY (sede_id) REFERENCES sedes(id),
    CONSTRAINT fk_pedidos_mesa_id FOREIGN KEY (mesa_id) REFERENCES mesas(id)
);
```
_Evidencia:_ ![paso-16](Reguistro%20visual/postpaso-16.png)

### 17. Creación de la tabla detalles_pedidoss
```sql
CREATE TABLE detalles_pedidos (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pedido_id INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,
    cantidad NUMERIC(12,2) NOT NULL,
    valor_unitario NUMERIC(12,2) NOT NULL,
    total NUMERIC(12,2) NOT NULL,
    observaciones VARCHAR(255),
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_detalles_pedidos_pedido_id FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    CONSTRAINT fk_detalles_pedidos_producto_id FOREIGN KEY (producto_id) REFERENCES productos(id)
);
```
_Evidencia:_ ![paso-17](Reguistro%20visual/postpaso-17.png)

### 18. Creación de la tabla pagos
```sql
CREATE TABLE pagos (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pedido_id INTEGER NOT NULL,
    metodo VARCHAR(30) NOT NULL,
    monto NUMERIC(12,2) NOT NULL,
    fecha TIMESTAMP NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_pagos_pedido_id FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
);
```
_Evidencia:_ ![paso-18](Reguistro%20visual/postpaso-18.png)

### 19. Creación de la tabla entregas
```sql
CREATE TABLE entregas (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pedido_id INTEGER NOT NULL,
    domiciliario_id INTEGER NOT NULL,
    fecha_inicio TIMESTAMP,
    fecha_fin TIMESTAMP,
    total NUMERIC(12,2),
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    observaciones VARCHAR(255),
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_entregas_pedido_id UNIQUE (pedido_id),
    CONSTRAINT fk_entregas_pedido_id FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    CONSTRAINT fk_entregas_domiciliario_id FOREIGN KEY (domiciliario_id) REFERENCES domiciliarios(id)
);
```
_Evidencia:_ ![paso-19](Reguistro%20visual/postpaso-19.png)

### Diagrma de la base de datos BrasaGo en DBeaver 

_Evidencia:_ ![paso-19](Reguistro%20visual/Diagramapost.png)

## Ejecución por pgAdmin

### 0. Creación de la base de datos


```sql
CREATE DATABASE BrasaGo;
```

_Evidencia:_ ![paso-0](Reguistro%20visual/pgpaso-0.png)

### 1.crear un nuevo tipo de dato ENUM llamado estatus_enum.

```sql
-- Tipo ENUM reutilizable para el campo de estatus (is_active / is_valid)
CREATE TYPE estatus_enum AS ENUM ('ACTIVE', 'INACTIVE');
```

_Evidencia:_ ![paso-1](Reguistro%20visual/pgpaso-1.png)

### 2. Creación de la tabla users

```sql
CREATE TABLE public.users
(
    id serial NOT NULL,
    username character(50) NOT NULL,
    email character(150) NOT NULL,
    password character(255) NOT NULL,
    avatar character(255),
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT uq_users_username UNIQUE (username),
    CONSTRAINT uq_users_email UNIQUE (email)
);

ALTER TABLE IF EXISTS public.users
    OWNER to admin;
```
_Evidencia:_ ![paso-2](Reguistro%20visual/pgpaso-2.png)

### 3. Creación de la tabla roles

```sql
CREATE TABLE public.roles
(
    id serial NOT NULL,
    name character(50) NOT NULL,
    is_active estatus_enum DEFAULT 'ACTIVE',
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT uq_roles_name UNIQUE (name)
);

ALTER TABLE IF EXISTS public.roles
    OWNER to admin;
```
_Evidencia:_ ![paso-3](Reguistro%20visual/pgpaso-3.png)

### 4. Creación de la tabla resources
```sql
CREATE TABLE public.resources
(
    id serial NOT NULL,
    patth character(255) NOT NULL,
    method character(10) NOT NULL,
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT uq_resources_path UNIQUE (patth),
    CONSTRAINT uq_resources_method UNIQUE (method)
);

ALTER TABLE IF EXISTS public.resources
    OWNER to admin;
```
_Evidencia:_ ![paso-4](Reguistro%20visual/pgpaso-4.png)

### 5. Creación de la tabla role_users
```sql
CREATE TABLE public.role_users
(
    id serial NOT NULL,
    role_id integer NOT NULL,
    user_id integer NOT NULL,
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT uq_role_users_role_id_user_id UNIQUE (role_id, user_id),
    CONSTRAINT fk_role_users_role_id FOREIGN KEY (role_id)
        REFERENCES public.roles (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT fk_role_users_user_id FOREIGN KEY (user_id)
        REFERENCES public.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
);

ALTER TABLE IF EXISTS public.role_users
    OWNER to admin;
```
_Evidencia:_ ![paso-5](Reguistro%20visual/pgpaso-5.png)

### 6. Creación de la tabla resource_roles
```sql
CREATE TABLE public.resource_roles
(
    id serial NOT NULL,
    resource_id integer NOT NULL,
    role_id integer NOT NULL,
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT uq_resource_roles_resource_id_role_id UNIQUE (resource_id, role_id),
    CONSTRAINT fk_resource_roles_resource_id FOREIGN KEY (resource_id)
        REFERENCES public.resources (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT fk_resource_roles_role_id FOREIGN KEY (role_id)
        REFERENCES public.roles (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
);

ALTER TABLE IF EXISTS public.resource_roles
    OWNER to admin;
```
_Evidencia:_ ![paso-6](Reguistro%20visual/pgpaso-6.png)

### 7. Creación de la tabla refresh_tokens
```sql
CREATE TABLE public.refresh_tokens
(
    id serial NOT NULL,
    user_id integer NOT NULL,
    token character(500) NOT NULL,
    device_info character(255) NOT NULL,
    is_valid estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_refresh_tokens_user_id FOREIGN KEY (user_id)
        REFERENCES public.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
);

ALTER TABLE IF EXISTS public.refresh_tokens
    OWNER to admin;
```
_Evidencia:_ ![paso-7](Reguistro%20visual/pgpaso-7.png)

### 8. Creación de la tabla sedes
```sql
CREATE TABLE public.sedes
(
    id serial NOT NULL,
    nombre character(100) NOT NULL,
    descripcion character(255),
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

ALTER TABLE IF EXISTS public.sedes
    OWNER to admin;
```
_Evidencia:_ ![paso-8](Reguistro%20visual/pgpaso-8.png)

### 9. Creación de la tabla mesas
```sql
CREATE TABLE public.mesas
(
    id serial NOT NULL,
    sede_id integer NOT NULL,
    nombre character(50) NOT NULL,
    descripcion character(255),
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    "    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP," timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_mesas_sede_id FOREIGN KEY (sede_id)
        REFERENCES public.sedes (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
);

ALTER TABLE IF EXISTS public.mesas
    OWNER to admin;
```
_Evidencia:_ ![paso-9](Reguistro%20visual/pgpaso-9.png)

### 10. Creación de la tabla clientes
```sql
CREATE TABLE public.clientes
(
    id serial NOT NULL,
    tipo_documento character(20) NOT NULL,
    numero_documento character(30) NOT NULL,
    nombre character(150) NOT NULL,
    telefono character(20),
    email character(150),
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at timestamp with time zone NOT NULL DEFAULT    CURRENT_TIMESTAMP,
    updated_at timestamp with time zone NOT NULL DEFAULT  CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT uq_clientes_numero_documento UNIQUE (numero_documento)
);

ALTER TABLE IF EXISTS public.clientes
    OWNER to admin;ublic.clientes
    OWNER to admin;
```
_Evidencia:_ ![paso-10](Reguistro%20visual/pgpaso-10.png)

### 11. Creación de la tabla reservas
```sql
CREATE TABLE public.reservas
(
    id serial NOT NULL,
    cliente_id integer NOT NULL,
    mesa_id integer NOT NULL,
    fecha_inicio timestamp with time zone NOT NULL,
    fecha_fin timestamp with time zone,
    estado character(20) NOT NULL DEFAULT 'PENDIENTE',
    observaciones character(255),
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_reservas_cliente_id FOREIGN KEY (cliente_id)
        REFERENCES public.clientes (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT fk_reservas_mesa_id FOREIGN KEY (mesa_id)
        REFERENCES public.mesas (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
);

ALTER TABLE IF EXISTS public.reservas
    OWNER to admin;
```
_Evidencia:_ ![paso-11](Reguistro%20visual/pgpaso-11.png)

### 12. Creación de la tabla productos
```sql
CREATE TABLE public.productos
(
    id serial NOT NULL,
    sku character(30) NOT NULL,
    nombre character(150) NOT NULL,
    descripcion character(255),
    precio bigint NOT NULL,
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT uq_productos_sku UNIQUE (sku)
);

ALTER TABLE IF EXISTS public.productos
    OWNER to admin;
```
_Evidencia:_ ![paso-12](Reguistro%20visual/pgpaso-12.png)

### 13. Creación de la tabla insumos
```sql
CREATE TABLE public.insumos
(
    id serial NOT NULL,
    codigo character(30) NOT NULL,
    nombre character(150) NOT NULL,
    unidad_medida character(20) NOT NULL,
    stock_minimo bigint,
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT uq_insumos_codigo UNIQUE (codigo)
);

ALTER TABLE IF EXISTS public.insumos
    OWNER to admin;
```
_Evidencia:_ ![paso-13](Reguistro%20visual/pgpaso-13.png)

### 14. Creación de la tabla recetas_insumos
```sql
CREATE TABLE public.recetas_insumos
(
    id serial NOT NULL,
    producto_id integer NOT NULL,
    insumo_id integer NOT NULL,
    cantidad bigint NOT NULL,
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT uq_recetas_insumos_producto_id_insumo_id UNIQUE (producto_id, insumo_id),
    CONSTRAINT fk_recetas_insumos_producto_id FOREIGN KEY (producto_id)
        REFERENCES public.productos (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT fk_recetas_insumos_insumo_id FOREIGN KEY (insumo_id)
        REFERENCES public.insumos (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
);

ALTER TABLE IF EXISTS public.recetas_insumos
    OWNER to admin;
```
_Evidencia:_ ![paso-14](Reguistro%20visual/pgpaso-14.png)

### 15. Creación de la tabla domiciliarios
```sql
CREATE TABLE public.domiciliarios
(
    id serial NOT NULL,
    nombre character(150) NOT NULL,
    descripcion character(255),
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

ALTER TABLE IF EXISTS public.domiciliarios
    OWNER to admin;
```
_Evidencia:_ ![paso-15](Reguistro%20visual/pgpaso-15.png)

### 16. Creación de la tabla pedidos
```sql
CREATE TABLE public.pedidos
(
    id serial NOT NULL,
    cliente_id integer NOT NULL,
    sede_id integer NOT NULL,
    mesa_id integer NOT NULL,
    canal character(30) NOT NULL,
    fecha timestamp with time zone NOT NULL,
    subtotal bigint NOT NULL,
    total bigint NOT NULL,
    estado character(20) NOT NULL DEFAULT 'PENDIENTE',
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_pedidos_cliente_id FOREIGN KEY (cliente_id)
        REFERENCES public.clientes (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT fk_pedidos_sede_id FOREIGN KEY (sede_id)
        REFERENCES public.sedes (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT fk_pedidos_mesa_id FOREIGN KEY (mesa_id)
        REFERENCES public.mesas (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
);
```
_Evidencia:_ ![paso-16](Reguistro%20visual/pgpaso-16.png)

### 17. Creación de la tabla detalles_pedidoss
```sql
CREATE TABLE public.detalles_pedidos
(
    id serial NOT NULL,
    pedido_id integer NOT NULL,
    producto_id integer NOT NULL,
    cantidad bigint NOT NULL,
    valor_unitario bigint NOT NULL,
    total bigint NOT NULL,
    observaciones character(255),
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_detalles_pedidos_pedido_id FOREIGN KEY (pedido_id)
        REFERENCES public.pedidos (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT fk_detalles_pedidos_producto_id FOREIGN KEY (producto_id)
        REFERENCES public.productos (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
);

ALTER TABLE IF EXISTS public.detalles_pedidos
    OWNER to admin;
```
_Evidencia:_ ![paso-17](Reguistro%20visual/pgpaso-17.png)

### 18. Creación de la tabla pagos
```sql
CREATE TABLE public.pagos
(
    id serial NOT NULL,
    pedido_id integer NOT NULL,
    metodo character(30) NOT NULL,
    monto bigint NOT NULL,
    fecha timestamp with time zone NOT NULL,
    estado character(20) NOT NULL DEFAULT 'PENDIENTE',
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_pagos_pedido_id FOREIGN KEY (pedido_id)
        REFERENCES public.pedidos (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
);

ALTER TABLE IF EXISTS public.pagos
    OWNER to admin;
```
_Evidencia:_ ![paso-18](Reguistro%20visual/pgpaso-18.png)

### 19. Creación de la tabla entregas
```sql
CREATE TABLE public.entregas
(
    id serial NOT NULL,
    pedido_id integer NOT NULL,
    domiciliario_id integer NOT NULL,
    fecha_inicio timestamp with time zone,
    fecha_fin timestamp with time zone,
    total bigint NOT NULL,
    estado character(20) NOT NULL DEFAULT 'PENDIENTE',
    observaciones character(255),
    is_active estatus_enum NOT NULL DEFAULT 'ACTIVE',
    created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT uq_entregas_pedido_id UNIQUE (pedido_id),
    CONSTRAINT fk_entregas_pedido_id FOREIGN KEY (pedido_id)
        REFERENCES public.pedidos (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT fk_entregas_domiciliario_id FOREIGN KEY (domiciliario_id)
        REFERENCES public.domiciliarios (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
);

ALTER TABLE IF EXISTS public.entregas
    OWNER to admin;
```
_Evidencia:_ ![paso-19](Reguistro%20visual/pgpaso-19.png)

### Diagrma de la base de datos BrasaGo en pgAdmin

_Evidencia:_ ![paso-20](Reguistro%20visual/modelopg.png)


---

## Motor: SQL Server

### 0. Creación de la base de datos

```sql
CREATE DATABASE brasago;
```

_Evidencia:_ ![paso-0](Reguistro%20visual/sqlpaso-0.png)

### 1. CEntrar en la base de datos

```sql
USE brasago;
```

_Evidencia:_ ![paso-1](Reguistro%20visual/sqlpaso-1.png)

### 2. Creación de la tabla users

```sql
CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(150) NOT NULL,
    password VARCHAR(255) NOT NULL,
    avatar VARCHAR(255),
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT uq_users_username UNIQUE (username),
    CONSTRAINT uq_users_email UNIQUE (email)
);
```
_Evidencia:_ ![paso-2](Reguistro%20visual/sqlpaso-2.png)

### 3. Creacion de la tabla roles
```sql
CREATE TABLE roles (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT uq_roles_name UNIQUE (name)
);
```
_Evidencia:_ ![paso-3](Reguistro%20visual/sqlpaso-3.png)

### 4. Creacion de la tabla resources
```sql
CREATE TABLE resources (
    id INT IDENTITY(1,1) PRIMARY KEY,
    path VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT uq_resources_path_method UNIQUE (path, method)
);
```
_Evidencia:_ ![paso-4](Reguistro%20visual/sqlpaso-4.png)

### 5. Creacion de la tabla role_users
```sql
CREATE TABLE role_users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    role_id INT NOT NULL,
    user_id INT NOT NULL,
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT uq_role_users_role_id_user_id UNIQUE (role_id, user_id),
    CONSTRAINT fk_role_users_role_id FOREIGN KEY (role_id) REFERENCES roles(id),
    CONSTRAINT fk_role_users_user_id FOREIGN KEY (user_id) REFERENCES users(id)
);
```
_Evidencia:_ ![paso-5](Reguistro%20visual/sqlpaso-5.png)

### 6. Creacion de la tabla resource_roles
```sql
CREATE TABLE resource_roles (
    id INT IDENTITY(1,1) PRIMARY KEY,
    resource_id INT NOT NULL,
    role_id INT NOT NULL,
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT uq_resource_roles_resource_id_role_id UNIQUE (resource_id, role_id),
    CONSTRAINT fk_resource_roles_resource_id FOREIGN KEY (resource_id) REFERENCES resources(id),
    CONSTRAINT fk_resource_roles_role_id FOREIGN KEY (role_id) REFERENCES roles(id)
);
```
_Evidencia:_ ![paso-6](Reguistro%20visual/sqlpaso-6.png)

### 7. Creacion de la tabla refresh_tokens
```sql
CREATE TABLE refresh_tokens (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(500) NOT NULL,
    device_info VARCHAR(255) NOT NULL,
    is_valid VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_valid IN ('ACTIVE','INACTIVE')),
    expires_at DATETIME2 NOT NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT fk_refresh_tokens_user_id FOREIGN KEY (user_id) REFERENCES users(id)
);
```
_Evidencia:_ ![paso-7](Reguistro%20visual/sqlpaso-7.png)

### 8. Creacion de la tabla sedes
```sql
CREATE TABLE sedes (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255),
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME()
);
```
_Evidencia:_ ![paso-8](Reguistro%20visual/sqlpaso-8.png)

### 9. Creacion de la tabla mesas
```sql
CREATE TABLE mesas (
    id INT IDENTITY(1,1) PRIMARY KEY,
    sede_id INT NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    descripcion VARCHAR(255),
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT fk_mesas_sede_id FOREIGN KEY (sede_id) REFERENCES sedes(id)
);
```
_Evidencia:_ ![paso-9](Reguistro%20visual/sqlpaso-9.png)

### 10. Creacion de la tabla clientes
```sql
CREATE TABLE clientes (
    id INT IDENTITY(1,1) PRIMARY KEY,
    tipo_documento VARCHAR(20) NOT NULL,
    numero_documento VARCHAR(30) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(150),
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT uq_clientes_numero_documento UNIQUE (numero_documento)
);
```
_Evidencia:_ ![paso-10](Reguistro%20visual/sqlpaso-10.png)

### 11. Creacion de la tabla reservas
```sql
CREATE TABLE reservas (
    id INT IDENTITY(1,1) PRIMARY KEY,
    cliente_id INT NOT NULL,
    mesa_id INT NOT NULL,
    fecha_inicio DATETIME2 NOT NULL,
    fecha_fin DATETIME2,
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    observaciones VARCHAR(255),
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT fk_reservas_cliente_id FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    CONSTRAINT fk_reservas_mesa_id FOREIGN KEY (mesa_id) REFERENCES mesas(id)
);
```
_Evidencia:_ ![paso-11](Reguistro%20visual/sqlpaso-11.png)

### 12. Creacion de la tabla productos
```sql
CREATE TABLE productos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    sku VARCHAR(30) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    descripcion VARCHAR(255),
    precio DECIMAL(12,2) NOT NULL,
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT uq_productos_sku UNIQUE (sku)
);
```
_Evidencia:_ ![paso-12](Reguistro%20visual/sqlpaso-12.png)

### 13. Creacion de la tabla insumos
```sql
CREATE TABLE insumos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    codigo VARCHAR(30) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    unidad_medida VARCHAR(20) NOT NULL,
    stock_minimo DECIMAL(12,2),
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT uq_insumos_codigo UNIQUE (codigo)
);
```
_Evidencia:_ ![paso-13](Reguistro%20visual/sqlpaso-13.png)

### 14. Creacion de la tabla recetas_insumos
```sql
CREATE TABLE recetas_insumos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    producto_id INT NOT NULL,
    insumo_id INT NOT NULL,
    cantidad DECIMAL(12,2) NOT NULL,
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT uq_recetas_insumos_producto_id_insumo_id UNIQUE (producto_id, insumo_id),
    CONSTRAINT fk_recetas_insumos_producto_id FOREIGN KEY (producto_id) REFERENCES productos(id),
    CONSTRAINT fk_recetas_insumos_insumo_id FOREIGN KEY (insumo_id) REFERENCES insumos(id)
);
```
_Evidencia:_ ![paso-14](Reguistro%20visual/sqlpaso-14.png)

### 15. Creacion de la tabla domiciliarios
```sql
CREATE TABLE domiciliarios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    descripcion VARCHAR(255),
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME()
);
```
_Evidencia:_ ![paso-15](Reguistro%20visual/sqlpaso-15.png)

### 16. Creacion de la tabla pedidos
```sql
CREATE TABLE pedidos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    cliente_id INT NOT NULL,
    sede_id INT NOT NULL,
    mesa_id INT,
    canal VARCHAR(20) NOT NULL,
    fecha DATETIME2 NOT NULL,
    subtotal DECIMAL(12,2) NOT NULL,
    total DECIMAL(12,2) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT fk_pedidos_cliente_id FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    CONSTRAINT fk_pedidos_sede_id FOREIGN KEY (sede_id) REFERENCES sedes(id),
    CONSTRAINT fk_pedidos_mesa_id FOREIGN KEY (mesa_id) REFERENCES mesas(id)
);
```
_Evidencia:_ ![paso-16](Reguistro%20visual/sqlpaso-16.png)

### 17. Creacion de la tabla detalles_pedidos
```sql
CREATE TABLE detalles_pedidos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    pedido_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad DECIMAL(12,2) NOT NULL,
    valor_unitario DECIMAL(12,2) NOT NULL,
    total DECIMAL(12,2) NOT NULL,
    observaciones VARCHAR(255),
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT fk_detalles_pedidos_pedido_id FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    CONSTRAINT fk_detalles_pedidos_producto_id FOREIGN KEY (producto_id) REFERENCES productos(id)
);
```
_Evidencia:_ ![paso-17](Reguistro%20visual/sqlpaso-17.png)

### 18. Creacion de la tabla pagos
```sql
CREATE TABLE pagos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    pedido_id INT NOT NULL,
    metodo VARCHAR(30) NOT NULL,
    monto DECIMAL(12,2) NOT NULL,
    fecha DATETIME2 NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT fk_pagos_pedido_id FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
);
```
_Evidencia:_ ![paso-18](Reguistro%20visual/sqlpaso-18.png)

### 19. Creacion de la tabla entregas
```sql
CREATE TABLE entregas (
    id INT IDENTITY(1,1) PRIMARY KEY,
    pedido_id INT NOT NULL,
    domiciliario_id INT NOT NULL,
    fecha_inicio DATETIME2,
    fecha_fin DATETIME2,
    total DECIMAL(12,2),
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    observaciones VARCHAR(255),
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT uq_entregas_pedido_id UNIQUE (pedido_id),
    CONSTRAINT fk_entregas_pedido_id FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    CONSTRAINT fk_entregas_domiciliario_id FOREIGN KEY (domiciliario_id) REFERENCES domiciliarios(id)
);
```
_Evidencia:_ ![paso-19](Reguistro%20visual/sqlpaso-19.png)

### Diagrma de la base de datos BrasaGo en DBeaver 

_Evidencia:_ ![paso-19](Reguistro%20visual/Diagramasql.png)

## Ejecución por Microsoft SQL Server

### 0. Creación de la base de datos

```sql
CREATE DATABASE BrasaGoserver;
```
_Evidencia:_ ![paso-0](Reguistro%20visual/serpaso-0.png)

### 1. Creación de la tabla users

```sql
CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(150) NOT NULL,
    password VARCHAR(255) NOT NULL,
    avatar VARCHAR(255),
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT uq_users_username UNIQUE (username),
    CONSTRAINT uq_users_email UNIQUE (email)
);
```
_Evidencia:_ ![paso-1](Reguistro%20visual/serpaso-1.png)

### 2. Creacion de la tabla roles
```sql
CREATE TABLE roles (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT uq_roles_name UNIQUE (name)
);
```
_Evidencia:_ ![paso-2](Reguistro%20visual/serpaso-2.png)

### 3. Creacion de la tabla resources
```sql
CREATE TABLE resources (
    id INT IDENTITY(1,1) PRIMARY KEY,
    path VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT uq_resources_path_method UNIQUE (path, method)
);
```
_Evidencia:_ ![paso-3](Reguistro%20visual/serpaso-3.png)

### 4. Creacion de la tabla role_users
```sql
CREATE TABLE role_users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    role_id INT NOT NULL,
    user_id INT NOT NULL,
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT uq_role_users_role_id_user_id UNIQUE (role_id, user_id),
    CONSTRAINT fk_role_users_role_id FOREIGN KEY (role_id) REFERENCES roles(id),
    CONSTRAINT fk_role_users_user_id FOREIGN KEY (user_id) REFERENCES users(id)
);
```
_Evidencia:_ ![paso-4](Reguistro%20visual/serpaso-4.png)

### 5. Creacion de la tabla resource_roles
```sql
CREATE TABLE resource_roles (
    id INT IDENTITY(1,1) PRIMARY KEY,
    resource_id INT NOT NULL,
    role_id INT NOT NULL,
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT uq_resource_roles_resource_id_role_id UNIQUE (resource_id, role_id),
    CONSTRAINT fk_resource_roles_resource_id FOREIGN KEY (resource_id) REFERENCES resources(id),
    CONSTRAINT fk_resource_roles_role_id FOREIGN KEY (role_id) REFERENCES roles(id)
);
```
_Evidencia:_ ![paso-5](Reguistro%20visual/serpaso-5.png)

### 6. Creacion de la tabla refresh_tokens
```sql
CREATE TABLE refresh_tokens (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(500) NOT NULL,
    device_info VARCHAR(255) NOT NULL,
    is_valid VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_valid IN ('ACTIVE','INACTIVE')),
    expires_at DATETIME2 NOT NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT fk_refresh_tokens_user_id FOREIGN KEY (user_id) REFERENCES users(id)
);
```
_Evidencia:_ ![paso-6](Reguistro%20visual/serpaso-6.png)

### 7. Creacion de la tabla sedes
```sql
CREATE TABLE sedes (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255),
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME()
);
```
_Evidencia:_ ![paso-7](Reguistro%20visual/serpaso-7.png)

### 8. Creacion de la tabla mesas
```sql
CREATE TABLE mesas (
    id INT IDENTITY(1,1) PRIMARY KEY,
    sede_id INT NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    descripcion VARCHAR(255),
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT fk_mesas_sede_id FOREIGN KEY (sede_id) REFERENCES sedes(id)
);
```
_Evidencia:_ ![paso-8](Reguistro%20visual/serpaso-8.png)

### 9. Creacion de la tabla clientes
```sql
CREATE TABLE clientes (
    id INT IDENTITY(1,1) PRIMARY KEY,
    tipo_documento VARCHAR(20) NOT NULL,
    numero_documento VARCHAR(30) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(150),
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT uq_clientes_numero_documento UNIQUE (numero_documento)
);
```
_Evidencia:_ ![paso-9](Reguistro%20visual/serpaso-9.png)

### 10. Creacion de la tabla reservas
```sql
CREATE TABLE reservas (
    id INT IDENTITY(1,1) PRIMARY KEY,
    cliente_id INT NOT NULL,
    mesa_id INT NOT NULL,
    fecha_inicio DATETIME2 NOT NULL,
    fecha_fin DATETIME2,
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    observaciones VARCHAR(255),
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT fk_reservas_cliente_id FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    CONSTRAINT fk_reservas_mesa_id FOREIGN KEY (mesa_id) REFERENCES mesas(id)
);
```
_Evidencia:_ ![paso-10](Reguistro%20visual/serpaso-10.png)

### 11. Creacion de la tabla productos
```sql
CREATE TABLE productos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    sku VARCHAR(30) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    descripcion VARCHAR(255),
    precio DECIMAL(12,2) NOT NULL,
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT uq_productos_sku UNIQUE (sku)
);
```
_Evidencia:_ ![paso-11](Reguistro%20visual/serpaso-11.png)

### 12. Creacion de la tabla insumos
```sql
CREATE TABLE insumos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    codigo VARCHAR(30) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    unidad_medida VARCHAR(20) NOT NULL,
    stock_minimo DECIMAL(12,2),
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT uq_insumos_codigo UNIQUE (codigo)
);
```
_Evidencia:_ ![paso-12](Reguistro%20visual/serpaso-12.png)

### 13. Creacion de la tabla recetas_insumos
```sql
CREATE TABLE recetas_insumos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    producto_id INT NOT NULL,
    insumo_id INT NOT NULL,
    cantidad DECIMAL(12,2) NOT NULL,
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT uq_recetas_insumos_producto_id_insumo_id UNIQUE (producto_id, insumo_id),
    CONSTRAINT fk_recetas_insumos_producto_id FOREIGN KEY (producto_id) REFERENCES productos(id),
    CONSTRAINT fk_recetas_insumos_insumo_id FOREIGN KEY (insumo_id) REFERENCES insumos(id)
);
```
_Evidencia:_ ![paso-13](Reguistro%20visual/serpaso-13.png)

### 14. Creacion de la tabla domiciliarios
```sql
CREATE TABLE domiciliarios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    descripcion VARCHAR(255),
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME()
);
```
_Evidencia:_ ![paso-14](Reguistro%20visual/serpaso-14.png)

### 15. Creacion de la tabla pedidos
```sql
CREATE TABLE pedidos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    cliente_id INT NOT NULL,
    sede_id INT NOT NULL,
    mesa_id INT,
    canal VARCHAR(20) NOT NULL,
    fecha DATETIME2 NOT NULL,
    subtotal DECIMAL(12,2) NOT NULL,
    total DECIMAL(12,2) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT fk_pedidos_cliente_id FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    CONSTRAINT fk_pedidos_sede_id FOREIGN KEY (sede_id) REFERENCES sedes(id),
    CONSTRAINT fk_pedidos_mesa_id FOREIGN KEY (mesa_id) REFERENCES mesas(id)
);
```
_Evidencia:_ ![paso-15](Reguistro%20visual/serpaso-15.png)

### 16. Creacion de la tabla detalles_pedidos
```sql
CREATE TABLE detalles_pedidos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    pedido_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad DECIMAL(12,2) NOT NULL,
    valor_unitario DECIMAL(12,2) NOT NULL,
    total DECIMAL(12,2) NOT NULL,
    observaciones VARCHAR(255),
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT fk_detalles_pedidos_pedido_id FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    CONSTRAINT fk_detalles_pedidos_producto_id FOREIGN KEY (producto_id) REFERENCES productos(id)
);
```
_Evidencia:_ ![paso-16](Reguistro%20visual/serpaso-16.png)

### 17. Creacion de la tabla pagos
```sql
CREATE TABLE pagos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    pedido_id INT NOT NULL,
    metodo VARCHAR(30) NOT NULL,
    monto DECIMAL(12,2) NOT NULL,
    fecha DATETIME2 NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT fk_pagos_pedido_id FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
);
```
_Evidencia:_ ![paso-17](Reguistro%20visual/serpaso-17.png)

### 18. Creacion de la tabla entregas
```sql
CREATE TABLE entregas (
    id INT IDENTITY(1,1) PRIMARY KEY,
    pedido_id INT NOT NULL,
    domiciliario_id INT NOT NULL,
    fecha_inicio DATETIME2,
    fecha_fin DATETIME2,
    total DECIMAL(12,2),
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    observaciones VARCHAR(255),
    is_active VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (is_active IN ('ACTIVE','INACTIVE')),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT uq_entregas_pedido_id UNIQUE (pedido_id),
    CONSTRAINT fk_entregas_pedido_id FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    CONSTRAINT fk_entregas_domiciliario_id FOREIGN KEY (domiciliario_id) REFERENCES domiciliarios(id)
);
```
_Evidencia:_ ![paso-18](Reguistro%20visual/serpaso-18.png)

### Diagrma de la base de datos BrasaGoserver en Microsoft SQL Server

_Evidencia:_ ![paso-19](Reguistro%20visual/Diagramaserver.png)

---

## Motor: Oracle

### 0. Creación de la base de datos

```sql
CREATE USER BrasaGo IDENTIFIED BY "5550101";
GRANT CONNECT, RESOURCE, DBA TO BrasaGo;
```
_Evidencia:_ ![paso-0](Reguistro%20visual/orapaso-0.png)

### 1. Creación de la tabla users

```sql
CREATE TABLE users (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    username VARCHAR2(50) NOT NULL,
    email VARCHAR2(150) NOT NULL,
    password VARCHAR2(255) NOT NULL,
    avatar VARCHAR2(255),
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT uq_users_username UNIQUE (username),
    CONSTRAINT uq_users_email UNIQUE (email),
    CONSTRAINT ck_users_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-1](Reguistro%20visual/orapaso-1.png)

### 2. Creación de la tabla roles
```sql
CREATE TABLE roles (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    name VARCHAR2(50) NOT NULL,
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT uq_roles_name UNIQUE (name),
    CONSTRAINT ck_roles_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-2](Reguistro%20visual/orapaso-2.png)

### 3. Creación de la tabla resources
```sql
CREATE TABLE resources (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    path VARCHAR2(255) NOT NULL,
    method VARCHAR2(10) NOT NULL,
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT uq_resources_path_method UNIQUE (path, method),
    CONSTRAINT ck_resources_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-3](Reguistro%20visual/orapaso-3.png)

### 4. Creación de la tabla role_users
```sql
CREATE TABLE role_users (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    role_id NUMBER NOT NULL,
    user_id NUMBER NOT NULL,
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT uq_role_users_role_id_user_id UNIQUE (role_id, user_id),
    CONSTRAINT fk_role_users_role_id FOREIGN KEY (role_id) REFERENCES roles(id),
    CONSTRAINT fk_role_users_user_id FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT ck_role_users_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-4](Reguistro%20visual/orapaso-4.png)

### 5. Creación de la tabla resource_roles
```sql
CREATE TABLE resource_roles (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    resource_id NUMBER NOT NULL,
    role_id NUMBER NOT NULL,
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT uq_resource_roles_resource_id_role_id UNIQUE (resource_id, role_id),
    CONSTRAINT fk_resource_roles_resource_id FOREIGN KEY (resource_id) REFERENCES resources(id),
    CONSTRAINT fk_resource_roles_role_id FOREIGN KEY (role_id) REFERENCES roles(id),
    CONSTRAINT ck_resource_roles_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-5](Reguistro%20visual/orapaso-5.png)

### 6. Creación de la tabla refresh_tokens
```sql
CREATE TABLE refresh_tokens (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    user_id NUMBER NOT NULL,
    token VARCHAR2(500) NOT NULL,
    device_info VARCHAR2(255) NOT NULL,
    is_valid VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    expires_at DATE NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT fk_refresh_tokens_user_id FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT ck_refresh_tokens_is_valid CHECK (is_valid IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-6](Reguistro%20visual/orapaso-6.png)

### 7. Creación de la tabla sedes
```sql
CREATE TABLE sedes (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    nombre VARCHAR2(100) NOT NULL,
    descripcion VARCHAR2(255),
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT ck_sedes_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-7](Reguistro%20visual/orapaso-7.png)

### 8. Creación de la tabla mesas
```sql
CREATE TABLE mesas (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    sede_id NUMBER NOT NULL,
    nombre VARCHAR2(50) NOT NULL,
    descripcion VARCHAR2(255),
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT fk_mesas_sede_id FOREIGN KEY (sede_id) REFERENCES sedes(id),
    CONSTRAINT ck_mesas_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-8](Reguistro%20visual/orapaso-8.png)

### 9. Creación de la tabla clientes
```sql
CREATE TABLE clientes (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    tipo_documento VARCHAR2(20) NOT NULL,
    numero_documento VARCHAR2(30) NOT NULL,
    nombre VARCHAR2(150) NOT NULL,
    telefono VARCHAR2(20),
    email VARCHAR2(150),
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT uq_clientes_numero_documento UNIQUE (numero_documento),
    CONSTRAINT ck_clientes_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-9](Reguistro%20visual/orapaso-9.png)

### 10. Creación de la tabla reservas
```sql
CREATE TABLE reservas (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    cliente_id NUMBER NOT NULL,
    mesa_id NUMBER NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    estado VARCHAR2(20) DEFAULT 'PENDIENTE' NOT NULL,
    observaciones VARCHAR2(255),
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT fk_reservas_cliente_id FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    CONSTRAINT fk_reservas_mesa_id FOREIGN KEY (mesa_id) REFERENCES mesas(id),
    CONSTRAINT ck_reservas_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-10](Reguistro%20visual/orapaso-10.png)

### 11. Creación de la tabla productos
```sql
CREATE TABLE productos (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    sku VARCHAR2(30) NOT NULL,
    nombre VARCHAR2(150) NOT NULL,
    descripcion VARCHAR2(255),
    precio NUMBER(12,2) NOT NULL,
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT uq_productos_sku UNIQUE (sku),
    CONSTRAINT ck_productos_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-11](Reguistro%20visual/orapaso-11.png)

### 12. Creación de la tabla insumos
```sql
CREATE TABLE insumos (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    codigo VARCHAR2(30) NOT NULL,
    nombre VARCHAR2(150) NOT NULL,
    unidad_medida VARCHAR2(20) NOT NULL,
    stock_minimo NUMBER(12,2),
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT uq_insumos_codigo UNIQUE (codigo),
    CONSTRAINT ck_insumos_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-12](Reguistro%20visual/orapaso-12.png)

### 13. Creación de la tabla recetas_insumos
```sql
CREATE TABLE recetas_insumos (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    producto_id NUMBER NOT NULL,
    insumo_id NUMBER NOT NULL,
    cantidad NUMBER(12,2) NOT NULL,
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT uq_recetas_insumos_producto_id_insumo_id UNIQUE (producto_id, insumo_id),
    CONSTRAINT fk_recetas_insumos_producto_id FOREIGN KEY (producto_id) REFERENCES productos(id),
    CONSTRAINT fk_recetas_insumos_insumo_id FOREIGN KEY (insumo_id) REFERENCES insumos(id),
    CONSTRAINT ck_recetas_insumos_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-13](Reguistro%20visual/orapaso-13.png)

### 14. Creación de la tabla domiciliarios
```sql
CREATE TABLE domiciliarios (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    nombre VARCHAR2(150) NOT NULL,
    descripcion VARCHAR2(255),
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT ck_domiciliarios_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-14](Reguistro%20visual/orapaso-14.png)

### 15. Creación de la tabla pedidos
```sql
CREATE TABLE pedidos (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    cliente_id NUMBER NOT NULL,
    sede_id NUMBER NOT NULL,
    mesa_id NUMBER,
    canal VARCHAR2(20) NOT NULL,
    fecha DATE NOT NULL,
    subtotal NUMBER(12,2) NOT NULL,
    total NUMBER(12,2) NOT NULL,
    estado VARCHAR2(20) DEFAULT 'PENDIENTE' NOT NULL,
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT fk_pedidos_cliente_id FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    CONSTRAINT fk_pedidos_sede_id FOREIGN KEY (sede_id) REFERENCES sedes(id),
    CONSTRAINT fk_pedidos_mesa_id FOREIGN KEY (mesa_id) REFERENCES mesas(id),
    CONSTRAINT ck_pedidos_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-15](Reguistro%20visual/orapaso-15.png)

### 16. Creación de la tabla detalles_pedidos
```sql
CREATE TABLE detalles_pedidos (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    pedido_id NUMBER NOT NULL,
    producto_id NUMBER NOT NULL,
    cantidad NUMBER(12,2) NOT NULL,
    valor_unitario NUMBER(12,2) NOT NULL,
    total NUMBER(12,2) NOT NULL,
    observaciones VARCHAR2(255),
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT fk_detalles_pedidos_pedido_id FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    CONSTRAINT fk_detalles_pedidos_producto_id FOREIGN KEY (producto_id) REFERENCES productos(id),
    CONSTRAINT ck_detalles_pedidos_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-16](Reguistro%20visual/orapaso-16.png)

### 17. Creación de la tabla pagos
```sql
CREATE TABLE pagos (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    pedido_id NUMBER NOT NULL,
    metodo VARCHAR2(30) NOT NULL,
    monto NUMBER(12,2) NOT NULL,
    fecha DATE NOT NULL,
    estado VARCHAR2(20) DEFAULT 'PENDIENTE' NOT NULL,
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT fk_pagos_pedido_id FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    CONSTRAINT ck_pagos_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-17](Reguistro%20visual/orapaso-17.png)

### 18. Creación de la tabla entregas
```sql
CREATE TABLE entregas (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    pedido_id NUMBER NOT NULL,
    domiciliario_id NUMBER NOT NULL,
    fecha_inicio DATE,
    fecha_fin DATE,
    total NUMBER(12,2),
    estado VARCHAR2(20) DEFAULT 'PENDIENTE' NOT NULL,
    observaciones VARCHAR2(255),
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT uq_entregas_pedido_id UNIQUE (pedido_id),
    CONSTRAINT fk_entregas_pedido_id FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    CONSTRAINT fk_entregas_domiciliario_id FOREIGN KEY (domiciliario_id) REFERENCES domiciliarios(id),
    CONSTRAINT ck_entregas_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-18](Reguistro%20visual/orapaso-18.png)

### Diagrma de la base de datos BrasaGo en DBeaver 

_Evidencia:_ ![paso-20](Reguistro%20visual/Diagramaora.png)

## Ejecución por Oracle SQL Developer

### 0. Creación de la base de datos

```sql
CREATE USER brasagodeve IDENTIFIED BY "5550101";
GRANT CONNECT, RESOURCE, DBA TO ;
```
_Evidencia:_ ![paso-0](Reguistro%20visual/devepaso-0.png)

### 1. Creación de la tabla users

```sql
CREATE TABLE users (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    username VARCHAR2(50) NOT NULL,
    email VARCHAR2(150) NOT NULL,
    password VARCHAR2(255) NOT NULL,
    avatar VARCHAR2(255),
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT uq_users_username UNIQUE (username),
    CONSTRAINT uq_users_email UNIQUE (email),
    CONSTRAINT ck_users_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-1](Reguistro%20visual/devepaso-1.png)

### 2. Creación de la tabla roles
```sql
CREATE TABLE roles (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    name VARCHAR2(50) NOT NULL,
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT uq_roles_name UNIQUE (name),
    CONSTRAINT ck_roles_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-2](Reguistro%20visual/devepaso-2.png)

### 3. Creación de la tabla resources
```sql
CREATE TABLE resources (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    path VARCHAR2(255) NOT NULL,
    method VARCHAR2(10) NOT NULL,
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT uq_resources_path_method UNIQUE (path, method),
    CONSTRAINT ck_resources_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-3](Reguistro%20visual/devepaso-3.png)

### 4. Creación de la tabla role_users
```sql
CREATE TABLE role_users (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    role_id NUMBER NOT NULL,
    user_id NUMBER NOT NULL,
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT uq_role_users_role_id_user_id UNIQUE (role_id, user_id),
    CONSTRAINT fk_role_users_role_id FOREIGN KEY (role_id) REFERENCES roles(id),
    CONSTRAINT fk_role_users_user_id FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT ck_role_users_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-4](Reguistro%20visual/devepaso-4.png)

### 5. Creación de la tabla resource_roles
```sql
CREATE TABLE resource_roles (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    resource_id NUMBER NOT NULL,
    role_id NUMBER NOT NULL,
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT uq_resource_roles_resource_id_role_id UNIQUE (resource_id, role_id),
    CONSTRAINT fk_resource_roles_resource_id FOREIGN KEY (resource_id) REFERENCES resources(id),
    CONSTRAINT fk_resource_roles_role_id FOREIGN KEY (role_id) REFERENCES roles(id),
    CONSTRAINT ck_resource_roles_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-5](Reguistro%20visual/devepaso-5.png)

### 6. Creación de la tabla refresh_tokens
```sql
CREATE TABLE refresh_tokens (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    user_id NUMBER NOT NULL,
    token VARCHAR2(500) NOT NULL,
    device_info VARCHAR2(255) NOT NULL,
    is_valid VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    expires_at DATE NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT fk_refresh_tokens_user_id FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT ck_refresh_tokens_is_valid CHECK (is_valid IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-6](Reguistro%20visual/devepaso-6.png)

### 7. Creación de la tabla sedes
```sql
CREATE TABLE sedes (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    nombre VARCHAR2(100) NOT NULL,
    descripcion VARCHAR2(255),
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT ck_sedes_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-7](Reguistro%20visual/devepaso-7.png)

### 8. Creación de la tabla mesas
```sql
CREATE TABLE mesas (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    sede_id NUMBER NOT NULL,
    nombre VARCHAR2(50) NOT NULL,
    descripcion VARCHAR2(255),
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT fk_mesas_sede_id FOREIGN KEY (sede_id) REFERENCES sedes(id),
    CONSTRAINT ck_mesas_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-8](Reguistro%20visual/devepaso-8.png)

### 9. Creación de la tabla clientes
```sql
CREATE TABLE clientes (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    tipo_documento VARCHAR2(20) NOT NULL,
    numero_documento VARCHAR2(30) NOT NULL,
    nombre VARCHAR2(150) NOT NULL,
    telefono VARCHAR2(20),
    email VARCHAR2(150),
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT uq_clientes_numero_documento UNIQUE (numero_documento),
    CONSTRAINT ck_clientes_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-9](Reguistro%20visual/devepaso-9.png)

### 10. Creación de la tabla reservas
```sql
CREATE TABLE reservas (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    cliente_id NUMBER NOT NULL,
    mesa_id NUMBER NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    estado VARCHAR2(20) DEFAULT 'PENDIENTE' NOT NULL,
    observaciones VARCHAR2(255),
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT fk_reservas_cliente_id FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    CONSTRAINT fk_reservas_mesa_id FOREIGN KEY (mesa_id) REFERENCES mesas(id),
    CONSTRAINT ck_reservas_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-10](Reguistro%20visual/devepaso-10.png)

### 11. Creación de la tabla productos
```sql
CREATE TABLE productos (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    sku VARCHAR2(30) NOT NULL,
    nombre VARCHAR2(150) NOT NULL,
    descripcion VARCHAR2(255),
    precio NUMBER(12,2) NOT NULL,
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT uq_productos_sku UNIQUE (sku),
    CONSTRAINT ck_productos_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-11](Reguistro%20visual/devepaso-11.png)

### 12. Creación de la tabla insumos
```sql
CREATE TABLE insumos (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    codigo VARCHAR2(30) NOT NULL,
    nombre VARCHAR2(150) NOT NULL,
    unidad_medida VARCHAR2(20) NOT NULL,
    stock_minimo NUMBER(12,2),
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT uq_insumos_codigo UNIQUE (codigo),
    CONSTRAINT ck_insumos_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-12](Reguistro%20visual/devepaso-12.png)

### 13. Creación de la tabla recetas_insumos
```sql
CREATE TABLE recetas_insumos (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    producto_id NUMBER NOT NULL,
    insumo_id NUMBER NOT NULL,
    cantidad NUMBER(12,2) NOT NULL,
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT uq_recetas_insumos_producto_id_insumo_id UNIQUE (producto_id, insumo_id),
    CONSTRAINT fk_recetas_insumos_producto_id FOREIGN KEY (producto_id) REFERENCES productos(id),
    CONSTRAINT fk_recetas_insumos_insumo_id FOREIGN KEY (insumo_id) REFERENCES insumos(id),
    CONSTRAINT ck_recetas_insumos_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-13](Reguistro%20visual/devepaso-13.png)

### 14. Creación de la tabla domiciliarios
```sql
CREATE TABLE domiciliarios (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    nombre VARCHAR2(150) NOT NULL,
    descripcion VARCHAR2(255),
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT ck_domiciliarios_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-14](Reguistro%20visual/devepaso-14.png)

### 15. Creación de la tabla pedidos
```sql
CREATE TABLE pedidos (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    cliente_id NUMBER NOT NULL,
    sede_id NUMBER NOT NULL,
    mesa_id NUMBER,
    canal VARCHAR2(20) NOT NULL,
    fecha DATE NOT NULL,
    subtotal NUMBER(12,2) NOT NULL,
    total NUMBER(12,2) NOT NULL,
    estado VARCHAR2(20) DEFAULT 'PENDIENTE' NOT NULL,
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT fk_pedidos_cliente_id FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    CONSTRAINT fk_pedidos_sede_id FOREIGN KEY (sede_id) REFERENCES sedes(id),
    CONSTRAINT fk_pedidos_mesa_id FOREIGN KEY (mesa_id) REFERENCES mesas(id),
    CONSTRAINT ck_pedidos_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-15](Reguistro%20visual/devepaso-15.png)

### 16. Creación de la tabla detalles_pedidos
```sql
CREATE TABLE detalles_pedidos (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    pedido_id NUMBER NOT NULL,
    producto_id NUMBER NOT NULL,
    cantidad NUMBER(12,2) NOT NULL,
    valor_unitario NUMBER(12,2) NOT NULL,
    total NUMBER(12,2) NOT NULL,
    observaciones VARCHAR2(255),
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT fk_detalles_pedidos_pedido_id FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    CONSTRAINT fk_detalles_pedidos_producto_id FOREIGN KEY (producto_id) REFERENCES productos(id),
    CONSTRAINT ck_detalles_pedidos_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-16](Reguistro%20visual/devepaso-16.png)

### 17. Creación de la tabla pagos
```sql
CREATE TABLE pagos (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    pedido_id NUMBER NOT NULL,
    metodo VARCHAR2(30) NOT NULL,
    monto NUMBER(12,2) NOT NULL,
    fecha DATE NOT NULL,
    estado VARCHAR2(20) DEFAULT 'PENDIENTE' NOT NULL,
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT fk_pagos_pedido_id FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    CONSTRAINT ck_pagos_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-17](Reguistro%20visual/devepaso-17.png)

### 18. Creación de la tabla entregas
```sql
CREATE TABLE entregas (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    pedido_id NUMBER NOT NULL,
    domiciliario_id NUMBER NOT NULL,
    fecha_inicio DATE,
    fecha_fin DATE,
    total NUMBER(12,2),
    estado VARCHAR2(20) DEFAULT 'PENDIENTE' NOT NULL,
    observaciones VARCHAR2(255),
    is_active VARCHAR2(10) DEFAULT 'ACTIVE' NOT NULL,
    created_at DATE DEFAULT SYSDATE NOT NULL,
    updated_at DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT uq_entregas_pedido_id UNIQUE (pedido_id),
    CONSTRAINT fk_entregas_pedido_id FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    CONSTRAINT fk_entregas_domiciliario_id FOREIGN KEY (domiciliario_id) REFERENCES domiciliarios(id),
    CONSTRAINT ck_entregas_is_active CHECK (is_active IN ('ACTIVE','INACTIVE'))
);
```
_Evidencia:_ ![paso-18](Reguistro%20visual/devepaso-18.png)

### Diagrma de la base de datos BrasaGo en Oracle SQL Developer

_Evidencia:_ ![paso-20](Reguistro%20visual/Diagramadeve.png)

## Firma

**Elkin Eliecer Aguas Giraldo**
Estudiante de Ingeniería de Sistemas — Facultad de Ingeniería — Universidad de La Guajira
Rol: responsable de la creacion configuracion y documentacion de la base de datos
Fecha del informe: 16/09/26