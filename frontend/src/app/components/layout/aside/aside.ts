import { Component, computed, inject, input, output } from '@angular/core';
import { MenuItem } from 'primeng/api';
import { PanelMenu } from 'primeng/panelmenu';

import { SessionStore } from '../../../core/session';

// permission usa el formato "MÉTODO /api/recurso". Sin permission, la opción es visible con sesión.
export interface NavItem extends MenuItem {
  permission?: string;
  items?: NavItem[];
}

export const MENU_ITEMS: NavItem[] = [
  {
    label: 'Negocio',
    icon: 'pi pi-fw pi-briefcase',
    expanded: true,
    items: [
      { label: 'Panel', icon: 'pi pi-fw pi-chart-bar', routerLink: '/dashboard', permission: 'GET /api/pedidos/' },
      { label: 'Clientes', icon: 'pi pi-fw pi-users', routerLink: '/clientes', permission: 'GET /api/clientes/' },
      { label: 'Productos', icon: 'pi pi-fw pi-shop', routerLink: '/productos', permission: 'GET /api/productos/' },
      { label: 'Pedidos', icon: 'pi pi-fw pi-shopping-cart', routerLink: '/pedidos', permission: 'GET /api/pedidos/' },
      { label: 'Líneas de pedido', icon: 'pi pi-fw pi-list', routerLink: '/detalle-pedidos', permission: 'GET /api/pedidos/' },
      { label: 'Pagos', icon: 'pi pi-fw pi-wallet', routerLink: '/pagos', permission: 'GET /api/pagos/' },
    ],
  },
  {
    label: 'Salón',
    icon: 'pi pi-fw pi-building',
    expanded: true,
    items: [
      { label: 'Reservas', icon: 'pi pi-fw pi-calendar', routerLink: '/reservas', permission: 'GET /api/reservas/' },
    ],
  },
  {
    label: 'Cocina',
    icon: 'pi pi-fw pi-box',
    expanded: true,
    items: [
      { label: 'Insumos', icon: 'pi pi-fw pi-box', routerLink: '/insumos', permission: 'GET /api/insumos/' },
      { label: 'Recetas', icon: 'pi pi-fw pi-book', routerLink: '/recetas', permission: 'GET /api/recetas/' },
    ],
  },
  {
    label: 'Domicilios',
    icon: 'pi pi-fw pi-truck',
    expanded: true,
    items: [
      { label: 'Domiciliarios', icon: 'pi pi-fw pi-id-card', routerLink: '/domiciliarios', permission: 'GET /api/domiciliarios/' },
      { label: 'Entregas', icon: 'pi pi-fw pi-send', routerLink: '/entregas', permission: 'GET /api/entregas/' },
    ],
  },
  {
    label: 'Seguridad',
    icon: 'pi pi-fw pi-lock',
    expanded: true,
    items: [
      { label: 'Usuarios', icon: 'pi pi-fw pi-user', routerLink: '/admin/usuarios', permission: 'GET /api/users/' },
      { label: 'Roles', icon: 'pi pi-fw pi-key', routerLink: '/admin/roles', permission: 'GET /api/roles/' },
      { label: 'Recursos', icon: 'pi pi-fw pi-server', routerLink: '/admin/recursos', permission: 'GET /api/resources/' },
      { label: 'Asignaciones', icon: 'pi pi-fw pi-link', routerLink: '/admin/asignaciones', permission: 'GET /api/role-users/' },
      { label: 'Permisos por rol', icon: 'pi pi-fw pi-shield', routerLink: '/admin/permisos', permission: 'GET /api/resource-roles/' },
    ],
  },
  {
    label: 'Cuenta',
    icon: 'pi pi-fw pi-user',
    expanded: true,
    items: [{ label: 'Mi perfil', icon: 'pi pi-fw pi-id-card', routerLink: '/perfil' }],
  },
];

// Quita las opciones sin permiso y los grupos que quedan vacíos.
function filterNav(items: NavItem[], can: (key: string) => boolean): NavItem[] {
  return items
    .map((item) => {
      if (item.items) {
        const children = filterNav(item.items, can);
        return children.length ? { ...item, items: children } : null;
      }
      return !item.permission || can(item.permission) ? item : null;
    })
    .filter((item): item is NavItem => item !== null);
}

@Component({
  selector: 'app-aside',
  standalone: true,
  imports: [PanelMenu],
  templateUrl: './aside.html',
  styleUrl: './aside.css',
})
export class Aside {
  private readonly session = inject(SessionStore);

  readonly items = input<NavItem[]>(MENU_ITEMS);
  readonly navigated = output<void>();

  readonly visibleItems = computed(() =>
    filterNav(this.items(), (key) => this.session.canPermission(key)),
  );

  // Solo cerramos el menú cuando se hace clic en un enlace, no al expandir un grupo.
  onNavClick(event: MouseEvent): void {
    if ((event.target as HTMLElement).closest('a')) {
      this.navigated.emit();
    }
  }
}
