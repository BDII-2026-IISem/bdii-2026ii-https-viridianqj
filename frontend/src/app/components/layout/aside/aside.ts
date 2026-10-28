import { Component, OnInit } from '@angular/core';
import { MenuItem } from 'primeng/api';
import { PanelMenu } from 'primeng/panelmenu';

@Component({
  selector: 'app-aside',
  standalone: true,
  imports: [PanelMenu],
  templateUrl: './aside.html',
  styleUrl: './aside.css',
})
export class Aside implements OnInit {
  items: MenuItem[] = [];

  ngOnInit(): void {
    this.items = [
      {
        label: 'Negocio',
        icon: 'pi pi-fw pi-briefcase',
        expanded: true,
        items: [
          { label: 'Clientes', icon: 'pi pi-fw pi-users', routerLink: '/clientes' },
          { label: 'Productos', icon: 'pi pi-fw pi-shopping-bag', routerLink: '/productos' },
          { label: 'Pedidos', icon: 'pi pi-fw pi-shopping-cart', routerLink: '/pedidos' },
          { label: 'Pagos', icon: 'pi pi-fw pi-wallet', routerLink: '/pagos' },
        ],
      },
      {
        label: 'Salón',
        icon: 'pi pi-fw pi-building',
        expanded: true,
        items: [{ label: 'Reservas', icon: 'pi pi-fw pi-calendar', routerLink: '/reservas' }],
      },
      {
        label: 'Cocina',
        icon: 'pi pi-fw pi-box',
        expanded: true,
        items: [
          { label: 'Insumos', icon: 'pi pi-fw pi-box', routerLink: '/insumos' },
          { label: 'Recetas', icon: 'pi pi-fw pi-book', routerLink: '/recetas' },
        ],
      },
      {
        label: 'Domicilios',
        icon: 'pi pi-fw pi-truck',
        expanded: true,
        items: [
          { label: 'Domiciliarios', icon: 'pi pi-fw pi-id-card', routerLink: '/domiciliarios' },
          { label: 'Entregas', icon: 'pi pi-fw pi-send', routerLink: '/entregas' },
        ],
      },
    ];
  }
}