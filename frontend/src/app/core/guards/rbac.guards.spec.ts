import { TestBed } from '@angular/core/testing';
import { ActivatedRouteSnapshot, Router, RouterStateSnapshot, UrlTree } from '@angular/router';

import { SessionStore } from '../session';
import { authGuard, permissionGuard } from './rbac.guards';

function route(permission: string): ActivatedRouteSnapshot {
  return { data: { permission } } as unknown as ActivatedRouteSnapshot;
}

function state(url: string): RouterStateSnapshot {
  return { url } as RouterStateSnapshot;
}

describe('rbac guards', () => {
  let session: SessionStore;
  let router: Router;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    session = TestBed.inject(SessionStore);
    router = TestBed.inject(Router);
    // Limpia tokens y permisos guardados por pruebas anteriores (localStorage).
    session.clear();
  });

  function login(): void {
    session.saveTokens({ access: 'a', refresh: 'r', tokenType: 'Bearer', accessExpiresIn: 3600 });
  }

  it('permissionGuard permite la ruta si el permiso está concedido', () => {
    login();
    session.setPermissions([{ method: 'GET', path: '/api/pedidos/', role: 'Cajero' }]);
    const result = TestBed.runInInjectionContext(() =>
      permissionGuard(route('GET /api/pedidos/'), state('/pedidos')),
    );
    expect(result).toBe(true);
  });

  it('permissionGuard redirige a /forbidden si falta el permiso', () => {
    login();
    // Lista no vacía sin el permiso requerido: decide de inmediato, sin llamar al backend.
    session.setPermissions([{ method: 'GET', path: '/api/clientes/', role: 'Cajero' }]);
    const result = TestBed.runInInjectionContext(() =>
      permissionGuard(route('GET /api/pedidos/'), state('/pedidos')),
    );
    expect(router.serializeUrl(result as UrlTree)).toContain('/forbidden?permission=');
  });

  it('authGuard redirige a /login con returnUrl si no hay sesión', () => {
    const result = TestBed.runInInjectionContext(() => authGuard(route(''), state('/clientes')));
    expect(router.serializeUrl(result as UrlTree)).toContain('/login?returnUrl=%2Fclientes');
  });
});
