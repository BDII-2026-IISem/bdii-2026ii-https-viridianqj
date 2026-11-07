# Bitácora del frontend de BrasaGo (Angular)

Registro del avance del frontend de **BrasaGo** (sistema omnicanal de restaurante) siguiendo la guía **Angular 20 · consumo de APIs Django** de Tecnogua, sin la parte de autenticación. Cada paso resume qué se hizo, qué se adaptó respecto a la guía, cómo se verificó y qué capturas lo respaldan.

| | |
|---|---|
| **Proyecto** | BrasaGo, Proyectos Integradores 2026-II (Desarrollo Web) |
| **Autor** | Elkin Eliecer Aguas Giraldo |
| **Alcance** | Estructura por componentes, plantilla (encabezado, menú lateral y pie), y listado ("mostrar") de las 9 entidades del negocio desde la API Django |
| **Guía de referencia** | [Angular 20 · APIs con Django](https://tecnogua.com/academic/site/frontend/angular20/apis_django/), con la instalación y el cliente Django del mismo sitio |
| **Backend consumido** | API REST de BrasaGo (Django 5.2 + DRF), `http://127.0.0.1:8000/api` |
| **Pruebas** | 36 pruebas OK en 19 archivos (`ng test`), ver sección 7 |
| **Última actualización** | 7 de noviembre de 2026 (ISS-11 en curso) |

---

## 1. Estado general

ISS = issue de la guía frontend2026. Extra BrasaGo = pantalla propia del dominio, sin ISS en la guía. Transversal = pruebas, build, repositorio y datos de ejemplo.

| Paso | Tema | Estado |
|---|---|---|
| F-00 · ISS-00 | Requisitos y versiones | Bien |
| F-01 · ISS-01 | Proyecto Angular, PrimeNG y Tailwind | Bien |
| F-02 · ISS-01A | Plantilla: encabezado, menú lateral y pie | Bien |
| F-03 · ISS-01 | Arranque de la aplicación | Bien |
| F-04 · ISS-02 | Acceso a la API en desarrollo (login automático e interceptor) | Reemplazado por F-22 |
| F-05 · ISS-02 | Base del consumo: `BaseApi`, modelos y estado | Bien |
| F-06 · ISS-03 | Listado de clientes | Bien |
| F-07 · ISS-01 | Licencia de PrimeNG | Bien |
| F-08 · ISS-05 | Listado de productos | Bien |
| F-09 · ISS-06 | Listado de pedidos con detalle desplegable | Bien |
| F-10 · Extra BrasaGo | Listados de pagos y reservas | Bien |
| F-11 · Extra BrasaGo | Listados de insumos, recetas, domiciliarios y entregas | Bien |
| F-12 · Transversal | Pruebas automáticas | Bien |
| F-13 · Transversal | Build de producción | Bien |
| F-14 · Transversal | Repositorio y manejo de secretos | Bien |
| F-15 · Transversal | Datos de ejemplo para las pantallas | Bien |
| F-16 · ISS-03 | CRUD de clientes (alta, edición, baja y búsqueda) | Bien |
| F-17 · ISS-05 | CRUD de productos (alta, edición, baja y búsqueda) | Bien |
| F-18 · Transversal | Pruebas después de los CRUD | Bien |
| F-19 · ISS-06 | Registro de pedidos desde la pantalla | Bien |
| F-20 · ISS-07 | Detalle de pedido y anulación (parcial: sin panel) | Bien |
| F-21 · ISS-07 | ISS-07 completado: líneas de pedido y panel del día | Bien |
| F-22 · ISS-08 | Login con JWT, sesión, interceptores y perfil | Bien |
| F-23 · ISS-01B | Layout y menú responsivo (adaptado) | Bien |
| F-24 · ISS-02 a ISS-08 | Revisión contra la guía y correcciones de validación y redirección | Bien |
| F-25 · ISS-08 a ISS-09 | Permisos por recurso, guards y menú filtrado | Bien |
| F-26 · Transversal | Identidad visual de BrasaGo (tema naranja, logo y capas CSS) | Bien |
| F-27 · ISS-10 | Administración RBAC: usuarios, roles, recursos, asignaciones, permisos por rol, ver permisos y menú Seguridad | Bien |
| F-28 · ISS-11 | Build de producción, presupuestos, calidad, responsive, accesibilidad y recorrido de verificación (pasos 1 a 3 y 11 a 13) | Parcial |
| F-29 · ISS-03 | Reactivar clientes desde la pantalla (corrección encontrada en ISS-11) | Bien |
| F-30 · ISS-11 | Roles y permisos en una sola pantalla, menú de Seguridad, botón de menú oculto en login y verificación del rol mesero | Parcial |

---

## 2. Entorno y versiones

| Componente | Versión |
|---|---|
| Node.js | 22.23.4 |
| Angular | 22.2 (componentes *standalone*, *signals*, archivos SSR) |
| PrimeNG | 22.1.4 con tema Aura (`@primeuix/themes`) |
| PrimeIcons | 8 |
| Tailwind CSS | 4 (vía `.postcssrc.json` y `@tailwindcss/postcss`) |
| Sistema | Ubuntu sobre WSL (Windows) |

La guía usa Angular 20 y PrimeNG 20. Se mantuvo el proyecto Angular 22 que ya existía.

---

## 3. Decisiones de diseño y adaptaciones frente a la guía

| Tema | Guía | BrasaGo | Motivo |
|---|---|---|---|
| Versión de Angular | 20 | 22.2 | Se siguió con el proyecto ya creado |
| Selector de ordenamiento | `p-sortIcon` | `p-sort-icon` | Nombre vigente en PrimeNG 22 |
| Licencia de PrimeNG | no existe | `providePrimeNG({ license })` con la licencia gratuita Community | PrimeNG 22 muestra un aviso rojo sin licencia |
| Autenticación | pantalla de login | omitida; login automático solo en desarrollo | Lo pidió el alcance del trabajo; la API exige JWT |
| Credenciales y licencia | no aplica | `dev-credentials.ts` y `primeng-license.ts` fuera de git, con archivos `.example.ts` | No publicar secretos en el repositorio |
| Entidades | Clientes, productos, ventas | Clientes, productos, pedidos, pagos, reservas, insumos, recetas, domiciliarios y entregas | Son las entidades del negocio de BrasaGo |
| Detalle del pedido | no existe | Fila desplegable con las líneas (`details`) | La API devuelve el detalle dentro del pedido |
| Sedes y mesas | no aplica | Sin pantalla | La API no tiene endpoints para ellas; se crean en Django Admin o con el shell de Django |
| Moneda y fechas | genérico | `CurrencyPipe` en COP sin decimales y `DatePipe` `dd/MM/yyyy HH:mm` | Formato local |
| Idioma de la página | no aplica | `<html lang="es" translate="no">` | El traductor de Chrome dañaba la tabla (ver sección 8) |

---

## 4. Estructura actual

```
frontend/
├── .postcssrc.json
├── package.json
└── src/
    ├── index.html                      (lang="es", translate="no")
    ├── styles.css                      (Tailwind 4, PrimeIcons)
    ├── environments/
    │   ├── environment.ts              (apiUrl, appName)
    │   ├── dev-credentials.example.ts  (el real queda fuera de git)
    │   └── primeng-license.example.ts  (el real queda fuera de git)
    └── app/
        ├── app.ts / app.html           (plantilla: header + aside + router-outlet + footer)
        ├── app.config.ts               (router, HttpClient con interceptor, PrimeNG)
        ├── app.routes.ts               (9 rutas con carga perezosa)
        ├── core/                       dev-auth.ts, dev-auth.interceptor.ts
        ├── shared/                     state-severity.ts
        ├── models/business/            client, product, order, payment, reservation,
        │                               supply, recipe, courier, delivery
        ├── models/security/            status, user, role, resource, role-user, resource-role
        ├── services/                   api.ts (BaseApi), crud.ts (CrudApi)
        │   ├── business/               un servicio por entidad
        │   └── security/               user, role, resource, role-user, resource-role (CrudApi)
        └── components/
            ├── layout/                 header, aside, footer
            ├── admin/users/user-list/  pantalla de usuarios (ISS-10)
            └── <entidad>/getall/       .html, .css, .ts y .spec.ts por pantalla
```

### Rutas del menú

| Grupo | Opción | Ruta | Endpoint |
|---|---|---|---|
| Negocio | Clientes | `/clientes` | `/api/clientes/` |
| Negocio | Productos | `/productos` | `/api/productos/` |
| Negocio | Pedidos | `/pedidos` | `/api/pedidos/` |
| Negocio | Pagos | `/pagos` | `/api/pagos/` |
| Salón | Reservas | `/reservas` | `/api/reservas/` |
| Cocina | Insumos | `/insumos` | `/api/insumos/` |
| Cocina | Recetas | `/recetas` | `/api/recetas/` |
| Domicilios | Domiciliarios | `/domiciliarios` | `/api/domiciliarios/` |
| Domicilios | Entregas | `/entregas` | `/api/entregas/` |

Grupo Seguridad (ISS-10): Usuarios (`/admin/usuarios`), Roles (`/admin/roles`), Recursos (`/admin/recursos`), Asignaciones (`/admin/asignaciones`) y Permisos por rol (`/admin/permisos`). Cada ruta está protegida con `permissionGuard`.

---

## 5. Cómo funciona un componente

Angular trabaja por componentes. `<app-root>` es el componente raíz y cada componente tiene cuatro archivos:

| Archivo | Para qué sirve |
|---|---|
| `.html` | La plantilla: lo que se pinta |
| `.css` | Los estilos del componente |
| `.ts` | El código: datos, métodos y la decoración `@Component` |
| `.spec.ts` | Las pruebas del componente |

Dentro de `@Component`, `standalone: true` indica que el componente no necesita un módulo y declara en `imports` lo que usa en su plantilla (tabla, botón, tag, pipes). `selector` es la etiqueta con la que se usa, `templateUrl` apunta al HTML y `styleUrl` al CSS.

**Patrón de cada entidad:** modelo (interfaz) → servicio que extiende `BaseApi<T>` con la ruta → componente `getall` (señales `items`, `loading` y `error`, y una `p-table`) → ruta con carga perezosa.

---

## 6. Detalle por paso

### F-00 · ISS-00 · Requisitos y versiones

Se comprobaron las versiones de Angular CLI, Node y npm, y que el backend responde en el puerto 8000 con el usuario de desarrollo.

![F-00 Angular CLI 22.2.4, Node 22.23.4 y npm 10.9.9](Reguistro%20visual/ISS-00/F-00-01-versiones.png)
*Angular CLI 22.2.4, Node 22.23.4 y npm 10.9.9*

![F-00 Backend en marcha y recursos concedidos al usuario de desarrollo](Reguistro%20visual/ISS-00/F-00-02-backend-en-marcha.png)
*Backend en marcha y recursos concedidos al usuario de desarrollo*


### F-01 · ISS-01 · Proyecto Angular, PrimeNG y Tailwind

Se creó el proyecto `front-brasago` con Angular 22 (CSS, enrutamiento y SSR), y se instalaron PrimeNG, `@primeuix/themes`, PrimeIcons y Tailwind 4 (configurado en `.postcssrc.json` y `styles.css`). Se generaron los `environments` con la URL de la API.

![F-01 `ng new front-brasago`](Reguistro%20visual/ISS-01/F-01-01-ng-new.png)
*`ng new front-brasago`*

![F-01 Archivos creados por `ng new`](Reguistro%20visual/ISS-01/F-01-02-ng-new-archivos.png)
*Archivos creados por `ng new`*

![F-01 Instalación de PrimeNG, temas e iconos](Reguistro%20visual/ISS-01/F-01-03-instalar-primeng.png)
*Instalación de PrimeNG, temas e iconos*

![F-01 Instalación de Tailwind y `.postcssrc.json`](Reguistro%20visual/ISS-01/F-01-04-instalar-tailwind.png)
*Instalación de Tailwind y `.postcssrc.json`*

![F-01 `styles.css` con Tailwind y PrimeIcons](Reguistro%20visual/ISS-01/F-01-05-styles-css.png)
*`styles.css` con Tailwind y PrimeIcons*

![F-01 `ng generate environments`](Reguistro%20visual/ISS-01/F-01-06-generate-environments.png)
*`ng generate environments`*

![F-01 `environment.ts` con la URL de la API](Reguistro%20visual/ISS-01/F-01-07-environment-ts.png)
*`environment.ts` con la URL de la API*

![F-01 `angular.json`](Reguistro%20visual/ISS-01/F-01-08-angular-json.png)
*`angular.json`*

![F-01 `app.ts` inicial](Reguistro%20visual/ISS-01/F-01-09-app-ts-inicial.png)
*`app.ts` inicial*

![F-01 `app.config.ts` con el tema Aura de PrimeNG](Reguistro%20visual/ISS-01/F-01-10-app-config-primeng.png)
*`app.config.ts` con el tema Aura de PrimeNG*


### F-02 · ISS-01A · Plantilla: encabezado, menú lateral y pie

Se generaron los componentes `header`, `aside` y `footer` en `components/layout/`. El menú lateral usa `PanelMenu` de PrimeNG con cuatro grupos (Negocio, Salón, Cocina y Domicilios) y `routerLink` en cada opción. `app.html` los organiza con Tailwind: encabezado arriba, menú a la izquierda, contenido en el centro (`router-outlet`) y pie abajo.

![F-02 Generación de los tres componentes con `ng generate component`](Reguistro%20visual/ISS-01A/F-02-01-ng-generate-layout.png)
*Generación de los tres componentes con `ng generate component`*

![F-02 `header.ts`](Reguistro%20visual/ISS-01A/F-02-02-header-ts.png)
*`header.ts`*

![F-02 `header.html`](Reguistro%20visual/ISS-01A/F-02-03-header-html.png)
*`header.html`*

![F-02 `footer.ts`](Reguistro%20visual/ISS-01A/F-02-04-footer-ts.png)
*`footer.ts`*

![F-02 `footer.html`](Reguistro%20visual/ISS-01A/F-02-05-footer-html.png)
*`footer.html`*

![F-02 `aside.ts` con los grupos del menú](Reguistro%20visual/ISS-01A/F-02-06-aside-ts.png)
*`aside.ts` con los grupos del menú*

![F-02 `aside.html` con `p-panelmenu`](Reguistro%20visual/ISS-01A/F-02-07-aside-html.png)
*`aside.html` con `p-panelmenu`*

![F-02 `app.ts` importando los tres componentes](Reguistro%20visual/ISS-01A/F-02-08-app-ts.png)
*`app.ts` importando los tres componentes*

![F-02 `app.html` con la estructura de la página](Reguistro%20visual/ISS-01A/F-02-09-app-html.png)
*`app.html` con la estructura de la página*

![F-02 Plantilla completa en el navegador](Reguistro%20visual/ISS-01A/F-02-10-plantilla-navegador.png)
*Plantilla completa en el navegador*


### F-03 · ISS-01 · Arranque de la aplicación

Primera ejecución con `npm start`: la aplicación abre en `localhost:4200`.

![F-03 Página inicial de Angular funcionando](Reguistro%20visual/ISS-01/F-03-01-primer-arranque.png)
*Página inicial de Angular funcionando*


### F-04 · ISS-02 · Acceso a la API en desarrollo

Todas las rutas de negocio exigen JWT. Para no construir la pantalla de login (fuera del alcance), el servicio `DevAuth` inicia sesión con un usuario de desarrollo y guarda el token. El interceptor `devAuthInterceptor` añade `Authorization: Bearer` a las peticiones a la API y, ante un 401, vuelve a iniciar sesión y reintenta una vez. Las credenciales viven en un archivo fuera de git.

![F-04 `environment.ts` con `apiUrl`](Reguistro%20visual/ISS-02/F-04-01-environment-api.png)
*`environment.ts` con `apiUrl`*

![F-04 `dev-auth.ts`](Reguistro%20visual/ISS-02/F-04-02-dev-auth.png)
*`dev-auth.ts`*

![F-04 `dev-auth.interceptor.ts`](Reguistro%20visual/ISS-02/F-04-03-dev-auth-interceptor.png)
*`dev-auth.interceptor.ts`*

![F-04 `app.config.ts` registrando el interceptor](Reguistro%20visual/ISS-02/F-04-04-app-config-interceptor.png)
*`app.config.ts` registrando el interceptor*


### F-05 · ISS-02 · Base del consumo de la API

`BaseApi<T>` concentra el `getAll()` contra `environment.apiUrl`; cada servicio solo declara su `path`. `shared/state-severity.ts` traduce los estados (`ACTIVE`, `PENDIENTE`, etc.) a etiqueta y color del `p-tag`.

![F-05 Modelo `ClientI`](Reguistro%20visual/ISS-02/F-05-01-modelo-cliente.png)
*Modelo `ClientI`*

![F-05 `BaseApi<T>`](Reguistro%20visual/ISS-02/F-05-02-base-api.png)
*`BaseApi<T>`*

![F-05 `ClientService` con el path `clientes`](Reguistro%20visual/ISS-02/F-05-03-servicio-clientes.png)
*`ClientService` con el path `clientes`*

![F-05 `state-severity.ts`](Reguistro%20visual/ISS-02/F-05-04-state-severity.png)
*`state-severity.ts`*


### F-06 · ISS-03 · Listado de clientes

Primer listado completo con tabla, paginador, ordenamiento y botón Actualizar. Al inicio salió con 0 registros porque la base estaba vacía; se crearon dos clientes desde Swagger y aparecieron. Las peticiones `login/` y `clientes/` responden 200.

![F-06 `getall.ts` del componente de clientes](Reguistro%20visual/ISS-03/F-06-01-getall-ts.png)
*`getall.ts` del componente de clientes*

![F-06 `getall.html` con `p-table`](Reguistro%20visual/ISS-03/F-06-02-getall-html.png)
*`getall.html` con `p-table`*

![F-06 `app.routes.ts` con la ruta `clientes` (carga perezosa)](Reguistro%20visual/ISS-03/F-06-03-rutas.png)
*`app.routes.ts` con la ruta `clientes` (carga perezosa)*

![F-06 `npm start` compila sin errores](Reguistro%20visual/ISS-03/F-06-04-npm-start-ok.png)
*`npm start` compila sin errores*

![F-06 Clientes con 0 registros (base vacía)](Reguistro%20visual/ISS-03/F-06-05-clientes-vacio.png)
*Clientes con 0 registros (base vacía)*

![F-06 Creación de un cliente desde Swagger](Reguistro%20visual/ISS-03/F-06-06-swagger-post-clientes.png)
*Creación de un cliente desde Swagger*

![F-06 Pestaña Network con `login/` y `clientes/` respondiendo](Reguistro%20visual/ISS-03/F-06-07-network.png)
*Pestaña Network con `login/` y `clientes/` respondiendo*

![F-06 Clientes con 2 registros](Reguistro%20visual/ISS-03/F-06-08-clientes-con-datos.png)
*Clientes con 2 registros*


### F-07 · ISS-01 · Licencia de PrimeNG

PrimeNG 22 mostraba el aviso rojo "Invalid PrimeUI License". Se configuró la licencia gratuita Community en `providePrimeNG({ license })`, leída desde `environments/primeng-license.ts` (archivo fuera de git).

![F-07 `app.config.ts` con `license: primengLicense`](Reguistro%20visual/ISS-01/F-07-01-app-config-licencia.png)
*`app.config.ts` con `license: primengLicense`*

![F-07 Aplicación sin el aviso de licencia](Reguistro%20visual/ISS-01/F-07-02-sin-aviso.png)
*Aplicación sin el aviso de licencia*


### F-08 · ISS-05 · Listado de productos

Modelo, servicio (`productos`), componente y ruta. El precio se formatea en pesos colombianos con `CurrencyPipe`. Se crearon tres productos desde Swagger.

![F-08 Modelo `ProductI` y `ProductService`](Reguistro%20visual/ISS-05/F-08-01-modelo-y-servicio.png)
*Modelo `ProductI` y `ProductService`*

![F-08 `getall.ts` de productos](Reguistro%20visual/ISS-05/F-08-02-getall-ts.png)
*`getall.ts` de productos*

![F-08 `getall.html` de productos](Reguistro%20visual/ISS-05/F-08-03-getall-html.png)
*`getall.html` de productos*

![F-08 `app.routes.ts` con `clientes` y `productos`](Reguistro%20visual/ISS-05/F-08-04-rutas.png)
*`app.routes.ts` con `clientes` y `productos`*

![F-08 Creación de un producto desde Swagger](Reguistro%20visual/ISS-05/F-08-05-swagger-post-productos.png)
*Creación de un producto desde Swagger*

![F-08 Listado de productos](Reguistro%20visual/ISS-05/F-08-06-productos.png)
*Listado de productos*


### F-09 · ISS-06 · Listado de pedidos con detalle

Cada pedido de la API trae una lista `details`. La fila principal muestra fecha, cliente, sede, mesa, canal, total y estado. Con `pRowToggler` se abre la plantilla `#expandedrow`, que recorre `row.details` con `@for` y dibuja una tabla con producto, cantidad, precio unitario, total y notas. Un pedido necesita una sede, que se creó desde el Django Admin porque la API no tiene endpoint para sedes.

![F-09 Modelos `OrderI` y `OrderDetailI`](Reguistro%20visual/ISS-06/F-09-01-modelo-pedido.png)
*Modelos `OrderI` y `OrderDetailI`*

![F-09 `OrderService`](Reguistro%20visual/ISS-06/F-09-02-servicio-pedidos.png)
*`OrderService`*

![F-09 `getall.ts` de pedidos](Reguistro%20visual/ISS-06/F-09-03-getall-ts.png)
*`getall.ts` de pedidos*

![F-09 `getall.html` con la fila desplegable `#expandedrow`](Reguistro%20visual/ISS-06/F-09-04-getall-html-detalle.png)
*`getall.html` con la fila desplegable `#expandedrow`*

![F-09 `app.routes.ts` con la ruta `pedidos`](Reguistro%20visual/ISS-06/F-09-05-rutas.png)
*`app.routes.ts` con la ruta `pedidos`*

![F-09 Sede creada en el Django Admin](Reguistro%20visual/ISS-06/F-09-06-admin-sede.png)
*Sede creada en el Django Admin*

![F-09 Creación de un pedido desde Swagger](Reguistro%20visual/ISS-06/F-09-07-swagger-post-pedidos.png)
*Creación de un pedido desde Swagger*

![F-09 Listado de pedidos con el detalle del pedido #3 desplegado](Reguistro%20visual/ISS-06/F-09-08-pedidos.png)
*Listado de pedidos (aquí se ve el problema del traductor, corregido en la sección 8)*


### F-10 · Extra BrasaGo · Listados de pagos y reservas

Mismo patrón: modelo, servicio, componente y ruta. Las capturas finales se tomaron con los datos de ejemplo del paso F-15.

![F-10 Modelo y servicio de pagos, y generación del componente](Reguistro%20visual/Extra-BrasaGo/F-10-01-pagos-modelo-servicio.png)
*Modelo y servicio de pagos, y generación del componente*

![F-10 `getall.ts` de pagos](Reguistro%20visual/Extra-BrasaGo/F-10-02-pagos-getall-ts.png)
*`getall.ts` de pagos*

![F-10 `getall.html` de pagos](Reguistro%20visual/Extra-BrasaGo/F-10-03-pagos-getall-html.png)
*`getall.html` de pagos*

![F-10 Modelo y servicio de reservas](Reguistro%20visual/Extra-BrasaGo/F-10-04-reservas-modelo-servicio.png)
*Modelo y servicio de reservas*

![F-10 `getall.ts` de reservas](Reguistro%20visual/Extra-BrasaGo/F-10-05-reservas-getall-ts.png)
*`getall.ts` de reservas*

![F-10 `getall.html` de reservas](Reguistro%20visual/Extra-BrasaGo/F-10-06-reservas-getall-html.png)
*`getall.html` de reservas*

![F-10 `app.routes.ts` con cinco pantallas](Reguistro%20visual/Extra-BrasaGo/F-10-07-rutas.png)
*`app.routes.ts` con cinco pantallas*

![F-10 Listado de pagos (5 registros)](Reguistro%20visual/Extra-BrasaGo/F-10-08-pagos.png)
*Listado de pagos (5 registros)*

![F-10 Listado de reservas (3 registros)](Reguistro%20visual/Extra-BrasaGo/F-10-09-reservas.png)
*Listado de reservas (3 registros)*


### F-11 · Extra BrasaGo · Listados de insumos, recetas, domiciliarios y entregas

Los cuatro siguen el mismo patrón. Los servicios se generaron con un bucle de shell, porque solo cambian el nombre y la ruta. Las capturas finales se tomaron con los datos de ejemplo del paso F-15.

![F-11 Modelos de insumos, recetas, domiciliarios y entregas](Reguistro%20visual/Extra-BrasaGo/F-11-01-modelos.png)
*Modelos de insumos, recetas, domiciliarios y entregas*

![F-11 Bucle que genera los cuatro servicios, y `ls` de modelos y servicios](Reguistro%20visual/Extra-BrasaGo/F-11-02-bucle-servicios.png)
*Bucle que genera los cuatro servicios, y `ls` de modelos y servicios*

![F-11 Generación de los componentes](Reguistro%20visual/Extra-BrasaGo/F-11-03-ng-generate.png)
*Generación de los componentes*

![F-11 `getall.ts` de insumos](Reguistro%20visual/Extra-BrasaGo/F-11-04-insumos-getall-ts.png)
*`getall.ts` de insumos*

![F-11 `getall.html` de insumos](Reguistro%20visual/Extra-BrasaGo/F-11-05-insumos-getall-html.png)
*`getall.html` de insumos*

![F-11 `getall.ts` de recetas](Reguistro%20visual/Extra-BrasaGo/F-11-06-recetas-getall-ts.png)
*`getall.ts` de recetas*

![F-11 `getall.html` de recetas](Reguistro%20visual/Extra-BrasaGo/F-11-07-recetas-getall-html.png)
*`getall.html` de recetas*

![F-11 `getall.ts` de domiciliarios](Reguistro%20visual/Extra-BrasaGo/F-11-08-domiciliarios-getall-ts.png)
*`getall.ts` de domiciliarios*

![F-11 `getall.html` de domiciliarios](Reguistro%20visual/Extra-BrasaGo/F-11-09-domiciliarios-getall-html.png)
*`getall.html` de domiciliarios*

![F-11 `getall.ts` de entregas](Reguistro%20visual/Extra-BrasaGo/F-11-10-entregas-getall-ts.png)
*`getall.ts` de entregas*

![F-11 `getall.html` de entregas](Reguistro%20visual/Extra-BrasaGo/F-11-11-entregas-getall-html.png)
*`getall.html` de entregas*

![F-11 `app.routes.ts` con las nueve pantallas](Reguistro%20visual/Extra-BrasaGo/F-11-12-rutas.png)
*`app.routes.ts` con las nueve pantallas*

![F-11 Listado de insumos (5 registros)](Reguistro%20visual/Extra-BrasaGo/F-11-13-insumos.png)
*Listado de insumos (5 registros)*

![F-11 Listado de recetas (6 registros)](Reguistro%20visual/Extra-BrasaGo/F-11-14-recetas.png)
*Listado de recetas (6 registros)*

![F-11 Listado de domiciliarios (3 registros)](Reguistro%20visual/Extra-BrasaGo/F-11-15-domiciliarios.png)
*Listado de domiciliarios (3 registros)*

![F-11 Listado de entregas (2 registros)](Reguistro%20visual/Extra-BrasaGo/F-11-16-entregas.png)
*Listado de entregas (2 registros)*


### F-12 · Transversal · Pruebas automáticas

Los `spec.ts` generados por Angular fallan cuando el componente usa `HttpClient`. Se reescribieron: cada `getall` comprueba que el componente se crea y que pide `GET /<ruta>/` (con `HttpTestingController` y `flush([])`). También se probaron `App` y el menú lateral. Resultado: **13 archivos y 22 pruebas OK**.

![F-12 Bucle que genera los `spec.ts` de las nueve pantallas](Reguistro%20visual/Transversal/F-12-01-bucle-specs.png)
*Bucle que genera los `spec.ts` de las nueve pantallas*

![F-12 `app.spec.ts`](Reguistro%20visual/Transversal/F-12-02-app-spec.png)
*`app.spec.ts`*

![F-12 `aside.spec.ts`](Reguistro%20visual/Transversal/F-12-03-aside-spec.png)
*`aside.spec.ts`*

![F-12 `ng test`: 13 archivos y 22 pruebas OK](Reguistro%20visual/Transversal/F-12-04-ng-test.png)
*`ng test`: 13 archivos y 22 pruebas OK*


### F-13 · Transversal · Build de producción

`ng build` termina sin errores: una *chunk* por pantalla (carga perezosa) y 9 rutas prerenderizadas.

![F-13 `ng build` sin errores](Reguistro%20visual/Transversal/F-13-01-ng-build.png)
*`ng build` sin errores*


### F-14 · Transversal · Repositorio y manejo de secretos

`dev-credentials.ts` y `primeng-license.ts` están en `.gitignore`. Se publican archivos `.example.ts` con valores falsos para que quien clone el repositorio pueda compilar. Antes de copiar el proyecto al repositorio se verificó que ninguna clave viaje en él.

![F-14 Comprobación del `.gitignore` y creación de los archivos de ejemplo](Reguistro%20visual/Transversal/F-14-01-gitignore-y-ejemplos.png)
*Comprobación del `.gitignore` y creación de los archivos de ejemplo*

![F-14 Archivo de ejemplo corregido y build posterior](Reguistro%20visual/Transversal/F-14-02-ejemplo-y-build.png)
*Archivo de ejemplo corregido y build posterior*

![F-14 Copia del frontend al repositorio sin `node_modules`, `dist` ni secretos](Reguistro%20visual/Transversal/F-14-03-copia-a-motores.png)
*Copia del frontend al repositorio sin `node_modules`, `dist` ni secretos*

![F-14 Verificación: la licencia no está en el repositorio](Reguistro%20visual/Transversal/F-14-04-verificacion.png)
*Verificación: la licencia no está en el repositorio*


### F-15 · Transversal · Datos de ejemplo para las pantallas

Para mostrar las pantallas con información real se cargaron datos de ejemplo **a través de la propia API** (con JWT y todas sus validaciones), con el script `seed_frontend.py` de esta carpeta. Antes se crearon tres mesas con un comando de Django, porque la API no tiene endpoint para mesas, y una reserva necesita una. El script pide la contraseña por teclado y no la guarda.

Reglas del backend que condicionaron los datos: una entrega solo acepta pedidos con canal `DOMICILIO`, un pago `PAGADO` no puede superar el total del pedido, y una reserva no puede solaparse con otra de la misma mesa.

| Entidad | Registros cargados |
|---|---|
| Insumos | 5 (arroz, carne de res, costilla de cerdo, pollo entero y aceite) |
| Recetas | 6 (dos insumos por producto) |
| Domiciliarios | 3 |
| Pedidos | 3 nuevos: uno en mesa y dos a domicilio |
| Pagos | 5: efectivo, transferencia, tarjeta pendiente y dos de pedidos anteriores |
| Reservas | 3, en tres mesas y dos días |
| Entregas | 2: una en camino y una pendiente |

![F-15 Creación de las mesas](Reguistro%20visual/Transversal/F-15-01-mesas.png)
*Creación de las mesas desde el shell de Django*

![F-15 Ejecución del script](Reguistro%20visual/Transversal/F-15-02-script.png)
*Ejecución de `seed_frontend.py`: un `OK` por cada registro creado*


### F-16 · ISS-03 · CRUD de clientes (adaptado)

Se amplió el listado de clientes con alta, edición, baja lógica y búsqueda. El servicio `ClientService` agrega `create`, `update` y `remove` sobre `/api/clientes/` (`POST`, `PATCH` y `DELETE`). El componente `getall` usa un formulario reactivo dentro de un `p-dialog`, que sirve tanto para alta como para edición.

Adaptaciones frente a la guía: la ruta es `/api/clientes/` (no `/api/clients/`), el estado es `ACTIVE`/`INACTIVE`, y la confirmación de baja usa el cuadro nativo `confirm()`. Los errores del backend (por ejemplo, documento duplicado) se muestran dentro del diálogo.

![Diálogo "Nuevo cliente" con validación de nombre corto](Reguistro%20visual/ISS-03/F-16-01-nombre-corto.png)
*Diálogo "Nuevo cliente" con validación de nombre corto*

![Búsqueda por "laura" en el listado de clientes](Reguistro%20visual/ISS-03/F-16-02-buscar.png)
*Búsqueda por "laura" en el listado de clientes*

![Error del backend por número de documento duplicado, mostrado en el diálogo](Reguistro%20visual/ISS-03/F-16-03-documento-duplicado.png)
*Error del backend por número de documento duplicado, mostrado en el diálogo*

![Cliente dado de baja: el estado queda como Inactivo](Reguistro%20visual/ISS-03/F-16-04-baja.png)
*Cliente dado de baja: el estado queda como Inactivo*

![`ng build` sin errores](Reguistro%20visual/ISS-03/F-16-05-ng-build.png)
*`ng build` sin errores*

### F-17 · ISS-05 · CRUD de productos (adaptado)

Se amplió el listado de productos con alta, edición, baja lógica y búsqueda. `ProductService` agrega `create`, `update` y `remove` sobre `/api/productos/`. El formulario valida SKU (2 a 50 caracteres), nombre (2 a 150), descripción opcional y precio no negativo, y lo envía como texto decimal, como lo espera el backend.

Adaptaciones frente a la guía: BrasaGo no tiene stock ni tipo de producto en el diagrama, así que se omiten las filas en ámbar por stock bajo, el selector de tipo y el interruptor de disponibles. El precio se muestra en pesos colombianos. La baja usa el mismo patrón que clientes.

![Diálogo "Nuevo producto" con validación de SKU corto](Reguistro%20visual/ISS-05/F-17-01-sku-corto.png)
*Diálogo "Nuevo producto" con validación de SKU corto*

![Producto nuevo en la tabla, con precio en pesos](Reguistro%20visual/ISS-05/F-17-02-producto-nuevo.png)
*Producto nuevo en la tabla, con precio en pesos*

![Error del backend por SKU duplicado, mostrado en el diálogo](Reguistro%20visual/ISS-05/F-17-03-sku-duplicado.png)
*Error del backend por SKU duplicado, mostrado en el diálogo*

![Producto dado de baja: el estado queda como Inactivo](Reguistro%20visual/ISS-05/F-17-04-baja.png)
*Producto dado de baja: el estado queda como Inactivo*

![`ng build` sin errores](Reguistro%20visual/ISS-05/F-17-05-ng-build.png)
*`ng build` sin errores*


### F-18 · Transversal · Pruebas después de los CRUD

Tras agregar alta, edición, baja y búsqueda, se volvió a ejecutar `npx ng test --no-watch`. Resultado: **13 archivos y 22 pruebas OK**, sin fallos. Las pruebas de `getall` de clientes y productos siguen pasando con el formulario y el servicio nuevos.

![F-18 ng test después de los CRUD](Reguistro%20visual/Transversal/F-18-01-ng-test.png)
*`ng test` con 13 archivos y 22 pruebas OK*


### F-19 · ISS-06 · Registro de pedidos desde la pantalla (adaptado)

El listado de pedidos suma un diálogo "Nuevo pedido" con un borrador hecho con signals (sin `FormGroup`, como pide la guía). El cliente es opcional, el canal puede ser Mesa, Recogida o Domicilio, y cada línea se agrega con producto y cantidad. El servicio `OrderService.create` envía `POST /api/pedidos/` con `clientId`, `branchId`, `tableId`, `channel` e `items`.

Reglas en el cliente: al menos un producto, cantidad entero mayor o igual a 1, sin productos repetidos y mesa obligatoria en canal Mesa. El total lo calcula el backend; en el diálogo solo se muestra un subtotal estimado.

Adaptaciones frente a la guía: no hay stock, impuestos ni descuentos en el diagrama, así que se omiten los avisos de stock. La sede y las mesas son constantes del frontend (`shared/venue.ts`), porque la API no tiene endpoints para ellas. La pantalla de venta se convierte en el registro de pedido.

![Diálogo "Nuevo pedido" con una línea y el subtotal estimado](Reguistro%20visual/ISS-06/F-19-01-dialogo-subtotal.png)
*Diálogo "Nuevo pedido" con una línea y el subtotal estimado*

![Aviso de producto repetido en el borrador](Reguistro%20visual/ISS-06/F-19-02-producto-repetido.png)
*Aviso de producto repetido en el borrador*

![Aviso de mesa obligatoria para un pedido en mesa](Reguistro%20visual/ISS-06/F-19-03-mesa-obligatoria.png)
*Aviso de mesa obligatoria para un pedido en mesa*

![Pedido nuevo en el listado, con su detalle desplegado](Reguistro%20visual/ISS-06/F-19-04-pedido-expandido.png)
*Pedido nuevo en el listado, con su detalle desplegado*

![`ng build` sin errores](Reguistro%20visual/ISS-06/F-19-05-ng-build.png)
*`ng build` sin errores*

### F-20 · ISS-07 · Detalle de pedido y anulación (adaptado)

Se crea la pantalla `/pedidos/:id` con la cabecera del pedido (fecha, cliente, sede, mesa, canal, estados y total) y sus líneas. El número del pedido en el listado enlaza a esa pantalla. La anulación llama a `DELETE /api/pedidos/{id}/`, pide confirmación, y al terminar recarga el pedido: queda en estado Cancelado y el botón de anular se oculta.

Adaptaciones frente a la guía: en BrasaGo no hay endpoint de líneas separado, así que el detalle usa los `details` que ya trae el pedido. No hay stock, así que el panel de stock bajo no aplica (se reemplaza por pedidos de hoy, pagos pendientes y entregas en camino). La ruta `pedidos/:id` se marca como renderizado en cliente (`app.routes.server.ts`), porque depende de un parámetro que no se puede prerenderizar.

![Detalle del pedido #7 con el botón Anular visible](Reguistro%20visual/ISS-07/F-20-01-detalle-con-anular.png)
*Detalle del pedido #7 con el botón Anular visible*

![Mismo pedido después de anularlo: estado Cancelado, registro Inactivo y botón oculto](Reguistro%20visual/ISS-07/F-20-02-anulado.png)
*Mismo pedido después de anularlo: estado Cancelado, registro Inactivo y botón oculto*

![Listado de pedidos con el pedido #7 en estado Cancelado](Reguistro%20visual/ISS-07/F-20-03-listado-cancelado.png)
*Listado de pedidos con el pedido #7 en estado Cancelado*

![`ng build` sin errores después del cambio de renderizado](Reguistro%20visual/ISS-07/F-20-04-ng-build.png)
*`ng build` sin errores después del cambio de renderizado*

---

### F-21 · ISS-07 · Líneas de pedido y panel del día

- Página `/detalle-pedidos` con las líneas de todos los pedidos (10 líneas), búsqueda y enlace al número de pedido. Captura 11.
- Panel `/dashboard` con datos del día tomados de la API: pedidos, total vendido, pagos pendientes y entregas en camino. Captura 10.
- Build de producción correcto: "Prerendered 11 static routes" antes del login y 13 después. Captura 12.
- Adaptación: el panel no muestra stock porque BrasaGo no maneja inventario de producto terminado.

### F-22 · ISS-08 · Login con JWT, sesión, interceptores y perfil

- Login en `/login` contra `POST /api/auth/login/`. Con credenciales incorrectas muestra "Usuario o contraseña incorrectos." (401).
- Con credenciales correctas guarda `access` y `refresh` en `localStorage` (clave `brasago.session.v1`) y entra al panel.
- `SessionStore` (signals) guarda tokens y usuario. Al recargar (F5) restaura la sesión y vuelve a pedir el perfil.
- `authInterceptor` agrega `Authorization: Bearer` a las peticiones de la API. Ante un 401 llama a `auth/refresh/` (una sola renovación en vuelo) y reintenta la petición. Evidencia: 401, refresh 200 y reintento 200 (captura 14).
- `errorInterceptor` muestra avisos (toast) para 403, 404, 409, 5xx y falta de conexión.
- Perfil en `/perfil` con usuario, nombre, correo y estado. Cerrar sesión llama a `auth/logout/` (204) y limpia la sesión (capturas 12 y 13).
- Menú lateral visible solo con sesión, con el grupo "Cuenta" y "Mi perfil".
- Pruebas: `ng test` con 13 archivos y 22 pruebas pasando. El `app.spec.ts` necesitó el proveedor `MessageService` porque el componente raíz ahora muestra avisos.
- Guards de rutas (ISS-09): resueltos en F-25.

---

### F-23 · ISS-01B · Layout y menú responsivo (adaptado)

- **Tailwind 4 y PrimeNG 22** configurados con el orden de capas `theme, base, primeng, utilities`. En `app.config.ts`, `cssLayer` usa `name: 'primeng'` y ese orden, y `styles.css` declara `@layer theme, base, primeng, utilities;` antes de los `@import`. Evidencia: en DevTools aparecen `Layer primeng` y `Layer base`.
- **Encabezado** (`components/layout/header`): botón de menú con `aria-label="Mostrar u ocultar el menú"`, que emite `menuRequested` con `output()`. Muestra el logo de BrasaGo sobre fondo blanco con línea naranja de marca.
- **Menú lateral** (`components/layout/aside`): recibe los items con `input<MenuItem[]>()` (por defecto, la lista de la app) y los pinta con `p-panelmenu [model]`. Emite `navigated` solo al hacer clic en un enlace, para no cerrar el menú al expandir un grupo.
- **Layout en `app.ts` / `app.html`**: en escritorio (1024 px o más), el botón colapsa y muestra el aside con signal `sidebarCollapsed`. En móvil, el botón abre un `p-drawer` desde la izquierda con signal `mobileOpen`, y al elegir una opción el drawer se cierra.
- Decisión de adaptación: en la guía el estado vive en un componente `construir`; en BrasaGo vive en `App`, porque la app ya tiene un único shell de layout y no hace falta un componente más.
- Pruebas: escritorio a 1280 px (menú visible y colapsado, capturas 15 y 15b), móvil a 390 px (drawer abierto, captura 16) y navegación desde el drawer a `/clientes` con cierre del drawer.
- `ng build` sin errores y `ng test`: 13 archivos y 22 pruebas pasando.
- Diferencias con la guía que se mantienen: rutas en `components/layout/` y no en `layout/`; el dominio de la app es BrasaGo, no StoreLab; los items del menú son los de BrasaGo.

---

### F-24 · ISS-02 a ISS-08 · Revisión contra la guía y correcciones

Se revisó el proyecto contra las guías ISS-02 a ISS-08. BrasaGo tiene otro dominio que StoreLab, así que varias partes se adaptaron y no se copiaron literalmente.

| Guía | Estado | Adaptación o diferencia |
|---|---|---|
| ISS-02 Núcleo y servicios | Parcial | Servicios por entidad sobre `BaseApi`, `environment` con `fileReplacements`. No hay carpeta `core/models/` separada, ni `NotificationService`, ni `toApiMessage` y `filterRows` como utilidades; los avisos usan `MessageService` directo. |
| ISS-03 CRUD de clientes | Cumple con adaptación | Lista, búsqueda, alta, edición y baja lógica (cliente `Inactivo`, botón de baja deshabilitado). Se usan tipo y número de documento porque el backend de BrasaGo los exige. |
| ISS-04 Tipos de producto | No aplica | BrasaGo no tiene tipos de producto. |
| ISS-05 CRUD de productos | Parcial | Sin tipo de producto ni stock en BrasaGo, así que no hay "solo disponibles" ni alerta de stock bajo. |
| ISS-06 Ventas y detalle | Parcial | Se implementó como pedidos: registro con líneas, validación de duplicados, totales y anulación (F-19 y F-20). No hay descuentos ni descuento de stock. |
| ISS-08 Autenticación JWT | Parcial | Login, refresh con una sola renovación, logout con 204, sesión que sobrevive a F5 y `Bearer` en las peticiones. Endpoint `/auth/permissions/` agregado para el control de acceso por pantalla (ver F-25). |

**Correcciones aplicadas en esta revisión:**
- Validación del teléfono de clientes: mínimo 7 y máximo 30 caracteres, solo dígitos, `+`, `-`, espacios y paréntesis (ISS-03).
- Al fallar el refresh del token, la redirección a `/login` conserva `returnUrl` para volver a la pantalla original (ISS-08).
- Se eliminó un archivo auxiliar de Windows dentro de `src/environments/`.

**Verificación:** `ng build` sin errores y `ng test --watch=false` con 22 pruebas pasando.

---

### F-25 · ISS-08 a ISS-09 · Permisos por recurso, guards y menú filtrado (adaptado)

Qué se hizo:
- Backend: endpoint `GET /api/auth/permissions/` (`apps/security/permissions_view.py`). Devuelve los permisos efectivos del usuario autenticado (`method`, `path` normalizado a `/api/recurso/:id/` y `role`), leídos de RoleUser → Role → ResourceRole → Resource, solo de registros ACTIVE. Pruebas de `apps.security`: 101 OK.
- Frontend: `SessionStore` guarda los permisos y `canPermission('MÉTODO /ruta')` normaliza la ruta y compara el método. `AuthService.refreshSession()` carga perfil y permisos en paralelo con `forkJoin`.
- Guards (`core/guards/rbac.guards.ts`): `authGuard` redirige a /login con `returnUrl`; `guestGuard` evita volver a login con sesión activa; `permissionGuard` lee `data.permission` de la ruta y, si falta, redirige a `/forbidden?permission=…`. La pantalla de acceso denegado está en `components/auth/forbidden`.
- Menú filtrado: cada opción declara su permiso. Las opciones sin permiso y los grupos vacíos no se muestran (`components/layout/aside`).
- Botones por permiso: directiva `*appHasPermission` (`shared/directives/has-permission.ts`) aplicada a Nuevo, editar y eliminar en Clientes y Productos, y a Nuevo pedido en Pedidos.

Adaptación frente a la guía: la guía pide una pantalla de permisos por rol. En BrasaGo el RBAC ya existía en el backend (84 recursos generados con `seed_rbac`), así que el frontend lo consume en lugar de duplicarlo en código.

Verificación:
- `ng test`: 29 pruebas en verde (22 de los pasos anteriores, más 2 de la directiva, 3 de los guards y 2 del menú).
- Usuario `sinpermisos`: el menú solo muestra Cuenta › Mi perfil, y entrar a /pedidos redirige a /forbidden con `GET /api/pedidos/`.
- Usuario `elkin`: menú completo y botones visibles en Clientes, Productos y Pedidos.

![F-25 Menú de sinpermisos: solo Cuenta › Mi perfil](Reguistro%20visual/ISS-09/F-25-01-menu-sinpermisos.png)
*Menú de `sinpermisos`: solo el grupo Cuenta con Mi perfil (Captura 18)*

![F-25 Acceso denegado al entrar a /pedidos](Reguistro%20visual/ISS-09/F-25-02-forbidden-pedidos.png)
*`sinpermisos` entra a /pedidos y ve la pantalla de acceso denegado con `GET /api/pedidos/`*

![F-25 Menú completo de elkin](Reguistro%20visual/ISS-09/F-25-03-menu-elkin.png)
*Menú completo del usuario `elkin` (Captura 20)*

![F-25 Build y 22 pruebas tras el menú filtrado](Reguistro%20visual/ISS-09/F-25-04-build-menu.png)
*`ng build` sin errores y pruebas en verde tras filtrar el menú*

![F-25 Pruebas tras la directiva de permisos](Reguistro%20visual/ISS-09/F-25-05-ng-test-directiva.png)
*`ng test` con 24 pruebas tras agregar `*appHasPermission`*

![F-25 Botones de Clientes con elkin](Reguistro%20visual/ISS-09/F-25-06-clientes-elkin.png)
*Clientes con `elkin`: Nuevo cliente, editar y eliminar visibles (Captura 21)*

![F-25 Botones de Productos con elkin](Reguistro%20visual/ISS-09/F-25-07-productos-elkin.png)
*Productos con `elkin`: Nuevo producto, editar y eliminar visibles*

![F-25 Botón Nuevo pedido con elkin](Reguistro%20visual/ISS-09/F-25-08-pedidos-elkin.png)
*Pedidos con `elkin`: botón Nuevo pedido visible (Captura 23)*

![F-25 Pruebas finales de ISS-09: 29 OK](Reguistro%20visual/ISS-09/F-25-09-ng-test-29.png)
*`ng test` con 29 pruebas en verde, incluidos los guards y el menú (Captura 24)*

### F-26 · Identidad visual de BrasaGo (adaptado)

Se cambió el tema de PrimeNG y la hoja de estilos para que la interfaz use la identidad de BrasaGo, en vez del tema azul por defecto.

- **Paleta de marca** en `app.config.ts`: `definePreset(Aura, …)` con una escala naranja a partir del color de marca `#e8502a` (nivel 500). Los extremos son `#fff4ef` (50) y `#32100a` (950), y así los botones principales, los enlaces y los estados activos del menú toman el naranja.
- **Capas CSS** (`styles.css` y `cssLayer` en `providePrimeNG`): `theme, base, primeng, utilities`, para que Tailwind no pise los estilos de PrimeNG.
- **Fondo y texto**: fondo `#f1f5f9` y texto `#1e293b` en `body`, con la fuente Inter.
- **Encabezado**: logo `brasago-logo.png` sobre fondo blanco con una línea naranja inferior de 4 px (`border-[#e8502a]`).
- **Tarjetas**: el panel, las tablas y los formularios se muestran en tarjetas blancas con sombra suave, sobre el fondo gris claro.

Adaptación frente a la guía: la guía usa el tema de PrimeNG tal cual. Aquí se definió un preset propio porque la marca BrasaGo tiene color propio y el proyecto lo pidió así.

Evidencias:

![F-26 Encabezado con el logo de BrasaGo y la línea naranja](Reguistro%20visual/Transversal/F-26-01-encabezado-logo.png)
*Encabezado con el logo y la línea naranja de marca*

![F-26 Botones y menú con el naranja de marca](Reguistro%20visual/Transversal/F-26-02-tema-naranja.png)
*Botón principal y estado activo del menú con el naranja de la marca*

![F-26 app.config.ts con el preset de marca](Reguistro%20visual/Transversal/F-26-03-app-config-preset.png)
*`app.config.ts` con `definePreset` y la escala naranja*

### F-27 · ISS-10 · Administración RBAC: usuarios, roles, recursos, asignaciones y permisos (adaptado)

Qué se hizo:
- Backend: endpoint `GET /api/users/<id>/permissions/` (`UserPermissionsAPIView`). Devuelve los permisos activos del usuario a través de sus roles, en formato `{method, path, role}`. Responde 404 si el usuario no existe.
- Frontend: `CrudApi<T, P>` (`services/security/crud.ts`) con `getAll`, `getById`, `create` (POST), `update` (PATCH) y `remove` (DELETE, 204). Se extiende en `UserApi`, `RoleApi`, `ResourceApi`, `RoleUserApi` y `ResourceRoleApi`. `UserApi.permissions(id)` consume el endpoint nuevo.
- Modelos en `models/security/`: `RecordStatus`, `UserI`/`UserPayload`, `UserPermission`, `RoleI`, `ResourceI`, `RoleUserI` y `ResourceRoleI`.
- Pantallas (`components/admin/`), todas con tabla, alta y edición en diálogo, baja lógica con confirmación, botones protegidos con `*appHasPermission` y ruta protegida con `permissionGuard`:
  - Usuarios (`/admin/usuarios`, `GET /api/users/`): búsqueda por usuario, correo o nombre. La contraseña es obligatoria al crear (mínimo 8) y no aparece al editar.
  - Roles (`/admin/roles`, `GET /api/roles/`): nombre de 2 a 30 letras o guion bajo, que se guarda en mayúsculas.
  - Recursos (`/admin/recursos`, `GET /api/resources/`): método entre los cinco verbos y ruta que empieza por `/api/`.
  - Asignaciones de rol (`/admin/asignaciones`, `GET /api/role-users/`): usuario y rol con selectores filtrables. Usa `forkJoin` para cargar asignaciones, roles y usuarios, y muestra nombres en lugar de IDs.
  - Permisos por rol (`/admin/permisos`, `GET /api/resource-roles/`): recurso (`MÉTODO ruta`) y rol con selectores filtrables.
- Diálogo **Ver permisos** en Usuarios: el icono de escudo abre una tabla con una fila por permiso (método, ruta y rol). Para `elkin` (ADMIN) muestra 85 filas.
- Menú lateral: grupo **Seguridad** entre Domicilios y Cuenta, con Usuarios, Roles, Recursos, Asignaciones y Permisos por rol. Cada opción declara su permiso.

Adaptación frente a la guía: el RBAC ya existe en el backend, así que el frontend consume esos recursos en lugar de duplicar el modelo de permisos.

Verificación:
- `ng build` termina sin errores después de cada pantalla.
- `ng test`: 19 archivos y 36 pruebas OK (captura F-27-48). Las pruebas nuevas de ISS-10 son `UserApi` (3), `ResourceRoleApi` (2) y `UserList` (2).
- Usuario `elkin` entra por URL a `/admin/usuarios` y a cada pantalla de seguridad desde el menú.
- Usuario `sinpermisos` entra a `/forbidden` con el permiso requerido, y el menú solo muestra Cuenta › Mi perfil.

**Acceso y usuarios**

![F-27 /admin/usuarios abierta por URL con los registros cargados](Reguistro%20visual/ISS-10/F-27-01_usuarios-url.png)
*/admin/usuarios abierta por URL con los registros cargados*

![F-27 Permisos de ADMIN desde `/api/auth/permissions/` (contraseña difuminada)](Reguistro%20visual/ISS-10/F-27-02_permisos-api.png)
*Permisos de ADMIN desde `/api/auth/permissions/` (contraseña difuminada)*

![F-27 Ruta `admin/usuarios` en `app.routes.ts`, verificada con `grep`](Reguistro%20visual/ISS-10/F-27-03_ruta-admin-usuarios.png)
*Ruta `admin/usuarios` en `app.routes.ts`, verificada con `grep`*

![F-27 `sinpermisos` en `/forbidden` con el permiso requerido `GET /api/pedidos/`](Reguistro%20visual/ISS-10/F-27-04_acceso-denegado.png)
*`sinpermisos` en `/forbidden` con el permiso requerido `GET /api/pedidos/`*

![F-27 Diálogo Nuevo usuario con el campo de contraseña (difuminado)](Reguistro%20visual/ISS-10/F-27-05_nuevo-usuario.png)
*Diálogo Nuevo usuario con el campo de contraseña (difuminado)*

![F-27 Diálogo Editar usuario sin campo de contraseña](Reguistro%20visual/ISS-10/F-27-06_editar-usuario.png)
*Diálogo Editar usuario sin campo de contraseña*

![F-27 Script que inserta la ruta `admin/usuarios` y build completo](Reguistro%20visual/ISS-10/F-27-07_insertar-ruta-build.png)
*Script que inserta la ruta `admin/usuarios` y build completo*

![F-27 Creación de `user-list.html`](Reguistro%20visual/ISS-10/F-27-08_user-list-html.png)
*Creación de `user-list.html`*

![F-27 Creación de `user-list.ts` (inicio)](Reguistro%20visual/ISS-10/F-27-09_user-list-ts.png)
*Creación de `user-list.ts` (inicio)*

![F-27 `user-list.ts`: guardar, baja y manejo de errores](Reguistro%20visual/ISS-10/F-27-10_user-list-ts-guardar.png)
*`user-list.ts`: guardar, baja y manejo de errores*

**Roles**

![F-27 Código de `role-list.ts`: guardar, baja y errores](Reguistro%20visual/ISS-10/F-27-11_roles-codigo-ts.png)
*Código de `role-list.ts`: guardar, baja y errores*

![F-27 Código de `role-list.html`](Reguistro%20visual/ISS-10/F-27-12_roles-codigo-html.png)
*Código de `role-list.html`*

![F-27 Script que agrega la ruta `admin/roles` y build completo](Reguistro%20visual/ISS-10/F-27-13_ruta-roles-build.png)
*Script que agrega la ruta `admin/roles` y build completo*

![F-27 Pantalla de roles con 2 registros (ADMIN activo y mesero inactivo)](Reguistro%20visual/ISS-10/F-27-15_roles-lista.png)
*Pantalla de roles con 2 registros (ADMIN activo y mesero inactivo)*

![F-27 Diálogo Nuevo rol vacío](Reguistro%20visual/ISS-10/F-27-16_roles-nuevo.png)
*Diálogo Nuevo rol vacío*

![F-27 Validación del nombre: mínimo 2 letras, sin números](Reguistro%20visual/ISS-10/F-27-17_roles-validacion.png)
*Validación del nombre: mínimo 2 letras, sin números*

**Menú Seguridad**

![F-27 Script que agrega el grupo Seguridad al menú](Reguistro%20visual/ISS-10/F-27-18_menu-seguridad-script.png)
*Script que agrega el grupo Seguridad al menú*

![F-27 Menú con el grupo Seguridad (Usuarios y Roles)](Reguistro%20visual/ISS-10/F-27-19_menu-seguridad-visible.png)
*Menú con el grupo Seguridad (Usuarios y Roles)*

**Recursos**

![F-27 Código de `resource-list.ts`](Reguistro%20visual/ISS-10/F-27-20_recursos-codigo-ts.png)
*Código de `resource-list.ts`*

![F-27 Código de `resource-list.html`](Reguistro%20visual/ISS-10/F-27-21_recursos-codigo-html.png)
*Código de `resource-list.html`*

![F-27 Script de ruta y menú de Recursos, y build completo](Reguistro%20visual/ISS-10/F-27-22_ruta-recursos-build.png)
*Script de ruta y menú de Recursos, y build completo*

![F-27 Pantalla de recursos con 85 registros](Reguistro%20visual/ISS-10/F-27-23_recursos-lista.png)
*Pantalla de recursos con 85 registros*

![F-27 Diálogo Nuevo recurso con validación de ruta, que debe empezar por `/api/`](Reguistro%20visual/ISS-10/F-27-24_recursos-validacion.png)
*Diálogo Nuevo recurso con validación de ruta, que debe empezar por `/api/`*

![F-27 Diálogo Editar recurso](Reguistro%20visual/ISS-10/F-27-25_recursos-editar.png)
*Diálogo Editar recurso*

**Asignaciones de rol**

![F-27 Código de `role-user-list.ts` con `forkJoin`](Reguistro%20visual/ISS-10/F-27-26_asignaciones-codigo-ts.png)
*Código de `role-user-list.ts` con `forkJoin`*

![F-27 Código de `role-user-list.html`](Reguistro%20visual/ISS-10/F-27-27_asignaciones-codigo-html.png)
*Código de `role-user-list.html`*

![F-27 Script de ruta y menú de Asignaciones, y build completo](Reguistro%20visual/ISS-10/F-27-28_ruta-asignaciones-build.png)
*Script de ruta y menú de Asignaciones, y build completo*

![F-27 Pantalla de asignaciones: muestra nombre de usuario y de rol](Reguistro%20visual/ISS-10/F-27-29_asignaciones-lista.png)
*Pantalla de asignaciones: muestra nombre de usuario y de rol*

![F-27 Diálogo Nueva asignación con selectores filtrables](Reguistro%20visual/ISS-10/F-27-30_asignaciones-nueva.png)
*Diálogo Nueva asignación con selectores filtrables*

![F-27 Diálogo Editar asignación](Reguistro%20visual/ISS-10/F-27-31_asignaciones-editar.png)
*Diálogo Editar asignación*

**Permisos por rol**

![F-27 Código de `resource-role-list.ts`](Reguistro%20visual/ISS-10/F-27-32_permisos-codigo-ts.png)
*Código de `resource-role-list.ts`*

![F-27 Código de `resource-role-list.html`](Reguistro%20visual/ISS-10/F-27-33_permisos-codigo-html.png)
*Código de `resource-role-list.html`*

![F-27 Script de ruta y menú de Permisos por rol, y build completo](Reguistro%20visual/ISS-10/F-27-34_ruta-permisos-build.png)
*Script de ruta y menú de Permisos por rol, y build completo*

![F-27 Pantalla de permisos por rol con 85 registros](Reguistro%20visual/ISS-10/F-27-35_permisos-lista.png)
*Pantalla de permisos por rol con 85 registros*

![F-27 Diálogo Nuevo permiso](Reguistro%20visual/ISS-10/F-27-36_permisos-nuevo.png)
*Diálogo Nuevo permiso*

![F-27 Diálogo Editar permiso](Reguistro%20visual/ISS-10/F-27-37_permisos-editar.png)
*Diálogo Editar permiso*

**Ver permisos de un usuario**

![F-27 Código de `user-list.ts` con `openPermissions`](Reguistro%20visual/ISS-10/F-27-38_ver-permisos-codigo-ts.png)
*Código de `user-list.ts` con `openPermissions`*

![F-27 Código de `user-list.html` con el diálogo de permisos](Reguistro%20visual/ISS-10/F-27-39_ver-permisos-codigo-html.png)
*Código de `user-list.html` con el diálogo de permisos*

![F-27 Script que agrega `Tooltip` y build completo](Reguistro%20visual/ISS-10/F-27-40_tooltip-build.png)
*Script que agrega `Tooltip` y build completo*

![F-27 Usuarios con el botón Ver permisos (3 registros)](Reguistro%20visual/ISS-10/F-27-41_usuarios-botones-permisos.png)
*Usuarios con el botón Ver permisos (3 registros)*

![F-27 Diálogo Permisos de elkin: una fila por permiso, con paginación](Reguistro%20visual/ISS-10/F-27-42_ver-permisos-elkin.png)
*Diálogo Permisos de elkin: una fila por permiso, con paginación*

**Pruebas**

![F-27 `ng test`: 16 archivos y 29 pruebas OK](Reguistro%20visual/ISS-10/F-27-43_ng-test-29.png)
*`ng test`: 16 archivos y 29 pruebas OK*

**Corrección: rutas de administración en el servidor**

![F-27 `app.routes.server.ts` con `admin/**` en `RenderMode.Client`](Reguistro%20visual/ISS-10/F-27-14_routes-server-admin.png)
*`app.routes.server.ts` con `admin/**` en `RenderMode.Client`*

**Pruebas de ISS-10**

![F-27 Código de user-api.spec.ts (versión inicial)](Reguistro%20visual/ISS-10/F-27-44_user-api-spec-codigo.png)
*Código de `user-api.spec.ts`. En esta versión la prueba usaba `toBeFalse()`, que Vitest no tiene; luego se cambió a `toBe(false)`*

![F-27 user-api.spec.ts: error de toBeFalse y corrección](Reguistro%20visual/ISS-10/F-27-45_user-api-spec-ok.png)
*Error `toBeFalse` al compilar, corrección con `sed` y 3 pruebas OK*

![F-27 resource-role-api.spec.ts con 2 pruebas OK](Reguistro%20visual/ISS-10/F-27-46_resource-role-api-spec.png)
*`resource-role-api.spec.ts`: el POST envía números y estado; 2 pruebas OK*

![F-27 user-list.spec.ts con 2 pruebas OK](Reguistro%20visual/ISS-10/F-27-47_user-list-spec.png)
*`user-list.spec.ts`: carga de usuarios y diálogo de permisos con una fila por permiso; 2 pruebas OK*

![F-27 ng test completo: 19 archivos y 36 pruebas OK](Reguistro%20visual/ISS-10/F-27-48_ng-test-36.png)
*`ng test`: 19 archivos y 36 pruebas OK, y `ng build` sin errores*

**Modelo RBAC (EVI-10-04)**

![F-27 Diagrama User, RoleUser, Role, ResourceRole y Resource](Reguistro%20visual/ISS-10/F-27-49_diagrama-rbac.png)
*Relación entre tablas: un permiso efectivo exige que RoleUser, Role, ResourceRole y Resource estén ACTIVE*

Incidentes de este paso (ver sección 8): la redirección de `/admin/*` al dashboard, el 403 en permisos por usuario, el token vencido y la ruta de administración que se renderizaba en el servidor sin sesión.

ISS-10 queda completo: pantallas, menú, pruebas y diagrama de la relación entre tablas (EVI-10-04).

---

### F-28 · ISS-11 · Build de producción, calidad y recorrido de verificación (parcial)

Se revisó la fase de cierre del frontend con la guía de ISS-11. Al cierre de esta entrada cumplen: el build de producción, los tipos, las pruebas, la revisión responsive y la accesibilidad básica del menú. El recorrido de 17 pasos está en curso: cumplen los pasos 1 a 3 y 12 y 13; el 11 tiene evidencia parcial.

**Entornos.** `environment.ts` quedó con `production: true`, `appName` y `apiUrl: 'http://localhost:8000/api'`, igual que `environment.development.ts` (`production: false`). Antes, el archivo de producción usaba `127.0.0.1` y no tenía la bandera `production`.

![Grep de entornos, reescritura de `environment.ts` y build inicial](Reguistro%20visual/ISS-11/F-28-01_entornos-y-build-inicial.png)
*Entornos alineados: mismo `apiUrl` y `production` en cada archivo*

**Presupuesto de bundle.** El primer `ng build` terminó con código 0, pero con aviso: el bundle inicial pesó 805.59 kB (542.15 kB `main`, 235.93 kB un chunk compartido y 27.51 kB de estilos) contra el aviso de 750 kB. Las rutas ya usaban `loadComponent` y ninguna pantalla entra de forma estática. El peso viene del arranque: PrimeNG (`api`, `toast`, `panelmenu`, `drawer`, `config`) y el tema `@primeuix/themes/aura`, que se usan en todas las pantallas. Se decidió subir el aviso inicial a 850 kB y dejar el error en 1 MB, y documentar el costo aceptado. El presupuesto `anyComponentStyle` (4 kB / 8 kB) ya estaba configurado.

![Build con aviso de presupuesto: 805.59 kB contra 750 kB](Reguistro%20visual/ISS-11/F-28-02_build-aviso-presupuesto.png)
*Primer build: aviso de presupuesto excedido*

![Rutas del proyecto con `loadComponent`](Reguistro%20visual/ISS-11/F-28-03_rutas-loadcomponent.png)
*Todas las pantallas se cargan de forma diferida*

![Tabla de chunks iniciales y limpieza de marcadores `Zone.Identifier`](Reguistro%20visual/ISS-11/F-28-04_zone-identifier-y-tabla-inicial.png)
*Tabla de chunks iniciales; se eliminaron los marcadores `*Zone.Identifier` que había en `src/`*

![Imports estáticos del arranque](Reguistro%20visual/ISS-11/F-28-05_imports-arranque.png)
*Imports del arranque: PrimeNG y el tema Aura*

![Aviso de presupuesto ajustado a 850 kB y build sin advertencias](Reguistro%20visual/ISS-11/F-28-06_presupuesto-850-build.png)
*Presupuesto a 850 kB y error a 1 MB: build sin advertencias*

**Tipos y pruebas.** `npx tsc -p tsconfig.app.json --noEmit` terminó sin salida y con código 0. `npm test -- --watch=false` pasó con 36 pruebas en 19 archivos. Estos números reemplazan a los 49 pruebas en 26 archivos que indica la guía, que no corresponden a este proyecto.

![tsc con código 0 y arranque de las pruebas](Reguistro%20visual/ISS-11/F-28-07_tsc-y-pruebas-inicio.png)
*`tsc` con código 0 y pruebas en curso*

![Resultado de las pruebas: 19 archivos y 36 pruebas OK](Reguistro%20visual/ISS-11/F-28-08_pruebas-36-en-19.png)
*19 archivos y 36 pruebas OK*

**Responsive y accesibilidad.** A 400 px el menú se abre como Drawer con los grupos Negocio, Salón, Cocina, Domicilios y Seguridad. `document.documentElement.scrollWidth <= clientWidth` devuelve `true`, así que no hay desplazamiento horizontal. Ningún botón de solo icono queda sin nombre accesible (resultado `0`). Con el Drawer abierto, `Tab` llega a la X y `Esc` lo cierra, y el foco vuelve al botón del menú. Pendiente: repetir `Tab` y `Esc` dentro de un `p-dialog` para cerrar AC-11-05.

![Drawer del menú a 400 px con los grupos de Seguridad](Reguistro%20visual/ISS-11/F-28-09_responsive-400-menu.png)
*Menú a 400 px: Drawer con todos los grupos*

![Consola: ningún botón sin nombre accesible](Reguistro%20visual/ISS-11/F-28-10_botones-sin-nombre.png)
*Botones sin nombre accesible: 0*

![Consola: sin desplazamiento horizontal a 400 px](Reguistro%20visual/ISS-11/F-28-11_sin-desplazamiento-horizontal.png)
*Sin desplazamiento horizontal: `true`*

**Recorrido de verificación (guía de 17 pasos).**

- **Paso 1:** `/clientes` sin sesión redirige a `/login?returnUrl=%2Fclientes`.
- **Paso 2:** el login con el usuario admin devuelve a `/clientes`, con el menú de Operación y Seguridad.
- **Paso 3 (CRUD de clientes):** alta con `POST` 201, edición con `PATCH` 200, búsqueda en memoria (pendiente confirmar en Red que no hay petición al escribir), baja con `DELETE` 204 y reactivación con `PATCH` 200. En la baja se encontró un fallo: no existía forma de reactivar desde la pantalla. Se corrigió en F-29.
- **Paso 11 (permisos del mesero, evidencia parcial):** se creó el permiso `GET api/clientes/` para el rol `mesero` (id 111), que es el permiso mínimo para ver clientes. Con sesión de `mesero`, `/pedidos` y `/admin/usuarios` muestran `/forbidden` con el permiso requerido (`GET /api/pedidos/` y `GET /api/users/`), y el menú solo muestra Negocio › Clientes y Cuenta › Mi perfil. Falta confirmar si el criterio del paso 11 pide redirección a otra ruta o si la pantalla `/forbidden` cumple.
- **Paso 12 (vendedor sin escritura):** `mesero` entra a `/clientes`, ve el listado sin el botón "Nuevo cliente" y sin acciones de edición, baja ni reactivación. Como no existe un usuario con rol vendedor, se usa `mesero`.
- **Paso 13 (403 en escritura):** con el token de `mesero`, `POST /api/clientes/` responde 403. El token se obtuvo con `read -s`, así que la contraseña no quedó en el historial.
- **Paso 14 (pendiente):** conceder `POST api/clientes/` al rol `mesero`.

![Paso 1: redirección a login con returnUrl](Reguistro%20visual/ISS-11/F-28-12_paso1-login-returnurl.png)
*Paso 1: `/clientes` redirige a login con `returnUrl`*

![Paso 3: diálogo de nuevo cliente](Reguistro%20visual/ISS-11/F-28-13_paso3-nuevo-cliente.png)
*Paso 3, alta: diálogo de nuevo cliente con los datos de prueba*

![Backend: POST /api/clientes/ responde 201](Reguistro%20visual/ISS-11/F-28-14_backend-post-201.png)
*Alta: `POST /api/clientes/` responde 201*

![Listado de clientes con el cliente nuevo](Reguistro%20visual/ISS-11/F-28-15_paso3-lista.png)
*Listado con 4 registros*

![Diálogo de edición con el teléfono modificado](Reguistro%20visual/ISS-11/F-28-16_paso3-editar.png)
*Edición de teléfono*

![Listado después de la edición](Reguistro%20visual/ISS-11/F-28-17_paso3-editado.png)
*Listado tras la edición*

![Backend: PATCH /api/clientes/4/ responde 200](Reguistro%20visual/ISS-11/F-28-18_backend-patch.png)
*Edición: `PATCH /api/clientes/4/` responde 200*

![Búsqueda "mich" en el listado](Reguistro%20visual/ISS-11/F-28-19_paso3-buscar.png)
*Búsqueda local con "mich" (pendiente confirmar en Red que no hay petición nueva)*

![Confirmación de baja](Reguistro%20visual/ISS-11/F-28-20_paso3-confirmar-baja.png)
*Confirmación de baja*

![Cliente dado de baja: estado Inactivo](Reguistro%20visual/ISS-11/F-28-21_paso3-baja-inactivo.png)
*Baja: estado Inactivo*

![Cabeceras de la baja: DELETE responde 204](Reguistro%20visual/ISS-11/F-28-22_paso3-baja-204.png)
*Baja: `DELETE /api/clientes/4/` responde 204*

![Nuevo permiso GET api/clientes/ para el rol mesero](Reguistro%20visual/ISS-11/F-28-23_paso11-nuevo-permiso-get-clientes.png)
*Permiso `GET api/clientes/` para el rol `mesero`*

![Permisos por rol con GET api/clientes/ de mesero (id 111)](Reguistro%20visual/ISS-11/F-28-24_paso11-permisos-lista-mesero.png)
*Lista de permisos: `GET api/clientes/` asignado a `mesero`*

![Mesero en /forbidden al entrar a /pedidos](Reguistro%20visual/ISS-11/F-28-25_paso11-pedidos-forbidden.png)
*Mesero en `/forbidden`: permiso requerido `GET /api/pedidos/`*

![Mesero en /forbidden al entrar a /admin/usuarios](Reguistro%20visual/ISS-11/F-28-26_paso11-usuarios-forbidden.png)
*Mesero en `/forbidden`: permiso requerido `GET /api/users/`*

![Mesero en /clientes sin botones de escritura](Reguistro%20visual/ISS-11/F-28-27_paso12-clientes-mesero.png)
*Paso 12: listado de clientes sin "Nuevo cliente" ni acciones de edición o baja*

![POST /api/clientes/ como mesero responde 403](Reguistro%20visual/ISS-11/F-28-28_paso13-post-403.png)
*Paso 13: `POST /api/clientes/` con el token de `mesero` responde 403*

**Evidencia adicional de ISS-10.** Validación del formulario "Nuevo usuario" con campos vacíos: los mensajes de error aparecen junto a cada campo.

![Formulario Nuevo usuario con validaciones](Reguistro%20visual/ISS-10/F-27-50_nuevo-usuario-validacion.png)
*Nuevo usuario con campos vacíos: mensajes de validación junto a cada campo*

Pendientes de ISS-11: pasos 4 a 10 del recorrido (CRUD de tipos y productos, venta con dos líneas, detalle y panel, anulación, recarga de sesión y `/forbidden` manual), pasos 14 a 17 (concesión de `POST` a mesero, actualizar permisos, revocación de refresh y cierre de sesión), la prueba de `Tab` y `Esc` en un `p-dialog`, y la prueba de 403 con `API_ACCESS=rbac` en un proceso aparte en el puerto 8011.

### F-29 · ISS-03 · Reactivar cliente desde la pantalla (corrección)

Durante el paso 3 de ISS-11 se encontró que, después de dar de baja un cliente, la pantalla no ofrecía forma de reactivarlo. La causa: el botón de baja tenía `[disabled]="row.status !== 'ACTIVE'"` y no existía ninguna acción para clientes `INACTIVE`. La API sí reactiva con `PATCH`.

Corrección:

- `ClientPayload` (`services/business/client.ts`) gana `status?: 'ACTIVE' | 'INACTIVE'`. Es opcional, así que crear y editar no cambian.
- `getall.ts`: método `reactivate(client)` que llama `service.update(id, { status: 'ACTIVE' })` y recarga la lista.
- `getall.html`: botón verde (`pi pi-replay`) visible solo cuando `row.status === 'INACTIVE'`, protegido con `*appHasPermission="'PATCH /api/clientes/:id/'"`.

Verificación: `tsc` con código 0; en el navegador, el cliente dado de baja (`DELETE` 204) muestra el botón de reactivar, al pulsarlo responde `PATCH /api/clientes/4/` con 200 y la fila vuelve a Activo.

Aclaración sobre la ruta: durante la revisión se sospechó que las claves de permiso estaban mal (`/api/clientes/`). Se comprobó en `backend/apps/client/urls.py` que el backend registra `clientes`, así que las claves del frontend eran correctas. La guía usa `/api/clients/` y estado en minúsculas; este proyecto usa `/api/clientes/` y `ACTIVE`/`INACTIVE`.

![Servicio `ClientService` con `status` opcional en `ClientPayload`](Reguistro%20visual/ISS-03/F-16-06_servicio-payload-status.png)
*`ClientPayload` con `status?` opcional*

![Método `reactivate` en `getall.ts`](Reguistro%20visual/ISS-03/F-16-07_reactivar-codigo-ts.png)
*Método `reactivate` en el componente*

![Botón de reactivar con `@if` para clientes inactivos](Reguistro%20visual/ISS-03/F-16-08_reactivar-codigo-html.png)
*Botón de reactivar visible solo en clientes inactivos*

![Cliente reactivado: fila en Activo y PATCH 200](Reguistro%20visual/ISS-03/F-16-09_reactivar-ok.png)
*Cliente reactivado: `PATCH` 200 y estado Activo*

---

### F-30 · ISS-11 · Roles y permisos en una sola pantalla y menú de login

El diseño pedía que los antiguos Roles, Asignaciones y Permisos por rol quedaran en una sola vista, con la lista de roles a la izquierda y, a la derecha, el nombre, el estado, los usuarios asignados y la matriz de permisos por entidad (C, R, U, D). Se unificó en `/admin/roles-permisos`, y las rutas anteriores redirigen a ella.

Cambios (sin commit). Se había creado un commit local `bf61f4a` por error; se deshizo con `git reset --mixed HEAD~1`. Los cambios quedan sin confirmar en el clon y no hubo push.

- `app.routes.ts`: nueva ruta `admin/roles-permisos` con `permissionGuard` y `GET /api/roles/`. `admin/roles`, `admin/asignaciones` y `admin/permisos` redirigen a ella (`Reguistro visual/ISS-11/F-30-05_app-routes-roles-permisos.png`).
- `components/layout/aside/aside.ts`: en Seguridad queda una sola opción, «Roles y permisos» (`Reguistro visual/ISS-11/F-30-06_aside-seguridad.png`, `Reguistro visual/ISS-11/F-30-12_aside-enlaces.png`).
- `components/admin/rbac/rbac-matrix.ts` (nuevo): funciones puras que usa la pantalla. `entityOf` toma el primer segmento tras `api/`. `buildEntityRows` agrupa solo recursos `ACTIVE`. `cellState` devuelve `none`, `off`, `some` o `all`. `applyCell` y `diffSets` calculan los cambios. `indexByRole` conserva las filas inactivas para poder reactivarlas, y `activeTargets` cuenta solo las activas (`Reguistro visual/ISS-11/F-30-07_rbac-matrix-ts.png`, `Reguistro visual/ISS-11/F-30-13_rbac-matrix-ts-revision.png`).
- `components/admin/rbac/rbac-matrix.spec.ts` (nuevo): 10 pruebas de esas funciones.
- `components/admin/rbac/roles-permissions/roles-permissions.ts`, `.html` y `.css` (nuevos): la pantalla. Lista de roles con `p-multiselect` para usuarios, `p-select` para estado y tabla con casillas por entidad y acción. El modo de creación se activa con `creating()` (`Reguistro visual/ISS-11/F-30-09_roles-permissions-ts.png`, `Reguistro visual/ISS-11/F-30-10_roles-permissions-html.png`, `Reguistro visual/ISS-11/F-30-11_roles-permissions-css.png`).

Cómo guarda la pantalla: compara el borrador con el estado del servidor y envía solo las diferencias. Si la fila ya existe como `INACTIVE`, hace `PATCH` a `ACTIVE` en lugar de `POST`, para no violar la unicidad de `(role, user)` y `(resource, role)`. El botón de guardar se activa solo cuando hay cambios (`dirty`).

Login sin hamburguesa: `header.ts` inyecta `SessionStore`, y `header.html` envuelve el botón de menú en `@if (sessionStore.isAuthenticated())`. Con sesión el botón sigue visible (`Reguistro visual/ISS-11/F-30-01_header-ts.png`, `Reguistro visual/ISS-11/F-30-02_header-html.png`, `Reguistro visual/ISS-11/F-30-03_login-sin-hamburguesa.png`, `Reguistro visual/ISS-11/F-30-04_panel-con-menu.png`).

Verificación:

- `npm test`: 19 archivos y 36 pruebas OK (`Reguistro visual/ISS-11/F-30-08_ng-test-36.png`). Esa captura es anterior al spec nuevo. La ejecución con `rbac-matrix.spec.ts` (10 pruebas más) no quedó capturada en este paquete.
- Rol mesero: la pantalla con ADMIN y MESERO (`Reguistro visual/ISS-11/F-30-14_roles-permisos-admin-mesero.png`) muestra que Leer de Clientes aparece en «parcial» (`Reguistro visual/ISS-11/F-30-15_mesero-leer-parcial.png`). Es el estado real del rol: solo tiene `GET` del listado de clientes, sin detalle. El perfil del mesero (`Reguistro visual/ISS-11/F-30-16_perfil-mesero.png`), el rol con 0 permisos (`Reguistro visual/ISS-11/F-30-17_rol-mesero-sin-permisos.png`) y la lista de roles (`Reguistro visual/ISS-11/F-30-18_lista-roles-con-mesero.png`) muestran el resultado. El usuario confirmó que el comportamiento era el esperado.

![Ruta `admin/roles-permisos` y redirecciones en `app.routes.ts`](Reguistro%20visual/ISS-11/F-30-05_app-routes-roles-permisos.png)
*Una sola ruta y tres redirecciones*

![`aside.ts` con una sola opción en Seguridad](Reguistro%20visual/ISS-11/F-30-06_aside-seguridad.png)
*Menú de Seguridad con «Roles y permisos»*

![`roles-permissions.ts` con imports y estado](Reguistro%20visual/ISS-11/F-30-09_roles-permissions-ts.png)
*Componente de la pantalla unificada*

![Pantalla Roles y permisos con ADMIN y MESERO](Reguistro%20visual/ISS-11/F-30-14_roles-permisos-admin-mesero.png)
*Matriz por entidad con C, R, U y D*

![Rol MESERO: Leer de Clientes en parcial](Reguistro%20visual/ISS-11/F-30-15_mesero-leer-parcial.png)
*Lectura parcial de clientes para el mesero*

![Lista de roles con MESERO](Reguistro%20visual/ISS-11/F-30-18_lista-roles-con-mesero.png)
*Lista de roles con usuarios asignados*

---

## 7. Pruebas

Comando: `npm test -- --watch=false`. Última corrida (2 de noviembre de 2026): 19 archivos y 36 pruebas OK (captura F-28-08).

| Archivo de pruebas | Qué verifica |
|---|---|
| `components/*/getall/getall.spec.ts` (9) | Se crea el componente y pide `GET /<ruta>/` |
| `components/layout/aside/aside.spec.ts` | Se crea el menú lateral |
| `components/layout/header/header.spec.ts` y `footer/footer.spec.ts` | Se crean el encabezado y el pie |
| `app.spec.ts` | Se crea la aplicación |
| `core/guards/rbac.guards.spec.ts` (3) | Guard de permisos concede o redirige a `/forbidden`, y `authGuard` redirige a `/login` |
| `components/layout/aside/aside-filter.spec.ts` (2) | El menú oculta opciones y grupos sin permiso |
| `shared/directives/has-permission.spec.ts` (2) | La directiva `*appHasPermission` muestra u oculta el elemento |
| `services/security/user-api.spec.ts` (3) | Lectura sin contraseña, PATCH sin contraseña y `GET /users/{id}/permissions/` |
| `services/security/resource-role-api.spec.ts` (2) | El POST envía `role`, `resource` y `status` como números; el GET lista asignaciones |
| `components/admin/users/user-list/user-list.spec.ts` (2) | Carga de usuarios y diálogo de permisos con una fila por permiso |

Resultado: **19 archivos y 36 pruebas OK** (16 archivos y 29 pruebas en F-25; 3 archivos y 7 pruebas de ISS-10 en F-27). El ejecutor de pruebas es el que trae Angular 22 por defecto.

---

## 8. Problemas encontrados y cómo se resolvieron

| Problema | Causa | Solución |
|---|---|---|
| `app.css` con error "Unknown word Component" | Se pegó código TypeScript en el CSS | Vaciar `app.css` |
| `No matching export ... ClientService` | El archivo del servicio tenía el código del modelo, y estaba en una carpeta equivocada | Mover y reescribir el servicio en `services/business/` |
| `p-sortIcon` no es un elemento conocido | PrimeNG 22 cambió el selector | Usar `<p-sort-icon>` |
| Tabla con 0 registros y sin error | La base `brasago_django` estaba vacía | Crear datos de ejemplo desde Swagger |
| Aviso rojo "Invalid PrimeUI License" | PrimeNG 22 pide licencia | Configurar la licencia Community (F-07) |
| Encabezados cambiados ("IDENTIFICACIÓN", "Colina baja") y contador en 0 | El traductor de Chrome reescribía el DOM y Angular actualizaba nodos que ya no estaban | `lang="es"`, `translate="no"` y `<meta name="google" content="notranslate">` |
| `No pipe found with name 'currency'` (NG8004) | Se usó `CurrencyPipe` en el HTML de productos sin importarlo en el componente | Agregar `CurrencyPipe` a `imports` y al `import` del archivo |
| `dev-credentials.example.ts` sin el cierre `};` | El `sed` dejó el archivo incompleto, y rompería el build | Reescribirlo completo |
| `/admin/usuarios` redirigía a `/dashboard` | `ng serve` seguía sirviendo un bundle sin la ruta nueva | Reiniciar `npm start` y recargar con Ctrl+Shift+R |
| `GET /api/users/<id>/permissions/` respondía 403 | El recurso nuevo no estaba asignado al rol ADMIN | `python manage.py grant_all_access <usuario>` |
| `KeyError: 'permissions'` al consultar permisos con `curl` | El token de acceso había vencido y la respuesta era un error | Iniciar sesión de nuevo para obtener un token válido |
| Las rutas de administración se redirigían a `/dashboard` al escribir la URL | Angular renderiza la ruta en el servidor (SSR), donde no hay sesión: `permissionGuard` mandaba a `/login` y `guestGuard` al dashboard | `RenderMode.Client` para `admin/**` en `app.routes.server.ts` |
| `toBeFalse` no existe en las pruebas de Angular 22 (Vitest) | Se escribió con la sintaxis de Jasmine | `toBe(false)` |
| El build inicial superó el presupuesto de 750 kB (805.59 kB) | PrimeNG y el tema Aura se cargan en el arranque | Aviso a 850 kB y error en 1 MB, documentado en F-28 |
| Marcadores `*Zone.Identifier` dentro de `src/` y en `dist/` | Archivos de Windows que se copian al descargar | `find src -name "*Zone.Identifier" -delete` |
| `environment.ts` de producción sin `production` y con otro `apiUrl` | Archivo incompleto y distinto del de desarrollo | Reescribirlo con `production: true` y el mismo `apiUrl` |
| No se podía reactivar un cliente desde la pantalla | El botón de baja se deshabilitaba y no había acción para `INACTIVE` | Botón de reactivar y `status?` en `ClientPayload` (F-29) |
| Se creó un commit local sin orden | Commit `bf61f4a` hecho por error durante ISS-11 | Deshecho con `git reset --mixed HEAD~1`; cambios sin confirmar y sin push (F-30) |
| Se supuso la ruta `/api/clients/` y el estado en minúsculas | Se tomaron de la guía sin verificarlos en el backend | Se comprobó en `urls.py`: `clientes` y `ACTIVE`/`INACTIVE` |

### Evidencias de los errores

![`npm start` falla: `app.css` contenía TypeScript](Reguistro%20visual/Errores/P-01-error-css.png)
*`npm start` falla: `app.css` contenía TypeScript*

![Módulos no encontrados: servicio y utilidades en carpetas equivocadas](Reguistro%20visual/Errores/P-02-error-modulos.png)
*Módulos no encontrados: servicio y utilidades en carpetas equivocadas*

![`p-sortIcon` no es un elemento conocido en PrimeNG 22](Reguistro%20visual/Errores/P-03-error-sort-icon.png)
*`p-sortIcon` no es un elemento conocido en PrimeNG 22*

![`No matching export ... ClientService` y su corrección](Reguistro%20visual/Errores/P-04-error-client-service.png)
*`No matching export ... ClientService` y su corrección*

![Traductor de Chrome alterando la tabla: encabezados traducidos y contador en 0](Reguistro%20visual/Errores/P-06-traductor.png)
*Traductor de Chrome alterando la tabla: "IDENTIFICACIÓN", "Colina baja" y contador en 0*

![Corrección del traductor: `lang="es"`, `translate="no"` y `notranslate`](Reguistro%20visual/Errores/P-05-fix-traductor.png)
*Corrección del traductor: `lang="es"`, `translate="no"` y `notranslate`*

---

## 9. Cómo ejecutarlo

```bash
# 1. Backend
cd backend && python manage.py runserver

# 2. Frontend
cd frontend
cp src/environments/dev-credentials.example.ts src/environments/dev-credentials.ts   # poner la clave real
cp src/environments/primeng-license.example.ts src/environments/primeng-license.ts   # poner la licencia Community
npm install
npm start          # http://localhost:4200
npm test           # pruebas
npm run build      # build de producción
```

El login ahora es real: en `/login` se escribe el usuario y la contraseña del backend (JWT). `dev-credentials.ts` ya no se usa para iniciar sesión; solo lo usa `seed_frontend.py` si se pide la clave por consola. El usuario debe tener acceso a la API (por ejemplo con `python manage.py grant_all_access <usuario>`).

---

## 10. Pendiente

- ISS-11: recorrido de pasos 4 a 10 y 14 a 17, prueba de `Tab` y `Esc` en un `p-dialog` (AC-11-05), prueba de 403 con `API_ACCESS=rbac` en el puerto 8011, y los casos de la tabla de resolución de problemas, incluido el 409 (AC-11-06 y AC-11-07).
- Antes de publicar la bitácora: difuminar las contraseñas visibles en F-27-02 y F-27-05, y retirar las contraseñas de los documentos de instalación de base de datos que están en el repositorio.
- Decidir qué desplegable del menú aparece al iniciar sesión (los grupos con `expanded: true` en `aside.ts` o el cajón `mobileOpen`) y aplicar el ajuste.
- Verificar en navegador el guardado y la carga de Roles y permisos; las capturas de F-30 muestran la pantalla, no el flujo de guardar.
- Commit y push del trabajo a `motores` cuando termine ISS-11, solo con orden explícita del autor.
- Pantalla de permisos de la guía: resuelta en F-25. El backend sí tiene RBAC; se expuso `GET /api/auth/permissions/` y el frontend filtra menú, botones y rutas con esos permisos.
- Pantallas de sedes y mesas, cuando el backend exponga sus endpoints.
