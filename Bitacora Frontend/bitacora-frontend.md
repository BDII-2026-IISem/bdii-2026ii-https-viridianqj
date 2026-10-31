# Bitácora del frontend de BrasaGo (Angular)

Registro del avance del frontend de **BrasaGo** (sistema omnicanal de restaurante) siguiendo la guía **Angular 20 · consumo de APIs Django** de Tecnogua, sin la parte de autenticación. Cada paso resume qué se hizo, qué se adaptó respecto a la guía, cómo se verificó y qué capturas lo respaldan.

| | |
|---|---|
| **Proyecto** | BrasaGo, Proyectos Integradores 2026-II (Desarrollo Web) |
| **Autor** | Elkin Eliecer Aguas Giraldo |
| **Alcance** | Estructura por componentes, plantilla (encabezado, menú lateral y pie), y listado ("mostrar") de las 9 entidades del negocio desde la API Django |
| **Guía de referencia** | [Angular 20 · APIs con Django](https://tecnogua.com/academic/site/frontend/angular20/apis_django/), con la instalación y el cliente Django del mismo sitio |
| **Backend consumido** | API REST de BrasaGo (Django 5.2 + DRF), `http://127.0.0.1:8000/api` |
| **Pruebas** | 29 pruebas OK en 16 archivos (`ng test`), ver sección 7 |
| **Fecha de cierre** | 31 de octubre de 2026 |

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
        ├── services/                   api.ts (BaseApi)
        │   └── business/               un servicio por entidad
        └── components/
            ├── layout/                 header, aside, footer
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

![F-00 Angular CLI 22.2.4, Node 22.23.4 y npm 10.9.9](Reguistro%20visual/F-00-01-versiones.png)
*Angular CLI 22.2.4, Node 22.23.4 y npm 10.9.9*

![F-00 Backend en marcha y recursos concedidos al usuario de desarrollo](Reguistro%20visual/F-00-02-backend-en-marcha.png)
*Backend en marcha y recursos concedidos al usuario de desarrollo*


### F-01 · ISS-01 · Proyecto Angular, PrimeNG y Tailwind

Se creó el proyecto `front-brasago` con Angular 22 (CSS, enrutamiento y SSR), y se instalaron PrimeNG, `@primeuix/themes`, PrimeIcons y Tailwind 4 (configurado en `.postcssrc.json` y `styles.css`). Se generaron los `environments` con la URL de la API.

![F-01 `ng new front-brasago`](Reguistro%20visual/F-01-01-ng-new.png)
*`ng new front-brasago`*

![F-01 Archivos creados por `ng new`](Reguistro%20visual/F-01-02-ng-new-archivos.png)
*Archivos creados por `ng new`*

![F-01 Instalación de PrimeNG, temas e iconos](Reguistro%20visual/F-01-03-instalar-primeng.png)
*Instalación de PrimeNG, temas e iconos*

![F-01 Instalación de Tailwind y `.postcssrc.json`](Reguistro%20visual/F-01-04-instalar-tailwind.png)
*Instalación de Tailwind y `.postcssrc.json`*

![F-01 `styles.css` con Tailwind y PrimeIcons](Reguistro%20visual/F-01-05-styles-css.png)
*`styles.css` con Tailwind y PrimeIcons*

![F-01 `ng generate environments`](Reguistro%20visual/F-01-06-generate-environments.png)
*`ng generate environments`*

![F-01 `environment.ts` con la URL de la API](Reguistro%20visual/F-01-07-environment-ts.png)
*`environment.ts` con la URL de la API*

![F-01 `angular.json`](Reguistro%20visual/F-01-08-angular-json.png)
*`angular.json`*

![F-01 `app.ts` inicial](Reguistro%20visual/F-01-09-app-ts-inicial.png)
*`app.ts` inicial*

![F-01 `app.config.ts` con el tema Aura de PrimeNG](Reguistro%20visual/F-01-10-app-config-primeng.png)
*`app.config.ts` con el tema Aura de PrimeNG*


### F-02 · ISS-01A · Plantilla: encabezado, menú lateral y pie

Se generaron los componentes `header`, `aside` y `footer` en `components/layout/`. El menú lateral usa `PanelMenu` de PrimeNG con cuatro grupos (Negocio, Salón, Cocina y Domicilios) y `routerLink` en cada opción. `app.html` los organiza con Tailwind: encabezado arriba, menú a la izquierda, contenido en el centro (`router-outlet`) y pie abajo.

![F-02 Generación de los tres componentes con `ng generate component`](Reguistro%20visual/F-02-01-ng-generate-layout.png)
*Generación de los tres componentes con `ng generate component`*

![F-02 `header.ts`](Reguistro%20visual/F-02-02-header-ts.png)
*`header.ts`*

![F-02 `header.html`](Reguistro%20visual/F-02-03-header-html.png)
*`header.html`*

![F-02 `footer.ts`](Reguistro%20visual/F-02-04-footer-ts.png)
*`footer.ts`*

![F-02 `footer.html`](Reguistro%20visual/F-02-05-footer-html.png)
*`footer.html`*

![F-02 `aside.ts` con los grupos del menú](Reguistro%20visual/F-02-06-aside-ts.png)
*`aside.ts` con los grupos del menú*

![F-02 `aside.html` con `p-panelmenu`](Reguistro%20visual/F-02-07-aside-html.png)
*`aside.html` con `p-panelmenu`*

![F-02 `app.ts` importando los tres componentes](Reguistro%20visual/F-02-08-app-ts.png)
*`app.ts` importando los tres componentes*

![F-02 `app.html` con la estructura de la página](Reguistro%20visual/F-02-09-app-html.png)
*`app.html` con la estructura de la página*

![F-02 Plantilla completa en el navegador](Reguistro%20visual/F-02-10-plantilla-navegador.png)
*Plantilla completa en el navegador*


### F-03 · ISS-01 · Arranque de la aplicación

Primera ejecución con `npm start`: la aplicación abre en `localhost:4200`.

![F-03 Página inicial de Angular funcionando](Reguistro%20visual/F-03-01-primer-arranque.png)
*Página inicial de Angular funcionando*


### F-04 · ISS-02 · Acceso a la API en desarrollo

Todas las rutas de negocio exigen JWT. Para no construir la pantalla de login (fuera del alcance), el servicio `DevAuth` inicia sesión con un usuario de desarrollo y guarda el token. El interceptor `devAuthInterceptor` añade `Authorization: Bearer` a las peticiones a la API y, ante un 401, vuelve a iniciar sesión y reintenta una vez. Las credenciales viven en un archivo fuera de git.

![F-04 `environment.ts` con `apiUrl`](Reguistro%20visual/F-04-01-environment-api.png)
*`environment.ts` con `apiUrl`*

![F-04 `dev-auth.ts`](Reguistro%20visual/F-04-02-dev-auth.png)
*`dev-auth.ts`*

![F-04 `dev-auth.interceptor.ts`](Reguistro%20visual/F-04-03-dev-auth-interceptor.png)
*`dev-auth.interceptor.ts`*

![F-04 `app.config.ts` registrando el interceptor](Reguistro%20visual/F-04-04-app-config-interceptor.png)
*`app.config.ts` registrando el interceptor*


### F-05 · ISS-02 · Base del consumo de la API

`BaseApi<T>` concentra el `getAll()` contra `environment.apiUrl`; cada servicio solo declara su `path`. `shared/state-severity.ts` traduce los estados (`ACTIVE`, `PENDIENTE`, etc.) a etiqueta y color del `p-tag`.

![F-05 Modelo `ClientI`](Reguistro%20visual/F-05-01-modelo-cliente.png)
*Modelo `ClientI`*

![F-05 `BaseApi<T>`](Reguistro%20visual/F-05-02-base-api.png)
*`BaseApi<T>`*

![F-05 `ClientService` con el path `clientes`](Reguistro%20visual/F-05-03-servicio-clientes.png)
*`ClientService` con el path `clientes`*

![F-05 `state-severity.ts`](Reguistro%20visual/F-05-04-state-severity.png)
*`state-severity.ts`*


### F-06 · ISS-03 · Listado de clientes

Primer listado completo con tabla, paginador, ordenamiento y botón Actualizar. Al inicio salió con 0 registros porque la base estaba vacía; se crearon dos clientes desde Swagger y aparecieron. Las peticiones `login/` y `clientes/` responden 200.

![F-06 `getall.ts` del componente de clientes](Reguistro%20visual/F-06-01-getall-ts.png)
*`getall.ts` del componente de clientes*

![F-06 `getall.html` con `p-table`](Reguistro%20visual/F-06-02-getall-html.png)
*`getall.html` con `p-table`*

![F-06 `app.routes.ts` con la ruta `clientes` (carga perezosa)](Reguistro%20visual/F-06-03-rutas.png)
*`app.routes.ts` con la ruta `clientes` (carga perezosa)*

![F-06 `npm start` compila sin errores](Reguistro%20visual/F-06-04-npm-start-ok.png)
*`npm start` compila sin errores*

![F-06 Clientes con 0 registros (base vacía)](Reguistro%20visual/F-06-05-clientes-vacio.png)
*Clientes con 0 registros (base vacía)*

![F-06 Creación de un cliente desde Swagger](Reguistro%20visual/F-06-06-swagger-post-clientes.png)
*Creación de un cliente desde Swagger*

![F-06 Pestaña Network con `login/` y `clientes/` respondiendo](Reguistro%20visual/F-06-07-network.png)
*Pestaña Network con `login/` y `clientes/` respondiendo*

![F-06 Clientes con 2 registros](Reguistro%20visual/F-06-08-clientes-con-datos.png)
*Clientes con 2 registros*


### F-07 · ISS-01 · Licencia de PrimeNG

PrimeNG 22 mostraba el aviso rojo "Invalid PrimeUI License". Se configuró la licencia gratuita Community en `providePrimeNG({ license })`, leída desde `environments/primeng-license.ts` (archivo fuera de git).

![F-07 `app.config.ts` con `license: primengLicense`](Reguistro%20visual/F-07-01-app-config-licencia.png)
*`app.config.ts` con `license: primengLicense`*

![F-07 Aplicación sin el aviso de licencia](Reguistro%20visual/F-07-02-sin-aviso.png)
*Aplicación sin el aviso de licencia*


### F-08 · ISS-05 · Listado de productos

Modelo, servicio (`productos`), componente y ruta. El precio se formatea en pesos colombianos con `CurrencyPipe`. Se crearon tres productos desde Swagger.

![F-08 Modelo `ProductI` y `ProductService`](Reguistro%20visual/F-08-01-modelo-y-servicio.png)
*Modelo `ProductI` y `ProductService`*

![F-08 `getall.ts` de productos](Reguistro%20visual/F-08-02-getall-ts.png)
*`getall.ts` de productos*

![F-08 `getall.html` de productos](Reguistro%20visual/F-08-03-getall-html.png)
*`getall.html` de productos*

![F-08 `app.routes.ts` con `clientes` y `productos`](Reguistro%20visual/F-08-04-rutas.png)
*`app.routes.ts` con `clientes` y `productos`*

![F-08 Creación de un producto desde Swagger](Reguistro%20visual/F-08-05-swagger-post-productos.png)
*Creación de un producto desde Swagger*

![F-08 Listado de productos](Reguistro%20visual/F-08-06-productos.png)
*Listado de productos*


### F-09 · ISS-06 · Listado de pedidos con detalle

Cada pedido de la API trae una lista `details`. La fila principal muestra fecha, cliente, sede, mesa, canal, total y estado. Con `pRowToggler` se abre la plantilla `#expandedrow`, que recorre `row.details` con `@for` y dibuja una tabla con producto, cantidad, precio unitario, total y notas. Un pedido necesita una sede, que se creó desde el Django Admin porque la API no tiene endpoint para sedes.

![F-09 Modelos `OrderI` y `OrderDetailI`](Reguistro%20visual/F-09-01-modelo-pedido.png)
*Modelos `OrderI` y `OrderDetailI`*

![F-09 `OrderService`](Reguistro%20visual/F-09-02-servicio-pedidos.png)
*`OrderService`*

![F-09 `getall.ts` de pedidos](Reguistro%20visual/F-09-03-getall-ts.png)
*`getall.ts` de pedidos*

![F-09 `getall.html` con la fila desplegable `#expandedrow`](Reguistro%20visual/F-09-04-getall-html-detalle.png)
*`getall.html` con la fila desplegable `#expandedrow`*

![F-09 `app.routes.ts` con la ruta `pedidos`](Reguistro%20visual/F-09-05-rutas.png)
*`app.routes.ts` con la ruta `pedidos`*

![F-09 Sede creada en el Django Admin](Reguistro%20visual/F-09-06-admin-sede.png)
*Sede creada en el Django Admin*

![F-09 Creación de un pedido desde Swagger](Reguistro%20visual/F-09-07-swagger-post-pedidos.png)
*Creación de un pedido desde Swagger*

![F-09 Listado de pedidos con el detalle del pedido #3 desplegado](Reguistro%20visual/F-09-08-pedidos.png)
*Listado de pedidos (aquí se ve el problema del traductor, corregido en la sección 8)*


### F-10 · Extra BrasaGo · Listados de pagos y reservas

Mismo patrón: modelo, servicio, componente y ruta. Las capturas finales se tomaron con los datos de ejemplo del paso F-15.

![F-10 Modelo y servicio de pagos, y generación del componente](Reguistro%20visual/F-10-01-pagos-modelo-servicio.png)
*Modelo y servicio de pagos, y generación del componente*

![F-10 `getall.ts` de pagos](Reguistro%20visual/F-10-02-pagos-getall-ts.png)
*`getall.ts` de pagos*

![F-10 `getall.html` de pagos](Reguistro%20visual/F-10-03-pagos-getall-html.png)
*`getall.html` de pagos*

![F-10 Modelo y servicio de reservas](Reguistro%20visual/F-10-04-reservas-modelo-servicio.png)
*Modelo y servicio de reservas*

![F-10 `getall.ts` de reservas](Reguistro%20visual/F-10-05-reservas-getall-ts.png)
*`getall.ts` de reservas*

![F-10 `getall.html` de reservas](Reguistro%20visual/F-10-06-reservas-getall-html.png)
*`getall.html` de reservas*

![F-10 `app.routes.ts` con cinco pantallas](Reguistro%20visual/F-10-07-rutas.png)
*`app.routes.ts` con cinco pantallas*

![F-10 Listado de pagos (5 registros)](Reguistro%20visual/F-10-08-pagos.png)
*Listado de pagos (5 registros)*

![F-10 Listado de reservas (3 registros)](Reguistro%20visual/F-10-09-reservas.png)
*Listado de reservas (3 registros)*


### F-11 · Extra BrasaGo · Listados de insumos, recetas, domiciliarios y entregas

Los cuatro siguen el mismo patrón. Los servicios se generaron con un bucle de shell, porque solo cambian el nombre y la ruta. Las capturas finales se tomaron con los datos de ejemplo del paso F-15.

![F-11 Modelos de insumos, recetas, domiciliarios y entregas](Reguistro%20visual/F-11-01-modelos.png)
*Modelos de insumos, recetas, domiciliarios y entregas*

![F-11 Bucle que genera los cuatro servicios, y `ls` de modelos y servicios](Reguistro%20visual/F-11-02-bucle-servicios.png)
*Bucle que genera los cuatro servicios, y `ls` de modelos y servicios*

![F-11 Generación de los componentes](Reguistro%20visual/F-11-03-ng-generate.png)
*Generación de los componentes*

![F-11 `getall.ts` de insumos](Reguistro%20visual/F-11-04-insumos-getall-ts.png)
*`getall.ts` de insumos*

![F-11 `getall.html` de insumos](Reguistro%20visual/F-11-05-insumos-getall-html.png)
*`getall.html` de insumos*

![F-11 `getall.ts` de recetas](Reguistro%20visual/F-11-06-recetas-getall-ts.png)
*`getall.ts` de recetas*

![F-11 `getall.html` de recetas](Reguistro%20visual/F-11-07-recetas-getall-html.png)
*`getall.html` de recetas*

![F-11 `getall.ts` de domiciliarios](Reguistro%20visual/F-11-08-domiciliarios-getall-ts.png)
*`getall.ts` de domiciliarios*

![F-11 `getall.html` de domiciliarios](Reguistro%20visual/F-11-09-domiciliarios-getall-html.png)
*`getall.html` de domiciliarios*

![F-11 `getall.ts` de entregas](Reguistro%20visual/F-11-10-entregas-getall-ts.png)
*`getall.ts` de entregas*

![F-11 `getall.html` de entregas](Reguistro%20visual/F-11-11-entregas-getall-html.png)
*`getall.html` de entregas*

![F-11 `app.routes.ts` con las nueve pantallas](Reguistro%20visual/F-11-12-rutas.png)
*`app.routes.ts` con las nueve pantallas*

![F-11 Listado de insumos (5 registros)](Reguistro%20visual/F-11-13-insumos.png)
*Listado de insumos (5 registros)*

![F-11 Listado de recetas (6 registros)](Reguistro%20visual/F-11-14-recetas.png)
*Listado de recetas (6 registros)*

![F-11 Listado de domiciliarios (3 registros)](Reguistro%20visual/F-11-15-domiciliarios.png)
*Listado de domiciliarios (3 registros)*

![F-11 Listado de entregas (2 registros)](Reguistro%20visual/F-11-16-entregas.png)
*Listado de entregas (2 registros)*


### F-12 · Transversal · Pruebas automáticas

Los `spec.ts` generados por Angular fallan cuando el componente usa `HttpClient`. Se reescribieron: cada `getall` comprueba que el componente se crea y que pide `GET /<ruta>/` (con `HttpTestingController` y `flush([])`). También se probaron `App` y el menú lateral. Resultado: **13 archivos y 22 pruebas OK**.

![F-12 Bucle que genera los `spec.ts` de las nueve pantallas](Reguistro%20visual/F-12-01-bucle-specs.png)
*Bucle que genera los `spec.ts` de las nueve pantallas*

![F-12 `app.spec.ts`](Reguistro%20visual/F-12-02-app-spec.png)
*`app.spec.ts`*

![F-12 `aside.spec.ts`](Reguistro%20visual/F-12-03-aside-spec.png)
*`aside.spec.ts`*

![F-12 `ng test`: 13 archivos y 22 pruebas OK](Reguistro%20visual/F-12-04-ng-test.png)
*`ng test`: 13 archivos y 22 pruebas OK*


### F-13 · Transversal · Build de producción

`ng build` termina sin errores: una *chunk* por pantalla (carga perezosa) y 9 rutas prerenderizadas.

![F-13 `ng build` sin errores](Reguistro%20visual/F-13-01-ng-build.png)
*`ng build` sin errores*


### F-14 · Transversal · Repositorio y manejo de secretos

`dev-credentials.ts` y `primeng-license.ts` están en `.gitignore`. Se publican archivos `.example.ts` con valores falsos para que quien clone el repositorio pueda compilar. Antes de copiar el proyecto al repositorio se verificó que ninguna clave viaje en él.

![F-14 Comprobación del `.gitignore` y creación de los archivos de ejemplo](Reguistro%20visual/F-14-01-gitignore-y-ejemplos.png)
*Comprobación del `.gitignore` y creación de los archivos de ejemplo*

![F-14 Archivo de ejemplo corregido y build posterior](Reguistro%20visual/F-14-02-ejemplo-y-build.png)
*Archivo de ejemplo corregido y build posterior*

![F-14 Copia del frontend al repositorio sin `node_modules`, `dist` ni secretos](Reguistro%20visual/F-14-03-copia-a-motores.png)
*Copia del frontend al repositorio sin `node_modules`, `dist` ni secretos*

![F-14 Verificación: la licencia no está en el repositorio](Reguistro%20visual/F-14-04-verificacion.png)
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

![F-15 Creación de las mesas](Reguistro%20visual/F-15-01-mesas.png)
*Creación de las mesas desde el shell de Django*

![F-15 Ejecución del script](Reguistro%20visual/F-15-02-script.png)
*Ejecución de `seed_frontend.py`: un `OK` por cada registro creado*


### F-16 · ISS-03 · CRUD de clientes (adaptado)

Se amplió el listado de clientes con alta, edición, baja lógica y búsqueda. El servicio `ClientService` agrega `create`, `update` y `remove` sobre `/api/clientes/` (`POST`, `PATCH` y `DELETE`). El componente `getall` usa un formulario reactivo dentro de un `p-dialog`, que sirve tanto para alta como para edición.

Adaptaciones frente a la guía: la ruta es `/api/clientes/` (no `/api/clients/`), el estado es `ACTIVE`/`INACTIVE`, y la confirmación de baja usa el cuadro nativo `confirm()`. Los errores del backend (por ejemplo, documento duplicado) se muestran dentro del diálogo.

![Diálogo "Nuevo cliente" con validación de nombre corto](Reguistro%20visual/F-16-01-nombre-corto.png)
*Diálogo "Nuevo cliente" con validación de nombre corto*

![Búsqueda por "laura" en el listado de clientes](Reguistro%20visual/F-16-02-buscar.png)
*Búsqueda por "laura" en el listado de clientes*

![Error del backend por número de documento duplicado, mostrado en el diálogo](Reguistro%20visual/F-16-03-documento-duplicado.png)
*Error del backend por número de documento duplicado, mostrado en el diálogo*

![Cliente dado de baja: el estado queda como Inactivo](Reguistro%20visual/F-16-04-baja.png)
*Cliente dado de baja: el estado queda como Inactivo*

![`ng build` sin errores](Reguistro%20visual/F-16-05-ng-build.png)
*`ng build` sin errores*

### F-17 · ISS-05 · CRUD de productos (adaptado)

Se amplió el listado de productos con alta, edición, baja lógica y búsqueda. `ProductService` agrega `create`, `update` y `remove` sobre `/api/productos/`. El formulario valida SKU (2 a 50 caracteres), nombre (2 a 150), descripción opcional y precio no negativo, y lo envía como texto decimal, como lo espera el backend.

Adaptaciones frente a la guía: BrasaGo no tiene stock ni tipo de producto en el diagrama, así que se omiten las filas en ámbar por stock bajo, el selector de tipo y el interruptor de disponibles. El precio se muestra en pesos colombianos. La baja usa el mismo patrón que clientes.

![Diálogo "Nuevo producto" con validación de SKU corto](Reguistro%20visual/F-17-01-sku-corto.png)
*Diálogo "Nuevo producto" con validación de SKU corto*

![Producto nuevo en la tabla, con precio en pesos](Reguistro%20visual/F-17-02-producto-nuevo.png)
*Producto nuevo en la tabla, con precio en pesos*

![Error del backend por SKU duplicado, mostrado en el diálogo](Reguistro%20visual/F-17-03-sku-duplicado.png)
*Error del backend por SKU duplicado, mostrado en el diálogo*

![Producto dado de baja: el estado queda como Inactivo](Reguistro%20visual/F-17-04-baja.png)
*Producto dado de baja: el estado queda como Inactivo*

![`ng build` sin errores](Reguistro%20visual/F-17-05-ng-build.png)
*`ng build` sin errores*


### F-18 · Transversal · Pruebas después de los CRUD

Tras agregar alta, edición, baja y búsqueda, se volvió a ejecutar `npx ng test --no-watch`. Resultado: **13 archivos y 22 pruebas OK**, sin fallos. Las pruebas de `getall` de clientes y productos siguen pasando con el formulario y el servicio nuevos.

![F-18 ng test después de los CRUD](Reguistro%20visual/F-18-01-ng-test.png)
*`ng test` con 13 archivos y 22 pruebas OK*


### F-19 · ISS-06 · Registro de pedidos desde la pantalla (adaptado)

El listado de pedidos suma un diálogo "Nuevo pedido" con un borrador hecho con signals (sin `FormGroup`, como pide la guía). El cliente es opcional, el canal puede ser Mesa, Recogida o Domicilio, y cada línea se agrega con producto y cantidad. El servicio `OrderService.create` envía `POST /api/pedidos/` con `clientId`, `branchId`, `tableId`, `channel` e `items`.

Reglas en el cliente: al menos un producto, cantidad entero mayor o igual a 1, sin productos repetidos y mesa obligatoria en canal Mesa. El total lo calcula el backend; en el diálogo solo se muestra un subtotal estimado.

Adaptaciones frente a la guía: no hay stock, impuestos ni descuentos en el diagrama, así que se omiten los avisos de stock. La sede y las mesas son constantes del frontend (`shared/venue.ts`), porque la API no tiene endpoints para ellas. La pantalla de venta se convierte en el registro de pedido.

![Diálogo "Nuevo pedido" con una línea y el subtotal estimado](Reguistro%20visual/F-19-01-dialogo-subtotal.png)
*Diálogo "Nuevo pedido" con una línea y el subtotal estimado*

![Aviso de producto repetido en el borrador](Reguistro%20visual/F-19-02-producto-repetido.png)
*Aviso de producto repetido en el borrador*

![Aviso de mesa obligatoria para un pedido en mesa](Reguistro%20visual/F-19-03-mesa-obligatoria.png)
*Aviso de mesa obligatoria para un pedido en mesa*

![Pedido nuevo en el listado, con su detalle desplegado](Reguistro%20visual/F-19-04-pedido-expandido.png)
*Pedido nuevo en el listado, con su detalle desplegado*

![`ng build` sin errores](Reguistro%20visual/F-19-05-ng-build.png)
*`ng build` sin errores*

### F-20 · ISS-07 · Detalle de pedido y anulación (adaptado)

Se crea la pantalla `/pedidos/:id` con la cabecera del pedido (fecha, cliente, sede, mesa, canal, estados y total) y sus líneas. El número del pedido en el listado enlaza a esa pantalla. La anulación llama a `DELETE /api/pedidos/{id}/`, pide confirmación, y al terminar recarga el pedido: queda en estado Cancelado y el botón de anular se oculta.

Adaptaciones frente a la guía: en BrasaGo no hay endpoint de líneas separado, así que el detalle usa los `details` que ya trae el pedido. No hay stock, así que el panel de stock bajo no aplica (se reemplaza por pedidos de hoy, pagos pendientes y entregas en camino). La ruta `pedidos/:id` se marca como renderizado en cliente (`app.routes.server.ts`), porque depende de un parámetro que no se puede prerenderizar.

![Detalle del pedido #7 con el botón Anular visible](Reguistro%20visual/F-20-01-detalle-con-anular.png)
*Detalle del pedido #7 con el botón Anular visible*

![Mismo pedido después de anularlo: estado Cancelado, registro Inactivo y botón oculto](Reguistro%20visual/F-20-02-anulado.png)
*Mismo pedido después de anularlo: estado Cancelado, registro Inactivo y botón oculto*

![Listado de pedidos con el pedido #7 en estado Cancelado](Reguistro%20visual/F-20-03-listado-cancelado.png)
*Listado de pedidos con el pedido #7 en estado Cancelado*

![`ng build` sin errores después del cambio de renderizado](Reguistro%20visual/F-20-04-ng-build.png)
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

![F-25 Menú de sinpermisos: solo Cuenta › Mi perfil](Reguistro%20visual/F-25-01-menu-sinpermisos.png)
*Menú de `sinpermisos`: solo el grupo Cuenta con Mi perfil (Captura 18)*

![F-25 Acceso denegado al entrar a /pedidos](Reguistro%20visual/F-25-02-forbidden-pedidos.png)
*`sinpermisos` entra a /pedidos y ve la pantalla de acceso denegado con `GET /api/pedidos/`*

![F-25 Menú completo de elkin](Reguistro%20visual/F-25-03-menu-elkin.png)
*Menú completo del usuario `elkin` (Captura 20)*

![F-25 Build y 22 pruebas tras el menú filtrado](Reguistro%20visual/F-25-04-build-menu.png)
*`ng build` sin errores y pruebas en verde tras filtrar el menú*

![F-25 Pruebas tras la directiva de permisos](Reguistro%20visual/F-25-05-ng-test-directiva.png)
*`ng test` con 24 pruebas tras agregar `*appHasPermission`*

![F-25 Botones de Clientes con elkin](Reguistro%20visual/F-25-06-clientes-elkin.png)
*Clientes con `elkin`: Nuevo cliente, editar y eliminar visibles (Captura 21)*

![F-25 Botones de Productos con elkin](Reguistro%20visual/F-25-07-productos-elkin.png)
*Productos con `elkin`: Nuevo producto, editar y eliminar visibles*

![F-25 Botón Nuevo pedido con elkin](Reguistro%20visual/F-25-08-pedidos-elkin.png)
*Pedidos con `elkin`: botón Nuevo pedido visible (Captura 23)*

![F-25 Pruebas finales de ISS-09: 29 OK](Reguistro%20visual/F-25-09-ng-test-29.png)
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

![F-26 Encabezado con el logo de BrasaGo y la línea naranja](Reguistro%20visual/F-26-01-encabezado-logo.png)
*Encabezado con el logo y la línea naranja de marca*

![F-26 Botones y menú con el naranja de marca](Reguistro%20visual/F-26-02-tema-naranja.png)
*Botón principal y estado activo del menú con el naranja de la marca*

![F-26 app.config.ts con el preset de marca](Reguistro%20visual/F-26-03-app-config-preset.png)
*`app.config.ts` con `definePreset` y la escala naranja*

## 7. Pruebas

Comando: `npx ng test --no-watch`.

| Archivo de pruebas | Qué verifica |
|---|---|
| `components/*/getall/getall.spec.ts` (9) | Se crea el componente y pide `GET /<ruta>/` |
| `components/layout/aside/aside.spec.ts` | Se crea el menú lateral |
| `components/layout/header/header.spec.ts` y `footer/footer.spec.ts` | Se crean el encabezado y el pie |
| `app.spec.ts` | Se crea la aplicación |
| `core/guards/rbac.guards.spec.ts` (3) | Guard de permisos concede o redirige a `/forbidden`, y `authGuard` redirige a `/login` |
| `components/layout/aside/aside-filter.spec.ts` (2) | El menú oculta opciones y grupos sin permiso |
| `shared/directives/has-permission.spec.ts` (2) | La directiva `*appHasPermission` muestra u oculta el elemento |

Resultado: **16 archivos y 29 pruebas OK** (ver F-25). El ejecutor de pruebas es el que trae Angular 22 por defecto.

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

### Evidencias de los errores

![`npm start` falla: `app.css` contenía TypeScript](Reguistro%20visual/P-01-error-css.png)
*`npm start` falla: `app.css` contenía TypeScript*

![Módulos no encontrados: servicio y utilidades en carpetas equivocadas](Reguistro%20visual/P-02-error-modulos.png)
*Módulos no encontrados: servicio y utilidades en carpetas equivocadas*

![`p-sortIcon` no es un elemento conocido en PrimeNG 22](Reguistro%20visual/P-03-error-sort-icon.png)
*`p-sortIcon` no es un elemento conocido en PrimeNG 22*

![`No matching export ... ClientService` y su corrección](Reguistro%20visual/P-04-error-client-service.png)
*`No matching export ... ClientService` y su corrección*

![Traductor de Chrome alterando la tabla: encabezados traducidos y contador en 0](Reguistro%20visual/P-06-traductor.png)
*Traductor de Chrome alterando la tabla: "IDENTIFICACIÓN", "Colina baja" y contador en 0*

![Corrección del traductor: `lang="es"`, `translate="no"` y `notranslate`](Reguistro%20visual/P-05-fix-traductor.png)
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

- Pantallas de administración (ISS-10): usuarios, roles, recursos y permisos por usuario.
- Build de producción, presupuestos, accesibilidad y checklist final (ISS-11).
- Commit y push del trabajo a `motores` cuando termine ISS-11.
- Pantalla de permisos de la guía: resuelta en F-25. El backend sí tiene RBAC; se expuso `GET /api/auth/permissions/` y el frontend filtra menú, botones y rutas con esos permisos.
- Pantallas de sedes y mesas, cuando el backend exponga sus endpoints.
