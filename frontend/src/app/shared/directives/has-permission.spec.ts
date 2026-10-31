import { Component } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SessionStore } from '../../core/session';
import { HasPermission } from './has-permission';

@Component({
  imports: [HasPermission],
  template: `<button *appHasPermission="permissionKey">Eliminar</button>`,
})
class HostComponent {
  permissionKey = 'DELETE /api/clientes/';
}

describe('HasPermission', () => {
  let session: SessionStore;
  let fixture: ComponentFixture<HostComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({ imports: [HostComponent] });
    session = TestBed.inject(SessionStore);
    fixture = TestBed.createComponent(HostComponent);
  });

  it('oculta el botón si no hay permiso', () => {
    session.setPermissions([]);
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('button')).toBeNull();
  });

  it('muestra el botón si hay permiso', () => {
    session.setPermissions([{ method: 'DELETE', path: '/api/clientes/', role: 'Admin' }]);
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('button')).not.toBeNull();
  });
});
