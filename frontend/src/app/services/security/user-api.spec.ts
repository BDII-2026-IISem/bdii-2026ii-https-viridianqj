import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { UserI, UserPermission } from '../../models/security/user';
import { UserApi } from './user-api';

describe('UserApi', () => {
  let api: UserApi;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    api = TestBed.inject(UserApi);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('la lectura de usuarios no incluye la contraseña', () => {
    let result: UserI[] = [];
    api.getAll().subscribe((rows) => (result = rows));

    const req = http.expectOne((r) => r.method === 'GET' && r.url.endsWith('/users/'));
    req.flush([
      { id: 2, username: 'elkin', email: 'elkin@example.com', firstName: 'Elkin', lastName: '', status: 'ACTIVE' },
    ]);

    expect(result.length).toBe(1);
    expect('password' in result[0]).toBe(false);
  });

  it('el PATCH al editar no envía la contraseña', () => {
    api
      .update(4, {
        username: 'jhonar',
        email: 'jdearco@example.com',
        firstName: 'jhonar',
        lastName: 'De arco',
        status: 'ACTIVE',
      })
      .subscribe();

    const req = http.expectOne((r) => r.method === 'PATCH' && r.url.endsWith('/users/4/'));
    expect(req.request.body.password).toBeUndefined();
    req.flush({ id: 4, username: 'jhonar' });
  });

  it('permissions(id) pide /users/{id}/permissions/ y devuelve la lista', () => {
    let result: UserPermission[] = [];
    api.permissions(2).subscribe((rows) => (result = rows));

    const req = http.expectOne((r) => r.url.endsWith('/users/2/permissions/'));
    req.flush({
      permissions: [
        { method: 'GET', path: '/api/users/', role: 'ADMIN' },
        { method: 'DELETE', path: '/api/users/:id/', role: 'ADMIN' },
      ],
    });

    expect(result.length).toBe(2);
    expect(result[0].path).toBe('/api/users/');
  });
});
