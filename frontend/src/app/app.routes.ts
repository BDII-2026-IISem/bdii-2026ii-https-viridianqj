import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'dashboard' },
  {
    path: 'login',
    title: 'Iniciar sesión',
    loadComponent: () => import('./components/auth/login/login').then((m) => m.Login),
  },
  {
    path: 'perfil',
    title: 'Perfil',
    loadComponent: () => import('./components/auth/profile/profile').then((m) => m.Profile),
  },
  {
    path: 'dashboard',
    title: 'Panel',
    loadComponent: () => import('./components/dashboard/dashboard').then((m) => m.Dashboard),
  },
  {
    path: 'clientes',
    title: 'Clientes',
    loadComponent: () => import('./components/client/getall/getall').then((m) => m.Getall),
  },
  {
    path: 'productos',
    title: 'Productos',
    loadComponent: () => import('./components/product/getall/getall').then((m) => m.Getall),
  },
  {
    path: 'pedidos',
    title: 'Pedidos',
    loadComponent: () => import('./components/order/getall/getall').then((m) => m.Getall),
  },
  {
    path: 'pedidos/:id',
    title: 'Detalle de pedido',
    loadComponent: () => import('./components/order/detail/detail').then((m) => m.Detail),
  },
  {
    path: 'detalle-pedidos',
    title: 'Líneas de pedido',
    loadComponent: () => import('./components/order/lines/lines').then((m) => m.Lines),
  },
  {
    path: 'pagos',
    title: 'Pagos',
    loadComponent: () => import('./components/payment/getall/getall').then((m) => m.Getall),
  },
  {
    path: 'reservas',
    title: 'Reservas',
    loadComponent: () => import('./components/reservation/getall/getall').then((m) => m.Getall),
  },
  {
    path: 'insumos',
    title: 'Insumos',
    loadComponent: () => import('./components/supply/getall/getall').then((m) => m.Getall),
  },
  {
    path: 'recetas',
    title: 'Recetas',
    loadComponent: () => import('./components/recipe/getall/getall').then((m) => m.Getall),
  },
  {
    path: 'domiciliarios',
    title: 'Domiciliarios',
    loadComponent: () => import('./components/courier/getall/getall').then((m) => m.Getall),
  },
  {
    path: 'entregas',
    title: 'Entregas',
    loadComponent: () => import('./components/delivery/getall/getall').then((m) => m.Getall),
  },
  { path: '**', redirectTo: 'dashboard' },
];
