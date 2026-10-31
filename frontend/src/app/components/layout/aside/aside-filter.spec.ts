import { TestBed } from '@angular/core/testing';

import { SessionStore } from '../../../core/session';
import { Aside, NavItem } from './aside';

describe('Aside filtrado por permisos', () => {
  let session: SessionStore;
  let aside: Aside;

  beforeEach(() => {
    TestBed.configureTestingModule({ imports: [Aside] });
    session = TestBed.inject(SessionStore);
    aside = TestBed.createComponent(Aside).componentInstance;
  });

  it('sin permisos solo muestra el grupo Cuenta', () => {
    session.setPermissions([]);
    const labels = aside.visibleItems().map((item: NavItem) => item.label);
    expect(labels).toEqual(['Cuenta']);
  });

  it('con permiso de pedidos muestra Panel, Pedidos y Líneas de pedido en Negocio', () => {
    session.setPermissions([{ method: 'GET', path: '/api/pedidos/', role: 'Cajero' }]);
    const negocio = aside.visibleItems().find((item: NavItem) => item.label === 'Negocio');
    expect(negocio?.items?.map((item: NavItem) => item.label)).toEqual([
      'Panel',
      'Pedidos',
      'Líneas de pedido',
    ]);
  });
});
