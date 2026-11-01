import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { UserI, UserPermission } from '../../../../models/security/user';
import { UserApi } from '../../../../services/security/user-api';
import { UserList } from './user-list';

describe('UserList', () => {
  const user: UserI = {
    id: 2,
    username: 'elkin',
    email: 'viridianqj@gmail.com',
    firstName: 'Elkin',
    lastName: '',
    status: 'ACTIVE',
  };

  const permissions: UserPermission[] = [
    { method: 'GET', path: '/api/users/', role: 'ADMIN' },
    { method: 'DELETE', path: '/api/users/:id/', role: 'ADMIN' },
  ];

  const apiMock = {
    getAll: () => of([user]),
    permissions: () => of(permissions),
    create: () => of(user),
    update: () => of(user),
    remove: () => of(undefined),
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [UserList],
      providers: [
        { provide: UserApi, useValue: apiMock },
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });
  });

  afterEach(() => {
    document.querySelectorAll('p-dialog, .p-dialog-mask').forEach((el) => el.remove());
  });

  it('carga la lista de usuarios', () => {
    const fixture = TestBed.createComponent(UserList);
    fixture.detectChanges();

    expect(fixture.componentInstance.items().length).toBe(1);
  });

  it('el diálogo de permisos muestra una fila por permiso', () => {
    const fixture = TestBed.createComponent(UserList);
    fixture.detectChanges();

    fixture.componentInstance.openPermissions(user);
    fixture.detectChanges();

    const rows = document.querySelectorAll('[data-testid="permisos"] tbody tr');
    expect(rows.length).toBe(permissions.length);
  });
});
