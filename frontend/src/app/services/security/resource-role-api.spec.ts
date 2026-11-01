import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { ResourceRolePayload } from '../../models/security/resource-role';
import { ResourceRoleApi } from './resource-role-api';

describe('ResourceRoleApi', () => {
  let api: ResourceRoleApi;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    api = TestBed.inject(ResourceRoleApi);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('el POST envía role, resource y status como valores numéricos y estado', () => {
    const payload: ResourceRolePayload = { role: 1, resource: 5, status: 'ACTIVE' };
    api.create(payload).subscribe();

    const req = http.expectOne((r) => r.method === 'POST' && r.url.endsWith('/resource-roles/'));
    expect(req.request.body).toEqual({ role: 1, resource: 5, status: 'ACTIVE' });
    expect(typeof req.request.body.role).toBe('number');
    expect(typeof req.request.body.resource).toBe('number');
    req.flush({ id: 10, ...payload });
  });

  it('getAll pide /resource-roles/ y devuelve las asignaciones', () => {
    let rows: unknown[] = [];
    api.getAll().subscribe((r) => (rows = r));

    const req = http.expectOne((r) => r.method === 'GET' && r.url.endsWith('/resource-roles/'));
    req.flush([{ id: 6, resource: 5, role: 1, status: 'ACTIVE' }]);

    expect(rows.length).toBe(1);
  });
});
